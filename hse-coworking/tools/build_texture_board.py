#!/usr/bin/env python3
"""Texture board, A4 landscape 300 dpi (3508 x 2480).

Builds every layer as a PNG in texture-board/layers/, a flat preview.jpg,
and build_texture_board.jsx: a Photoshop script that assembles the layered
document with live text layers. The same SPEC drives the preview and the JSX.

    python3 hse-coworking/tools/build_texture_board.py
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')
OUT = os.path.join(ROOT, 'texture-board')
LAY = os.path.join(OUT, 'layers')
FONTS = os.path.join(ROOT, 'fonts')
os.makedirs(LAY, exist_ok=True)

W, H = 3508, 2480
CELL = 480
rng = np.random.default_rng(7)
random.seed(7)

INK = '#26252B'
MUTED = '#8C8680'
ACCENT = '#7B5A93'   # deep lilac for numbers


# ---------------------------------------------------------------- helpers
def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def noise(shape, scale, octaves=4, seed=0):
    """Smooth value noise in [0,1]."""
    r = np.random.default_rng(seed)
    h, w = shape
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        small = r.random((h // s + 2, w // s + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w + s * 2, h + s * 2), Image.BICUBIC)
        out += amp * (np.asarray(im, np.float32)[:h, :w] / 255.0)
        tot += amp
        amp *= 0.5
    return out / tot


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def crop_square(path, box, size=CELL):
    im = Image.open(path).convert('RGB').crop(box).resize((size, size), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))


# ---------------------------------------------------------------- swatches
def sw_stucco():
    return crop_square(os.path.join(SRC, '03-reception-draft.webp'), (0, 0, 370, 370))


def sw_glass():
    return crop_square(os.path.join(SRC, '03-reception-draft.webp'), (590, 895, 880, 1185))


def sw_parquet(size=CELL):
    # herringbone: lattice (Wp,Wp),(Lp,-Lp); H plank [0,L]x[0,W], V plank at (0,W) size W x L
    Wp, Lp = 34, 170
    S = int(size * 1.6)
    base = np.array(hex2rgb('#C8976A'), np.float32)
    canvas = Image.new('RGB', (S, S))
    grain_src = noise((Wp * 3, Lp * 6), 6, 3, seed=11)

    def plank(horizontal):
        g = np.zeros((Wp, Lp), np.float32)
        oy = random.randint(0, Wp * 2)
        ox = random.randint(0, Lp * 5)
        streak = grain_src[oy:oy + Wp, ox:ox + 1].repeat(Lp, 1)
        wav = noise((Wp, Lp), 40, 2, seed=random.randint(0, 9999))
        g = 0.55 * streak + 0.45 * wav
        fine = rng.random((Wp, Lp)).astype(np.float32)
        tone = random.uniform(-16, 14)
        warm = random.uniform(-6, 6)
        col = np.empty((Wp, Lp, 3), np.float32)
        col[..., 0] = base[0] + tone + warm + (g - .5) * 38 + (fine - .5) * 6
        col[..., 1] = base[1] + tone + (g - .5) * 34 + (fine - .5) * 6
        col[..., 2] = base[2] + tone - warm + (g - .5) * 26 + (fine - .5) * 6
        col[0, :] *= 0.80; col[-1, :] *= 0.86; col[:, 0] *= 0.82; col[:, -1] *= 0.86  # joints
        im = to_img(col)
        return im if horizontal else im.rotate(90, expand=True)

    for a in range(-40, 40):
        for b in range(-12, 12):
            ox, oy = a * Wp + b * Lp, a * Wp - b * Lp + S // 2
            if -Lp <= ox <= S and -Lp <= oy <= S:
                canvas.paste(plank(True), (ox, oy))
                canvas.paste(plank(False), (ox, oy + Wp))
    canvas = canvas.rotate(45, resample=Image.BICUBIC)
    c = (S - size) // 2
    im = canvas.crop((c, c, c + size, c + size))
    # soft oil sheen
    sheen = noise((size, size), 160, 2, seed=3)
    arr = np.asarray(im, np.float32) * (0.94 + 0.12 * sheen[..., None])
    return to_img(arr)


def sw_velvet(size=CELL):
    base = np.array(hex2rgb('#AE781B'), np.float32)
    hi = np.array(hex2rgb('#D9A23A'), np.float32)
    crush = noise((size, size), 22, 3, seed=21)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    fold = 0.5 + 0.5 * np.sin((xx * 0.9 + yy * 0.5) * math.pi * 1.3 + 0.8 * noise((size, size), 180, 2, seed=5))
    pile = rng.random((size, size)).astype(np.float32)
    pile = np.asarray(Image.fromarray((pile * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    k = np.clip(0.30 + 0.45 * fold + 0.16 * (crush - .5) + 0.10 * (pile - .5), 0, 1)[..., None]
    arr = base * (0.62 + 0.38 * k) + (hi - base) * k ** 3
    return to_img(arr)


def sw_cement(size=CELL):
    n = 2
    t = size // n
    im = Image.new('RGB', (size, size), hex2rgb('#2E2C2A'))
    dark, light = np.array(hex2rgb('#3C4147'), np.float32), np.array(hex2rgb('#D7CFC2'), np.float32)
    for i in range(n):
        for j in range(n):
            yy, xx = np.mgrid[0:t, 0:t]
            m = (yy > xx).astype(np.float32)[..., None]  # lower-left triangle dark
            mott = noise((t, t), 50, 4, seed=i * 7 + j)[..., None]
            grit = rng.random((t, t, 1)).astype(np.float32)
            tile = m * dark + (1 - m) * light
            tile = tile * (0.90 + 0.16 * mott) + (grit - .5) * 14
            tile[:3] *= 0.9; tile[:, :3] *= 0.9
            im.paste(to_img(tile).crop((3, 3, t - 3, t - 3)), (i * t + 3, j * t + 3))
    return im


def sw_brass(size=CELL):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    streak = noise((size, 4), 2, 3, seed=31).repeat(size // 4 + 1, 1)[:, :size]
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).resize((size, size)), np.float32) / 255
    fine = rng.random((size, 1)).astype(np.float32).repeat(size, 1)
    band = np.exp(-((xx + yy * 0.35 - size * 0.62) / (size * 0.22)) ** 2)
    v = 0.62 + 0.30 * band + 0.10 * (streak - .5) + 0.07 * (fine - .5) - 0.12 * (yy / size)
    c1, c2 = np.array(hex2rgb('#8A6A35'), np.float32), np.array(hex2rgb('#E6C987'), np.float32)
    v = np.clip(v, 0, 1)[..., None]
    return to_img(c1 + (c2 - c1) * v)


def sw_smalt(size=CELL):
    im = Image.new('RGB', (size, size), hex2rgb('#5A4A33'))
    d = ImageDraw.Draw(im)
    s = 22
    golds = ['#C9A042', '#DDB758', '#B88B2E', '#E9CB78', '#A97E2C', '#D2AA4B']
    for gy in range(-1, size // s + 2):
        off = random.randint(-6, 6)
        for gx in range(-1, size // s + 2):
            x0 = gx * s + off + random.randint(-2, 2)
            y0 = gy * s + random.randint(-2, 2)
            w = s - random.randint(3, 6)
            h = s - random.randint(3, 6)
            c = hex2rgb(random.choice(golds))
            k = random.uniform(.85, 1.12)
            c = tuple(min(255, int(v * k)) for v in c)
            d.polygon([(x0 + random.randint(0, 2), y0 + random.randint(0, 2)),
                       (x0 + w - random.randint(0, 2), y0 + random.randint(0, 2)),
                       (x0 + w - random.randint(0, 2), y0 + h - random.randint(0, 2)),
                       (x0 + random.randint(0, 2), y0 + h - random.randint(0, 2))], fill=c)
    sheen = noise((size, size), 120, 2, seed=41)
    arr = np.asarray(im, np.float32) * (0.85 + 0.3 * sheen[..., None])
    return to_img(arr)


def sw_chrome(size=CELL):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    t = xx * 0.85 + yy * 0.35
    warp = noise((size, size), 200, 2, seed=51)
    t = t + 0.06 * (warp - .5)
    v = (0.55 + 0.25 * np.sin(t * 9.0) + 0.35 * np.exp(-((t - 0.55) / 0.035) ** 2)
         + 0.25 * np.exp(-((t - 0.86) / 0.02) ** 2) - 0.30 * np.exp(-((t - 0.30) / 0.09) ** 2))
    v = np.clip(v, 0.05, 1.0)
    brushed = rng.random((size, 1)).astype(np.float32).repeat(size, 1)
    v = v + 0.03 * (brushed - .5)
    lo, hi = np.array(hex2rgb('#3E434A'), np.float32), np.array(hex2rgb('#F4F6F8'), np.float32)
    return to_img(lo + (hi - lo) * v[..., None])


def sw_placeholder(size=CELL):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = hex2rgb('#B9B2AA') + (255,)
    dash, gap, t = 18, 12, 3
    for x in range(0, size, dash + gap):
        d.rectangle([x, 0, min(x + dash, size), t - 1], fill=col)
        d.rectangle([x, size - t, min(x + dash, size), size - 1], fill=col)
    for y in range(0, size, dash + gap):
        d.rectangle([0, y, t - 1, min(y + dash, size)], fill=col)
        d.rectangle([size - t, y, size - 1, min(y + dash, size)], fill=col)
    c = size // 2
    d.rectangle([c - 40, c - 1, c + 40, c + 1], fill=col)
    d.rectangle([c - 1, c - 40, c + 1, c + 40], fill=col)
    return im


def shadow(size=CELL, pad=90, blur=28, opacity=0.30):
    im = Image.new('L', (size + pad * 2, size + pad * 2), 0)
    ImageDraw.Draw(im).rectangle([pad, pad, pad + size, pad + size], fill=int(255 * opacity))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    rgba = Image.new('RGBA', im.size, (40, 30, 25, 0))
    rgba.putalpha(im)
    return rgba


# ---------------------------------------------------------------- spec
GRID_X0 = W - 180 - (4 * CELL + 3 * 64)   # 1216
COLS = [GRID_X0 + i * (CELL + 64) for i in range(4)]
ROWS = [470, 470 + CELL + 300]

SWATCHES = [
    ('01', 'Лепнина', ['гипс, тёплая белая', 'матовая краска'], 'потолки · карнизы', sw_stucco),
    ('02', 'Лиловое стекло', ['рифлёное и гладкое,', 'тонированное'], 'ресепшен · кабины', sw_glass),
    ('03', 'Паркет «ёлочка»', ['дуб, медовый тон,', 'масло'], 'рабочая зона', sw_parquet),
    ('04', 'Бархат', ['мохер, горчичный'], 'кресло с оттоманкой', sw_velvet),
    ('05', 'Цементная плитка', ['графит и беж,', 'диагональ'], 'мини-кухня', sw_cement),
    ('06', 'Латунь', ['шлифованная,', 'тёплый тон'], 'детали · свет · панно', sw_brass),
    ('07', 'Золотая смальта', ['мозаика в духе', '«Новослободской»'], 'панно', sw_smalt),
    ('08', 'Хром', ['полированная сталь,', 'зеркальный блеск'], 'рабочие кресла', sw_chrome),
]

PALETTE = [
    ('Тёплый белый', '#EFE6DC'), ('Лиловое стекло', '#B79AC8'),
    ('Медовый дуб', '#C8976A'), ('Горчичный', '#B57E1F'),
    ('Латунь', '#B08D57'), ('Бирюза', '#1F8A93'),
    ('Графит', '#3B4046'), ('Хром', '#C4C8CE'),
]

F_DISPLAY = ('CormorantGaramond-Light', 'CormorantGaramond.ttf', 300)
F_DISPLAY_IT = ('CormorantGaramond-Italic', 'CormorantGaramond-Italic.ttf', 400)
F_TEXT = ('Inter-Light', '/usr/share/fonts/opentype/inter/Inter-Light.otf', None)
F_TEXT_MED = ('Inter-Medium', '/usr/share/fonts/opentype/inter/Inter-Medium.otf', None)
F_TEXT_REG = ('Inter-Regular', '/usr/share/fonts/opentype/inter/Inter-Regular.otf', None)

texts = []   # dict(group, name, lines, font, size, color, x, y(baseline), leading, tracking)


def T(group, name, lines, font, size, color, x, y, leading=None, tracking=0):
    texts.append(dict(group=group, name=name, lines=lines, font=font, size=size, color=color,
                      x=x, y=y, leading=leading or int(size * 1.25), tracking=tracking))


LX = 200
T('Заголовок', 'Надзаголовок', ['КОВОРКИНГ · ЦЕНТР МОСКВЫ'], F_TEXT_MED, 30, MUTED, LX, 520, tracking=180)
T('Заголовок', 'Заголовок', ['Текстурная', 'доска'], F_DISPLAY, 210, INK, LX, 740, leading=190)
T('Заголовок', 'Подводка', ['Историческая оболочка — лепнина', 'и паркет — встречается с цветным',
                           'стеклом, бархатом и золотом', 'советской мозаики.'],
  F_TEXT, 38, INK, LX, 1110, leading=60)
T('Палитра', 'Палитра — подпись', ['ПАЛИТРА'], F_TEXT_MED, 28, MUTED, LX, 1520, tracking=180)

circles = []
PD, PSP = 130, 222
for i, (nm, hx) in enumerate(PALETTE):
    cx = LX + PD // 2 + (i % 4) * PSP
    cy = 1640 + (i // 4) * 330
    circles.append(dict(name=nm, hex=hx, cx=cx, cy=cy, d=PD))
    T('Палитра', 'Цвет — ' + nm, [nm], F_TEXT_REG, 24, INK, cx - PD // 2, cy + PD // 2 + 56)
    T('Палитра', 'HEX — ' + nm, [hx], F_TEXT, 22, MUTED, cx - PD // 2, cy + PD // 2 + 92)

images = []   # dict(group, name, file, x, y, blend, opacity, smart)
for i, (num, name, desc, zone, fn) in enumerate(SWATCHES):
    x, y = COLS[i % 4], ROWS[i // 4]
    g = f'{num} {name}'
    slug = f'swatch-{num}'
    if fn:
        shadow().save(os.path.join(LAY, f'{slug}-shadow.png'))
        images.append(dict(group=g, name='Тень', file=f'{slug}-shadow.png', x=x - 90, y=y - 90 + 16,
                           blend='multiply', opacity=100, smart=False))
        fn().save(os.path.join(LAY, f'{slug}.png'))
        images.append(dict(group=g, name=f'Образец — {name}', file=f'{slug}.png', x=x, y=y,
                           blend='normal', opacity=100, smart=True))
    else:
        sw_placeholder().save(os.path.join(LAY, f'{slug}.png'))
        images.append(dict(group=g, name='Пустой слот', file=f'{slug}.png', x=x, y=y,
                           blend='normal', opacity=100, smart=False))
    by = y + CELL + 84
    T(g, 'Номер', [num], F_DISPLAY_IT, 64, ACCENT, x, by)
    T(g, 'Название', [name], F_TEXT_MED, 32, INK, x + 78, by - 6)
    T(g, 'Описание', desc, F_TEXT, 26, INK, x + 78, by + 44, leading=38)
    if zone:
        T(g, 'Зона', [zone.upper()], F_TEXT_MED, 19, MUTED, x + 78, by + 44 + 38 * len(desc) + 14, tracking=140)

SPEC = dict(width=W, height=H, resolution=300, background='#FFFFFF',
            images=images, texts=texts, circles=circles, title='Текстурная доска')


# ---------------------------------------------------------------- preview
def pil_font(f, size):
    path = f[1] if os.path.isabs(f[1]) else os.path.join(FONTS, f[1])
    fo = ImageFont.truetype(path, size)
    if f[2]:
        try:
            fo.set_variation_by_axes([f[2]])
        except Exception:
            pass
    return fo


def render_preview():
    im = Image.new('RGB', (W, H), SPEC['background'])
    for e in images:
        layer = Image.open(os.path.join(LAY, e['file'])).convert('RGBA')
        im.paste(layer, (e['x'], e['y']), layer)
    d = ImageDraw.Draw(im)
    for c in circles:
        r = c['d'] / 2
        d.ellipse([c['cx'] - r, c['cy'] - r, c['cx'] + r, c['cy'] + r], fill=c['hex'])
        if c['hex'] == '#EFE6DC':
            d.ellipse([c['cx'] - r, c['cy'] - r, c['cx'] + r, c['cy'] + r], outline='#DDD3C7', width=2)
    for t in texts:
        fo = pil_font(t['font'], t['size'])
        for k, line in enumerate(t['lines']):
            y = t['y'] + k * t['leading']
            if t['tracking']:
                x = t['x']
                for ch in line:
                    d.text((x, y), ch, font=fo, fill=t['color'], anchor='ls')
                    x += fo.getlength(ch) + t['tracking'] / 1000 * t['size']
            else:
                d.text((t['x'], y), line, font=fo, fill=t['color'], anchor='ls')
    im.save(os.path.join(OUT, 'preview.jpg'), quality=90)
    im.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(OUT, 'preview-small.jpg'), quality=88)


# ---------------------------------------------------------------- photoshop script
JSX = r'''// Текстурная доска — сборка в Photoshop.
// Файл → Сценарии → Обзор… → выбрать этот файл. Папка layers/ должна лежать рядом.
#target photoshop
app.bringToFront();
(function () {
var SPEC = __SPEC__;
var here = File($.fileName).parent;
var oldRuler = app.preferences.rulerUnits, oldType = app.preferences.typeUnits;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
app.displayDialogs = DialogModes.NO;

function rgb(hex) { var c = new SolidColor(); c.rgb.hexValue = hex.replace('#', ''); return c; }

var doc = app.documents.add(SPEC.width, SPEC.height, SPEC.resolution, SPEC.title,
                            NewDocumentMode.RGB, DocumentFill.WHITE);
doc.artLayers[0].name = 'Фон';

var groups = {};
function group(name) {
  if (!groups[name]) { groups[name] = doc.layerSets.add(); groups[name].name = name; }
  return groups[name];
}

function toSmart() {
  try { executeAction(stringIDToTypeID('newPlacedLayer'), undefined, DialogModes.NO); } catch (e) {}
}

// images
for (var i = 0; i < SPEC.images.length; i++) {
  var e = SPEC.images[i];
  var f = new File(here + '/layers/' + e.file);
  if (!f.exists) { alert('Нет файла: ' + f.fsName); continue; }
  var src = app.open(f);
  var lyr = src.activeLayer.duplicate(doc, ElementPlacement.PLACEATBEGINNING);
  src.close(SaveOptions.DONOTSAVECHANGES);
  app.activeDocument = doc;
  doc.activeLayer = lyr;
  var b = lyr.bounds;
  lyr.translate(e.x - b[0].as('px'), e.y - b[1].as('px'));
  if (e.smart) { toSmart(); lyr = doc.activeLayer; }
  lyr.name = e.name;
  if (e.blend == 'multiply') lyr.blendMode = BlendMode.MULTIPLY;
  lyr.opacity = e.opacity;
  lyr.move(group(e.group), ElementPlacement.PLACEATBEGINNING);
}

// palette circles
for (var i = 0; i < SPEC.circles.length; i++) {
  var c = SPEC.circles[i], r = c.d / 2, pts = [];
  for (var k = 0; k < 96; k++) {
    var a = k / 96 * Math.PI * 2;
    pts.push([c.cx + r * Math.cos(a), c.cy + r * Math.sin(a)]);
  }
  var lyr = doc.artLayers.add();
  lyr.name = 'Круг — ' + c.name;
  doc.selection.select(pts, SelectionType.REPLACE, 0, true);
  doc.selection.fill(rgb(c.hex));
  doc.selection.deselect();
  lyr.move(group('Палитра'), ElementPlacement.PLACEATBEGINNING);
}

// text layers (point text; lines split with \r)
var missingFonts = {};
for (var i = 0; i < SPEC.texts.length; i++) {
  var t = SPEC.texts[i];
  var lyr = doc.artLayers.add();
  lyr.kind = LayerKind.TEXT;
  lyr.name = t.name;
  var ti = lyr.textItem;
  ti.contents = t.lines.join('\r');
  try { ti.font = t.font[0]; } catch (err) { missingFonts[t.font[0]] = 1; }
  ti.size = t.size;
  ti.color = rgb(t.color);
  ti.useAutoLeading = false;
  ti.leading = t.leading;
  ti.tracking = t.tracking;
  ti.position = [t.x, t.y];
  lyr.move(group(t.group), ElementPlacement.PLACEATBEGINNING);
}

app.preferences.rulerUnits = oldRuler;
app.preferences.typeUnits = oldType;
var mf = []; for (var k in missingFonts) mf.push(k);
if (mf.length) alert('Не найдены шрифты: ' + mf.join(', ') + '\nУстановите Cormorant Garamond и Inter из папки fonts и запустите заново.');
})();
'''


def write_jsx():
    with open(os.path.join(OUT, 'build_texture_board.jsx'), 'w', encoding='utf-8') as fh:
        fh.write('﻿' + JSX.replace('__SPEC__', json.dumps(SPEC, ensure_ascii=False, indent=1)))


if __name__ == '__main__':
    render_preview()
    write_jsx()
    print('ok', OUT)
