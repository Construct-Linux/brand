import cv2, sys

# usage: play.py [video.mp4]  -- loops until q / Esc
SRC = sys.argv[1] if len(sys.argv) > 1 else "construct.mp4"

cap = cv2.VideoCapture(SRC)
if not cap.isOpened():
    sys.exit(f"cannot open {SRC} (run encode.py first)")
delay = max(1, int(1000 / (cap.get(cv2.CAP_PROP_FPS) or 9.6)))
while True:
    ok, img = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    cv2.imshow(SRC, img)
    if cv2.waitKey(delay) & 0xFF in (ord("q"), 27):
        break
cap.release()
cv2.destroyAllWindows()
