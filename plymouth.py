import glob, os, sys
import numpy as np
from PIL import Image

# usage: plymouth.py [frames_dir] [out_dir] [colors]
# Turns the rendered frames (light on black) into transparent PNGs for Plymouth, which
# draws them over its own black background. The palette is built from the image as seen
# on black, then every palette entry becomes alpha = brightness + un-premultiplied color,
# so over black each pixel is exactly the palette color (no alpha banding in the glow).
# colors=0 writes full RGBA instead (lossless, ~4x bigger).
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "plymouth"
COLORS = int(sys.argv[3]) if len(sys.argv) > 3 else 256

def to_rgba(rgb):
    c = np.asarray(rgb, np.float32)
    a = c.max(axis=-1, keepdims=True)
    return np.where(a > 0, c * 255 / np.maximum(a, 1), 0).round().astype(np.uint8), a.round().astype(np.uint8)

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
os.makedirs(OUT, exist_ok=True)
total = 0
for i, f in enumerate(files, 1):
    rgb = Image.open(f).convert("RGB")
    path = f"{OUT}/construct-{i:04d}.png"
    if COLORS:
        ref = rgb.quantize(COLORS, method=Image.Quantize.MEDIANCUT)
        img = rgb.quantize(palette=ref, dither=Image.Dither.NONE)  # no dither: smaller PNG
        pal = np.array(img.getpalette()[:3 * COLORS], np.uint8).reshape(-1, 3)
        color, alpha = to_rgba(pal)
        img.putpalette(color.flatten().tolist())
        img.save(path, optimize=True, transparency=alpha.flatten().tobytes())
    else:
        color, alpha = to_rgba(rgb)
        Image.fromarray(np.concatenate([color, alpha], axis=-1), "RGBA").save(path, optimize=True)
    total += os.path.getsize(path)
w, h = Image.open(files[0]).size
print(f"{OUT}/: {len(files)} frames {w}x{h}, {total / 1024:.0f} KiB total, {total / 1024 / len(files):.0f} KiB/frame")
