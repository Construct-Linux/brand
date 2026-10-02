import json, numpy as np, cv2, os, sys
from PIL import Image, ImageDraw, ImageFont

# CONSTRUCT boot animation. "The image doesn't move. The workspace does."
# Two layers with fixed roles:
#   - the OUTLINE of the open room (= the logo mark) is the stable base image: drawn early in
#     one gesture from the corner, then held at full, unchanged, to the last frame;
#   - the interior GRID is the workspace: finer and dimmer, it is built inside the outline,
#     switches on, breathes while the system waits and fades away at the end.
# The clip is split into segments so Plymouth can wait for any length of time without
# tearing the room down and rebuilding it:
#   intro (once) -> loop (repeat while booting; seamless) -> outro (once, ends on the logo).
# Nothing here is tied to boot state, so nothing pretends to be progress or verification:
# the intro is choreography with a fixed length, the loop has no direction.

W = H = int(os.environ.get("SIZE", 1080))  # output px (square); the design is laid out at 1080
SS = 2  # supersampling
U = W / 1080  # layout scale
PX = SS * U   # one design pixel on the supersampled canvas
# Audiowide (SIL Open Font License, fonts/OFL.txt), shipped in the repo: same file
# everywhere, no system font needed. The word is baked into the frames.
FONT = os.environ.get("FONT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Audiowide-Regular.ttf")
CYAN = np.array([1.0, 0.90, 0.0])  # BGR -> cyan (#00E5FF)

# ---------- segments (frame counts) ----------
INTRO, LOOP, OUTRO = 26, 12, 10
N = INTRO + LOOP + OUTRO  # 48: the preview clip plays the loop once (5 s at 9.6 fps)
SEGMENTS = {"intro": (0, INTRO), "loop": (INTRO, INTRO + LOOP), "outro": (INTRO + LOOP, N)}

# ---------- camera: room = cube 3x3x3, x right, y up, z depth (z=0 open front) ----------
# Front view, one-point perspective: the camera looks straight down +z with no yaw, pitch
# or roll, so every x line (floor front edge, the line above the word) stays horizontal
# and every y line stays vertical; only depth converges, to the vanishing point.
# Framing is done by shifting the image (like an architectural shift lens), never by
# turning the camera.
cam = np.array([0.6, 1.2, -2.9])  # position (x, y=height, z=distance in front); same as logo.py
FOCAL = 620                       # focal length in design px: larger = closer / bigger room
F = FOCAL * PX
# vanishing point on screen; VX centers the floor front edge over the word:
VX, VY = 0.5 - FOCAL * (1.5 - cam[0]) / -cam[2] / 1080, 0.49
CX, CY = W * SS * VX, H * SS * VY

def P(p):
    x, y, z = np.array(p, float) - cam
    return np.array([CX + F * x / z, CY - F * y / z])

SHIFT = 4  # cv2 fixed-point bits: draw at 1/16 px instead of rounding to whole pixels

def pt(q):
    return tuple(int(v) for v in np.round(np.asarray(q) * (1 << SHIFT)))

def clamp01(t):
    return min(max(t, 0.0), 1.0)

def ease(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)

def prog(f, a, b):
    return ease((f - a) / max(b - a, 1e-6))

def snapf(n):
    """Window for a line drawn entirely between frames n-1 and n: no frame shows it half-way.
    Used for interior verticals, which would otherwise read as loose posts or cuts."""
    return n - 1 + 0.02, n - 0.02

# ---------- intro timings (in frames) ----------
SPARK = (-1, 1)              # light at the corner
OUTLINE = (0.6, 6.4)         # the outline, drawn from the corner; complete at frame 7
TEXT = (6, 10)               # the word: the identity is complete from frame 10 (~1 s)
FLOOR = (10, 14.5)           # grid: floor lines, from edge to edge
HI = (14.5, 17)              # grid: walls, y=2 lines from the outer edges inward to the axis
VERT_HI = snapf(18)          # grid: walls, inner verticals top edge -> y=2 line (whole in frame 18)
VERT_LO = snapf(19)          # ...then y=2 line -> floor (whole in frame 19)
LO = (19.2, 21.5)            # grid: walls, y=1 lines between existing lines
ACTIVATE = (21.5, INTRO)     # grid switches on, all at once; reaches ACTIVE as the loop begins
DRAFT, ACTIVE, BREATH = 0.35, 0.8, 0.12  # grid levels: while drawn, switched on, loop depth
FADE = (INTRO + LOOP, N - 3) # outro: grid fades out; the last frames are the logo lockup

# ---------- geometry ----------
# outline: pens leave the back-right-bottom corner at the same constant speed (on screen);
# each edge starts when a pen reaches its first vertex, so every line extends one already
# drawn. Outer verticals hang from the top edges down to the floor: never a loose post.
OUTLINE_EDGES = [  # (from, to), in drawing direction
    ((3, 0, 3), (0, 0, 3)),  # floor back edge
    ((3, 0, 3), (3, 0, 0)),  # floor / right wall seam
    ((3, 0, 3), (3, 3, 3)),  # corner axis
    ((0, 0, 3), (0, 0, 0)),  # floor left edge
    ((3, 0, 0), (0, 0, 0)),  # floor front edge
    ((3, 3, 3), (0, 3, 3)),  # back wall top edge
    ((3, 3, 3), (3, 3, 0)),  # right wall top edge
    ((0, 3, 3), (0, 0, 3)),  # back wall left edge, down
    ((3, 3, 0), (3, 0, 0)),  # right wall front edge, down
]

def outline_schedule():
    """(p0, p1, start, end) per edge, in pen-length units normalized to 0..1."""
    arrive, sched = {(3, 0, 3): 0.0}, []
    for a, b in OUTLINE_EDGES:  # listed so that every edge's start vertex is already reached
        l = np.linalg.norm(P(b) - P(a))
        t0 = arrive[a]
        sched.append((np.array(a, float), np.array(b, float), t0, t0 + l))
        arrive[b] = min(arrive.get(b, np.inf), t0 + l)
    total = max(e for *_, e in sched)
    return [(a, b, s / total, e / total) for a, b, s, e in sched]

OUTLINE_SCHED = outline_schedule()

# interior grid: every line runs between two lines already drawn (outline or grid)
GRID = []  # (p0, p1, (start, end))
for i in (1, 2):
    GRID.append(((i, 0, 3), (i, 0, 0), FLOOR))     # floor columns, back -> front
    GRID.append(((3, 0, i), (0, 0, i), FLOOR))     # floor rows, right -> left
GRID.append(((3, 2, 0), (3, 2, 3), HI))            # right wall y=2, front edge -> axis
GRID.append(((0, 2, 3), (3, 2, 3), HI))            # back wall y=2, left edge -> axis
for k in (1, 2):
    for (y0, y1), win in (((3, 2), VERT_HI), ((2, 0), VERT_LO)):
        GRID.append(((3, y0, 3 - k), (3, y1, 3 - k), win))  # right wall verticals
        GRID.append(((3 - k, y0, 3), (3 - k, y1, 3), win))  # back wall verticals
GRID.append(((3, 1, 0), (3, 1, 3), LO))            # right wall y=1, front edge -> axis
GRID.append(((0, 1, 3), (3, 1, 3), LO))            # back wall y=1, left edge -> axis

MIN_LEN = 14 * PX  # px a growing line needs before it is shown

def grid_level(f):
    """How lit the workspace grid is: drafted, switched on, breathing, fading out."""
    if f < INTRO:
        return DRAFT + (ACTIVE - DRAFT) * prog(f, *ACTIVATE)
    if f < INTRO + LOOP:  # one breath per loop; starts and ends at ACTIVE, so it repeats seamlessly
        u = (f - INTRO) / LOOP
        return ACTIVE - BREATH * (1 - np.cos(2 * np.pi * u)) / 2
    return ACTIVE * (1 - prog(f, *FADE))

def glow(img, strength=1.0):
    out = img.copy()
    for k, w in ((9, 0.9), (31, 0.7), (91, 0.55)):
        out += cv2.GaussianBlur(img, (0, 0), k * PX / 3) * w * strength
    return out

def render(f, tagline=None):
    shape = (H * SS, W * SS)
    base = np.zeros(shape, np.float32)   # outline: once drawn, always 1.0
    grid = np.zeros(shape, np.float32)   # workspace, scaled by grid_level
    heads = np.zeros(shape, np.float32)  # bright tips of lines being drawn
    lw, gw = max(1, round(3 * PX)), max(1, round(2 * PX))
    head_r = round(4 * PX * (1 << SHIFT))
    # spark at the corner, absorbed by the outline once it is closed
    s = prog(f, *SPARK) * (1 - prog(f, OUTLINE[1] - 2, OUTLINE[1] + 1))
    if s > 0:
        cv2.circle(base, pt(P((3, 0, 3))), round(5 * PX * (1 << SHIFT)), s, -1, cv2.LINE_AA, SHIFT)
    # outline: ease-out, the pens slow down and settle as the room closes
    T = clamp01((f - OUTLINE[0]) / (OUTLINE[1] - OUTLINE[0]))
    T = 1 - (1 - T) ** 2
    for p0, p1, a, b in OUTLINE_SCHED:
        t = clamp01((T - a) / (b - a))
        if t <= 0: continue
        q0, q1 = P(p0), P(p0 + (p1 - p0) * t)
        cv2.line(base, pt(q0), pt(q1), 1.0, lw, cv2.LINE_AA, SHIFT)
        if t < 1:
            cv2.circle(heads, pt(q1), head_r, 1.4, -1, cv2.LINE_AA, SHIFT)
    # grid
    for p0, p1, (a, b) in GRID:
        t = clamp01((f - a) / (b - a))  # linear: steady growth
        if t <= 0: continue
        p0, p1 = np.array(p0, float), np.array(p1, float)
        q0, q1 = P(p0), P(p0 + (p1 - p0) * t)
        if t < 1 and np.linalg.norm(q1 - q0) < MIN_LEN: continue  # a dot is not a line yet
        cv2.line(grid, pt(q0), pt(q1), 1.0, gw, cv2.LINE_AA, SHIFT)
        if t < 1:
            cv2.circle(heads, pt(q1), round(head_r * 0.75), 1.0, -1, cv2.LINE_AA, SHIFT)
    lines = np.maximum(base, grid * grid_level(f)) + heads
    img = glow(lines)[..., None] * CYAN[None, None, :]
    img += np.clip(lines, 0, 2)[..., None] * 0.35  # white-hot core
    img = cv2.resize(np.clip(img, 0, 1), (W, H), interpolation=cv2.INTER_AREA)
    out = (img * 255).astype(np.uint8)
    a = prog(f, *TEXT)
    if a > 0:
        out = draw_text(out, a, tagline)
    return out

def draw_text(bgr, a, tagline=None):
    """The word (opacity a); optionally a tagline under it (only for reviews: not in the splash)."""
    txt = "CONSTRUCT"
    # the word spans exactly the floor front edge above it (x 0..3 at z=0)
    span = (P((3, 0, 0))[0] - P((0, 0, 0))[0]) / SS
    track = 0.35  # letter spacing, in em
    ref = ImageFont.truetype(FONT, 100)
    em_width = (sum(ref.getlength(ch) for ch in txt[:-1]) + ref.getbbox(txt[-1])[2]) / 100 + track * (len(txt) - 1)
    size = span / em_width
    font = ImageFont.truetype(FONT, round(size))
    spacing = track * size
    layer = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(layer)
    x = (W - span) / 2
    y = 918 * U  # cap middle of the word, under the floor edge
    for ch in txt:
        dr.text((x, y), ch, font=font, fill=255, anchor="lm")
        x += font.getlength(ch) + spacing
    if tagline:  # smaller, light tracking, light gray
        tf = ImageFont.truetype(FONT, round(size * 0.42))
        tsp = 0.12 * tf.size
        for line_index, line in enumerate(tagline.splitlines()):
            tx = (W - sum(tf.getlength(ch) for ch in line) - tsp * (len(line) - 1)) / 2
            for ch in line:
                dr.text((tx, y + size * 1.25 + line_index * tf.size * 1.5), ch, font=tf, fill=150, anchor="lm")
                tx += tf.getlength(ch) + tsp
    m = np.asarray(layer, np.float32) / 255 * a
    halo = cv2.GaussianBlur(m, (0, 0), 7 * U) * 0.3  # soft: the room is the logo
    base = bgr.astype(np.float32) / 255
    base += halo[..., None] * np.array([1.0, 0.95, 0.7])
    base = base * (1 - m[..., None]) + m[..., None]
    return (np.clip(base, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"
    os.makedirs(OUT, exist_ok=True)
    frames = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(N)
    for f in frames:
        cv2.imwrite(f"{OUT}/construct_{f+1:02d}.png", render(f))
    # 1-based, inclusive frame ranges per segment, for plymouth.py and the review sheet
    json.dump({k: [a + 1, b] for k, (a, b) in SEGMENTS.items()}, open(f"{OUT}/segments.json", "w"), indent=1)
    print("ok")
