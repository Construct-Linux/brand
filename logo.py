import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# usage: logo.py [out_dir]
# Logo proposals for Construct. Same one-point camera as the animation (video.py), so the
# mark is a frame of the same world. Each mark is a list of strokes plus accent strokes
# (heavier: the lit entrance) in a 0..100 box; it is written as SVG (color + mono) and rendered to PNG at icon sizes.
OUT = sys.argv[1] if len(sys.argv) > 1 else "logos"
os.makedirs(OUT, exist_ok=True)

CYAN = "#00E5FF"
INK = "#0B1116"     # dark background for previews
PAPER = "#F4F6F8"   # light background for mono previews
FONT = os.environ.get("FONT") or next(p for p in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    os.path.expanduser("~/Library/Fonts/DejaVuSans-Bold.ttf"),
    "/Library/Fonts/DejaVuSans-Bold.ttf",
] if os.path.exists(p))

# ---------- camera from video.py: room = cube 3x3x3, looking straight down +z ----------
CAM = np.array([0.6, 1.2, -2.9])  # same camera as video.py ("lado abierto")

def proj(p, cam):
    x, y, z = np.array(p, float) - cam
    return np.array([x / z, -y / z])

def mark(lines3d, accents3d, cam=CAM, pad=0.0):
    """Project 3D strokes and normalize them into the 0..100 box (aspect kept)."""
    lines = [(proj(a, cam), proj(b, cam)) for a, b in lines3d]
    accents = [(proj(a, cam), proj(b, cam)) for a, b in accents3d]
    pts = np.array([p for l in lines + accents for p in l])
    lo, hi = pts.min(0), pts.max(0)
    s = (100 - 2 * pad) / (hi - lo).max()
    off = (100 - (hi - lo) * s) / 2 - lo * s
    n = lambda p: p * s + off
    return [(n(a), n(b)) for a, b in lines], [(n(a), n(b)) for a, b in accents]

MARKS = {}

BACK = [((0, 0, 3), (3, 0, 3)), ((0, 0, 3), (0, 3, 3)), ((0, 3, 3), (3, 3, 3)), ((3, 0, 3), (3, 3, 3))]
FLOOR = [((0, 0, 0), (3, 0, 0)), ((0, 0, 0), (0, 0, 3)), ((3, 0, 0), (3, 0, 3))]
RIGHT = [((3, 0, 0), (3, 3, 0)), ((3, 3, 0), (3, 3, 3))]
ROOM = BACK + FLOOR + RIGHT

def door(z0, z1, h=2):
    """Entrance in the right wall (x=3) between depths z0..z1, as in the animation."""
    return [(3, 0, z0), (3, h, z0), (3, h, z1), (3, 0, z1)]

def outline(poly):
    return [(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]

def centered_door(cam=CAM, frac=0.29):
    """Entrance centered on the right wall *as seen* (perspective squeezes the far half, so
    the 3D-centered z 1..2 looks pushed to the back). Same door as video.py.
    frac = door width / wall width on screen."""
    X = lambda z: (3 - cam[0]) / (z - cam[2])   # screen x of the right wall at depth z
    Z = lambda x: (3 - cam[0]) / x + cam[2]     # inverse
    near, far = X(0), X(3)
    mid, half = (near + far) / 2, (near - far) * frac / 2
    return door(Z(mid + half), Z(mid - half))

# The mark: the animation's last frame without the grid - the room in outline, open on the
# left, the entrance in the right wall as a lit frame (jambs + lintel), opening left clear
MARKS["construct"] = (*mark(ROOM, outline(centered_door())),
    "El último frame de la animación sin rejilla: el cuarto en trazo, abierto a la izquierda, y la entrada en la pared derecha como un marco encendido, sin relleno.")

# ---------- output ----------
ACCENT = 2.2  # the entrance frame is this much heavier than the room lines

def svg(lines, accents, color, stroke=1.2, bg=None):
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 112 112">']
    if bg: out.append(f'<rect x="-6" y="-6" width="112" height="112" fill="{bg}"/>')
    out.append(f'<g fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">')
    out += [f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}"/>' for a, b in lines]
    out.append('</g>')
    out.append(f'<g fill="none" stroke="{color}" stroke-width="{stroke * ACCENT:.2f}" stroke-linecap="round" stroke-linejoin="round">')
    out += [f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}"/>' for a, b in accents]
    out.append('</g>')
    out.append('</svg>')
    return "\n".join(out) + "\n"

def hex2bgr(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (4, 2, 0))

def stroke_px(size):
    # fine line, ~1% of the mark like the animation's grid; never below 1 px so it survives 16 px
    return max(1.0, size * 0.011)

def render(lines, accents, size, color, bg, neon=False):
    ss = 8
    S = size * ss
    k = S / 112
    T = lambda p: (int(round((p[0] + 6) * k * 16)), int(round((p[1] + 6) * k * 16)))
    ink = np.zeros((S, S), np.float32)
    w = max(1, int(round(stroke_px(size) * ss)))
    for a, b in lines:
        cv2.line(ink, T(a), T(b), 1.0, w, cv2.LINE_AA, 4)
    for a, b in accents:
        cv2.line(ink, T(a), T(b), 1.0, max(1, int(round(w * ACCENT))), cv2.LINE_AA, 4)
    if neon:  # soft halo like the boot animation
        ink = ink + sum(cv2.GaussianBlur(ink, (0, 0), size * ss * r) * a for r, a in ((0.005, 0.8), (0.015, 0.5), (0.035, 0.25)))
    a = cv2.resize(np.clip(ink, 0, 1), (size, size), interpolation=cv2.INTER_AREA)[..., None]
    c, b = np.array(hex2bgr(color), np.float32), np.array(hex2bgr(bg), np.float32)
    return (b + (c - b) * a).round().astype(np.uint8)

SIZES = [512, 128, 64, 48, 32, 16]
for name, (lines, accents, _) in MARKS.items():
    for variant, color in (("", CYAN), ("-mono", "currentColor")):
        open(f"{OUT}/{name}{variant}.svg", "w").write(svg(lines, accents, color))
    for s in SIZES:
        cv2.imwrite(f"{OUT}/{name}-{s}.png", render(lines, accents, s, CYAN, INK))
    cv2.imwrite(f"{OUT}/{name}-neon-512.png", render(lines, accents, 512, CYAN, INK, neon=True))

# ---------- preview sheet: per mark, sizes on dark + mono on light + lockup ----------
TEXT_FONT = FONT.replace("-Bold", "") if os.path.exists(FONT.replace("-Bold", "")) else FONT

def lockup(lines, accents, h, color, bg, text_color, neon=False):
    m = render(lines, accents, h, color, bg, neon)
    font = ImageFont.truetype(TEXT_FONT, int(h * 0.26))  # regular weight, to match the fine line
    tw = int(font.getlength("CONSTRUCT") + 8 * h * 0.08 + h * 0.15)
    canvas = Image.new("RGB", (h + int(h * 0.25) + tw, h), bg)
    canvas.paste(Image.fromarray(cv2.cvtColor(m, cv2.COLOR_BGR2RGB)), (0, 0))
    d = ImageDraw.Draw(canvas)
    x = h + int(h * 0.25)
    for ch in "CONSTRUCT":
        d.text((x, h * 0.5), ch, font=font, fill=text_color, anchor="lm")
        x += font.getlength(ch) + h * 0.08
    return canvas

W = 1500
rows = []
label_font = ImageFont.truetype(FONT, 22)
note_font = ImageFont.truetype(FONT.replace("-Bold", ""), 17) if os.path.exists(FONT.replace("-Bold", "")) else label_font
for name, (lines, accents, note) in MARKS.items():
    row = Image.new("RGB", (W, 560), INK)
    d = ImageDraw.Draw(row)
    d.text((30, 22), name.upper(), font=label_font, fill=CYAN)
    d.text((30, 54), note, font=note_font, fill="#9FB3C0")
    # sizes, actual pixels, on dark
    x = 30
    for s in [256, 128, 64, 48, 32, 16]:
        im = render(lines, accents, s, CYAN, INK, neon=s == 256)
        row.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), (x, 100 + 256 - s))
        d.text((x, 370), f"{s}px", font=note_font, fill="#5F7380")
        x += s + 30
    # 16px blown up 8x to judge legibility
    tiny = render(lines, accents, 16, CYAN, INK)
    big = cv2.resize(tiny, (128, 128), interpolation=cv2.INTER_NEAREST)
    row.paste(Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)), (x + 10, 228))
    d.text((x + 10, 370), "16px x8", font=note_font, fill="#5F7380")
    # mono on light
    mono = render(lines, accents, 128, "#11181E", PAPER)
    row.paste(Image.fromarray(cv2.cvtColor(mono, cv2.COLOR_BGR2RGB)), (W - 30 - 128, 228))
    d.text((W - 30 - 128, 370), "mono", font=note_font, fill="#5F7380")
    # lockups
    row.paste(lockup(lines, accents, 120, CYAN, INK, "#FFFFFF", neon=True), (30, 410))
    lk = lockup(lines, accents, 120, "#11181E", PAPER, "#11181E")
    row.paste(lk, (W - 30 - lk.width, 410))
    rows.append(row)
sheet = Image.new("RGB", (W, sum(r.height for r in rows) + 6 * (len(rows) - 1)), "#222A30")
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height + 6
sheet.save(f"{OUT}/preview.png")
print(f"{OUT}/: {len(MARKS)} marks -> svg, mono svg, png {SIZES}, preview.png")
