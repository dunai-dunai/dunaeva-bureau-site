#!/usr/bin/env python3
"""Two layout suggestions built from the pieces of the board the user made (source/11-her-board.jpg).
Only a demonstration of arrangement: shapes, rotation, scale, overlaps, shadows.
Outputs board-layouts/layout-A.jpg, layout-B.jpg."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'board-layouts'); os.makedirs(OUT, exist_ok=True)
B = Image.open(os.path.join(ROOT, 'source', '11-her-board.jpg')).convert('RGB')
W, H = 2000, 1414

CROPS = {
    'mosaic': (395, 185, 712, 505), 'stucco': (824, 92, 1168, 508), 'crystal': (1174, 216, 1444, 508),
    'gold': (1450, 140, 1668, 444), 'marble': (1452, 450, 1758, 712), 'walnut': (1247, 722, 1460, 980),
    'teal': (1467, 787, 1676, 930), 'velvet': (1494, 990, 1756, 1238), 'pearl': (1146, 992, 1444, 1246),
    'cement': (803, 1056, 1067, 1320), 'parquet': (243, 720, 680, 1246),
}
GLASS = Image.open(os.path.join(ROOT, 'cutouts', 'glass-lilac.png')).convert('RGBA')
SPHERE = Image.open(os.path.join(ROOT, 'cutouts', 'mirror-sphere-room-hq.png')).convert('RGBA')


def shape_mask(w, h, kind, seed=0):
    r = random.Random(seed)
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    if kind == 'rect':
        d.rectangle([0, 0, w - 1, h - 1], fill=255)
    elif kind == 'arch':                                   # lunette: flat bottom, round top
        rad = w / 2
        d.rectangle([0, rad, w - 1, h - 1], fill=255); d.ellipse([0, 0, w - 1, 2 * rad], fill=255)
    elif kind in ('torn', 'rag'):
        amp, step = (16, 14) if kind == 'torn' else (6, 22)
        pts = []
        for (x0, y0, x1, y1) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
            n = max(2, int(math.dist((x0, y0), (x1, y1)) / step))
            for i in range(n):
                t = i / n; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
                nx, ny = (y1 - y0), -(x1 - x0); L = math.hypot(nx, ny) or 1
                dd = r.uniform(-amp, amp * .3) if i else 0
                pts.append((x + nx / L * dd, y + ny / L * dd))
        d.polygon(pts, fill=255)
    elif kind == 'blob':
        cx, cy = w / 2, h / 2; pts = []
        for k in range(48):
            a = k / 48 * 2 * math.pi
            rr = 1 + .16 * math.sin(3 * a + seed) + .08 * math.sin(5 * a + 1.3)
            pts.append((cx + math.cos(a) * w * .46 * rr, cy + math.sin(a) * h * .44 * rr))
        d.polygon(pts, fill=255); m = m.filter(ImageFilter.GaussianBlur(3)).point(lambda q: 255 if q > 128 else 0)
    elif kind == 'circle':
        d.ellipse([0, 0, w - 1, h - 1], fill=255)
    return m


def put(canvas, name, x, y, scale=1.0, rot=0, kind='rect', seed=0, shadow=.32, tint=(45, 35, 30)):
    if name == 'glass':
        im = GLASS.copy(); im = im.crop(im.getbbox())
    elif name == 'sphere':
        im = SPHERE.copy()
    else:
        im = B.crop(CROPS[name]).convert('RGBA')
        im.putalpha(shape_mask(im.width, im.height, kind, seed))
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = im.split()[3]
    pad = 60
    sh = Image.new('L', (im.width + pad * 2, im.height + pad * 2), 0); sh.paste(a, (pad + 12, pad + 18))
    sh = sh.filter(ImageFilter.GaussianBlur(18)).point(lambda q: int(q * shadow))
    shl = Image.new('RGBA', sh.size, tint + (0,)); shl.putalpha(sh)
    canvas.alpha_composite(shl, (int(x - pad), int(y - pad)))
    canvas.alpha_composite(im, (int(x), int(y)))


def board(items, fn):
    c = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    for it in items:
        put(c, **it)
    c.convert('RGB').save(os.path.join(OUT, fn), quality=90)


# A — floor → walls → furniture, left to right
A = [
    dict(name='parquet', x=150, y=330, scale=1.25),
    dict(name='cement', x=390, y=860, scale=1.15, rot=45),
    dict(name='stucco', x=760, y=230, scale=1.65, kind='torn', seed=2),
    dict(name='mosaic', x=600, y=110, scale=1.2, kind='arch'),
    dict(name='glass', x=980, y=600, scale=.42, shadow=.12, tint=(90, 60, 120)),
    dict(name='pearl', x=760, y=1000, scale=.95, rot=-4),
    dict(name='marble', x=1420, y=140, scale=1.35, rot=3),
    dict(name='crystal', x=1300, y=330, scale=.85, rot=-7),
    dict(name='walnut', x=1600, y=520, scale=1.0, rot=6),
    dict(name='velvet', x=1420, y=780, scale=1.45, kind='rag', seed=4),
    dict(name='gold', x=1330, y=640, scale=.75, rot=-3),
    dict(name='teal', x=1650, y=1020, scale=1.2, kind='blob', seed=1),
    dict(name='sphere', x=1520, y=860, scale=.08, shadow=.4),
]
# B — a gold diagonal from top-left to bottom-right; cool materials in the other corners
Bl = [
    dict(name='marble', x=1420, y=110, scale=1.5, rot=-3),
    dict(name='crystal', x=1660, y=300, scale=.8, rot=5),
    dict(name='cement', x=160, y=900, scale=1.2, rot=45),
    dict(name='parquet', x=430, y=760, scale=1.0, rot=-2),
    dict(name='mosaic', x=170, y=120, scale=1.45, kind='arch'),
    dict(name='stucco', x=640, y=180, scale=1.75, kind='torn', seed=5),
    dict(name='gold', x=980, y=560, scale=1.0, rot=4),
    dict(name='glass', x=1130, y=380, scale=.40, shadow=.12, tint=(90, 60, 120)),
    dict(name='walnut', x=1240, y=830, scale=.95, rot=-6),
    dict(name='velvet', x=1500, y=880, scale=1.45, kind='rag', seed=7),
    dict(name='pearl', x=980, y=1000, scale=.85, rot=3),
    dict(name='teal', x=1480, y=640, scale=1.1, kind='blob', seed=3),
    dict(name='sphere', x=1130, y=690, scale=.075, shadow=.4),
]

if __name__ == '__main__':
    board(A, 'layout-A.jpg'); board(Bl, 'layout-B.jpg'); print('ok')
