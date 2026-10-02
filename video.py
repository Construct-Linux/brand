import numpy as np, cv2, os, sys
from PIL import Image, ImageDraw, ImageFont

W = H = int(os.environ.get("SIZE", 1080))  # output px (square); the design is laid out at 1080
SS = 2  # supersampling
U = W / 1080  # layout scale
PX = SS * U   # one design pixel on the supersampled canvas
# DejaVu Sans Bold (same package as DejaVu Sans, the default font for Plymouth ("Sans" -> fontconfig) on Debian/Ubuntu/Fedora/Arch)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",    # Debian/Ubuntu
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",  # Fedora/RHEL
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",                # Arch
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",             # openSUSE / older Fedora
    os.path.expanduser("~/Library/Fonts/DejaVuSans-Bold.ttf"), # macOS (brew --cask font-dejavu)
    "/Library/Fonts/DejaVuSans-Bold.ttf",                      # macOS
]
FONT = os.environ.get("FONT") or next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if not FONT:
    sys.exit("DejaVuSans-Bold.ttf not found: install fonts-dejavu-core / dejavu-sans-fonts or set FONT=/path/DejaVuSans-Bold.ttf")
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
# Front view, one-point perspective: the camera looks straight down +z with no yaw, pitch
# or roll, so every x line (floor front edge, the line above the word) stays horizontal
# and every y line stays vertical; only depth converges, to the vanishing point.
# Framing is done by shifting the image (like an architectural shift lens), never by
# turning the camera.
cam = np.array([1.3, 1.2, -2.9])  # position (x, y=height, z=distance in front)
F = 620 * PX                      # focal length: larger = closer / bigger room
VX, VY = 0.48, 0.51               # where the vanishing point (straight ahead) sits on screen
CX, CY = W * SS * VX, H * SS * VY

def P(p):
    x, y, z = np.array(p, float) - cam
    return np.array([CX + F * x / z, CY - F * y / z])

SHIFT = 4  # cv2 fixed-point bits: draw at 1/16 px instead of rounding to whole pixels

def pt(q):
    return tuple(int(v) for v in np.round(np.asarray(q) * (1 << SHIFT)))

def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)

def prog(f, a, b):
    return ease((f - a) / max(b - a, 1e-6))

# Construction grows outward from the back-right-bottom corner (3,0,3) like a wavefront:
# every line is one cell edge that starts at a vertex already reached and is drawn
# while the wave moves one step (Manhattan distance on the grid) away from the corner.
#   1) floor:  d = (3-x) + (3-z)
#   2) walls, in order, each line starting on something already drawn:
#      corner axis -> top edges from its tip -> outer vertical edges from the floor up to
#      the top edge (walls framed) -> grid from those edges inward: upper horizontals,
#      verticals hanging from the top edge, lower horizontals between existing lines
# segment list: (p0, p1, start, end)
segs = []
def S(p0, p1, a, b):
    segs.append((np.array(p0, float), np.array(p1, float), a, b))

CORNER_A, CORNER_B = 4, 9    # spark at the corner
FLOOR_A, FLOOR_STEP = 9, 2.5  # 6 waves -> floor closed at 24
AXIS_A, AXIS_B = 24, 27       # walls: corner axis
TOP_A, TOP_B = 27, 29.5       # top edges
def snap(n):
    """Timing for a line drawn entirely between frames n-1 and n (1-based): no frame shows
    it half-way. Used for vertical lines, which would otherwise read as loose posts/cuts."""
    return timeline(n - 2) + 0.02, timeline(n - 1) - 0.02

OUTER = snap(30)              # outer vertical edges, floor -> top edge: whole in frame 30
HI_A, HI_B = 31.1, 33.3       # y=2 horizontals, outer edge -> axis
VERT_HI = snap(33)            # inner verticals, top edge -> y=2 line: whole in frame 33
VERT_LO = snap(34)            # ...then y=2 line -> floor: whole in frame 34
LO_A, LO_B = 34.6, 37         # y=1 horizontals -> room closed at 37
DOOR_A, DOOR_B = 37.2, 40.5   # entrance lights up once the room is closed...
TEXT_A, TEXT_B = 41.2, 45.2   # ...then the word, fully white for the last frames

def edge(p0, p1, d, start, step):
    S(p0, p1, start + d * step, start + (d + 1) * step)

for x in range(4):
    for z in range(4):
        d = (3 - x) + (3 - z)
        if x > 0: edge((x, 0, z), (x - 1, 0, z), d, FLOOR_A, FLOOR_STEP)
        if z > 0: edge((x, 0, z), (x, 0, z - 1), d, FLOOR_A, FLOOR_STEP)

# door: an open entrance in the right wall, middle column (z 1..2), two lower rows (y 0..2).
# No fill: the frame lights up brighter than the grid.
DOOR = [(3, 0, 1), (3, 2, 1), (3, 2, 2), (3, 0, 2)]

S((3, 0, 3), (3, 3, 3), AXIS_A, AXIS_B)  # corner axis
S((3, 3, 3), (3, 3, 0), TOP_A, TOP_B)    # right wall top edge
S((3, 3, 3), (0, 3, 3), TOP_A, TOP_B)    # back wall top edge
S((3, 0, 0), (3, 3, 0), *OUTER)  # right wall front edge
S((0, 0, 3), (0, 3, 3), *OUTER)  # back wall left edge
S((3, 2, 0), (3, 2, 3), HI_A, HI_B)        # right wall y=2 (door lintel line)
S((0, 2, 3), (3, 2, 3), HI_A, HI_B)        # back wall y=2
for k in (1, 2):  # right wall z=1, z=2 are the door jambs
    for (y0, y1), win in (((3, 2), VERT_HI), ((2, 0), VERT_LO)):
        S((3, y0, 3 - k), (3, y1, 3 - k), *win)  # right wall
        S((3 - k, y0, 3), (3 - k, y1, 3), *win)  # back wall
S((0, 1, 3), (3, 1, 3), LO_A, LO_B)        # back wall y=1
# right wall y=1 stops at the door jambs: one piece from the front edge, one from the axis
S((3, 1, 0), (3, 1, 1), LO_A, LO_B)
S((3, 1, 3), (3, 1, 2), LO_A, LO_B)
# the room is open on the left and the front: those sides end on the floor/back-wall edges

MIN_LEN = 14 * PX  # px a growing line needs before it is shown

def glow(img, strength=1.0):
    out = img.copy()
    for k, w in ((9, 0.9), (31, 0.7), (91, 0.55)):
        out += cv2.GaussianBlur(img, (0, 0), k * PX / 3) * w * strength
    return out

def render(frame):
    g = intensity(frame)
    f = timeline(frame)
    lines = np.zeros((H * SS, W * SS, 3), np.float32)
    lw = max(1, round(3 * PX))
    # starting point of light
    c = prog(f, CORNER_A, CORNER_B)
    fade = 1 - 0.6 * prog(f, 14, 20)
    if c > 0:
        p = pt(P((3, 0, 3)))
        cv2.circle(lines, p, round(5 * PX * (1 << SHIFT)), (c * fade,) * 3, -1, cv2.LINE_AA, SHIFT)
    for p0, p1, a, b in segs:
        t = min(max((f - a) / (b - a), 0), 1)  # linear: steady wavefront
        if t <= 0: continue
        q0, q1 = P(p0), P(p0 + (p1 - p0) * t)
        if t < 1 and np.linalg.norm(q1 - q0) < MIN_LEN: continue  # a dot is not a line yet
        cv2.line(lines, pt(q0), pt(q1), (1.0,) * 3, lw, cv2.LINE_AA, SHIFT)
        # bright drawing head
        if t < 1:
            cv2.circle(lines, pt(q1), round(4 * PX * (1 << SHIFT)), (1.4,) * 3, -1, cv2.LINE_AA, SHIFT)
    # door frame: jambs + lintel brighten over the grid
    d = prog(f, DOOR_A, DOOR_B)
    if d > 0:
        jamb_pts = np.array([pt(P(p)) for p in DOOR], np.int32)
        cv2.polylines(lines, [jamb_pts], False, (1.0 + 1.2 * d,) * 3, int(lw * (1 + 0.8 * d)), cv2.LINE_AA, SHIFT)
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
    size = round(64 * U)
    font = ImageFont.truetype(FONT, size)
    spacing = 30 * U
    widths = [font.getlength(ch) for ch in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    layer = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(layer)
    x = (W - total) / 2
    y = 905 * U
    for ch, w in zip(txt, widths):
        dr.text((x, y), ch, font=font, fill=255)
        x += w + spacing
    m = np.asarray(layer, np.float32) / 255 * a
    halo = cv2.GaussianBlur(m, (0, 0), (4 + 3 * g) * U) * (0.1 + 0.2 * g)  # soft: the room is the logo
    base = bgr.astype(np.float32) / 255
    base += halo[..., None] * np.array([1.0, 0.95, 0.7])
    base = base * (1 - m[..., None]) + m[..., None]
    return (np.clip(base, 0, 1) * 255).astype(np.uint8)

frames = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(N)
for f in frames:
    cv2.imwrite(f"{OUT}/construct_{f+1:02d}.png", render(f))
print("ok")
