#!/usr/bin/env python3
"""Chrome sphere that reflects our own interior (stucco ceiling, oak herringbone,
lilac glass), rendered by true mirror reflection of an environment built from
source/02-workspace-draft.webp. Output: cutouts/mirror-sphere-interior.png
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S2 = Image.open(os.path.join(ROOT, 'source', '02-workspace-draft.webp')).convert('RGB')
S3 = Image.open(os.path.join(ROOT, 'source', '03-reception-draft.webp')).convert('RGB')
EW, EH = 4096, 2048


def strip(img, box, h, w=EW, mirror=True):
    """Tile a crop across the full width, alternating mirrored copies (no visible repeats)."""
    c = img.crop(box); c = c.resize((int(c.width * h / c.height), h), Image.LANCZOS)
    out = Image.new('RGB', (w, h)); x = 0; k = 0
    while x < w:
        t = c.transpose(Image.FLIP_LEFT_RIGHT) if (mirror and k % 2) else c
        out.paste(t, (x, 0)); x += c.width; k += 1
    return out


def row_lat(lat):
    return int((.5 - lat / 180) * EH)


ceil_h = row_lat(28)
wall_h = row_lat(-8) - ceil_h
floor_h = EH - row_lat(-8)
ceiling = strip(S3, (60, 0, 1030, 240), ceil_h)                     # stucco, rosette
# wall band: lilac glass booths | white window wall | lilac reception glass | white panels
segs = [S2.crop((520, 130, 1110, 495)), S2.crop((1130, 110, 1536, 500)),
        S3.crop((100, 380, 230, 1000)), S3.crop((870, 380, 1000, 1000)), S2.crop((540, 150, 1000, 520)), S2.crop((1130, 110, 1536, 500))]
wall = Image.new('RGB', (EW, wall_h)); x = 0; k = 0
while x < EW:
    c = segs[k % len(segs)]; c = c.resize((int(c.width * wall_h / c.height), wall_h), Image.LANCZOS)
    if k % 2: c = c.transpose(Image.FLIP_LEFT_RIGHT)
    wall.paste(c, (x, 0)); x += c.width; k += 1
floor = strip(S3, (0, 1260, 1086, 1448), floor_h)                   # warm herringbone in sun
env_im = Image.new('RGB', (EW, EH)); env_im.paste(ceiling, (0, 0)); env_im.paste(wall, (0, ceil_h)); env_im.paste(floor, (0, ceil_h + wall_h))
env = np.asarray(env_im, np.float32).copy()
# keep tile joints of ceiling/floor away from the ball's vertical axis
env[:ceil_h] = np.roll(env[:ceil_h], 311, 1)
env[ceil_h + wall_h:] = np.roll(env[ceil_h + wall_h:], 523, 1)
# soften the two seams between bands
for yb in (ceil_h, ceil_h + wall_h):
    band = env[yb - 24:yb + 24].copy()
    env[yb - 24:yb + 24] = np.asarray(Image.fromarray(band.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32)
# the viewer's side (centre of the ball) is darker — the photographer and the room behind
lonc = np.linspace(-math.pi, math.pi, EW, dtype=np.float32)
behind = np.exp(-((lonc) / .55) ** 2)
env = env * (1 - .45 * behind[None, :, None])
EH, EW = env.shape[:2]

D = 1400                                           # sphere diameter, px (≈12 cm at 300 dpi)
SS = 2
N = D * SS
y, x = np.mgrid[0:N, 0:N].astype(np.float32)
x = (x + .5) / N * 2 - 1
y = (y + .5) / N * 2 - 1
rr = x * x + y * y
inside = rr <= 1
z = np.sqrt(np.clip(1 - rr, 0, 1))
nx, ny, nz = x, -y, z
# view along -z; reflected ray r = v - 2(n·v)n, v = (0,0,-1)
rx, ry, rz = 2 * nz * nx, 2 * nz * ny, -1 + 2 * nz * nz
lon = np.arctan2(rx, -rz)                          # 0 = the room behind the sphere
lat = np.arcsin(np.clip(ry, -1, 1))
u = ((lon / (2 * math.pi)) % 1.0) * (EW - 1)   # sphere centre -> middle of the env, seam hides at the rim
v = (.5 - lat / math.pi) * (EH - 1)


def bilinear(img, u, v):
    u0 = np.clip(np.floor(u).astype(int), 0, img.shape[1] - 2); v0 = np.clip(np.floor(v).astype(int), 0, img.shape[0] - 2)
    fu = (u - u0)[..., None]; fv = (v - v0)[..., None]
    a = img[v0, u0]; b = img[v0, u0 + 1]; c = img[v0 + 1, u0]; d = img[v0 + 1, u0 + 1]
    return (a * (1 - fu) + b * fu) * (1 - fv) + (c * (1 - fu) + d * fu) * fv


col = bilinear(env, u, v)
# chrome is not a perfect mirror: a little darker and cooler, rim darkens (grazing angle)
col = col * .90 * np.array([.97, .98, 1.02], np.float32)
rim = np.clip((rr - .80) / .20, 0, 1)[..., None]
col = col * (1 - .45 * rim ** 1.6)
# window highlight: soft hot spot upper-left
hl = np.exp(-(((x + .38) ** 2 + (y + .40) ** 2) / .012))[..., None]
col = col + 110 * hl
col = np.clip((col - 128) * 1.12 + 128, 0, 255)

alpha = (inside * 255).astype(np.uint8)
im = Image.fromarray(col.astype(np.uint8)); im.putalpha(Image.fromarray(alpha))
im = im.resize((D, D), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 40, 2))
a = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(a).ellipse([2, 2, D * 4 - 3, D * 4 - 3], fill=255)
im.putalpha(a.resize((D, D), Image.LANCZOS))
out = os.path.join(ROOT, 'cutouts', 'mirror-sphere-interior.png')
im.save(out)
print(out)
