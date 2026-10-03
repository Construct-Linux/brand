import glob, os, sys
import numpy as np
from PIL import Image

# usage: check.py <committed_dir> <regenerated_dir>
# Whether a committed directory (plymouth/, logos/, wallpapers/, palette/) is what the sources
# make: every file in one is in the other, text byte for byte, and each pair of images looks the
# same over black - as Plymouth and a dark page show them. Images are not compared byte for
# byte: OpenCV picks its vector code by the processor, so a blur or a resize can land a shade
# apart on another machine where nothing was changed.
A = sys.argv[1]
B = sys.argv[2]

# Mean and largest per-channel difference allowed, out of 255, by directory. The logos and the
# wallpapers are drawn straight from the sources: one shade of OpenCV rounding is all that may
# move (a cyan 6/255 off moves the dark wallpaper's lines by 4 and the logos by 6). The Plymouth
# frames go through pngquant, whose palette follows the pixels: a shade there can move a whole
# palette entry, so only a changed drawing fails.
TOLERANCE = {"logos": (0.05, 2), "wallpapers": (0.05, 2), "plymouth": (1.0, 48)}


def on_black(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    bg.alpha_composite(im)
    return np.asarray(bg.convert("RGB"), np.int16)


def differs(a, b):
    if not a.endswith(".png"):
        return None if open(a, "rb").read() == open(b, "rb").read() else "differs from what the sources make"
    x, y = on_black(a), on_black(b)
    if x.shape != y.shape:
        return f"{x.shape[1]}x{x.shape[0]} committed, {y.shape[1]}x{y.shape[0]} made"
    mean, peak = TOLERANCE[os.path.basename(os.path.normpath(A))]
    d = np.abs(x - y)
    if d.mean() > mean or d.max() > peak:
        return f"differs from what the sources make (mean {d.mean():.2f}, peak {d.max()})"
    return None


names = lambda d: {os.path.relpath(p, d) for p in glob.glob(f"{d}/**/*", recursive=True) if os.path.isfile(p)}
committed, regenerated = names(A), names(B)
problems = [f"{n}: committed, not made by the sources" for n in sorted(committed - regenerated)]
problems += [f"{n}: made by the sources, not committed" for n in sorted(regenerated - committed)]
for n in sorted(committed & regenerated):
    if why := differs(f"{A}/{n}", f"{B}/{n}"):
        problems.append(f"{A}/{n}: {why}")
if problems:
    sys.exit("\n".join(problems) + "\nregenerate and commit: task plymouth logo wallpaper palette")
print(f"{A}/: {len(committed)} files match the sources")
