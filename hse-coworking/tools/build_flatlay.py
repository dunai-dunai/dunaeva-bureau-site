#!/usr/bin/env python3
"""Texture board v2 — flat-lay of physical samples, A4 landscape 300 dpi.

One sample per material, big enough for the texture to read; each piece has
thickness, a contact shadow and a soft cast shadow. Exports every piece as its
own PNG layer, a preview, and a Photoshop build script (live text layers).

    python3 hse-coworking/tools/build_flatlay.py
"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')
OUT = os.path.join(ROOT, 'texture-board-v2')
LAY = os.path.join(OUT, 'layers')
FONTS = os.path.join(ROOT, 'fonts')
os.makedirs(LAY, exist_ok=True)

W, H = 3508, 2480
rng = np.random.default_rng(3)
random.seed(3)
INK, MUTED = '#2A2826', '#8A837B'


def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def noise(shape, scale, octaves=4, seed=0):
    r = np.random.default_rng(seed); h, w = shape
    out = np.zeros(shape, np.float32); amp = tot = 0.0; amp = 1.0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        small = r.random((h // s + 2, w // s + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w + s * 2, h + s * 2), Image.BICUBIC)
        out += amp * np.asarray(im, np.float32)[:h, :w] / 255; tot += amp; amp *= .5
    return out / tot


def to_img(a, mode='RGB'):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), mode) if mode != 'RGB' else Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ masks
def jagged_poly(w, h, broken=('r', 'b'), amp=40, step=26, seed=0):
    r = random.Random(seed)
    pts = []
    def edge(p0, p1, rough):
        n = max(2, int(math.dist(p0, p1) / step))
        for i in range(n):
            t = i / n
            x = p0[0] + (p1[0] - p0[0]) * t; y = p0[1] + (p1[1] - p0[1]) * t
            if rough and 0 < i:
                nx, ny = (p1[1] - p0[1]), -(p1[0] - p0[0]); L = math.hypot(nx, ny)
                d = r.uniform(-amp, amp * .35)
                x += nx / L * d; y += ny / L * d
            pts.append((x, y))
    edge((0, 0), (w, 0), 't' in broken)
    edge((w, 0), (w, h), 'r' in broken)
    edge((w, h), (0, h), 'b' in broken)
    edge((0, h), (0, 0), 'l' in broken)
    return pts


def poly_mask(w, h, pts):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return m


def rrect_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m


# ------------------------------------------------------------------ textures
def tex_parquet_cluster():
    """A handful of herringbone planks with their natural zig-zag outline."""
    Wp, Lp = 120, 600
    S = 1500
    canvas = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    base = np.array(hex2rgb('#C8976A'), np.float32)
    def plank(seed):
        r = random.Random(seed)
        streak = noise((Wp, 8), 3, 3, seed=seed).repeat(Lp // 8 + 1, 1)[:, :Lp]
        wav = noise((Wp, Lp), 70, 3, seed=seed + 1)
        rays = noise((Wp, Lp), 12, 2, seed=seed + 2)
        g = .55 * streak + .35 * wav + .10 * rays
        fine = rng.random((Wp, Lp)).astype(np.float32)
        tone = r.uniform(-14, 12)
        col = np.empty((Wp, Lp, 3), np.float32)
        col[..., 0] = base[0] + tone + (g - .5) * 80 + (fine - .5) * 7
        col[..., 1] = base[1] + tone + (g - .5) * 72 + (fine - .5) * 7
        col[..., 2] = base[2] + tone + (g - .5) * 55 + (fine - .5) * 7
        col[:3] *= .78; col[-3:] *= .85; col[:, :3] *= .8; col[:, -3:] *= .85
        return to_img(col)
    keep = []
    for a in range(-12, 12):
        for b in range(-4, 4):
            ox, oy = a * Wp + b * Lp + 300, a * Wp - b * Lp + 300
            for (x, y, horiz) in ((ox, oy, True), (ox, oy + Wp, False)):
                cx, cy = (x + Lp / 2, y + Wp / 2) if horiz else (x + Wp / 2, y + Lp / 2)
                if (cx - 700) ** 2 / 380 ** 2 + (cy - 700) ** 2 / 300 ** 2 < 1:
                    keep.append((x, y, horiz))
    for i, (x, y, horiz) in enumerate(keep):
        p = plank(100 + i)
        if not horiz: p = p.rotate(90, expand=True)
        canvas.paste(p, (x, y))
        a = canvas.split()[3]; ImageDraw.Draw(a).rectangle([x, y, x + p.width - 1, y + p.height - 1], fill=255)
        canvas.putalpha(a)
    canvas = canvas.rotate(45, resample=Image.BICUBIC, expand=True)
    return canvas.crop(canvas.getbbox())


def tex_glass(w, h):
    xx = np.arange(w, dtype=np.float32)
    per = 46
    ph = (xx % per) / per
    prof = np.cos((ph - .5) * math.pi)            # 0 at grooves, 1 at crown
    hl = np.exp(-((ph - .32) / .05) ** 2)          # specular line on each reed
    groove = np.exp(-((ph) / .04) ** 2) + np.exp(-((ph - 1) / .04) ** 2)
    base = np.array(hex2rgb('#B79AC8'), np.float32)
    v = (0.80 + 0.22 * prof + 0.35 * hl - 0.25 * groove)[None, :, None]
    grad = np.linspace(1.04, 0.92, h, dtype=np.float32)[:, None, None]
    rgb = np.clip(base * v * grad + 40 * hl[None, :, None], 0, 255)
    rgb = np.broadcast_to(rgb, (h, w, 3))
    alpha = np.clip(95 + 55 * prof + 90 * hl + 40 * groove, 0, 255)[None, :].repeat(h, 0)
    im = Image.fromarray(rgb.astype(np.uint8)); im.putalpha(Image.fromarray(alpha.astype(np.uint8)))
    return im


def tex_velvet(w, h):
    base = np.array(hex2rgb('#AE781B'), np.float32); hi = np.array(hex2rgb('#DDA640'), np.float32)
    crush = noise((h, w), 26, 3, seed=21)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    fold = .5 + .5 * np.sin((xx / w * 1.0 + yy / h * .45) * math.pi * 2.2 + 1.2 * noise((h, w), 220, 2, seed=5))
    pile = rng.random((h, w)).astype(np.float32)
    pile = np.asarray(Image.fromarray((pile * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
    k = np.clip(.30 + .45 * fold + .16 * (crush - .5) + .10 * (pile - .5), 0, 1)[..., None]
    return to_img(base * (.62 + .38 * k) + (hi - base) * k ** 3)


def tex_stripe_velvet():
    src = Image.open(os.path.join(SRC, '04-stripe-chair.jpg')).convert('RGB').crop((240, 445, 600, 655))
    c = np.asarray(src, np.float32)
    lum = c @ np.array([.3, .59, .11], np.float32)
    x = np.clip((lum - 40) / 185, 0, 1); x = x * x * (3 - 2 * x)
    milk, ink = np.array([239, 230, 214], np.float32), np.array([22, 21, 20], np.float32)
    im = to_img(ink + (milk - ink) * x[..., None])
    return im.resize((int(im.width * 1.9), int(im.height * 1.9)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))


def tex_cement(s):
    yy, xx = np.mgrid[0:s, 0:s]
    m = (yy > xx).astype(np.float32)[..., None]
    dark, light = np.array(hex2rgb('#3C4147'), np.float32), np.array(hex2rgb('#D9D1C4'), np.float32)
    mott = noise((s, s), 80, 5, seed=61)[..., None]
    grit = rng.random((s, s, 1)).astype(np.float32)
    pores = (rng.random((s, s, 1)) > .997).astype(np.float32)
    t = m * dark + (1 - m) * light
    return to_img(t * (.88 + .2 * mott) + (grit - .5) * 16 - pores * 40)


def tex_brass(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    streak = noise((h, 6), 2, 3, seed=31).repeat(w // 6 + 1, 1)[:, :w]
    band = np.exp(-((yy / h - .35) / .18) ** 2)
    v = np.clip(.55 + .38 * band + .10 * (streak - .5) - .1 * (xx / w), 0, 1)[..., None]
    c1, c2 = np.array(hex2rgb('#7E5F2C'), np.float32), np.array(hex2rgb('#ECD08F'), np.float32)
    return to_img(c1 + (c2 - c1) * v)


def tex_chrome(w, h):
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    v = (.35 + .35 * np.sin(yy * math.pi) + .55 * np.exp(-((yy - .30) / .05) ** 2)
         + .25 * np.exp(-((yy - .72) / .04) ** 2) - .25 * np.exp(-((yy - .52) / .08) ** 2))
    v = np.clip(v, 0, 1).repeat(w, 1)[..., None]
    lo, hi = np.array(hex2rgb('#3A3F46'), np.float32), np.array(hex2rgb('#F6F8FA'), np.float32)
    return to_img(lo + (hi - lo) * v)


def tex_smalt_fragment():
    S, s = 760, 46
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    golds = ['#C9A042', '#DDB758', '#B88B2E', '#E9CB78', '#A97E2C', '#D2AA4B', '#F1D78E']
    blob = noise((S, S), 260, 2, seed=71)
    bed = Image.new('L', (S, S), 0); bd = ImageDraw.Draw(bed)
    cells = []
    for gy in range(S // s + 1):
        off = random.randint(-10, 10)
        for gx in range(S // s + 1):
            x0, y0 = gx * s + off + random.randint(-3, 3), gy * s + random.randint(-3, 3)
            cx, cy = x0 + s / 2, y0 + s / 2
            r = ((cx - S / 2) / (S * .44)) ** 2 + ((cy - S / 2) / (S * .38)) ** 2
            if 0 <= cx < S and 0 <= cy < S and r + .55 * (blob[int(cy), int(cx)] - .5) < 1:
                cells.append((x0, y0))
    for (x0, y0) in cells:   # grout bed under tesserae
        bd.rectangle([x0 - 3, y0 - 3, x0 + s + 2, y0 + s + 2], fill=255)
    bed = bed.filter(ImageFilter.MaxFilter(5))
    im.paste((92, 80, 62, 255), (0, 0), bed)
    for (x0, y0) in cells:
        w_, h_ = s - random.randint(5, 10), s - random.randint(5, 10)
        c = hex2rgb(random.choice(golds)); k = random.uniform(.8, 1.15)
        c = tuple(min(255, int(v * k)) for v in c)
        j = lambda: random.randint(0, 3)
        d.polygon([(x0 + j(), y0 + j()), (x0 + w_ - j(), y0 + j()), (x0 + w_ - j(), y0 + h_ - j()), (x0 + j(), y0 + h_ - j())], fill=c + (255,))
        d.line([(x0 + 4, y0 + 4), (x0 + w_ - 6, y0 + 4)], fill=(255, 244, 205, 255), width=2)
    return im.crop(im.getbbox())


def tex_hammered_steel():
    """Mirror-polished stainless with water-ripple hammering, organic outline."""
    S = 820
    hgt = np.zeros((S, S), np.float32)
    r = np.random.default_rng(81)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    for _ in range(420):
        cx, cy = r.uniform(0, S, 2); rad = r.uniform(18, 46)
        hgt += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * rad ** 2)) * r.uniform(.6, 1.2)
    gy, gx = np.gradient(hgt)
    nx, ny = gx * 6, gy * 6
    # environment: cool sky, white light, dark room — mapped by reflected direction
    u = np.clip(.5 + nx * 1.6 + (xx / S - .5) * .25, 0, 1)
    v = np.clip(.5 + ny * 1.6 + (yy / S - .5) * .25, 0, 1)
    env = (.5 + .5 * np.sin(u * 14.0 + v * 4.0) * np.cos(v * 11.0 - u * 3.0))
    spec = np.exp(-((u - .35) ** 2 + (v - .30) ** 2) / .004) + .7 * np.exp(-((u - .7) ** 2 + (v - .62) ** 2) / .003)
    sharp = 1 / (1 + np.exp(-(env - .32) * 14))      # mostly bright, crisp dark crescents
    k = np.clip(.12 + .80 * sharp + spec * .6, 0, 1)
    cool = np.array([38, 42, 48], np.float32); bright = np.array([250, 251, 252], np.float32)
    rgb = cool + (bright - cool) * k[..., None]
    rgb[..., 2] += 10 * (1 - k)
    blob = noise((S, S), 300, 3, seed=82)
    rr = ((xx - S / 2) / (S * .40)) ** 2 + ((yy - S / 2) / (S * .46)) ** 2
    m = ((rr + .9 * (blob - .5)) < 1).astype(np.uint8) * 255
    m = Image.fromarray(m).filter(ImageFilter.GaussianBlur(6)).point(lambda q: 255 if q > 128 else 0).filter(ImageFilter.GaussianBlur(1.2))
    im = to_img(rgb).convert('RGBA'); im.putalpha(m)
    return im.crop(im.getbbox())


def tex_shag(w, h):
    base = np.array(hex2rgb('#C48A1A'), np.float32)
    clumps = noise((h, w), 7, 2, seed=91)
    tufts = noise((h, w), 3, 1, seed=92)
    broad = noise((h, w), 200, 2, seed=93)
    fine = rng.random((h, w)).astype(np.float32)
    k = .45 * clumps + .25 * tufts + .15 * fine + .15 * broad
    k = (k - k.mean()) / k.std()
    return to_img(base[None, None] * (1 + .16 * k[..., None]) + np.array([12, 8, 0]) * (k[..., None] > 1.2))


def tex_stucco(w, h):
    src = Image.open(os.path.join(SRC, '03-reception-draft.webp')).convert('RGB').crop((40, 0, 420, 150))
    return src.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2.5, 70, 2))


def shift(im, dx, dy):
    out = Image.new(im.mode, im.size, 0); out.paste(im, (dx, dy)); return out


# ------------------------------------------------------------------ piece builder
pieces = []   # (name, label, layer RGBA full canvas, shadow RGBA full canvas)


def place(name, top, mask, x, y, thick=20, side=.62, rot=0, shadow=.32, lift=1.0, side_rgb=None, side_alpha=1.0):
    """top: RGB/RGBA face; mask: L. Returns full-canvas piece + shadow layers."""
    if top.mode != 'RGBA': top = top.convert('RGBA')
    a = ImageChops.multiply(top.split()[3], mask)
    face = top.copy(); face.putalpha(a)
    pad = thick + 8
    w, h = face.size
    body = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    # sides: stacked, darkened copies of the face (light from top-left)
    sd = face.convert('RGB')
    sd = Image.eval(sd, lambda v: int(v * side)) if side_rgb is None else Image.new('RGB', face.size, side_rgb)
    sm = face.split()[3].point(lambda v: 255 if v > 30 else 0)
    sides = Image.new('RGBA', body.size, (0, 0, 0, 0))
    for k in range(thick, 0, -1):
        sides.paste(sd, (pad + int(k * .45), pad + k), sm)
    if side_alpha < 1:
        sa = sides.split()[3].point(lambda q: int(q * side_alpha))
        hole = Image.new('L', body.size, 0); hole.paste(sm, (pad, pad))   # no side under the face itself
        sa = ImageChops.subtract(sa, hole); sides.putalpha(sa)
    body.alpha_composite(sides)
    body.alpha_composite(face, (pad, pad))
    # top-left edge highlight
    edge = ImageChops.subtract(sm, shift(sm, 3, 3)).filter(ImageFilter.GaussianBlur(1))
    hl = Image.new('RGBA', face.size, (255, 255, 255, 0)); hl.putalpha(edge.point(lambda v: int(v * .45)))
    body.alpha_composite(hl, (pad, pad))
    if rot:
        body = body.rotate(rot, resample=Image.BICUBIC, expand=True)
    full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    full.alpha_composite(body, (int(x - pad), int(y - pad)))
    # shadow
    sil = full.split()[3].point(lambda v: 255 if v > 20 else 0)
    soft = shift(sil, int(28 * lift), int(40 * lift)).filter(ImageFilter.GaussianBlur(46 * lift))
    contact = shift(sil, 4, 7).filter(ImageFilter.GaussianBlur(7))
    sh = ImageChops.lighter(soft.point(lambda v: int(v * shadow)), contact.point(lambda v: int(v * .42)))
    shadow_l = Image.new('RGBA', (W, H), (52, 40, 30, 0)); shadow_l.putalpha(sh)
    pieces.append(dict(name=name, layer=full, shadow=shadow_l, bbox=full.getbbox()))
    return full.getbbox()


def build():
    # background: milky plaster
    bgn = noise((H, W), 300, 5, seed=1)
    fine = rng.random((H, W)).astype(np.float32)
    base = np.array(hex2rgb('#ECE6DD'), np.float32)
    bg = base * (.975 + .04 * bgn[..., None]) + (fine[..., None] - .5) * 5
    to_img(bg).save(os.path.join(LAY, '00-background.png'))

    # 1 stucco fragment (ornament)
    w, h = 820, 330
    place('Лепнина', tex_stucco(w, h), poly_mask(w, h, jagged_poly(w, h, ('r', 'b', 'l'), 30, 20, seed=1)),
          230, 430, thick=34, side=.88, side_rgb=(214, 206, 196), rot=-3)
    # 2 parquet planks
    pq = tex_parquet_cluster()
    pq = pq.resize((int(pq.width * .74), int(pq.height * .74)), Image.LANCZOS)
    place('Паркет', pq, pq.split()[3], 1150, 230, thick=22, side=.55)
    # 3 cement tile, single
    s_ = 520
    cm = poly_mask(s_, s_, [(0, 0), (s_, 0), (s_, s_ - 40), (s_ - 46, s_), (0, s_)])
    place('Цементная плитка', tex_cement(s_), cm, 2050, 260, thick=30, side=.70, rot=5)
    # 4 velvet, mustard: soft fabric piece
    w, h = 700, 520
    v = tex_velvet(w, h)
    m = poly_mask(w, h, jagged_poly(w, h, ('r', 'b', 'l', 't'), 10, 60, seed=9)).filter(ImageFilter.GaussianBlur(2))
    dist = m.filter(ImageFilter.GaussianBlur(40))
    va = np.asarray(v, np.float32) * (.6 + .4 * (np.asarray(dist, np.float32)[..., None] / 255))
    place('Бархат', to_img(va), m, 280, 1000, thick=4, side=.45, rot=4, lift=.8)
    # 5 smalt fragment
    sm = tex_smalt_fragment(); sm = sm.resize((int(sm.width * .82), int(sm.height * .82)), Image.LANCZOS)
    place('Золотая смальта', sm, sm.split()[3], 1180, 1120, thick=12, side=.45, rot=-6)
    # 6 lilac fluted glass, overlapping the cement tile
    w, h = 540, 760
    gl = Image.open(os.path.join(ROOT, 'cutouts', 'glass-lilac.png')).convert('RGBA')
    gl = gl.crop(gl.getbbox()); gl = gl.resize((int(gl.width * .62), int(gl.height * .62)), Image.LANCZOS)
    place('Лиловое стекло', gl, gl.split()[3].point(lambda q: 255 if q else 0), 2420, 560, thick=0, rot=-4, shadow=.10, lift=.6)
    # 7 stripe velvet (black + milk)
    st = tex_stripe_velvet(); st = st.resize((int(st.width * .85), int(st.height * .85)), Image.LANCZOS)
    place('Бархат в полоску', st, rrect_mask(st.width, st.height, 16), 2700, 1560, thick=6, side=.5, rot=7, lift=.9)
    # 8 mustard shag
    w, h = 600, 430
    place('Ковёр', tex_shag(w, h), poly_mask(w, h, jagged_poly(w, h, ('r', 'b', 'l', 't'), 7, 9, seed=5)),
          330, 1720, thick=12, side=.55, rot=-5)
    # 9 brass bar
    w, h = 1100, 150
    place('Латунь', tex_brass(w, h), rrect_mask(w, h, 6), 1120, 2000, thick=22, side=.55, rot=3)
    # 10 hammered mirror steel
    hs = tex_hammered_steel(); hs = hs.resize((int(hs.width * .9), int(hs.height * .9)), Image.LANCZOS)
    place('Зеркальная сталь', hs, hs.split()[3], 1900, 1240, thick=8, side=.5, lift=.8)

    # layers out
    meta = []
    for i, p in enumerate(pieces, 1):
        for kind in ('shadow', 'layer'):
            img = p[kind]; bb = img.getbbox()
            fn = f'{i:02d}-{p["name"]}-{"тень" if kind == "shadow" else "образец"}.png'
            img.crop(bb).save(os.path.join(LAY, fn))
            meta.append(dict(group=f'{i:02d} {p["name"]}', name=('Тень' if kind == 'shadow' else 'Образец — ' + p['name']),
                             file=fn, x=bb[0], y=bb[1], blend='multiply' if kind == 'shadow' else 'normal',
                             opacity=100, smart=kind == 'layer'))
    return meta


LABEL_TEXT = {
    'Лепнина': 'лепнина · гипс', 'Паркет': 'паркет · дуб, ёлочка', 'Цементная плитка': 'плитка · цемент',
    'Бархат': 'бархат · мохер, горчичный', 'Золотая смальта': 'смальта · золото', 'Лиловое стекло': 'стекло · лиловое, тонированное',
    'Бархат в полоску': 'бархат · чёрный и молочный', 'Ковёр': 'ковёр · горчичный ворс', 'Латунь': 'латунь',
    'Зеркальная сталь': 'сталь · зеркальная, выбивка',
}
LABEL_NUDGE = {'Лиловое стекло': (330, -10), 'Цементная плитка': (0, 0)}

F_IT = ('CormorantGaramond-Italic', 'CormorantGaramond-Italic.ttf', 400)
F_DISP = ('CormorantGaramond-Light', 'CormorantGaramond.ttf', 300)
F_SMALL = ('Inter-Medium', '/usr/share/fonts/opentype/inter/Inter-Medium.otf', None)


def texts_spec():
    t = []
    for p in pieces:
        bb = p['bbox']; txt = LABEL_TEXT[p['name']]
        dx, dy = LABEL_NUDGE.get(p['name'], (0, 0))
        x, y = bb[0] + 20 + dx, bb[3] + 62 + dy
        t.append(dict(group='Подписи', name=txt, lines=[txt], font=F_IT, size=44, color=INK, x=x, y=y, leading=56, tracking=0))
    t.append(dict(group='Заголовок', name='Надзаголовок', lines=['КОВОРКИНГ · ЦЕНТР МОСКВЫ'], font=F_SMALL, size=26,
                  color=MUTED, x=236, y=200, leading=32, tracking=180))
    t.append(dict(group='Заголовок', name='Заголовок', lines=['Текстурная доска'], font=F_DISP, size=96,
                  color=INK, x=230, y=320, leading=100, tracking=0))
    return t


def pil_font(f, size):
    path = f[1] if os.path.isabs(f[1]) else os.path.join(FONTS, f[1])
    fo = ImageFont.truetype(path, size)
    if f[2]:
        try: fo.set_variation_by_axes([f[2]])
        except Exception: pass
    return fo


def main():
    meta = build()
    texts = texts_spec()
    images = [dict(group='Фон', name='Фон — молочная штукатурка', file='00-background.png', x=0, y=0,
                   blend='normal', opacity=100, smart=False)] + meta
    # preview
    im = Image.open(os.path.join(LAY, '00-background.png')).convert('RGBA')
    for e in meta:
        l = Image.open(os.path.join(LAY, e['file'])).convert('RGBA')
        if e['blend'] == 'multiply':
            # emulate multiply with dark tint
            region = im.crop((e['x'], e['y'], e['x'] + l.width, e['y'] + l.height))
            a = np.asarray(l, np.float32); r = np.asarray(region, np.float32)
            al = a[..., 3:4] / 255
            out = r[..., :3] * (1 - al) + r[..., :3] * (a[..., :3] / 255) * al
            region = Image.fromarray(np.concatenate([out, r[..., 3:]], 2).astype(np.uint8), 'RGBA')
            im.paste(region, (e['x'], e['y']))
        else:
            im.alpha_composite(l, (e['x'], e['y']))
    d = ImageDraw.Draw(im)
    for t in texts:
        fo = pil_font(t['font'], t['size'])
        x = t['x']
        for ch in t['lines'][0]:
            d.text((x, t['y']), ch, font=fo, fill=t['color'], anchor='ls')
            x += fo.getlength(ch) + t['tracking'] / 1000 * t['size']
    im = im.convert('RGB')
    im.save(os.path.join(OUT, 'preview.jpg'), quality=90)
    im.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(OUT, 'preview-small.jpg'), quality=88)
    # jsx (reuse the v1 template)
    import build_texture_board as v1
    spec = dict(width=W, height=H, resolution=300, background='#FFFFFF', images=images, texts=texts,
                circles=[], title='Текстурная доска v2')
    jsx = v1.JSX.replace('__SPEC__', json.dumps(spec, ensure_ascii=False, indent=1))
    with open(os.path.join(OUT, 'build_texture_board_v2.jsx'), 'w', encoding='utf-8') as fh:
        fh.write('﻿' + jsx)
    print('ok')


if __name__ == '__main__':
    main()
