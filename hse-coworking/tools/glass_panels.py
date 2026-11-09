#!/usr/bin/env python3
"""Tall lilac glass panels as separate transparent PNGs, for assembling booths in Photoshop.

Same measured tint as cutouts/glass-lilac.png. For each panel two files:
  *.png        — one layer, Normal blend (tuned for light walls)
  *-tint.png   — tint only: put it in Multiply blend, it then tints whatever is under it correctly
Panels: front (facing the viewer), side (seen at an angle, narrow trapezoid, denser colour),
edge (the glass seen end-on: a thin dark violet line).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cutouts', 'glass-panels'); os.makedirs(OUT, exist_ok=True)
T = np.array([.78, .64, .87], np.float32)            # transmittance measured from the reference photo
EDGE = (58, 26, 72)
WALL = np.array([236, 230, 221], np.float32)


def save_pair(name, face_mask, tint_strength, edges, sheen):
    """face_mask: L image; tint_strength: 0..1 array (how much glass the light passes through)."""
    w, h = face_mask.size
    m = np.asarray(face_mask, np.float32) / 255
    Tm = 1 - (1 - T)[None, None, :] * tint_strength[..., None]           # deeper where more glass
    # tint layer for Multiply
    tint = np.zeros((h, w, 4), np.float32); tint[..., :3] = 255 * Tm; tint[..., 3] = 255 * m
    # normal-mode layer reproducing multiply over a light wall
    A = .5
    C = (WALL * Tm - (1 - A) * WALL) / A
    one = np.zeros((h, w, 4), np.float32); one[..., :3] = np.clip(C, 0, 255); one[..., 3] = 255 * A * m
    im_t = Image.fromarray(tint.astype(np.uint8), 'RGBA')
    im_o = Image.fromarray(one.astype(np.uint8), 'RGBA')
    # shine + edges on both
    sh = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    sh.putalpha(Image.fromarray((np.clip(sheen, 0, 1) * 255 * m).astype(np.uint8)))
    ed = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ed)
    for pts, col, wd in edges:
        d.line(pts, fill=col, width=wd)
    ed = ed.filter(ImageFilter.GaussianBlur(.7))
    for im in (im_o, im_t):
        im.alpha_composite(sh); im.alpha_composite(ed)
    im_o.save(os.path.join(OUT, f'{name}.png'))
    im_t.save(os.path.join(OUT, f'{name}-tint.png'))
    return im_o


H = 2800
# --- front panel
Wf = 720
yy, xx = np.mgrid[0:H, 0:Wf].astype(np.float32)
u, v = xx / Wf, yy / H
sheen = .22 * np.exp(-((u + v * .25 - .30) / .06) ** 2) + .10 * np.exp(-((u + v * .25 - .48) / .025) ** 2)
sheen += .06 * np.exp(-((v - .02) / .03) ** 2)                                    # light catching the top
front = save_pair('panel-front', Image.new('L', (Wf, H), 255), np.ones((H, Wf), np.float32), [
    ([(1, 0), (1, H)], (255, 255, 255, 200), 3), ([(0, 1), (Wf, 1)], (255, 255, 255, 220), 3),
    ([(Wf - 2, 0), (Wf - 2, H)], EDGE + (230,), 4), ([(0, H - 2), (Wf, H - 2)], EDGE + (200,), 3)], sheen)

# --- side panel (seen at an angle): trapezoid, colour deepens toward the far edge
Ws = 300
top_near, top_far = 0, 140          # far edge is shorter (perspective)
m = Image.new('L', (Ws, H), 0)
ImageDraw.Draw(m).polygon([(0, top_near), (Ws, top_far), (Ws, H - top_far * .35), (0, H)], fill=255)
yy, xx = np.mgrid[0:H, 0:Ws].astype(np.float32)
strength = 1.25 + .55 * (xx / Ws)                     # oblique view = longer path through glass
sheen = .25 * np.exp(-((xx / Ws - .25) / .08) ** 2) * (.6 + .4 * (yy / H))
side = save_pair('panel-side', m, strength, [
    ([(1, top_near), (1, H)], (255, 255, 255, 210), 3),
    ([(Ws - 2, top_far), (Ws - 2, H - top_far * .35)], EDGE + (240,), 5),
    ([(0, top_near + 1), (Ws, top_far + 1)], (255, 255, 255, 200), 3)], sheen)

# --- edge (glass seen end-on)
We = 18
m = Image.new('L', (We, H), 255)
yy, xx = np.mgrid[0:H, 0:We].astype(np.float32)
edge = save_pair('panel-edge', m, np.full((H, We), 3.2, np.float32), [
    ([(2, 0), (2, H)], (255, 255, 255, 160), 2), ([(We - 3, 0), (We - 3, H)], EDGE + (255,), 4)],
    np.zeros((H, We), np.float32))

# --- demo: a booth-like arrangement over a wall with a stripe so transparency shows
demo = Image.new('RGB', (1900, 1500), tuple(WALL.astype(int)))
dd = ImageDraw.Draw(demo)
for k in range(0, 1900, 120):
    dd.rectangle([k, 0, k + 50, 1500], fill=(222, 214, 202))            # wall panelling
dd.rectangle([0, 1240, 1900, 1500], fill=(200, 151, 106))               # oak floor
dd.rectangle([820, 900, 1080, 1300], fill=(32, 32, 34))                 # a dark desk behind glass
demo = demo.convert('RGBA')
sc = 1300 / H
f = front.resize((int(Wf * sc), 1300)); s = side.resize((int(Ws * sc), 1300)); e = edge.resize((max(3, int(We * sc * 1.6)), 1300))
demo.alpha_composite(s, (300, 80)); demo.alpha_composite(f, (300 + s.width, 80)); demo.alpha_composite(e, (300 + s.width + f.width, 80))
demo.alpha_composite(s, (980, 80)); demo.alpha_composite(f, (980 + s.width, 80))
demo.convert('RGB').resize((950, 750), Image.LANCZOS).save(os.path.join(OUT, 'demo.jpg'), quality=90)
print('ok')
