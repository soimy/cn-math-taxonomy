#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二下按人教版 2026 春（dzkbw xs2x_2026）目录小节对齐。"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g123_bank_g2 import BANK as BANK_G2  # noqa: E402
from g1_g2_g3_grade_align import convert  # noqa: E402

NOTE = "依据 dzkbw xs2x_2026（2026 春）小节补点。"

RENAMES = {
    "cnm_p050": {
        "name": "有余数的除法",
        "description": "认识有余数的除法，知道余数必须比除数小，会写出商和余数。",
        "mastery_criteria": ["能说出余数比除数小", "能写出有余数除法的商和余数"],
    },
    "cnm_p061": {
        "name": "认识时间",
        "description": "认识时间单位秒，知道秒针走一圈是 1 分，能进行分与秒的简单换算。",
        "mastery_criteria": ["能说出 1 分等于 60 秒", "能把几分换算成秒"],
        "domain": "综合与实践",
        "type": "conceptual",
        "standards": [
            {"id": "cms-2022:1.IP.03", "confidence": "exact", "note": NOTE},
        ],
    },
    "cnm_p063": {
        "name": "我与时间的故事",
        "description": "能结合生活故事计算经过的时间，并用时、分说出自己的时间经历。",
        "mastery_criteria": ["能算出同一时内经过多少分", "能说出跨过整点时经过多少分"],
        "domain": "综合与实践",
        "type": "application",
    },
    "cnm_p053": {
        "name": "1000以内数的认识",
        "description": "能认、读、写 1000 以内的数，知道百位、十位、个位，认识 1000。",
        "mastery_criteria": ["能读出 1000 以内的数", "知道 999 的后面是 1000"],
    },
    "cnm_p071": {
        "name": "加法",
        "description": "会用竖式计算三位数加三位数（含连续进位），解决万以内加法问题。",
        "mastery_criteria": ["能把相同数位对齐", "连续进位时不错位"],
    },
    "cnm_p072": {
        "name": "减法",
        "description": "会用竖式计算三位数减三位数（含连续退位），解决万以内减法问题。",
        "mastery_criteria": ["能把相同数位对齐", "连续退位时不错位"],
    },
    "cnm_p060": {
        "description": "能发现一列数每次增加或减少相同的数，并写出后面的数。暂挂「复习与关联·应用提升」，新版目录未单列变化规律，待核。",
        "chapter": "二年级下册 第5单元 复习与关联",
    },
    "cnm_p062": {
        "domain": "综合与实践",
    },
}

NEW_TOPICS = [
    {
        "id": "cnm_p269",
        "name": "10000以内数的认识",
        "domain": "数与代数",
        "grade": 2,
        "semester": "下",
        "chapter": "二年级下册 第3单元 万以内数的认识",
        "type": "conceptual",
        "description": "能认、读、写 10000 以内的数，知道千位，认识 10000（1 万）。",
        "mastery_criteria": ["能读出四位数", "知道 9999 的后面是 10000"],
        "standards": [
            {"id": "cms-2022:1.NA.01", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p270",
        "name": "简单的加、减法",
        "domain": "数与代数",
        "grade": 2,
        "semester": "下",
        "chapter": "二年级下册 第3单元 万以内数的认识",
        "type": "procedural",
        "description": "会计算整千、整百的简单加减（如 3000＋2000、4500＋300），体会数的组成。",
        "mastery_criteria": ["能算整千数加减", "能算整百数加在四位数上"],
        "standards": [
            {"id": "cms-2022:1.NA.04", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.01", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p271",
        "name": "数独游戏",
        "domain": "数与代数",
        "grade": 2,
        "semester": "下",
        "chapter": "二年级下册 第4单元 万以内的加法和减法",
        "type": "reasoning",
        "description": "会在简单数独（或填数）游戏中，根据「每行每列数字不重复」推出空格里的数。",
        "mastery_criteria": ["知道一行里的数一般不重复", "能根据已有数字推出空格"],
        "standards": [
            {"id": "cms-2022:1.NA.06", "confidence": "inferred", "note": NOTE},
            {"id": "cms-2022:1.NA.02", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p272",
        "name": "连环画分享会",
        "domain": "综合与实践",
        "grade": 2,
        "semester": "下",
        "chapter": "二年级下册 综合与实践 数学连环画",
        "type": "modeling",
        "description": "能用连环画讲简单的乘除或加减故事，并写出对应的算式。",
        "mastery_criteria": ["能给故事配上合适的算式", "能看连环画说出用乘法还是除法"],
        "standards": [
            {"id": "cms-2022:1.IP.06", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.07", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p273",
        "name": "我的时间小书",
        "domain": "综合与实践",
        "grade": 2,
        "semester": "下",
        "chapter": "二年级下册 综合与实践 时间在哪里",
        "type": "modeling",
        "description": "会记录一天里各件事用的时间，整理成「时间小书」，并进行简单加减或换算。",
        "mastery_criteria": ["能记录两件事各用多少分", "能算出合计或相差的时间"],
        "standards": [
            {"id": "cms-2022:1.IP.03", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.IP.06", "confidence": "inferred", "note": NOTE},
        ],
    },
]

NEW_EDGES = [
    ("cnm_p269", "cnm_p053", "hard", "学习「10000以内数的认识」需要先掌握「1000以内数的认识」。"),
    ("cnm_p054", "cnm_p269", "soft", "「10000以内数的认识」对学习「万以内数的大小比较」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p055", "cnm_p269", "soft", "「10000以内数的认识」对学习「万以内数的组成」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p270", "cnm_p053", "hard", "学习「简单的加、减法」需要先掌握「1000以内数的认识」。"),
    ("cnm_p270", "cnm_p269", "hard", "学习「简单的加、减法」需要先掌握「10000以内数的认识」。"),
    ("cnm_p064", "cnm_p270", "soft", "「简单的加、减法」对学习「几百几十的口算加法」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p271", "cnm_p054", "hard", "学习「数独游戏」需要先掌握「万以内数的大小比较」。"),
    ("cnm_p271", "cnm_p055", "soft", "「万以内数的组成」对学习「数独游戏」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p272", "cnm_p219", "hard", "学习「连环画分享会」需要先掌握「数量间的乘除关系」。"),
    ("cnm_p272", "cnm_p048", "soft", "「选择一种运算解决问题」对学习「连环画分享会」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p273", "cnm_p062", "hard", "学习「我的时间小书」需要先掌握「时、分、秒的进率」。"),
    ("cnm_p273", "cnm_p063", "soft", "「我与时间的故事」对学习「我的时间小书」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p096", "cnm_p269", "soft", "「10000以内数的认识」对学习「亿以内数的认识」有帮助，但不会前者也可以开始学后者。"),
]

NAME_IN_REASON = [
    ("有余数除法的意义", "有余数的除法"),
    ("秒的认识", "认识时间"),
    ("经过时间", "我与时间的故事"),
    ("万以内数的认识", "1000以内数的认识"),
    ("三位数加法笔算", "加法"),
    ("三位数减法笔算", "减法"),
]

EXISTING_XIA = [
    "cnm_p050", "cnm_p051", "cnm_p052", "cnm_p219", "cnm_p053", "cnm_p054", "cnm_p055",
    "cnm_p064", "cnm_p065", "cnm_p066", "cnm_p071", "cnm_p072", "cnm_p220",
    "cnm_p061", "cnm_p062", "cnm_p063", "cnm_p060",
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
    rows = [convert(r) for r in BANK_G2[tid]]
    q1 = rows[0]
    if q1["type"] == "choice":
        ans = [x["text"] for x in q1["choices"] if x["key"] == q1["answer"]][0]
    else:
        ans = str(q1["answer"])
    return {"question": q1["prompt"], "answer": ans}, rows


def replace_reason_names(reason):
    # Apply longer keys first to avoid partial double-replace issues
    for old, new in sorted(NAME_IN_REASON, key=lambda x: -len(x[0])):
        if old in reason and new not in reason:
            reason = reason.replace(old, new)
        elif old in reason and new in reason:
            # already updated fragment nearby — only replace standalone old if not part of new
            pass
        else:
            reason = reason.replace(old, new)
    # Fix accidental doubles if any
    reason = reason.replace("1000以内数的认识以内", "1000以内数的认识")
    # Special: 「万以内数的认识」→「1000以内数的认识」 but edges to p053 that should mention 1000
    # Edges that meant general 万以内 for p096 etc. — soft add p269 separately
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

    # insert new topics after p268
    insert_at = None
    for i, t in enumerate(topics):
        if t["id"] == "cnm_p268":
            insert_at = i + 1
            break
    if insert_at is None:
        for i, t in enumerate(topics):
            if t["id"] == "cnm_p260":
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
        if tid in BANK_G2 and tid in by_id:
            dq, _ = dq_from_bank(tid)
            by_id[tid]["diagnostic_question"] = dq

    # deps
    new_deps = []
    for d in deps:
        d = dict(d)
        d["reason"] = replace_reason_names(d.get("reason", ""))
        # Fix specific: p096 <- p053 reason should stay about 1000以内 as foundation for 亿
        # After replace it becomes 1000以内 which is correct enough
        new_deps.append(d)

    # Careful fix: edges that said 万以内数的认识 for p053 prerequisite text
    # replace_reason_names already mapped.
    # But p054 <- p053: 「学习「万以内数的大小比较」需要先掌握「1000以内数的认识」」OK
    # p064 <- p053 similarly OK
    # p076, p096, p201: learning higher numbers from 1000以内 is OK; soft p269 added for p096

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

    # Also fix reasons that incorrectly doubled
    for d in new_deps:
        r = d["reason"]
        for bad, good in [
            ("1000以内数的认识以内数的认识", "1000以内数的认识"),
            ("认识时间的认识", "认识时间"),
            ("有余数的除法的除法", "有余数的除法"),
        ]:
            if bad in r:
                d["reason"] = r.replace(bad, good)

    # questions
    all_xia = EXISTING_XIA + [x["id"] for x in NEW_TOPICS]
    bank_qs = {}
    for tid in all_xia:
        rows = [convert(r) for r in BANK_G2[tid]]
        items = []
        for i, q in enumerate(rows, 1):
            item = dict(q)
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
        if q.get("id") == "cnm_p268_q4":
            insert_q = i + 1
            break
    chunk = []
    for tid in [x["id"] for x in NEW_TOPICS]:
        chunk.extend(bank_qs[tid])
    out_q[insert_q:insert_q] = chunk

    g2_batch = [q for q in out_q if by_id.get(q["topicId"], {}).get("grade") == 2
                and str(q["topicId"]).startswith("cnm_")]

    dump_pretty("topics.json", topics)
    dump_pretty("dependencies.json", new_deps)
    dump_compact("questions.json", out_q)
    dump_pretty("_qbatches/primary_g2.json", g2_batch)

    g2x = [t for t in topics if t.get("grade") == 2 and t.get("semester") == "下"
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

    print("二下", len(g2x), [t["id"] + " " + t["name"] for t in sorted(g2x, key=lambda x: x["id"])])
    print("小学", len(primary), "数学", len(math_topics))
    print("mathDeps", len(math_deps), "hard", hard, "soft", soft, "小学内部", len(pi))
    print("新增边", added)
    print("小学题", len(pq), "数学题", len(mq), "总题", len(out_q), "g2batch", len(g2_batch))
    # check reason doubles
    bad = [d for d in new_deps if "以内数的认识以内" in d["reason"] or "的除法的除法" in d["reason"]]
    print("bad reasons", len(bad))
    for d in new_deps:
        if "万以内数的认识" in d.get("reason", ""):
            print("still 万以内认识:", d["topicId"], d["prerequisiteId"], d["reason"][:70])


if __name__ == "__main__":
    main()
