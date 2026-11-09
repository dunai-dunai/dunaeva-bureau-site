"""
DXF-блок для AutoCAD: лаунж-кресло + поворотный столик + банкетка, план (вид сверху).
Единицы — мм, масштаб 1:1.

Контуры взяты векторизацией вида сверху с чертежа производителя
(reference_trace.json, см. trace_reference.py) и приведены к размерам из паспорта:
  кресло:            ширина 798, глубина 889
  столик:            299 x 553
  кресло + столик:   1143
  банкетка:          533 x 437

Кресло и банкетка симметричны: берётся правая половина контура и зеркалится.
Начало координат — центр кресла по ширине, передний край сиденья смотрит в -Y.

Запуск:  python3 make_lounge_chair_block.py
"""
import json
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import linemerge, unary_union
from shapely import affinity

HERE = Path(__file__).parent
OUT = HERE / "lounge_chair_ottoman_plan.dxf"
TRACE = json.loads((HERE / "reference_trace.json").read_text())

CHAIR_W, CHAIR_D = 798, 889
TAB_W, TAB_D = 299, 553
TOTAL_W = 1143
OTT_W, OTT_D = 533, 437
OTT_GAP = 150  # зазор кресло — банкетка

# --- опорные координаты на чертеже (пиксели исходного изображения) --------
CH_RIGHT_PX = 541.25           # правый край подлокотника (размер 798)
CH_LEFT_PX = 445.0             # левая выносная линия размера 798
CH_CX_PX = (CH_LEFT_PX + CH_RIGHT_PX) / 2
TAB_RIGHT_PX = 447.5           # всё левее — столик
BRACKET_Y_PX = (224.0, 230.5)  # кронштейн столика


def lines(paths):
    return [LineString(p) for p in paths if len(p) > 1]


def bounds(geoms):
    return unary_union(geoms).bounds


def mirror_half(geoms, cx):
    """Правая половина + её зеркальная копия, линии сшиты по оси."""
    half = unary_union(geoms).intersection(box(cx, -1e6, 1e6, 1e6))
    mir = affinity.scale(half, xfact=-1, yfact=1, origin=(cx, 0))
    merged = linemerge(unary_union([half, mir]))
    return list(merged.geoms) if hasattr(merged, "geoms") else [merged]


# ------------------------------------------------------------------ кресло
chair_px = lines(TRACE["chair"])
right_side = [g for g in chair_px if g.bounds[2] > CH_CX_PX]
chair = mirror_half(right_side, CH_CX_PX)
_, cy0, _, cy1 = bounds(chair)  # y вниз на картинке
sx = CHAIR_W / (CH_RIGHT_PX - CH_LEFT_PX)
sy = CHAIR_D / (cy1 - cy0)
CH_CY_PX = (cy0 + cy1) / 2


def chair_to_mm(g):
    g = affinity.translate(g, -CH_CX_PX, -CH_CY_PX)
    return affinity.scale(g, xfact=sx, yfact=-sy, origin=(0, 0))


chair_mm = [chair_to_mm(g) for g in chair]
Y_BACK, Y_FRONT = CHAIR_D / 2, -CHAIR_D / 2
CH_R = CHAIR_W / 2

# ------------------------------------------------------------------ столик
tab_px = [g for g in chair_px if g.bounds[2] <= TAB_RIGHT_PX]
TAB_EDGE_R_PX = 445.6          # правый край столешницы на чертеже
tx0 = unary_union(tab_px).bounds[0]
# столешница симметрична — берём чистую левую половину и зеркалим
tab_px = unary_union(mirror_half(
    [affinity.scale(g, xfact=-1, origin=((tx0 + TAB_EDGE_R_PX) / 2, 0)) for g in tab_px],
    (tx0 + TAB_EDGE_R_PX) / 2))
tab_px = linemerge(tab_px) if tab_px.geom_type == "MultiLineString" else tab_px
tx0, ty0, tx1, ty1 = tab_px.bounds
tab_left_mm = CH_R - TOTAL_W
tab_cy_mm = -((ty0 + ty1) / 2 - CH_CY_PX) * sy
tablet = affinity.translate(tab_px, -(tx0 + tx1) / 2, -(ty0 + ty1) / 2)
tablet = affinity.scale(tablet, TAB_W / (tx1 - tx0), -TAB_D / (ty1 - ty0), origin=(0, 0))
tablet = affinity.translate(tablet, tab_left_mm + TAB_W / 2, tab_cy_mm)
tab_right_mm = tab_left_mm + TAB_W

# кронштейн: две линии от столика до корпуса кресла (как на чертеже)
x_shell = None
for g in chair_mm:  # ближайшая к оси линия корпуса слева на уровне кронштейна
    yb = -(sum(BRACKET_Y_PX) / 2 - CH_CY_PX) * sy
    hit = g.intersection(LineString([(-CH_R, yb), (0, yb)]))
    for p in getattr(hit, "geoms", [hit]):
        if not p.is_empty and p.geom_type == "Point":
            x_shell = p.x if x_shell is None else min(x_shell, p.x, key=lambda v: abs(v + CH_R - 50))
bracket = []
arm_cover = unary_union([g for g in chair_mm])
for ypx in BRACKET_Y_PX:
    y = -(ypx - CH_CY_PX) * sy
    seg = LineString([(tab_right_mm, y), (x_shell + 5, y)])
    # кронштейн уходит под подлокотник — обрезаем по первой встреченной линии
    hit = seg.intersection(arm_cover)
    xs = [q.x for q in getattr(hit, "geoms", [hit]) if not q.is_empty and q.geom_type == "Point"]
    bracket.append(LineString([(tab_right_mm, y), (min(xs) if xs else x_shell, y)]))

# ---------------------------------------------------------------- банкетка
ott_px = lines(TRACE["ottoman"])
ox0, oy0, ox1, oy1 = bounds(ott_px)
ott = mirror_half(ott_px, (ox0 + ox1) / 2)
ox0, oy0, ox1, oy1 = bounds(ott)
OTT_CY = Y_FRONT - OTT_GAP - OTT_D / 2


def ott_to_mm(g):
    g = affinity.translate(g, -(ox0 + ox1) / 2, -(oy0 + oy1) / 2)
    g = affinity.scale(g, OTT_W / (ox1 - ox0), -OTT_D / (oy1 - oy0), origin=(0, 0))
    return affinity.translate(g, 0, OTT_CY)


ott_mm = [ott_to_mm(g) for g in ott]

# ===================================================================== DXF
doc = ezdxf.new("R2013", setup=True)
doc.header["$INSUNITS"] = 4
doc.header["$MEASUREMENT"] = 1
doc.layers.add("A-FURN", color=7)
doc.layers.add("A-FURN-DIMS", color=8)

ATTR = {"layer": "0", "color": 0, "lineweight": -2}  # ПоБлоку


def add(blk, g):
    if g.is_empty:
        return
    if hasattr(g, "geoms"):
        for gg in g.geoms:
            add(blk, gg)
        return
    pts = list(g.coords)
    closed = len(pts) > 3 and g.is_ring
    if closed:
        pts = pts[:-1]
    blk.add_lwpolyline(pts, close=closed, dxfattribs=ATTR)


chair_blk = doc.blocks.new("LOUNGE_CHAIR_PLAN", base_point=(0, 0))
for g in chair_mm:
    add(chair_blk, g)

tab_blk = doc.blocks.new("LOUNGE_CHAIR_TABLET_PLAN", base_point=(0, 0))
add(tab_blk, tablet)
for g in bracket:
    add(tab_blk, g)

ott_blk = doc.blocks.new("LOUNGE_OTTOMAN_PLAN", base_point=(0, OTT_CY))
for g in ott_mm:
    add(ott_blk, g)

set_blk = doc.blocks.new("LOUNGE_CHAIR_SET_PLAN", base_point=(0, 0))
for name, pt in [("LOUNGE_CHAIR_PLAN", (0, 0)), ("LOUNGE_CHAIR_TABLET_PLAN", (0, 0)),
                 ("LOUNGE_OTTOMAN_PLAN", (0, OTT_CY))]:
    set_blk.add_blockref(name, pt, dxfattribs={"layer": "0"})

msp = doc.modelspace()
msp.add_blockref("LOUNGE_CHAIR_SET_PLAN", (0, 0), dxfattribs={"layer": "A-FURN"})

# --- размеры ---------------------------------------------------------------
ds = doc.dimstyles.get("EZDXF")
for k, v in dict(dimtxt=40, dimasz=30, dimexo=10, dimexe=20, dimdec=0,
                 dimtad=1, dimlfac=1, dimscale=1).items():
    ds.dxf.set(k, v)
DA = {"layer": "A-FURN-DIMS"}
tb, tt = tab_cy_mm - TAB_D / 2, tab_cy_mm + TAB_D / 2
dims = [
    ((-CH_R, Y_BACK), (CH_R, Y_BACK), Y_BACK + 120, 0),
    ((tab_left_mm, tt), (CH_R, Y_BACK), Y_BACK + 240, 0),
    ((CH_R, Y_BACK), (CH_R, Y_FRONT), CH_R + 150, 90),
    ((tab_left_mm, tt), (tab_left_mm, tb), tab_left_mm - 120, 90),
    ((tab_left_mm, tb), (tab_right_mm, tb), tb - 120, 0),
    ((-OTT_W / 2, OTT_CY - OTT_D / 2), (OTT_W / 2, OTT_CY - OTT_D / 2), OTT_CY - OTT_D / 2 - 120, 0),
    ((OTT_W / 2, OTT_CY + OTT_D / 2), (OTT_W / 2, OTT_CY - OTT_D / 2), OTT_W / 2 + 150, 90),
]
for p1, p2, base, ang in dims:
    loc = (0, base) if ang == 0 else (base, 0)
    msp.add_linear_dim(base=loc, p1=p1, p2=p2, angle=ang, dimstyle="EZDXF",
                       dxfattribs=DA).render()

msp.add_text("Кресло со столиком и банкеткой — план, мм", height=45,
             dxfattribs=DA).set_placement((tab_left_mm, OTT_CY - OTT_D / 2 - 320),
                                          align=TextEntityAlignment.LEFT)

doc.saveas(OUT)
print("saved", OUT, f"scale x={sx:.2f} y={sy:.2f} mm/px, x_shell={x_shell:.0f}")
