# -*- coding: utf-8 -*-
"""初中地理数据的登记与题目生成。由 scripts/geo_build.py 调用。

目录依据（公开目录，dzskb / 教师之家，未逐页核对纸质课本）：
- 七上：2024 秋修订人教《地理》七年级上册。
- 七下：2024 审定人教《地理》七年级下册（2025 春使用）。
- 八上：2024 审定人教《地理》八年级上册（2025 秋使用）。
- 八下：2024 审定人教《地理》八年级下册（2026 春使用）。
六三制初中地理只开七、八年级，九年级没有地理课。
"""

import re

TOPICS = []
HARD = []

# (年级, 学期, 章号) -> (章名, 领域, 默认课标符号)
UNITS = {
    (7, "上", 1): ("地球", "地球与地图", "em_earth"),
    (7, "上", 2): ("地图", "地球与地图", "em_map"),
    (7, "上", 3): ("陆地和海洋", "地球与地图", "em_land"),
    (7, "上", 4): ("天气与气候", "世界地理", "wg_climate"),
    (7, "上", 5): ("居民与文化", "世界地理", "wg_people"),
    (7, "上", 6): ("发展与合作", "世界地理", "wg_dev"),
    (7, "下", 7): ("我们生活的大洲——亚洲", "世界地理", "wg_asia"),
    (7, "下", 8): ("我们邻近的地区和国家", "世界地理", "wg_near"),
    (7, "下", 9): ("东半球其他的地区和国家", "世界地理", "wg_east"),
    (7, "下", 10): ("西半球的国家", "世界地理", "wg_west"),
    (7, "下", 11): ("极地地区", "世界地理", "wg_polar"),
    (8, "上", 1): ("从世界看中国", "中国地理", "cg_land"),
    (8, "上", 2): ("中国的自然环境", "中国地理", "cg_nature"),
    (8, "上", 3): ("中国的自然资源", "中国地理", "cg_res"),
    (8, "上", 4): ("中国的经济发展", "中国地理", "cg_econ"),
    (8, "上", 5): ("建设美丽中国", "中国地理", "cg_beauty"),
    (8, "下", 6): ("中国的地理差异", "中国地理", "cg_diff"),
    (8, "下", 7): ("北方地区", "中国地理", "cg_north"),
    (8, "下", 8): ("南方地区", "中国地理", "cg_south"),
    (8, "下", 9): ("西北地区", "中国地理", "cg_nw"),
    (8, "下", 10): ("青藏地区", "中国地理", "cg_qing"),
    (8, "下", 11): ("奋进中的中国", "中国地理", "cg_world"),
}

DOMAINS = ("地球与地图", "世界地理", "中国地理")
CODE_OF = {
    "EM": "地球与地图", "WG": "世界地理", "CG": "中国地理",
}

# 课标条目是《义务教育地理课程标准（2022年版）》第四学段内容要求的公开转述，不是逐页核对的原文。
STANDARD_ROWS = [
    ("em_earth", "EM", "地球", "知道地球的宇宙环境、形状和大小，会用地球仪表示经纬网，并说明地球自转、公转的地理意义。"),
    ("em_map", "EM", "地图", "会读普通地图和地形图，选用合适的地图获取地理信息。"),
    ("em_land", "EM", "陆地和海洋", "运用地图和资料，说出七大洲、四大洋的分布，描述世界主要地形，并说明海陆变迁的基本原因。"),
    ("wg_climate", "WG", "天气与气候", "区分天气和气候，说出气温、降水的变化与分布，并归纳世界主要气候类型的分布。"),
    ("wg_people", "WG", "居民与文化", "运用地图和资料，说出世界人口、人种、聚落和文化的主要特点。"),
    ("wg_dev", "WG", "发展与合作", "知道发达国家与发展中国家的分布差异，以及国际合作的意义。"),
    ("wg_asia", "WG", "亚洲", "运用地图和资料，说出亚洲的位置、自然环境特点和人文地理概况。"),
    ("wg_near", "WG", "邻近的地区和国家", "认识日本、东南亚、印度和俄罗斯的位置、自然环境和经济发展特点。"),
    ("wg_east", "WG", "东半球其他地区和国家", "认识西亚、欧洲西部、撒哈拉以南非洲和澳大利亚的地理位置与区域特征。"),
    ("wg_west", "WG", "西半球的国家", "认识美国和巴西的位置、自然环境和经济发展特点。"),
    ("wg_polar", "WG", "极地地区", "运用地图和资料，说出极地地区的自然环境特点及其地理意义。"),
    ("cg_land", "CG", "疆域人口民族", "运用地图说出中国的疆域、邻国、行政区划，以及人口和民族的分布特点。"),
    ("cg_nature", "CG", "中国的自然环境", "运用地图和资料，说出中国地形、气候、河流与湖泊的主要特征。"),
    ("cg_res", "CG", "中国的自然资源", "知道土地、水、矿产和海洋等自然资源的基本特征，以及合理利用的重要性。"),
    ("cg_econ", "CG", "中国的经济发展", "运用资料说出中国农业、工业和交通运输的分布特点。"),
    ("cg_beauty", "CG", "建设美丽中国", "知道中国主要自然灾害与防灾减灾，以及环境保护和可持续发展的基本要求。"),
    ("cg_diff", "CG", "中国的地理差异", "运用地图说出中国四大地理区域的划分依据和总体差异。"),
    ("cg_north", "CG", "北方地区", "认识北方地区的自然特征与农业，以及东北三省、黄土高原和北京的区域特点。"),
    ("cg_south", "CG", "南方地区", "认识南方地区的自然特征与农业，以及长江三角洲、香港澳门和台湾的区域特点。"),
    ("cg_nw", "CG", "西北地区", "认识西北地区的自然特征与农业，以及塔里木盆地的区域特点。"),
    ("cg_qing", "CG", "青藏地区", "认识青藏地区的自然特征与农业，以及三江源地区的生态意义。"),
    ("cg_world", "CG", "奋进中的中国", "知道中国发展成就、面临的挑战，以及在世界上的责任与作用。"),
]

TYPES = ("conceptual", "procedural", "reasoning", "application", "modeling")
CRIT = {
    "地球与地图": ["能说出本课的基本概念、数据和空间位置", "能在地图或示意图上作出与教材相符的判断"],
    "世界地理": ["能说出本课的位置、自然或人文特征", "能把区域特征对应到教材中的典型事实"],
    "中国地理": ["能说出本课的位置、分布或基本国情", "能把自然或人文特征对应到教材中的典型事实"],
}
NOTE = "人教版该课的常见教学内容。条目是公开转述，不是逐页核对的原文。"

_BANNED_START = re.compile(r"^(同一|上题|该题|同上)")
_BANNED_META = re.compile(r"本知识点|课标|是否要求|你认为|是否应该|谁之过|是否必要")
_BANNED_COPY = re.compile("免费|AI\\s*初稿")
_CUR = {}


def chapter(grade, sem, unit):
    cn = "零一二三四五六七八九"[grade]
    title = UNITS[(grade, sem, unit)][0]
    return "%s年级%s册 第%d单元 %s" % (cn, sem, unit, title)


def hard(topic, prereq, reason):
    HARD.append((topic, prereq, reason))


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


def load_block(text):
    """解析 V/L/Q 行。字段用 | 分开，题目文字里不要写 |。"""
    cur = None
    qs = []

    def flush():
        if cur is None:
            return
        key, name, unit, typ, desc = cur
        K(key, name, int(unit), typ, desc, qs)

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        tag = parts[0]
        if tag == "V":
            flush()
            cur, qs = None, []
            if len(parts) != 3:
                raise SystemExit("V 行格式应为 V|年级|学期：%s" % line)
            vol(int(parts[1]), parts[2])
        elif tag == "L":
            flush()
            if len(parts) != 6:
                raise SystemExit("L 行字段数不对：%s" % line)
            cur = parts[1:]
            qs = []
        elif tag == "Q":
            if cur is None:
                raise SystemExit("Q 出现在 L 之前：%s" % line)
            if len(parts) != 7:
                raise SystemExit("Q 行字段数不对：%s" % line)
            _tag, prompt, answer, w1, w2, w3, expl = parts
            qs.append((prompt, answer, [w1, w2, w3], expl))
        else:
            raise SystemExit("无法识别的行：%s" % line[:40])
    flush()


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


def check_question(key, q):
    if _BANNED_START.match(q["p"]):
        raise SystemExit("%s 题干以禁用词开头：%s" % (key, q["p"][:20]))
    blob = "\n".join([q["p"], q["e"], q["a"]] + q["w"])
    if _BANNED_META.search(blob):
        raise SystemExit("%s 出现禁用元问题用语：%s" % (key, q["p"][:24]))
    if _BANNED_COPY.search(blob):
        raise SystemExit("%s 出现不该出现的字样" % key)
    opts = [q["a"]] + q["w"]
    if len(set(re.sub(r"\s+", "", o) for o in opts)) != 4 or not all(opts):
        raise SystemExit("%s 选项重复或为空：%s" % (key, opts))
    if not q["e"]:
        raise SystemExit("%s 缺少解析" % key)
