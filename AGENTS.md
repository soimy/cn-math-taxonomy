# 仓库协作指南

适用于整个仓库。修改前先看相关源码和测试；README 与设计文档中存在历史统计、旧端口和旧流程描述，当前行为以源码、`data/` 和可复现检查为准。

## 项目定位与技术栈

- 面向中小学与高中课程的多学科知识图谱、题库、自适应前置诊断和学习路径工具。学科包括数学、英语、物理、语文、科学、道德与法治、历史、地理；并非所有学科覆盖全部学段。
- 前端为原生 HTML / CSS / JavaScript，无 React/Vue、打包器或前端构建步骤。HTML 用普通 `<script>` 按顺序加载；通用逻辑多采用 UMD，同时支持浏览器全局对象与 Node `require()`。
- 图谱使用随仓库分发的 Cytoscape、dagre、cytoscape-dagre；二维码使用 qrcode-generator。版本与许可证见 `assets/vendor/VENDOR.md`，不要直接修改压缩库文件。
- Node 标准库提供本地静态服务和 `/v1/*` LLM 反向代理。模型服务独立运行，不在此仓库实现；没有账号服务、业务数据库或云端学生档案服务。
- Python 3 脚本负责离线数据生成、整理和校验。核心校验只使用标准库，不是 Python Web 后端。
- 静态 JSON 是运行时内容来源；浏览器 `localStorage` 保存会话、孩子档案、盲区和部分 AI 缓存，Service Worker Cache 保存离线资源。
- `package.json` 使用 CommonJS，目前没有 dependencies/devDependencies；`main: index.js` 不代表实际应用入口，`npm test` 仍是失败的占位命令。预览与核心测试无需先执行 `npm install`。

## 目录与职责

| 位置 | 职责 / 修改入口 |
| --- | --- |
| `index.html`、`assets/home.js`、`assets/site.css` | 首页、数据统计、年级入口、全站样式 |
| `explore/` | 知识图谱浏览、筛选、先修关系与教材映射展示 |
| `diagnose/app.js` | 诊断页面编排、数据加载、DOM、会话存储、练习、结果导出 |
| `diagnose/engine.js` | 图索引、自适应出题、判题、会话重放、薄弱点与学习路径；保持无 DOM 的核心逻辑边界 |
| `diagnose/route.js`、`route-page.js`、`route.html` | 自然语言作业分析 → 数学知识点定位 → 候选先修路径；逻辑与页面分离 |
| `diagnose/variants.js` | 确定性模板变式，用于练习补题 |
| `diagnose/llm-variants.js`、`llm-eval.js`、`llm-gateway.js` | LLM 变式生成与缓存、表达式/答案验证、请求与工具调用循环 |
| `diagnose/explain.js` | 渐进式讲解与追问；生成讲解失败时保留静态讲解 |
| `diagnose/funclab.js`、`geomlab.js`、`labmatch.js`、`chatgraph.js` | 函数/几何交互画板、题意与图形参数校验、追问绘图 |
| `diagnose/llm-config.js`、`settings.html`、`settings.js` | LLM 地址、型号、预算与超时配置；浏览器直连设置 |
| `children/`、`assets/children.js`、`assets/blindspots.js` | 孩子档案、历史记录、备份导入导出与盲区汇总 |
| `data/` | 知识点、先修边、题库、课标、旧 ID 别名、教材映射及历史核验材料 |
| `scripts/` | 数据生成/校验、覆盖率审计、截图、本地服务、fork 守卫；脚本副作用各不相同 |
| `sw.js`、`manifest.webmanifest`、`assets/pwa.*` | PWA 安装与离线缓存 |
| `tests/`、`tests/manual/` | Node 断言测试、浏览器测试、人工交互验收页 |
| `docs/` | 数据来源、设计与核验记录；先读与当前修改相关的文档 |

## 核心数据流与 RAG 边界

诊断主流程：页面 `fetch` JSON → 按学科筛选 → `engine.buildGraph()` → `createSession()` → `nextItem()` / `judgeQuestion()` / `applyAnswer()` → `summarize()` → 页面、档案与导出。会话可序列化与重放；题库加载失败时保留 `diagnostic_question` 回退。

诊断结论来自答题状态与确定性规则。知识点连续答对达到阈值才掌握，答错后用确认题区分“不稳”和“薄弱”，再按先修关系回溯。图中的先修关系不等于学生已被测出的薄弱点。

作业文字定位是结构化检索增强流程，目前只处理数学：

```text
输入文字
  → parseFields：正则/关键词抽取年级、学段、领域、章节与考点
  → candidates：从本地 topics 中按字段筛选候选
  → buildPrompt / askLLM：携带候选描述，请模型选择 1–3 个知识点
  → verifyPick：校验候选 ID、名称及字符 n-gram 覆盖率
  → prerequisites / buildPath：沿 hard 边回溯并生成待测路径
  → 用户进入诊断，结合真实答题结果确认
```

- 没有文档切块、embedding、向量库、向量召回或独立检索服务；不能把当前实现描述成完整向量 RAG 平台。
- `buildPrompt()` 当前只发送候选池前 120 项；这是召回范围限制，不是语义排序。扩大覆盖时先检查候选筛选、提示词与测试。
- 定位页主路径只用 hard 边，并有跨学段过滤；诊断引擎另有年级截断与先修优先级。两套策略用途不同，不要误当成同一套规则。
- LLM 输出是不可信候选。保留 ID/名称校验、答案验证、画板参数校验、超时与拒绝分支；不能用模型自验替代确定性验证。
- 变式题属于练习补充，保持其与正式题库/诊断会话的既有隔离；不要无意写入 `graph.bank` 或改变诊断结论。

## 服务、配置与隐私

在仓库根目录运行：

```sh
node scripts/serve.js              # 默认 127.0.0.1:8920
node scripts/serve.js 8930         # 指定端口
```

入口为 `/`、`/explore/`、`/diagnose/`、`/diagnose/route.html`、`/children/`、`/diagnose/settings.html`。

- 本地验收使用 `scripts/serve.js` 的禁缓存响应，避免普通静态服务器造成旧代码误判；仍需留意已安装的 Service Worker 缓存。
- 本地默认链路：浏览器 `/v1/*` → `serve.js` → 独立 LLM 网关；上游由 `llm-config.js` 读取 `LLM_UPSTREAM`。修改模型、地址、预算和超时应集中在配置模块，不要复制到各调用方。
- 纯静态托管不能运行 Node 反代；可通过设置页配置兼容接口直连，接口须支持浏览器跨域请求。模型配置在模块加载时读取，保存后需要刷新消费页面。
- `compose.yaml` 若存在，使用 Node 22 镜像、只读挂载工作目录，并通过 `host.docker.internal` 访问宿主网关。当前映射对局域网开放；`serve.js` 不提供用户鉴权或限流，不把它当作已加固的公网服务。
- 档案与答题记录没有自动云同步；LLM 功能会把相关题目、作答或输入文字发送给配置的模型端点。不要笼统声称所有功能均不联网。
- 直连 API Key 保存在当前站点的 `localStorage`，不是服务端秘密。不得将真实密钥写入代码、日志、截图或测试夹具；不要擅自清除用户浏览器存储。
- 保留存储键、旧 ID 别名和备份格式兼容性；涉及迁移时覆盖导入失败、版本不兼容和原数据保留场景。

## 数据修改约束

- `topics.json`、`dependencies.json`、`questions.json` 顶层是数组；课标为对象，条目在 `items`；别名在 `id-aliases.json` 的 `aliases`。
- 边 `{topicId, prerequisiteId, strength, reason}` 表示前者依赖后者；`strength` 为 `hard` 或 `soft`。保持 DAG、引用完整与 ID 稳定，不按数组下标重编号。
- 数学节点常省略 `subject`，使用现有 `engine.subjectOf()` / ID 前缀约定。物理的 `mathLinks` 是跨学科提示，不是跨学科先修边。
- 高中 `grade` 部分表示册次，不是实际学年；数学、英语、物理的册次范围不同，复用现有解析与标签逻辑。
- 学科数据由 `primary_*`、`hs_*`、`en*`、`zh_*`、`phy_*` 等草稿、构建脚本及后续修订脚本共同形成。先确认要改的数据来源和写回范围，再同步相关生成源、运行数据、测试与说明。
- 不存在统一且可安全重跑的“全库构建”。有的脚本一次性追加，有的重写多份数据；不要把 `*_build.py`、`build_primary.py` 或修订脚本当只读检查批量运行。
- `data/_qbatches/`、`data/_second_pass/`、核验报告和复核日志是历史材料，不是浏览器加载的主库；不要顺手删除或把旧报告当作当前数据已验证的证据。
- 修改字段时一起检查数据加载方、生成脚本、`validate.py`、判题/验证器、相关测试与导出格式。新增页面/资源或改变数据结构时检查 `sw.js` 的清单和缓存版本。
- 保留来源、`exact` / `inferred`、`verbatim` 与“待核”标记。自动校验通过不代表教师审核通过，不能删除 AI 初稿与未核验内容的说明。

## 检查与测试

按修改范围选择现有检查；不要使用占位的 `npm test`。当前 `.github/` 只有 Issue 模板，没有随仓库定义的 Actions 测试工作流。

| 修改范围 | 命令 |
| --- | --- |
| 数据结构、ID、先修图、题库格式、课标引用 | `python3 scripts/validate.py` |
| 题库答案与 verify 表达式一致性（不写报告） | `python3 scripts/verify_questions.py --file data/questions.json` |
| 诊断、判题、会话、模板变式 | `node tests/test_engine.js` |
| 作业文字定位与路径 | `node tests/test_route.js` |
| LLM 配置与设置 | `node tests/test_llm_settings.js` |
| LLM 数学验证 / 变式管线 | `node tests/test_llm_eval.js` / `node tests/test_llm_variants.js` |
| 讲解 / 函数画板 / 曲线 / 几何画板 | `node tests/test_explain.js` / `node tests/test_funclab.js` / `node tests/test_funclab_curves.js` / `node tests/test_geomlab.js` |
| 画板语义匹配 / 追问绘图 | `node tests/test_labmatch.js` / `node tests/test_chatgraph.js` |
| 档案、备份 / 盲区 | `node tests/test_children.js` / `node tests/test_blindspots.js` |
| 本地服务 | `node tests/test_serve.js` |
| fork 的保留规则 | `node tests/test_fork_guards.js` |

- `verify_questions.py` 不带参数会改写 `data/verification_report.json`；只读核验用上表的 `--file`，此模式不合并历史第二遍复核日志，也不代表独立盲解。
- Node 核心测试可离线运行，LLM 测试使用 mock；测试通过不证明真实网关、型号、CORS 或线上部署可用。需要真实联调时单独说明验证范围。
- UI/备份浏览器验收可用 `node tests/test_children_browser.js`；截图冒烟用 `node scripts/screenshot.js`，需要本机 Chrome/Chromium（可设置 `CHROME`），截图默认写 `.cache/screenshots/`。刷新跟踪中的截图需显式 `SHOTS_OUT=screenshots` 并人工审查差异。
- 不为文档或平凡修改新增测试框架。非平凡逻辑改动使用现有 Node `assert` / Python 校验模式，补一个能验证实际行为的最小回归检查。

## fork 与工作区纪律

- 开始及结束时检查 `git status`。保留用户已有的未提交修改，不清理无关文件、不顺手重生成数据，也不未经请求提交、推送或部署。
- 合并上游或处理页面/配置时先读 `docs/fork-divergences.md`。保留本站分享链接、移除外链推广位、关闭默认统计上报、集中 LLM 配置等分叉意图。
- `scripts/fork-guard.mjs` 会修改/删除文件，不是只读 lint。仅在需要应用清理规则时运行，检查 diff；用 `tests/test_fork_guards.js` 验证。新增分叉同步维护说明和断言。
- 沿用当前文件的风格与模块边界；优先复用已有 helper 和标准库，不为小改动引入框架、依赖或抽象层。改公共函数前搜索所有调用方，保持浏览器和 Node 两端可用。
- 交付时说明实际修改、已运行检查、失败与未验证项；区分本地通过、真实模型联调、浏览器验收及上线状态。
