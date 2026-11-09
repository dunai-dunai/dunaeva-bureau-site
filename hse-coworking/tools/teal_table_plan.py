#!/usr/bin/env python3
"""Plan (top view) of the 3-piece organic coffee table from the photo source/14-teal-table.jpg.

The top faces are segmented by colour, then un-projected from the photo's oblique view to a plan
(depth stretched by 1/sin(camera elevation), far parts enlarged for perspective), scaled so the
whole set is LENGTH mm long, and written as closed splines into a DXF block TEAL_TABLE_SET.
This is an approximation from one photo, not manufacturer data.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cad'); os.makedirs(OUT, exist_ok=True)
LENGTH = 2400              # mm, overall length of the set (assumed)
ELEV = 24                  # camera elevation above the table plane, degrees (estimated)
Y_FAR, Y_NEAR = 590, 980   # image rows of the farthest / nearest top edges
PERSP = .18                # far edge looks this much smaller than the near edge

im = Image.open(os.path.join(ROOT, 'source', '14-teal-table.jpg')).convert('RGB')
c = np.asarray(im, np.float32); r, g, b = c[..., 0], c[..., 1], c[..., 2]
lum = .3 * r + .59 * g + .11 * b
top = Image.fromarray((((g - r > 40) & (lum > 115)) * 255).astype(np.uint8))
top = top.filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.MinFilter(7))
pieces = []
for seed in ((300, 700), (850, 820), (1300, 680)):
    t = top.convert('RGB'); ImageDraw.floodfill(t, seed, (255, 0, 0))
    sel = (np.asarray(t) == [255, 0, 0]).all(2)
    sel = np.asarray(Image.fromarray((sel * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
                     .filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15)).filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    pieces.append(sel)

k = 1 / np.sin(np.radians(ELEV))


def unproject(x, y):
    t = np.clip((Y_NEAR - y) / (Y_NEAR - Y_FAR), -.3, 1.3)      # 0 near … 1 far
    s = 1 + PERSP * t
    return (x - 1000) * s, (Y_NEAR - y) * k * (1 + PERSP * t / 2)


outlines = []
for sel in pieces:
    fig = plt.figure(); cs = plt.contour(sel, levels=[.5]); plt.close(fig)
    paths = cs.allsegs[0]
    seg = max(paths, key=len)
    n = 25                                         # circular moving average: smooth, CAD-clean curves
    ext = np.concatenate([seg[-n:], seg, seg[:n]])
    ker = np.ones(2 * n + 1) / (2 * n + 1)
    seg = np.stack([np.convolve(ext[:, 0], ker, 'same')[n:-n], np.convolve(ext[:, 1], ker, 'same')[n:-n]], 1)
    seg = seg[::12]
    px, py = unproject(seg[:, 0], seg[:, 1])
    outlines.append(np.stack([px, py], 1))
allp = np.concatenate(outlines)
scale = LENGTH / (allp[:, 0].max() - allp[:, 0].min())
x0, y0 = allp[:, 0].min(), allp[:, 1].min()
outlines = [np.stack([(o[:, 0] - x0) * scale, (o[:, 1] - y0) * scale], 1) for o in outlines]

doc = ezdxf.new('R2013', setup=True); doc.units = ezdxf.units.MM
doc.layers.add('TABLE-TOP', color=7)
doc.layers.add('TABLE-TEXT', color=8)
blk = doc.blocks.new('TEAL_TABLE_SET')
names = ['Стол 1', 'Стол 2', 'Стол 3']
for o, nm in zip(outlines, names):
    pts = [(float(x), float(y)) for x, y in o]
    blk.add_spline(fit_points=pts + [pts[0]], dxfattribs={'layer': 'TABLE-TOP'}).closed = True
doc.modelspace().add_blockref('TEAL_TABLE_SET', (0, 0))
doc.saveas(os.path.join(OUT, 'teal-table-set-plan.dxf'))

# preview with overall dims
fig = plt.figure(figsize=(10, 5)); ax = fig.add_axes([0.05, 0.08, .9, .87])
for o in outlines:
    ax.fill(o[:, 0], o[:, 1], color='#d9eef0', ec='black', lw=1)
W_ = max(o[:, 0].max() for o in outlines); D_ = max(o[:, 1].max() for o in outlines)
ax.set_aspect('equal'); ax.set_xlim(-100, W_ + 100); ax.set_ylim(-100, D_ + 100)
ax.set_title(f'План, мм (приблизительно): {W_:.0f} × {D_:.0f}')
fig.savefig(os.path.join(OUT, 'teal-table-set-plan.png'), dpi=140, facecolor='white')
print(round(W_), round(D_), [len(o) for o in outlines])
