"""Rear outer panels: rear wings, rear deck, boot lid and rear panel (Haynes Ch 12 Sec 25-26).

Explode: the boot lid off its hinges first (Sec 26), then the rear wings outward, the deck up and the rear panel
back (welded panels, shown apart by area)."""
from build123d import Location

ID = "body.rear"
NAME = "Rear panels and boot lid"
PARENT = "body"
HAYNES = {"section": 26}
LOD = "body"
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"boot": {"axis": UP, "order": 1, "distance_mm": 420}}
I = []
O = Location((0, 0, 0))


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc=O, n=1, **o):
    I.append((f"body.rear.{part}#{n}", f"body.rear.{part}", loc, o))


add("boot-skin", groups=["boot"])
add("boot-frame", groups=["boot"])
add("boot-handle", groups=["boot"], explode=ex(BACK, 0.5, 100))
add("boot-lock", explode=ex(BACK, 0.5, 120))
add("boot-hinge-l", explode=ex(UP, 1.5, 150))
add("boot-hinge-r", explode=ex(UP, 1.5, 150))
add("rear-wing-l", explode=ex(LEFT, 2, 350))
add("rear-wing-r", explode=ex(RIGHT, 2, 350))
add("rear-deck", explode=ex(UP, 3, 250))
add("rear-panel", explode=ex(BACK, 3, 250))
# spare wheel lying on the boot floor's locating ring, valve up (P9's parts, no spinner), and its clamp
from build123d import Rot  # noqa: E402
from mgb import underbody_layout as U, wheel_layout as WL  # noqa: E402
from parts.body import structure as St  # noqa: E402
SP = Location((St.SPARE_X, St.SPARE_Y, U.BOOT_FLOOR_Z + St.T + 80.0 - WL.CENTRE_PLANE)) * Rot(90, 0, 0)
for p in ("wheel", "tyre", "valve"):
    I.append((f"body.rear.spare-{p}#1", f"wheels.road-wheels.{p}", SP, {"explode": ex(UP, 4, 350)}))
add("spare-clamp", explode=ex(UP, 3.5, 450))
add("boot-carpet", explode=ex(UP, 2.5, 200))
add("jack", explode=ex(UP, 3, 300))
add("hammer", explode=ex(UP, 3, 260))
INSTANCES = I
