# -*- coding: utf-8 -*-
"""小学道德与法治数据的登记与题目生成。由 scripts/mor_build.py 调用。

目录依据（公开目录，dzkbw / 统编教材）：
- 一上 2024 秋、一下 2025 春、二上 2025 秋、二下 2026 春、三上 2025 秋、三下 2026 春、
  四上 2026 秋、五上 2026 秋、六上 2026 秋：统编修订版。
- 四下、五下、六下：修订版公开目录仍用现行统编版。
"""

import re

TOPICS = []
HARD = []

# (年级, 学期, 单元) -> (单元名, 领域, 默认课标符号)
UNITS = {
    (1, "上", 1): ("我是小学生啦", "学校生活", "xx1_sch"),
    (1, "上", 2): ("过好校园生活", "学校生活", "xx1_sch"),
    (1, "上", 3): ("养成良好习惯", "生活与安全", "ls1_hab"),
    (1, "上", 4): ("我们讲文明", "社会规则", "sh1_civ"),
    (1, "下", 1): ("我有新面貌", "生活与安全", "ls1_hab"),
    (1, "下", 2): ("我们一起长大", "学校生活", "xx1_sch"),
    (1, "下", 3): ("幸福一家人", "家庭与亲情", "jt1_fam"),
    (1, "下", 4): ("争做中国好儿童", "公民与国家", "gm1_nat"),
    (2, "上", 1): ("过好节假日", "生活与安全", "ls1_hab"),
    (2, "上", 2): ("我爱我们班", "学校生活", "xx1_sch"),
    (2, "上", 3): ("我的家乡美", "自然与环境", "zr1_nat"),
    (2, "上", 4): ("我爱我们的祖国", "公民与国家", "gm1_nat"),
    (2, "下", 1): ("我乐观我向上", "生活与安全", "ls1_hab"),
    (2, "下", 2): ("大自然，谢谢您", "自然与环境", "zr1_nat"),
    (2, "下", 3): ("传统美德我弘扬", "社会规则", "sh1_civ"),
    (2, "下", 4): ("播下梦想的种子", "生活与安全", "ls1_hab"),
    (3, "上", 1): ("做学习的主人", "学校生活", "xx2_cls"),
    (3, "上", 2): ("爱科学 学科学", "生活与安全", "ls2_safe"),
    (3, "上", 3): ("在集体中成长", "学校生活", "xx2_cls"),
    (3, "上", 4): ("公共生活靠大家", "社会规则", "sh2_rule"),
    (3, "下", 1): ("共建美好生活", "公民与国家", "gm2_cit"),
    (3, "下", 2): ("劳动最光荣", "生活与安全", "ls2_safe"),
    (3, "下", 3): ("我是家庭一员", "家庭与亲情", "jt2_share"),
    (3, "下", 4): ("我们来交往", "社会规则", "sh2_rule"),
    (4, "上", 1): ("我们的班集体", "学校生活", "xx2_cls"),
    (4, "上", 2): ("少年在成长", "生活与安全", "ls2_safe"),
    (4, "上", 3): ("生活在信息社会", "生活与安全", "ls2_safe"),
    (4, "上", 4): ("做文明的消费者", "社会规则", "sh2_rule"),
    (4, "下", 1): ("同伴与交往", "社会规则", "sh2_rule"),
    (4, "下", 2): ("做聪明的消费者", "社会规则", "sh2_rule"),
    (4, "下", 3): ("美好生活哪里来", "社会规则", "sh2_rule"),
    (4, "下", 4): ("感受家乡文化 关心家乡发展", "公民与国家", "gm2_cit"),
    (5, "上", 1): ("没有共产党就没有新中国", "公民与国家", "gm3_law"),
    (5, "上", 2): ("建设社会主义新中国", "公民与国家", "gm3_law"),
    (5, "上", 3): ("进行改革开放", "公民与国家", "gm3_law"),
    (5, "上", 4): ("开创新时代", "公民与国家", "gm3_law"),
    (5, "下", 1): ("我们一家人", "家庭与亲情", "jt3_virt"),
    (5, "下", 2): ("公共生活靠大家", "社会规则", "sh3_pub"),
    (5, "下", 3): ("百年追梦 复兴中华", "公民与国家", "gm3_law"),
    (6, "上", 1): ("生活中的法律", "公民与国家", "gm3_law"),
    (6, "上", 2): ("公民与国家", "公民与国家", "gm3_law"),
    (6, "上", 3): ("我们受特殊保护", "公民与国家", "gm3_law"),
    (6, "上", 4): ("知法守法 依法维权", "公民与国家", "gm3_law"),
    (6, "下", 1): ("完善自我 健康成长", "社会规则", "sh3_pub"),
    (6, "下", 2): ("爱护地球 共同责任", "自然与环境", "zr3_earth"),
    (6, "下", 3): ("多样文明 多彩生活", "公民与国家", "gm3_law"),
    (6, "下", 4): ("让世界更美好", "公民与国家", "gm3_law"),
}

DOMAINS = ("生活与安全", "学校生活", "家庭与亲情", "社会规则", "公民与国家", "自然与环境")
CODE_OF = {"LS": "生活与安全", "XX": "学校生活", "JT": "家庭与亲情", "SH": "社会规则", "GM": "公民与国家", "ZR": "自然与环境"}

# 课标条目是《义务教育道德与法治课程标准（2022年版）》相关学段要求的公开转述，不是逐页核对的原文。
STANDARD_ROWS = [
    ("ls1_hab", "1", "LS", "健康安全的生活", "养成规律作息、卫生饮食、安全出行等基本生活习惯，知道遇到危险要告诉信任的大人。"),
    ("xx1_sch", "1", "XX", "适应学校生活", "认识校园环境和师生关系，遵守课堂和课间基本要求，友善与同学相处。"),
    ("jt1_fam", "1", "JT", "感受家庭关爱", "感受家人的爱，做力所能及的家务，尊敬长辈。"),
    ("sh1_civ", "1", "SH", "公共文明起步", "在公共场所轻声、排队、不乱扔、爱护公物，对人有礼貌。"),
    ("gm1_nat", "1", "GM", "爱祖国爱集体", "认识国旗，参加升旗礼仪，了解少先队和儿童节等基本常识，表达对祖国的热爱。"),
    ("zr1_nat", "1", "ZR", "亲近自然", "亲近大自然，爱护花草树木和小动物，节约一张纸一滴水。"),
    ("ls2_safe", "2", "LS", "安全与自我保护", "珍爱生命，掌握基本安全与自我保护方法，合理使用电子媒体。"),
    ("xx2_cls", "2", "XX", "班集体生活", "参与班级事务，遵守班规，关爱同学，为集体作贡献。"),
    ("jt2_share", "2", "JT", "家庭责任", "体会家庭责任，少让父母操心，弘扬家庭美德。"),
    ("sh2_rule", "2", "SH", "规则与交往", "理解生活离不开规则，诚信交往，正确处理同伴冲突，文明消费。"),
    ("gm2_cit", "2", "GM", "家乡与祖国", "了解家乡与祖国，尊重各民族，关心国家发展的基本事实。"),
    ("zr2_env", "2", "ZR", "绿色生活", "认识常见环境问题，践行垃圾分类、低碳生活等环保行动。"),
    ("ls3_grow", "3", "LS", "健全人格与反思", "学会尊重、宽容与反思，正确面对成长中的问题。"),
    ("xx3_learn", "3", "XX", "学会学习与集体自治", "做学习的主人，通过选举、协商参与班级管理。"),
    ("jt3_virt", "3", "JT", "家风与亲情沟通", "读懂家人心意，建设美好家庭，传承优秀家风。"),
    ("sh3_pub", "3", "SH", "公共生活与奉献", "维护公共秩序，热心公益，在公共生活中负责任。"),
    ("gm3_law", "3", "GM", "法治与公民", "知道法律与宪法的基本作用，了解公民权利义务和国家机构，依法保护自己，做守法小公民；了解近代以来中华民族奋斗与国家发展的基本史实。"),
    ("zr3_earth", "3", "ZR", "地球家园与多样文明", "认识地球是人类共同家园，了解应对灾害的基本方法，尊重多样文化，热爱和平。"),
]

TYPES = ("conceptual", "procedural", "reasoning", "application", "modeling")
CRIT = {
    "生活与安全": ["能说出与本课相关的安全或健康做法", "能在情境中选择正确行为"],
    "学校生活": ["能说出校园或班级中的正确做法", "能说明为什么要这样做"],
    "家庭与亲情": ["能说出关爱家人、分担家务的做法", "能在情境中选择体贴家人的行为"],
    "社会规则": ["能说出公共场合应遵守的规则", "能判断违反规则的行为并改正"],
    "公民与国家": ["能说出与本课相关的基本常识", "能说明自己可以怎样做一名好学生或小公民"],
    "自然与环境": ["能说出爱护自然或节约资源的做法", "能在生活中选择环保行为"],
}
NOTE = "统编版该课的常见教学内容。条目是公开转述，不是逐页核对的原文。"


def chapter(grade, sem, unit):
    cn = "零一二三四五六"[grade]
    title = UNITS[(grade, sem, unit)][0]
    return "%s年级%s册 第%d单元 %s" % (cn, sem, unit, title)


def hard(topic, prereq, reason):
    HARD.append((topic, prereq, reason))


_CUR = {}


def vol(grade, sem):
    _CUR["g"], _CUR["s"] = grade, sem


def K(key, name, unit, typ, desc, qs, std=None, domain=None):
    """登记一个知识点。qs 是 4 道选择题：(题干, 正确答案, [三个干扰项], 解析)，难度依次 basic、basic、standard、challenge。"""
    g, s = _CUR["g"], _CUR["s"]
    if (g, s, unit) not in UNITS:
        raise SystemExit("%s 单元未登记：%s%s 第%d单元" % (key, g, s, unit))
    _u, udom, ustd = UNITS[(g, s, unit)]
    domain = domain or udom
    if domain not in DOMAINS:
        raise SystemExit("%s 领域无法识别：%s" % (key, domain))
    if typ not in TYPES:
        raise SystemExit("%s type 非法：%s" % (key, typ))
    if len(qs) != 4:
        raise SystemExit("%s 需要恰好 4 题" % key)
    if any(t["key"] == key for t in TOPICS):
        raise SystemExit("知识点 key 重复：%s" % key)
    TOPICS.append({
        "key": key, "name": name, "domain": domain, "grade": g, "semester": s,
        "unit": unit, "type": typ, "description": desc,
        "mastery_criteria": list(CRIT[domain]), "std": std or ustd, "conf": "inferred", "note": NOTE,
        "items": [tuple(q) for q in qs],
    })


def materialise_questions(spec):
    diffs = ["basic", "basic", "standard", "challenge"]
    made = []
    for diff, item in zip(diffs, spec["items"]):
        prompt, answer, wrongs, expl = item
        if len(wrongs) != 3:
            raise SystemExit("%s 干扰项必须是 3 个：%s" % (spec["key"], prompt[:30]))
        made.append({"d": diff, "t": "choice", "p": str(prompt).strip(), "a": str(answer).strip(),
                     "w": [str(w).strip() for w in wrongs], "e": str(expl).strip()})
    return made


_BANNED_START = re.compile(r"^(同一|上题|该题|同上)")
_BANNED_META = re.compile(r"本知识点|课标|是否要求")
_BANNED_COPY = re.compile("\u514d\u8d39|AI\\s*\u521d\u7a3f")


def check_question(key, q):
    if _BANNED_START.match(q["p"]):
        raise SystemExit("%s 题干以禁用词开头：%s" % (key, q["p"][:20]))
    blob = "\n".join([q["p"], q["e"], q["a"]] + q["w"])
    if _BANNED_META.search(blob):
        raise SystemExit("%s 出现禁用元问题用语" % key)
    if _BANNED_COPY.search(blob):
        raise SystemExit("%s 出现不该出现的字样" % key)
    opts = [q["a"]] + q["w"]
    if len(set(re.sub(r"\s+", "", o) for o in opts)) != 4 or not all(opts):
        raise SystemExit("%s 选项重复或为空：%s" % (key, opts))
    if not q["e"]:
        raise SystemExit("%s 缺少解析" % key)
