#!/usr/bin/env python3
"""Cut the two desk clusters (tops + white sled frames) out of source/12-workspace.webp, without chairs.
Tops are polygons; frames are the bars of hollow quads (so chair bases seen through the frames stay out);
dividers are saved separately. Output: cutouts/desks/*.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cutouts', 'desks'); os.makedirs(OUT, exist_ok=True)
im = Image.open(os.path.join(ROOT, 'source', '12-workspace.webp')).convert('RGB'); W, H = im.size
c = np.asarray(im, np.float32)
lum = c @ np.array([.3, .59, .11], np.float32)
sat = (c.max(2) - c.min(2)) / np.maximum(c.max(2), 1)


def poly(pts):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return np.asarray(m) > 0


def frame(tl, tr, br, bl, t=12):
    """bars of a sled frame given its 4 outer corners (hollow quad, bar thickness t)."""
    outer = poly([tl, tr, br, bl])
    inner = poly([(tl[0] + t, tl[1] + t), (tr[0] - t, tr[1] + t), (br[0] - t, br[1] - t), (bl[0] + t, bl[1] - t)])
    return outer & ~inner


white = (sat < .16) & (lum > 95)

L_top = poly([(312, 736), (446, 697), (446, 660), (500, 633), (712, 642), (712, 651), (572, 766), (312, 748)])
L_frames = frame((313, 745), (441, 752), (441, 893), (313, 886), 11) | frame((443, 752), (574, 756), (574, 898), (443, 893), 11)
L_back = poly([(455, 790), (532, 794), (532, 803), (455, 799)]) | poly([(529, 760), (541, 760), (541, 803), (529, 803)])
L_div = poly([(446, 660), (555, 615), (626, 611), (626, 641), (555, 685), (446, 737)])

R_top = poly([(990, 648), (1190, 648), (1277, 790), (1277, 801), (985, 788), (985, 776)])
R_frames = frame((983, 775), (1123, 779), (1123, 942), (983, 930), 12) | frame((1125, 780), (1276, 790), (1272, 952), (1125, 942), 12)
R_back = poly([(1000, 822), (1100, 826), (1100, 840), (1000, 836)]) | poly([(1137, 790), (1262, 795), (1262, 805), (1137, 800)])
R_div = poly([(1086, 578), (1133, 660), (1133, 771), (1110, 756), (1086, 648)])


def cut(mask, name, feather=.6):
    a = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather))
    l = im.convert('RGBA'); l.putalpha(a)
    bb = l.getbbox(); l.crop(bb).save(os.path.join(OUT, name)); return bb


for side, top, frames, div in (('left', L_top, L_frames, L_div), ('right', R_top, R_frames, R_div)):
    cut(top | frames | div, f'desk-{side}.png')

# check on a neutral background
sheet = Image.new('RGB', (760, 420), (236, 230, 221))
x = 20
for f in ('desk-left.png', 'desk-right.png'):
    p = Image.open(os.path.join(OUT, f)); sheet.paste(p, (x, 20), p); x += p.width + 20
sheet.save(os.path.join(OUT, 'check.jpg'), quality=90)
print('ok')
