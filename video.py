import numpy as np, cv2, os, sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
SS = 2  # supersampling
FONT = "fonts/Michroma.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"
os.makedirs(OUT, exist_ok=True)
N = 48
CYAN = np.array([1.0, 0.90, 0.0])  # BGR -> cyan (#00E5FF)

# ---------- camera: room = cube 3x3x3, x right, y up, z depth (z=0 open front) ----------
cam = np.array([0.55, 1.75, -2.6])
target = np.array([1.9, 1.15, 2.4])
fwd = target - cam; fwd /= np.linalg.norm(fwd)
right = np.cross([0, 1, 0], fwd); right /= np.linalg.norm(right)
up = np.cross(fwd, right)
F = 700 * SS
CX, CY = W * SS * 0.47, H * SS * 0.41

def P(p):
    d = np.array(p, float) - cam
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([CX + F * x / z, CY - F * y / z])

def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)

def prog(f, a, b):
    return ease((f - a) / max(b - a, 1e-6))

# segment list: (p0, p1, start, end, maxlen, alpha)
segs = []
def S(p0, p1, a, b, maxlen=1.0, alpha=1.0):
    segs.append((np.array(p0, float), np.array(p1, float), a, b, maxlen, alpha))

g = [0, 1, 2, 3]
# 1) three edges from back-right-bottom corner (3,0,3)
S((3, 0, 3), (0, 0, 3), 8, 16)      # floor back edge
S((3, 0, 3), (3, 3, 3), 8, 16)      # back-right vertical
S((3, 0, 3), (3, 0, 0), 8, 16)      # floor/right-wall seam
# 2) rest of floor outline
S((0, 0, 3), (0, 0, 0), 13, 19)     # floor/left seam
S((3, 0, 0), (0, 0, 0), 13, 19)     # floor front edge
# 3) floor grid
for i in (1, 2):
    S((i, 0, 3), (i, 0, 0), 17, 23)  # columns (back -> front)
    S((3, 0, i), (0, 0, i), 18, 24)  # rows (right -> left)
# 4) right wall outline (x=3)
S((3, 0, 0), (3, 3, 0), 21, 27)     # front vertical
S((3, 3, 3), (3, 3, 0), 22, 28)     # top edge
# 5) right wall grid: verticals continue floor rows, horizontals
for i in (1, 2):
    S((3, 0, i), (3, 3, i), 25, 31)
    S((3, i, 3), (3, i, 0), 26, 32)
# 6) back wall (z=3)
S((0, 0, 3), (0, 3, 3), 28, 34)     # back-left vertical
S((3, 3, 3), (0, 3, 3), 29, 35)     # top edge
for i in (1, 2):
    S((i, 0, 3), (i, 3, 3), 31, 37)  # verticals continue floor columns
    S((3, i, 3), (0, i, 3), 32, 38)  # horizontals continue right-wall rows
# 7) left wall (x=0) – deliberately incomplete
S((0, 0, 0), (0, 3, 0), 34, 41, 0.55, 0.85)
S((0, 3, 3), (0, 3, 0), 35, 42, 0.40, 0.70)
S((0, 0, 1), (0, 3, 1), 36, 42, 0.70, 0.80)
S((0, 0, 2), (0, 3, 2), 35, 41, 0.35, 0.75)
S((0, 1, 3), (0, 1, 0), 36, 43, 0.85, 0.85)
S((0, 2, 3), (0, 2, 0), 37, 43, 0.30, 0.60)

# door: right wall, middle column (z 1..2), two lower rows (y 0..2)
DOOR = [(3, 0, 1), (3, 2, 1), (3, 2, 2), (3, 0, 2)]
DOOR_A, DOOR_B = 36, 44
TEXT_A, TEXT_B = 40, 46
CORNER_A, CORNER_B = 4, 9

def glow(img):
    out = img.copy()
    for k, w in ((9, 0.9), (31, 0.7), (91, 0.55)):
        out += cv2.GaussianBlur(img, (0, 0), k * SS / 3) * w
    return out

def render(f):
    lines = np.zeros((H * SS, W * SS, 3), np.float32)
    fill = np.zeros_like(lines)
    lw = 3 * SS
    # starting point of light
    c = prog(f, CORNER_A, CORNER_B)
    fade = 1 - 0.6 * prog(f, 14, 20)
    if c > 0:
        p = P((3, 0, 3)).astype(int)
        cv2.circle(lines, tuple(p), int(5 * SS), (c * fade,) * 3, -1, cv2.LINE_AA)
    for p0, p1, a, b, ml, al in segs:
        t = prog(f, a, b) * ml
        if t <= 0: continue
        q0, q1 = P(p0), P(p0 + (p1 - p0) * t)
        # fading tail for incomplete left-wall lines
        if ml < 1:
            n = 12
            for k in range(n):
                s0, s1 = k / n, (k + 1) / n
                aa = al * (1 - s0 * 0.85)
                cv2.line(lines, tuple((q0 + (q1 - q0) * s0).astype(int)),
                         tuple((q0 + (q1 - q0) * s1).astype(int)), (aa,) * 3, lw, cv2.LINE_AA)
        else:
            cv2.line(lines, tuple(q0.astype(int)), tuple(q1.astype(int)), (al,) * 3, lw, cv2.LINE_AA)
            # bright drawing head
            if 0 < t < 1:
                cv2.circle(lines, tuple(q1.astype(int)), int(4 * SS), (1.4,) * 3, -1, cv2.LINE_AA)
    # door
    d = prog(f, DOOR_A, DOOR_B)
    if d > 0:
        poly = np.array([P(p) for p in DOOR], np.int32)
        cv2.fillPoly(fill, [poly], (0.55 * d,) * 3, cv2.LINE_AA)
        # floor reflection
        refl = np.array([P((x, -y * 0.6, z)) for x, y, z in DOOR], np.int32)
        r = np.zeros_like(fill)
        cv2.fillPoly(r, [refl], (0.22 * d,) * 3, cv2.LINE_AA)
        r = cv2.GaussianBlur(r, (0, 0), 14 * SS)
        mask = np.zeros_like(r)
        floor = np.array([P(p) for p in [(0,0,0),(3,0,0),(3,0,3),(0,0,3)]], np.int32)
        cv2.fillPoly(mask, [floor], (1,1,1))
        fill += r * mask
    mono = glow(lines + fill)[..., 0]
    img = mono[..., None] * CYAN[None, None, :]
    # white-hot core on lines
    img += np.clip(lines[..., :1] - 0.0, 0, 1) * 0.35 + fill[..., :1] * np.array([0.6, 0.3, 0])
    # floor reflection of floor lines (subtle)
    img = np.clip(img, 0, 1)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    out = (img * 255).astype(np.uint8)
    # text
    tt = prog(f, TEXT_A, TEXT_B)
    if tt > 0:
        out = draw_text(out, tt)
    return out

def draw_text(bgr, a):
    txt = "CONSTRUCT"
    size = 64
    font = ImageFont.truetype(FONT, size)
    spacing = 30
    widths = [font.getlength(ch) for ch in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    layer = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(layer)
    x = (W - total) / 2
    y = 905
    for ch, w in zip(txt, widths):
        dr.text((x, y), ch, font=font, fill=255)
        x += w + spacing
    m = np.asarray(layer, np.float32) / 255 * a
    halo = cv2.GaussianBlur(m, (0, 0), 10) * 0.6
    base = bgr.astype(np.float32) / 255
    base += halo[..., None] * np.array([1.0, 0.95, 0.7])
    base = base * (1 - m[..., None]) + m[..., None]
    return (np.clip(base, 0, 1) * 255).astype(np.uint8)

frames = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(N)
for f in frames:
    cv2.imwrite(f"{OUT}/construct_{f+1:02d}.png", render(f))
print("ok")
