import cv2, glob, math, sys

# usage: encode.py <frames_dir> <out.mp4> [duration_s]
# The preview video; nothing ships it.
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "construct.mp4"
DURATION = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
if not math.isfinite(DURATION) or DURATION <= 0:
    sys.exit("duration must be a positive finite number")

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
fps = len(files) / DURATION  # 48 frames / 5s = 9.6 fps
first = cv2.imread(files[0])
if first is None:
    sys.exit(f"cannot read frame {files[0]}")
h, w = first.shape[:2]
vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
if not vw.isOpened():
    sys.exit(f"cannot create video {OUT}")
try:
    for f in files:
        img = cv2.imread(f)
        if img is None or img.shape[:2] != (h, w):
            sys.exit(f"frame {f} is unreadable or not {w}x{h}")
        vw.write(img)
finally:
    vw.release()
print(f"{OUT}: {len(files)} frames @ {fps:g} fps = {DURATION:g}s")
