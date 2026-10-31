#!/usr/bin/env python3
"""给初中历史（topicId 以 cnh_j 开头）里最需要看路线、时间或制度的题写入内联 SVG。

只改下面登记的题。可重复运行：
  python3 scripts/his_figs.py
  python3 scripts/his_figs.py --preview /tmp/his-figs.html

图只用 currentColor，不引用外网。正确选项的整句不写入图中。
图里的阿拉伯数字必须能在该题题干或选项里找到。
终点若正是题目在问的地名，图上标「?」，不把地名写出来。
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fig_draw import circ, edge, esc, face, hidden, line, n, poly, svg, text, thin  # noqa: E402
from check_figures import figure_problems  # noqa: E402

ROOT = os.path.dirname(HERE)
QUESTIONS = os.path.join(ROOT, "data", "questions.json")

# 示意国界（经纬度），只求相对位置能认，不作为实测地图。
# 轮廓故意画满，避免河西走廊在小图上断成两块。
_BORDER_LL = [
    (75, 40), (82, 45), (92, 47), (102, 48), (112, 48), (118, 50),
    (126, 52), (134, 48), (130, 43), (124, 40), (121, 37), (119, 34),
    (122, 31), (120, 27), (116, 23.5), (110, 21.5), (104, 22), (97, 25),
    (90, 28), (82, 32), (76, 36),
]


def _xy(lon, lat, ox, oy, s):
    x = ox + (lon - 73) / 62 * s
    y = oy + (54 - lat) / 36 * s * 0.92
    return (x, y)


def _china(ox, oy, s):
    return [_xy(lon, lat, ox, oy, s) for lon, lat in _BORDER_LL]


def _at(lon, lat, ox, oy, s):
    return _xy(lon, lat, ox, oy, s)


def rect(x, y, w, h, attrs, rx=0):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s/>' % (
        n(x), n(y), n(w), n(h), n(rx), attrs)


def ell(cx, cy, rx, ry, attrs):
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (
        n(cx), n(cy), n(rx), n(ry), attrs)


def path(d, attrs):
    return '<path d="%s" %s/>' % (d, attrs)


def arrow(a, b, sw=2.2):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    length = 10
    tip = b
    p1 = (b[0] - length * math.cos(ang - 0.42), b[1] - length * math.sin(ang - 0.42))
    p2 = (b[0] - length * math.cos(ang + 0.42), b[1] - length * math.sin(ang + 0.42))
    end = (b[0] - 1.5 * math.cos(ang), b[1] - 1.5 * math.sin(ang))
    return line(a, end, thin(sw)) + poly([tip, p1, p2], face(1))


def route(pts, sw=2.3):
    body = ""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        body += arrow(a, b, sw) if i == len(pts) - 2 else line(a, b, thin(sw))
    return body


def blob(pts, op=0.08, sw=1.7):
    return poly(pts, face(op)) + poly(pts, edge(sw))


def box(x, y, w, h, lines, op=0.07, size=15, sw=1.8):
    if isinstance(lines, str):
        lines = [lines]
    body = rect(x, y, w, h, face(op), 8) + rect(x, y, w, h, edge(sw), 8)
    gap = size + 5
    block = gap * len(lines)
    y0 = y + (h - block) / 2 + size - 1
    for i, line_s in enumerate(lines):
        body += text(x + w / 2, y0 + i * gap, line_s, size)
    return body


def pin(x, y, label, dx=0, dy=-12, size=14, anchor="middle", r=4.2):
    return circ(x, y, r, face(1)) + text(x + dx, y + dy, label, size, anchor)


def ask(x, y, r=12):
    return circ(x, y, r, edge(2.1)) + text(x, y + 5, "?", 16)


def north(x, y):
    return arrow((x, y + 16), (x, y), 1.6) + text(x, y + 30, "北", 12)


def frame(w, h, body, title, note=""):
    if title:
        body += text(w / 2, 20, title, 15)
    if note:
        body += text(w / 2, h - 12, note, 13)
    return svg(w, h, body)


def land_china(ox, oy, s, op=0.08):
    return blob(_china(ox, oy, s), op)


def _tw(s, size):
    width = 0.0
    for ch in s:
        width += size if ord(ch) > 127 else size * 0.56
    return width


def overflow_problems(drawing):
    """文字不要画出 viewBox。"""
    m = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', drawing)
    if not m:
        return ["缺少 viewBox"]
    w, h = float(m.group(1)), float(m.group(2))
    bad = []
    for t in re.finditer(
        r'<text x="([^"]+)" y="([^"]+)"[^>]*font-size="([^"]+)" text-anchor="([^"]+)">([^<]*)</text>',
        drawing,
    ):
        x, y = float(t.group(1)), float(t.group(2))
        size = float(t.group(3))
        anchor, s = t.group(4), t.group(5)
        tw = _tw(s, size)
        if anchor == "start":
            left, right = x, x + tw
        elif anchor == "end":
            left, right = x - tw, x
        else:
            left, right = x - tw / 2, x + tw / 2
        if left < 1 or right > w - 1 or y - size < 0 or y > h - 1:
            bad.append("文字越界「%s」" % s)
    return bad


# ---------------------------------------------------------------- 地图与路线

def silk_road():
    """东在右、西在左。路线从长安向西画到留空的终点。"""
    w, h = 440, 176
    y = 92
    stops = [(400, "长安"), (320, "河西走廊"), (230, "西域"), (150, "中亚")]
    body = rect(24, 68, 392, 48, face(0.06), 16)
    body += route([(x, y) for x, _ in stops] + [(58, y)])
    for x, lab in stops:
        body += pin(x, y, lab, dy=-16, size=14)
    body += ask(58, y)
    body += text(58, 128, "西", 13)
    body += text(400, 128, "东", 13)
    return frame(w, h, body, "丝绸之路（陆路向西）", "示意图，不按比例")


def grand_canal():
    """北端、南端写在题外的常识位置上，中心城市留空。"""
    w, h = 420, 268
    ox, oy, s = 86, 40, 230
    body = land_china(ox, oy, s)
    body += north(w - 28, 44)
    a = _at(116.2, 39.7, ox, oy, s)
    b = _at(112.5, 34.7, ox, oy, s)  # 中心位置，不写地名
    c = _at(120.1, 30.3, ox, oy, s)
    body += route([a, b, c], 2.4)
    body += pin(a[0], a[1], "涿郡", dx=-26, dy=-8, anchor="end", size=14)
    body += pin(c[0], c[1], "余杭", dx=14, dy=-8, anchor="start", size=14)
    body += ask(b[0], b[1])
    body += text(b[0] + 18, b[1] - 8, "中心", 13, "start")
    return frame(w, h, body, "隋朝大运河", "北端涿郡，南端余杭")


def three_kingdoms():
    w, h = 420, 268
    ox, oy, s = 86, 40, 230
    body = land_china(ox, oy, s)
    body += north(w - 26, 44)
    marks = [
        ((108, 38), "魏", "北"),
        ((104, 30), "蜀", "西南"),
        ((118, 29), "吴", "东南"),
    ]
    for (lon, lat), name, where in marks:
        x, y = _at(lon, lat, ox, oy, s)
        body += circ(x, y, 16, face(0.16)) + circ(x, y, 16, edge(1.6))
        body += text(x, y + 5, name, 15)
        body += text(x, y + 28, where, 12)
    return frame(w, h, body, "三国大致范围", "只标位置，不标建立年份")


def xuanzang():
    w, h = 420, 168
    y = 86
    xs = [70, 180, 290, 380]
    body = rect(28, 64, 364, 44, face(0.06), 14)
    body += route([(x, y) for x in xs])
    for x, lab in zip(xs, ["长安", "河西走廊", "西域"]):
        body += pin(x, y, lab, dy=-16)
    body += ask(xs[-1], y)
    return frame(w, h, body, "玄奘西行", "箭头继续向西")


def jianzhen():
    w, h = 420, 168
    y = 88
    body = rect(36, 58, 200, 70, face(0.07), 10)
    body += text(110, 78, "大陆", 13)
    body += rect(250, 58, 140, 70, face(0.05), 10)
    body += text(320, 78, "海", 13)
    body += pin(120, y + 16, "扬州", dy=22)
    body += route([(120, y + 16), (230, y), (340, y)])
    body += ask(360, y)
    return frame(w, h, body, "鉴真东渡", "自扬州经海路向东")


def zhenghe():
    w, h = 440, 176
    y = 90
    xs = [56, 160, 270, 380]
    labels = ["刘家港", "南海", "印度洋"]
    body = rect(24, 66, 392, 48, face(0.05), 16)
    body += route([(x, y) for x in xs])
    for x, lab in zip(xs, labels):
        body += pin(x, y, lab, dy=-16)
    body += ask(xs[-1], y)
    return frame(w, h, body, "郑和远航", "沿海岸向外，最远处留空")


def long_march():
    w, h = 420, 268
    ox, oy, s = 80, 40, 220
    body = land_china(ox, oy, s)
    body += north(w - 26, 44)
    stops = [("江西", 116.0, 26.0), ("遵义", 106.9, 27.7), ("雪山草地", 100.5, 31.0), ("陕北", 109.5, 36.8)]
    pts = [_at(lon, lat, ox, oy, s) for _, lon, lat in stops]
    body += route(pts, 2.3)
    offsets = [(12, -12, "start"), (-8, 18, "end"), (-8, -14, "end"), (10, -14, "start")]
    for (name, _lon, _lat), (x, y), (dx, dy, anchor) in zip(stops, pts, offsets):
        body += pin(x, y, name, dx=dx, dy=dy, anchor=anchor, size=13)
    body += text(_at(106.9, 27.7, ox, oy, s)[0], _at(106.9, 27.7, ox, oy, s)[1] - 16, "1935", 12)
    return frame(w, h, body, "长征路线从简", "突出遵义一段")


def northern_expedition():
    w, h = 420, 268
    ox, oy, s = 80, 40, 220
    body = land_china(ox, oy, s)
    body += north(w - 26, 44)
    start = _at(113.3, 23.4, ox, oy, s)
    targets = [_at(114.3, 30.6, ox, oy, s), _at(118.8, 32.0, ox, oy, s), _at(117.0, 36.5, ox, oy, s)]
    for p in targets:
        body += arrow(start, p, 2.0)
    body += pin(start[0], start[1], "广东", dy=-12, size=14)
    body += text(targets[0][0] - 8, targets[0][1] - 8, "长江中游", 13, "end")
    body += text(targets[1][0] + 8, targets[1][1] - 8, "东南", 13, "start")
    body += text(targets[2][0] + 6, targets[2][1] - 10, "更北", 13, "start")
    return frame(w, h, body, "1926年北伐进军", "三路北上，不标对象姓名")


def three_campaigns():
    w, h = 420, 268
    ox, oy, s = 70, 44, 230
    body = land_china(ox, oy, s)
    body += north(w - 26, 44)
    zones = [("东北", 126.5, 45.5, 22), ("华北", 116.4, 39.5, 18), ("淮河一带", 117.2, 33.6, 20)]
    for name, lon, lat, rad in zones:
        x, y = _at(lon, lat, ox, oy, s)
        body += circ(x, y, rad, face(0.18)) + circ(x, y, rad, edge(1.6))
        body += text(x, y + 4, name, 13)
    return frame(w, h, body, "1948–1949 三场决战的区域", "只标地区，不标战役名称")


def dujiangyan():
    w, h = 420, 210
    body = path("M150 36 L140 78 L50 176", edge(2.3))
    body += path("M230 36 L240 78 L240 118 L300 118", edge(2.3))
    body += path("M190 78 L130 168", edge(2.2))
    body += poly([(172, 70), (208, 70), (190, 96)], face(0.22))
    body += poly([(172, 70), (208, 70), (190, 96)], edge(1.6))
    body += text(190, 62, "鱼嘴", 14)
    body += text(96, 140, "外江", 16)
    body += text(214, 104, "内江", 16)
    body += line((168, 118), (198, 132), hidden(2))
    body += text(150, 112, "飞沙堰", 13, "end")
    body += rect(300, 106, 24, 28, edge(2.2), 2)
    body += text(336, 100, "宝瓶口", 14, "start")
    body += rect(336, 96, 64, 58, face(0.08), 6)
    body += rect(336, 96, 64, 58, edge(1.5), 6)
    body += text(368, 130, "灌区", 15)
    return frame(w, h, body, "都江堰分水", "鱼嘴分流，宝瓶口进水")


def maguan():
    w, h = 420, 268
    ox, oy, s = 56, 40, 230
    body = land_china(ox, oy, s)
    body += north(w - 26, 44)
    x, y = _at(122.2, 39.6, ox, oy, s)
    body += ell(x, y, 16, 12, face(0.28)) + ell(x, y, 16, 12, edge(1.6))
    body += text(x - 18, y - 4, "辽东半岛", 13, "end")
    tx, ty = _at(121.0, 23.7, ox, oy, s)
    body += ell(tx + 26, ty, 8, 16, face(0.28)) + ell(tx + 26, ty, 8, 16, edge(1.6))
    body += text(tx + 40, ty - 10, "台湾岛", 13, "start")
    px, py = _at(119.6, 23.6, ox, oy, s)
    body += circ(px + 10, py + 6, 3.2, face(1))
    body += text(px - 4, py + 8, "澎湖", 13, "end")
    return frame(w, h, body, "1895年条约涉及的地区", "示意图")


def treaty_ports():
    w, h = 420, 200
    body = path("M36 150 C 90 140, 130 120, 180 112 C 230 100, 280 78, 340 62 C 370 54, 390 48, 400 44", edge(2.4))
    body += text(70, 40, "陆地", 13, "start")
    body += text(300, 150, "海", 14)
    dots = [(70, 146), (150, 118), (210, 108), (300, 74), (348, 60)]
    for x, y in dots:
        body += circ(x, y, 5, face(1))
    body += text(78, 172, "珠江口一带", 13, "start")
    body += text(168, 96, "福建沿海", 13, "start")
    body += text(250, 52, "长江口一带", 13, "start")
    return frame(w, h, body, "五个通商口岸所在的海岸", "东南沿海，不标城市名")


def song_sea():
    w, h = 420, 260
    ox, oy, s = 24, 40, 210
    body = land_china(ox, oy, s, 0.07)
    gz = _at(113.3, 23.1, ox, oy, s)
    qz = _at(118.6, 24.9, ox, oy, s)
    body += arrow(gz, (gz[0] + 22, gz[1] + 16), 2.0)
    body += arrow(qz, (qz[0] + 30, qz[1] + 14), 2.0)
    body += pin(gz[0], gz[1], "广州", dx=-14, dy=16, anchor="end", size=13)
    body += pin(qz[0], qz[1], "泉州", dx=8, dy=-14, anchor="start", size=13)
    body += text(qz[0] + 40, qz[1] + 22, "南海", 14, "start")
    return frame(w, h, body, "宋元港口向外的航线", "广州、泉州是主要海港")


def arab_empire():
    w, h = 440, 200
    body = ell(90, 110, 36, 22, face(0.08)) + ell(90, 110, 36, 22, edge(1.5))
    body += ell(168, 118, 34, 48, face(0.08)) + ell(168, 118, 34, 48, edge(1.5))
    body += ell(300, 100, 90, 46, face(0.08)) + ell(300, 100, 90, 46, edge(1.5))
    body += path("M70 108 C 120 90, 200 80, 360 96 C 300 130, 180 150, 70 120 Z", face(0.16))
    body += text(78, 78, "地中海北岸一角", 12)
    body += text(168, 176, "北非", 14)
    body += text(250, 108, "阿拉伯半岛", 14)
    body += text(372, 78, "印度河", 14)
    return frame(w, h, body, "8世纪中期的控制范围", "色块表示连成一片的地区")


def _world(labels, west=True):
    """labels: (欧, 非, 亚, 西边大陆)。west=False 时不画最西边那块陆地。"""
    body = rect(16, 40, 408, 120, face(0.04), 8)
    body += ell(250, 78, 28, 20, face(0.1)) + ell(250, 78, 28, 20, edge(1.5))
    body += ell(268, 128, 24, 36, face(0.1)) + ell(268, 128, 24, 36, edge(1.5))
    body += ell(360, 100, 48, 36, face(0.1)) + ell(360, 100, 48, 36, edge(1.5))
    if west:
        body += ell(78, 100, 22, 46, face(0.1)) + ell(78, 100, 22, 46, edge(1.5))
    eu, af, asia, west_lab = labels
    if eu:
        body += text(250, 74, eu, 13)
    if af:
        body += text(268, 132, af, 13)
    if asia:
        body += text(372, 96, asia, 13)
    if west and west_lab:
        body += text(78, 96, west_lab, 12)
    return body


def dias():
    w, h = 440, 200
    body = _world(("欧洲", "非洲", "亚洲", ""), west=False)
    body += route([(236, 70), (228, 110), (240, 158)])
    body += ask(252, 172)
    body += text(36, 58, "1487年", 13, "start")
    return frame(w, h, body, "沿非洲西岸向南", "南端留空")


def columbus():
    w, h = 440, 200
    body = _world(("欧洲", "非洲", "亚洲", ""))
    body += route([(222, 78), (150, 92), (108, 100)])
    body += ask(78, 100)
    body += text(168, 56, "1492年 向西横渡", 14)
    return frame(w, h, body, "横渡大洋", "对岸陆地不写名称")


def gama():
    w, h = 440, 200
    body = _world(("欧洲", "非洲", "亚洲", ""), west=False)
    body += route([(236, 70), (238, 156), (290, 162), (312, 140)])
    body += ask(330, 128)
    body += text(36, 58, "1497–1498年", 13, "start")
    return frame(w, h, body, "绕过非洲南端再向东", "终点留空")


def magellan():
    w, h = 440, 200
    body = _world(("欧洲", "非洲", "亚洲", ""))
    body += path("M262 62 C 160 36, 36 48, 36 110 C 36 176, 220 184, 390 140 C 410 120, 300 58, 270 66", thin(2.2))
    body += arrow((278, 60), (258, 70), 2.2)
    body += text(36, 168, "1519–1522年", 13, "start")
    return frame(w, h, body, "船队绕地球一圈后回到出发地", "不标领队姓名")


def triangle_trade():
    w, h = 420, 210
    # 方框先画，箭头停在框外，方向是欧洲→非洲→美洲→欧洲。
    boxes = [(174, 40, "欧洲"), (40, 132, "非洲"), (292, 132, "美洲")]
    body = ""
    for x, y, lab in boxes:
        body += box(x, y, 84, 36, lab, size=15)
    body += arrow((210, 76), (100, 132), 2.1)
    body += arrow((124, 150), (292, 150), 2.1)
    body += arrow((334, 132), (250, 76), 2.1)
    body += ask(208, 138)
    return frame(w, h, body, "三角贸易的方向", "非洲到美洲这一段留空")


def poland_1939():
    w, h = 420, 180
    body = rect(40, 48, 150, 80, face(0.08), 6) + rect(40, 48, 150, 80, edge(1.8), 6)
    body += rect(190, 48, 150, 80, face(0.08), 6) + rect(190, 48, 150, 80, edge(1.8), 6)
    body += text(115, 94, "德国", 18)
    body += text(265, 94, "波兰", 18)
    body += arrow((155, 88), (185, 88), 2.4)
    return frame(w, h, body, "1939年9月1日", "箭头表示突袭方向")


def north_loss():
    w, h = 420, 268
    ox, oy, s = 48, 52, 230
    body = land_china(ox, oy, s)
    body += north(28, 48)
    x, y = _at(127, 51, ox, oy, s)
    body += ell(x, y, 34, 14, face(0.22)) + ell(x, y, 34, 14, hidden(1.5))
    body += text(x - 42, y - 2, "黑龙江以北", 13, "end")
    body += ell(x + 42, y + 26, 12, 22, face(0.22)) + ell(x + 42, y + 26, 12, 22, hidden(1.5))
    body += text(x + 58, y + 30, "乌苏里江以东", 12, "start")
    return frame(w, h, body, "北方被占的土地", "虚线范围在当时边界之外")


# ---------------------------------------------------------------- 制度与结构

def qin_counties():
    w, h = 400, 230
    body = box(150, 36, 100, 34, "皇帝")
    body += box(40, 96, 80, 32, "郡")
    body += box(160, 96, 80, 32, "郡")
    body += box(280, 96, 80, 32, "郡")
    body += box(46, 150, 68, 30, "县", size=14)
    body += box(166, 150, 68, 30, "县", size=14)
    body += box(286, 150, 68, 30, "县", size=14)
    body += line((200, 70), (80, 96), thin(1.6))
    body += line((200, 70), (200, 96), thin(1.6))
    body += line((200, 70), (320, 96), thin(1.6))
    body += line((80, 128), (80, 150), thin(1.6))
    body += line((200, 128), (200, 150), thin(1.6))
    body += line((320, 128), (320, 150), thin(1.6))
    return frame(w, h, body, "秦朝地方由中央任免官员", "职位不能世袭")


def tui_en():
    w, h = 440, 180
    body = box(24, 70, 120, 64, ["一个诸侯国"], size=15)
    body += arrow((150, 102), (210, 102), 2.2)
    for i in range(6):
        x = 220 + (i % 3) * 68
        y = 48 + (i // 3) * 58
        body += box(x, y, 60, 44, "小封地", size=13)
    return frame(w, h, body, "诸侯王的封地", "越分越小")


def yuan_province():
    w, h = 420, 200
    body = box(150, 36, 120, 36, "中央")
    body += box(30, 96, 110, 40, "行中书省", size=14)
    body += box(155, 96, 110, 40, "行中书省", size=14)
    body += box(280, 96, 110, 40, "行中书省", size=14)
    body += box(90, 152, 240, 32, "路、府、州、县", size=14)
    body += line((210, 72), (85, 96), thin(1.6))
    body += line((210, 72), (210, 96), thin(1.6))
    body += line((210, 72), (335, 96), thin(1.6))
    body += line((85, 136), (160, 152), thin(1.6))
    body += line((210, 136), (210, 152), thin(1.6))
    body += line((335, 136), (260, 152), thin(1.6))
    return frame(w, h, body, "元朝地方层级", "")


def ming_boards():
    w, h = 440, 220
    body = text(100, 40, "以前", 14)
    body += text(320, 40, "以后", 14)
    body += box(40, 50, 120, 32, "皇帝", size=14)
    body += box(40, 96, 120, 32, "丞相", size=14)
    body += box(40, 142, 120, 32, "六部", size=14)
    body += arrow((100, 82), (100, 96), 1.8)
    body += arrow((100, 128), (100, 142), 1.8)
    body += box(250, 50, 130, 32, "皇帝", size=14)
    body += box(250, 142, 130, 32, "六部", size=14)
    body += arrow((315, 82), (315, 142), 1.8)
    body += rect(248, 96, 134, 32, edge(1.5), 6)
    body += line((256, 102), (374, 122), thin(1.6))
    body += line((256, 122), (374, 102), thin(1.6))
    body += text(315, 116, "丞相", 14)
    return frame(w, h, body, "明太祖调整中央机构", "右图由皇帝直接面对六部")


def junjichu():
    w, h = 360, 210
    body = box(110, 32, 140, 36, "皇帝")
    body += box(110, 92, 140, 40, ["军机处", "只负责传令"], size=14)
    body += box(80, 156, 200, 34, "各部去执行", size=14)
    body += arrow((180, 68), (180, 92), 2)
    body += arrow((180, 132), (180, 156), 2)
    return frame(w, h, body, "军机处在决策链上的位置", "不能自行决定军国大事")


def sanmin():
    w, h = 440, 168
    body = box(16, 44, 130, 96, ["民族", "驱除鞑虏", "恢复中华"], size=14)
    body += box(156, 44, 128, 96, ["民权", "?"], size=16)
    body += box(294, 44, 130, 96, ["民生", "平均地权"], size=15)
    return frame(w, h, body, "三民主义的三栏", "民权一栏留空")


def encircle():
    w, h = 400, 210
    body = ""
    spots = [(36, 40, 155, 90), (264, 40, 245, 90), (36, 150, 155, 122), (264, 150, 245, 122)]
    for x, y, tx, ty in spots:
        body += box(x, y, 100, 32, "根据地", size=14)
        body += arrow((x + 50, y + 16), (tx, ty), 1.7)
    body += box(155, 86, 90, 36, "大城市")
    return frame(w, h, body, "先在乡村建立根据地", "箭头指向大城市")


def basic_line():
    w, h = 440, 190
    body = box(145, 40, 150, 52, ["?", "中心"], size=16)
    body += box(24, 124, 180, 40, "四项基本原则", size=15)
    body += box(230, 124, 180, 40, "改革开放", size=15)
    body += line((180, 92), (114, 124), thin(1.6))
    body += line((260, 92), (320, 124), thin(1.6))
    return frame(w, h, body, "基本路线", "中心写什么，图上留空")


def caste():
    w, h = 360, 230
    labels = ["最上：祭祀", "军事与行政", "农、牧、商", "劳役"]
    body = ""
    for i, lab in enumerate(labels):
        bw = 120 + i * 52
        x = (w - bw) / 2
        y = 40 + i * 42
        body += rect(x, y, bw, 36, face(0.06 + i * 0.03), 4)
        body += rect(x, y, bw, 36, edge(1.7), 4)
        body += text(w / 2, y + 24, lab, 15)
    return frame(w, h, body, "四个等级从上到下", "栏内是职事，不是等级名称")


def verdun():
    w, h = 440, 170
    body = rect(30, 58, 380, 70, face(0.06), 4)
    body += rect(30, 58, 380, 70, edge(1.8), 4)
    body += line((156, 58), (156, 128), edge(1.6))
    body += line((282, 58), (282, 128), edge(1.6))
    body += text(93, 98, "西部", 16)
    body += text(219, 98, "中部", 16)
    body += text(345, 98, "东部", 16)
    return frame(w, h, body, "843年分成三部分", "原来是同一帝国")


def feudal():
    w, h = 380, 220
    body = box(130, 36, 120, 34, "国王")
    body += box(130, 92, 120, 34, "领主")
    body += box(130, 148, 120, 34, "骑士")
    body += arrow((108, 48), (108, 168), 1.8)
    body += text(78, 112, "赐地", 14)
    body += arrow((272, 168), (272, 48), 1.8)
    body += text(302, 112, "效忠", 14)
    return frame(w, h, body, "土地与效忠", "上对下赐地，下对上效忠")


def constitutional():
    w, h = 440, 160
    body = box(30, 58, 160, 64, ["议会", "制定法律"], size=15)
    body += box(250, 58, 160, 64, ["国王", "依照法律行事"], size=15)
    body += arrow((190, 90), (250, 90), 2.2)
    return frame(w, h, body, "法律把国王限制住", "")


def us_branches():
    w, h = 440, 180
    body = box(16, 44, 120, 64, ["国会", "立法"], size=15)
    body += box(160, 44, 120, 64, ["总统", "行政"], size=15)
    body += box(304, 44, 120, 64, ["法院", "司法"], size=15)
    body += box(70, 124, 300, 34, "各州还管自己的一部分事务", size=14)
    return frame(w, h, body, "1787年宪法里的三组权力", "")


def haihan():
    w, h = 440, 200
    body = text(100, 36, "以前", 14)
    body += text(320, 36, "以后", 14)
    body += box(40, 46, 130, 32, "中央", size=14)
    for i in range(3):
        body += box(24 + i * 48, 110, 44, 32, "藩", size=14)
    body += box(250, 46, 140, 32, "中央", size=14)
    for i in range(3):
        body += box(236 + i * 52, 110, 48, 32, "县", size=14)
        body += line((320, 78), (260 + i * 52, 110), thin(1.5))
    return frame(w, h, body, "明治维新以后的地方", "许多藩改成由中央管辖的县")


def blocs():
    w, h = 440, 180
    body = rect(20, 44, 190, 110, face(0.06), 8) + rect(20, 44, 190, 110, edge(1.7), 8)
    body += rect(230, 44, 190, 110, face(0.06), 8) + rect(230, 44, 190, 110, edge(1.7), 8)
    body += text(115, 78, "德国", 16)
    body += text(115, 102, "奥匈帝国", 15)
    body += text(115, 126, "意大利", 15)
    body += text(325, 78, "英国", 16)
    body += text(325, 102, "法国", 16)
    body += text(325, 126, "俄国", 16)
    return frame(w, h, body, "第一次世界大战前的两组国家", "不标集团名称")


def security_council():
    w, h = 420, 190
    body = box(40, 70, 200, 70, ["五个常任理事国", "各有一票否决权"], size=15)
    body += ask(320, 104, 16)
    body += text(320, 146, "这个机构叫什么", 13)
    body += arrow((240, 104), (300, 104), 2)
    return frame(w, h, body, "谁能否决", "机构名称留空")


def muye_timeline():
    w, h = 440, 150
    y = 78
    body = line((40, y), (400, y), edge(2.2))
    xs = [70, 200, 360]
    names = ["夏", "商", "西周"]
    for x, name in zip(xs, names):
        body += circ(x, y, 5, face(1))
        body += text(x, y - 16, name, 16)
    body += line((270, y - 22), (270, y + 18), hidden(1.4))
    body += text(270, y + 36, "牧野之战", 14)
    return frame(w, h, body, "夏、商、西周", "战役标在商和西周之间")


def nixon_timeline():
    w, h = 440, 150
    y = 78
    body = line((50, y), (390, y), edge(2.2))
    body += circ(120, y, 5, face(1))
    body += circ(320, y, 5, face(1))
    body += text(120, y - 18, "1972年", 15)
    body += text(120, y + 28, "尼克松访华", 14)
    body += text(320, y - 18, "1979年", 15)
    body += text(320, y + 28, "中美建交", 14)
    return frame(w, h, body, "中美关系上的两件事", "年份取自题干")


# ---------------------------------------------------------------- 登记

def catalog():
    """(题号, svg, 题干里必须有的片段, 额外允许的数字, 图里必须有的文字)。"""
    rows = []

    def add(qid, drawing, expect, extra=(), must=()):
        rows.append((qid, drawing, expect, set(extra), tuple(must)))

    add("cnh_j014_q2", silk_road(), "丝绸之路从长安出发", must=("长安", "西域", "?"))
    add("cnh_j022_q3", grand_canal(), "隋朝大运河以哪里为中心", must=("涿郡", "余杭", "?"))
    add("cnh_j016_q3", three_kingdoms(), "三国的建立顺序", must=("魏", "蜀", "吴"))
    add("cnh_j027_q1", xuanzang(), "玄奘西行的目的地", must=("长安", "?"))
    add("cnh_j027_q2", jianzhen(), "鉴真东渡传播佛法", must=("扬州", "?"))
    add("cnh_j037_q2", zhenghe(), "郑和船队最远到达", must=("刘家港", "印度洋", "?"))
    add("cnh_j058_q2", long_march(), "遵义会议着重解决了", must=("遵义", "1935"))
    add("cnh_j056_q3", northern_expedition(), "1926年北伐的主要对象", must=("广东", "1926"))
    add("cnh_j064_q2", three_campaigns(), "三大战役是", must=("东北", "华北", "淮河一带"))
    add("cnh_j006_q4", dujiangyan(), "都江堰位于", must=("鱼嘴", "宝瓶口", "飞沙堰"))
    add("cnh_j048_q3", maguan(), "《马关条约》割让", must=("辽东半岛", "台湾岛", "澎湖"))
    add("cnh_j044_q4", treaty_ports(), "《南京条约》开放的通商口岸", must=("珠江口", "长江口"))
    add("cnh_j034_q4", song_sea(), "宋元时期对外交通", must=("广州", "泉州"))
    add("cnh_j100_q3", arab_empire(), "阿拉伯帝国的版图地跨", must=("阿拉伯半岛", "印度河"))
    add("cnh_j103_q1", dias(), "迪亚士到达", must=("1487", "非洲", "?"))
    add("cnh_j103_q2", columbus(), "哥伦布横渡大西洋", must=("1492", "?"))
    add("cnh_j103_q3", gama(), "达·伽马开辟了通往哪里", must=("1497", "1498", "?"))
    add("cnh_j103_q4", magellan(), "完成环球航行的是", must=("1519", "1522"))
    add("cnh_j104_q2", triangle_trade(), "从非洲运往美洲的主要是", must=("欧洲", "非洲", "美洲", "?"))
    add("cnh_j126_q1", poland_1939(), "德国突袭波兰", must=("德国", "波兰", "1939"))
    add("cnh_j045_q4", north_loss(), "侵占中国北方大片领土", must=("黑龙江以北", "乌苏里江以东"))
    add("cnh_j009_q4", qin_counties(), "秦朝为加强中央对地方的控制", must=("皇帝", "郡", "县"))
    add("cnh_j012_q1", tui_en(), "汉武帝接受主父偃的建议", must=("诸侯国", "小封地"))
    add("cnh_j032_q4", yuan_province(), "元朝在地方实行的制度", must=("行中书省", "路、府、州、县"))
    add("cnh_j036_q2", ming_boards(), "明太祖加强君权的一项措施", must=("丞相", "六部"))
    add("cnh_j040_q2", junjichu(), "军机处的主要职责", must=("军机处", "皇帝"))
    add("cnh_j051_q4", sanmin(), "三民主义中的民权主义", must=("民族", "民权", "民生", "?"))
    add("cnh_j057_q4", encircle(), "井冈山道路的主要内容", must=("根据地", "大城市"))
    add("cnh_j076_q3", basic_line(), "一个中心是指", must=("四项基本原则", "改革开放", "?"))
    add("cnh_j093_q1", caste(), "古代印度种姓制度中居于首位", must=("祭祀", "劳役"))
    add("cnh_j096_q3", verdun(), "分成三部分的条约", must=("843", "西部", "中部", "东部"))
    add("cnh_j096_q4", feudal(), "西欧封建等级制度的核心", must=("赐地", "效忠"))
    add("cnh_j105_q4", constitutional(), "英国资产阶级革命后逐渐形成的政体", must=("议会", "国王"))
    add("cnh_j106_q4", us_branches(), "1787年美国宪法规定的政体", must=("国会", "总统", "法院"))
    add("cnh_j115_q2", haihan(), "明治维新在政治上的措施", must=("藩", "县", "中央"))
    add("cnh_j119_q2", blocs(), "德国所属的集团是", must=("德国", "奥匈帝国", "英国"))
    add("cnh_j131_q2", security_council(), "拥有否决权的机构是", must=("常任理事国", "否决权", "?"))
    add("cnh_j004_q3", muye_timeline(), "牧野之战的结果", must=("夏", "商", "西周", "牧野之战"))
    add("cnh_j072_q4", nixon_timeline(), "尼克松访华和1979年中美建交", must=("1972", "1979", "尼克松访华"))
    return rows


def figure_for(q):
    """按题号取图。题干对不上就停，避免知识点重排后图贴错题。"""
    hit = _BY_ID.get(q.get("id"))
    if not hit:
        return None
    drawing, expect = hit
    if expect not in (q.get("prompt") or ""):
        raise SystemExit("配图题干对不上 %s，需要含「%s」" % (q.get("id"), expect))
    return drawing


def _index():
    out = {}
    for qid, drawing, expect, _extra, _must in catalog():
        out[qid] = (drawing, expect)
    return out


_BY_ID = _index()


def svg_texts(drawing):
    return re.findall(r">([^<]+)</text>", drawing)


def number_problems(qid, drawing, blob, extra):
    bad = []
    nums = set(re.findall(r"\d+(?:\.\d+)?", blob))
    for s in svg_texts(drawing):
        for tok in re.findall(r"\d+(?:\.\d+)?", s):
            if tok not in nums and tok not in extra and tok != "0":
                bad.append("%s 的图里有数字 %s，题干和选项里没有（文字：%s）" % (qid, tok, s))
    return bad


def check_items(items, byid):
    problems = []
    seen = set()
    if not (20 <= len(items) <= 40):
        problems.append("配图题数 %d 不在 20–40" % len(items))
    for qid, drawing, expect, extra, must in items:
        if qid in seen:
            problems.append("重复登记 " + qid)
        seen.add(qid)
        q = byid.get(qid)
        if not q:
            problems.append("找不到题目 " + qid)
            continue
        if not str(q.get("topicId", "")).startswith("cnh_j"):
            problems.append("%s 不是初中历史题" % qid)
        if expect not in q.get("prompt", ""):
            problems.append("%s 题干不含「%s」" % (qid, expect))
        problems += figure_problems(drawing, qid)
        problems += overflow_problems(drawing)
        blob = q.get("prompt", "") + " " + " ".join(
            c.get("text", "") for c in (q.get("choices") or []) if isinstance(c, dict))
        problems += number_problems(qid, drawing, blob, extra)
        if re.search(r"AI\s*初稿|免费", drawing):
            problems.append(qid + " 图里有不允许的文案")
        answer = ""
        for c in q.get("choices") or []:
            if isinstance(c, dict) and c.get("key") == q.get("answer"):
                answer = c.get("text") or ""
        if answer and answer in drawing:
            problems.append("%s 的图里写出了正确选项「%s」" % (qid, answer))
        for phrase in must:
            if phrase not in drawing:
                problems.append("%s 的图缺少「%s」" % (qid, phrase))
    return problems


def write_preview(items, path, byid):
    parts = [
        "<!DOCTYPE html><meta charset=\"utf-8\"><title>历史图示预览</title>",
        "<style>body{margin:0;font-family:sans-serif;background:#fff;color:#162033}",
        ".row{display:flex;gap:12px;flex-wrap:wrap;padding:8px}",
        ".card{width:440px;padding:8px;box-sizing:border-box;border:1px solid #ddd}",
        "svg{width:100%;height:auto;display:block}h2{font-size:13px;margin:4px 0}",
        "p{font-size:12px;margin:2px 0 6px;color:#444}</style><div class=\"row\">",
    ]
    for qid, drawing, _e, _x, _m in items:
        q = byid.get(qid, {})
        prompt = esc(q.get("prompt", ""))
        parts.append("<div class=\"card\"><h2>%s</h2><p>%s</p>%s</div>" % (qid, prompt, drawing))
    parts.append("</div>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("预览", path, "共", len(items), "题")


def main():
    items = catalog()
    with open(QUESTIONS, encoding="utf-8") as f:
        questions = json.load(f)
    byid = {q["id"]: q for q in questions if isinstance(q, dict) and "id" in q}
    problems = check_items(items, byid)
    if problems:
        print("图示自检失败：")
        for p in problems:
            print("  " + p)
        return 1
    if len(sys.argv) >= 3 and sys.argv[1] == "--preview":
        write_preview(items, sys.argv[2], byid)
        return 0
    added = 0
    for qid, drawing, _e, _x, _m in items:
        q = byid[qid]
        if q.get("figure") != drawing:
            q["figure"] = drawing
            added += 1
    with open(QUESTIONS, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("初中历史带图题：%d（本次新写入或更新 %d）" % (len(items), added))
    return 0


if __name__ == "__main__":
    sys.exit(main())
