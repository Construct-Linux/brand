import numpy as np, cv2, os, sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
SS = 2  # supersampling
# DejaVu Sans: default font for Plymouth ("Sans" -> fontconfig) on Debian/Ubuntu/Fedora/Arch
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",    # Debian/Ubuntu
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",  # Fedora/RHEL
    "/usr/share/fonts/TTF/DejaVuSans.ttf",                # Arch
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",             # openSUSE / older Fedora
    os.path.expanduser("~/Library/Fonts/DejaVuSans.ttf"), # macOS (brew --cask font-dejavu)
    "/Library/Fonts/DejaVuSans.ttf",                      # macOS
]
FONT = os.environ.get("FONT") or next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if not FONT:
    sys.exit("DejaVuSans.ttf not found: install fonts-dejavu-core / dejavu-sans-fonts or set FONT=/path/DejaVuSans.ttf")
OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"
os.makedirs(OUT, exist_ok=True)
N = 48  # total frames (encode.py turns them into a 5s video)
CYAN = np.array([1.0, 0.90, 0.0])  # BGR -> cyan (#00E5FF)
DIM = np.array([0.55, 0.50, 0.38])  # BGR -> desaturated teal, the starting color
# story timeline (units used by the segment/door/text timings below) mapped onto N frames:
# the first frame already shows the spark, the last frame is the fully lit logo
T0, T1 = 7, 46

def timeline(f):
    return T0 + f * (T1 - T0) / (N - 1)

def intensity(f):
    """0 -> 1 over the whole clip: drives color saturation, brightness and neon glow."""
    return (f / (N - 1)) ** 1.4  # ease-in: the neon keeps building up to the last frame

# ---------- camera: room = cube 3x3x3, x right, y up, z depth (z=0 open front) ----------
# front view: camera low and centered in front of the open side, looking straight in
cam = np.array([1.3, 1.2, -2.9])     # position (x, y=height, z=distance in front)
target = np.array([1.5, 1.1, 3.0])   # point it looks at
fwd = target - cam; fwd /= np.linalg.norm(fwd)
right = np.cross([0, 1, 0], fwd); right /= np.linalg.norm(right)
up = np.cross(fwd, right)
F = 620 * SS  # focal length: larger = closer / bigger room
CX, CY = W * SS * 0.5, H * SS * 0.52  # where target lands on screen

def P(p):
    d = np.array(p, float) - cam
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([CX + F * x / z, CY - F * y / z])

def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)

def prog(f, a, b):
    return ease((f - a) / max(b - a, 1e-6))

# segment list: (p0, p1, start, end); every line ends on a vertex of the grid
segs = []
def S(p0, p1, a, b):
    segs.append((np.array(p0, float), np.array(p1, float), a, b))

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
    if i == 1:  # the door opening (z 1..2, y 0..2) stays clear of grid lines
        S((3, i, 3), (3, i, 2), 26, 29)
        S((3, i, 1), (3, i, 0), 29, 32)
    else:
        S((3, i, 3), (3, i, 0), 26, 32)
# 6) back wall (z=3)
S((0, 0, 3), (0, 3, 3), 28, 34)     # back-left vertical
S((3, 3, 3), (0, 3, 3), 29, 35)     # top edge
for i in (1, 2):
    S((i, 0, 3), (i, 3, 3), 31, 37)  # verticals continue floor columns
    S((3, i, 3), (0, i, 3), 32, 38)  # horizontals continue right-wall rows
# the room is open on the left and the front: those sides end on the floor/back-wall edges

# door: an open entrance in the right wall, middle column (z 1..2), two lower rows (y 0..2).
# No fill: the frame lights up brighter than the grid.
DOOR = [(3, 0, 1), (3, 2, 1), (3, 2, 2), (3, 0, 2)]
DOOR_A, DOOR_B = 34, 42
TEXT_A, TEXT_B = 40, 46
CORNER_A, CORNER_B = 4, 9

def glow(img, strength=1.0):
    out = img.copy()
    for k, w in ((9, 0.9), (31, 0.7), (91, 0.55)):
        out += cv2.GaussianBlur(img, (0, 0), k * SS / 3) * w * strength
    return out

def render(frame):
    g = intensity(frame)
    f = timeline(frame)
    lines = np.zeros((H * SS, W * SS, 3), np.float32)
    lw = 3 * SS
    # starting point of light
    c = prog(f, CORNER_A, CORNER_B)
    fade = 1 - 0.6 * prog(f, 14, 20)
    if c > 0:
        p = P((3, 0, 3)).astype(int)
        cv2.circle(lines, tuple(p), int(5 * SS), (c * fade,) * 3, -1, cv2.LINE_AA)
    for p0, p1, a, b in segs:
        t = prog(f, a, b)
        if t <= 0: continue
        q0, q1 = P(p0), P(p0 + (p1 - p0) * t)
        cv2.line(lines, tuple(q0.astype(int)), tuple(q1.astype(int)), (1.0,) * 3, lw, cv2.LINE_AA)
        # bright drawing head
        if t < 1:
            cv2.circle(lines, tuple(q1.astype(int)), int(4 * SS), (1.4,) * 3, -1, cv2.LINE_AA)
    # door frame: jambs + lintel brighten over the grid
    d = prog(f, DOOR_A, DOOR_B)
    if d > 0:
        jamb_pts = np.array([P(p) for p in DOOR], np.int32)
        cv2.polylines(lines, [jamb_pts], False, (1.0 + 0.8 * d,) * 3, int(lw * (1 + 0.5 * d)), cv2.LINE_AA)
    # from less to more: brightness, glow and saturation all ramp with g
    lines *= 0.6 + 0.4 * g
    mono = glow(lines, 0.15 + 1.15 * g)[..., 0]
    color = DIM + (CYAN - DIM) * g
    img = mono[..., None] * color[None, None, :]
    # white-hot core on lines
    img += np.clip(lines[..., :1], 0, 2) * 0.35 * g  # >1 only on the door frame: whiter core
    img = np.clip(img, 0, 1)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    out = (img * 255).astype(np.uint8)
    # text
    tt = prog(f, TEXT_A, TEXT_B)
    if tt > 0:
        out = draw_text(out, tt, g)
    return out

def draw_text(bgr, a, g=1.0):
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
    halo = cv2.GaussianBlur(m, (0, 0), 4 + 3 * g) * (0.1 + 0.2 * g)  # soft: the room is the logo
    base = bgr.astype(np.float32) / 255
    base += halo[..., None] * np.array([1.0, 0.95, 0.7])
    base = base * (1 - m[..., None]) + m[..., None]
    return (np.clip(base, 0, 1) * 255).astype(np.uint8)

frames = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(N)
for f in frames:
    cv2.imwrite(f"{OUT}/construct_{f+1:02d}.png", render(f))
print("ok")
