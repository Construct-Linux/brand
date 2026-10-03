import os, sys
import numpy as np
import cv2
import palette, room

# usage: logo.py [out_dir]
# The Construct mark: the animation's last frame without the grid - the room in outline,
# open on the left. Same room and camera as video.py (room.py). The strokes live in a 0..100 box;
# they are written as SVG (color, GNOME symbolic, Orchis' Activities button) and rendered to PNG
# at icon sizes.
OUT = sys.argv[1] if len(sys.argv) > 1 else "logos"
os.makedirs(OUT, exist_ok=True)

PAL = palette.load()
CYAN = PAL["brand"]["cyan"]

# ---------- the room's outline (room.py), seen by the animation's camera ----------
def mark(lines3d):
    """Project 3D strokes and normalize them into the 0..100 box (aspect kept)."""
    lines = [(room.project(a), room.project(b)) for a, b in lines3d]
    pts = np.array([p for l in lines for p in l])
    lo, hi = pts.min(0), pts.max(0)
    s = 100 / (hi - lo).max()
    off = (100 - (hi - lo) * s) / 2 - lo * s
    return [(a * s + off, b * s + off) for a, b in lines]

LINES = mark(room.OUTLINE)
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
    # Whole pixels: 1 px only at 16, where 2 would fill the mark; from 24 up two, or the line
    # fades (a 1 px cyan stroke at 32 px all but vanished).
    return 1 if size <= 16 else 2

def snap(lines, size):
    """Move endpoints onto the pixel grid so verticals and horizontals cover whole pixels: a
    1 px line on a pixel's center, a 2 px one on the edge between two."""
    off = 0.5 if stroke_px(size) % 2 else 0.0
    c = lambda v: (np.floor((v + 6) * size / 112) + off) * 112 / size - 6
    return [(c(np.asarray(a)), c(np.asarray(b))) for a, b in lines]

def render(lines, size, color):
    """The mark in color on a transparent background, as the SVG is: BGRA."""
    ss = 8
    lines = snap(lines, size)
    S = size * ss
    k = S / 112
    T = lambda p: (int(round((p[0] + 6) * k * 16)), int(round((p[1] + 6) * k * 16)))
    ink = np.zeros((S, S), np.float32)
    w = int(round(stroke_px(size) * ss))
    for pts, closed in chain(lines):
        cv2.polylines(ink, [np.array([T(p) for p in pts], np.int32)], closed, 1.0, w, cv2.LINE_AA, 4)
    a = cv2.resize(np.clip(ink, 0, 1), (size, size), interpolation=cv2.INTER_AREA)
    out = np.empty((size, size, 4), np.uint8)
    out[..., :3] = hex2bgr(color)
    out[..., 3] = (a * 255).round()
    return out

def symbolic(lines):
    """GNOME's symbolic icon: the mark on a 16 px grid, one color GTK replaces with the
    theme's (#2e3436 is the one it looks for), a stroke thick enough to read at 16 px."""
    d = " ".join("M" + " L".join(f"{(p[0] + 6) * 16 / 112:.2f} {(p[1] + 6) * 16 / 112:.2f}" for p in pts) + (" Z" if closed else "")
                 for pts, closed in chain(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">\n'
            f'<path d="{d}" fill="none" stroke="#2e3436" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n')

def activities(lines):
    """The Activities button of Orchis' GNOME Shell theme (its -i option): 48 px, white, as the
    theme's own icons are; the shell tints nothing, so the stroke is drawn at panel weight."""
    d = " ".join("M" + " L".join(f"{6 + (p[0] + 6) * 36 / 112:.2f} {6 + (p[1] + 6) * 36 / 112:.2f}" for p in pts) + (" Z" if closed else "")
                 for pts, closed in chain(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">\n'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="3" '
            f'stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n')

SIZES = [64, 48, 32, 24, 16]  # above 64 px the SVG is the icon
open(f"{OUT}/{NAME}.svg", "w").write(svg(LINES, CYAN))
open(f"{OUT}/{NAME}-symbolic.svg", "w").write(symbolic(LINES))
open(f"{OUT}/{NAME}-activities.svg", "w").write(activities(LINES))
for s in SIZES:
    cv2.imwrite(f"{OUT}/{NAME}-{s}.png", render(LINES, s, CYAN))
print(f"{OUT}/: {NAME} -> svg, symbolic and activities svg, png {SIZES}")
