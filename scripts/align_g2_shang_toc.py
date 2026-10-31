#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二上按人教版 2025 秋（dzkbw xs2s_2025）目录小节对齐。

改名/改挂已有点，新增 cnm_p261–cnm_p268，各 4 题；更新先修边。
题面写入后可再跑 g1_g2_g3_grade_align.py 同步 diagnostic 与 primary_g2。
"""
import json
import os
import sys
from copy import deepcopy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g123_bank_g2 import BANK as BANK_G2  # noqa: E402
from g1_g2_g3_grade_align import convert, c, n  # noqa: E402

NOTE = "依据 dzkbw xs2s_2025（2025 秋）小节补点。"

RENAMES = {
    "cnm_p038": {
        "name": "乘法的初步认识",
        "description": "知道乘法是求几个相同加数的和，认识乘号，会读写乘法算式。",
        "mastery_criteria": ["能把几个几写成乘法算式", "能说出乘号的读法"],
    },
    "cnm_p039": {
        "name": "2～6的乘法口诀",
        "description": "能熟记 2～6 的乘法口诀（含 5 的口诀、2、3、4 的口诀、6 的口诀），并用来计算。",
        "mastery_criteria": ["能背出 2～6 的口诀", "能用口诀算出积"],
    },
    "cnm_p057": {
        "name": "乘加、乘减",
        "description": "知道算式里有乘法和加减法时，先算乘法，再算加减法。",
        "mastery_criteria": ["能说出先乘后加减", "能正确计算乘加、乘减"],
    },
    "cnm_p048": {
        "name": "选择一种运算解决问题",
        "description": "能根据实际问题判断用加法还是乘法，并列出算式解决问题。",
        "mastery_criteria": ["能分清「几个几」用乘法、「合起来」用加法", "能列出算式并算出得数"],
        "type": "application",
    },
    "cnm_p046": {
        "name": "用2～6的乘法口诀求商",
        "description": "会用 2～6 的乘法口诀求商。",
        "mastery_criteria": ["能想口诀说出商", "能正确计算表内除法"],
    },
    "cnm_p047": {
        "name": "除法的基本应用",
        "description": "会用表内除法解决简单实际问题，并用「商×除数＝被除数」验算。",
        "mastery_criteria": ["能看懂平均分的问题并列式", "会用乘法验算除法"],
        "type": "application",
    },
    "cnm_p049": {
        "name": "认识东、南、西、北",
        "description": "认识东、南、西、北，给定一个方向能辨别其余三个。",
        "mastery_criteria": ["能指出东南西北四个方向", "知道东和西、南和北是相反方向"],
    },
    "cnm_p040": {
        "name": "认识厘米及用厘米量",
        "description": "认识长度单位厘米，会用直尺量整厘米的长度。",
        "mastery_criteria": ["知道 1 厘米大约多长", "会用直尺量整厘米"],
    },
    "cnm_p041": {
        "name": "认识米及用米量",
        "description": "认识米，知道 1 米＝100 厘米，会选择米或厘米来量。",
        "mastery_criteria": ["知道 1 米＝100 厘米", "能选择合适的单位"],
    },
    "cnm_p045": {
        "name": "寻找、测量、运用身体尺",
        "description": "会测量身体上的长度（一拃、一步等），并用来估测其他物体。",
        "mastery_criteria": ["能量出自己的一拃或一步大约多长", "会用身体尺估测并说明单位"],
        "domain": "综合与实践",
        "type": "modeling",
    },
    "cnm_p042": {
        "name": "7～9的乘法口诀",
        "description": "能熟记 7、8、9 的乘法口诀。",
        "mastery_criteria": ["能背出 7、8、9 的口诀", "能用口诀算出积"],
    },
    "cnm_p044": {
        "name": "用7～9的乘法口诀求商",
        "description": "会用 7、8、9 的乘法口诀求商。",
        "mastery_criteria": ["能想 7、8、9 的口诀说出商", "能正确计算"],
    },
    "cnm_p037": {
        "description": "能按给定标准或自选标准给物品分类，并用表格或数字记下每一类有多少。",
        "mastery_criteria": ["能说出分类标准（给定或自选）", "能数出每一类的个数并比较多少"],
    },
    "cnm_p043": {
        "description": "知道除法表示平均分，会读写除法算式，知道被除数、除数和商。",
        "mastery_criteria": ["能说出平均分要用除法", "会读除法算式并说出各部分名称"],
    },
}

CHAPTER_REPLACEMENTS = [
    ("二年级上册 第2单元 1到6的表内乘法", "二年级上册 第2单元 1～6的表内乘法"),
    ("二年级上册 第3单元 1到6的表内除法", "二年级上册 第3单元 1～6的表内除法"),
    ("二年级上册 第5单元 7到9的表内乘、除法", "二年级上册 第5单元 7～9的表内乘、除法"),
]

NEW_TOPICS = [
    {
        "id": "cnm_p261",
        "name": "逐层分类",
        "domain": "统计与概率",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第1单元 分类与整理",
        "type": "conceptual",
        "description": "能先按一个标准分类，再在某一类里按另一个标准继续分（逐层分类）。",
        "mastery_criteria": ["能说出每一层用的分类标准", "能数出最后一层每一类的个数"],
        "standards": [
            {"id": "cms-2022:1.SP.01", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:2.SP.01", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p262",
        "name": "用乘法解决购物问题",
        "domain": "数与代数",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第2单元 1～6的表内乘法",
        "type": "application",
        "description": "会用表内乘法解决「单价×数量」一类的购物问题，有时还要再加或再减。",
        "mastery_criteria": ["能看出相同加数用乘法算总价", "能算出应付或剩余的钱"],
        "standards": [
            {"id": "cms-2022:1.NA.05", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.07", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p263",
        "name": "平均分（包含）",
        "domain": "数与代数",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第3单元 1～6的表内除法",
        "type": "conceptual",
        "description": "知道「每几个一份」求能分成几份，是包含除意义的平均分。",
        "mastery_criteria": ["能说出每份几个、求份数", "能用圆片等分一分"],
        "standards": [
            {"id": "cms-2022:1.NA.03", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.05", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p264",
        "name": "平均分（等分）",
        "domain": "数与代数",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第3单元 1～6的表内除法",
        "type": "conceptual",
        "description": "知道「平均分成几份」求每份几个，是等分意义的平均分。",
        "mastery_criteria": ["能说出分成几份、求每份几个", "能把总数平均分成几份"],
        "standards": [
            {"id": "cms-2022:1.NA.03", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.05", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p265",
        "name": "认识线段",
        "domain": "图形与几何",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第4单元 厘米和米",
        "type": "conceptual",
        "description": "认识线段，知道线段有两个端点，会量整厘米的线段。",
        "mastery_criteria": ["能指出线段的两个端点", "会量线段的长度"],
        "standards": [
            {"id": "cms-2022:1.GG.02", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.GG.03", "confidence": "inferred", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p266",
        "name": "用估量解决问题",
        "domain": "图形与几何",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第4单元 厘米和米",
        "type": "application",
        "description": "会先估测物体大约多长，再选择米或厘米测量，并比较估的和量的结果。",
        "mastery_criteria": ["能先估再量", "能说出估的和量的大约差多少"],
        "standards": [
            {"id": "cms-2022:1.GG.02", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.GG.03", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p267",
        "name": "设计导游路线",
        "domain": "综合与实践",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 综合与实践 校园小导游",
        "type": "modeling",
        "description": "能根据东南西北设计简单的校园导游路线，并说出怎么走。",
        "mastery_criteria": ["能看图说出景点方向", "能说出转向后朝哪个方向"],
        "standards": [
            {"id": "cms-2022:1.IP.04", "confidence": "exact", "note": NOTE},
        ],
    },
    {
        "id": "cnm_p268",
        "name": "解决连续两问的问题",
        "domain": "数与代数",
        "grade": 2,
        "semester": "上",
        "chapter": "二年级上册 第5单元 7～9的表内乘、除法",
        "type": "application",
        "description": "会解决需要连续回答两个问题的表内乘除实际问题，如先求总数再求剩余。",
        "mastery_criteria": ["能分清先求什么、再求什么", "能分两步列出算式"],
        "standards": [
            {"id": "cms-2022:1.NA.05", "confidence": "exact", "note": NOTE},
            {"id": "cms-2022:1.NA.07", "confidence": "exact", "note": NOTE},
        ],
    },
]

NEW_EDGES = [
    ("cnm_p261", "cnm_p037", "hard", "学习「逐层分类」需要先掌握「分类与整理」。"),
    ("cnm_p262", "cnm_p039", "hard", "学习「用乘法解决购物问题」需要先掌握「2～6的乘法口诀」。"),
    ("cnm_p262", "cnm_p048", "hard", "学习「用乘法解决购物问题」需要先掌握「选择一种运算解决问题」。"),
    ("cnm_p263", "cnm_p038", "hard", "学习「平均分（包含）」需要先掌握「乘法的初步认识」。"),
    ("cnm_p264", "cnm_p038", "hard", "学习「平均分（等分）」需要先掌握「乘法的初步认识」。"),
    ("cnm_p043", "cnm_p263", "hard", "学习「除法的意义」需要先掌握「平均分（包含）」。"),
    ("cnm_p043", "cnm_p264", "hard", "学习「除法的意义」需要先掌握「平均分（等分）」。"),
    ("cnm_p265", "cnm_p040", "hard", "学习「认识线段」需要先掌握「认识厘米及用厘米量」。"),
    ("cnm_p266", "cnm_p041", "hard", "学习「用估量解决问题」需要先掌握「认识米及用米量」。"),
    ("cnm_p266", "cnm_p040", "soft", "「认识厘米及用厘米量」对学习「用估量解决问题」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p267", "cnm_p049", "hard", "学习「设计导游路线」需要先掌握「认识东、南、西、北」。"),
    ("cnm_p268", "cnm_p042", "hard", "学习「解决连续两问的问题」需要先掌握「7～9的乘法口诀」。"),
    ("cnm_p268", "cnm_p044", "hard", "学习「解决连续两问的问题」需要先掌握「用7～9的乘法口诀求商」。"),
    ("cnm_p045", "cnm_p266", "soft", "「用估量解决问题」对学习「寻找、测量、运用身体尺」有帮助，但不会前者也可以开始学后者。"),
    ("cnm_p099", "cnm_p265", "soft", "「认识线段」对学习「线段、直线和射线」有帮助，但不会前者也可以开始学后者。"),
]

# Remove cross-unit edge: 除法的基本应用(三单元) <- 用7～9求商(五单元)
REMOVE_EDGES = {
    ("cnm_p047", "cnm_p044"),
}

NAME_IN_REASON = [
    ("乘法的意义", "乘法的初步认识"),
    ("2到6的乘法口诀", "2～6的乘法口诀"),
    ("乘加乘减的运算顺序", "乘加、乘减"),
    ("表内乘法解决实际问题", "选择一种运算解决问题"),
    ("用1到6的口诀求商", "用2～6的乘法口诀求商"),
    ("用乘法验算除法", "除法的基本应用"),
    ("东、南、西、北", "认识东、南、西、北"),
    ("认识厘米", "认识厘米及用厘米量"),
    ("认识米", "认识米及用米量"),
    ("用身体上的长度估测", "寻找、测量、运用身体尺"),
    ("7、8、9的乘法口诀", "7～9的乘法口诀"),
    ("用7、8、9的口诀求商", "用7～9的乘法口诀求商"),
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


def main():
    topics = load("topics.json")
    deps = load("dependencies.json")
    questions = load("questions.json")
    by_id = {t["id"]: t for t in topics}

    # chapter renames for all 二上 topics
    for t in topics:
        ch = t.get("chapter") or ""
        for old, new in CHAPTER_REPLACEMENTS:
            if ch == old:
                t["chapter"] = new

    # field renames
    for tid, fields in RENAMES.items():
        t = by_id[tid]
        for k, v in fields.items():
            t[k] = v

    # insert new topics after cnm_p044 block area — append near end of cnm_p* before other subjects
    # Find insertion index: after last existing cnm_p260 or after cnm_p044's position
    insert_at = None
    for i, t in enumerate(topics):
        if t["id"] == "cnm_p260":
            insert_at = i + 1
            break
    if insert_at is None:
        insert_at = len(topics)

    new_topic_objs = []
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
        new_topic_objs.append(obj)
        by_id[spec["id"]] = obj
    for i, obj in enumerate(new_topic_objs):
        topics.insert(insert_at + i, obj)

    # refresh diagnostic for renamed bank topics
    for tid in list(RENAMES) + [x["id"] for x in NEW_TOPICS]:
        if tid in BANK_G2 and tid in by_id:
            dq, _ = dq_from_bank(tid)
            by_id[tid]["diagnostic_question"] = dq

    # dependencies: update reason text
    new_deps = []
    removed = 0
    for d in deps:
        key = (d["topicId"], d["prerequisiteId"])
        if key in REMOVE_EDGES:
            removed += 1
            continue
        reason = d.get("reason", "")
        for old, new in NAME_IN_REASON:
            if old in reason:
                reason = reason.replace(old, new)
        d = dict(d)
        d["reason"] = reason
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

    # questions: replace 二上 bank topics + append new
    shang_ids = [
        "cnm_p037", "cnm_p038", "cnm_p039", "cnm_p057", "cnm_p048", "cnm_p043",
        "cnm_p046", "cnm_p047", "cnm_p049", "cnm_p040", "cnm_p041", "cnm_p045",
        "cnm_p042", "cnm_p044",
    ] + [x["id"] for x in NEW_TOPICS]
    bank_qs = {}
    for tid in shang_ids:
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
        if tid in bank_qs and tid not in seen and tid in [
            "cnm_p037", "cnm_p038", "cnm_p039", "cnm_p057", "cnm_p048", "cnm_p043",
            "cnm_p046", "cnm_p047", "cnm_p049", "cnm_p040", "cnm_p041", "cnm_p045",
            "cnm_p042", "cnm_p044",
        ]:
            j = i
            while j < len(questions) and questions[j].get("topicId") == tid:
                j += 1
            out_q.extend(bank_qs[tid])
            seen.add(tid)
            i = j
        else:
            out_q.append(questions[i])
            i += 1

    # append new topic questions after last seen 二上 question (or after p260 qs)
    new_ids = [x["id"] for x in NEW_TOPICS]
    # find insert position: after cnm_p260_q4 if present, else end
    insert_q = len(out_q)
    for i, q in enumerate(out_q):
        if q.get("id") == "cnm_p260_q4":
            insert_q = i + 1
            break
    chunk = []
    for tid in new_ids:
        chunk.extend(bank_qs[tid])
    out_q[insert_q:insert_q] = chunk

    # primary_g2 batch
    g2_batch = [q for q in out_q if by_id.get(q["topicId"], {}).get("grade") == 2
                and str(q["topicId"]).startswith("cnm_")]

    dump_pretty("topics.json", topics)
    dump_pretty("dependencies.json", new_deps)
    dump_compact("questions.json", out_q)
    dump_pretty("_qbatches/primary_g2.json", g2_batch)

    g2s = [t for t in topics if t.get("grade") == 2 and t.get("semester") == "上"
           and str(t["id"]).startswith("cnm_p")]
    primary = [t for t in topics if t.get("grade") in range(1, 7) and str(t["id"]).startswith("cnm_p")]
    math_topics = [t for t in topics if str(t["id"]).startswith("cnm_")]
    math_deps = [d for d in new_deps if str(d["topicId"]).startswith("cnm_")
                 or str(d["prerequisiteId"]).startswith("cnm_")]
    # stricter: both ends math
    math_deps2 = [d for d in new_deps
                  if str(d["topicId"]).startswith("cnm_") and str(d["prerequisiteId"]).startswith("cnm_")]
    primary_internal = [d for d in math_deps2
                        if by_id.get(d["topicId"], {}).get("grade", 99) <= 6
                        and by_id.get(d["prerequisiteId"], {}).get("grade", 99) <= 6]
    hard = sum(1 for d in math_deps2 if d["strength"] == "hard")
    soft = sum(1 for d in math_deps2 if d["strength"] == "soft")
    pq = [q for q in out_q if str(q["topicId"]).startswith("cnm_p")]
    mq = [q for q in out_q if str(q["topicId"]).startswith("cnm_")]

    print("二上知识点", len(g2s), [t["id"] + " " + t["name"] for t in sorted(g2s, key=lambda x: x["id"])])
    print("小学数学", len(primary))
    print("数学知识点", len(math_topics))
    print("数学先修边(两端cnm_)", len(math_deps2), "hard", hard, "soft", soft)
    print("小学内部边", len(primary_internal))
    print("新增边", added, "删除边", removed)
    print("小学数学题", len(pq), "数学题", len(mq), "总题", len(out_q))
    print("primary_g2", len(g2_batch))


if __name__ == "__main__":
    main()
