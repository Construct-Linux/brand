import os, sys
import numpy as np
import cv2
import palette

# usage: wallpaper.py [out_dir] [width] [height]
# The desktop background: the boot animation's wait - the room with its workspace grid lit -
# held still and set back behind the windows. Same camera and room as video.py; no word, the
# top bar and the dock already say whose desktop it is.
# One image per mode: the dark one is the boot's cyan on ink, quieter; the light one draws the
# room in the light accent on paper. GNOME scales them to the screen, so they are made once, at
# 4K.
OUT = sys.argv[1] if len(sys.argv) > 1 else "wallpapers"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 3840
H = int(sys.argv[3]) if len(sys.argv) > 3 else 2160
os.makedirs(OUT, exist_ok=True)
PAL = palette.load()
U = H / 1080  # design px, as in video.py

# ---------- camera and room: video.py's ----------
cam = np.array([0.6, 1.2, -2.9])
F = 620 * U * 0.82                  # a little further back than the splash: room for windows
CX = W / 2 - F * (1.5 - cam[0]) / -cam[2]  # the floor's front edge centered, as in video.py
CY = H * 0.47

def P(p):
    x, y, z = np.array(p, float) - cam
    return np.array([CX + F * x / z, CY - F * y / z])

OUTLINE = [((3, 0, 3), (0, 0, 3)), ((3, 0, 3), (3, 0, 0)), ((3, 0, 3), (3, 3, 3)),
           ((0, 0, 3), (0, 0, 0)), ((3, 0, 0), (0, 0, 0)), ((3, 3, 3), (0, 3, 3)),
           ((3, 3, 3), (3, 3, 0)), ((0, 3, 3), (0, 0, 3)), ((3, 3, 0), (3, 0, 0))]
GRID = []
for i in (1, 2):
    GRID += [((i, 0, 3), (i, 0, 0)), ((3, 0, i), (0, 0, i)),   # floor
             ((3, i, 0), (3, i, 3)), ((0, i, 3), (3, i, 3)),   # walls, rows
             ((3, 3, 3 - i), (3, 0, 3 - i)), ((3 - i, 3, 3), (3 - i, 0, 3))]  # walls, columns

SHIFT = 4
pt = lambda q: tuple(int(v) for v in np.round(np.asarray(q) * (1 << SHIFT)))

def layer(edges, width):
    m = np.zeros((H, W), np.float32)
    for a, b in edges:
        cv2.line(m, pt(P(a)), pt(P(b)), 1.0, max(1, round(width * U)), cv2.LINE_AA, SHIFT)
    return m

def rgb(h):
    return np.array(palette.rgb(h)[::-1], np.float32) / 255  # BGR, as cv2 writes

outline, grid = layer(OUTLINE, 3), layer(GRID, 2)
# (background, lines, outline level, grid level, glow): the dark one glows like the splash,
# the light one is ink on paper and does not
MODES = {
    "dark": (PAL["brand"]["ink"], PAL["dark"]["accent"], 0.55, 0.22, 0.6),
    "light": (PAL["brand"]["paper"], PAL["light"]["accent"], 0.45, 0.16, 0.0),
}
for mode, (bg, ink, lo, lg, glow) in MODES.items():
    lines = np.maximum(outline * lo, grid * lg)
    if glow:
        lines = lines + sum(cv2.GaussianBlur(lines, (0, 0), s * U) * w for s, w in ((6, 0.6), (24, 0.35))) * glow
    a = np.clip(lines, 0, 1)[..., None]
    img = rgb(bg) + (rgb(ink) - rgb(bg)) * a
    cv2.imwrite(f"{OUT}/construct-{mode}.png", (img * 255).round().astype(np.uint8),
                [cv2.IMWRITE_PNG_COMPRESSION, 9])
print(f"{OUT}/: construct-dark.png, construct-light.png ({W}x{H})")
