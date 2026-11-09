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

L_top = poly([(312, 737), (456, 613), (712, 642), (712, 651), (572, 766), (312, 748)])
L_frames = frame((313, 745), (441, 752), (441, 893), (313, 886), 11) | frame((443, 752), (574, 756), (574, 898), (443, 893), 11)
L_back = poly([(455, 790), (532, 794), (532, 803), (455, 799)]) | poly([(529, 760), (541, 760), (541, 803), (529, 803)])
L_div = poly([(446, 660), (555, 615), (626, 611), (626, 641), (555, 685), (446, 737)])

R_top = poly([(990, 648), (1190, 648), (1277, 790), (1277, 801), (985, 788), (985, 776)])
R_frames = frame((983, 775), (1123, 779), (1123, 942), (983, 930), 12) | frame((1125, 780), (1276, 790), (1272, 952), (1125, 942), 12)
R_back = poly([(1000, 822), (1100, 826), (1100, 840), (1000, 836)]) | poly([(1137, 790), (1262, 795), (1262, 805), (1137, 800)])
R_div = poly([(1086, 578), (1133, 660), (1133, 771), (1110, 756), (1086, 648)])


def soft(mask, grow=0, blur=.5):
    m = Image.fromarray((mask * 255).astype(np.uint8))
    if grow > 0: m = m.filter(ImageFilter.MaxFilter(2 * grow + 1))
    if grow < 0: m = m.filter(ImageFilter.MinFilter(-2 * grow + 1))
    if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255


# whiteness: 1 on white/grey frame paint, 0 on orange parquet and on dark gaps/casters
whiteness = np.clip((.26 - sat) / .10, 0, 1) * np.clip((lum - 85) / 30, 0, 1)
whiteness = np.asarray(Image.fromarray((whiteness * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3)), np.float32) / 255


def cut(top, frames, div, name):
    a_top = soft(top, grow=0, blur=.6)
    a_frame = soft(frames, grow=3, blur=0) * whiteness
    a_div = soft(div, grow=0, blur=.6)
    a = np.maximum.reduce([a_top, a_frame, a_div])
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.4)), np.float32)
    a[a < 14] = 0                                     # no faint haze around
    l = im.convert('RGBA'); l.putalpha(Image.fromarray(a.astype(np.uint8)))
    bb = l.getbbox(); l.crop(bb).save(os.path.join(OUT, name)); return bb


def grow(m, n):
    if n <= 0: return m.copy()
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * n + 1))) > 0


def masked_mean(img, m, rad):
    """local mean of img over pixels where m is set (box of radius rad)."""
    from_ = np.zeros(img.shape[:2] + (img.shape[2],), np.float64)
    num = np.stack([box_mean(img[..., k] * m, rad) for k in range(img.shape[2])], -1)
    den = box_mean(m.astype(np.float32), rad)[..., None]
    return num / np.maximum(den, 1e-4), den[..., 0]


def box_mean(a, rad):
    k = 2 * rad + 1
    p = np.pad(a, rad + 1, mode='edge').astype(np.float64)
    ii = p.cumsum(0).cumsum(1)
    s = ii[k:, k:] - ii[:-k, k:] - ii[k:, :-k] + ii[:-k, :-k]
    return (s / (k * k))[:a.shape[0], :a.shape[1]]


def remove_divider(rgb, top, div, shifts):
    out = rgb.copy()
    divg = grow(div, 2)
    D = divg & top
    clean = top & ~grow(div, 3)
    # local un-tint: ratio of walnut around to glass-covered walnut, per neighbourhood
    g_out, _ = masked_mean(rgb, clean, 28)
    g_in, _ = masked_mean(rgb, D, 14)
    gain = np.clip(g_out / np.maximum(g_in, 1), .6, 2.2)
    out[D] = np.clip(rgb[D] * gain[D], 0, 255)
    # anything in D that still is not walnut (glass edges, brackets, things behind the glass) is rebuilt
    ref, _ = masked_mean(rgb, clean, 18)
    dist = np.sqrt(((out - ref) ** 2).sum(2))
    l2 = out @ np.array([.3, .59, .11], np.float32)
    s2 = (out.max(2) - out.min(2)) / np.maximum(out.max(2), 1)
    bad = D & ((dist > 42) | (s2 < .25) | (l2 < 45))
    bad = grow(bad, 2) & D
    # fill: walnut texture copied from nearby clean walnut (first shift that lands on clean wood),
    # brightness matched to the local neighbourhood
    filled = out.copy(); done = ~bad
    for dx, dy in shifts:
        src = np.roll(np.roll(out, -dy, 0), -dx, 1)
        ok = np.roll(np.roll(clean, -dy, 0), -dx, 1)
        take = bad & ~done & ok
        filled[take] = src[take]; done |= take
    # whatever is still missing: diffuse from neighbours
    known = done.copy()
    for _ in range(80):
        if known.all() or not (bad & ~known).any(): break
        acc = np.zeros_like(filled); cnt = np.zeros(known.shape, np.float32)
        for ddy in (-1, 0, 1):
            for ddx in (-1, 0, 1):
                if ddx == ddy == 0: continue
                k = np.roll(np.roll(known, ddy, 0), ddx, 1)
                acc += np.roll(np.roll(filled, ddy, 0), ddx, 1) * k[..., None]; cnt += k
        new = bad & ~known & (cnt > 0)
        filled[new] = acc[new] / cnt[new][:, None]; known |= new
    # match local brightness of the rebuilt part, then soften the seam
    m_f, _ = masked_mean(filled, bad, 10)
    m_c, _ = masked_mean(filled, clean | (D & ~bad), 22)
    filled[bad] = np.clip(filled[bad] * (m_c[bad] / np.maximum(m_f[bad], 1)), 0, 255)
    blur = np.asarray(Image.fromarray(filled.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
    edge = grow(bad, 2) & ~bad
    filled[edge] = filled[edge] * .5 + blur[edge] * .5
    return filled


def cut_rgb(rgb, top, frames, name):
    a_top = soft(top, grow=0, blur=.6)
    a_frame = soft(frames, grow=3, blur=0) * whiteness
    a = np.maximum(a_top, a_frame)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.4)), np.float32)
    a[a < 14] = 0
    l = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); l.putalpha(Image.fromarray(a.astype(np.uint8)))
    l.crop(l.getbbox()).save(os.path.join(OUT, name))


# ---- dividers removed in a rectified (top-down) view of each table top, where the grain is straight
def persp_coeffs(src_pts, dst_pts):
    """coefficients for Image.transform(PERSPECTIVE): maps output point (in dst) -> input point (in src)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64)).tolist()


def rectify(quad, size):
    ul, ll, lr, ur = quad
    return im.transform(size, Image.QUAD, (*ul, *ll, *lr, *ur), Image.BICUBIC)


def unrectify(rect, quad):
    w, h = rect.size
    ul, ll, lr, ur = quad
    co = persp_coeffs([(0, 0), (0, h), (w, h), (w, 0)], [ul, ll, lr, ur])
    return rect.transform((W, H), Image.PERSPECTIVE, co, Image.BICUBIC)


def mirror_cols(n, start, end):
    """index map for mirror-tiling the column range [start, end) across n columns."""
    period = end - start
    idx = np.arange(n) - start
    k = np.mod(idx, 2 * period)
    return start + np.where(k < period, k, 2 * period - 1 - k)


def fix_left():
    quad = [(456, 613), (312, 737), (572, 756), (712, 642)]
    w, h = 520, 220
    r = np.asarray(rectify(quad, (w, h)), np.float32).copy()
    src0, src1 = 372, 496                     # clean walnut, grain runs along the rows
    cols = mirror_cols(w, src0, src1)
    out = r.copy()
    out[:, :src0] = r[:, cols[:src0]]
    # the join between the two tables (vertical) and between back/front tables (horizontal) stay visible
    out[:, 248:250] *= .78
    for (x0, y0, x1, y1) in ((372, 0, 400, 30),):
        out[y0:y1, x0:x1] = r[y0:y1, x0 + 40:x1 + 40]
    out[:16] = out[16:32][::-1]                           # back rim: no dark remnants from behind the table
    return quad, Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def fix_right():
    quad = [(990, 648), (985, 778), (1277, 790), (1190, 648)]
    w, h = 400, 300
    r = np.asarray(rectify(quad, (w, h)), np.float32).copy()
    out = r.copy()
    band0, band1 = 172, 266                   # divider + brackets (grain runs along the columns)
    FE = 270                                  # rows below are the front edge (thickness) of the top
    src = np.arange(band0 - (band1 - band0), band0)
    out[:FE, band0:band1] = r[:FE, src]
    # match brightness of the inserted planks to their right-hand neighbours, row by row
    gl = r[:FE, band1:band1 + 12].mean(1, keepdims=True) / np.maximum(r[:FE, src[-12:]].mean(1, keepdims=True), 1)
    ramp = np.linspace(0, 1, band1 - band0, dtype=np.float32)[None, :, None]
    out[:FE, band0:band1] *= (1 + (gl - 1) * ramp)
    # soft seams on both sides of the insert
    for x in range(6):
        t = (x + 1) / 7
        out[:FE, band0 + x] = out[:FE, band0 + x] * t + r[:FE, band0 + x - 7] * 0 + out[:FE, band0 - 1] * (1 - t) if False else out[:FE, band0 + x]
        out[:FE, band1 - 1 - x] = out[:FE, band1 - 1 - x] * t + r[:FE, band1 + 1] * (1 - t) * 0 + out[:FE, band1 - 1 - x] * (1 - t)
    out[:FE, 196:198] *= .82                  # centre join between the two desks
    # front edge: only the divider's black foot line needs replacing
    out[FE:, 186:206] = r[FE:, 166:186]
    out[FE:, 196:198] *= .8
    return quad, Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def build(side, top, frames, fixer):
    quad, rect = fixer()
    warped = np.asarray(unrectify(rect, quad).convert('RGB'), np.float32)
    qmask = poly([quad[0], quad[3], quad[2], quad[1]])
    rgb = c.copy()
    inner = qmask & ~grow(~qmask, 2)
    rgb[inner] = warped[inner]
    band = top & ~qmask & grow(div_of[side], 4)
    if band.any():
        ys, xs = np.nonzero(band)
        rgb[ys, xs] = c[ys, np.clip(xs + 70, 0, W - 1)]
    top_full = top | qmask
    cut_rgb(rgb, top_full, frames, f'desk-{side}.png')


div_of = {'left': L_div, 'right': R_div}
for side, top, frames, div, fixer in (('left', L_top, L_frames, L_div, fix_left), ('right', R_top, R_frames, R_div, fix_right)):
    cut(top, frames, div, f'desk-{side}-with-divider.png')
    build(side, top, frames, fixer)

# check on a neutral background
sheet = Image.new('RGB', (760, 420), (236, 230, 221))
x = 20
for f in ('desk-left.png', 'desk-right.png'):
    p = Image.open(os.path.join(OUT, f)); sheet.paste(p, (x, 20), p); x += p.width + 20
sheet.save(os.path.join(OUT, 'check.jpg'), quality=90)
print('ok')
