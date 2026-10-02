import cv2, glob, sys

# usage: encode.py <frames_dir> <out.mp4> [duration_s]
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "construct.mp4"
DURATION = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
fps = len(files) / DURATION  # 48 frames / 5s = 9.6 fps
h, w = cv2.imread(files[0]).shape[:2]
vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
for f in files:
    vw.write(cv2.imread(f))
vw.release()
print(f"{OUT}: {len(files)} frames @ {fps:g} fps = {DURATION:g}s")
