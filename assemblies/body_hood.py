"""Hood (soft top), erected. Explode: the cover and rear window lifted off the frame, then the frame."""
from build123d import Location, Rot

ID = "body.hood"
NAME = "Hood"
PARENT = "body"
HAYNES = {"section": 1}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"hood": {"axis": UP, "order": 2, "distance_mm": 400}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    pid = part if "." in part else f"body.hood.{part}"
    I.append((f"{pid}#{n}", pid, loc, o))


add("cover", groups=["hood"])
add("rear-window", groups=["hood"])
add("seams", groups=["hood"])
for p in ("bow-front", "bow-middle", "bow-rear", "side-rail-l", "side-rail-r"):
    add(p, explode=ex(UP, 3, 200))
INSTANCES = I
