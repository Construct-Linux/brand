import glob, os, sys
import numpy as np
from PIL import Image

# usage: check.py <committed_dir> <regenerated_dir>
# Whether the committed images (plymouth/, logos/) are what the sources make: every file in one
# is in the other, and each pair looks the same over black - as Plymouth and a dark page show
# them. Not byte for byte: OpenCV picks its vector code by the processor, and pngquant's palette
# follows the pixels, so two machines can differ by a shade where nothing was changed. A changed
# drawing moves far more than the tolerance.
A = sys.argv[1]
B = sys.argv[2]
MEAN, PEAK = 1.0, 48  # mean and largest per-channel difference allowed, out of 255

def on_black(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    bg.alpha_composite(im)
    return np.asarray(bg.convert("RGB"), np.int16)

names = lambda d: {os.path.relpath(p, d) for p in glob.glob(f"{d}/**/*.png", recursive=True)}
committed, regenerated = names(A), names(B)
problems = [f"{n}: committed, not made by the sources" for n in sorted(committed - regenerated)]
problems += [f"{n}: made by the sources, not committed" for n in sorted(regenerated - committed)]
for n in sorted(committed & regenerated):
    a, b = on_black(f"{A}/{n}"), on_black(f"{B}/{n}")
    if a.shape != b.shape:
        problems.append(f"{n}: {a.shape[1]}x{a.shape[0]} committed, {b.shape[1]}x{b.shape[0]} made")
        continue
    d = np.abs(a - b)
    if d.mean() > MEAN or d.max() > PEAK:
        problems.append(f"{n}: differs from what the sources make (mean {d.mean():.2f}, peak {d.max()})")
if problems:
    sys.exit("\n".join(problems) + "\nregenerate and commit: task plymouth logo")
print(f"{A}/: {len(committed)} images match the sources")
