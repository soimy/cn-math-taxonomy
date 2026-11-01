/* LLM 配置唯一真源：网关地址、型号、max_tokens 预算、超时。
 *
 * 为什么集中到一处
 * ----------------
 * 网关地址与型号以前在 explain / labmatch / llm-gateway / route 里各写一遍，
 * 网关重启成不带 CORS 的配置时页面会整层静默 fail-closed。现在浏览器统一走
 * scripts/serve.js 的同源反代 /v1，配置只在这里改。
 *
 * 双端：浏览器挂 window.LLMConfig；Node 下 require('./llm-config.js')。
 * 零依赖，纯 ES5。
 *
 * 解析规则：有 document 的浏览器默认相对 /v1（走反代）；没有 document 的 Node
 * 脚本/测试默认绝对地址 upstream + /v1（scripts/audit_*.js 直接 fetch 需要绝对 URL）。
 * 静态托管没有反代时可用 ?llm=<url> 或 localStorage['cnmDiagnose.llmBase'] 覆盖基址。
 */
(function (root, factory) {
  var cfg = factory();
  root.LLMConfig = cfg;
  if (typeof module !== 'undefined' && module.exports) module.exports = cfg;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var BASE = '/v1';

  /* 本地网关默认地址。Node 下允许 LLM_UPSTREAM 覆盖（浏览器里没有 process，必须守卫）。 */
  var upstream = 'http://127.0.0.1:3000';
  if (typeof process !== 'undefined' && process && process.env && process.env.LLM_UPSTREAM) {
    upstream = String(process.env.LLM_UPSTREAM);
  }
  upstream = String(upstream).replace(/\/+$/, '');

  var model = 'DeepSeek-V4.1-Flash-1017-Unlimited';

  var maxTokens = {
    /* O3-6：max_tokens 单一出处。
     * 讲解输出实测 300-800 token 足够 —— 2048 留足余量且不放大计费（追问的预算见下，另行说明）；
     * 不写裸数字，避免「改一处漏一处」（O3-4 探测漏改 max_tokens:100 即此类事故）。
     * 改这两个值之前先看 tests/test_engine.js 的 max_tokens 契约断言。 */
    explain: 2048,    /* 三步讲解（prompt/hint/reveal 的 JSON） */
    /* 讲解中追问：单轮，但输出是 JSON 对象 {text, graph|null}（不是纯文本）。
     * JSON 比纯文本多吃 token（键名、引号、转义 + graph 结构化参数），且推理模型的
     * reasoning 会先吃预算 —— 正文可能一个字都吐不出来（finish_reason=length、content 空串
     * → 学生看到「AI 老师暂时离线」）。实测同一 prompt 反复打网关：
     *   max_tokens=1024：稳定 finish=length、content 空（本卡根因）
     *   max_tokens=2048：仍有 3/10 次被 reasoning 吃光（completion=2048、content 空）
     *   max_tokens=4096：37/37 次 finish=stop、JSON 完整（completion 448–3342）
     * 取 4096：reasoning 长度有长尾 —— 2048 多数情况够（另有一次同 prompt 量测 completion=1080、
     * 约 2 倍余量），但长尾下会被吃光，故取 4096 换稳定；max_tokens 只是上限、按实际用量计费，
     * 抬高上限不额外花钱，且 <= 4096 是 test_engine.js 既有的防过度放大红线。 */
    followup: 4096,
    /* 验证时用 500 会把 JSON 截断（reason 字段被切掉一半 → 解析失败）。
     * 注意网关把 reasoning_content 也算进预算：1200 在长推理题上仍会截断（实测 cnm_202_q1 同题重试就顶到上限），
     * 因此给 2000 —— 卡面「给足 1200」是最低要求，不是上限。
     * 现用型号见 llm-config.js 的 model 字段，实测（cnm_235_q2 题面，4 次）：finish_reason 全为 stop，
     * completion_tokens 99–161，离 2000 很远，暂无上调必要；换型号/换 prompt 后要重新量。 */
    labmatch: 2000,
    /* O3-6：max_tokens 单一出处（各文件自持，关键是一处定义、多处引用）。
     * GEN  —— 出题：一道题 JSON（题面+答案+解析），扩族后题面变长，500 会撞截断。
     *   为什么现在能到 8192（实测，不是拍脑袋）：
     *   网关吞吐实测约 250 token/s → 10s 只够约 2500 token，所以旧的 1024 上限其实在当「保险丝」用；
     *   一道需要长推理的题目用 max_tokens=8192 实测 10.5s / completion 2972 才 finish=stop；
     *   同一题 max_tokens=2048 时 8.1s、finish=length、内容被截断。
     *   即：8192 才够长题面不截断，但它必然跑过旧的 10s，所以 timeouts.chat 必须同步放到 30000。
     *   8192 只对出题生效；工具轮见下，仍是 512，不受影响。
     * TOOL —— 工具轮：只需返回 tool_calls 参数，不需要长文本，取 512（也是 >=512 下限）
     * 改这两个值之前先看 tests/test_llm_variants.js 的 max_tokens 契约断言。 */
    variants: 8192,
    tools: 512,
    route: 1600     /* ≥1200：网关把 reasoning 算进预算 */
  };

  var timeouts = {
    /* 与 maxTokens.variants=8192 配套（实测依据见上）：网关吞吐约 250 token/s，
     * 长推理题 max_tokens=8192 实测 10.5s / completion 2972 才 finish=stop，旧的 10s 会先触发超时。
     * 取 30000：宁可等，也不要超时后 fail-closed 丢掉已经生成的内容
     * （超时 abort 会连同已产出的题目 JSON 一起丢）。 */
    chat: 30000,
    /* O3-4：探测超时放宽到 15s（联调时网关负载大响应可能 >5s，5s 太紧导致误判 false） */
    probe: 15000,
    labmatch: 20000,  /* 推理模型 + 多选项题面实测可超 12s（cnm_230_q1 就吃过超时） */
    route: 60000
  };

  /** 浏览器（有 document.location）才默认走相对路径 /v1（同源反代） */
  function _hasDom() {
    return typeof document !== 'undefined' && document && document.location;
  }

  function _stripTrailingSlash(u) {
    return String(u == null ? '' : u).replace(/\/+$/, '');
  }

  /** 没有覆盖时的默认基址：浏览器 /v1；Node 绝对地址 upstream + /v1 */
  function _defaultBase() {
    return _hasDom() ? BASE : upstream + BASE;
  }

  /** 覆盖链：?llm=<url> → localStorage['cnmDiagnose.llmBase'] → 默认基址 */
  function resolveBase() {
    var custom = null;

    /* 查询参数只在浏览器（有 location.search）下读 */
    try {
      if (typeof location !== 'undefined' && location && typeof location.search === 'string') {
        var m = /[?&]llm=([^&]*)/.exec(location.search);
        if (m) {
          try { custom = decodeURIComponent(m[1].replace(/\+/g, ' ')); }
          catch (e) { custom = m[1]; }
        }
      }
    } catch (e) { /* 取不到就当没有 */ }

    if (!custom) {
      try {
        if (typeof localStorage !== 'undefined' && localStorage) {
          custom = localStorage.getItem('cnmDiagnose.llmBase');
        }
      } catch (e) { /* 隐私模式/配额异常：忽略覆盖 */ }
    }

    var base = _stripTrailingSlash(custom || _defaultBase());
    return base || _stripTrailingSlash(_defaultBase());
  }

  function chatUrl() {
    return resolveBase() + '/chat/completions';
  }

  function modelsUrl() {
    return resolveBase() + '/models';
  }

  return {
    base: BASE,
    upstream: upstream,
    model: model,
    maxTokens: maxTokens,
    timeouts: timeouts,
    resolveBase: resolveBase,
    chatUrl: chatUrl,
    modelsUrl: modelsUrl
  };
});
