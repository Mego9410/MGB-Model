"""Windscreen (Haynes Ch 12 Sec 18, Figs 12.7-12.9). Explode follows Sec 18: the mirror and centre rod off, the screen
assembly lifted off the scuttle, then the glass out of the frame."""
from build123d import Location, Rot

ID = "body.glass"
NAME = "Windscreen"
PARENT = "body"
HAYNES = {"section": 18}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"screen": {"axis": UP, "order": 3, "distance_mm": 300}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    pid = part if "." in part else f"body.glass.{part}"
    I.append((f"{pid}#{n}", pid, loc, o))


add("mirror", explode=ex(BACK, 1, 120))
add("centre-rod", explode=ex(BACK, 2, 150))
add("windscreen", groups=["screen"], explode=ex(BACK, 4, 160))
for p in ("top-rail", "bottom-rail", "pillar-l", "pillar-r"):
    add(p, groups=["screen"])
INSTANCES = I
