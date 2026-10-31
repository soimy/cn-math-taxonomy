#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三下按人教版 2026 春（dzkbw xs3x_2026）目录小节对齐。"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g123_bank_g3 import BANK as BANK_G3  # noqa: E402
from g1_g2_g3_grade_align import convert  # noqa: E402

NOTE = "依据 dzkbw xs3x_2026（2026 春）小节补点。"

CH_U1 = "三年级下册 第1单元 生活中的运动现象"
CH_U2 = "三年级下册 第2单元 除数是一位数的除法"
CH_U3 = "三年级下册 第3单元 长方形和正方形"
CH_U4 = "三年级下册 第4单元 图形的面积"
CH_U5 = "三年级下册 第5单元 数据的收集与整理"
CH_YMD = "三年级下册 综合与实践 年、月、日的秘密"
CH_U6 = "三年级下册 第6单元 小数的初步认识"
CH_U7 = "三年级下册 第7单元 复习与关联"

RENAMES = {
    "cnm_p228": {"chapter": CH_U1},
    "cnm_p083": {
        "name": "笔算除法",
        "description": "会用竖式计算除数是一位数的除法，从高位除起，商的位置写对。",
        "mastery_criteria": ["能从高位除起写竖式", "商的数位不错位"],
        "chapter": CH_U2,
    },
    "cnm_p084": {
        "description": "能用除数是一位数的除法解决平均分、包含等实际问题。",
        "chapter": CH_U2,
    },
    "cnm_p229": {
        "name": "多边形",
        "description": "认识多边形，知道几边形有几条边、几个角。",
        "mastery_criteria": ["能说出几边形的边数", "知道边数和角数相同"],
        "chapter": CH_U3,
    },
    "cnm_p077": {
        "chapter": CH_U3,
        "description": "认识长方形和正方形的特征：对边相等、四个角都是直角；正方形四边相等。",
    },
    "cnm_p078": {
        "name": "周长",
        "description": "知道周长是围成图形一周的长度，会求长方形和正方形的周长。",
        "mastery_criteria": ["能说出周长的含义", "会用（长＋宽）×2 或边长×4 求周长"],
        "chapter": CH_U3,
    },
    "cnm_p088": {
        "name": "面积和面积单位",
        "description": "知道面积是物体表面或封闭图形的大小，认识常用面积单位。",
        "mastery_criteria": ["能区分周长和面积", "知道要用面积单位表示大小"],
        "chapter": CH_U4,
    },
    "cnm_p089": {"chapter": CH_U4},
    "cnm_p090": {
        "name": "面积单位间的进率",
        "description": "知道相邻面积单位间的进率（如 1 平方米＝100 平方分米），会简单换算。",
        "mastery_criteria": ["能说出常用进率", "能把平方米换成平方分米"],
        "chapter": CH_U4,
    },
    "cnm_p085": {
        "name": "数据的收集与整理",
        "description": "能收集简单数据并整理成统计表（含复式统计表），从表中获取信息。",
        "mastery_criteria": ["能从表中读出指定数据", "会求合计或比较两类数据"],
        "chapter": CH_U5,
        "standards": [
            {"id": "cms-2022:2.SP.01", "confidence": "exact", "note": NOTE},
        ],
    },
    "cnm_p091": {
        "name": "年历中的秘密",
        "description": "认识年、月、日，知道平年、闰年和各月天数，能从年历中发现规律。",
        "mastery_criteria": ["能说出一年有 12 个月", "知道平年、闰年 2 月的天数"],
        "chapter": CH_YMD,
    },
    "cnm_p092": {
        "name": "作息时间表中的秘密",
        "description": "会用 24 时记时法读写时刻，能结合作息时间表计算经过的时间。",
        "mastery_criteria": ["能把下午时刻写成 24 时记时", "能算出跨过整点经过几小时"],
        "chapter": CH_YMD,
    },
    "cnm_p093": {
        "name": "认识小数",
        "description": "初步认识一位小数，能结合元角分、米和分米等写出小数。",
        "mastery_criteria": ["能读写一位小数", "知道 0.1 表示十分之一"],
        "chapter": CH_U6,
    },
    "cnm_p094": {
        "name": "简单的小数加、减法",
        "description": "会计算简单的一位小数加法和减法，小数点对齐。",
        "mastery_criteria": ["能把小数点对齐再算", "能解决简单的小数加减问题"],
        "chapter": CH_U6,
    },
    "cnm_p082": {
        "chapter": CH_U7,
        "description": "认识东北、东南、西北、西南四个方向。新版 2026 春目录未单列方向单元，暂挂复习与关联·图形的认识与测量，待核。",
        "standards": [
            {"id": "cms-2022:2.GG.04", "confidence": "inferred", "note": "暂挂复习与关联，待核。"},
        ],
    },
}

NEW_TOPICS = [
    {
        "id": "cnm_p281",
        "name": "剪纸",
        "domain": "图形与几何",
        "grade": 3,
        "semester": "下",
        "chapter": CH_U1,
        "type": "application",
        "description": "能结合剪纸活动体会轴对称，通过对折剪出两边一样的图案。",
        "mastery_criteria": ["知道对折剪纸与轴对称有关", "能说出展开后两边一样"],
        "standards": [
            {"id": "cms-2022:2.GG.05", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p282",
        "name": "口算除法",
        "domain": "数与代数",
        "grade": 3,
        "semester": "下",
        "chapter": CH_U2,
        "type": "procedural",
        "description": "会口算整十、整百数除以一位数等简单的除数是一位数的除法。",
        "mastery_criteria": ["能口算整十除以一位数", "能口算整百除以一位数"],
        "standards": [
            {"id": "cms-2022:2.NA.01", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p283",
        "name": "拼图游戏",
        "domain": "图形与几何",
        "grade": 3,
        "semester": "下",
        "chapter": CH_U3,
        "type": "application",
        "description": "能用长方形、正方形等拼成新图形，并求拼成图形的边长或周长。",
        "mastery_criteria": ["能说出拼成后新图形的边长", "能求简单拼图的周长"],
        "standards": [
            {"id": "cms-2022:2.GG.02", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p284",
        "name": "小数的大小比较",
        "domain": "数与代数",
        "grade": 3,
        "semester": "下",
        "chapter": CH_U6,
        "type": "reasoning",
        "description": "会比较一位小数的大小，能找出一组小数中的最大或最小。",
        "mastery_criteria": ["能比较两个一位小数的大小", "能在三个小数中找出最大的"],
        "standards": [
            {"id": "cms-2022:2.NA.02", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p285",
        "name": "年历设计师",
        "domain": "综合与实践",
        "grade": 3,
        "semester": "下",
        "chapter": CH_YMD,
        "type": "modeling",
        "description": "能根据平年、闰年和各月天数设计或完善简单年历。",
        "mastery_criteria": ["设计前能先判断平年或闰年", "知道要按星期排列日期"],
        "standards": [
            {"id": "cms-2022:2.IP.03", "confidence": "inferred", "note": NOTE},
        ],
    },
]

NEW_EDGES = [
    ("cnm_p281", "cnm_p228", "hard", "学习「剪纸」需要先掌握「生活中的运动现象」。"),
    ("cnm_p281", "cnm_p024", "soft", "「图形的拼组」对学习「剪纸」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p282", "cnm_p044", "hard", "学习「口算除法」需要先掌握「用7～9的乘法口诀求商」。"),
    ("cnm_p282", "cnm_p046", "soft", "「用2～6的乘法口诀求商」对学习「口算除法」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p083", "cnm_p282", "hard", "学习「笔算除法」需要先掌握「口算除法」。"),
    ("cnm_p283", "cnm_p078", "hard", "学习「拼图游戏」需要先掌握「周长」。"),
    ("cnm_p283", "cnm_p077", "soft", "「长方形和正方形的特征」对学习「拼图游戏」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p284", "cnm_p093", "hard", "学习「小数的大小比较」需要先掌握「认识小数」。"),
    ("cnm_p094", "cnm_p284", "soft", "「小数的大小比较」对学习「简单的小数加、减法」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p285", "cnm_p091", "hard", "学习「年历设计师」需要先掌握「年历中的秘密」。"),
    ("cnm_p285", "cnm_p092", "soft", "「作息时间表中的秘密」对学习「年历设计师」有帮助，但不会前者也可以开始学后者。"),
]

NAME_IN_REASON = [
    ("多边形的认识", "多边形"),
    ("除数是一位数的除法", "笔算除法"),
    ("长方形和正方形的周长", "周长"),
    ("面积的意义", "面积和面积单位"),
    ("面积单位的换算", "面积单位间的进率"),
    ("复式统计表", "数据的收集与整理"),
    ("年、月、日", "年历中的秘密"),
    ("24时记时法", "作息时间表中的秘密"),
    ("一位小数的初步认识", "认识小数"),
    ("一位小数的加减", "简单的小数加、减法"),
]

EXISTING_XIA = [
    "cnm_p228", "cnm_p083", "cnm_p084", "cnm_p229", "cnm_p077", "cnm_p078",
    "cnm_p088", "cnm_p089", "cnm_p090", "cnm_p085", "cnm_p091", "cnm_p092",
    "cnm_p093", "cnm_p094", "cnm_p082",
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
        if old not in reason:
            continue
        if new in reason and old in new:
            pattern = "「" + re.escape(old) + "」"
            reason = re.sub(pattern, "「" + new + "」", reason)
        else:
            reason = reason.replace(old, new)
    doubles = [
        ("笔算除法的除法", "笔算除法"),
        ("多边形的认识", "多边形"),  # leftover
        ("面积和面积单位的意义", "面积和面积单位"),
        ("面积单位间的进率的换算", "面积单位间的进率"),
        ("年历中的秘密的秘密", "年历中的秘密"),
        ("认识小数的初步认识", "认识小数"),
        ("简单的小数加、减法的加减", "简单的小数加、减法"),
        ("数据的收集与整理表", "数据的收集与整理"),
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
        if t["id"] == "cnm_p280":
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

    new_deps = []
    for d in deps:
        d = dict(d)
        d["reason"] = replace_reason_names(d.get("reason", ""))
        new_deps.append(d)

    # Soften old hard p083<-p044 if 口算 now intermediates — keep hard on p044 via p282; make p083<-p044 soft
    for d in new_deps:
        if d["topicId"] == "cnm_p083" and d["prerequisiteId"] == "cnm_p044" and d["strength"] == "hard":
            d["strength"] = "soft"
            d["reason"] = "「用7～9的乘法口诀求商」对学习「笔算除法」有帮助，但不会前者也可以开始学后者。"

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

    for d in new_deps:
        r = d["reason"]
        for bad, good in [
            ("笔算除法的除法", "笔算除法"),
            ("认识认识小数", "认识小数"),
            ("年历中的秘密中的秘密", "年历中的秘密"),
            ("数据的收集与整理的收集与整理", "数据的收集与整理"),
        ]:
            if bad in r:
                d["reason"] = r.replace(bad, good)
                r = d["reason"]

    all_xia = EXISTING_XIA + [x["id"] for x in NEW_TOPICS]
    bank_qs = {}
    for tid in all_xia:
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
        if tid in EXISTING_XIA and tid not in seen:
            j = i
            while j < len(questions) and questions[j].get("topicId") == tid:
                j += 1
            out_q.extend(bank_qs[tid])
            seen.add(tid)
            i = j
        else:
            out_q.append(questions[i])
            i += 1

    leftover = set(EXISTING_XIA) - seen
    if leftover:
        raise SystemExit("未替换旧题：" + "、".join(sorted(leftover)))

    insert_q = len(out_q)
    for i, q in enumerate(out_q):
        if q.get("id") == "cnm_p280_q4":
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

    g3x = [t for t in topics if t.get("grade") == 3 and t.get("semester") == "下"
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

    print("三下", len(g3x))
    for t in sorted(g3x, key=lambda x: (x["chapter"], x["id"])):
        print(" ", t["id"], t["name"], "|", t["chapter"])
    print("小学", len(primary), "数学", len(math_topics))
    print("mathDeps", len(math_deps), "hard", hard, "soft", soft, "小学内部", len(pi))
    print("新增边", added)
    print("小学题", len(pq), "数学题", len(mq), "总题", len(out_q), "g3batch", len(g3_batch))
    bad = [d for d in new_deps if "的认识的认识" in d["reason"] or "笔算除法的除法" in d["reason"]]
    print("bad reasons", len(bad))
    for d in bad[:8]:
        print(" ", d["reason"][:80])


if __name__ == "__main__":
    main()
