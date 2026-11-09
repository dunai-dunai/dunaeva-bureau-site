#!/usr/bin/env python3
"""Chrome sphere that reflects our own interior (stucco ceiling, oak herringbone,
lilac glass), rendered by true mirror reflection of an environment built from
source/02-workspace-draft.webp. Output: cutouts/mirror-sphere-small.png
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


# studio for chrome: bright above, crisp dark horizon, dark floor, a couple of bright windows
lat_rows = 90 - np.linspace(0, 180, EH, dtype=np.float32)
L = lat_rows[:, None, None]
sky = np.array([250, 250, 250], np.float32); haze = np.array([214, 214, 218], np.float32)
dark = np.array([40, 40, 44], np.float32); floor = np.array([168, 166, 170], np.float32)
env = np.where(L > 3, haze + (sky - haze) * np.clip((L - 3) / 60, 0, 1),
      np.where(L > -3, dark, floor * (1 - .35 * np.clip((-L - 3) / 80, 0, 1))))
env = np.broadcast_to(env, (EH, EW, 3)).copy()


def lonlat_box(lon0, lon1, lat0, lat1):          # lon 0..360, 180 = straight back at the viewer
    return int(lon0 / 360 * EW), row_lat(lat1), int(lon1 / 360 * EW), row_lat(lat0)


def put(img, box, lon0, lon1, lat0, lat1, feather=6, color=None):
    x0, y0, x1, y1 = lonlat_box(lon0, lon1, lat0, lat1)
    if color is not None:
        c = np.broadcast_to(np.array(color, np.float32), (y1 - y0, x1 - x0, 3))
    else:
        c = np.asarray(img.crop(box).convert('RGB').resize((x1 - x0, y1 - y0), Image.LANCZOS), np.float32)
    m = Image.new('L', (x1 - x0, y1 - y0), 0); ImageDraw.Draw(m).rectangle([feather, feather, x1 - x0 - feather, y1 - y0 - feather], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(feather / 2)), np.float32)[..., None] / 255
    env[y0:y1, x0:x1] = env[y0:y1, x0:x1] * (1 - m) + c * m


G = Image.open(os.path.join(ROOT, 'source', '08-lilac-glass.jpg'))
put(None, None, 60, 80, 20, 48, color=(255, 255, 255))         # window
put(None, None, 280, 296, 18, 44, color=(255, 255, 255))       # window
put(S3, (60, 0, 760, 240), 120, 215, 22, 72)                   # stucco ornament, wraps over the top
put(G, (440, 260, 735, 800), 190, 262, -30, 26)                # lilac glass panels, right side
EH, EW = env.shape[:2]

D = 520                                           # sphere diameter, px (≈12 cm at 300 dpi)
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
u = ((lon / (2 * math.pi)) % 1.0) * (EW - 1)
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

col = np.clip((col - 128) * 1.12 + 128, 0, 255)

alpha = (inside * 255).astype(np.uint8)
im = Image.fromarray(col.astype(np.uint8)); im.putalpha(Image.fromarray(alpha))
im = im.resize((D, D), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 40, 2))
a = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(a).ellipse([2, 2, D * 4 - 3, D * 4 - 3], fill=255)
im.putalpha(a.resize((D, D), Image.LANCZOS))
out = os.path.join(ROOT, 'cutouts', 'mirror-sphere-small.png')
im.save(out)
print(out)
