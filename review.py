import json, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import video

# usage: review.py [frames_dir] [out_dir]
# Review sheets for the identity and the boot animation:
#   comparison.png - key moments of the splash (first second, waiting, end = logo), the
#                    logo next to the last frame, and the identity tagline (not in the splash)
#   sequence.png   - every frame grouped by segment (intro / loop / outro) with the light
#                    levels of the two layers: outline (base image) and grid (workspace)
FRAMES = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "review"
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
    """items: [(image, label)]"""
    r = Image.new("RGB", (W, 100 + T + 50), INK)
    d = ImageDraw.Draw(r)
    caption(d, (pad, 28), title, sub)
    for k, (im, label) in enumerate(items):
        x = pad + k * (T + pad)
        r.paste(im.resize((T, T), Image.LANCZOS), (x, 100))
        d.text((x, 100 + T + 14), label, font=font(12), fill=TEXT)
    rows.append(r)

loop_mid = (segments["loop"][0] + segments["loop"][1]) // 2
row("El splash", "La marca se reconoce desde el primer segundo; la grilla vive dentro del contorno y se apaga al final.",
    [(frame(FRAMES, 7), "Frame 7: contorno cerrado"), (frame(FRAMES, 10), "Frame 10: contorno + palabra"),
     (frame(FRAMES, loop_mid), f"Frame {loop_mid}: espera, espacio activo")])
row("Logo = último frame", "El símbolo es el contorno: la base estable. La grilla (el espacio de trabajo) vive solo en la animación.",
    [(Image.open("logos/construct-neon-512.png").convert("RGB"), "Símbolo"), (frame(FRAMES, n), f"Frame {n}: cierre del splash")])

# Identity tagline, rendered on the final frame for review only.
tags = [None, "the workspace.\nthe image, verified."]
notes = ["Sin tagline (splash)", "Con tagline - identidad"]
tw = (W - pad * (len(tags) + 1)) // len(tags)
r = Image.new("RGB", (W, 100 + tw + 50), INK)
d = ImageDraw.Draw(r)
caption(d, (pad, 28), "Tagline - identidad", "the workspace. / the image, verified. - en dos líneas, fuera del splash.")
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
