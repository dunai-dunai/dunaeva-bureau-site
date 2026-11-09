#!/usr/bin/env python3
"""Round table D700 with two small lounge armchairs, plan, mm. Output: cad/table-d700-2chairs.dxf
Blocks: TABLE_D700, ARMCHAIR_S (620 x 620, front = -Y), group block TABLE_D700_2CHAIRS. Works in ArchiCAD
(File > Interoperability > Merge / or Open DXF) and AutoCAD (Save As DWG)."""
import os, math
import numpy as np
import ezdxf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cad'); os.makedirs(OUT, exist_ok=True)
doc = ezdxf.new('R2013', setup=True); doc.units = ezdxf.units.MM
doc.layers.add('FURN-TABLE', color=7); doc.layers.add('FURN-CHAIR', color=7); doc.layers.add('FURN-DETAIL', color=8)

# table
t = doc.blocks.new('TABLE_D700')
t.add_circle((0, 0), 350, dxfattribs={'layer': 'FURN-TABLE'})
t.add_circle((0, 0), 330, dxfattribs={'layer': 'FURN-DETAIL'})        # edge chamfer
t.add_circle((0, 0), 60, dxfattribs={'layer': 'FURN-DETAIL', 'linetype': 'DASHED'})   # pedestal below

# armchair 620 x 620, centre at origin, seat faces -Y
W, D, R = 620, 620, 110
c = doc.blocks.new('ARMCHAIR_S')
b = math.tan(math.pi / 8)
x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
SAG = 120                                     # how much the back bulges
yb = y1 - SAG
bul = 2 * SAG / W                             # bulge of the back arc (sagitta / half-chord)
c.add_lwpolyline([(x0 + R, y0, 0), (x1 - R, y0, b), (x1, y0 + R, 0), (x1, yb, bul), (x0, yb, 0), (x0, y0 + R, b)],
                 format='xyb', close=True, dxfattribs={'layer': 'FURN-CHAIR'})
# inner line of arms + backrest (same curve, offset inward)
AW, BT = 85, 110
xi0, xi1 = x0 + AW, x1 - AW
ybi = yb - BT + 40
sag_i = SAG * (xi1 - xi0) / W
c.add_lwpolyline([(xi0, y0 + 30, 0), (xi0, ybi, -2 * sag_i / (xi1 - xi0)), (xi1, ybi, 0), (xi1, y0 + 30, 0)],
                 format='xyb', dxfattribs={'layer': 'FURN-DETAIL'})
# seat cushion with a soft front edge
cw = (xi1 - 15) - (xi0 + 15)
c.add_lwpolyline([(xi0 + 15, y0 + 45, 0), (xi1 - 15, y0 + 45, 0), (xi1 - 15, ybi - 25, 2 * sag_i * .85 / cw), (xi0 + 15, ybi - 25, 0)],
                 format='xyb', close=True, dxfattribs={'layer': 'FURN-DETAIL'})

# group: chairs left and right of the table, turned slightly toward each other's front
g = doc.blocks.new('TABLE_D700_2CHAIRS')
g.add_blockref('TABLE_D700', (0, 0))
gap = 90                                        # table edge to chair front
dist = 350 + gap + D / 2
for side in (-1, 1):
    open_ = 15                                   # chairs turned a little toward the room (front = -Y)
    rot = (90 if side < 0 else -90) + side * open_
    g.add_blockref('ARMCHAIR_S', (side * dist, -70), dxfattribs={'rotation': rot})
doc.modelspace().add_blockref('TABLE_D700_2CHAIRS', (0, 0))
path = os.path.join(OUT, 'table-d700-2chairs.dxf'); doc.saveas(path)

import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
fig = plt.figure(figsize=(8, 4)); ax = fig.add_axes([0, 0, 1, 1])
Frontend(RenderContext(doc), MatplotlibBackend(ax),
         config=Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)).draw_layout(doc.modelspace())
ax.set_aspect('equal'); fig.savefig(os.path.join(OUT, 'table-d700-2chairs.png'), dpi=150, facecolor='white')
print(path)
