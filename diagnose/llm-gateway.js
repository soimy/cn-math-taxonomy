/* O3 网关层：本地网关探测 / 单次请求 / 工具自验循环 + max_tokens 常量。
 *
 * 从 llm-variants.js 拆出（O3-8 重构，零行为变更）：
 *   - 探测：probeGateway（GET /v1/models）/ probeFunctionCalling（带 tools 的最小请求）
 *   - 请求：postOnce（带超时，返回响应 JSON 或 null）
 *   - 工具自验（§2.4 效率层）：TOOLS schema / executeToolCalls / runToolLoop
 *   - 常量：PROXY / MODEL / TIMEOUT_MS / PROBE_* / GEN_MAX_TOKENS / TOOL_MAX_TOKENS
 *           （值统一取自 diagnose/llm-config.js，本模块只保留同名别名）
 *
 * 依赖注入：表达式求值由调用方拿进来（本模块不碰纯函数层的内部实现），
 * 浏览器取 window.DiagLLMEval，Node 下 require('./llm-eval.js')。
 * 时钟可注入（setNow），探测结果 TTL 内命中缓存；fetch 在调用时读全局，便于测试 mock。
 *
 * UMD 包装沿用 variants.js / llm-variants.js 风格：
 *   浏览器 → window.DiagLLMGateway；Node → require() 直接拿到对象。
 *   Node 下自取 llm-eval 作为默认注入；浏览器下按 index.html 顺序先加载 llm-eval。
 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory(require('./llm-eval.js'));
  } else {
    root.DiagLLMGateway = factory(root.DiagLLMEval);
  }
})(typeof self !== 'undefined' ? self : this, function (__eval) {
  'use strict';

  /* 表达式工具（工具自验用）：默认取 UMD 注入的纯函数层，可 setEval 替换 */
  var _evp = __eval || null;

  function setEval(ev) { if (ev) _evp = ev; return _evp; }

  function _evTools() { return _evp; }

  /* 配置唯一真源：diagnose/llm-config.js（浏览器由 index.html 先加载，Node 直接 require） */
  function _loadLLMConfig() {
    if (typeof LLMConfig !== 'undefined' && LLMConfig) return LLMConfig;
    if (typeof require === 'function') {
      try { return require('./llm-config.js'); } catch (e) { /* 落到 fail-closed */ }
    }
    return null;
  }

  var CFG = _loadLLMConfig();

  /* max_tokens 单一真源已收敛到 llm-config.js 的 maxTokens.variants / maxTokens.tools（O3-6 契约，
   * tests/test_llm_variants.js 静态断言）。本模块保留同名别名，仍接受 setLimits 注入覆盖。 */
  var GEN_MAX_TOKENS = CFG ? CFG.maxTokens.variants : null;
  var TOOL_MAX_TOKENS = CFG ? CFG.maxTokens.tools : null;

  function setLimits(lim) {
    if (!lim) return;
    if (typeof lim.GEN_MAX_TOKENS === 'number') GEN_MAX_TOKENS = lim.GEN_MAX_TOKENS;
    if (typeof lim.TOOL_MAX_TOKENS === 'number') TOOL_MAX_TOKENS = lim.TOOL_MAX_TOKENS;
  }

  var PROXY = CFG ? CFG.chatUrl() : null;

  var MODEL = CFG ? CFG.model : null;

  var TIMEOUT_MS = CFG ? CFG.timeouts.chat : null;

  /* O3-4：探测超时放宽到 15s（联调时网关负载大响应可能 >5s，5s 太紧导致误判 false）
   * 值与实测依据都搬到了 llm-config.js 的 timeouts.probe。 */
  var PROBE_TIMEOUT_MS = CFG ? CFG.timeouts.probe : null;

  /* O3-4：探测结果 5 分钟 TTL，过期自动重探（避免 false 永久污染钉死功能） */
  var PROBE_TTL_MS = 5 * 60 * 1000;

  /* ================================================================
   * 网关可达性探测（§6.1 调用前检查）
   * try 一次 /v1/models 或超时标记，不可达直接走降级，不拖慢页面。
   * ================================================================ */

  var _gatewayReachable = null;   /* null=未探测, true=可达, false=不可达 */

  var _gatewayProbeAt = 0;        /* 上次探测时间戳（O3-4：TTL 过期自动重探） */

  var _supportsTools = null;      /* null=未探测, true=支持, false=不支持 */

  var _supportsToolsAt = 0;       /* 上次探测时间戳（O3-4：TTL 过期自动重探） */

  /* 可注入时钟（测试推进时间用）；默认 Date.now */
  var _nowFn = function () { return Date.now(); };

  /* 探测结果是否已过期：从未探测(0)或超过 TTL 视为过期 */
  function _probeExpired(at) {
    return !at || (_nowFn() - at) >= PROBE_TTL_MS;
  }

  /**
   * 探测网关是否可达。try 一次 /v1/models，15 秒超时。
   * 结果缓存在 _gatewayReachable，TTL 内命中缓存，过期自动重探。
   * @returns {Promise<boolean>}
   */
  function probeGateway() {
    if (typeof fetch !== 'function') {
      _gatewayReachable = false; _gatewayProbeAt = _nowFn();
      return Promise.resolve(false);
    }
    /* 配置没加载：按不可达降级，不把 null 传给 fetch */
    if (!CFG) {
      _gatewayReachable = false; _gatewayProbeAt = _nowFn();
      return Promise.resolve(false);
    }
    if (!_probeExpired(_gatewayProbeAt) && _gatewayReachable !== null) {
      return Promise.resolve(_gatewayReachable);
    }

    var modelsUrl = CFG.modelsUrl();
    var controller = null;
    var timeoutId = null;
    if (typeof AbortController !== 'undefined') {
      controller = new AbortController();
      timeoutId = setTimeout(function () { controller.abort(); }, PROBE_TIMEOUT_MS);
    }

    return fetch(modelsUrl, {
      method: 'GET',
      signal: controller ? controller.signal : undefined
    })
      .then(function (res) {
        if (timeoutId) clearTimeout(timeoutId);
        _gatewayReachable = res.ok;
        _gatewayProbeAt = _nowFn();
        return _gatewayReachable;
      })
      .catch(function () {
        if (timeoutId) clearTimeout(timeoutId);
        _gatewayReachable = false;
        _gatewayProbeAt = _nowFn();
        return false;
      });
  }

  /* ================================================================
   * function calling 探测（§2.4 工具自验）
   * 探测网关模型是否支持 function calling（OpenAI 兼容 tools 参数）。
   * 支持 → LLM 侧 tools 接入（evaluateExpression/solveCheck/normalizeSet）。
   * 不支持 → 记录结论，维持引擎外部验证路径（验证门仍保留为硬保证）。
   *
   * O3-4 修复：成功判定改为「HTTP 200 且响应无 error 字段 → 支持」，
   * 不再依赖 tool_calls 是否出现（模型选择直接回答也算支持——探测的是
   * 网关/模型接受 tools 参数）。超时放宽到 15s，去掉 max_tokens:100 截断。
   * ================================================================ */

  /* §2.4 工具集：evaluateExpression / solveCheck / normalizeSet（OpenAI 兼容 schema） */
  var TOOLS = [
    {
      type: 'function',
      function: {
        name: 'evaluateExpression',
        description: '数值求值：在给定 x 值数组处计算表达式 expr 的数值',
        parameters: {
          type: 'object',
          properties: {
            expr: { type: 'string', description: '数学表达式' },
            xValues: { type: 'array', items: { type: 'number' }, description: 'x 取值数组' }
          },
          required: ['expr', 'xValues']
        }
      }
    },
    {
      type: 'function',
      function: {
        name: 'solveCheck',
        description: '代入验根：验证 candidate 是否满足 equation',
        parameters: {
          type: 'object',
          properties: {
            equation: { type: 'string', description: '方程表达式' },
            candidate: { type: 'string', description: '候选根' }
          },
          required: ['equation', 'candidate']
        }
      }
    },
    {
      type: 'function',
      function: {
        name: 'normalizeSet',
        description: '集合归一：把多值答案归一为数值集合',
        parameters: {
          type: 'object',
          properties: {
            answers: { type: 'string', description: '多值答案文本' }
          },
          required: ['answers']
        }
      }
    }
  ];

  /**
   * 探测网关模型是否支持 function calling。
   * 发一个带 tools 参数的最小候选请求。
   * 成功判定：HTTP 200 且响应无 error 字段 → 支持（模型接受 tools 参数）。
   * 结果带时间戳缓存，TTL 过期自动重探。
   * @returns {Promise<boolean>}
   */
  function probeFunctionCalling() {
    if (typeof fetch !== 'function') {
      _supportsTools = false; _supportsToolsAt = _nowFn();
      return Promise.resolve(false);
    }
    /* 配置没加载：按不支持降级，不把 null 传给 fetch */
    if (!CFG) {
      _supportsTools = false; _supportsToolsAt = _nowFn();
      return Promise.resolve(false);
    }
    if (!_probeExpired(_supportsToolsAt) && _supportsTools !== null) {
      return Promise.resolve(_supportsTools);
    }

    var controller = null;
    var timeoutId = null;
    if (typeof AbortController !== 'undefined') {
      controller = new AbortController();
      timeoutId = setTimeout(function () { controller.abort(); }, PROBE_TIMEOUT_MS);
    }

    var body = {
      model: MODEL,
      messages: [
        { role: 'user', content: '调用 check 工具验证 x=1 是否满足 x-1=0' }
      ],
      tools: [{
        type: 'function',
        function: {
          name: 'solveCheck',
          description: '代入验根：验证 candidate 是否满足 equation',
          parameters: {
            type: 'object',
            properties: {
              equation: { type: 'string', description: '方程表达式' },
              candidate: { type: 'string', description: '候选根' }
            },
            required: ['equation', 'candidate']
          }
        }
      }],
      tool_choice: 'auto'
    };

    return fetch(PROXY, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined
    })
      .then(function (res) {
        if (timeoutId) clearTimeout(timeoutId);
        /* O3-4：HTTP 200 且无 error 字段 → 支持。res.ok 覆盖 2xx。 */
        if (!res.ok) { _supportsTools = false; _supportsToolsAt = _nowFn(); return false; }
        return res.json();
      })
      .then(function (data) {
        if (timeoutId) clearTimeout(timeoutId);
        /* json 为空（无 error 也无 choices）→ 保守按不支持（无有效响应） */
        if (!data) { _supportsTools = false; _supportsToolsAt = _nowFn(); return false; }
        /* O3-4：响应含 error 字段 → 不支持（网关/模型拒绝 tools 参数） */
        if (data.error) { _supportsTools = false; _supportsToolsAt = _nowFn(); return false; }
        /* 否则：HTTP 200 且无 error → 模型接受了 tools 参数，判定支持 */
        _supportsTools = true;
        _supportsToolsAt = _nowFn();
        return true;
      })
      .catch(function () {
        if (timeoutId) clearTimeout(timeoutId);
        _supportsTools = false;
        _supportsToolsAt = _nowFn();
        return false;
      });
  }

  /**
   * 单次 POST 请求（带超时）。返回响应 JSON 或 null。
   * @param {object} body
   * @returns {Promise<object|null>}
   */
  function _postOnce(body) {
    /* 配置没加载：沿用「请求失败返回 null」的降级路径，不把 null 传给 fetch */
    if (!CFG) return Promise.resolve(null);
    var controller = null;
    var timeoutId = null;
    if (typeof AbortController !== 'undefined') {
      controller = new AbortController();
      timeoutId = setTimeout(function () { controller.abort(); }, TIMEOUT_MS);
    }
    return fetch(PROXY, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined
    })
      .then(function (res) {
        if (timeoutId) clearTimeout(timeoutId);
        if (!res.ok) return null;
        return res.json();
      })
      .catch(function () {
        if (timeoutId) clearTimeout(timeoutId);
        return null;
      });
  }

  /**
   * 执行 tool_calls 数组中的 JS 函数，构造 role:'tool' 结果消息数组。
   * 返回 null 表示任一调用无法安全执行（未知工具/抛错）→ 上层回退单层。
   * @param {object[]} toolCalls
   * @returns {object[]|null}
   */
  function _executeToolCalls(toolCalls, ev) {
    var results = [];
    try {
      for (var i = 0; i < toolCalls.length; i++) {
        var tc = toolCalls[i];
        if (!tc || !tc.function || !tc.id) return null;
        var name = tc.function.name;
        var args = {};
        try { args = JSON.parse(tc.function.arguments || '{}'); } catch (e) { /* 参数畸形按空对象处理 */ }
        var out;
        if (name === 'evaluateExpression') {
          out = ev.evaluateExpression(args.expr, args.xValues);
        } else if (name === 'solveCheck') {
          out = ev.solveCheck(args.equation, args.candidate);
        } else if (name === 'normalizeSet') {
          out = ev.normalizeSet(args.answers);
        } else {
          return null;  /* 未知工具 → 回退单层 */
        }
        /* Set → 数组序列化；数组/标量直接 JSON */
        var content;
        if (typeof Set !== 'undefined' && out instanceof Set) {
          content = JSON.stringify(Array.from(out));
        } else {
          content = JSON.stringify(out);
        }
        results.push({ role: 'tool', tool_call_id: tc.id, content: content });
      }
      return results;
    } catch (e) {
      return null;
    }
  }

  /**
   * 工具自验循环：执行 tool_calls 中的 JS 函数，把 assistant tool_calls 消息
   * + tool role 结果消息追加进 messages，发起二次请求取最终题。
   * 任一工具执行抛错/未知工具 → 返回 null（上层回退单层 content）。
   * @param {object[]} messages - 会原地追加 assistant + tool 结果消息
   * @param {object} msg - 首次响应的 message（含 tool_calls）
   * @returns {Promise<object|null>}
   */
  function _runToolLoop(messages, msg, parseCandidate, ev) {
    var toolResults = _executeToolCalls(msg.tool_calls, ev);
    if (toolResults === null) {
      /* 工具执行抛错/未知工具 → 回退单层，用首次响应已有 content */
      return Promise.resolve(parseCandidate(msg.content));
    }
    /* 追加 assistant tool_calls 消息 + tool role 结果消息 */
    messages.push({ role: 'assistant', content: msg.content || null, tool_calls: msg.tool_calls });
    for (var i = 0; i < toolResults.length; i++) {
      messages.push(toolResults[i]);
    }
    var body = {
      model: MODEL,
      messages: messages,
      max_tokens: TOOL_MAX_TOKENS,
      temperature: 0.8
    };
    return _postOnce(body).then(function (data) {
      if (!data || !data.choices || !data.choices[0]) return null;
      return parseCandidate(data.choices[0].message.content);
    });
  }

  return {
    PROXY: PROXY,
    MODEL: MODEL,
    TIMEOUT_MS: TIMEOUT_MS,
    PROBE_TIMEOUT_MS: PROBE_TIMEOUT_MS,
    PROBE_TTL_MS: PROBE_TTL_MS,
    GEN_MAX_TOKENS: GEN_MAX_TOKENS,
    TOOL_MAX_TOKENS: TOOL_MAX_TOKENS,
    TOOLS: TOOLS,
    probeGateway: probeGateway,
    probeFunctionCalling: probeFunctionCalling,
    postOnce: _postOnce,
    executeToolCalls: _executeToolCalls,
    runToolLoop: _runToolLoop,
    setEval: setEval,
    setLimits: setLimits,
    setNow: function (fn) { _nowFn = fn || function () { return Date.now(); }; },
    resetProbe: function () {
      _gatewayReachable = null; _gatewayProbeAt = 0;
      _supportsTools = null; _supportsToolsAt = 0;
      _nowFn = function () { return Date.now(); };
    }
  };
});
