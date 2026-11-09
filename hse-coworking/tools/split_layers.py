#!/usr/bin/env python3
"""Split the workspace render (source/12-workspace.webp) into Photoshop layers.

Geometry (walls, glass, mirror, desk tops) is cut with polygons; chairs and
desk frames by colour (white, smooth) and casters by darkness. The full render
stays as the bottom layer, so nothing is lost if a mask needs touching up.
Output: layers/workspace-layers.psd and layers/workspace/*.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', '12-workspace.webp')
OUT = os.path.join(ROOT, 'layers'); PNG = os.path.join(OUT, 'workspace'); os.makedirs(PNG, exist_ok=True)
im = Image.open(SRC).convert('RGB'); W, H = im.size
c = np.asarray(im, np.float32)
r, g, b = c[..., 0], c[..., 1], c[..., 2]
lum = .3 * r + .59 * g + .11 * b
mx, mn = c.max(2), c.min(2); sat = (mx - mn) / np.maximum(mx, 1)
yy, xx = np.mgrid[0:H, 0:W]


def poly(*pts):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return np.asarray(m) > 0


def box(x0, y0, x1, y1):
    return (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)


def box_mean(a, rad):
    k = 2 * rad + 1
    p = np.pad(a, rad + 1, mode='edge').astype(np.float64)
    ii = p.cumsum(0).cumsum(1)
    s = ii[k:, k:] - ii[:-k, k:] - ii[k:, :-k] + ii[:-k, :-k]
    return (s / (k * k))[:a.shape[0], :a.shape[1]]


def local_std(a, rad=3):
    m1 = box_mean(a, rad); m2 = box_mean(a * a, rad)
    return np.sqrt(np.clip(m2 - m1 * m1, 0, None)).astype(np.float32)


std = local_std(lum)

# --- geometry
mosaic = poly((36, 0), (330, 0), (488, 92), (488, 642), (68, 782), (38, 772))
ceiling = poly((330, 0), (1475, 0), (1475, 98), (1355, 140), (1120, 150), (1000, 103), (560, 118), (508, 172), (488, 92))
mirror = poly((1138, 140), (1356, 140), (1356, 692), (1138, 692))
glass = poly((508, 175), (560, 118), (1000, 103), (1120, 150), (1120, 602), (1005, 602), (995, 652), (830, 668), (800, 692),
             (560, 692), (508, 642))
floor = poly((40, 792), (488, 645), (560, 694), (800, 694), (830, 670), (995, 655), (1100, 660), (1450, 692), (1536, 820),
             (1536, 1024), (0, 1024), (0, 800))
mfp = box(1013, 565, 1096, 650)
tops = poly((455, 625), (712, 642), (712, 651), (572, 765), (312, 747), (312, 737)) | \
       poly((990, 648), (1190, 648), (1277, 790), (1277, 800), (985, 788), (985, 776))
dividers = poly((446, 660), (555, 615), (626, 611), (626, 641), (555, 685), (446, 737)) | \
           poly((1086, 578), (1133, 660), (1133, 771), (1110, 756), (1086, 648))

# --- booth chairs (zebra): warm beige stripes + black, inside their boxes, not the black booth desks
chair_boxes = box(558, 545, 632, 642) | box(663, 545, 748, 652) | box(828, 546, 914, 670)
booth_desks = box(600, 563, 668, 642) | box(745, 563, 810, 688) | box(916, 568, 988, 652)
beige = (r - b > 35) & (r > 120) & (g > 90)
dark = lum < 70
booth_chairs = chair_boxes & (beige | (dark & ~booth_desks))
booth_chairs = np.asarray(Image.fromarray((booth_chairs * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))) > 0

# --- white furniture (chairs + desk frames): white/grey, smooth; casters: very dark
zones = box(255, 586, 762, 906) | box(878, 600, 1385, 955) | box(1195, 600, 1300, 730)
white = (sat < .14) & (lum > 105) & (std < 14) & ~mosaic & ~mirror
casters = (lum < 60) & (yy > 760)
# two chairs stand in front of the mosaic: there a smooth white test, ignoring the mosaic polygon
front_of_mosaic = box(255, 586, 410, 862) | box(396, 586, 492, 700)
white_fm = (sat < .12) & (lum > 120) & (std < 9)
furniture_white = (zones & (white | casters) & ~tops & ~dividers) | (front_of_mosaic & (white_fm | casters))
fw = Image.fromarray((furniture_white * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))
fw = fw.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
furniture_white = np.asarray(fw) > 0

# keep layers mutually sensible
furniture_any = furniture_white | tops | dividers | mfp
floor_only = floor & ~furniture_any
glass_only = glass & ~booth_chairs & ~mfp & ~dividers
mosaic_only = mosaic & ~furniture_any

LAYERS = [   # bottom → top
    ('Оболочка — весь рендер', np.ones((H, W), bool)),
    ('Пол — паркет', floor_only),
    ('Потолок и лепнина', ceiling),
    ('Панно — мозаика', mosaic_only),
    ('Зеркальный шкаф', mirror & ~furniture_any),
    ('Стеклянные кабины', glass_only),
    ('Кресла в кабинах (зебра)', booth_chairs),
    ('МФУ', mfp),
    ('Столешницы', tops),
    ('Перегородки на столах', dividers),
    ('Кресла и опоры столов', furniture_white),
]


def to_layer(mask, feather=.7):
    a = Image.fromarray((mask * 255).astype(np.uint8))
    if feather: a = a.filter(ImageFilter.GaussianBlur(feather))
    l = im.copy().convert('RGBA'); l.putalpha(a); return l


if __name__ == '__main__':
    from psd_tools import PSDImage
    from psd_tools.api.layers import PixelLayer
    psd = PSDImage.new('RGB', (W, H))
    for i, (name, m) in enumerate(LAYERS):
        L = to_layer(m, feather=0 if i == 0 else .7)
        L.save(os.path.join(PNG, f'{i:02d} {name}.png'))
        bb = L.getbbox()
        part = L.crop(bb)
        layer = PixelLayer.frompil(part, psd, f'layer{i}', top=bb[1], left=bb[0])
        psd.append(layer)
        layer.name = name
    psd.save(os.path.join(OUT, 'workspace-layers.psd'))
    # check sheet: each layer tinted over a dim render
    sheet = Image.new('RGB', (W * 3 // 2, H * 4 // 2 + 40), 'white')
    for i, (name, m) in enumerate(LAYERS[1:]):
        base = (c * .25).astype(np.uint8)
        base[m] = c[m].astype(np.uint8)
        t = Image.fromarray(base).resize((W // 2, H // 2))
        sheet.paste(t, ((i % 3) * W // 2, (i // 3) * H // 2))
    sheet.save(os.path.join(OUT, 'workspace-layers-check.jpg'), quality=85)
    print('ok')
