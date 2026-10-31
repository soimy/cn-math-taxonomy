#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小学英语四上/四下/六上/六下按 dzkbw PEP 目录 densify（本地，不上线）。

- 四上 2025秋 pep4s_2025：按 Part A/B/C/Reading 补点，24→约 38
- 四下 2026春 pep4x_2026：对齐单元名 On the farm；补薄单元
- 六上 2026秋 pep6s_2026：补 Healthy life 等薄单元
- 六下现行 peps6x：补 Unit3 Where did you go（现缺）
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

NOTE4S = "依据 dzkbw pep4s_2025（2025 秋）Part A/B/C/Reading 补点，待核。"
NOTE4X = "依据 dzkbw pep4x_2026（2026 春）单元目录补点，待核。"
NOTE6S = "依据 dzkbw pep6s_2026（2026 秋）单元目录补点，待核。"
NOTE6X = "依据 dzkbw peps6x（现行六下）Unit3 Where did you go 补点，待核。"


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def dump(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def std(sid, note):
    return [{"id": sid, "confidence": "inferred", "note": note}]


def topic(tid, name, domain, grade, sem, chapter, typ, desc, criteria, dq, sid, note):
    return {
        "id": tid,
        "name": name,
        "domain": domain,
        "grade": grade,
        "semester": sem,
        "chapter": chapter,
        "type": typ,
        "description": desc,
        "mastery_criteria": criteria,
        "diagnostic_question": {"question": dq[0], "answer": dq[1]},
        "external": False,
        "subject": "english",
        "standards": std(sid, note),
    }


def choice_q(tid, n, diff, prompt, answer_text, wrongs, expl):
    opts = [answer_text] + list(wrongs)
    # rotate so answer letter varies by n
    shift = (n - 1) % 4
    ordered = opts[shift:] + opts[:shift]
    keys = "ABCD"
    answer_key = keys[ordered.index(answer_text)]
    return {
        "id": "%s_q%d" % (tid, n),
        "topicId": tid,
        "difficulty": diff,
        "type": "choice",
        "prompt": prompt,
        "choices": [{"key": k, "text": t} for k, t in zip(keys, ordered)],
        "answer": answer_key,
        "explanation": expl,
        "verify": json.dumps(answer_text, ensure_ascii=False),
    }


def four_qs(tid, items):
    """items: list of (diff, prompt, answer, wrongs, expl) length 4."""
    out = []
    for i, (diff, prompt, answer, wrongs, expl) in enumerate(items, 1):
        out.append(choice_q(tid, i, diff, prompt, answer, wrongs, expl))
    return out


def dep(tid, pre, strength, reason):
    return {
        "topicId": tid,
        "prerequisiteId": pre,
        "strength": strength,
        "reason": reason,
    }


CH4 = {
    1: "四年级上册 第1单元 Helping at home",
    2: "四年级上册 第2单元 My friends",
    3: "四年级上册 第3单元 Places we live in",
    4: "四年级上册 第4单元 Helping in the community",
    5: "四年级上册 第5单元 The weather and us",
    6: "四年级上册 第6单元 Changing for the seasons",
    "rev": "四年级上册 复习 Let's help!",
}
CH4X = {
    2: "四年级下册 第2单元 Family rules",
    5: "四年级下册 第5单元 Farms and us",
    6: "四年级下册 第6单元 On the farm",
}
CH6S = {
    2: "六年级上册 第2单元 Getting together",
    3: "六年级上册 第3单元 Healthy life",
    4: "六年级上册 第4单元 Managing money well",
    5: "六年级上册 第5单元 Exploring space",
}
CH6X3 = "六年级下册 第3单元 Where did you go"


def build_new():
    topics = []
    questions = []
    deps = []

    # ---------- 四上 densify (+14) ----------
    # U1 Part B/C
    topics.append(topic(
        "cne_p209", "家务活动", "词汇", 4, "上", CH4[1], "conceptual",
        "认读 cook、clean、wash、sweep 等家务活动词（Part B How can we help our family?）。",
        ["能选出家务活动词的中文意思", "能根据中文选出英文单词"],
        ("哪个单词的意思是「打扫」？", "clean"),
        "ces-2022:1.VO.01", NOTE4S,
    ))
    questions += four_qs("cne_p209", [
        ("basic", "哪个单词的意思是「打扫」？", "clean", ["cook", "wash", "sweep"], "clean 是打扫。"),
        ("basic", "cook 的意思是？", "做饭", ["洗碗", "扫地", "擦桌子"], "cook 是做饭。"),
        ("standard", "「洗碗」用哪个词最合适？", "wash", ["cook", "sweep", "make"], "wash the dishes 是洗碗。"),
        ("standard", "sweep the floor 是在做什么？", "扫地", ["做饭", "洗碗", "擦桌子"], "sweep the floor 是扫地。"),
    ])
    deps += [dep("cne_p209", "cne_p080", "soft", "先认识家人职业，再学家务活动词。")]

    topics.append(topic(
        "cne_p210", "帮忙做家务", "日常表达", 4, "上", CH4[1], "application",
        "用 I can help … / Let me … 说自己能帮家里做什么（Part B）。",
        ["能选出正确的帮忙句子", "能读懂帮忙做家务的对话"],
        ("想说「我可以帮忙做饭」，应选哪一句？", "I can help cook."),
        "ces-2022:1.FU.02", NOTE4S,
    ))
    questions += four_qs("cne_p210", [
        ("basic", "想说「我可以帮忙做饭」，应选哪一句？", "I can help cook.",
         ["I can help cooks.", "I help can cook.", "I am help cook."], "帮忙做某事用 I can help + 动词原形。"),
        ("basic", "Let me wash the dishes. 这句是在说什么？", "让我来洗碗",
         ["让我来扫地", "让我来做饭", "请你洗碗"], "wash the dishes 是洗碗。"),
        ("standard", "哪一句表示主动帮忙打扫？", "I can help clean.",
         ["I can help cooking.", "I helps clean.", "Can I helping clean?"], "help 后用动词原形 clean。"),
        ("standard", "Mum is busy. I can ____. 横线上最合适的是？", "help her",
         ["helps her", "helping her", "to help she"], "can 后用动词原形 help。"),
    ])
    deps += [
        dep("cne_p210", "cne_p209", "hard", "先认家务词，再说帮忙句子。"),
        dep("cne_p210", "cne_p082", "soft", "先会介绍家人，再谈帮忙。"),
    ]

    topics.append(topic(
        "cne_p211", "读懂快乐家庭介绍", "读写", 4, "上", CH4[1], "application",
        "读家庭海报或短介绍，找出家人和他们做的家务（Part C / Reading time）。",
        ["能根据短文选出家人做的事", "能选出和短文一致的句子"],
        ("读一读：My dad can cook. My mum can clean. 谁会做饭？", "爸爸"),
        "ces-2022:1.RW.02", NOTE4S,
    ))
    questions += four_qs("cne_p211", [
        ("basic", "读一读：My dad can cook. My mum can clean. 谁会做饭？", "爸爸",
         ["妈妈", "我", "哥哥"], "dad can cook。"),
        ("basic", "读一读：I help wash the dishes every day. 我每天做什么？", "洗碗",
         ["扫地", "做饭", "擦桌子"], "wash the dishes 是洗碗。"),
        ("standard", "读一读：We are a happy family. Dad cooks. Mum cleans. I sweep. 哪一句和短文一致？", "我扫地。",
         ["妈妈做饭。", "爸爸扫地。", "我不帮忙。"], "I sweep 是扫地。"),
        ("standard", "读一读：Amy helps her family. She can cook and wash. 艾米会做什么？", "做饭和洗碗",
         ["只做饭", "只扫地", "只擦桌子"], "cook and wash。"),
    ])
    deps += [dep("cne_p211", "cne_p210", "hard", "读懂帮忙介绍前先会帮忙句。")]

    # U2 Part B/C
    topics.append(topic(
        "cne_p212", "朋友的品质", "词汇", 4, "上", CH4[2], "conceptual",
        "认读 kind、helpful、funny、honest 等选择朋友时的品质词（Part B）。",
        ["能选出品质词的意思", "能根据中文选出英文单词"],
        ("哪个单词的意思是「友好善良的」？", "kind"),
        "ces-2022:1.VO.01", NOTE4S,
    ))
    questions += four_qs("cne_p212", [
        ("basic", "哪个单词的意思是「友好善良的」？", "kind", ["funny", "tall", "quiet"], "kind 是善良友好的。"),
        ("basic", "helpful 的意思是？", "乐于助人的", ["有趣的", "诚实的", "安静的"], "helpful 是乐于助人。"),
        ("standard", "「有趣的」用哪个词？", "funny", ["kind", "honest", "helpful"], "funny 是有趣的。"),
        ("standard", "He is honest. 他怎么样？", "诚实", ["有趣", "强壮", "安静"], "honest 是诚实。"),
    ])
    deps += [dep("cne_p212", "cne_p067", "soft", "先会描述朋友，再学品质词。")]

    topics.append(topic(
        "cne_p213", "介绍并选择朋友", "日常表达", 4, "上", CH4[2], "application",
        "用 He/She is … 说明为什么选某人为朋友，并读懂朋友小书要点（Part B/C）。",
        ["能选出介绍朋友品质的句子", "能读懂选择朋友的理由"],
        ("想说「她乐于助人」，应选哪一句？", "She is helpful."),
        "ces-2022:1.FU.02", NOTE4S,
    ))
    questions += four_qs("cne_p213", [
        ("basic", "想说「她乐于助人」，应选哪一句？", "She is helpful.",
         ["She is help.", "She helpful is.", "She are helpful."], "She is + 形容词。"),
        ("basic", "I choose him because he is kind. 我选他的原因是？", "他善良",
         ["他很高", "他很安静", "他有眼镜"], "because he is kind。"),
        ("standard", "哪一句适合写进朋友小书？", "My friend is funny and kind.",
         ["My friend is a book.", "My friend are funny.", "Friend my is kind."], "用 is 连接品质词。"),
        ("standard", "She is honest and helpful. 哪一句意思相同？", "她诚实而且乐于助人。",
         ["她有趣而且安静。", "她强壮而且高。", "他诚实。"], "honest and helpful，主语 She。"),
    ])
    deps += [
        dep("cne_p213", "cne_p212", "hard", "先认品质词，再用来介绍朋友。"),
        dep("cne_p213", "cne_p069", "soft", "先会介绍朋友。"),
    ]

    # U3 Part A/B
    topics.append(topic(
        "cne_p214", "社区场所", "词汇", 4, "上", CH4[3], "conceptual",
        "认读 park、shop、hospital、library 等社区场所词（Part A What can we see in a community?）。",
        ["能选出场所词的中文意思", "能根据中文选出英文单词"],
        ("哪个单词的意思是「医院」？", "hospital"),
        "ces-2022:1.VO.01", NOTE4S,
    ))
    questions += four_qs("cne_p214", [
        ("basic", "哪个单词的意思是「医院」？", "hospital", ["park", "shop", "library"], "hospital 是医院。"),
        ("basic", "library 的意思是？", "图书馆", ["公园", "商店", "学校"], "library 是图书馆。"),
        ("standard", "「公园」用哪个词？", "park", ["shop", "hospital", "zoo"], "park 是公园。"),
        ("standard", "We can buy things in a ____.", "shop", ["park", "hospital", "library"], "商店是 shop。"),
    ])
    deps += [dep("cne_p214", "cne_p072", "soft", "先认识家里的房间，再学社区场所。")]

    topics.append(topic(
        "cne_p215", "社区里人们做什么", "日常表达", 4, "上", CH4[3], "application",
        "说社区里人们在公园、商店、医院等做什么（Part B）。",
        ["能选出与场所匹配的活动句", "能读懂社区短句"],
        ("在图书馆人们常常做什么？", "read books"),
        "ces-2022:1.FU.03", NOTE4S,
    ))
    questions += four_qs("cne_p215", [
        ("basic", "在图书馆人们常常做什么？", "read books",
         ["see a doctor", "buy food", "play football"], "图书馆读书。"),
        ("basic", "People see a doctor in the hospital. 人们在哪里看病？", "医院",
         ["公园", "商店", "图书馆"], "hospital 是医院。"),
        ("standard", "哪一句和「在公园玩耍」意思相同？", "People play in the park.",
         ["People play in the shop.", "People read in the park.", "People cook in the park."], "play in the park。"),
        ("standard", "We buy fruit in the shop. 我们在商店做什么？", "买水果",
         ["看病", "读书", "踢球"], "buy fruit 是买水果。"),
    ])
    deps += [dep("cne_p215", "cne_p214", "hard", "先认社区场所，再说人们做什么。")]

    # U4 Part B/C
    topics.append(topic(
        "cne_p216", "年轻人如何帮助社区", "日常表达", 4, "上", CH4[4], "application",
        "用 We can help … 说年轻人能为社区做什么（Part B）。",
        ["能选出帮助社区的句子", "能读懂帮助社区的短句"],
        ("想说「我们可以帮助打扫公园」，应选哪一句？", "We can help clean the park."),
        "ces-2022:1.FU.02", NOTE4S,
    ))
    questions += four_qs("cne_p216", [
        ("basic", "想说「我们可以帮助打扫公园」，应选哪一句？", "We can help clean the park.",
         ["We can help cleans the park.", "We help can clean the park.", "We are help the park."],
         "can help + 动词原形。"),
        ("basic", "We can help at the library. 这句是在说什么？", "我们可以在图书馆帮忙",
         ["我们可以在医院帮忙", "我们在商店买书", "我们打扫公园"], "at the library。"),
        ("standard", "哪一句表示帮助社区？", "We can help old people.",
         ["We can help cooks.", "We helps old people.", "Can we helping?"], "help old people。"),
        ("standard", "Young people can ____ in the community.", "help",
         ["helps", "helping", "to help"], "can 后用动词原形。"),
    ])
    deps += [
        dep("cne_p216", "cne_p210", "soft", "先会帮忙做家务，再谈帮忙社区。"),
        dep("cne_p216", "cne_p084", "soft", "先认识学校/社区场所。"),
    ]

    topics.append(topic(
        "cne_p217", "读懂学校帮手介绍", "读写", 4, "上", CH4[4], "application",
        "读学校帮手海报或短文，找出谁在帮忙、帮什么（Part C Project）。",
        ["能根据短文选出帮手和职责", "能选出和短文一致的句子"],
        ("读一读：Miss White is a school helper. She helps in the library. 怀特老师在哪里帮忙？", "图书馆"),
        "ces-2022:1.RW.02", NOTE4S,
    ))
    questions += four_qs("cne_p217", [
        ("basic", "读一读：Miss White is a school helper. She helps in the library. 怀特老师在哪里帮忙？", "图书馆",
         ["医院", "公园", "商店"], "in the library。"),
        ("basic", "读一读：Tom helps clean the playground. 汤姆帮忙做什么？", "打扫操场",
         ["做饭", "买东西", "看病"], "clean the playground。"),
        ("standard", "读一读：Our school helpers are kind. They help teachers and students. 哪一句和短文一致？", "学校帮手很善良。",
         ["学校帮手不帮忙。", "老师不需要帮手。", "学生不能帮忙。"], "helpers are kind。"),
        ("standard", "读一读：Amy is a helper. She can help at the school gate. 艾米在哪里帮忙？", "校门口",
         ["图书馆", "教室", "食堂"], "at the school gate。"),
    ])
    deps += [dep("cne_p217", "cne_p216", "hard", "读懂帮手介绍前先会说帮忙。")]

    # U5 Part B/C
    topics.append(topic(
        "cne_p218", "不同天气做什么", "日常表达", 4, "上", CH4[5], "application",
        "根据天气说出适宜活动，如 rainy → stay inside（Part B）。",
        ["能选出与天气匹配的活动", "能读懂天气建议句"],
        ("下雨天适合做什么？", "stay inside"),
        "ces-2022:1.FU.03", NOTE4S,
    ))
    questions += four_qs("cne_p218", [
        ("basic", "下雨天适合做什么？", "stay inside",
         ["fly a kite", "have a picnic", "swim outside"], "rainy → stay inside。"),
        ("basic", "It's sunny. We can ____.", "play outside",
         ["stay in bed all day", "take an umbrella only", "close all windows forever"], "晴天可 outdoors 玩。"),
        ("standard", "哪一句适合大风天？", "Don't fly a kite.",
         ["Let's have a picnic.", "Let's go swimming outside.", "Open all the windows."], "大风不宜放风筝。"),
        ("standard", "It's snowy. We can make a snowman. 天气怎么样？", "下雪",
         ["下雨", "晴天", "多云"], "snowy 是下雪。"),
    ])
    deps += [
        dep("cne_p218", "cne_p092", "hard", "先会天气词，再说不同天气做什么。"),
        dep("cne_p218", "cne_p094", "soft", "先会谈天气建议。"),
    ]

    topics.append(topic(
        "cne_p219", "恶劣天气提醒", "读写", 4, "上", CH4[5], "application",
        "读坏天气提醒卡，找出要注意的事（Part C Project）。",
        ["能根据提醒卡选出正确做法", "能选出和文字一致的句子"],
        ("读一读：Rainy day! Take an umbrella. 下雨天要带什么？", "雨伞"),
        "ces-2022:1.RW.02", NOTE4S,
    ))
    questions += four_qs("cne_p219", [
        ("basic", "读一读：Rainy day! Take an umbrella. 下雨天要带什么？", "雨伞",
         ["太阳镜", "风筝", "雪人"], "umbrella 是雨伞。"),
        ("basic", "读一读：Windy! Don't fly a kite near the road. 大风天不要做什么？", "在路边放风筝",
         ["待在家里", "带雨伞", "穿外套"], "Don't fly a kite near the road。"),
        ("standard", "读一读：Hot day! Drink water. Wear a hat. 哪一句和提醒一致？", "要喝水、戴帽子。",
         ["要放风筝。", "要关窗睡觉。", "不要喝水。"], "Drink water. Wear a hat。"),
        ("standard", "读一读：Snowy! Put on a coat. 下雪天要穿什么？", "外套",
         ["短裤", "凉鞋", "雨伞"], "coat 是外套。"),
    ])
    deps += [dep("cne_p219", "cne_p218", "hard", "读懂提醒前先会说不同天气做什么。")]

    # U6 Part B/C + Revision
    topics.append(topic(
        "cne_p220", "季节里的活动", "词汇", 4, "上", CH4[6], "conceptual",
        "认读 swim、fly a kite、make a snowman、pick apples 等季节活动（Part B）。",
        ["能选出季节活动词的意思", "能把活动和季节粗略对应"],
        ("「堆雪人」用哪一组词？", "make a snowman"),
        "ces-2022:1.VO.01", NOTE4S,
    ))
    questions += four_qs("cne_p220", [
        ("basic", "「堆雪人」用哪一组词？", "make a snowman",
         ["fly a kite", "go swimming", "pick apples"], "make a snowman 是堆雪人。"),
        ("basic", "fly a kite 的意思是？", "放风筝", ["游泳", "堆雪人", "摘苹果"], "fly a kite 是放风筝。"),
        ("standard", "夏天常做的活动是？", "go swimming",
         ["make a snowman", "wear a thick coat", "skate on ice"], "夏天常游泳。"),
        ("standard", "pick apples 多在哪个季节？", "秋天",
         ["冬天", "春天只放风筝", "夏天只游泳"], "摘苹果多在秋天。"),
    ])
    deps += [dep("cne_p220", "cne_p100", "soft", "先认衣服，再学季节活动。")]

    topics.append(topic(
        "cne_p221", "读懂旅行卡片", "读写", 4, "上", CH4[6], "application",
        "读季节旅行卡片，找出季节、穿着和活动（Part C Project）。",
        ["能根据卡片选出季节和活动", "能选出和卡片一致的句子"],
        ("读一读：Season: summer. Wear: T-shirt. Do: swim. 卡片里的季节是？", "夏天"),
        "ces-2022:1.RW.02", NOTE4S,
    ))
    questions += four_qs("cne_p221", [
        ("basic", "读一读：Season: summer. Wear: T-shirt. Do: swim. 卡片里的季节是？", "夏天",
         ["冬天", "秋天", "春天"], "summer 是夏天。"),
        ("basic", "读一读：Season: winter. Wear: coat. Do: make a snowman. 冬天做什么？", "堆雪人",
         ["游泳", "放风筝", "摘苹果"], "make a snowman。"),
        ("standard", "读一读：Spring trip. Wear a sweater. Fly a kite. 哪一句和卡片一致？", "春天可以放风筝。",
         ["春天要穿大衣堆雪人。", "春天去游泳。", "春天摘苹果。"], "Fly a kite。"),
        ("standard", "读一读：Autumn. Wear a jacket. Pick apples. 穿着是什么？", "夹克",
         ["T 恤", "大衣", "泳装"], "jacket 是夹克。"),
    ])
    deps += [
        dep("cne_p221", "cne_p220", "hard", "读懂旅行卡片前先会季节活动词。"),
        dep("cne_p221", "cne_p102", "soft", "先会谈论穿着。"),
    ]

    topics.append(topic(
        "cne_p222", "复习：一起帮忙", "读写", 4, "上", CH4["rev"], "application",
        "综合复习帮忙家人、朋友和社区的短文，找出谁在帮忙、帮什么（Revision Let's help!）。",
        ["能综合读懂帮忙主题短文", "能选出和短文一致的信息"],
        ("读一读：I help at home. I clean. I help in the park too. 我在哪里帮忙？", "家里和公园"),
        "ces-2022:1.RW.02", NOTE4S,
    ))
    questions += four_qs("cne_p222", [
        ("basic", "读一读：I help at home. I clean. I help in the park too. 我在哪里帮忙？", "家里和公园",
         ["只在家里", "只在公园", "在医院"], "at home … in the park too。"),
        ("basic", "读一读：Let's help! We can help our family and community. 短文号召做什么？", "一起帮忙",
         ["一起购物", "一起睡觉", "一起吵架"], "Let's help。"),
        ("standard", "读一读：Amy is kind. She helps her mum cook. She helps at school too. 哪一句一致？", "艾米在家和学校都帮忙。",
         ["艾米不帮忙。", "艾米只在商店帮忙。", "艾米不会做饭。"], "helps mum … helps at school too。"),
        ("standard", "读一读：We help old people in our community. 我们帮助谁？", "社区里的老人",
         ["只有老师", "只有同学", "动物"], "old people in our community。"),
    ])
    deps += [
        dep("cne_p222", "cne_p211", "soft", "先读懂家庭帮忙。"),
        dep("cne_p222", "cne_p217", "soft", "先读懂社区/学校帮手。"),
    ]

    # ---------- 四下 densify (+6) + rename U6 ----------
    topics.append(topic(
        "cne_p229", "家规用词", "词汇", 4, "下", CH4X[2], "conceptual",
        "认读 make the bed、do housework、keep quiet、go to bed early 等家规相关表达。",
        ["能选出家规相关词的意思", "能根据中文选出英文表达"],
        ("「整理床铺」用哪一组词？", "make the bed"),
        "ces-2022:1.VO.01", NOTE4X,
    ))
    questions += four_qs("cne_p229", [
        ("basic", "「整理床铺」用哪一组词？", "make the bed",
         ["do homework", "go to bed", "keep quiet"], "make the bed 是整理床铺。"),
        ("basic", "keep quiet 的意思是？", "保持安静", ["早睡", "做家务", "起床"], "keep quiet 是保持安静。"),
        ("standard", "「早睡」用哪一组？", "go to bed early",
         ["get up late", "make the bed", "watch TV late"], "go to bed early。"),
        ("standard", "do housework 是在说什么？", "做家务", ["做作业", "做游戏", "做运动"], "housework 是家务。"),
    ])
    deps += [dep("cne_p229", "cne_p199", "soft", "与 have to / can't 家规同单元，先接触规则词。")]

    topics.append(topic(
        "cne_p230", "用 have to 说家规", "日常表达", 4, "下", CH4X[2], "application",
        "用 have to / don't have to / can't 说出家里的规则。",
        ["能选出正确的家规句子", "能区分必须做和不能做"],
        ("想说「我必须早睡」，应选哪一句？", "I have to go to bed early."),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p230", [
        ("basic", "想说「我必须早睡」，应选哪一句？", "I have to go to bed early.",
         ["I have go to bed early.", "I has to go to bed early.", "I have to going to bed early."],
         "have to + 动词原形。"),
        ("basic", "I can't watch TV late. 这句家规是？", "不能很晚看电视",
         ["必须很晚看电视", "可以不整理床铺", "必须大声说话"], "can't 表示不能。"),
        ("standard", "哪一句表示「不必」？", "I don't have to cook today.",
         ["I have to cook today.", "I can't cook today.", "I must cook today."], "don't have to 是不必。"),
        ("standard", "At home I ____ make the bed.", "have to",
         ["have", "has to", "having to"], "I 后用 have to。"),
    ])
    deps += [
        dep("cne_p230", "cne_p199", "hard", "先懂 have to 与 can't，再练说家规。"),
        dep("cne_p230", "cne_p229", "hard", "先认家规用词。"),
    ]

    topics.append(topic(
        "cne_p231", "读懂家规短文", "读写", 4, "下", CH4X[2], "application",
        "读家规列表或短文，找出必须做和不能做的事。",
        ["能根据短文选出家规", "能选出和短文一致的句子"],
        ("读一读：I have to make the bed. I can't play football inside. 我必须做什么？", "整理床铺"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p231", [
        ("basic", "读一读：I have to make the bed. I can't play football inside. 我必须做什么？", "整理床铺",
         ["在屋里踢球", "晚睡", "大声说话"], "have to make the bed。"),
        ("basic", "读一读：We have to keep quiet at night. 晚上要怎样？", "保持安静",
         ["大声唱歌", "踢足球", "开派对"], "keep quiet。"),
        ("standard", "读一读：Tom has to do housework. He can't watch TV before homework. 哪一句一致？", "做完作业前不能看电视。",
         ["他不必做家务。", "他可以先看电视。", "他没有家规。"], "can't watch TV before homework。"),
        ("standard", "读一读：I don't have to cook, but I have to wash the dishes. 我必须做什么？", "洗碗",
         ["做饭", "不必洗碗", "看电视"], "have to wash the dishes。"),
    ])
    deps += [dep("cne_p231", "cne_p230", "hard", "读懂家规前先会说 have to。")]

    topics.append(topic(
        "cne_p232", "农场活动", "词汇", 4, "下", CH4X[6], "conceptual",
        "认读 milk cows、pick vegetables、feed chickens、plant seeds 等农场活动（On the farm）。",
        ["能选出农场活动的意思", "能根据中文选出英文表达"],
        ("「挤牛奶」用哪一组词？", "milk cows"),
        "ces-2022:1.VO.01", NOTE4X,
    ))
    questions += four_qs("cne_p232", [
        ("basic", "「挤牛奶」用哪一组词？", "milk cows",
         ["feed chickens", "pick vegetables", "plant seeds"], "milk cows 是挤牛奶。"),
        ("basic", "feed chickens 的意思是？", "喂鸡", ["挤牛奶", "摘菜", "播种"], "feed chickens 是喂鸡。"),
        ("standard", "「摘蔬菜」用哪一组？", "pick vegetables",
         ["plant seeds", "milk cows", "ride a horse"], "pick vegetables。"),
        ("standard", "plant seeds 是在做什么？", "播种", ["喂鸡", "挤奶", "买菜"], "plant seeds 是播种。"),
    ])
    deps += [dep("cne_p232", "cne_p096", "soft", "先认农场词，再学农场活动。")]

    topics.append(topic(
        "cne_p233", "在农场做什么", "日常表达", 4, "下", CH4X[6], "application",
        "用 I can … / We … on the farm 说在农场做的事。",
        ["能选出农场活动句子", "能读懂农场对话"],
        ("想说「我可以在农场喂鸡」，应选哪一句？", "I can feed chickens on the farm."),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p233", [
        ("basic", "想说「我可以在农场喂鸡」，应选哪一句？", "I can feed chickens on the farm.",
         ["I can feed chickens on the shop.", "I can feeding chickens.", "I can feeds chickens."],
         "can + 动词原形；地点 on the farm。"),
        ("basic", "We pick vegetables on the farm. 我们在农场做什么？", "摘蔬菜",
         ["挤牛奶", "看书", "看电影"], "pick vegetables。"),
        ("standard", "哪一句是在农场做的事？", "They milk cows every morning.",
         ["They buy milk in a cinema.", "They milk cows in the library.", "They watch TV on the farm only."],
         "milk cows 是农场活动。"),
        ("standard", "On the farm I ____ plant seeds.", "can",
         ["cans", "am", "is"], "情态 can 后接原形。"),
    ])
    deps += [dep("cne_p233", "cne_p232", "hard", "先认农场活动词，再说句子。")]

    topics.append(topic(
        "cne_p234", "读懂农场劳动短文", "读写", 4, "下", CH4X[6], "application",
        "读农场短文，找出人们在农场做的劳动。",
        ["能根据短文选出农场活动", "能选出和短文一致的句子"],
        ("读一读：On the farm we milk cows and feed chickens. 我们做什么？", "挤牛奶和喂鸡"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p234", [
        ("basic", "读一读：On the farm we milk cows and feed chickens. 我们做什么？", "挤牛奶和喂鸡",
         ["只摘菜", "只播种", "去商店"], "milk cows and feed chickens。"),
        ("basic", "读一读：Farmers plant seeds in spring. 农民春天做什么？", "播种",
         ["堆雪人", "放风筝", "游泳"], "plant seeds。"),
        ("standard", "读一读：Amy picks vegetables. Tom milks cows. 哪一句一致？", "汤姆挤牛奶。",
         ["艾米挤牛奶。", "汤姆摘菜。", "他们在图书馆。"], "Tom milks cows。"),
        ("standard", "读一读：From the farm we get milk and eggs. 我们从农场得到什么？", "牛奶和鸡蛋",
         ["书和笔", "衣服", "汽车"], "milk and eggs。"),
    ])
    deps += [
        dep("cne_p234", "cne_p233", "hard", "读懂农场短文前先会说活动。"),
        dep("cne_p234", "cne_p200", "soft", "与从农场到餐桌内容衔接。"),
    ]

    # ---------- 六上 densify thin (+6) ----------
    topics.append(topic(
        "cne_p238", "聚会与邀请词汇", "词汇", 6, "上", CH6S[2], "conceptual",
        "认读 party、invite、together、join、celebrate 等聚会相关词（Getting together）。",
        ["能选出聚会词的意思", "能根据中文选出英文单词"],
        ("invite 的意思是？", "邀请"),
        "ces-2022:2.VO.01", NOTE6S,
    ))
    questions += four_qs("cne_p238", [
        ("basic", "invite 的意思是？", "邀请", ["参加", "庆祝", "聚会"], "invite 是邀请。"),
        ("basic", "哪个单词的意思是「聚会」？", "party", ["invite", "join", "plan"], "party 是聚会。"),
        ("standard", "「一起」用哪个词？", "together", ["invite", "alone", "never"], "together 是一起。"),
        ("standard", "celebrate 的意思是？", "庆祝", ["取消", "邀请", "拒绝"], "celebrate 是庆祝。"),
    ])
    deps += [dep("cne_p238", "cne_p163", "soft", "先接触周末计划，再学聚会词。")]

    topics.append(topic(
        "cne_p235", "健康生活词汇", "词汇", 6, "上", CH6S[3], "conceptual",
        "认读 healthy、exercise、sleep、diet、habit 等健康生活词（Healthy life）。",
        ["能选出健康生活词的意思", "能根据中文选出英文单词"],
        ("healthy 的意思是？", "健康的"),
        "ces-2022:2.VO.01", NOTE6S,
    ))
    questions += four_qs("cne_p235", [
        ("basic", "healthy 的意思是？", "健康的", ["生病的", "忙碌的", "懒惰的"], "healthy 是健康的。"),
        ("basic", "exercise 的意思是？", "锻炼", ["睡觉", "饮食", "习惯"], "exercise 是锻炼。"),
        ("standard", "「习惯」用哪个词？", "habit", ["diet", "sleep", "party"], "habit 是习惯。"),
        ("standard", "A good ____ helps you grow.", "diet",
         ["noise", "mess", "fight"], "diet 可指饮食。"),
    ])
    deps += [dep("cne_p235", "cne_p176", "soft", "与 should 提建议同单元。")]

    topics.append(topic(
        "cne_p236", "健康习惯建议", "日常表达", 6, "上", CH6S[3], "application",
        "用 You should … / You shouldn't … 给出健康生活建议。",
        ["能选出正确的健康建议句", "能区分应该和不应该"],
        ("想建议多锻炼，应选哪一句？", "You should exercise more."),
        "ces-2022:2.FU.02", NOTE6S,
    ))
    questions += four_qs("cne_p236", [
        ("basic", "想建议多锻炼，应选哪一句？", "You should exercise more.",
         ["You should exercising more.", "You shouldn't exercise more.", "You should exercises more."],
         "should + 动词原形。"),
        ("basic", "You shouldn't stay up late. 这句建议是？", "不该熬夜",
         ["应该熬夜", "必须熬夜", "可以不睡觉"], "shouldn't 表示不该。"),
        ("standard", "哪一句是健康建议？", "You should sleep early.",
         ["You should eat junk food every day.", "You shouldn't drink water.", "You should never exercise."],
         "早睡是健康建议。"),
        ("standard", "To keep healthy, you ____ eat fruit.", "should",
         ["shouldn't", "aren't", "don't can"], "should 表示建议。"),
    ])
    deps += [
        dep("cne_p236", "cne_p176", "hard", "先会 should，再练健康建议。"),
        dep("cne_p236", "cne_p235", "hard", "先认健康词汇。"),
    ]

    topics.append(topic(
        "cne_p237", "读懂健康生活短文", "读写", 6, "上", CH6S[3], "application",
        "读健康生活短文，找出好习惯和建议。",
        ["能根据短文选出健康习惯", "能选出和短文一致的句子"],
        ("读一读：Tom exercises every day. He sleeps early. 汤姆有什么好习惯？", "天天锻炼、早睡"),
        "ces-2022:2.RW.01", NOTE6S,
    ))
    questions += four_qs("cne_p237", [
        ("basic", "读一读：Tom exercises every day. He sleeps early. 汤姆有什么好习惯？", "天天锻炼、早睡",
         ["从不锻炼", "天天熬夜", "只吃零食"], "exercises every day … sleeps early。"),
        ("basic", "读一读：You should eat more vegetables. 短文建议吃什么？", "更多蔬菜",
         ["更多糖果", "更少水", "不吃饭"], "more vegetables。"),
        ("standard", "读一读：A healthy life needs good habits. Amy has a good diet. 哪一句一致？", "艾米饮食较好。",
         ["艾米没有好习惯。", "健康生活不需要习惯。", "艾米从不吃饭。"], "good diet。"),
        ("standard", "读一读：Don't sit too long. Go out and exercise. 短文建议？", "别久坐，出去锻炼",
         ["一直坐着", "不要锻炼", "只在室内睡觉"], "Don't sit too long. Go out and exercise。"),
    ])
    deps += [
        dep("cne_p237", "cne_p236", "hard", "读懂短文前先会健康建议。"),
        dep("cne_p237", "cne_p178", "soft", "先会读感受和建议。"),
    ]

    topics.append(topic(
        "cne_p239", "谈论存钱计划", "日常表达", 6, "上", CH6S[4], "application",
        "用 I want to save … / I will spend … on … 谈论零花钱计划。",
        ["能选出正确的存钱/花钱句子", "能读懂简单计划句"],
        ("想说「我想存钱买书」，应选哪一句？", "I want to save money for books."),
        "ces-2022:2.FU.02", NOTE6S,
    ))
    questions += four_qs("cne_p239", [
        ("basic", "想说「我想存钱买书」，应选哪一句？", "I want to save money for books.",
         ["I want to spend money for save.", "I want save money books.", "I wants to save money."],
         "want to save money for …"),
        ("basic", "I will spend 10 yuan on fruit. 我打算？", "花 10 元买水果",
         ["存 10 元", "卖水果", "借 10 元"], "spend … on … 是花钱买。"),
        ("standard", "哪一句是存钱计划？", "I will save my pocket money.",
         ["I will spend all money today.", "I never save.", "I lose money on purpose."],
         "save pocket money。"),
        ("standard", "She wants to ____ money for a gift.", "save",
         ["cost", "cheap", "price"], "攒钱用 save。"),
    ])
    deps += [
        dep("cne_p239", "cne_p201", "hard", "先认金钱词汇。"),
        dep("cne_p239", "cne_p202", "soft", "先会说价格数量。"),
    ]

    topics.append(topic(
        "cne_p240", "谈论太空探索", "日常表达", 6, "上", CH6S[5], "application",
        "用 will / be going to 谈论未来的太空旅行或探索。",
        ["能选出谈论未来太空的句子", "能读懂简单太空计划句"],
        ("想说「将来人们会去火星」，应选哪一句？", "People will go to Mars."),
        "ces-2022:2.FU.02", NOTE6S,
    ))
    questions += four_qs("cne_p240", [
        ("basic", "想说「将来人们会去火星」，应选哪一句？", "People will go to Mars.",
         ["People will goes to Mars.", "People going to Mars yesterday.", "People go to Mars yesterday."],
         "will + 动词原形表将来。"),
        ("basic", "I am going to be an astronaut. 这句是在说？", "我打算当宇航员",
         ["我昨天是宇航员", "我不是宇航员", "我害怕太空"], "be going to 表打算。"),
        ("standard", "哪一句谈未来太空生活？", "We will live on a space station.",
         ["We lived on a space station yesterday only.", "We never will.", "Space is a book."],
         "will live 表将来。"),
        ("standard", "They ____ explore the moon next year.", "will",
         ["did", "are", "was"], "next year 用 will。"),
    ])
    deps += [
        dep("cne_p240", "cne_p205", "hard", "先会 will 说未来太空生活。"),
        dep("cne_p240", "cne_p204", "soft", "先认太空词汇。"),
    ]

    # ---------- 六下 Unit3 Where did you go (+6) ----------
    topics.append(topic(
        "cne_p223", "假期活动词汇", "词汇", 6, "下", CH6X3, "conceptual",
        "认读 rode a horse、went camping、went fishing、hurt my foot、took pictures、bought gifts 等假期活动（Unit3 Part A/B）。",
        ["能选出假期活动短语的意思", "能根据中文选出英文短语"],
        ("「骑马」的过去式短语是？", "rode a horse"),
        "ces-2022:2.VO.01", NOTE6X,
    ))
    questions += four_qs("cne_p223", [
        ("basic", "「骑马」的过去式短语是？", "rode a horse",
         ["ride a horse", "rided a horse", "went a horse"], "ride 的过去式是 rode。"),
        ("basic", "went camping 的意思是？", "去野营了", ["去钓鱼了", "受伤了", "买礼物了"], "went camping 是去野营。"),
        ("standard", "「拍了很多照片」用哪一组？", "took pictures",
         ["take pictures", "taked pictures", "bought pictures"], "take 的过去式是 took。"),
        ("standard", "hurt my foot 是在说什么？", "伤了脚", ["洗了脚", "看了脚", "买了鞋"], "hurt 可作过去式「伤了」。"),
    ])
    deps += [
        dep("cne_p223", "cne_p189", "soft", "先接触不规则过去式，再记假期短语。"),
        dep("cne_p223", "cne_p187", "soft", "先会谈上周末。"),
    ]

    topics.append(topic(
        "cne_p224", "Where did you go 问去向", "语法", 6, "下", CH6X3, "procedural",
        "用 Where did you go …? / I went to … 询问和回答过去去过的地方。",
        ["能选出正确的过去去向问句", "能用 went to 回答"],
        ("想问「你去了哪里？」，应选哪一句？", "Where did you go?"),
        "ces-2022:2.GR.07", NOTE6X,
    ))
    questions += four_qs("cne_p224", [
        ("basic", "想问「你去了哪里？」，应选哪一句？", "Where did you go?",
         ["Where do you go?", "Where did you went?", "Where are you go?"], "Did 后用动词原形 go。"),
        ("basic", "I ____ to the park last Sunday.", "went",
         ["go", "goes", "going"], "过去式用 went。"),
        ("standard", "哪一句正确？", "Where did they go over the holiday?",
         ["Where did they went over the holiday?", "Where do they went?", "Where they did go?"],
         "did + 主语 + 动词原形。"),
        ("standard", "—Where did you go? —I went to Sanya. 答句去了哪里？", "三亚",
         ["公园", "学校", "医院"], "Sanya 是三亚。"),
    ])
    deps += [
        dep("cne_p224", "cne_p186", "hard", "先会 Did 提问。"),
        dep("cne_p224", "cne_p223", "soft", "先接触假期活动词。"),
    ]

    topics.append(topic(
        "cne_p225", "What did you do 问活动", "日常表达", 6, "下", CH6X3, "application",
        "用 What did you do …? / I rode … / I went … 询问和回答过去做的事。",
        ["能选出正确的过去活动问句", "能用过去式短语回答"],
        ("想问「你在那里做了什么？」，应选哪一句？", "What did you do there?"),
        "ces-2022:2.FU.02", NOTE6X,
    ))
    questions += four_qs("cne_p225", [
        ("basic", "想问「你在那里做了什么？」，应选哪一句？", "What did you do there?",
         ["What did you did there?", "What do you did there?", "What you did there?"],
         "What did you do …"),
        ("basic", "I rode a bike in the forest park. 我做了什么？", "骑自行车",
         ["骑马", "钓鱼", "野营"], "rode a bike。"),
        ("standard", "哪一句回答「做了什么」？", "I went fishing.",
         ["I go fishing yesterday.", "I going fishing.", "I goed fishing."], "went fishing。"),
        ("standard", "—What did you do? —I ____ gifts.", "bought",
         ["buy", "buys", "buying"], "过去式 bought。"),
    ])
    deps += [
        dep("cne_p225", "cne_p224", "hard", "先会问去向，再问活动。"),
        dep("cne_p225", "cne_p223", "hard", "回答要用假期活动词。"),
    ]

    topics.append(topic(
        "cne_p226", "怎么去的与和谁去的", "日常表达", 6, "下", CH6X3, "application",
        "用 How did you go …? / Who did you go with? 询问出行方式和同伴。",
        ["能选出正确的问句", "能用 by plane / with my parents 等回答"],
        ("想问「你怎么去的？」，应选哪一句？", "How did you go there?"),
        "ces-2022:2.FU.02", NOTE6X,
    ))
    questions += four_qs("cne_p226", [
        ("basic", "想问「你怎么去的？」，应选哪一句？", "How did you go there?",
         ["How did you went there?", "How do you went there?", "How you go there yesterday?"],
         "How did you go …"),
        ("basic", "We went there by plane. 我们怎么去的？", "坐飞机",
         ["坐火车步行", "骑自行车", "没写方式"], "by plane。"),
        ("standard", "想问「你和谁一起去的？」应选？", "Who did you go with?",
         ["Who did you went with?", "Who do you go with yesterday?", "With who you go?"],
         "Who did you go with?"),
        ("standard", "—Who did you go with? —____.", "My parents",
         ["By plane", "It was warm", "I took pictures"], "问同伴用人物回答。"),
    ])
    deps += [
        dep("cne_p226", "cne_p224", "hard", "先会问去向。"),
        dep("cne_p226", "cne_p159", "soft", "先认识交通工具。"),
    ]

    topics.append(topic(
        "cne_p227", "谈论假期旅行", "日常表达", 6, "下", CH6X3, "application",
        "综合用 Where / What / How / Who 谈论一次假期旅行经历。",
        ["能选出完整的旅行对话答句", "能读懂简短旅行对话"],
        ("对话：—Where did you go over the holiday? —____.", "I went to Hangzhou."),
        "ces-2022:2.FU.02", NOTE6X,
    ))
    questions += four_qs("cne_p227", [
        ("basic", "对话：—Where did you go over the holiday? —____.", "I went to Hangzhou.",
         ["I go to Hangzhou.", "I goes to Hangzhou.", "I going to Hangzhou."], "用 went to 回答。"),
        ("basic", "It was so warm in Sanya. 三亚怎么样？", "很暖和",
         ["很冷", "在下雪", "没有天气信息"], "so warm。"),
        ("standard", "哪一组句子能完整谈一次旅行？", "I went to Xinjiang. I rode a horse.",
         ["I go to Xinjiang. I ride a horse yesterday.", "I going Xinjiang.", "Xinjiang go I."],
         "过去式 went / rode。"),
        ("standard", "—How was your holiday? —____.", "It was good.",
         ["It is tomorrow.", "I am a holiday.", "Yes, I do every day."], "用 It was … 评价过去假期。"),
    ])
    deps += [
        dep("cne_p227", "cne_p225", "hard", "先会问做什么。"),
        dep("cne_p227", "cne_p226", "hard", "先会问怎么去、和谁去。"),
    ]

    topics.append(topic(
        "cne_p228", "读懂假期旅行短文", "读写", 6, "下", CH6X3, "application",
        "读假期旅行短文或日记，找出地点、同伴、交通方式和活动。",
        ["能根据短文选出旅行信息", "能选出和短文一致的句子"],
        ("读一读：Last holiday I went to Sanya with my parents by plane. I went swimming. 我去了哪里？", "三亚"),
        "ces-2022:2.RW.01", NOTE6X,
    ))
    questions += four_qs("cne_p228", [
        ("basic", "读一读：Last holiday I went to Sanya with my parents by plane. I went swimming. 我去了哪里？", "三亚",
         ["杭州", "新疆", "公园"], "went to Sanya。"),
        ("basic", "读一读：We saw lots of grapes in Turpan, but we couldn't eat them. 在吐鲁番看到了什么？", "很多葡萄",
         ["很多马", "很多礼物", "很多雪"], "lots of grapes。"),
        ("standard", "读一读：John hurt his foot and couldn't come to school. 约翰怎么了？", "脚受伤了",
         ["他去游泳了", "他买了礼物", "他骑马了"], "hurt his foot。"),
        ("standard", "读一读：I took lots of pictures and bought gifts for my friends. 哪一句一致？", "我拍了很多照片，还买了礼物。",
         ["我什么都没买。", "我没有拍照。", "我只待在家里。"], "took pictures … bought gifts。"),
    ])
    deps += [
        dep("cne_p228", "cne_p227", "hard", "读懂旅行短文前先会谈论旅行。"),
        dep("cne_p228", "cne_p188", "soft", "先会读上周末日记。"),
    ]

    return topics, questions, deps


def insert_topics(topics, new_topics):
    """Insert each new topic after the last existing topic of the same chapter when possible."""
    by_id = {t["id"]: i for i, t in enumerate(topics)}
    # group new by chapter
    from collections import defaultdict
    chapter_news = defaultdict(list)
    for nt in new_topics:
        chapter_news[nt["chapter"]].append(nt)

    # process in reverse index order so insertions don't shift earlier targets wrongly
    inserts = []  # (index_after, topic)
    for ch, nlist in chapter_news.items():
        # find last index with this chapter
        last = -1
        for i, t in enumerate(topics):
            if t.get("chapter") == ch:
                last = i
        if last < 0:
            # fallback: for revision / new chapter, place after last 四上 / 六下 sibling
            grade = nlist[0]["grade"]
            sem = nlist[0]["semester"]
            last = -1
            for i, t in enumerate(topics):
                if t.get("subject") == "english" and t.get("grade") == grade and t.get("semester") == sem:
                    last = i
        if last < 0:
            last = len(topics) - 1
        inserts.append((last, nlist))

    inserts.sort(key=lambda x: x[0], reverse=True)
    for last, nlist in inserts:
        for j, nt in enumerate(nlist):
            topics.insert(last + 1 + j, nt)
    return topics


def main():
    topics = load("topics.json")
    questions = load("questions.json")
    deps = load("dependencies.json")

    existing = {t["id"] for t in topics}
    new_topics, new_qs, new_deps = build_new()
    new_topics = [t for t in new_topics if t["id"] not in existing]
    if not new_topics:
        print("已存在新点，跳过写入。")
        return

    # rename 四下 U6 chapter
    for t in topics:
        if t.get("chapter") == "四年级下册 第6单元 From farm to table":
            t["chapter"] = CH4X[6]
            if t["id"] == "cne_p200":
                # keep name; note in description
                if "On the farm" not in t.get("description", ""):
                    t["description"] = t["description"].rstrip("。") + "（挂新版第6单元 On the farm）。"

    # also fix soft chapter string in deps reasons? skip

    topics = insert_topics(topics, new_topics)
    questions.extend(new_qs)
    # avoid dup deps
    dep_keys = {(d["topicId"], d["prerequisiteId"], d["strength"]) for d in deps}
    for d in new_deps:
        k = (d["topicId"], d["prerequisiteId"], d["strength"])
        if k not in dep_keys:
            deps.append(d)
            dep_keys.add(k)

    dump("topics.json", topics)
    dump("questions.json", questions)
    dump("dependencies.json", deps)

    # counts
    eng_p = [t for t in topics if str(t["id"]).startswith("cne_p")]
    g4s = [t for t in eng_p if t["grade"] == 4 and t["semester"] == "上"]
    g4x = [t for t in eng_p if t["grade"] == 4 and t["semester"] == "下"]
    g6s = [t for t in eng_p if t["grade"] == 6 and t["semester"] == "上"]
    g6x = [t for t in eng_p if t["grade"] == 6 and t["semester"] == "下"]
    print("新增知识点", len(new_topics), "题", len(new_qs), "边", len(new_deps))
    print("小学英语总点数", len(eng_p))
    print("四上", len(g4s), "四下", len(g4x), "六上", len(g6s), "六下", len(g6x))
    # unit3 check
    u3 = [t for t in g6x if "Where did you go" in t.get("chapter", "")]
    print("六下 Unit3", len(u3), [t["name"] for t in u3])


if __name__ == "__main__":
    main()
