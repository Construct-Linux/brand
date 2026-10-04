import os, sys
import numpy as np
import cv2
import palette, room

# usage: wallpaper.py [out_dir] [width] [height]
# The desktop backgrounds: the boot animation's wait - the room with its workspace grid lit -
# held still and set back behind the windows. Same camera and room as video.py; no word, the
# top bar and the dock already say whose desktop it is.
# Four pairs, each dark and light. The default, construct-*, is the boot's last frame held still:
# Plymouth's outro goes back to the grid so GDM takes over on this drawing, so its mark stays where
# the boot puts it. The other three are quieter, for long sessions, and fail here unless they are
# calmer than the default of their mode. Dark draws in the accent on ink; light draws the room in
# the ink's hue (light.muted) on the desk, a technical drawing, with no cyan - except the mark,
# which is the brand mark and keeps the light accent.
# GNOME zooms them to the screen, so they are made once, at 16:10 and 2880x1800, the ThinkPad X9's
# panel; a 16:9 screen crops 90px from the top and the bottom, a 3:2 one from the sides.
# construct.xml offers each pair to Settings (gnome-background-properties): the light one with the
# dark one for dark mode, as GNOME's own backgrounds are, the ink as the color behind them.
OUT = sys.argv[1] if len(sys.argv) > 1 else "wallpapers"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 2880
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1800
os.makedirs(OUT, exist_ok=True)
PAL = palette.load()
U = H / 1080  # design px, as in video.py

# ---------- camera and room: room.py's ----------
F0 = 620 * U * 0.82                 # a little further back than the splash: room for windows
GRID = room.FLOOR + room.rows(1) + room.rows(2) + room.COLUMNS
VERTS = [v for e in room.OUTLINE for v in e]
MARK_CENTER = 0.4222                # THEMING.md: where the boot and the wallpaper put the mark

SHIFT = 4
pt = lambda q: tuple(int(v) for v in np.round(np.asarray(q) * (1 << SHIFT)))


def bbox(P):
    q = np.array([P(v) for v in VERTS])
    return q.min(0), q.max(0)


def camera(scale, place):
    """The default framing - the floor's front edge centred, as in video.py - or the room at
    scale with its outline's right and bottom edges at place (fractions of W and H)."""
    if place is None:
        return room.view(F0, W, H * 0.47)
    F = F0 * scale
    _, hi = bbox(room.view(F, 0, 0))
    return room.view(F, 2 * (place[0] * W - hi[0]), place[1] * H - hi[1])


def layer(P, edges, width):
    m = np.zeros((H, W), np.float32)
    for a, b in edges:
        cv2.line(m, pt(P(a)), pt(P(b)), 1.0, max(1, round(width * U)), cv2.LINE_AA, SHIFT)
    return m


def rgb(h):
    return np.array(palette.rgb(h)[::-1], np.float32) / 255  # BGR, as cv2 writes


INK, DESK = PAL["brand"]["ink"], PAL["light"]["desk"]
DARK, LIGHT, MUTED = PAL["dark"]["accent"], PAL["light"]["accent"], PAL["light"]["muted"]
# name -> (scale, place, grid, outline width, {mode: (ground, lines, outline level, grid level, glow)})
VARIANTS = {
    # The boot's drawing: the dark one glows like the splash; the light one is ink on the desk.
    "construct": (1, None, True, 3, {"dark": (INK, DARK, 0.55, 0.22, 0.6), "light": (DESK, MUTED, 0.50, 0.15, 0)}),
    # The same drawing at a third of the level and without the glow, whose haze is most of the
    # default's busyness (8.5% of the screen against 1.1% for the lines alone). Same camera: it may
    # take over from the boot too.
    "quiet": (1, None, True, 3, {"dark": (INK, DARK, 0.17, 0.045, 0), "light": (DESK, MUTED, 0.28, 0.11, 0)}),
    # The room smaller, low on the right third, its tall wall facing the empty two thirds where
    # GNOME opens windows; a step above quiet, or at 0.62 it would vanish.
    "offset": (0.62, (5 / 6, 0.80), True, 3, {"dark": (INK, DARK, 0.24, 0.08, 0), "light": (DESK, MUTED, 0.34, 0.12, 0)}),
    # Only the brand mark, small, in the corner: 201px from the right and the bottom, 90px of
    # zoom crop (16:9 and 3:2) plus the dock's top and a space step at 150%, (6 + 44 + 24) x 1.5.
    "mark": (0.22, (1 - 201 / W, 1 - 201 / H), False, 2, {"dark": (INK, DARK, 0.45, 0, 0), "light": (DESK, LIGHT, 0.40, 0, 0)}),
}

# What makes a quiet wallpaper quiet, as ΔE00 against its ground (palette.py's): the dark outline
# at most 15 and the grid 6 - the default's are 39.6 and 18 - and the grid still 5 from h, so a
# menu's edge never merges with a line under it. Every line stays 3 or more (an edge's floor) so
# the drawing does not vanish on a washed-out panel.
QUIET = {"outline": 15, "grid": 6, "grid_vs_h": 5, "floor": 3}


def de(a, b):
    return palette.perceive(a, b)[0]


problems, report, measured = [], [], {}
for name, (scale, place, with_grid, width, modes) in VARIANTS.items():
    P = camera(scale, place)
    outline, grid = layer(P, room.OUTLINE, width), layer(P, GRID, 2) if with_grid else None
    lo_, hi_ = bbox(P)
    for mode, (bg, ink, lo, lg, glow) in modes.items():
        lines = outline * lo if grid is None else np.maximum(outline * lo, grid * lg)
        if glow:
            lines = lines + sum(cv2.GaussianBlur(lines, (0, 0), s * U) * w for s, w in ((6, 0.6), (24, 0.35))) * glow
        a = np.clip(lines, 0, 1)[..., None]
        img = ((rgb(bg) + (rgb(ink) - rgb(bg)) * a) * 255).round().astype(np.uint8)
        file = "construct" if name == "construct" else f"construct-{name}"
        cv2.imwrite(f"{OUT}/{file}-{mode}.png", img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        # Calm, measured two ways: the strongest line's contrast with the ground, and how much of
        # the screen differs from the ground at all (the glow's haze counts).
        line_o = palette.mix(ink, bg, lo)
        coverage = float((np.abs(img.astype(np.int16) - (rgb(bg) * 255).round()).max(2) > 2).mean())
        measured[name, mode] = (palette.contrast(line_o, bg), coverage)
        levels = {"outline": de(line_o, bg)}
        if grid is not None:
            levels["grid"] = de(palette.mix(ink, bg, lg), bg)
        report.append(f"  {file}-{mode}: outline {palette.contrast(line_o, bg):.2f}:1, ΔE00 "
                      + ", ".join(f"{k} {v:.1f}" for k, v in levels.items()) + f"; {coverage:.2%} of the screen")
        problems += [f"{file}-{mode}: the {k} is ΔE00 {v:.1f} from the ground, below {QUIET['floor']}"
                     for k, v in levels.items() if v < QUIET["floor"]]
        if mode == "dark" and name == "quiet":
            if levels["outline"] > QUIET["outline"] or levels["grid"] > QUIET["grid"]:
                problems.append(f"quiet-dark: outline {levels['outline']:.1f}, grid {levels['grid']:.1f} ΔE00 from ink, "
                                f"at most {QUIET['outline']} and {QUIET['grid']}")
            if de(palette.mix(ink, bg, lg), PAL["neutral"]["h"]) < QUIET["grid_vs_h"]:
                problems.append(f"quiet-dark: the grid is under ΔE00 {QUIET['grid_vs_h']} from h, a menu's edge would merge")
        if mode == "light" and ink == LIGHT and name != "mark":
            problems.append(f"{file}-light: light draws in the ink's hue, not cyan; only the mark is the accent")
    if place is None:
        centre = (lo_[1] + hi_[1]) / 2 / H
        if abs(centre - MARK_CENTER) > 0.002:
            problems.append(f"{name}: the mark's centre is at {centre:.4f} H, the boot's is {MARK_CENTER}")
for (name, mode), (c, cov) in measured.items():
    c0, cov0 = measured["construct", mode]
    if name != "construct" and not (c < c0 and cov <= cov0):
        problems.append(f"{name}-{mode}: {c:.2f}:1 over {cov:.2%} is not calmer than the default's {c0:.2f}:1 over {cov0:.2%}")
print("wallpapers:\n" + "\n".join(report))
if problems:
    sys.exit("wallpaper.py:\n  " + "\n  ".join(problems))

# Where the image installs them: the paths are absolute, as Settings reads them.
DIR = "/usr/share/backgrounds/construct"
NAMES = {"construct": "CONSTRUCT", "quiet": "CONSTRUCT Quiet", "offset": "CONSTRUCT Offset", "mark": "CONSTRUCT Mark"}
entries = "".join(f"""  <wallpaper deleted="false">
    <name>{NAMES[name]}</name>
    <filename>{DIR}/{file}-light.png</filename>
    <filename-dark>{DIR}/{file}-dark.png</filename-dark>
    <options>zoom</options>
    <shade_type>solid</shade_type>
    <pcolor>{INK}</pcolor>
  </wallpaper>
""" for name, file in ((n, "construct" if n == "construct" else f"construct-{n}") for n in VARIANTS))
open(f"{OUT}/construct.xml", "w").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>
{entries}</wallpapers>
""")
print(f"{OUT}/: construct, construct-quiet, construct-offset, construct-mark, -dark and -light.png ({W}x{H}), construct.xml")
