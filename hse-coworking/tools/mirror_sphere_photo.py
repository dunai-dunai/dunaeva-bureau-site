#!/usr/bin/env python3
"""Spherical mirror that reflects a whole picture (default: source/02-workspace-draft.webp).

A mirror ball bends rays by twice the surface angle: a point at radius rho from the
centre reflects the direction psi = 2*asin(rho) away from the view axis. That
direction is projected into the picture as a rectilinear camera; beyond the picture
the edges are mirrored, and the rim darkens as on real chrome.

    python3 tools/mirror_sphere_photo.py [picture] [diameter_px]
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pic = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'source', '02-workspace-draft.webp')
D = int(sys.argv[2]) if len(sys.argv) > 2 else 700
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0     # 0.125 = reflection 8x smaller
OUTNAME = sys.argv[4] if len(sys.argv) > 4 else 'mirror-sphere-room.png'
img = np.asarray(Image.open(pic).convert('RGB'), np.float32)
IH, IW = img.shape[:2]
FOV = math.radians(84)                         # horizontal field of view of the picture
f = (IW / 2) / math.tan(FOV / 2)

SS = 3; N = D * SS
y, x = np.mgrid[0:N, 0:N].astype(np.float32)
x = (x + .5) / N * 2 - 1; y = (y + .5) / N * 2 - 1
rho = np.sqrt(x * x + y * y); inside = rho <= 1
psi = 2 * np.arcsin(np.clip(rho, 0, 1))        # reflected angle from the axis
phi = np.arctan2(y, x)
# fisheye-like: picture fills the middle, its mirrored surroundings squeeze toward the rim
A = (IW / 2) / .78 / SCALE
r = A * rho * (1 + .9 * rho ** 8)
px = IW / 2 + r * np.cos(phi)
py = IH / 2 + r * np.sin(phi) * 1.0


def mirror_coord(c, n):                        # reflect out-of-range coords back into the picture
    p = 2 * (n - 1)
    c = np.mod(c, p)
    return np.where(c > n - 1, p - c, c)


inpic = (px >= 0) & (px <= IW - 1) & (py >= 0) & (py <= IH - 1)
# soft border of the picture (in picture pixels)
edge = np.minimum.reduce([px, IW - 1 - px, py, IH - 1 - py])
wpic = np.clip(edge / 6.0, 0, 1)[..., None] if SCALE < 1 else np.ones_like(px)[..., None]
if SCALE >= 1:
    px = mirror_coord(px, IW); py = mirror_coord(py, IH)
pxc = np.clip(px, 0, IW - 1.001); pyc = np.clip(py, 0, IH - 1.001)
x0 = np.clip(np.floor(pxc).astype(int), 0, IW - 2); y0 = np.clip(np.floor(pyc).astype(int), 0, IH - 2)
fx = (pxc - x0)[..., None]; fy = (pyc - y0)[..., None]
col = ((img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy)
       + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy)
if SCALE < 1:
    # plain chrome surroundings, by the reflected ray's height: light above, dark horizon, grey below
    zz = np.sqrt(np.clip(1 - rho * rho, 0, 1)); ry = 2 * zz * (-y)
    top, haze, dark, flo = (np.array(c, np.float32) for c in ([248, 248, 249], [205, 205, 209], [52, 52, 56], [150, 148, 152]))
    R = ry[..., None]
    studio = np.where(R > .05, haze + (top - haze) * np.clip((R - .05) / .8, 0, 1),
             np.where(R > -.05, dark, flo * (1 - .3 * np.clip((-R - .05) / .9, 0, 1))))
    col = col * wpic + studio * (1 - wpic)

# chrome: slightly darker and cooler than the scene, dark rim, soft specular
col = col * .92 * np.array([.97, .98, 1.02], np.float32)
rim = np.clip((rho - .74) / .26, 0, 1)[..., None]
col = col * (1 - .62 * rim ** 1.4)
spec = np.exp(-(((x + .36) ** 2 + (y + .42) ** 2) / .006))[..., None]
col = np.clip((col - 128) * 1.08 + 128 + 120 * spec, 0, 255)

im = Image.fromarray(col.astype(np.uint8)).resize((D, D), Image.LANCZOS)
a = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(a).ellipse([2, 2, D * 4 - 3, D * 4 - 3], fill=255)
im.putalpha(a.resize((D, D), Image.LANCZOS))
out = os.path.join(ROOT, 'cutouts', OUTNAME)
im.save(out)
print(out)
