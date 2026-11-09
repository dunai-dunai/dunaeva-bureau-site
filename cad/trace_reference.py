"""
Векторизация вида сверху (кресло + столик, банкетка) с чертежа производителя.
Результат — полилинии в пикселях исходного изображения, сохраняются в JSON.

Запуск: python3 trace_reference.py <путь_к_чертежу.png>
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.morphology import skeletonize, remove_small_objects
from skimage.measure import label

UP = 8  # увеличение для субпиксельной точности
REGIONS = {
    "chair": (400, 550, 140, 268),   # x0, x1, y0, y1 в пикселях исходника
    "ottoman": (724, 806, 178, 250),
}

NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def trace_paths(sk):
    """Разбивает скелет на пути между узлами/концами + замкнутые петли."""
    pts = set(zip(*np.nonzero(sk)))

    def nbrs(p):
        return [(p[0] + dy, p[1] + dx) for dy, dx in NB if (p[0] + dy, p[1] + dx) in pts]

    deg = {p: len(nbrs(p)) for p in pts}
    nodes = {p for p, d in deg.items() if d != 2}
    used = set()  # рёбра (p,q)
    paths = []

    def walk(a, b):
        path = [a, b]
        used.add((a, b)); used.add((b, a))
        prev, cur = a, b
        while cur not in nodes:
            nxt = [q for q in nbrs(cur) if q != prev and (cur, q) not in used]
            if not nxt:
                break
            q = nxt[0]
            used.add((cur, q)); used.add((q, cur))
            path.append(q)
            prev, cur = cur, q
            if cur == a:
                break
        return path

    for n in nodes:
        for q in nbrs(n):
            if (n, q) not in used:
                paths.append(walk(n, q))
    # петли без узлов
    for p in pts:
        for q in nbrs(p):
            if (p, q) not in used:
                paths.append(walk(p, q))
    return paths


def smooth(path, win=9):
    a = np.array(path, float)
    if len(a) < win + 2:
        return a
    closed = np.allclose(a[0], a[-1])
    k = np.ones(win) / win
    if closed:
        ext = np.vstack([a[-win:-1], a, a[1:win]])
        sm = np.column_stack([np.convolve(ext[:, i], k, "same") for i in range(2)])
        out = sm[win - 1: win - 1 + len(a)]
        out[-1] = out[0]
        return out
    # окно сужается к концам — концы на месте, без изломов
    h = win // 2
    n = len(a)
    sm = np.empty_like(a)
    for i in range(n):
        w = min(h, i, n - 1 - i)
        sm[i] = a[i - w: i + w + 1].mean(axis=0)
    return sm


def rdp(a, eps):
    if len(a) < 3:
        return a
    s, e = a[0], a[-1]
    d = e - s
    n = np.hypot(*d)
    if n == 0:
        dist = np.hypot(*(a - s).T)
    else:
        dist = np.abs(d[0] * (a[:, 1] - s[1]) - d[1] * (a[:, 0] - s[0])) / n
    i = int(np.argmax(dist))
    if dist[i] > eps:
        return np.vstack([rdp(a[: i + 1], eps)[:-1], rdp(a[i:], eps)])
    return np.vstack([s, e])


def main(src):
    g = Image.open(src).convert("L")
    out = {}
    for name, (x0, x1, y0, y1) in REGIONS.items():
        crop = g.crop((x0, y0, x1, y1))
        big = np.array(crop.resize(((x1 - x0) * UP, (y1 - y0) * UP), Image.BICUBIC))
        mask = big < 165
        mask = remove_small_objects(mask, max_size=40 * UP)
        sk = skeletonize(mask)
        polys = []
        for p in trace_paths(sk):
            if len(p) < UP:  # обрезки на стыках
                continue
            a = smooth(p, win=4 * UP + 1)
            a = rdp(a, 0.03 * UP)
            # (row, col) -> (x, y) в пикселях исходника
            xy = [[x0 + c / UP, y0 + r / UP] for r, c in a]
            polys.append(xy)
        out[name] = polys
        print(name, len(polys), "polylines")
    Path(__file__).with_name("reference_trace.json").write_text(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1])
