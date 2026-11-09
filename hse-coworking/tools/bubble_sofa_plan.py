#!/usr/bin/env python3
"""Plan (top view) of the curved bubble sofa from source/15-bubble-sofa.jpg as a CAD block, mm.
Built geometrically (curved plan wrapping toward the sitter, scalloped "bubble" edges), not traced:
overall size is an assumption (about 2400 x 1150), adjust LENGTH / DEPTH and re-run.
"""
import os, math
import numpy as np
import ezdxf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cad'); os.makedirs(OUT, exist_ok=True)

DEPTH = 1150          # back of the back cushions to the front of the seat
BACK_T = 380          # back cushion depth
ARM_T = 300           # arm width (at the ends)
RI = 4200             # radius of the front edge (sofa wraps around a centre in front of it)
RO = RI + DEPTH
SPAN = math.radians(23)   # angle of the curved body (without the round ends)
C = np.array([0.0, -RI])  # centre of curvature (in front of the sofa)


def P(r, a):
    return C + r * np.array([math.sin(a), math.cos(a)])


def scallop(r0, a0, a1, n, amp, outward=True, k=60):
    """polyline along radius r0 from angle a0 to a1 with n bubbles bulging outward/inward."""
    pts = []
    for i in range(n * k + 1):
        t = i / (n * k)
        a = a0 + (a1 - a0) * t
        bump = abs(math.sin(math.pi * t * n)) ** .55
        pts.append(P(r0 + (amp if outward else -amp) * bump, a))
    return pts


def arc(cx, cy, rad, b0, b1, k=60):
    return [np.array([cx + rad * math.cos(b), cy + rad * math.sin(b)]) for b in np.linspace(b0, b1, k)]


a0, a1 = -SPAN / 2, SPAN / 2
rm = (RI + RO) / 2
# outer contour: back (scalloped) → right round end → front (scalloped, reversed) → left round end
back = scallop(RO - 40, a0, a1, 7, 40)
front = scallop(RI + 30, a1, a0, 10, 30)
CAP = 330                                     # how far the round arm ends stick out


def cap(a, side):
    r_b, r_f = RO - 40, RI + 30                       # where the back / front scallops end
    c = P((r_b + r_f) / 2, a); hr = (r_b - r_f) / 2
    u = np.array([math.sin(a), math.cos(a)])          # radial, outward (to the back)
    v = side * np.array([math.cos(a), -math.sin(a)])  # tangential, away from the middle
    ts = np.linspace(0, math.pi, 120) if side > 0 else np.linspace(math.pi, 0, 120)
    out = []
    for t in ts:
        bub = 1 + .045 * abs(math.sin(4 * t)) ** .55  # the arm is made of bubbles too
        out.append(c + hr * u * math.cos(t) * bub + CAP * v * math.sin(t) * bub)
    return out


capR = cap(a1, 1)
capL = cap(a0, -1)
outline = back + capR + front + capL

# inner lines
back_inner = scallop(RO - BACK_T, a0, a1, 7, 45, outward=False)
seat_front = scallop(RI + 230, a0, a1, 10, 25, outward=True)
armL = [P(r, a0 + .004) for r in np.linspace(RI + 40, RO - BACK_T + 20, 30)]
armR = [P(r, a1 - .004) for r in np.linspace(RI + 40, RO - BACK_T + 20, 30)]
# seat bubbles: radial joints between front bubbles (seat), and back bubbles
seat_joints = [[P(RI + 40, a), P(RI + 230, a)] for a in np.linspace(a0, a1, 11)[1:-1]]
back_joints = [[P(RO - BACK_T - 10, a), P(RO - 60, a)] for a in np.linspace(a0, a1, 8)[1:-1]]
seat_mid = scallop(RO - BACK_T - 230, a0 + .02, a1 - .02, 5, 30, outward=False)

doc = ezdxf.new('R2013', setup=True); doc.units = ezdxf.units.MM
doc.layers.add('SOFA-OUTLINE', color=7)
doc.layers.add('SOFA-CUSHIONS', color=8)
blk = doc.blocks.new('BUBBLE_SOFA')
tup = lambda pts: [(float(p[0]), float(p[1])) for p in pts]
blk.add_lwpolyline(tup(outline), close=True, dxfattribs={'layer': 'SOFA-OUTLINE'})
for line in [back_inner, seat_front, armL, armR, seat_mid] + seat_joints + back_joints:
    blk.add_lwpolyline(tup(line), dxfattribs={'layer': 'SOFA-CUSHIONS'})
doc.modelspace().add_blockref('BUBBLE_SOFA', (0, 0))
path = os.path.join(OUT, 'bubble-sofa-plan.dxf'); doc.saveas(path)

# preview
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
o = np.array(outline)
fig = plt.figure(figsize=(10, 5)); ax = fig.add_axes([.05, .08, .9, .85])
ax.fill(o[:, 0], o[:, 1], color='#f2f0ec', ec='black', lw=1.2)
for line in [back_inner, seat_front, armL, armR, seat_mid] + seat_joints + back_joints:
    l = np.array(line); ax.plot(l[:, 0], l[:, 1], color='#555', lw=.8)
ax.set_aspect('equal')
Wd, Dd = o[:, 0].max() - o[:, 0].min(), o[:, 1].max() - o[:, 1].min()
ax.set_title(f'Диван, план, мм (габарит ≈ {Wd:.0f} × {Dd:.0f})')
fig.savefig(os.path.join(OUT, 'bubble-sofa-plan.png'), dpi=140, facecolor='white')
print(round(Wd), round(Dd))
