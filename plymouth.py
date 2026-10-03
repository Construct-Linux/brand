import glob, json, os, sys
import numpy as np
from PIL import Image

# usage: plymouth.py [frames_dir] [out_dir]
# Turns the rendered frames (light on black) into transparent PNGs for Plymouth, which draws
# them over its own black background: every pixel becomes alpha = brightness and its color
# un-premultiplied, so over black it is exactly the rendered pixel. The files are lossless
# RGBA; the plymouth task then compresses them with pngquant.
# The files are named per segment of video.py's segments.json, each numbered from 1:
# intro-NNNN.png (play once), loop-NNNN.png (repeat while booting), outro-NNNN.png (play once
# at the end; its last frame is the logo).
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "plymouth"

def to_rgba(rgb):
    c = np.asarray(rgb, np.float32)
    a = c.max(axis=-1, keepdims=True)
    color = np.where(a > 0, c * 255 / np.maximum(a, 1), 0).round().astype(np.uint8)
    return np.concatenate([color, a.round().astype(np.uint8)], axis=-1)

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
segments = json.load(open(f"{SRC}/segments.json"))

def name(i):  # 1-based frame -> output file name
    for seg, (a, b) in segments.items():
        if a <= i <= b:
            return f"{seg}-{i - a + 1:04d}.png"
    sys.exit(f"frame {i} is not in any segment of {SRC}/segments.json")

os.makedirs(OUT, exist_ok=True)
total = 0
for i, f in enumerate(files, 1):
    path = f"{OUT}/{name(i)}"
    Image.fromarray(to_rgba(Image.open(f).convert("RGB")), "RGBA").save(path, optimize=True)
    total += os.path.getsize(path)
w, h = Image.open(files[0]).size
print(f"{OUT}/: {len(files)} frames {w}x{h} ({', '.join(f'{k} {b - a + 1}' for k, (a, b) in segments.items())}), {total / 1024:.0f} KiB total, {total / 1024 / len(files):.0f} KiB/frame")
