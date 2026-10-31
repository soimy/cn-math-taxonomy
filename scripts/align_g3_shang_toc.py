#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三上按人教版 2025 秋（dzkbw xs3s_2025）目录小节对齐。"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g123_bank_g3 import BANK as BANK_G3  # noqa: E402
from g1_g2_g3_grade_align import convert  # noqa: E402

NOTE = "依据 dzkbw xs3s_2025（2025 秋）小节补点。"

CH_U1 = "三年级上册 第1单元 观察物体"
CH_U2 = "三年级上册 第2单元 混合运算"
CH_U3 = "三年级上册 第3单元 毫米、分米和千米"
CH_CAO = "三年级上册 综合与实践 曹冲称象的故事"
CH_U4 = "三年级上册 第4单元 多位数乘一位数"
CH_CODE = "三年级上册 综合与实践 数字编码"
CH_U5 = "三年级上册 第5单元 线和角"
CH_U6 = "三年级上册 第6单元 分数的初步认识"
CH_U7 = "三年级上册 第7单元 复习与关联"

RENAMES = {
    "cnm_p221": {
        "chapter": CH_U1,
    },
    "cnm_p222": {
        "name": "长方体纸盒的展开",
        "description": "知道把长方体、正方体纸盒沿棱剪开可以展成平面图形，展开由 6 个面组成，相对的面完全一样。",
        "mastery_criteria": ["能说出长方体展开有 6 个面", "知道相对的面完全一样"],
        "chapter": CH_U1,
    },
    "cnm_p223": {
        "name": "同级运算与两级运算",
        "description": "知道只有加减或只有乘除要从左往右算；有乘除又有加减时，先算乘除再算加减。",
        "mastery_criteria": ["能按从左往右算同级运算", "能先乘除后加减算两级运算"],
        "chapter": CH_U2,
    },
    "cnm_p058": {
        "name": "含有小括号的两级运算",
        "description": "知道小括号里的运算要先算，再按两级运算顺序算。",
        "mastery_criteria": ["能先算小括号里面的", "能完成含小括号的两级运算"],
        "chapter": CH_U2,
    },
    "cnm_p059": {
        "name": "用混合运算解决问题",
        "description": "能用同级或两级混合运算解决两步实际问题，并能用两种思路想。",
        "mastery_criteria": ["能列出两步算式", "能说出先算哪一步"],
        "chapter": CH_U2,
        "type": "application",
    },
    "cnm_p067": {
        "name": "毫米的认识",
        "description": "认识毫米，知道 1 厘米＝10 毫米，会进行厘米与毫米的简单换算。",
        "mastery_criteria": ["能说出 1 厘米等于 10 毫米", "能把几厘米换成毫米"],
        "chapter": CH_U3,
    },
    "cnm_p068": {
        "name": "分米的认识及单位换算",
        "description": "认识分米，知道 1 分米＝10 厘米，会进行分米与厘米的简单换算。",
        "mastery_criteria": ["能说出 1 分米等于 10 厘米", "能把几分米换成厘米"],
        "chapter": CH_U3,
    },
    "cnm_p069": {
        "name": "千米的认识及单位换算",
        "description": "认识千米，知道 1 千米＝1000 米，会进行千米与米的简单换算。",
        "mastery_criteria": ["能说出 1 千米等于 1000 米", "能把几千米换成米"],
        "chapter": CH_U3,
    },
    "cnm_p224": {
        "name": "等量代换",
        "description": "能借助曹冲称象等情境理解等量代换，用同样重的物品互相代替。",
        "mastery_criteria": ["能说出为什么石头能代替大象的重量", "能做简单的等量代换"],
        "chapter": CH_CAO,
    },
    "cnm_p056": {
        "name": "认识质量单位",
        "description": "认识质量单位克和千克，知道 1 千克＝1000 克，能选用合适的单位。",
        "mastery_criteria": ["能说出 1 千克等于 1000 克", "能判断物体大约用克还是千克"],
        "chapter": CH_CAO,
        "standards": [
            {"id": "cms-2022:2.IP.02", "confidence": "exact", "note": NOTE},
        ],
    },
    "cnm_p070": {
        "chapter": CH_CAO,
        "description": "认识吨，知道 1 吨＝1000 千克，能进行吨与千克的简单换算。",
    },
    "cnm_p074": {
        "name": "笔算乘法",
        "description": "会用竖式计算两、三位数乘一位数（含不进位、进位、连续进位），从个位乘起。",
        "mastery_criteria": ["能从个位乘起写竖式", "满几十能正确进位"],
        "chapter": CH_U4,
    },
    "cnm_p075": {
        "name": "因数中间或末尾有0的乘法",
        "description": "会计算因数中间或末尾有 0 的多位数乘一位数。",
        "mastery_criteria": ["末尾有 0 时能先算再补 0", "中间有 0 时不错位"],
        "chapter": CH_U4,
    },
    "cnm_p076": {
        "name": "认识数字编码",
        "description": "知道可以用数字给事物编码，编码里的每一位可以表示不同的意思。",
        "mastery_criteria": ["能说出编码某一位表示什么", "能读懂简单的数字编码"],
        "chapter": CH_CODE,
    },
    "cnm_p099": {
        "name": "线段、射线、直线的概念",
        "description": "认识线段、射线和直线，知道端点个数和能否度量、延长。",
        "mastery_criteria": ["能说出线段有两个端点", "能区分射线和直线"],
        "chapter": CH_U5,
    },
    "cnm_p225": {
        "chapter": CH_U5,
    },
    "cnm_p101": {
        "name": "直角、锐角、钝角",
        "description": "认识直角、锐角和钝角，能判断一个角是直角、锐角还是钝角。",
        "mastery_criteria": ["能辨认直角", "能说出锐角比直角小、钝角比直角大"],
        "chapter": CH_U5,
    },
    "cnm_p079": {
        "name": "认识几分之一",
        "description": "初步认识几分之一，知道把一个整体平均分成几份，其中一份就是几分之一。",
        "mastery_criteria": ["能说出几分之一表示什么", "能写出简单的几分之一"],
        "chapter": CH_U6,
    },
    "cnm_p226": {
        "name": "认识几分之几",
        "description": "认识几分之几，知道平均分成几份后取其中几份。",
        "mastery_criteria": ["能读写几分之几", "能说出分子、分母各表示什么"],
        "chapter": CH_U6,
    },
    "cnm_p227": {
        "chapter": CH_U6,
    },
    "cnm_p080": {
        "name": "同分母分数的加减法",
        "description": "会计算同分母分数的加法和减法，分母不变、只算分子。",
        "mastery_criteria": ["能算同分母分数加法", "能算同分母分数减法"],
        "chapter": CH_U6,
    },
    "cnm_p073": {
        "chapter": CH_U7,
        "description": "知道「几倍」就是几个那么多，会求一个数的几倍。旧版独立单元内容，新版 2025 秋目录未单列，暂挂复习与关联·数量关系，待核。",
        "standards": [
            {"id": "cms-2022:2.NA.08", "confidence": "exact", "note": "暂挂复习与关联，待核。"},
            {"id": "cms-2022:1.NA.05", "confidence": "exact"},
        ],
    },
    "cnm_p081": {
        "chapter": CH_U7,
        "description": "能看懂简单的集合图，知道重叠部分表示两类都有的，会求只算一次的总数。旧版内容，新版 2025 秋目录未单列，暂挂复习与关联，待核。",
        "standards": [
            {"id": "cms-2022:2.NA.10", "confidence": "inferred", "note": "暂挂复习与关联，待核。"},
        ],
    },
    "cnm_p095": {
        "name": "搭配问题",
        "description": "能有序地数出两种事物的搭配种数，不重复也不遗漏。对应复习与关联中的数学广角：搭配问题。",
        "mastery_criteria": ["能按顺序一种一种地配", "能用乘法算出搭配种数"],
        "chapter": CH_U7,
        "standards": [
            {"id": "cms-2022:2.NA.10", "confidence": "inferred", "note": NOTE},
        ],
    },
}

NEW_TOPICS = [
    {
        "id": "cnm_p274",
        "name": "根据直观图猜测积木形状",
        "domain": "图形与几何",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U1,
        "type": "reasoning",
        "description": "能根据从正面、上面等看到的直观图，猜测或说出积木的摆法与个数。",
        "mastery_criteria": ["能根据正面图估计最少块数", "能把上面图和正面图结合起来想"],
        "standards": [
            {"id": "cms-2022:2.GG.06", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p275",
        "name": "口算乘法",
        "domain": "数与代数",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U4,
        "type": "procedural",
        "description": "会口算整十、整百数乘一位数等简单的多位数乘一位数。",
        "mastery_criteria": ["能口算整十乘一位数", "能口算整百乘一位数"],
        "standards": [
            {"id": "cms-2022:2.NA.01", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p276",
        "name": "乘法估算",
        "domain": "数与代数",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U4,
        "type": "application",
        "description": "能把多位数看成接近的整十、整百数，估算多位数乘一位数的积。",
        "mastery_criteria": ["能选择合适的整十数来估", "能说出大约是多少"],
        "standards": [
            {"id": "cms-2022:2.NA.01", "confidence": "inferred", "note": NOTE},
            {"id": "cms-2022:2.NA.09", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p277",
        "name": "用圆规比较线段的长短",
        "domain": "图形与几何",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U5,
        "type": "procedural",
        "description": "会用圆规量取一条线段的长，并与另一条线段比较长短。",
        "mastery_criteria": ["知道圆规两脚对准端点", "能根据开口判断哪条更长"],
        "standards": [
            {"id": "cms-2022:2.GG.01", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p278",
        "name": "认识二分之一",
        "domain": "数与代数",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U6,
        "type": "conceptual",
        "description": "认识 1/2，知道把一个整体平均分成 2 份，其中一份就是二分之一。",
        "mastery_criteria": ["能指出平均分成两份中的一份是 1/2", "知道必须平均分才是 1/2"],
        "standards": [
            {"id": "cms-2022:2.NA.02", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p279",
        "name": "估测距离",
        "domain": "图形与几何",
        "grade": 3,
        "semester": "上",
        "chapter": CH_U3,
        "type": "application",
        "description": "能结合千米、米等单位，对生活中的路程做合理估测。",
        "mastery_criteria": ["能选择合适的单位估路程", "能用加减估算两段路程合计"],
        "standards": [
            {"id": "cms-2022:2.GG.03", "confidence": "inferred", "note": NOTE},
            {"id": "cms-2022:2.NA.09", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p280",
        "name": "编制学号",
        "domain": "综合与实践",
        "grade": 3,
        "semester": "上",
        "chapter": CH_CODE,
        "type": "modeling",
        "description": "能按班级、座号等规则编制学号，并读懂学号里每一位的意思。",
        "mastery_criteria": ["能按规则写出学号", "能从学号读出席号或班号"],
        "standards": [
            {"id": "cms-2022:2.NA.05", "confidence": "inferred", "note": NOTE},
        ],
    },
]

NEW_EDGES = [
    ("cnm_p274", "cnm_p221", "hard", "学习「根据直观图猜测积木形状」需要先掌握「观察简单的立体积木」。"),
    ("cnm_p222", "cnm_p274", "soft", "「根据直观图猜测积木形状」对学习「长方体纸盒的展开」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p275", "cnm_p042", "hard", "学习「口算乘法」需要先掌握「7～9的乘法口诀」。"),
    ("cnm_p275", "cnm_p039", "soft", "「2～6的乘法口诀」对学习「口算乘法」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p074", "cnm_p275", "hard", "学习「笔算乘法」需要先掌握「口算乘法」。"),
    ("cnm_p276", "cnm_p275", "hard", "学习「乘法估算」需要先掌握「口算乘法」。"),
    ("cnm_p276", "cnm_p074", "soft", "「笔算乘法」对学习「乘法估算」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p277", "cnm_p099", "hard", "学习「用圆规比较线段的长短」需要先掌握「线段、射线、直线的概念」。"),
    ("cnm_p277", "cnm_p265", "soft", "「认识线段」对学习「用圆规比较线段的长短」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p278", "cnm_p043", "hard", "学习「认识二分之一」需要先掌握「除法的意义」。"),
    ("cnm_p079", "cnm_p278", "hard", "学习「认识几分之一」需要先掌握「认识二分之一」。"),
    ("cnm_p279", "cnm_p069", "hard", "学习「估测距离」需要先掌握「千米的认识及单位换算」。"),
    ("cnm_p279", "cnm_p041", "soft", "「认识米及用米量」对学习「估测距离」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p280", "cnm_p076", "hard", "学习「编制学号」需要先掌握「认识数字编码」。"),
    ("cnm_p280", "cnm_p053", "soft", "「1000以内数的认识」对学习「编制学号」有帮助，但不会前者也可以开始学后者。"),
]

# (old, new) — longer keys first via sort
NAME_IN_REASON = [
    ("长方体纸盒的展开图", "长方体纸盒的展开"),
    ("同级运算与两级运算的运算顺序", "同级运算与两级运算"),
    ("带小括号的两步运算", "含有小括号的两级运算"),
    ("两步加减应用", "用混合运算解决问题"),
    ("分米的认识及单位换算", "分米的认识及单位换算"),  # noop guard
    ("千米的认识及单位换算", "千米的认识及单位换算"),
    ("毫米的认识", "毫米的认识"),
    ("等量代换（曹冲称象）", "等量代换"),
    ("克和千克", "认识质量单位"),
    ("多位数乘一位数", "笔算乘法"),
    ("因数中间或末尾有 0 的乘法", "因数中间或末尾有0的乘法"),
    ("数字编码", "认识数字编码"),
    ("线段、直线和射线", "线段、射线、直线的概念"),
    ("锐角、直角和钝角", "直角、锐角、钝角"),
    ("几分之一", "认识几分之一"),
    ("几分之几", "认识几分之几"),
    ("同分母分数的初步加减", "同分母分数的加减法"),
    ("简单的搭配", "搭配问题"),
    ("毫米", "毫米的认识"),
    ("分米", "分米的认识及单位换算"),
    ("千米", "千米的认识及单位换算"),
]

EXISTING_SHANG = [
    "cnm_p221", "cnm_p222", "cnm_p223", "cnm_p058", "cnm_p059",
    "cnm_p067", "cnm_p068", "cnm_p069", "cnm_p224", "cnm_p056", "cnm_p070",
    "cnm_p074", "cnm_p075", "cnm_p076", "cnm_p099", "cnm_p225", "cnm_p101",
    "cnm_p079", "cnm_p226", "cnm_p227", "cnm_p080", "cnm_p073", "cnm_p081", "cnm_p095",
]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def dump_pretty(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def dump_compact(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")


def dq_from_bank(tid):
    rows = [convert(r) for r in BANK_G3[tid]]
    q1 = rows[0]
    if q1["type"] == "choice":
        ans = [x["text"] for x in q1["choices"] if x["key"] == q1["answer"]][0]
    else:
        ans = str(q1["answer"])
    return {"question": q1["prompt"], "answer": ans}, rows


def replace_reason_names(reason):
    for old, new in sorted(NAME_IN_REASON, key=lambda x: -len(x[0])):
        if old == new:
            continue
        if old not in reason:
            continue
        # Avoid double-prefix when new already contains/extends old fragment
        if new in reason and old in new:
            # e.g. already 「毫米的认识」— don't turn into 「毫米的认识的认识」
            # Replace only when old appears as full quoted name without new prefix
            import re
            # Replace 「old」 when not already 「...new...」 covering it
            pattern = "「" + re.escape(old) + "」"
            replacement = "「" + new + "」"
            reason = re.sub(pattern, replacement, reason)
            # Also bare occurrences outside quotes that are exact topic refs — skip bare
        else:
            reason = reason.replace(old, new)
    # Fix accidental doubles
    doubles = [
        ("毫米的认识的认识", "毫米的认识"),
        ("分米的认识及单位换算的认识及单位换算", "分米的认识及单位换算"),
        ("千米的认识及单位换算的认识及单位换算", "千米的认识及单位换算"),
        ("认识质量单位的认识", "认识质量单位"),
        ("认识数字编码的认识", "认识数字编码"),
        ("认识几分之一的认识", "认识几分之一"),
        ("认识几分之几的认识", "认识几分之几"),
        ("认识二分之一的认识", "认识二分之一"),
        ("笔算乘法乘一位数", "笔算乘法"),
    ]
    for bad, good in doubles:
        reason = reason.replace(bad, good)
    return reason


def main():
    topics = load("topics.json")
    deps = load("dependencies.json")
    questions = load("questions.json")
    by_id = {t["id"]: t for t in topics}

    for tid, fields in RENAMES.items():
        t = by_id[tid]
        for k, v in fields.items():
            t[k] = v

    insert_at = None
    for i, t in enumerate(topics):
        if t["id"] == "cnm_p273":
            insert_at = i + 1
            break
    if insert_at is None:
        insert_at = len(topics)

    new_objs = []
    for spec in NEW_TOPICS:
        if spec["id"] in by_id:
            raise SystemExit("已存在 " + spec["id"])
        dq, _ = dq_from_bank(spec["id"])
        obj = {
            "id": spec["id"],
            "name": spec["name"],
            "domain": spec["domain"],
            "grade": spec["grade"],
            "semester": spec["semester"],
            "chapter": spec["chapter"],
            "type": spec["type"],
            "description": spec["description"],
            "mastery_criteria": spec["mastery_criteria"],
            "diagnostic_question": dq,
            "external": False,
            "standards": spec["standards"],
        }
        new_objs.append(obj)
        by_id[spec["id"]] = obj
    for i, obj in enumerate(new_objs):
        topics.insert(insert_at + i, obj)

    for tid in list(RENAMES) + [x["id"] for x in NEW_TOPICS]:
        if tid in BANK_G3 and tid in by_id:
            dq, _ = dq_from_bank(tid)
            by_id[tid]["diagnostic_question"] = dq

    # Topic-id-aware reason rewrite for renames
    rename_names = {}
    for tid, fields in RENAMES.items():
        if "name" in fields:
            rename_names[tid] = fields["name"]

    new_deps = []
    for d in deps:
        d = dict(d)
        r = d.get("reason", "")
        # Prefer quoting updates for known renamed endpoints
        for endpoint in (d.get("topicId"), d.get("prerequisiteId")):
            if endpoint in rename_names and endpoint in by_id:
                # after rename by_id already has new name; get old from reason via global replace
                pass
        d["reason"] = replace_reason_names(r)
        new_deps.append(d)

    existing = {(d["topicId"], d["prerequisiteId"]) for d in new_deps}
    added = 0
    for tid, pre, strength, reason in NEW_EDGES:
        if (tid, pre) in existing:
            continue
        new_deps.append({
            "topicId": tid,
            "prerequisiteId": pre,
            "strength": strength,
            "reason": reason,
        })
        existing.add((tid, pre))
        added += 1

    # Soften old hard p074<-p042 if we now have p275 in between? Keep both hard.
    # Soften old hard p079<-p043 if p278 is now hard for p079 — keep p043 as soft maybe
    for d in new_deps:
        if d["topicId"] == "cnm_p079" and d["prerequisiteId"] == "cnm_p043" and d["strength"] == "hard":
            d["strength"] = "soft"
            d["reason"] = "「除法的意义」对学习「认识几分之一」有帮助，但不会前者也可以开始学后者。"

    # Fix remaining doubles after global replace
    for d in new_deps:
        r = d["reason"]
        for bad, good in [
            ("毫米的认识的认识", "毫米的认识"),
            ("分米的认识及单位换算的认识及单位换算", "分米的认识及单位换算"),
            ("千米的认识及单位换算的认识及单位换算", "千米的认识及单位换算"),
            ("认识数字编码编码", "认识数字编码"),
            ("认识几分之几之几", "认识几分之几"),
            ("认识几分之一之一", "认识几分之一"),
            ("笔算乘法乘一位数", "笔算乘法"),
            ("线段、射线、直线的概念的概念", "线段、射线、直线的概念"),
        ]:
            if bad in r:
                d["reason"] = r.replace(bad, good)
                r = d["reason"]

    # Special: p076 was 「数字编码」→「认识数字编码」; edges that said 数字编码 may have become 认识认识数字编码
    for d in new_deps:
        d["reason"] = d["reason"].replace("认识认识数字编码", "认识数字编码")
        d["reason"] = d["reason"].replace("认识认识质量单位", "认识质量单位")
        d["reason"] = d["reason"].replace("认识认识几分之一", "认识几分之一")
        d["reason"] = d["reason"].replace("认识认识几分之几", "认识几分之几")
        d["reason"] = d["reason"].replace("认识认识二分之一", "认识二分之一")

    # questions
    all_shang = EXISTING_SHANG + [x["id"] for x in NEW_TOPICS]
    bank_qs = {}
    for tid in all_shang:
        rows = [convert(r) for r in BANK_G3[tid]]
        items = []
        for i, q in enumerate(rows, 1):
            item = dict(q)
            item.pop("_adopt", None)
            item["id"] = "%s_q%d" % (tid, i)
            item["topicId"] = tid
            items.append(item)
        bank_qs[tid] = items

    out_q = []
    seen = set()
    i = 0
    while i < len(questions):
        tid = questions[i].get("topicId")
        if tid in EXISTING_SHANG and tid not in seen:
            j = i
            while j < len(questions) and questions[j].get("topicId") == tid:
                j += 1
            out_q.extend(bank_qs[tid])
            seen.add(tid)
            i = j
        else:
            out_q.append(questions[i])
            i += 1

    leftover = set(EXISTING_SHANG) - seen
    if leftover:
        raise SystemExit("未替换旧题：" + "、".join(sorted(leftover)))

    insert_q = len(out_q)
    for i, q in enumerate(out_q):
        if q.get("id") == "cnm_p273_q4":
            insert_q = i + 1
            break
    chunk = []
    for tid in [x["id"] for x in NEW_TOPICS]:
        chunk.extend(bank_qs[tid])
    out_q[insert_q:insert_q] = chunk

    g3_batch = [q for q in out_q if by_id.get(q["topicId"], {}).get("grade") == 3
                and str(q["topicId"]).startswith("cnm_")]

    dump_pretty("topics.json", topics)
    dump_pretty("dependencies.json", new_deps)
    dump_compact("questions.json", out_q)
    dump_pretty("_qbatches/primary_g3.json", g3_batch)

    g3s = [t for t in topics if t.get("grade") == 3 and t.get("semester") == "上"
           and str(t["id"]).startswith("cnm_p")]
    primary = [t for t in topics if t.get("grade") in range(1, 7) and str(t["id"]).startswith("cnm_p")]
    math_topics = [t for t in topics if str(t["id"]).startswith("cnm_")]
    math_deps = [d for d in new_deps if str(d["topicId"]).startswith("cnm_")]
    hard = sum(1 for d in math_deps if d["strength"] == "hard")
    soft = sum(1 for d in math_deps if d["strength"] == "soft")
    by = {t["id"]: t for t in topics}
    pi = [d for d in math_deps
          if by.get(d["topicId"], {}).get("grade", 99) <= 6
          and by.get(d["prerequisiteId"], {}).get("grade", 99) <= 6]
    pq = [q for q in out_q if str(q["topicId"]).startswith("cnm_p")]
    mq = [q for q in out_q if str(q["topicId"]).startswith("cnm_")]

    print("三上", len(g3s))
    for t in sorted(g3s, key=lambda x: (x["chapter"], x["id"])):
        print(" ", t["id"], t["name"], "|", t["chapter"])
    print("小学", len(primary), "数学", len(math_topics))
    print("mathDeps", len(math_deps), "hard", hard, "soft", soft, "小学内部", len(pi))
    print("新增边", added)
    print("小学题", len(pq), "数学题", len(mq), "总题", len(out_q), "g3batch", len(g3_batch))
    bad = [d for d in new_deps if "的认识的认识" in d["reason"] or "认识认识" in d["reason"]]
    print("bad reasons", len(bad))
    for d in bad[:10]:
        print(" ", d["topicId"], d["prerequisiteId"], d["reason"][:80])


if __name__ == "__main__":
    main()
