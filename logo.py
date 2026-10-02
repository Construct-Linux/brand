import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# usage: logo.py [out_dir]
# The Construct mark: the animation's last frame without the grid - the room in outline,
# open on the left. Same one-point camera as video.py. The strokes live in a 0..100 box;
# they are written as SVG (color + mono) and rendered to PNG at icon sizes.
OUT = sys.argv[1] if len(sys.argv) > 1 else "logos"
os.makedirs(OUT, exist_ok=True)

CYAN = "#00E5FF"
INK = "#0B1116"     # dark background for previews
PAPER = "#F4F6F8"   # light background for mono previews
FONT = os.environ.get("FONT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Audiowide-Regular.ttf")  # OFL, same as video.py

# ---------- camera from video.py: room = cube 3x3x3, looking straight down +z ----------
CAM = np.array([0.6, 1.2, -2.9])  # same camera as video.py

def proj(p):
    x, y, z = np.array(p, float) - CAM
    return np.array([x / z, -y / z])

def mark(lines3d):
    """Project 3D strokes and normalize them into the 0..100 box (aspect kept)."""
    lines = [(proj(a), proj(b)) for a, b in lines3d]
    pts = np.array([p for l in lines for p in l])
    lo, hi = pts.min(0), pts.max(0)
    s = 100 / (hi - lo).max()
    off = (100 - (hi - lo) * s) / 2 - lo * s
    return [(a * s + off, b * s + off) for a, b in lines]

BACK = [((0, 0, 3), (3, 0, 3)), ((0, 0, 3), (0, 3, 3)), ((0, 3, 3), (3, 3, 3)), ((3, 0, 3), (3, 3, 3))]
FLOOR = [((0, 0, 0), (3, 0, 0)), ((0, 0, 0), (0, 0, 3)), ((3, 0, 0), (3, 0, 3))]
RIGHT = [((3, 0, 0), (3, 3, 0)), ((3, 3, 0), (3, 3, 3))]
LINES = mark(BACK + FLOOR + RIGHT)
NAME = "construct"

# ---------- output ----------
def chain(segments, eps=1e-6):
    """Join segments that share endpoints into continuous strokes (polylines), so corners
    are real joins instead of separate lines meeting. Returns (points, closed) pairs."""
    segs = [(np.asarray(a, float), np.asarray(b, float)) for a, b in segments]
    same = lambda p, q: np.linalg.norm(p - q) < eps
    out = []
    while segs:
        a, b = segs.pop(0)
        pts = [a, b]
        grown = True
        while grown:
            grown = False
            for i, (c, d) in enumerate(segs):
                for (u, v) in ((c, d), (d, c)):
                    if same(pts[-1], u): pts.append(v)
                    elif same(pts[0], v): pts.insert(0, u)
                    else: continue
                    segs.pop(i); grown = True; break
                if grown: break
        closed = len(pts) > 2 and same(pts[0], pts[-1])
        out.append((pts[:-1] if closed else pts, closed))
    return out

def svg(lines, color, stroke=1.2):
    d = " ".join("M" + " L".join(f"{p[0]:.2f} {p[1]:.2f}" for p in pts) + (" Z" if closed else "")
                 for pts, closed in chain(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 112 112">\n'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n')

def hex2bgr(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (4, 2, 0))

def stroke_px(size):
    # Large: a fine line, ~1% of the mark like the animation's grid. Icon sizes: whole pixels -
    # 1 px only at 16, where 2 would fill the mark; from 24 to 64 two, or the line fades into
    # the background (a 1 px cyan stroke at 32 px all but vanished).
    if size <= 16:
        return 1
    if size <= SMALL:
        return 2
    return max(1.0, size * 0.011)

SMALL = 64  # at or below this size, lines are snapped to the pixel grid (crisp icon)

def snap(lines, size):
    """Move endpoints onto the pixel grid so verticals and horizontals cover whole pixels: a
    1 px line on a pixel's center, a 2 px one on the edge between two."""
    off = 0.5 if stroke_px(size) % 2 else 0.0
    c = lambda v: (np.floor((v + 6) * size / 112) + off) * 112 / size - 6
    return [(c(np.asarray(a)), c(np.asarray(b))) for a, b in lines]

def render(lines, size, color, bg, neon=False):
    ss = 8
    small = size <= SMALL
    if small:
        lines = snap(lines, size)
    S = size * ss
    k = S / 112
    T = lambda p: (int(round((p[0] + 6) * k * 16)), int(round((p[1] + 6) * k * 16)))
    ink = np.zeros((S, S), np.float32)
    w = int(round(stroke_px(size) * ss))  # whole pixels when small
    for pts, closed in chain(lines):
        cv2.polylines(ink, [np.array([T(p) for p in pts], np.int32)], closed, 1.0, w, cv2.LINE_AA, 4)
    if neon:  # soft halo like the boot animation
        ink = ink + sum(cv2.GaussianBlur(ink, (0, 0), size * ss * r) * a for r, a in ((0.005, 0.8), (0.015, 0.5), (0.035, 0.25)))
    a = cv2.resize(np.clip(ink, 0, 1), (size, size), interpolation=cv2.INTER_AREA)[..., None]
    c, b = np.array(hex2bgr(color), np.float32), np.array(hex2bgr(bg), np.float32)
    return (b + (c - b) * a).round().astype(np.uint8)

def symbolic(lines):
    """GNOME's symbolic icon: the mark on a 16 px grid, one color GTK replaces with the
    theme's (#2e3436 is the one it looks for), a stroke thick enough to read at 16 px."""
    d = " ".join("M" + " L".join(f"{(p[0] + 6) * 16 / 112:.2f} {(p[1] + 6) * 16 / 112:.2f}" for p in pts) + (" Z" if closed else "")
                 for pts, closed in chain(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">\n'
            f'<path d="{d}" fill="none" stroke="#2e3436" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n')

SIZES = [512, 128, 64, 48, 32, 24, 16]
for variant, color in (("", CYAN), ("-mono", "currentColor")):
    open(f"{OUT}/{NAME}{variant}.svg", "w").write(svg(LINES, color))
open(f"{OUT}/{NAME}-symbolic.svg", "w").write(symbolic(LINES))
for s in SIZES:
    cv2.imwrite(f"{OUT}/{NAME}-{s}.png", render(LINES, s, CYAN, INK))
cv2.imwrite(f"{OUT}/{NAME}-neon-512.png", render(LINES, 512, CYAN, INK, neon=True))

# ---------- preview sheet: sizes on dark + mono on light + lockup ----------
def to_pil(im):
    return Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))

def lockup(h, color, bg, text_color, neon=False):
    font = ImageFont.truetype(FONT, int(h * 0.2))
    track = font.size * 0.35  # same letter spacing as the animation
    tw = int(font.getlength("CONSTRUCT") + 8 * track + h * 0.15)
    canvas = Image.new("RGB", (h + int(h * 0.25) + tw, h), bg)
    canvas.paste(to_pil(render(LINES, h, color, bg, neon)), (0, 0))
    d = ImageDraw.Draw(canvas)
    x = h + int(h * 0.25)
    for ch in "CONSTRUCT":
        d.text((x, h * 0.5), ch, font=font, fill=text_color, anchor="lm")
        x += font.getlength(ch) + track
    return canvas

W = 1500
sheet = Image.new("RGB", (W, 560), INK)
d = ImageDraw.Draw(sheet)
note_font = ImageFont.truetype(FONT, 12)
d.text((30, 22), NAME.upper(), font=ImageFont.truetype(FONT, 20), fill=CYAN)
d.text((30, 54), "The animation's last frame without the grid: the room in outline, open on the left.", font=note_font, fill="#9FB3C0")
x = 30
for s in [256, 128, 64, 48, 32, 24, 16]:  # actual pixels, on dark
    sheet.paste(to_pil(render(LINES, s, CYAN, INK, neon=s == 256)), (x, 100 + 256 - s))
    d.text((x, 370), f"{s}px", font=note_font, fill="#5F7380")
    x += s + 30
big = cv2.resize(render(LINES, 16, CYAN, INK), (128, 128), interpolation=cv2.INTER_NEAREST)  # 16 px x8
sheet.paste(to_pil(big), (x + 10, 228))
d.text((x + 10, 370), "16px x8", font=note_font, fill="#5F7380")
sheet.paste(to_pil(render(LINES, 128, "#11181E", PAPER)), (W - 30 - 128, 228))
d.text((W - 30 - 128, 370), "mono", font=note_font, fill="#5F7380")
sheet.paste(lockup(120, CYAN, INK, "#FFFFFF", neon=True), (30, 410))
lk = lockup(120, "#11181E", PAPER, "#11181E")
sheet.paste(lk, (W - 30 - lk.width, 410))
sheet.save(f"{OUT}/preview.png")
print(f"{OUT}/: {NAME} -> svg, mono and symbolic svg, png {SIZES}, neon, preview.png")
