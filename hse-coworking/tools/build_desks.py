#!/usr/bin/env python3
"""Clean coworking desks built from geometry (no render artefacts, no sun patches).

A bench of 4 tables (2 x 2, 1400 x 700 mm each, top 25 mm, height 740 mm) on white O-frames,
walnut veneer from the user's own board (source/11-her-board.jpg), evened out (no light gradients).
Rendered with even studio light, 4x supersampling for crisp edges.
Outputs cutouts/desks-clean/: desk-front.png, desk-angle.png (+ soft floor shadow layers).
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cutouts', 'desks-clean'); os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- walnut texture (even, tileable-ish)
src = Image.open(os.path.join(ROOT, 'source', '11-her-board.jpg')).convert('RGB').crop((1262, 740, 1450, 965))
a = np.asarray(src, np.float32)
low = np.asarray(src.filter(ImageFilter.GaussianBlur(30)), np.float32)
a = a / np.maximum(low, 1) * a.reshape(-1, 3).mean(0)          # remove light gradient, keep grain
a = (a - a.mean((0, 1))) * .9 + np.array([132, 86, 58], np.float32)   # walnut tone
tile = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).rotate(90, expand=True)   # grain along length
tw, th = tile.size
# mirror-tile to a long plank texture
row = Image.new('RGB', (tw * 4, th))
for k in range(4):
    row.paste(tile if k % 2 == 0 else tile.transpose(Image.FLIP_LEFT_RIGHT), (k * tw, 0))
WALNUT = Image.new('RGB', (tw * 4, th * 2))
WALNUT.paste(row, (0, 0)); WALNUT.paste(row.transpose(Image.FLIP_TOP_BOTTOM), (0, th))
WALNUT = WALNUT.resize((2400, 1200), Image.BICUBIC)

WHITE = np.array([242, 240, 236], np.float32)
EDGE_WOOD = np.array([98, 62, 40], np.float32)

# ---------------------------------------------------------------- scene (mm): x along bench, y depth, z up
# bench like in the render: two rows of two tables, long side going away from the viewer.
# x across (2 x 700 = 1400), y along the length (2 x 1400 = 2800); white O-frames at the table ends.
TW, TL, TT, HT = 700, 1400, 25, 740
BAR = 45
tops, frames = [], []
for i in range(2):
    for j in range(2):
        tops.append((i * TW, j * TL, HT - TT, (i + 1) * TW, (j + 1) * TL, HT))
for i in range(2):
    x0, x1 = i * TW + 30, (i + 1) * TW - 30
    for yc in (70, TL, 2 * TL - 70):
        y0, y1 = yc - BAR / 2, yc + BAR / 2
        zt = HT - TT
        frames += [(x0, y0, zt - BAR, x1, y1, zt),          # top rail
                   (x0, y0, 0, x1, y1, BAR),                 # foot
                   (x0, y0, 0, x0 + BAR, y1, zt),            # left post
                   (x1 - BAR, y0, 0, x1, y1, zt)]            # right post
    # long beam under the top joining the frames (as on real bench desks)
    xm = (x0 + x1) / 2
    frames.append((xm - 20, 70, zt - 60, xm + 20, 2 * TL - 70, zt))
WALNUT = WALNUT.rotate(90, expand=True)          # grain along the table length (y)


def camera(yaw_deg, pitch_deg, dist, target=(TW, TL, 380), f=2600):
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    tx, ty, tz = target

    def proj(p):
        x, y, z = p[0] - tx, p[1] - ty, p[2] - tz
        # yaw around z
        x, y = x * math.cos(yaw) - y * math.sin(yaw), x * math.sin(yaw) + y * math.cos(yaw)
        # camera looks along +y, tilted down by pitch
        y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
        y += dist
        return (f * x / y, -f * z / y, y)
    return proj


def box_faces(b):
    x0, y0, z0, x1, y1, z1 = b
    P = lambda x, y, z: (x, y, z)
    return {
        'top': [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)],
        'front': [P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)],
        'back': [P(x1, y1, z0), P(x0, y1, z0), P(x0, y1, z1), P(x1, y1, z1)],
        'left': [P(x0, y1, z0), P(x0, y0, z0), P(x0, y0, z1), P(x0, y1, z1)],
        'right': [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)],
        'bottom': [P(x0, y1, z0), P(x1, y1, z0), P(x1, y0, z0), P(x0, y0, z0)],
    }


LIGHT = {'top': 1.0, 'front': .86, 'left': .78, 'right': .74, 'back': .7, 'bottom': .6}


def persp_coeffs(src_pts, dst_pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64)).tolist()


def render(name, yaw, pitch, dist, SS=4, pad=60):
    proj = camera(yaw, pitch, dist)
    # bounds
    pts = [proj(p)[:2] for b in tops + frames for fc in box_faces(b).values() for p in fc]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    ox, oy = min(xs) - pad, min(ys) - pad
    Wd, Hd = int(max(xs) - ox + pad), int(max(ys) - oy + pad)
    W, H = Wd * SS, Hd * SS
    canvas = np.zeros((H, W, 4), np.float32)
    zbuf = np.full((H, W), np.inf, np.float32)
    texcache = {}

    def to2d(p):
        q = proj(p); return ((q[0] - ox) * SS, (q[1] - oy) * SS), q[2]

    def visible(poly2):
        (x0, y0), (x1, y1), (x2, y2) = poly2[0], poly2[1], poly2[2]
        return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0) < 0

    def raster(poly2, depths, rgb):
        xs_ = [p[0] for p in poly2]; ys_ = [p[1] for p in poly2]
        bx0, by0 = max(int(min(xs_)) - 1, 0), max(int(min(ys_)) - 1, 0)
        bx1, by1 = min(int(max(xs_)) + 2, W), min(int(max(ys_)) + 2, H)
        if bx1 <= bx0 or by1 <= by0: return
        m = Image.new('L', (bx1 - bx0, by1 - by0), 0)
        ImageDraw.Draw(m).polygon([(x - bx0, y - by0) for x, y in poly2], fill=255)
        m = np.asarray(m) > 0
        # 1/depth is affine in screen space for a planar face
        A = np.array([[poly2[k][0], poly2[k][1], 1] for k in range(3)], np.float64)
        coef = np.linalg.solve(A, np.array([1 / depths[k] for k in range(3)]))
        yy_, xx_ = np.mgrid[by0:by1, bx0:bx1]
        z = 1 / (coef[0] * xx_ + coef[1] * yy_ + coef[2])
        zb = zbuf[by0:by1, bx0:bx1]
        win = m & (z < zb - .5)
        zb[win] = z[win]
        cv = canvas[by0:by1, bx0:bx1]
        col = rgb(bx0, by0, bx1, by1) if callable(rgb) else np.broadcast_to(np.array(rgb, np.float32), cv[..., :3].shape)
        cv[..., :3][win] = col[win]; cv[..., 3][win] = 255

    def draw_box(b, kind):
        for fname, fc in box_faces(b).items():
            p2 = [to2d(p) for p in fc]
            poly2 = [q[0] for q in p2]
            if not visible(poly2): continue
            depths = [q[1] for q in p2]
            k = LIGHT[fname]
            if kind == 'frame':
                rgb = WHITE * (.80 + .20 * k)
            elif fname == 'top':
                tw_, th_ = WALNUT.size
                co = persp_coeffs([(0, 0), (tw_, 0), (tw_, th_), (0, th_)], poly2)
                tex = np.asarray(WALNUT.transform((W, H), Image.PERSPECTIVE, co, Image.BICUBIC), np.float32)
                rgb = (lambda t: (lambda x0, y0, x1, y1: t[y0:y1, x0:x1]))(tex)
            else:
                rgb = EDGE_WOOD * k / .86
            raster(poly2, depths, rgb)

    for b in frames:
        draw_box(b, 'frame')
    for b in tops:
        draw_box(b, 'top')
    canvas = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(canvas)
    seam = (70, 44, 30, 255)
    for line in ([(TW, 0, HT), (TW, 2 * TL, HT)], [(0, TL, HT), (2 * TW, TL, HT)], [(TW, 0, HT - TT), (TW, 0, HT)]):
        d.line([to2d(p)[0] for p in line], fill=seam, width=max(1, int(1.2 * SS)))
    img = canvas.resize((Wd, Hd), Image.LANCZOS)
    img.save(os.path.join(OUT, f'{name}.png'))
    # soft floor shadow, separate layer (Multiply)
    sh = Image.new('L', (W, H), 0)
    fl = [to2d(p)[0] for p in [(-40, -40, 0), (2 * TW + 40, -40, 0), (2 * TW + 40, 2 * TL + 40, 0), (-40, 2 * TL + 40, 0)]]
    ImageDraw.Draw(sh).polygon(fl, fill=110)
    sh = sh.resize((Wd, Hd), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    shl = Image.new('RGBA', (Wd, Hd), (40, 30, 24, 0)); shl.putalpha(sh)
    shl.save(os.path.join(OUT, f'{name}-shadow.png'))
    return img


if __name__ == '__main__':
    views = [('desk-end', 0, 16, 5200), ('desk-angle-left', -32, 16, 5600), ('desk-angle-right', 32, 16, 5600)]
    imgs = [render(n, yaw=y, pitch=pt, dist=dd) for n, y, pt, dd in views]
    sheet = Image.new('RGB', (sum(i.width for i in imgs) + 20 * (len(imgs) + 1), max(i.height for i in imgs) + 40), (236, 230, 221))
    x = 20
    for (n, *_), im in zip(views, imgs):
        sh = Image.open(os.path.join(OUT, n + '-shadow.png'))
        sheet.paste((40, 30, 24), (x, 20), sh); sheet.paste(im, (x, 20), im); x += im.width + 20
    sheet.thumbnail((1800, 900)); sheet.save(os.path.join(OUT, 'check.jpg'), quality=90)
    print([i.size for i in imgs])
