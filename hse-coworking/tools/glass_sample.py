#!/usr/bin/env python3
"""Lilac glass sample as a transparent PNG.

The tint is measured from source/08-lilac-glass.jpg (stone seen through the glass
vs. the same stone outside it), so the pane is the real glass colour, not a guess.
Outputs (cutouts/):
  glass-lilac.png          — one layer, Normal blend: drag onto the board
  glass-lilac-tint.png     — tint only, for Multiply blend (most physically right)
  glass-lilac-shine.png    — reflections + edges, for Screen/Normal on top
  glass-lilac-demo.jpg     — the pane laid over other samples to show transparency
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cutouts')
os.makedirs(OUT, exist_ok=True)

# transmittance measured from the photo: glass-over-stone / bare stone ≈ (.70,.46,.70),
# glass-over-plaster ≈ (.79,.63,.78); averaged and nudged to the lilac of the booths
T = np.array([.78, .64, .87], np.float32)
EDGE = np.array([58, 26, 72], np.float32)        # dark violet edge line seen on the panes

Wp, Hp, TH = 900, 1200, 26                         # pane size and visible thickness (px @300dpi)
PAD = 40
W, H = Wp + TH + PAD * 2, Hp + TH + PAD * 2
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

face = np.zeros((H, W), bool); face[PAD:PAD + Hp, PAD:PAD + Wp] = True
side = np.zeros((H, W), bool)
for k in range(1, TH + 1):                          # thickness, light from top-left
    side[PAD + k:PAD + Hp + k, PAD + int(k * .45):PAD + Wp + int(k * .45)] = True
side &= ~face

# --- tint layer (Multiply): colour = 255*T, alpha 255 on the face, deeper on the edge
tint = np.zeros((H, W, 4), np.float32)
tint[face, :3] = 255 * T
tint[face, 3] = 255
tint[side, :3] = 255 * T ** 2.2                     # light travels through more glass at the edge
tint[side, 3] = 255

# --- shine layer: soft diagonal sheen + crisp edge highlights
u = (xx - PAD) / Wp; v = (yy - PAD) / Hp
sheen = .30 * np.exp(-((u + v * .55 - .42) / .07) ** 2) + .12 * np.exp(-((u + v * .55 - .62) / .03) ** 2)
sheen += .05 * np.exp(-((u - .9) / .2) ** 2)
shine = np.zeros((H, W, 4), np.float32)
shine[..., :3] = 255
shine[face, 3] = 255 * sheen[face]
im_sh = Image.fromarray(shine.astype(np.uint8), 'RGBA')
d = ImageDraw.Draw(im_sh)
d.line([(PAD, PAD), (PAD + Wp, PAD)], fill=(255, 255, 255, 230), width=3)          # lit top edge
d.line([(PAD, PAD), (PAD, PAD + Hp)], fill=(255, 255, 255, 190), width=3)          # lit left edge
d.line([(PAD + Wp - 1, PAD), (PAD + Wp - 1, PAD + Hp)], fill=tuple(EDGE.astype(int)) + (230,), width=3)
d.line([(PAD, PAD + Hp - 1), (PAD + Wp, PAD + Hp - 1)], fill=tuple(EDGE.astype(int)) + (230,), width=3)
im_sh = im_sh.filter(ImageFilter.GaussianBlur(.6))

im_tint = Image.fromarray(tint.astype(np.uint8), 'RGBA')
im_tint.save(os.path.join(OUT, 'glass-lilac-tint.png'))
im_sh.save(os.path.join(OUT, 'glass-lilac-shine.png'))

# --- single Normal-mode layer that reproduces Multiply over a light board (B≈#ECE6DD)
B = np.array([236, 230, 221], np.float32)
A_FACE, A_SIDE = .50, .82
one = np.zeros((H, W, 4), np.float32)
for m, A, Tm in ((face, A_FACE, T), (side, A_SIDE, T ** 2.2)):
    C = (B * Tm - (1 - A) * B) / A
    one[m, :3] = np.clip(C, 0, 255); one[m, 3] = 255 * A
base = Image.fromarray(one.astype(np.uint8), 'RGBA')
base.alpha_composite(im_sh)
base.save(os.path.join(OUT, 'glass-lilac.png'))

# --- demo: lay the pane over a tile + parquet stub on the board colour
demo = Image.new('RGB', (W + 500, H + 200), tuple(B.astype(int)))
dd = ImageDraw.Draw(demo)
dd.polygon([(120, 300), (720, 300), (120, 900)], fill=(60, 65, 71))            # graphite half of a cement tile
dd.polygon([(720, 300), (720, 900), (120, 900)], fill=(217, 209, 196))
dd.rectangle([700, 1000, 1350, 1150], fill=(200, 151, 106))                    # an oak plank
dd.rectangle([1150, 200, 1300, 900], fill=(40, 38, 36))                        # black velvet strip
dd.rectangle([1300, 200, 1400, 900], fill=(239, 230, 214))
demo = demo.convert('RGBA')
demo.alpha_composite(base, (330, 60))
demo.convert('RGB').resize(((W + 500) // 2, (H + 200) // 2), Image.LANCZOS).save(
    os.path.join(OUT, 'glass-lilac-demo.jpg'), quality=90)
print('ok')
