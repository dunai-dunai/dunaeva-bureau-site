#!/usr/bin/env python3
"""Single phone booth (plan) as a CAD block, mm. Output: cad/phone-booth-1p.dxf (+ PNG preview).
AutoCAD: open the DXF and Save As DWG; the block is called PHONE_BOOTH_1P (insertion point = front-left corner).
"""
import os, math
import ezdxf
from ezdxf.enums import TextEntityAlignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cad'); os.makedirs(OUT, exist_ok=True)

W, D = 1100, 1100          # outer size
POST = 55                  # corner posts
WALL = 60                  # side wall panels
BACK = 40                  # back wall
GL_Y0, GL_Y1 = 30, 42      # front glass (12 mm)
DESK = 360                 # desk shelf depth
DOOR_HINGE = (POST + 30, GL_Y0)
DOOR_W = 870

doc = ezdxf.new('R2013', setup=True)
doc.units = ezdxf.units.MM
for name, color, lt in (('BOOTH-FRAME', 7, 'CONTINUOUS'), ('BOOTH-GLASS', 4, 'CONTINUOUS'),
                        ('BOOTH-FURN', 8, 'CONTINUOUS'), ('BOOTH-DOOR', 7, 'DASHED')):
    doc.layers.add(name, color=color, linetype=lt)

blk = doc.blocks.new('PHONE_BOOTH_1P')


def rect(x0, y0, x1, y1, layer):
    blk.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={'layer': layer})


# corner posts (full depth)
rect(0, 0, POST, D, 'BOOTH-FRAME')
rect(W - POST, 0, W, D, 'BOOTH-FRAME')
# back wall
rect(POST, D - BACK, W - POST, D, 'BOOTH-FRAME')
# side wall panels, chamfered at the back corners
c = 40
for sx in (1, -1):
    x_out = POST if sx == 1 else W - POST
    x_in = x_out + sx * WALL
    blk.add_lwpolyline([(x_out, GL_Y1 + 20), (x_in, GL_Y1 + 60), (x_in, D - BACK - c), (x_in - sx * c * .0 + 0, D - BACK - c),
                        (x_out, D - BACK)], close=False, dxfattribs={'layer': 'BOOTH-FRAME'})
    blk.add_line((x_in, D - BACK - c), (x_in + sx * c, D - BACK), dxfattribs={'layer': 'BOOTH-FRAME'})
# front glass (two lines)
blk.add_line((POST, GL_Y0), (W - POST, GL_Y0), dxfattribs={'layer': 'BOOTH-GLASS'})
blk.add_line((POST, GL_Y1), (W - POST, GL_Y1), dxfattribs={'layer': 'BOOTH-GLASS'})
# desk shelf
xi0, xi1 = POST + WALL, W - POST - WALL
blk.add_line((xi0, D - BACK - DESK), (xi1, D - BACK - DESK), dxfattribs={'layer': 'BOOTH-FURN'})
blk.add_line((xi0, D - BACK - DESK - 18), (xi1, D - BACK - DESK - 18), dxfattribs={'layer': 'BOOTH-FURN'})
# stool seat: rounded square 330 x 300, r = 70
cx, cy, sw, sh, r = W / 2, D - BACK - DESK - 220, 330, 300, 70
x0, x1, y0, y1 = cx - sw / 2, cx + sw / 2, cy - sh / 2, cy + sh / 2
b = math.tan(math.pi / 8)          # bulge for 90° arcs
blk.add_lwpolyline([(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b), (x1 - r, y1, 0),
                    (x0 + r, y1, b), (x0, y1 - r, 0), (x0, y0 + r, b)], format='xyb', close=True,
                   dxfattribs={'layer': 'BOOTH-FURN'})
# hinge and handle
hx, hy = DOOR_HINGE
blk.add_circle((hx, hy + 6), 12, dxfattribs={'layer': 'BOOTH-FRAME'})
rect(hx + DOOR_W - 60, GL_Y1, hx + DOOR_W - 45, GL_Y1 + 45, 'BOOTH-FRAME')
rect(hx + DOOR_W - 60, GL_Y0 - 45, hx + DOOR_W - 45, GL_Y0, 'BOOTH-FRAME')
# door: open leaf + swing
blk.add_line((hx, hy), (hx, hy - DOOR_W), dxfattribs={'layer': 'BOOTH-DOOR'})
blk.add_arc((hx, hy), DOOR_W, 270, 360, dxfattribs={'layer': 'BOOTH-DOOR'})

msp = doc.modelspace()
msp.add_blockref('PHONE_BOOTH_1P', (0, 0))
doc.header['$LTSCALE'] = 10
path = os.path.join(OUT, 'phone-booth-1p.dxf')
doc.saveas(path)

# preview
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
fig = plt.figure(figsize=(6, 8)); ax = fig.add_axes([0, 0, 1, 1])
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp)
ax.set_aspect('equal'); fig.savefig(os.path.join(OUT, 'phone-booth-1p.png'), dpi=150, facecolor='white')
print(path)
