import json, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import video

# usage: review.py [frames_dir] [before_dir] [out_dir]
# Review sheets for the identity and the boot animation:
#   comparison.png - before / after (end of the splash, the first second, the logo) and
#                    tagline explorations on the final frame (not part of the splash)
#   sequence.png   - every frame grouped by segment (intro / loop / outro) with the light
#                    levels of the two layers: outline (base image) and grid (workspace)
# before_dir is optional: a copy of a previous frames/ (frames_dir layout) to compare with.
FRAMES = sys.argv[1] if len(sys.argv) > 1 else "frames"
BEFORE = sys.argv[2] if len(sys.argv) > 2 else ""
OUT = sys.argv[3] if len(sys.argv) > 3 else "review"
os.makedirs(OUT, exist_ok=True)

INK, LINE, MUTED, TEXT, CYAN = "#0B1116", "#1C252C", "#5F7380", "#C9D6DE", "#00E5FF"
font = lambda s: ImageFont.truetype(video.FONT, s)
segments = json.load(open(f"{FRAMES}/segments.json"))
n = max(b for a, b in segments.values())
frame = lambda d, i: Image.open(f"{d}/construct_{i:02d}.png").convert("RGB")

def caption(d, xy, title, sub=None):
    d.text(xy, title, font=font(18), fill=CYAN)
    if sub:
        d.text((xy[0], xy[1] + 28), sub, font=font(12), fill=MUTED)

# ---------- comparison ----------
T = 420  # thumbnail size
pad = 40
cols = 3
W = pad + cols * (T + pad)
rows = []

def row(title, sub, items):
    """items: [(image or None, label)]"""
    r = Image.new("RGB", (W, 100 + T + 50), INK)
    d = ImageDraw.Draw(r)
    caption(d, (pad, 28), title, sub)
    for k, (im, label) in enumerate(items):
        x = pad + k * (T + pad)
        if im is not None:
            r.paste(im.resize((T, T), Image.LANCZOS), (x, 100))
        else:
            d.rectangle((x, 100, x + T, 100 + T), outline=LINE)
            d.text((x + T / 2, 100 + T / 2), "sin versión anterior", font=font(12), fill=MUTED, anchor="mm")
        d.text((x, 100 + T + 14), label, font=font(12), fill=TEXT)
    rows.append(r)

has_before = BEFORE and os.path.exists(f"{BEFORE}/construct_48.png")
b = (lambda i: frame(BEFORE, i)) if has_before else (lambda i: None)
loop_mid = (segments["loop"][0] + segments["loop"][1]) // 2
row("Final del splash", "Antes: grilla encendida y tagline.  Ahora: la grilla se apaga y queda el símbolo con la palabra.",
    [(b(48), "Antes - frame 48"), (frame(FRAMES, loop_mid), f"Ahora - espera (frame {loop_mid})"), (frame(FRAMES, n), f"Ahora - frame {n}")])
row("El primer segundo", "Si el arranque termina temprano, ¿se reconoce la marca?",
    [(b(10), "Antes - frame 10"), (frame(FRAMES, 7), "Ahora - frame 7: contorno cerrado"), (frame(FRAMES, 10), "Ahora - frame 10: contorno + palabra")])
logo = Image.open("logos/construct-neon-512.png").convert("RGB") if os.path.exists("logos/construct-neon-512.png") else None
row("Logo = último frame", "El símbolo es el contorno: la base estable. La grilla (el espacio de trabajo) vive solo en la animación.",
    [(logo, "Símbolo"), (frame(FRAMES, n), "Splash, último frame"), (frame(FRAMES, loop_mid), "Splash, espacio activo")])

# tagline explorations, rendered on the final frame (review only)
tags = [None, "Your workspace on the grid", "Una base firme. Tu espacio para construir", "A solid base. Your space to build"]
notes = ["Sin tagline (splash actual)", "Anterior: habla solo del interior", "Exploración: nombra base y espacio", "Exploración, en inglés"]
tw = (W - pad * 5) // 4
r = Image.new("RGB", (W, 100 + tw + 50), INK)
d = ImageDraw.Draw(r)
caption(d, (pad, 28), "Tagline - exploración", "No incorporado al splash. Solo para evaluar dirección y peso.")
for k, (tag, note) in enumerate(zip(tags, notes)):
    im = Image.fromarray(cv2.cvtColor(video.render(n - 1, tagline=tag), cv2.COLOR_BGR2RGB))
    x = pad + k * (tw + pad)
    r.paste(im.resize((tw, tw), Image.LANCZOS), (x, 100))
    d.text((x, 100 + tw + 14), note, font=font(12), fill=TEXT)
rows.append(r)

sheet = Image.new("RGB", (W, sum(x.height for x in rows) + 4 * (len(rows) - 1)), LINE)
y = 0
for x in rows:
    sheet.paste(x, (0, y)); y += x.height + 4
sheet.save(f"{OUT}/comparison.png")

# ---------- sequence ----------
t = 200
per_row = 12
labels = {"intro": "INTRO - una vez: contorno, palabra, grilla, activación",
          "loop": "ESPERA - se repite mientras arranca; sin dirección, sin costura",
          "outro": "CIERRE - la grilla se apaga; queda el logo"}
blocks = []
for seg, (a, bb) in segments.items():
    ids = list(range(a, bb + 1))
    nrows = (len(ids) + per_row - 1) // per_row
    blk = Image.new("RGB", (pad * 2 + per_row * (t + 8), 70 + nrows * (t + 30)), INK)
    d = ImageDraw.Draw(blk)
    caption(d, (pad, 22), labels[seg])
    for k, i in enumerate(ids):
        x = pad + (k % per_row) * (t + 8)
        y = 70 + (k // per_row) * (t + 30)
        blk.paste(frame(FRAMES, i).resize((t, t), Image.LANCZOS), (x, y))
        d.text((x + 6, y + 4), str(i), font=font(12), fill=TEXT)
    blocks.append(blk)

# light levels of the two layers, frame by frame
Wc = blocks[0].width
ch = Image.new("RGB", (Wc, 260), INK)
d = ImageDraw.Draw(ch)
caption(d, (pad, 22), "Niveles de luz", "Contorno (base) fijo desde que se cierra. Grilla (espacio): trazo, activación, respiración, salida.")
x0, x1, y0, y1 = pad, Wc - pad, 90, 230
d.rectangle((x0, y0, x1, y1), outline=LINE)
X = lambda f: x0 + (x1 - x0) * f / (n - 1)
Y = lambda v: y1 - (y1 - y0) * v
for seg, (a, bb) in segments.items():
    d.line((X(a - 1), y0, X(a - 1), y1), fill=LINE)
    d.text((X(a - 1) + 6, y1 + 6), seg, font=font(11), fill=MUTED)
outline = [min(1, max(0, (f - video.OUTLINE[0]) / (video.OUTLINE[1] - video.OUTLINE[0]))) for f in range(n)]
gridl = [video.grid_level(f) if f >= video.FLOOR[0] else 0 for f in range(n)]
d.line([(X(f), Y(v)) for f, v in enumerate(outline)], fill=CYAN, width=3)
d.line([(X(f), Y(v)) for f, v in enumerate(gridl)], fill="#7FB8C4", width=2)
d.text((x1 - 260, y0 + 8), "contorno", font=font(11), fill=CYAN)
d.text((x1 - 140, y0 + 8), "grilla", font=font(11), fill="#7FB8C4")
blocks.append(ch)

seq = Image.new("RGB", (Wc, sum(x.height for x in blocks) + 4 * (len(blocks) - 1)), LINE)
y = 0
for x in blocks:
    seq.paste(x, (0, y)); y += x.height + 4
seq.save(f"{OUT}/sequence.png")
print(f"{OUT}/: comparison.png, sequence.png")
