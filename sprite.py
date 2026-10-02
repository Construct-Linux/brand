import cv2, glob, math, sys
import numpy as np

# usage: sprite.py [frames_dir] [out.png] [cols] [thumb_px]
SRC = sys.argv[1] if len(sys.argv) > 1 else "frames"
OUT = sys.argv[2] if len(sys.argv) > 2 else "sprite.png"
COLS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
THUMB = int(sys.argv[4]) if len(sys.argv) > 4 else 270
GAP = 4

files = sorted(glob.glob(f"{SRC}/construct_*.png"))
if not files:
    sys.exit(f"no frames in {SRC}/ (run video.py first)")
rows = math.ceil(len(files) / COLS)
sheet = np.full((rows * (THUMB + GAP) + GAP, COLS * (THUMB + GAP) + GAP, 3), 40, np.uint8)
for i, f in enumerate(files):
    t = cv2.resize(cv2.imread(f), (THUMB, THUMB), interpolation=cv2.INTER_AREA)
    # frame number, top-left
    cv2.putText(t, str(i + 1), (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(t, str(i + 1), (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
    r, c = divmod(i, COLS)
    y, x = GAP + r * (THUMB + GAP), GAP + c * (THUMB + GAP)
    sheet[y:y + THUMB, x:x + THUMB] = t
cv2.imwrite(OUT, sheet)
print(f"{OUT}: {len(files)} frames, {COLS}x{rows} grid, {sheet.shape[1]}x{sheet.shape[0]}px")
