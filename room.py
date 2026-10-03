import numpy as np

# The room every image of the brand draws: a cube 3x3x3, x right, y up, z depth (z=0 the open
# front), seen by one camera. video.py builds it, wallpaper.py holds it still, logo.py is its
# outline.
# Front view, one-point perspective: the camera looks straight down +z with no yaw, pitch or
# roll, so every x line (floor front edge, the line above the word) stays horizontal and every
# y line stays vertical; only depth converges, to the vanishing point. Framing is done by
# shifting the image (like an architectural shift lens), never by turning the camera.
CAM = np.array([0.6, 1.2, -2.9])  # position (x, y=height, z=distance in front)


def project(p):
    """p on the image plane at focal length 1, x right and y down, the vanishing point at 0."""
    x, y, z = np.asarray(p, float) - CAM
    return np.array([x / z, -y / z])


def view(focal, width, cy):
    """Screen position of a point at this focal length (px), the floor's front edge centered
    across width and the vanishing point at height cy."""
    c = np.array([width / 2 - focal * project((1.5, 0, 0))[0], cy])
    return lambda p: c + focal * project(p)


# The outline, the logo's mark. Listed in drawing order from the back-right-bottom corner, so
# every edge starts at a vertex an earlier edge reaches: video.py draws it with pens that leave
# that corner together. The outer verticals hang from the top edges down to the floor.
OUTLINE = [  # (from, to)
    ((3, 0, 3), (0, 0, 3)),  # floor back edge
    ((3, 0, 3), (3, 0, 0)),  # floor / right wall seam
    ((3, 0, 3), (3, 3, 3)),  # corner axis
    ((0, 0, 3), (0, 0, 0)),  # floor left edge
    ((3, 0, 0), (0, 0, 0)),  # floor front edge
    ((3, 3, 3), (0, 3, 3)),  # back wall top edge
    ((3, 3, 3), (3, 3, 0)),  # right wall top edge
    ((0, 3, 3), (0, 0, 3)),  # back wall left edge, down
    ((3, 3, 0), (3, 0, 0)),  # right wall front edge, down
]

# The interior grid, the workspace: the room cut in thirds. Each line runs between two lines of
# the outline, in the direction video.py draws it.
FLOOR = [l for i in (1, 2) for l in (((i, 0, 3), (i, 0, 0)),     # columns, back -> front
                                     ((3, 0, i), (0, 0, i)))]    # rows, right -> left


def rows(y):
    """The walls' horizontal line at height y, each from the open edge to the corner axis."""
    return [((3, y, 0), (3, y, 3)), ((0, y, 3), (3, y, 3))]


# The walls' inner verticals, top -> floor.
COLUMNS = [l for k in (1, 2) for l in (((3, 3, 3 - k), (3, 0, 3 - k)),   # right wall
                                       ((3 - k, 3, 3), (3 - k, 0, 3)))]  # back wall
