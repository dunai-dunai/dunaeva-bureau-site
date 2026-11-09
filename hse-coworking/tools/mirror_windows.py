#!/usr/bin/env python3
"""Mirror wall that reflects only the windows, the wall and a strip of parquet (no furniture).

Starts from cutouts/mirror-wall/mirror-wall-flat.png (440 x 1120, straightened).
Above y=CUT the reflection is kept as is; below, it is rebuilt: windows continue down to the sill,
sill ledge, plain wall, baseboard, then herringbone parquet (from the user's own board) in perspective.
Outputs mirror-wall-windows-flat.png, mirror-wall-windows.png (back in the render's perspective), PSD.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'cutouts', 'mirror-wall')
flat = Image.open(os.path.join(D, 'mirror-wall-flat.png')).convert('RGB')
a = np.asarray(flat, np.float32).copy()
H, W = a.shape[:2]
CUT, SILL, BASE = 696, 778, 842

# panel joints: darkest columns in the clean upper part
prof = a[20:220].mean(2).mean(0)
joints = [x for x in range(4, W - 4) if prof[x] < prof[max(0, x - 6):x + 7].mean() - 12]
joints = sorted(set(joints))

# 1) windows/piers continue to the sill: stretch rows CUT-40..CUT downward
band = a[CUT - 50:CUT - 10]
rows = np.linspace(0, band.shape[0] - 1, SILL - CUT).astype(int)
stretched = band[rows]
fade = np.clip(np.arange(SILL - CUT, dtype=np.float32) / 24, 0, 1)[:, None, None]
orig = a[CUT:SILL].copy()
a[CUT:SILL] = stretched * fade + band[-1:] * (1 - fade)
# 2) sill ledge
a[SILL:SILL + 7] = np.array([238, 233, 226], np.float32)
a[SILL + 7:SILL + 11] = np.array([206, 198, 188], np.float32)
# 3) wall below the sill: colour of the piers
pier = np.median(a[600:CUT, 165:195].reshape(-1, 3), 0)
g = np.linspace(1.0, .93, BASE - SILL - 11, dtype=np.float32)[:, None, None]
a[SILL + 11:BASE] = pier[None, None, :] * g
# baseboard
a[BASE:BASE + 10] = pier * .86
a[BASE + 10:BASE + 12] = pier * .72
# 4) parquet: herringbone from the user's board, laid in perspective (receding to the left)
# herringbone assembled from real planks cut out of the user's parquet photo
BOARD = Image.open(os.path.join(ROOT, 'source', '11-her-board.jpg')).convert('RGB')
HP = [(415, 917, 632, 947), (378, 955, 590, 985), (340, 993, 555, 1022), (300, 1030, 520, 1058), (490, 842, 676, 872)]
VP = [(450, 718, 483, 875), (376, 730, 408, 985)]
PL, PWD = 200, 36
planks = []
for bx0, by0, bx1, by1 in HP:
    planks.append(BOARD.crop((bx0, by0, bx1, by1)).resize((PL, PWD), Image.BICUBIC))
for bx0, by0, bx1, by1 in VP:
    planks.append(BOARD.crop((bx0, by0, bx1, by1)).rotate(90, expand=True).resize((PL, PWD), Image.BICUBIC))
pm = np.mean([np.asarray(p_, np.float32).reshape(-1, 3).mean(0) for p_ in planks], 0)
norm = []
for p_ in planks:
    q = np.asarray(p_, np.float32); q = q / q.reshape(-1, 3).mean(0) * pm
    q[:2] *= .8; q[-2:] *= .86; q[:, :2] *= .82; q[:, -2:] *= .86
    norm.append(Image.fromarray(np.clip(q, 0, 255).astype(np.uint8)))
rnd = np.random.default_rng(5)
SZ = 2400
hb = Image.new('RGB', (SZ, SZ))
for ia in range(-60, 60):
    for ib in range(-12, 12):
        ox_, oy_ = ia * PWD + ib * PL, ia * PWD - ib * PL + SZ // 2
        if -PL <= ox_ <= SZ and -PL <= oy_ <= SZ:
            p1 = norm[rnd.integers(len(norm))]; p1 = p1.transpose(Image.FLIP_LEFT_RIGHT) if rnd.random() < .5 else p1
            p2 = norm[rnd.integers(len(norm))].rotate(90, expand=True)
            hb.paste(p1, (ox_, oy_)); hb.paste(p2, (ox_, oy_ + PWD))
hb = hb.rotate(45, resample=Image.BICUBIC).crop((500, 500, SZ - 500, SZ - 500))
pq = hb
pw, ph = pq.size
F0 = BASE + 12
dst = [(-700, F0), (W + 80, F0), (W + 900, H + 700), (-2300, H + 700)]      # UL, UR, LR, LL


def persp_coeffs(src_pts, dst_pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64)).tolist()


co = persp_coeffs([(0, 0), (pw, 0), (pw, ph), (0, ph)], dst)
floor = np.asarray(pq.transform((W, H), Image.PERSPECTIVE, co, Image.BICUBIC), np.float32)
# match the reflection's tone: the mirror is slightly cooler/greyer and softer
ref_floor = np.array([186, 148, 112], np.float32)
floor = floor / np.maximum(floor[F0:].reshape(-1, 3).mean(0), 1) * ref_floor
floor = floor * .5 + np.asarray(Image.fromarray(np.clip(floor, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8)), np.float32) * .5
depth = np.linspace(.9, 1.0, H - F0, dtype=np.float32)[:, None, None]      # farther = a bit darker
a[F0:] = floor[F0:] * depth
# soft contact shadow under the baseboard
for k in range(10):
    a[F0 + k] *= .82 + .018 * k
# light haze on the rebuilt part so it sits in the same glass
haze = np.array([238, 234, 230], np.float32)
rh = np.clip((np.arange(H - CUT, dtype=np.float32) - 0) / 80, 0, 1)[:, None, None] * .06
a[CUT:] = a[CUT:] * (1 - rh) + haze * rh
# soften the seam at CUT
for k in range(8):
    t = (k + 1) / 9
    a[CUT - 4 + k] = a[CUT - 4 + k] * t + a[CUT - 5] * (1 - t) if k < 4 else a[CUT - 4 + k]
# redraw the panel joints over the rebuilt area
clusters = []
for x in joints:
    if clusters and x - clusters[-1][-1] <= 2: clusters[-1].append(x)
    else: clusters.append([x])
for cl in clusters:
    lo, hi = cl[0] - 1, cl[-1] + 1
    for x in range(lo, hi + 1):                       # erase the original joint over the full height
        t = (x - lo + 1) / (hi - lo + 2)
        a[:, x] = a[:, lo - 2] * (1 - t) + a[:, hi + 2] * t
    core = (cl[0] + cl[-1]) // 2                      # redraw one even joint line, top to bottom
    a[:, core] *= .58
    a[:, core + 1] *= .86
out_flat = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
out_flat.save(os.path.join(D, 'mirror-wall-windows-flat.png'))

# back into the render's perspective, same placement as mirror-wall.png
quad = [(1142, 148), (1354, 146), (1344, 688), (1142, 691)]
bx, by = 1139, 144
qq = [(x - bx, y - by) for x, y in quad]
Wp, Hp = 218, 550
S = 4
co2 = persp_coeffs([(0, 0), (W, 0), (W, H), (0, H)], [(x * S, y * S) for x, y in qq])
big = out_flat.transform((Wp * S, Hp * S), Image.PERSPECTIVE, co2, Image.BICUBIC)
m = Image.new('L', (Wp * S, Hp * S), 0); ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in qq], fill=255)
big = big.convert('RGBA'); big.putalpha(m)
big = big.resize((Wp, Hp), Image.LANCZOS)
big.save(os.path.join(D, 'mirror-wall-windows.png'))

from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
psd = PSDImage.new('RGB', out_flat.size)
L = PixelLayer.frompil(out_flat.convert('RGBA'), psd, 'l', top=0, left=0); psd.append(L); L.name = 'Зеркало — окна и паркет'
psd.save(os.path.join(D, 'mirror-wall-windows.psd'))
print('joints', joints)
