import glob, hashlib, json, os, sys
import numpy as np
from PIL import Image

# usage: plymouth.py [frames_dir] [out_dir]
# Turns the rendered frames (light on black) into transparent PNGs for Plymouth, which draws
# them over its own black background: every pixel becomes alpha = brightness and its color
# un-premultiplied, so over black it is exactly the rendered pixel. The files are lossless
# RGBA; the plymouth task then compresses them with pngquant.
# The animation shows some pictures more than once - the loop breathes out the way it breathed
# in, and the outro ends on the logo the intro already reached - and every file goes into the
# initrd, so each picture is written once, as frame-NNNN.png in order of first appearance.
# sequence.json says what to play: for each segment of video.py's segments.json - intro (once),
# loop (repeat while booting), outro (once at the end; its last frame is the logo) - the list
# of frame numbers, NNNN of the files - and mark_center, where the mark's centre is in the frame
# (below), so the image can put the frame where the wallpaper draws the mark.
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "plymouth"

# The mark's rows are those of the last picture (the logo) brighter than this, out of 255: the
# glow's faint edge is left out, as the eye leaves it out.
MARK_ALPHA = 32

def mark_center(rgb):
    """The mark's vertical centre as a fraction of the frame's height: the rows above the largest
    dark gap between rows, which parts the mark from the wordmark under it."""
    rows = np.flatnonzero(np.asarray(rgb).max(axis=(1, 2)) > MARK_ALPHA)
    gap = np.argmax(np.diff(rows))
    return round((rows[0] + rows[gap] + 1) / 2 / len(np.asarray(rgb)), 4)

def to_rgba(rgb):
    c = np.asarray(rgb, np.float32)
    a = c.max(axis=-1, keepdims=True)
    color = np.where(a > 0, c * 255 / np.maximum(a, 1), 0).round().astype(np.uint8)
    return np.concatenate([color, a.round().astype(np.uint8)], axis=-1)

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
segments = json.load(open(f"{SRC}/segments.json"))

os.makedirs(OUT, exist_ok=True)
number, played, total = {}, [], 0  # picture digest -> frame number; frame number per rendered frame
for f in files:
    rgb = np.asarray(Image.open(f).convert("RGB"))
    key = hashlib.sha256(rgb.tobytes()).digest()
    if key not in number:
        number[key] = len(number) + 1
        path = f"{OUT}/frame-{number[key]:04d}.png"
        Image.fromarray(to_rgba(rgb), "RGBA").save(path, optimize=True)
        total += os.path.getsize(path)
    played.append(number[key])
sequence = {seg: played[a - 1:b] for seg, (a, b) in segments.items()}
if sum(map(len, sequence.values())) != len(files):
    sys.exit(f"{SRC}/segments.json does not cover the {len(files)} frames")
with open(f"{OUT}/sequence.json", "w") as out:
    center = mark_center(Image.open(files[segments["outro"][1] - 1]).convert("RGB"))
    rows = [f' "{seg}": {json.dumps(n)}' for seg, n in sequence.items()] + [f' "mark_center": {center}']
    out.write("{\n" + ",\n".join(rows) + "\n}\n")
w, h = Image.open(files[0]).size
print(f"{OUT}/: {len(number)} frames {w}x{h} for {len(files)} shown "
      f"({', '.join(f'{k} {len(n)}' for k, n in sequence.items())}), {total / 1024:.0f} KiB")
