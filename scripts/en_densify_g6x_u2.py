#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补六年级下册 Unit2 Last weekend 薄点，并加 Recycle 复习点（本地，不上线）。"""
from __future__ import annotations

import json
import os
import sys

# reuse helpers from sibling densify
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_densify_g46 import (  # noqa: E402
    load, dump, topic, four_qs, dep, insert_topics, NOTE6X,
)

CH = "六年级下册 第2单元 Last weekend"
CH_REV = "六年级下册 复习 Mike's happy days"
NOTE = "依据 dzkbw peps6x（现行六下）Unit2 Last weekend / Recycle 补点，待核。"


def build():
    topics, questions, deps = [], [], []

    topics.append(topic(
        "cne_p241", "周末活动词汇", "词汇", 6, "下", CH, "conceptual",
        "认读 cleaned my room、washed my clothes、stayed at home、had a cold、slept、read a book 等周末活动（Unit2 Part A/B）。",
        ["能选出周末活动短语的意思", "能根据中文选出英文短语"],
        ("「打扫房间」的过去式短语是？", "cleaned my room"),
        "ces-2022:2.VO.01", NOTE,
    ))
    questions += four_qs("cne_p241", [
        ("basic", "「打扫房间」的过去式短语是？", "cleaned my room",
         ["clean my room", "cleaning my room", "cleans my room"], "clean 的过去式是 cleaned。"),
        ("basic", "stayed at home 的意思是？", "待在家里", ["去了公园", "看了电影", "洗了衣服"], "stayed at home 是待在家里。"),
        ("standard", "「洗衣服」用哪一组？", "washed my clothes",
         ["wash my clothes yesterday", "washing clothes", "washes clothes"], "washed my clothes。"),
        ("standard", "had a cold 是在说什么？", "感冒了", ["很冷", "喝了冷饮", "去滑雪了"], "had a cold 是感冒了。"),
    ])
    deps += [
        dep("cne_p241", "cne_p185", "soft", "先接触规则动词过去式。"),
        dep("cne_p241", "cne_p189", "soft", "先接触不规则过去式。"),
    ]

    topics.append(topic(
        "cne_p242", "Did you 问周末活动", "语法", 6, "下", CH, "procedural",
        "用 Did you …? / Yes, I did. / No, I didn't. 询问和回答上周末是否做某事。",
        ["能选出正确的 Did 问句", "能用 did / didn't 简短回答"],
        ("想问「你上周末打扫房间了吗？」，应选哪一句？", "Did you clean your room last weekend?"),
        "ces-2022:2.GR.07", NOTE,
    ))
    questions += four_qs("cne_p242", [
        ("basic", "想问「你上周末打扫房间了吗？」，应选哪一句？", "Did you clean your room last weekend?",
         ["Did you cleaned your room last weekend?", "Do you cleaned your room?", "Did you cleaning your room?"],
         "Did + 主语 + 动词原形。"),
        ("basic", "—Did you stay at home? —Yes, I ____.", "did",
         ["do", "does", "didn't stay"], "肯定简答用 did。"),
        ("standard", "哪一句正确？", "Did they wash their clothes?",
         ["Did they washed their clothes?", "Did they washing?", "Do they washed?"],
         "Did 后用原形 wash。"),
        ("standard", "—Did you see a film? —No, I ____.", "didn't",
         ["did", "don't", "wasn't"], "否定简答用 didn't。"),
    ])
    deps += [
        dep("cne_p242", "cne_p186", "hard", "先会 Did 提问。"),
        dep("cne_p242", "cne_p241", "hard", "问句里要用周末活动词。"),
    ]

    topics.append(topic(
        "cne_p243", "How was your weekend", "日常表达", 6, "下", CH, "application",
        "用 How was your weekend? / It was good/fine/OK. / It wasn't good. 评价上周末。",
        ["能选出正确的评价问句和答句", "能读懂简短周末评价"],
        ("想问「你周末过得怎么样？」，应选哪一句？", "How was your weekend?"),
        "ces-2022:2.FU.02", NOTE,
    ))
    questions += four_qs("cne_p243", [
        ("basic", "想问「你周末过得怎么样？」，应选哪一句？", "How was your weekend?",
         ["How is your weekend yesterday?", "How were you weekend?", "How did your weekend?"],
         "How was your weekend?"),
        ("basic", "—How was your weekend? —It was good. 周末怎么样？", "很好",
         ["不好", "还没过", "不知道"], "It was good。"),
        ("standard", "哪一句评价上周末不好？", "It wasn't good.",
         ["It is tomorrow.", "It was a book.", "Yes, I do every day."], "wasn't good 表示不好。"),
        ("standard", "—How was your weekend? —____. I stayed at home and slept.", "It was OK",
         ["It is Monday", "I am a weekend", "Yes, I clean"], "用 It was … 评价。"),
    ])
    deps += [
        dep("cne_p243", "cne_p242", "soft", "先会问是否做某事，再评价周末。"),
        dep("cne_p243", "cne_p187", "hard", "与谈论上周末衔接。"),
    ]

    topics.append(topic(
        "cne_p244", "用过去式说周末安排", "日常表达", 6, "下", CH, "application",
        "综合用过去式说出上周末做了什么、没做什么，并简单评价。",
        ["能选出完整的周末经历句子", "能读懂简短周末对话"],
        ("想说「我上周末洗衣服了，很忙」，应选哪一句？", "I washed my clothes last weekend. It was busy."),
        "ces-2022:2.FU.02", NOTE,
    ))
    questions += four_qs("cne_p244", [
        ("basic", "想说「我上周末洗衣服了，很忙」，应选哪一句？", "I washed my clothes last weekend. It was busy.",
         ["I wash my clothes last weekend.", "I washing clothes yesterday.", "I washes my clothes."],
         "过去式 washed；评价 It was busy。"),
        ("basic", "I didn't go out. I had a cold. 我怎么了？", "感冒了，没出门",
         ["去看电影了", "去公园了", "很开心出门"], "had a cold; didn't go out。"),
        ("standard", "哪一组能完整谈上周末？", "I cleaned my room. It was good.",
         ["I clean my room tomorrow.", "I cleaning now only.", "Clean room I yesterday."],
         "过去式 + 评价。"),
        ("standard", "—What did you do last weekend? —____.", "I read a book at home.",
         ["I read a book tomorrow.", "I reading a book now every day.", "I reads a book."],
         "用过去式回答。"),
    ])
    deps += [
        dep("cne_p244", "cne_p241", "hard", "先认周末活动词。"),
        dep("cne_p244", "cne_p243", "hard", "先会评价周末。"),
        dep("cne_p244", "cne_p187", "hard", "与谈论上周末综合。"),
    ]

    # Recycle
    topics.append(topic(
        "cne_p245", "复习：Mike 的快乐日子", "读写", 6, "下", CH_REV, "application",
        "综合复习比较级、上周末和假期旅行：读 Mike's happy days 类短文，找出身高比较、周末活动和旅行经历。",
        ["能根据短文选出比较或过去经历信息", "能选出和短文一致的句子"],
        ("读一读：Mike is taller than before. Last weekend he cleaned his room. 迈克上周末做什么？", "打扫房间"),
        "ces-2022:2.RW.01", NOTE,
    ))
    questions += four_qs("cne_p245", [
        ("basic", "读一读：Mike is taller than before. Last weekend he cleaned his room. 迈克上周末做什么？", "打扫房间",
         ["去旅行", "洗衣服", "看电影"], "cleaned his room。"),
        ("basic", "读一读：He went to the park and rode a bike. 他去了哪里？", "公园",
         ["学校", "医院", "商店"], "went to the park。"),
        ("standard", "读一读：Mike was short then. Now he is taller than his friend. 哪一句一致？", "迈克现在比朋友高。",
         ["迈克现在更矮。", "迈克没有朋友。", "迈克从不长高。"], "taller than his friend。"),
        ("standard", "读一读：Over the holiday Mike went to Sanya with his parents. 假期他和谁去的？", "父母",
         ["老师", "同学", "独自一人"], "with his parents。"),
    ])
    deps += [
        dep("cne_p245", "cne_p183", "soft", "先会询问身高比较。"),
        dep("cne_p245", "cne_p244", "soft", "先会说周末安排。"),
        dep("cne_p245", "cne_p227", "soft", "先会谈论假期旅行。"),
    ]

    return topics, questions, deps


def main():
    topics = load("topics.json")
    questions = load("questions.json")
    deps = load("dependencies.json")

    existing = {t["id"] for t in topics}
    new_topics, new_qs, new_deps = build()
    new_topics = [t for t in new_topics if t["id"] not in existing]
    if not new_topics:
        print("已存在新点，跳过写入。")
        return

    topics = insert_topics(topics, new_topics)
    # also wire soft dep from existing 读懂日记 onto new talking point
    q_ids = {q["id"] for q in questions}
    questions.extend([q for q in new_qs if q["id"] not in q_ids])
    dep_keys = {(d["topicId"], d["prerequisiteId"]) for d in deps}
    for d in new_deps:
        if (d["topicId"], d["prerequisiteId"]) not in dep_keys:
            deps.append(d)

    # existing 读懂上周末日记 可软依赖新的周末活动词
    extra = dep("cne_p188", "cne_p241", "soft", "读日记前先认周末活动词。")
    if (extra["topicId"], extra["prerequisiteId"]) not in dep_keys:
        deps.append(extra)

    dump("topics.json", topics)
    dump("questions.json", questions)
    dump("dependencies.json", deps)

    eng = [t for t in topics if str(t["id"]).startswith("cne_p")]
    u2 = [t for t in eng if t.get("chapter") == CH]
    rev = [t for t in eng if t.get("chapter") == CH_REV]
    print("新增", len(new_topics), "小学英语现", len(eng))
    print("六下 Unit2", len(u2), [t["name"] for t in u2])
    print("Recycle", len(rev), [t["name"] for t in rev])


if __name__ == "__main__":
    main()
