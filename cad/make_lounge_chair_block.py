"""
Генератор DXF-блока: лаунж-кресло + банкетка (оттоманка) + поворотный столик,
план (вид сверху), единицы — мм, масштаб 1:1.

Размеры по паспорту производителя:
  кресло:   ширина 798, глубина 889 (в вертикальном положении)
  столик:   299 x 553, общая ширина кресло+столик 1143
  банкетка: 533 x 437

Начало координат блоков — центр опоры кресла; сиденье смотрит в сторону -Y.

Запуск:  python3 make_lounge_chair_block.py
"""
import math
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

OUT = Path(__file__).with_name("lounge_chair_ottoman_plan.dxf")

# ---------------------------------------------------------------- геометрия


def superellipse(cx, cy, a, b, n=3.0, taper=0.0, seg=160):
    """Скруглённый «прямоугольник-овал». taper>0 — шире спереди (-Y)."""
    pts = []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / n), c)
        y = b * math.copysign(abs(s) ** (2 / n), s)
        x *= 1 + taper * (-y / b)
        pts.append((cx + x, cy + y))
    return Polygon(pts)


def star_base(cx, cy, r, legs=4, w=34, start=45):
    parts = []
    for k in range(legs):
        ang = math.radians(start + 360 * k / legs)
        tip = (cx + r * math.cos(ang), cy + r * math.sin(ang))
        parts.append(LineString([(cx, cy), tip]).buffer(w / 2, cap_style=1))
    parts.append(Point(cx, cy).buffer(w * 0.9))
    return unary_union(parts)


# Кресло
CHAIR_W, CHAIR_D = 798, 889
Y_BACK, Y_FRONT = 444, -445

shell = superellipse(0, 110, 300, 334, n=2.8, taper=0.14)
back_cushion = superellipse(0, 175, 232, 205, n=3.0, taper=0.06)
headrest = superellipse(0, 382, 205, 58, n=3.2)
arm_l = superellipse(-336, -55, 61, 232, n=3.0)
arm_r = superellipse(336, -55, 61, 232, n=3.0)
seat = superellipse(0, -205, 274, 240, n=3.2, taper=0.03)
chair_base = star_base(0, 0, 350)

# Столик (поворотный, крепится к левому подлокотнику)
TAB_CX = -CHAIR_W / 2 - 46 - 299 / 2  # = -594.5
TAB_CY = -60
tablet = superellipse(TAB_CX, TAB_CY, 299 / 2, 553 / 2, n=2.4)
tablet_arm = LineString([(TAB_CX, TAB_CY), (-336, TAB_CY)]).buffer(15, cap_style=2)
tablet_post = Point(TAB_CX, TAB_CY).buffer(22)

# Банкетка
OTT_CY = Y_FRONT - 150 - 437 / 2  # зазор 150 мм от кресла
ottoman = superellipse(0, OTT_CY, 533 / 2, 437 / 2, n=3.0, taper=-0.06)
ottoman_base = star_base(0, OTT_CY, 225, legs=4)


# ---------------------------------------------------------------- DXF

doc = ezdxf.new("R2013", setup=True)
doc.header["$INSUNITS"] = 4  # мм
doc.header["$MEASUREMENT"] = 1
doc.header["$LTSCALE"] = 1

for name, color, lt in [
    ("A-FURN", 7, "CONTINUOUS"),
    ("A-FURN-DIMS", 8, "CONTINUOUS"),
]:
    doc.layers.add(name, color=color, linetype=lt)

LT_HIDDEN = "DASHED"
LTS = 20  # масштаб типа линии для мм


def add_geom(blk, geom, **attrs):
    """Пишет контур(ы) shapely как LWPOLYLINE в блок."""
    if geom.is_empty:
        return
    if geom.geom_type in ("Polygon",):
        geoms = [geom.exterior] + list(geom.interiors)
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection", "MultiLineString"):
        for g in geom.geoms:
            add_geom(blk, g, **attrs)
        return
    else:
        geoms = [geom]
    for g in geoms:
        coords = list(g.coords)
        if len(coords) < 2:
            continue
        closed = g.geom_type == "LinearRing" or (
            len(coords) > 3 and Point(coords[0]).distance(Point(coords[-1])) < 1e-6
        )
        if closed:
            coords = coords[:-1]
        blk.add_lwpolyline(coords, close=closed, dxfattribs=attrs)


def visible_hidden(blk, poly, covers, detail=False):
    """Видимая часть контура — сплошной, скрытая под covers — штрихом."""
    edge = poly.exterior
    cov = unary_union(covers) if covers else None
    vis = edge.difference(cov) if cov else edge
    attrs = {"layer": "0", "color": 0}  # ПоБлоку
    if detail:
        attrs = {"layer": "0", "color": 8, "lineweight": 13}
    add_geom(blk, vis, **attrs)
    return edge.intersection(cov) if cov else None


def hidden(blk, geom):
    if geom is None or geom.is_empty:
        return
    add_geom(blk, geom, layer="0", color=8, linetype=LT_HIDDEN,
             ltscale=LTS, lineweight=13)


def piping(poly, d=16):
    """Кант — внутренний контур со смещением."""
    return poly.buffer(-d, join_style=1)


# --- блок КРЕСЛО ---------------------------------------------------------
chair_blk = doc.blocks.new("LOUNGE_CHAIR_PLAN", base_point=(0, 0))
top_chair = [arm_l, arm_r]
visible_hidden(chair_blk, arm_l, [])
visible_hidden(chair_blk, arm_r, [])
add_geom(chair_blk, piping(arm_l, 14).exterior, layer="0", color=8, lineweight=13)
add_geom(chair_blk, piping(arm_r, 14).exterior, layer="0", color=8, lineweight=13)
visible_hidden(chair_blk, seat, top_chair)
pseat = piping(seat, 18)
add_geom(chair_blk, pseat.exterior.difference(unary_union(top_chair)),
         layer="0", color=8, lineweight=13)
# прострочка-ямка в сиденье
chair_blk.add_lwpolyline([(-38, -40), (0, -46), (38, -40)],
                         dxfattribs={"layer": "0", "color": 8, "lineweight": 13})
visible_hidden(chair_blk, headrest, [])
visible_hidden(chair_blk, back_cushion, [seat, headrest] + top_chair, detail=True)
# шов на спинке (как на фото)
chair_blk.add_lwpolyline([(-60, 70), (60, 70)],
                         dxfattribs={"layer": "0", "color": 8, "lineweight": 13})
visible_hidden(chair_blk, shell, [seat, headrest] + top_chair)
# опора — скрытой линией
hidden(chair_blk, chair_base.exterior)

# --- блок СТОЛИК ---------------------------------------------------------
tab_blk = doc.blocks.new("LOUNGE_CHAIR_TABLET_PLAN", base_point=(0, 0))
visible_hidden(tab_blk, tablet, [])
add_geom(tab_blk, piping(tablet, 8).exterior, layer="0", color=8, lineweight=13)
arm_vis = tablet_arm.difference(unary_union([tablet, arm_l]))
add_geom(tab_blk, arm_vis.boundary.difference(tablet.union(arm_l).buffer(0.01)),
         layer="0", color=0)
hidden(tab_blk, tablet_arm.boundary.intersection(tablet))
hidden(tab_blk, tablet_post.exterior)

# --- блок БАНКЕТКА -------------------------------------------------------
ott_blk = doc.blocks.new("LOUNGE_OTTOMAN_PLAN", base_point=(0, OTT_CY))
visible_hidden(ott_blk, ottoman, [])
add_geom(ott_blk, piping(ottoman, 18).exterior, layer="0", color=8, lineweight=13)
ott_blk.add_circle((0, OTT_CY), 9, dxfattribs={"layer": "0", "color": 8, "lineweight": 13})
hidden(ott_blk, ottoman_base.exterior)

# --- сборный блок --------------------------------------------------------
set_blk = doc.blocks.new("LOUNGE_CHAIR_SET_PLAN", base_point=(0, 0))
set_blk.add_blockref("LOUNGE_CHAIR_PLAN", (0, 0), dxfattribs={"layer": "0"})
set_blk.add_blockref("LOUNGE_CHAIR_TABLET_PLAN", (0, 0), dxfattribs={"layer": "0"})
set_blk.add_blockref("LOUNGE_OTTOMAN_PLAN", (0, OTT_CY), dxfattribs={"layer": "0"})

# --- пространство модели ------------------------------------------------
msp = doc.modelspace()
msp.add_blockref("LOUNGE_CHAIR_SET_PLAN", (0, 0), dxfattribs={"layer": "A-FURN"})

# размеры (вне блока, на отдельном слое)
dimstyle = "EZDXF"
ds = doc.dimstyles.get(dimstyle)
ds.dxf.dimtxt = 40
ds.dxf.dimasz = 30
ds.dxf.dimexo = 10
ds.dxf.dimexe = 20
ds.dxf.dimdec = 0
ds.dxf.dimlfac = 1
ds.dxf.dimscale = 1
ds.dxf.dimtad = 1
DA = {"layer": "A-FURN-DIMS"}
tab_left = TAB_CX - 299 / 2
dims = [
    ((-CHAIR_W / 2, Y_BACK), (CHAIR_W / 2, Y_BACK), 560, 0),
    ((tab_left, Y_BACK), (CHAIR_W / 2, Y_BACK), 680, 0),
    ((CHAIR_W / 2, Y_BACK), (CHAIR_W / 2, Y_FRONT), 560, 90),
    ((tab_left, TAB_CY + 276.5), (tab_left, TAB_CY - 276.5), tab_left - 120, 90),
    ((tab_left, TAB_CY - 276.5), (tab_left + 299, TAB_CY - 276.5), -500, 0),
    ((-266.5, OTT_CY - 218.5), (266.5, OTT_CY - 218.5), OTT_CY - 360, 0),
    ((266.5, OTT_CY + 218.5), (266.5, OTT_CY - 218.5), 560, 90),
]
for p1, p2, base, ang in dims:
    if ang == 0:
        loc = (0, base)
    else:
        loc = (base, 0)
    msp.add_linear_dim(base=loc, p1=p1, p2=p2, angle=ang,
                       dimstyle=dimstyle, dxfattribs=DA).render()

msp.add_text("Кресло с банкеткой и столиком — план, мм",
             height=45, dxfattribs={"layer": "A-FURN-DIMS"}).set_placement(
    (tab_left, OTT_CY - 520), align=TextEntityAlignment.LEFT)

doc.saveas(OUT)
print("saved", OUT)
