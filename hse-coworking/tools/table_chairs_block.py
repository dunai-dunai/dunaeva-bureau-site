#!/usr/bin/env python3
"""Round table D700 with two light bentwood (Vienna-type) chairs, plan, mm.
Output: cad/table-d700-2chairs.dxf (+ PNG preview).
Blocks: TABLE_D700, CHAIR_VIENNA (single chair, front = -Y, seat centre at origin),
TABLE_D700_2CHAIRS_TUCKED (chairs pushed under the table; parts under the top are dashed).
Opens in ArchiCAD (File > Open / Interoperability > Merge) and AutoCAD (Save As DWG)."""
import os, math
import numpy as np
import ezdxf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cad'); os.makedirs(OUT, exist_ok=True)
TR = 350
doc = ezdxf.new('R2013', setup=True); doc.units = ezdxf.units.MM
for n, col, lt in (('FURN-TABLE', 7, 'CONTINUOUS'), ('FURN-CHAIR', 7, 'CONTINUOUS'),
                   ('FURN-DETAIL', 8, 'CONTINUOUS'), ('FURN-HIDDEN', 8, 'DASHED')):
    doc.layers.add(n, color=col, linetype=lt)
doc.header['$LTSCALE'] = 6

t = doc.blocks.new('TABLE_D700')
t.add_circle((0, 0), TR, dxfattribs={'layer': 'FURN-TABLE'})
t.add_circle((0, 0), TR - 15, dxfattribs={'layer': 'FURN-DETAIL'})
t.add_circle((0, 0), 60, dxfattribs={'layer': 'FURN-HIDDEN'})


def circle_pts(cx, cy, r, a0=0, a1=360, n=None):
    n = n or max(24, int(abs(a1 - a0) / 3))
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


# chair (front = -Y): round seat D410, bentwood back hoop behind it, 4 slightly splayed legs
SEAT = 205
CHAIR = [
    (circle_pts(0, 0, SEAT), True, 'FURN-CHAIR'),                         # seat rim
    (circle_pts(0, 0, SEAT - 22), True, 'FURN-DETAIL'),                   # cane / plywood insert
    (circle_pts(0, 25, 232, 20, 160), False, 'FURN-CHAIR'),               # back hoop, outer
    (circle_pts(0, 25, 212, 20, 160), False, 'FURN-CHAIR'),               # back hoop, inner
]
for a in (20, 160):                                                        # hoop ends
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    CHAIR.append(([(212 * ca, 25 + 212 * sa), (232 * ca, 25 + 232 * sa)], False, 'FURN-CHAIR'))
for a, r in ((235, 214), (305, 214), (65, 200), (115, 200)):              # legs
    CHAIR.append((circle_pts(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 14), True, 'FURN-DETAIL'))
CHAIR.append((circle_pts(0, 0, 150), True, 'FURN-HIDDEN'))               # leg ring under the seat

ch = doc.blocks.new('CHAIR_VIENNA')
for pts, closed, layer in CHAIR:
    ch.add_lwpolyline(pts, close=closed, dxfattribs={'layer': layer})


def place(pts, x, y, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]


def add_clipped(blk, pts, closed, layer):
    """parts outside the table drawn as is, parts under the top dashed."""
    if closed: pts = pts + [pts[0]]
    dense = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 4))
        dense += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
    dense.append(pts[-1])
    inside = [math.hypot(*p) < TR for p in dense]
    run, cur = [], inside[0]
    for p, ins in zip(dense, inside):
        if ins != cur and run:
            blk.add_lwpolyline(run + [p], dxfattribs={'layer': 'FURN-HIDDEN' if cur else layer})
            run, cur = [p], ins
        else:
            run.append(p)
    if len(run) > 1:
        blk.add_lwpolyline(run, dxfattribs={'layer': 'FURN-HIDDEN' if cur else layer})


g = doc.blocks.new('TABLE_D700_2CHAIRS_TUCKED')
g.add_blockref('TABLE_D700', (0, 0))
DIST = 300            # seat centre from table centre: seat under the top, back hoop against its edge
for side in (-1, 1):
    rot = 90 if side < 0 else -90       # front (-Y) toward the table centre
    for pts, closed, layer in CHAIR:
        if layer != 'FURN-HIDDEN':
            add_clipped(g, place(pts, side * DIST, 0, rot), closed, layer)

msp = doc.modelspace()
msp.add_blockref('TABLE_D700_2CHAIRS_TUCKED', (0, 0))
msp.add_blockref('CHAIR_VIENNA', (0, -900))     # a loose chair to copy around
path = os.path.join(OUT, 'table-d700-2chairs.dxf'); doc.saveas(path)

import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
fig = plt.figure(figsize=(6, 7)); ax = fig.add_axes([0, 0, 1, 1])
Frontend(RenderContext(doc), MatplotlibBackend(ax),
         config=Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)).draw_layout(msp)
ax.set_aspect('equal'); fig.savefig(os.path.join(OUT, 'table-d700-2chairs.png'), dpi=150, facecolor='white')
print(path)
