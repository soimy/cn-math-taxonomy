#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小学英语四下/五下 densify（本地，不上线）。

- 四下 2026春 pep4x_2026：薄单元 Part B/C + Revision A great weekend plan，24→约 36
- 五下现行 peps5x（新版未上线）：补薄单元，并补回 Unit6 Work quietly，18→约 36
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

NOTE4X = "依据 dzkbw pep4x_2026（2026 春）单元目录补点，待核。"
NOTE5X = "依据 dzkbw peps5x（现行五下，新版未上线）单元目录补点，待核。"


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
    """items: 4 × (diff, prompt, answer, wrongs, expl); expect 2 basic + 1 standard + 1 challenge."""
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


CH4X = {
    1: "四年级下册 第1单元 Class rules",
    3: "四年级下册 第3单元 Time for school",
    4: "四年级下册 第4单元 Going shopping",
    5: "四年级下册 第5单元 Farms and us",
    "rev": "四年级下册 复习 A great weekend plan",
}
CH5X = {
    1: "五年级下册 第1单元 My day",
    2: "五年级下册 第2单元 My favourite season",
    3: "五年级下册 第3单元 My school calendar",
    4: "五年级下册 第4单元 When is the art show",
    5: "五年级下册 第5单元 Whose dog is it",
    6: "五年级下册 第6单元 Work quietly",
}


def build_new():
    topics = []
    questions = []
    deps = []

    # ========== 四下 densify (+12) ==========
    # U1 Class rules
    topics.append(topic(
        "cne_p246", "must 与 mustn't 说班规", "语法", 4, "下", CH4X[1], "procedural",
        "用 must / mustn't 说明教室里必须做和不能做的事（Part B）。",
        ["能选出正确的 must / mustn't 句子", "能区分必须与禁止"],
        ("想说「我们必须听老师讲」，应选哪一句？", "We must listen to the teacher."),
        "ces-2022:1.GR.06", NOTE4X,
    ))
    questions += four_qs("cne_p246", [
        ("basic", "想说「我们必须听老师讲」，应选哪一句？", "We must listen to the teacher.",
         ["We must listening to the teacher.", "We mustn't listen to the teacher.", "We must listens to the teacher."],
         "must + 动词原形。"),
        ("basic", "We mustn't run in the hall. 这句班规是？", "走廊里不能跑",
         ["走廊里必须跑", "教室里必须跑", "可以在走廊大喊"], "mustn't 表示禁止。"),
        ("standard", "哪一句表示「必须」？", "You must keep quiet in class.",
         ["You mustn't keep quiet in class.", "You can never listen.", "You don't must talk."],
         "must 表示必须。"),
        ("challenge", "读一读：We must raise our hands. We mustn't shout. 哪一句和班规一致？", "要举手，不能大喊。",
         ["要大喊，不能举手。", "不必举手。", "可以在走廊跑。"], "must raise … mustn't shout。"),
    ])
    deps += [
        dep("cne_p246", "cne_p152", "hard", "先会祈使句，再学 must / mustn't。"),
        dep("cne_p246", "cne_p151", "soft", "先认规则用词。"),
    ]

    topics.append(topic(
        "cne_p247", "制作班级规则海报", "读写", 4, "下", CH4X[1], "application",
        "读懂班级规则海报，并能选出适合写进海报的句子（Project）。",
        ["能根据海报表述选出规则", "能判断哪句适合写进班规海报"],
        ("海报上写 Keep the classroom clean. 这是在要求？", "保持教室干净"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p247", [
        ("basic", "海报上写 Keep the classroom clean. 这是在要求？", "保持教室干净",
         ["在走廊跑", "大声说话", "乱扔垃圾"], "keep … clean。"),
        ("basic", "哪一句适合写进班规海报？", "Listen to the teacher.",
         ["I like apples.", "It is sunny today.", "My name is Tom."], "班规用祈使句。"),
        ("standard", "读一读海报：1. Listen carefully. 2. Don't push. 不可以做什么？", "推搡",
         ["认真听", "举手", "保持安静"], "Don't push。"),
        ("challenge", "读一读：Our class rules: We must help each other. We mustn't litter. 哪一句可加进海报？", "Keep the floor clean.",
         ["Run in the hall every day.", "Shout in class.", "Never listen."], "保持干净与不乱扔一致。"),
    ])
    deps += [
        dep("cne_p247", "cne_p246", "hard", "先会 must 班规，再做海报读写。"),
        dep("cne_p247", "cne_p154", "soft", "先会读规则。"),
    ]

    # U3 Time for school
    topics.append(topic(
        "cne_p248", "It's time to 该做什么", "日常表达", 4, "下", CH4X[3], "application",
        "用 It's time to … / It's time for … 说出该做的事。",
        ["能选出正确的 It's time 句子", "能区分 time to 与 time for"],
        ("想说「该起床了」，应选哪一句？", "It's time to get up."),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p248", [
        ("basic", "想说「该起床了」，应选哪一句？", "It's time to get up.",
         ["It's time to getting up.", "It's time for get up.", "It time to get up."],
         "It's time to + 动词原形。"),
        ("basic", "It's time for breakfast. 这句是在说？", "该吃早饭了",
         ["该睡觉了", "该上学了", "该放学了"], "time for breakfast。"),
        ("standard", "哪一句正确？", "It's time to go to school.",
         ["It's time to goes to school.", "It's time for go to school.", "It's time going to school."],
         "time to + 原形。"),
        ("challenge", "读一读：It's 7:00. It's time to ____. 早上七点最合适填？", "go to school",
         ["go to bed", "watch TV all night", "sleep in class"], "七点常是上学时间。"),
    ])
    deps += [
        dep("cne_p248", "cne_p089", "hard", "先会问几点，再说该做什么。"),
        dep("cne_p248", "cne_p090", "soft", "先会说时刻和该做的事。"),
    ]

    topics.append(topic(
        "cne_p249", "读懂作息时间表", "读写", 4, "下", CH4X[3], "application",
        "读简单作息表或短文，找出几点该做什么。",
        ["能根据时间表选出活动", "能选出和短文一致的句子"],
        ("读一读：7:00 get up. 7:30 breakfast. 七点半做什么？", "吃早饭"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p249", [
        ("basic", "读一读：7:00 get up. 7:30 breakfast. 七点半做什么？", "吃早饭",
         ["起床", "睡觉", "放学"], "7:30 breakfast。"),
        ("basic", "读一读：It's time to go to bed at 9:00. 九点该做什么？", "睡觉",
         ["起床", "吃早饭", "去上学"], "go to bed。"),
        ("standard", "读一读：Amy: 6:30 get up; 7:00 go to school. 艾米几点去上学？", "7 点",
         ["6:30", "8 点", "9 点"], "7:00 go to school。"),
        ("challenge", "读一读：Tom gets up at 6:30. He has breakfast at 7:00. It's time to go at 7:20. 他先做什么？", "起床",
         ["先出门", "先吃晚饭", "先睡觉"], "先 get up，再 breakfast，再 go。"),
    ])
    deps += [
        dep("cne_p249", "cne_p248", "hard", "先会 It's time，再读时间表。"),
        dep("cne_p249", "cne_p091", "soft", "先会读作息时刻。"),
    ]

    # U4 Going shopping
    topics.append(topic(
        "cne_p250", "购物用语 I'll take", "日常表达", 4, "下", CH4X[4], "application",
        "用 Can I help you? / How much …? / I'll take … 完成简单购物对话。",
        ["能选出正确的购物答句", "能读懂简短购物对话"],
        ("店员问 Can I help you? 想买钢笔，应选哪一句？", "I'd like a pen, please."),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p250", [
        ("basic", "店员问 Can I help you? 想买钢笔，应选哪一句？", "I'd like a pen, please.",
         ["I'd like a book, please.", "I don't like pens.", "How old are you?"],
         "想要用 I'd like …"),
        ("basic", "I'll take two. 这句购物时表示？", "我要买两个",
         ["我只要看", "太贵了", "不要了"], "I'll take 表示决定买。"),
        ("standard", "—How much is it? —____.", "It's ten yuan.",
         ["I'm ten.", "It's ten o'clock.", "I take ten."], "问价格用 It's … yuan。"),
        ("challenge", "读对话：—Can I help you? —Yes. How much are the apples? —Five yuan. —OK, I'll take them. 顾客最后决定？", "买下苹果",
         ["只问时间", "不买了", "只要一支笔"], "I'll take them。"),
    ])
    deps += [
        dep("cne_p250", "cne_p105", "hard", "先会 How much，再练完整购物句。"),
        dep("cne_p250", "cne_p106", "soft", "先会在商店购物。"),
    ]

    topics.append(topic(
        "cne_p251", "读懂购物小票与价签", "读写", 4, "下", CH4X[4], "application",
        "读价签或简短购物记录，找出物品和价格。",
        ["能根据价签选出价格", "能选出和记录一致的句子"],
        ("价签：ruler — 3 yuan. 尺子多少钱？", "3 元"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p251", [
        ("basic", "价签：ruler — 3 yuan. 尺子多少钱？", "3 元",
         ["4 元", "5 元", "10 元"], "3 yuan。"),
        ("basic", "读一读：I buy a notebook. It is 5 yuan. 本子多少钱？", "5 元",
         ["3 元", "笔记本免费", "10 元"], "5 yuan。"),
        ("standard", "读一读：pen 2 yuan; eraser 1 yuan. 买一支笔和一块橡皮一共？", "3 元",
         ["2 元", "1 元", "4 元"], "2+1=3。"),
        ("challenge", "读一读：Amy buys two pencils. Each is 2 yuan. She pays ____ yuan.", "4",
         ["2", "3", "6"], "两支各 2 元共 4 元。"),
    ])
    deps += [
        dep("cne_p251", "cne_p250", "hard", "先会购物对话，再读价签。"),
        dep("cne_p251", "cne_p107", "soft", "先会读价签。"),
    ]

    # U5 Farms and us
    topics.append(topic(
        "cne_p252", "农场动物与作物", "词汇", 4, "下", CH4X[5], "conceptual",
        "认读 hen、cow、horse、tomato、potato、carrot 等农场动物与作物词（Part B）。",
        ["能选出农场词的意思", "能根据中文选出英文单词"],
        ("哪个单词的意思是「奶牛」？", "cow"),
        "ces-2022:1.VO.01", NOTE4X,
    ))
    questions += four_qs("cne_p252", [
        ("basic", "哪个单词的意思是「奶牛」？", "cow",
         ["hen", "horse", "carrot"], "cow 是奶牛。"),
        ("basic", "tomato 的意思是？", "西红柿",
         ["土豆", "胡萝卜", "母鸡"], "tomato 是西红柿。"),
        ("standard", "「马」用哪个词？", "horse",
         ["cow", "hen", "potato"], "horse 是马。"),
        ("challenge", "读一读：We have hens and cows on the farm. We grow carrots. 农场没有提到哪种？", "马",
         ["母鸡", "奶牛", "胡萝卜"], "写了 hens、cows、carrots，没有 horse。"),
    ])
    deps += [dep("cne_p252", "cne_p096", "soft", "先认农场词，再扩动物与作物。")]

    topics.append(topic(
        "cne_p253", "There be 说农场有什么", "语法", 4, "下", CH4X[5], "procedural",
        "用 There is / There are 描述农场里有什么。",
        ["能选出正确的 There be 句子", "能区分 is 与 are"],
        ("想说「农场里有一匹马」，应选哪一句？", "There is a horse on the farm."),
        "ces-2022:1.GR.03", NOTE4X,
    ))
    questions += four_qs("cne_p253", [
        ("basic", "想说「农场里有一匹马」，应选哪一句？", "There is a horse on the farm.",
         ["There are a horse on the farm.", "There is horse on the farm.", "There be a horse on the farm."],
         "单数用 There is。"),
        ("basic", "There are many hens. 这句话里母鸡是？", "很多只",
         ["只有一只", "没有母鸡", "一只马"], "are + many 表复数。"),
        ("standard", "哪一句正确？", "There are some tomatoes.",
         ["There is some tomatoes.", "There are a tomato.", "There be tomatoes."],
         "复数 tomatoes 用 are。"),
        ("challenge", "读一读：There is a cow. There are three horses. 一共提到几只动物？", "4",
         ["1", "3", "5"], "1 头牛 + 3 匹马 = 4。"),
    ])
    deps += [
        dep("cne_p253", "cne_p097", "soft", "先接触 These/Those，再练 There be。"),
        dep("cne_p253", "cne_p252", "hard", "先认农场词，再说有什么。"),
    ]

    # Revision A great weekend plan
    topics.append(topic(
        "cne_p254", "周末计划词汇", "词汇", 4, "下", CH4X["rev"], "conceptual",
        "认读 picnic、cinema、museum、visit、plan 等周末计划相关词（Revision）。",
        ["能选出周末计划词的意思", "能根据中文选出英文单词"],
        ("picnic 的意思是？", "野餐"),
        "ces-2022:1.VO.01", NOTE4X,
    ))
    questions += four_qs("cne_p254", [
        ("basic", "picnic 的意思是？", "野餐",
         ["电影院", "博物馆", "计划"], "picnic 是野餐。"),
        ("basic", "哪个单词的意思是「博物馆」？", "museum",
         ["cinema", "picnic", "park"], "museum 是博物馆。"),
        ("standard", "「计划」用哪个词？", "plan",
         ["play", "plant", "plate"], "plan 是计划。"),
        ("challenge", "读一读：Our weekend plan: visit a museum and see a film. 计划里没有？", "去野餐",
         ["参观博物馆", "看电影", "周末安排"], "写了 museum 和 film，没有 picnic。"),
    ])
    deps += [dep("cne_p254", "cne_p088", "soft", "先认一天活动，再学周末计划词。")]

    topics.append(topic(
        "cne_p255", "用 will 说周末打算", "日常表达", 4, "下", CH4X["rev"], "application",
        "用 I will … / We will … 说出周末打算做的事。",
        ["能选出正确的 will 计划句", "能读懂简短打算"],
        ("想说「我们周末将去野餐」，应选哪一句？", "We will have a picnic this weekend."),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p255", [
        ("basic", "想说「我们周末将去野餐」，应选哪一句？", "We will have a picnic this weekend.",
         ["We will having a picnic this weekend.", "We will has a picnic.", "We are will picnic."],
         "will + 动词原形。"),
        ("basic", "I will visit my grandma. 我打算？", "看望奶奶",
         ["去电影院上班", "去博物馆睡觉", "不去了"], "visit grandma。"),
        ("standard", "哪一句是周末打算？", "I will go to the cinema on Saturday.",
         ["I went to the cinema yesterday only.", "I go to the cinema yesterday.", "I going cinema."],
         "will … on Saturday。"),
        ("challenge", "读一读：Tom will go to the museum. Amy will stay at home. 谁打算去博物馆？", "汤姆",
         ["艾米", "两人都去", "谁都不去"], "Tom will go to the museum。"),
    ])
    deps += [
        dep("cne_p255", "cne_p254", "hard", "先认计划词，再说 will 打算。"),
        dep("cne_p255", "cne_p090", "soft", "先会说该做的事。"),
    ]

    topics.append(topic(
        "cne_p256", "讨论精彩周末计划", "日常表达", 4, "下", CH4X["rev"], "application",
        "综合用 What will you do …? / Let's … 讨论一个精彩的周末计划。",
        ["能选出询问周末计划的问句", "能选出合适的建议句"],
        ("想问「你周末将做什么？」，应选哪一句？", "What will you do this weekend?"),
        "ces-2022:1.FU.02", NOTE4X,
    ))
    questions += four_qs("cne_p256", [
        ("basic", "想问「你周末将做什么？」，应选哪一句？", "What will you do this weekend?",
         ["What will you did this weekend?", "What do you did this weekend?", "What you will do?"],
         "What will you do …"),
        ("basic", "Let's go to the park! 这句是在？", "提议去公园",
         ["禁止去公园", "询问价格", "说明昨天去了"], "Let's 表提议。"),
        ("standard", "—What will you do on Sunday? —____.", "I will read books.",
         ["I read books yesterday only.", "I am books.", "Yes, I am Sunday."],
         "用 will 回答打算。"),
        ("challenge", "读对话：—Let's visit the museum! —Great! I will take a camera. 他们同意做什么？", "参观博物馆",
         ["只在家睡觉", "去买菜", "取消计划"], "Let's visit the museum，对方说 Great。"),
    ])
    deps += [dep("cne_p256", "cne_p255", "hard", "先会用 will 说打算，再讨论计划。")]

    topics.append(topic(
        "cne_p257", "读懂周末计划短文", "读写", 4, "下", CH4X["rev"], "application",
        "读周末计划短文或海报，找出时间、地点和活动。",
        ["能根据短文选出计划内容", "能选出和短文一致的句子"],
        ("读一读：On Saturday we will have a picnic. 星期六计划做什么？", "野餐"),
        "ces-2022:1.RW.02", NOTE4X,
    ))
    questions += four_qs("cne_p257", [
        ("basic", "读一读：On Saturday we will have a picnic. 星期六计划做什么？", "野餐",
         ["看电影", "睡觉", "考试"], "have a picnic。"),
        ("basic", "读一读：Sunday: visit the museum. 星期天去哪里？", "博物馆",
         ["电影院", "农场", "医院"], "visit the museum。"),
        ("standard", "读一读：My great weekend plan: cinema on Saturday, park on Sunday. 哪一句一致？", "周日去公园。",
         ["周日去电影院。", "周六去公园。", "没有计划。"], "park on Sunday。"),
        ("challenge", "读一读：We will meet at 9:00. We will go to the cinema. Don't be late! 集合几点？", "9 点",
         ["电影院开门时间未写", "8 点", "晚上"], "meet at 9:00。"),
    ])
    deps += [dep("cne_p257", "cne_p256", "hard", "读懂计划前先会讨论计划。")]

    # ========== 五下 densify (+18) ==========
    # U1 My day
    topics.append(topic(
        "cne_p258", "频率词 often usually sometimes", "词汇", 5, "下", CH5X[1], "conceptual",
        "认读 often、usually、sometimes、always、never 等频率词，描述作息习惯（Part B）。",
        ["能选出频率词的意思", "能根据中文选出英文单词"],
        ("often 的意思是？", "经常"),
        "ces-2022:2.VO.01", NOTE5X,
    ))
    questions += four_qs("cne_p258", [
        ("basic", "often 的意思是？", "经常",
         ["从不", "有时", "总是"], "often 是经常。"),
        ("basic", "哪个单词的意思是「有时」？", "sometimes",
         ["always", "never", "usually"], "sometimes 是有时。"),
        ("standard", "「从不」用哪个词？", "never",
         ["always", "often", "usually"], "never 是从不。"),
        ("challenge", "读一读：I usually get up early. I never go to bed late. 哪一句一致？", "我从不晚睡。",
         ["我总是晚睡。", "我从不早起。", "我不早起。"], "never go to bed late。"),
    ])
    deps += [dep("cne_p258", "cne_p133", "soft", "先认一天活动，再学频率词。")]

    topics.append(topic(
        "cne_p259", "用频率词谈作息", "日常表达", 5, "下", CH5X[1], "application",
        "用 I usually / often … at … 描述自己的一天。",
        ["能选出带频率词的作息句", "能读懂频率与时间"],
        ("想说「我通常六点起床」，应选哪一句？", "I usually get up at 6 o'clock."),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p259", [
        ("basic", "想说「我通常六点起床」，应选哪一句？", "I usually get up at 6 o'clock.",
         ["I usually gets up at 6 o'clock.", "I usual get up at 6.", "I get usually up at 6."],
         "usually 放在实义动词前。"),
        ("basic", "I sometimes eat dinner at 7. 我怎样吃晚饭？", "有时七点吃",
         ["从不吃", "总是九点吃", "没有晚饭"], "sometimes … at 7。"),
        ("standard", "哪一句正确？", "She often cleans her room on the weekend.",
         ["She often clean her room on the weekend.", "She cleans often her room.", "She often cleaning her room."],
         "三单 cleans；often 在动词前。"),
        ("challenge", "读一读：Mike always goes to school at 7. He never late for class. 哪句与短文最贴近？", "他总是七点去上学。",
         ["他从不去上学。", "他有时七点去。", "他总是迟到。"], "always … at 7。"),
    ])
    deps += [
        dep("cne_p259", "cne_p258", "hard", "先认频率词，再练作息句。"),
        dep("cne_p259", "cne_p135", "soft", "先会谈论作息。"),
    ]

    # U2 My favourite season
    topics.append(topic(
        "cne_p260", "季节活动词汇", "词汇", 5, "下", CH5X[2], "conceptual",
        "认读 plant flowers、swim、pick apples、make a snowman 等季节活动（Part B）。",
        ["能选出季节活动的意思", "能把活动与季节对应"],
        ("「堆雪人」用哪一组？", "make a snowman"),
        "ces-2022:2.VO.01", NOTE5X,
    ))
    questions += four_qs("cne_p260", [
        ("basic", "「堆雪人」用哪一组？", "make a snowman",
         ["plant flowers", "go swimming", "pick apples"], "make a snowman。"),
        ("basic", "pick apples 的意思是？", "摘苹果",
         ["种花", "游泳", "堆雪人"], "pick apples。"),
        ("standard", "夏天常做的活动是？", "go swimming",
         ["make a snowman", "plant flowers in the snow", "pick ice"], "夏天适合游泳。"),
        ("challenge", "读一读：In spring I plant flowers. In autumn I pick apples. 春天做什么？", "种花",
         ["摘苹果", "堆雪人", "游泳"], "plant flowers in spring。"),
    ])
    deps += [dep("cne_p260", "cne_p137", "soft", "先认季节词，再学季节活动。")]

    topics.append(topic(
        "cne_p261", "Why 与 because 说理由", "语法", 5, "下", CH5X[2], "procedural",
        "用 Why do you like …? / Because … 说明喜欢某季节的原因。",
        ["能选出正确的 Why / Because 问答", "能读懂简单理由"],
        ("想问「你为什么喜欢夏天？」，应选哪一句？", "Why do you like summer?"),
        "ces-2022:2.GR.02", NOTE5X,
    ))
    questions += four_qs("cne_p261", [
        ("basic", "想问「你为什么喜欢夏天？」，应选哪一句？", "Why do you like summer?",
         ["Why does you like summer?", "Why do you likes summer?", "What do you like summer?"],
         "Why do you like …"),
        ("basic", "—Why do you like spring? —____.", "Because there are flowers.",
         ["Because I don't.", "Yes, I do.", "It is Monday."], "用 Because 回答 Why。"),
        ("standard", "哪一句正确？", "I like winter because I can make a snowman.",
         ["I like winter because I can making a snowman.", "I like winter so I can snowman.", "Because I like winter make snowman."],
         "because + 完整句。"),
        ("challenge", "读一读：—Why do you like autumn? —Because it is cool and golden. 喜欢秋天的原因是？", "凉爽又金黄",
         ["很热", "可以游泳", "没有理由"], "cool and golden。"),
    ])
    deps += [
        dep("cne_p261", "cne_p138", "hard", "先会谈最喜欢的季节，再说理由。"),
        dep("cne_p261", "cne_p260", "soft", "理由常涉及季节活动。"),
    ]

    topics.append(topic(
        "cne_p262", "读懂季节与理由短文", "读写", 5, "下", CH5X[2], "application",
        "读季节短文，找出最喜欢的季节、活动和原因。",
        ["能根据短文选出季节信息", "能选出和短文一致的句子"],
        ("读一读：I like summer best because I can swim. 最喜欢哪个季节？", "夏天"),
        "ces-2022:2.RW.01", NOTE5X,
    ))
    questions += four_qs("cne_p262", [
        ("basic", "读一读：I like summer best because I can swim. 最喜欢哪个季节？", "夏天",
         ["春天", "秋天", "冬天"], "summer。"),
        ("basic", "读一读：Winter is white. I can make a snowman. 冬天可以做什么？", "堆雪人",
         ["游泳", "摘苹果", "种花"], "make a snowman。"),
        ("standard", "读一读：My favourite season is spring. There are pretty flowers. 哪一句一致？", "春天有漂亮的花。",
         ["春天没有花。", "最喜欢冬天。", "夏天有雪。"], "pretty flowers。"),
        ("challenge", "读一读：Amy likes autumn because she can pick apples. Tom likes winter because he can ski. 谁喜欢秋天？", "艾米",
         ["汤姆", "两人都喜欢", "谁都不喜欢"], "Amy likes autumn。"),
    ])
    deps += [
        dep("cne_p262", "cne_p261", "hard", "读懂理由前先会 Why/Because。"),
        dep("cne_p262", "cne_p139", "soft", "先会读季节短文。"),
    ]

    # U3 My school calendar
    topics.append(topic(
        "cne_p263", "更多月份", "词汇", 5, "下", CH5X[3], "conceptual",
        "认读 January、February、April、June、July、August、September、November 等更多月份。",
        ["能选出月份单词的意思", "能按顺序判断月份"],
        ("哪个单词的意思是「一月」？", "January"),
        "ces-2022:2.VO.01", NOTE5X,
    ))
    questions += four_qs("cne_p263", [
        ("basic", "哪个单词的意思是「一月」？", "January",
         ["June", "July", "February"], "January 是一月。"),
        ("basic", "September 的意思是？", "九月",
         ["十一月", "八月", "四月"], "September 是九月。"),
        ("standard", "「八月」用哪个词？", "August",
         ["April", "Augusts", "Autumn"], "August 是八月。"),
        ("challenge", "读一读：School starts in September. Winter holiday is in January and February. 开学在几月？", "九月",
         ["一月", "二月", "八月"], "starts in September。"),
    ])
    deps += [dep("cne_p263", "cne_p140", "hard", "先认部分月份，再扩更多月份。")]

    topics.append(topic(
        "cne_p264", "谈论校历活动月份", "日常表达", 5, "下", CH5X[3], "application",
        "用 When is …? / It's in … 谈论校历上的活动在几月。",
        ["能选出正确的月份问答", "能读懂校历活动句"],
        ("想问「运动会在几月？」，应选哪一句？", "When is the sports meet?"),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p264", [
        ("basic", "想问「运动会在几月？」，应选哪一句？", "When is the sports meet?",
         ["When are the sports meet?", "What is the sports meet month?", "When the sports meet is?"],
         "When is …"),
        ("basic", "—When is the school trip? —____.", "It's in May.",
         ["It's on May.", "It's at May.", "It's May in."], "月份用 in。"),
        ("standard", "哪一句正确？", "The singing contest is in November.",
         ["The singing contest is on November.", "The singing contest is at November.", "The singing contest in is November."],
         "in November。"),
        ("challenge", "读一读：Sports meet — October; New Year party — December. 元旦晚会在几月？", "十二月",
         ["十月", "十一月", "一月"], "New Year party — December。"),
    ])
    deps += [
        dep("cne_p264", "cne_p142", "soft", "先会谈节日在几月。"),
        dep("cne_p264", "cne_p263", "hard", "先认更多月份。"),
    ]

    # U4 When is the art show
    topics.append(topic(
        "cne_p265", "更多序数词", "语法", 5, "下", CH5X[4], "procedural",
        "认读 fifth、twelfth、 twentieth、twenty-first、thirtieth 等更多序数词。",
        ["能选出序数词读法", "能区分基数词与序数词"],
        ("12th 怎么读？", "twelfth"),
        "ces-2022:2.GR.04", NOTE5X,
    ))
    questions += four_qs("cne_p265", [
        ("basic", "12th 怎么读？", "twelfth",
         ["twelve", "twentieth", "second"], "12th 是 twelfth。"),
        ("basic", "哪一个是序数词？", "fifth",
         ["five", "fifteen", "fifty"], "fifth 是序数词。"),
        ("standard", "21st 的英文是？", "twenty-first",
         ["twenty-one", "twenty-firsts", "twelve-first"], "21st 是 twenty-first。"),
        ("challenge", "读一读：My birthday is on the 20th. The show is on the 30th. 演出在几号？", "30 日",
         ["20 日", "12 日", "21 日"], "30th。"),
    ])
    deps += [dep("cne_p265", "cne_p144", "hard", "先会基础序数词，再学更多序数词。")]

    topics.append(topic(
        "cne_p266", "When is your birthday", "日常表达", 5, "下", CH5X[4], "application",
        "用 When is your birthday? / My birthday is on … 询问和回答生日。",
        ["能选出正确的生日问答", "能用 on + 月 + 序数词说日期"],
        ("想问「你的生日是哪一天？」，应选哪一句？", "When is your birthday?"),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p266", [
        ("basic", "想问「你的生日是哪一天？」，应选哪一句？", "When is your birthday?",
         ["When are your birthday?", "What is you birthday?", "When your birthday is?"],
         "When is your birthday?"),
        ("basic", "My birthday is on March 21st. 生日是？", "3 月 21 日",
         ["3 月 12 日", "2 月 21 日", "3 月 1 日"], "March 21st。"),
        ("standard", "哪一句正确？", "Her birthday is on May 5th.",
         ["Her birthday is in May 5th.", "Her birthday is at May 5th.", "Her birthday is May on 5th."],
         "具体日期用 on。"),
        ("challenge", "读对话：—When is your birthday? —It's on April 1st. The art show is on that day too! 艺术节和生日？", "同一天",
         ["差一个月", "不在四月", "没有日期"], "都在 April 1st。"),
    ])
    deps += [
        dep("cne_p266", "cne_p145", "hard", "先会说日期，再问生日。"),
        dep("cne_p266", "cne_p265", "soft", "生日日期常用序数词。"),
    ]

    topics.append(topic(
        "cne_p267", "读懂活动日程表", "读写", 5, "下", CH5X[4], "application",
        "读活动通知或日程，找出几月几日有什么活动。",
        ["能根据通知选出日期", "能选出和通知一致的句子"],
        ("读一读：The art show is on April 1st. 艺术节是哪一天？", "4 月 1 日"),
        "ces-2022:2.RW.01", NOTE5X,
    ))
    questions += four_qs("cne_p267", [
        ("basic", "读一读：The art show is on April 1st. 艺术节是哪一天？", "4 月 1 日",
         ["4 月 5 日", "5 月 1 日", "1 月 4 日"], "April 1st。"),
        ("basic", "读一读：Reading festival — May 4th. 读书节在？", "5 月 4 日",
         ["4 月 5 日", "5 月 1 日", "4 月 4 日"], "May 4th。"),
        ("standard", "读一读：Maths test on March 12th; English test on March 15th. 英语考试在几号？", "15 日",
         ["12 日", "13 日", "11 日"], "English … 15th。"),
        ("challenge", "读一读：Things to do: April 1 art show; April 5 school trip; May 1 holiday. 最早的活动是？", "艺术节",
         ["春游", "五一假期", "没有活动"], "April 1 最早。"),
    ])
    deps += [
        dep("cne_p267", "cne_p266", "hard", "先会说生日日期，再读日程。"),
        dep("cne_p267", "cne_p146", "soft", "先会读日期通知。"),
    ]

    # U5 Whose dog is it
    topics.append(topic(
        "cne_p268", "现在分词变化", "语法", 5, "下", CH5X[5], "procedural",
        "掌握 run→running、swim→swimming、write→writing、take→taking 等常见 -ing 变化。",
        ["能选出正确的 -ing 形式", "能判断双写或去 e"],
        ("run 的现在分词是？", "running"),
        "ces-2022:2.GR.06", NOTE5X,
    ))
    questions += four_qs("cne_p268", [
        ("basic", "run 的现在分词是？", "running",
         ["runing", "runs", "ran"], "重读闭音节双写 n 再加 ing。"),
        ("basic", "write 的现在分词是？", "writing",
         ["writeing", "writting", "writes"], "去 e 加 ing。"),
        ("standard", "哪一组正确？", "swim → swimming",
         ["swim → swiming", "swim → swimmings", "swim → swam"], "双写 m 加 ing。"),
        ("challenge", "读一读：He is ____ (take) pictures. 横线应填？", "taking",
         ["takeing", "takinge", "took"], "take → taking。"),
    ])
    deps += [dep("cne_p268", "cne_p148", "hard", "先会现在进行时结构，再练 -ing 变化。")]

    topics.append(topic(
        "cne_p269", "看图说谁的与正在做什么", "日常表达", 5, "下", CH5X[5], "application",
        "综合用 Whose … is it? 与 What is … doing? 描述图中人物和物品。",
        ["能选出正确的综合问答", "能读懂简短看图描述"],
        ("想问「它正在做什么？」，应选哪一句？", "What is it doing?"),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p269", [
        ("basic", "想问「它正在做什么？」，应选哪一句？", "What is it doing?",
         ["What is it do?", "What are it doing?", "What it is doing?"],
         "What is it doing?"),
        ("basic", "—Whose dog is it? —____. —What's it doing? —It's running.", "It's mine",
         ["It's my", "It's me", "It's I"], "名词性物主代词 mine。"),
        ("standard", "哪一组问答正确？", "Whose cat is it? It's hers. It's sleeping.",
         ["Whose cat is it? It's her. It sleeping.", "Whose cat is it? It's hers. It sleep.", "Who cat is it? It's hers."],
         "hers + is sleeping。"),
        ("challenge", "读一读：The dog is John's. It is eating. Whose dog is eating?", "约翰的狗",
         ["我的狗", "她的猫", "无人的狗"], "John's dog is eating。"),
    ])
    deps += [
        dep("cne_p269", "cne_p149", "hard", "先会 Whose 与正在做的事。"),
        dep("cne_p269", "cne_p268", "soft", "描述动作常用 -ing。"),
    ]

    # U6 Work quietly (restore)
    topics.append(topic(
        "cne_p270", "安静做事用词", "词汇", 5, "下", CH5X[6], "conceptual",
        "认读 quietly、loudly、keep、clean、turn、right 等与安静做事、公共秩序有关的词。",
        ["能选出规则相关词的意思", "能根据中文选出英文单词"],
        ("quietly 的意思是？", "安静地"),
        "ces-2022:2.VO.01", NOTE5X,
    ))
    questions += four_qs("cne_p270", [
        ("basic", "quietly 的意思是？", "安静地",
         ["大声地", "快速地", "慢慢地"], "quietly 是安静地。"),
        ("basic", "哪个单词的意思是「大声地」？", "loudly",
         ["quietly", "clean", "right"], "loudly 是大声地。"),
        ("standard", "keep your desk clean 是在说？", "保持书桌干净",
         ["靠右走", "大声说话", "跑步"], "keep … clean。"),
        ("challenge", "读一读：Talk quietly. Don't talk loudly. 两句都在强调？", "要小声说话",
         ["要大喊", "不要说话也可以大喊", "保持书桌"], "quietly，不要 loudly。"),
    ])
    deps += [
        dep("cne_p270", "cne_p151", "soft", "四下已学班级规则词，五下再学安静做事词。"),
        dep("cne_p270", "cne_p148", "soft", "本单元常与正在做的事一起出现。"),
    ]

    topics.append(topic(
        "cne_p271", "Keep 与 No 类规则", "语法", 5, "下", CH5X[6], "procedural",
        "用 Keep … / No + doing / Talk quietly 等表达公共场所规则。",
        ["能选出正确的规则句式", "能区分 Keep 与 No"],
        ("想说「禁止饮食」，应选哪一句？", "No eating or drinking."),
        "ces-2022:2.GR.07", NOTE5X,
    ))
    questions += four_qs("cne_p271", [
        ("basic", "想说「禁止饮食」，应选哪一句？", "No eating or drinking.",
         ["No eat or drink.", "Not eating or drinking.", "Don't eating."],
         "No + doing。"),
        ("basic", "Keep to the right. 这句是在说？", "靠右走",
         ["靠左走", "保持安静", "不要走"], "Keep to the right。"),
        ("standard", "哪一句正确？", "Keep your desk clean.",
         ["Keep your desk cleaning.", "Keep your desk to clean.", "Keeping your desk clean is no."],
         "Keep + 名词 + 形容词。"),
        ("challenge", "读一读：Library rules: Talk quietly. No eating. Keep the books clean. 可以做的是？", "小声说话",
         ["吃零食", "把书弄脏", "大声喊"], "Talk quietly 是允许的要求。"),
    ])
    deps += [
        dep("cne_p271", "cne_p270", "hard", "先认安静做事词，再练 Keep/No。"),
        dep("cne_p271", "cne_p152", "soft", "先接触过祈使句。"),
    ]

    topics.append(topic(
        "cne_p272", "说图书馆与教室规则", "日常表达", 5, "下", CH5X[6], "application",
        "用祈使句说出图书馆、教室里应安静做事时的规则。",
        ["能选出合适的规则句子", "能判断场合该用哪条规则"],
        ("在图书馆应选哪一句？", "Talk quietly."),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p272", [
        ("basic", "在图书馆应选哪一句？", "Talk quietly.",
         ["Talk loudly.", "Run fast.", "Eat snacks."], "图书馆要小声。"),
        ("basic", "Work quietly. 这句要求？", "安静地做事",
         ["大声玩", "跑出教室", "吃东西"], "Work quietly。"),
        ("standard", "哪一句适合教室？", "Keep your desk clean.",
         ["Shout in class.", "Throw paper on the floor.", "Run between desks."],
         "保持书桌干净。"),
        ("challenge", "读情景：同学们在阅览室看书。管理员最该说？", "Please work quietly.",
         ["Please shout.", "Please run.", "Please eat here."], "阅览室要安静做事。"),
    ])
    deps += [
        dep("cne_p272", "cne_p271", "hard", "先会 Keep/No 句式，再说场合规则。"),
        dep("cne_p272", "cne_p153", "soft", "四下已练说过规则。"),
    ]

    topics.append(topic(
        "cne_p273", "正在做与遵守规则", "日常表达", 5, "下", CH5X[6], "application",
        "把现在进行时与规则结合：描述别人正在做什么，并判断是否守规。",
        ["能选出进行时描述", "能判断行为是否符合规则"],
        ("想说「他们正在安静地看书」，应选哪一句？", "They are reading quietly."),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p273", [
        ("basic", "想说「他们正在安静地看书」，应选哪一句？", "They are reading quietly.",
         ["They are read quietly.", "They reading quietly.", "They is reading quietly."],
         "are + reading + quietly。"),
        ("basic", "He is shouting in the library. 他守规吗？", "不守规",
         ["守规", "在睡觉", "在排队"], "图书馆不应大喊。"),
        ("standard", "哪一句既写正在做又守规？", "She is walking quietly in the hall.",
         ["She is running in the hall.", "She walking quietly.", "She are walking quietly."],
         "walking quietly。"),
        ("challenge", "读一读：Rule: No eating. Look! Tom is eating an apple. 汤姆？", "违规了",
         ["守规", "没有在吃", "规则允许吃"], "No eating，他却 is eating。"),
    ])
    deps += [
        dep("cne_p273", "cne_p148", "hard", "先会现在进行时。"),
        dep("cne_p273", "cne_p272", "hard", "先会说规则。"),
    ]

    topics.append(topic(
        "cne_p274", "排队与轮流", "日常表达", 5, "下", CH5X[6], "application",
        "用 take turns、wait in line、Keep to the right 等表达排队与轮流。",
        ["能选出排队轮流相关句子", "能读懂简短秩序提示"],
        ("想说「请排队」，应选哪一句？", "Please wait in line."),
        "ces-2022:2.FU.02", NOTE5X,
    ))
    questions += four_qs("cne_p274", [
        ("basic", "想说「请排队」，应选哪一句？", "Please wait in line.",
         ["Please wait in lines.", "Please waiting in line.", "Please wait on line classroom."],
         "wait in line。"),
        ("basic", "take turns 的意思是？", "轮流",
         ["插队", "奔跑", "大喊"], "take turns 是轮流。"),
        ("standard", "哪一句正确？", "Let's take turns.",
         ["Let's take turning.", "Let's takes turns.", "Let's take turnings."],
         "take turns。"),
        ("challenge", "读一读：Keep to the right. Wait in line. Take turns. 这三条都在讲？", "公共秩序",
         ["怎么做饭", "怎么游泳", "怎么画画"], "靠右、排队、轮流都是秩序。"),
    ])
    deps += [dep("cne_p274", "cne_p272", "hard", "先会说基本规则，再学排队轮流。")]

    topics.append(topic(
        "cne_p275", "读懂公共场所规则", "读写", 5, "下", CH5X[6], "application",
        "读图书馆、教室或公园规则短文，找出可以做和不可以做的事。",
        ["能根据短文选出规则", "能选出和短文一致的句子"],
        ("读一读：Talk quietly. Do not eat. 不可以做什么？", "吃东西"),
        "ces-2022:2.RW.01", NOTE5X,
    ))
    questions += four_qs("cne_p275", [
        ("basic", "读一读：Talk quietly. Do not eat. 不可以做什么？", "吃东西",
         ["小声说话", "看书", "排队"], "Do not eat。"),
        ("basic", "读一读：Keep to the right. 应怎样走？", "靠右",
         ["靠左", "跑", "停住不走"], "Keep to the right。"),
        ("standard", "读一读：We are in the library. Please work quietly. Keep the books clean. 哪一句一致？", "请安静做事并爱护书。",
         ["可以吃东西。", "可以大喊。", "可以把书撕坏。"], "work quietly … books clean。"),
        ("challenge", "读一读：Rules: 1. Take turns. 2. No running. 3. Keep the desk clean. 小明在跑，他违反了第几条？", "第 2 条",
         ["第 1 条", "第 3 条", "没有违反"], "No running 是第 2 条。"),
    ])
    deps += [
        dep("cne_p275", "cne_p273", "hard", "读懂规则前先会进行时与守规。"),
        dep("cne_p275", "cne_p274", "soft", "短文可能含排队轮流。"),
        dep("cne_p275", "cne_p154", "soft", "四下已练读规则。"),
    ]

    return topics, questions, deps


def insert_topics(topics, new_topics):
    chapter_news = defaultdict(list)
    for nt in new_topics:
        chapter_news[nt["chapter"]].append(nt)

    inserts = []
    for ch, nlist in chapter_news.items():
        last = -1
        for i, t in enumerate(topics):
            if t.get("chapter") == ch:
                last = i
        if last < 0:
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

    # ensure 五下 U4 chapter title consistent (art show)
    for t in topics:
        if t.get("grade") == 5 and t.get("semester") == "下" and "When is" in str(t.get("chapter", "")):
            if "Easter" in t["chapter"]:
                t["chapter"] = CH5X[4]

    topics = insert_topics(topics, new_topics)
    q_ids = {q["id"] for q in questions}
    for q in new_qs:
        if q["id"] not in q_ids:
            questions.append(q)
            q_ids.add(q["id"])

    dep_keys = {(d["topicId"], d["prerequisiteId"], d["strength"]) for d in deps}
    added_deps = 0
    for d in new_deps:
        k = (d["topicId"], d["prerequisiteId"], d["strength"])
        if k not in dep_keys:
            deps.append(d)
            dep_keys.add(k)
            added_deps += 1

    dump("topics.json", topics)
    dump("questions.json", questions)
    dump("dependencies.json", deps)

    eng_p = [t for t in topics if str(t["id"]).startswith("cne_p")]
    g4x = [t for t in eng_p if t["grade"] == 4 and t["semester"] == "下"]
    g5x = [t for t in eng_p if t["grade"] == 5 and t["semester"] == "下"]
    print("新增知识点", len(new_topics), "题", len(new_qs), "边", added_deps)
    print("小学英语总点数", len(eng_p))
    print("四下", len(g4x), "五下", len(g5x))
    u6 = [t for t in g5x if "Work quietly" in t.get("chapter", "")]
    print("五下 Unit6", len(u6), [t["name"] for t in u6])
    rev = [t for t in g4x if "weekend plan" in t.get("chapter", "")]
    print("四下 Revision", len(rev), [t["name"] for t in rev])


if __name__ == "__main__":
    main()
