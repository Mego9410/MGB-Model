"""Doors (Haynes Ch 12 Sec 29-39, Figs 12.13 and 12.15): outer skins, frames, hinges, glass, quarter-lights, locks
and pull handles.

Explode follows Sec 29-39: the trim pad and handles off, the glass and quarter-light out, then the door off its
hinges (Sec 32), outward."""
from build123d import Location

ID = "body.doors"
NAME = "Doors"
PARENT = "body"
HAYNES = {"section": 32}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"door-l": {"axis": LEFT, "order": 5, "distance_mm": 400}, "door-r": {"axis": RIGHT, "order": 5, "distance_mm": 400}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    I.append((f"body.doors.{part}#{n}", f"body.doors.{part}", loc, o))


for n, s_, out in (("l", 1, LEFT), ("r", -1, RIGHT)):
    g = [f"door-{n}"]
    add(f"glass-{n}", groups=g, explode=ex(UP, 1, 380))
    add(f"quarter-light-glass-{n}", groups=g, explode=ex(UP, 2, 300))
    add(f"quarter-light-frame-{n}", groups=g, explode=ex(UP, 2, 300))
    add(f"quarter-light-seal-{n}", groups=g, explode=ex(UP, 2, 300))
    add(f"glass-channel-{n}", groups=g, explode=ex(UP, 2, 300))
    add(f"pull-handle-{n}", groups=g, explode=ex(out, 3, 120))
    add(f"skin-{n}", groups=g)
    add(f"frame-{n}", groups=g)
    add(f"hinge-lower-{n}", explode=ex(FWD, 6, 80))
    add(f"hinge-upper-{n}", explode=ex(FWD, 6, 80))
    add(f"striker-{n}", explode=ex(BACK, 4, 60))
add("mirror", groups=["door-r"], explode=ex(RIGHT, 2.5, 160))
add("mirror-glass", groups=["door-r"], explode=ex(RIGHT, 2.5, 160))
INSTANCES = I
