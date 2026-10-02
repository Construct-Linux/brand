import cv2, glob, math, sys

# usage: encode.py <frames_dir> <out.mp4> [duration_s]
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "construct.mp4"
DURATION = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
if not math.isfinite(DURATION) or DURATION <= 0:
    sys.exit("duration must be a positive finite number")

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
fps = len(files) / DURATION  # 48 frames / 5s = 9.6 fps
shape = None
for f in files:
    img = cv2.imread(f)
    if img is None:
        sys.exit(f"cannot read frame {f}")
    if shape is None:
        shape = img.shape
    elif img.shape != shape:
        sys.exit(f"frame {f} has dimensions {img.shape}; expected {shape}")
h, w = shape[:2]
vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
if not vw.isOpened():
    vw.release()
    sys.exit(f"cannot create video {OUT}")
try:
    for f in files:
        vw.write(cv2.imread(f))
finally:
    vw.release()
# OpenCV's write() does not report failures; check the finished video.
cap = cv2.VideoCapture(OUT)
count = 0
try:
    while cap.isOpened():
        ok, img = cap.read()
        if not ok:
            break
        if img.shape[:2] != (h, w):
            sys.exit(f"video {OUT} has unexpected dimensions {img.shape[:2]}")
        count += 1
finally:
    cap.release()
if count != len(files):
    sys.exit(f"video {OUT} contains {count} frames; expected {len(files)}")
print(f"{OUT}: {len(files)} frames @ {fps:g} fps = {DURATION:g}s")
