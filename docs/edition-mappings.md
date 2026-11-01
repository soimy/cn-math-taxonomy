# 教材版本对照（mappings）贡献指南

对应 Issue #11（沪教版等其他教材版本）。

## 方案

不另做一套沪教版知识点库。知识点（`data/topics.json`）仍然按人教版编排：`grade`、`semester`、`chapter` 就是人教版的册次和章节，缺省就是人教版。其他版本只回答一个问题：**同一个知识点，在该版本教材里排在哪一册、哪一单元**。

知识点本身（名称、先修边、题库、课标对齐）各版本共用。版本之间知识点的取舍和粒度有差异，这套对照只做「大致位置」，不保证一一对应。

## 数据格式

### 1. topic 上的可选字段 `mappings`

```json
{
  "id": "cnm_p158",
  "name": "最大公因数",
  "grade": 5,
  "semester": "下",
  "chapter": "五年级下册 第2单元 因数与倍数",
  "mappings": {
    "hujiao_math": {"grade": 5, "term": "上", "unit": "（单元名）", "chapter": "（章节名）"}
  }
}
```

（上面的数值只用来说明形状，不是真实对照。）

- `mappings` 是对象，键是**版本 id**：小写字母、数字、下划线，写成 `<版本拼音>_<学科>`，如 `hujiao_math`（沪教版）、`sujiao_math`（苏教版）、`beishida_math`（北师大版）。苏教、北师大等用同一格式。
- 人教版**不写**进 `mappings`（`renjiao_math`、`pep_math` 会被校验拒绝），它就是 topic 自己的 `grade` / `semester` / `chapter`。
- 值是对照条目：

| 字段 | 必填 | 说明 |
|---|---|---|
| `grade` | 是 | 该版本教材里的年级，整数（1–9；高中沿用本库的 10–14 编号） |
| `term` | 是 | `上` / `下` / `全`（沪教版称第一、第二学期，分别写 `上`、`下`） |
| `unit` | 否 | 单元（或章）名称，非空字符串 |
| `chapter` | 否 | 节 / 课时名称，非空字符串 |
| `note` | 否 | 与人教版取舍不同、拆合并等需要说明的地方 |

- 没有对照的知识点**不要**写 `mappings`（空对象会被拒绝）；缺省不会触发任何校验错误。
- `topics.json` 里的 `mappings` 由对照表文件合并而来（见下），不要手改；目前 200 个知识点带对照。

### 2. 贡献用的对照表文件 `data/mappings/<版本 id>.json`

直接改 `topics.json`（一个很大的文件）不利于 PR 审阅，所以贡献走独立的小文件，审核通过后再由维护者合并进各 topic 的 `mappings`。

```json
{
  "edition": "hujiao_math",
  "label": "沪教版（上海教育出版社）数学",
  "status": "draft",
  "source": "对照依据：教材名称、版次、目录页或网址、查证日期",
  "entries": [
    {"topicId": "cnm_p158", "grade": 5, "term": "上", "unit": "…", "chapter": "…"}
  ]
}
```

- `status`：`example`（示例，仅演示格式）、`draft`（有依据，待核）、`reviewed`（已另一人对照教材核过）。`draft` 和 `reviewed` 必须写 `source`。
- 文件名必须以 `edition` 开头；示例文件叫 `<edition>.example.json`，`status` 必须是 `example`，至多 10 条。
- `entries[].topicId` 必须是该版本学科对应的正式知识点（版本 id 的学科后缀决定学科：`hujiao_math` → 数学、`hujiao_english` → 英语），同一文件里不能重复；`grade`、`term`、`unit`、`chapter`、`note` 规则同上。

仓库里现有 `hujiao_math.json`（沪教版数学 1–5 年级，160 条，`draft`）、`hujiao_english.json`（沪教版英语五上，38 条，`draft`）、`sd54_math.json`（山东五四制青岛版，12 条，`draft`），以及只有 6 条**占位**数据、不能当目录用的 `hujiao_math.example.json`。

### 3. 合并进 topics.json

浏览器不 fetch `data/mappings/`，运行时只读 `topics.json`（PWA 预缓存、离线可用）。改完对照表后跑：

```sh
python3 scripts/merge_mappings.py          # 全量重建 topic.mappings，可反复运行
python3 scripts/merge_mappings.py --check  # 只报告差异，不写文件
python3 scripts/validate.py
```

脚本会先清掉所有 `mappings` 再按当前对照文件写回（跳过 `status: example`），所以删掉某条对照重跑就生效。`mappings` 固定插在 `standards` 后面，diff 只有新增行。

## 怎么提 PR

1. 先确认你手上有可核对的依据：教材目录页、教师用书目录、教育部门或出版社公开目录，并记下版次和查证日期。**不要凭记忆填**，也不要从别的网站整页复制。
2. 复制示例文件为 `data/mappings/<版本 id>.json`，把 `status` 改成 `draft`，写好 `label` 和 `source`。
3. 从 `data/topics.json` 里按年级找到对应知识点，逐条填 `topicId`、`grade`、`term`，目录里有单元名就填 `unit`。**一次提交一个年级或一册**，方便审阅。
4. 版本之间取舍不同的（该版本没有这个知识点、或把几个点合讲）：没有的知识点直接不写；合讲的在 `note` 里说明。
5. 本地跑 `python3 scripts/validate.py`，应当输出 `VALIDATION PASSED`，并在「教材版本对照」一行看到你的条目数。
6. 提 PR，描述里写清依据和覆盖范围（例如「沪教版一年级第一、第二学期，已覆盖 X 个」），不要写成全册已对齐。

## 现状和限制

- 诊断页**已读取**对照数据：开始页「按年级整体诊断」的年级和范围跟随孩子档案的年级、教材版本（`assets/children.js` 的 `grade` / `textbook`），按 `mappings` 里的年级/学期筛范围，整年级筛查的按单元汇总也用该版本的单元名（`diagnose/app.js` 的 `targetsFor()` / `chapterSummaryOf()`，`engine.gradeTargets()` 第 4 个参数）。
- 该版本/年级没有对照、或该学科没有对照表时，回退人教版的册次范围，并在卡片上提示「××这个年级还没有对照表，按人教版出题」；不会因为缺映射隐藏知识点。
- 目前生效的只有 `沪教版`：`hujiao` 前缀映射到 `hujiao_<学科>`，`assets/children.js` 的 `TEXTBOOKS` 里其他版本（北师大版、苏教版、外研版、译林版）还没有对照表，选了仍按人教版出题。
- 开始页的「按册、章浏览」也按该版本分组：册 = `mappings` 的年级+学期，章 = `mappings.unit`，行内副标题 = `mappings.chapter`（没有对照的知识点不会出现在这个列表里，可仍用搜索或整年级范围测到）。
- 图谱页（`explore/`）仍按人教版册次显示。
- 对照表覆盖不全是正常状态，不要为了凑满而填占位值。
