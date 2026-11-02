"""Handbrake, early layout (Haynes Ch 9 Fig 9.10; Secs 4 and 16).

Lever and cable in the car frame, compensator and rods in the axle frame (all built in place); the clevis pins
and their split pins are placed here. The fulcrum pin is P7's (axle.casing); the backplate levers are
brakes.rear's.
Explode stages, in the Haynes order (Sec 16 paras 1-6):
  the adjusting nut off and the cable pulled out of the trunnion                       orders 1-2
  the lever: nut and washer, operating lever, the lever drawn out; the ratchet plate's
  three bolts and the plate                                                            orders 3-5
  the cable clips; the cable freed from the compensating lever                         orders 6-7
  split pins and clevis pins out, the rods off; the compensator off its pin            orders 8-10
"""
import math

from build123d import Location, Plane, Rot

from mgb import brake_layout as B, rear_axle_layout as A
from parts.brakes import handbrake as H

ID = "brakes.handbrake"
NAME = "Handbrake lever, cable and compensator"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.10"}], "section": 16}

UP, DOWN, FWD, BACK, LEFT, RIGHT = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
GROUPS = {"lever": {"axis": UP, "order": 4.5, "distance_mm": 180},
          "cable": {"axis": DOWN, "order": 7, "distance_mm": 150},
          "comp": {"axis": BACK, "order": 10, "distance_mm": 120}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc=None, **o):
    pid = "brakes.handbrake." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc if loc is not None else Location((0, 0, 0)), o))


# ---- trunnion end ----------------------------------------------------------------------------------
add("adjusting-nut", explode=ex(FWD, 1, 50))
add("trunnion", explode=ex(DOWN, 2, 40))
add("cable-washer-front", explode=ex(BACK, 2, 20))
add("cable-spring", explode=ex(BACK, 2, 30))
add("cable-washer-rear", explode=ex(BACK, 2, 40))
# ---- lever ---------------------------------------------------------------------------------------------
add("lever-nut", explode=ex(LEFT, 3, 60))
add("washer-lever", explode=ex(LEFT, 3, 40))
add("operating-lever", explode=ex(DOWN, 3.5, 80))
for part in ("handle", "grip", "knob", "knob-spring", "pawl-rod", "pawl", "washer-handle"):
    add(part, groups=["lever"])
for x, z in H.ratchet_bolts():
    add("ratchet-bolt", Location((x, H.PAWL_Y[0], z)) * Rot(90, 0, 0) * Rot(180, 0, 0), explode=ex(RIGHT, 5, 40))
add("ratchet-plate", explode=ex(RIGHT, 5, 80))
# ---- cable -----------------------------------------------------------------------------------------------
add("floor-clip", explode=ex(DOWN, 6, 40))
add("axle-clip", explode=ex(UP, 6, 40))
add("cable", groups=["cable"])
add("cable-inner", groups=["cable"])
# ---- rods and compensator -------------------------------------------------------------------------------
pin_len = 16.0
for side in (1, -1):
    a, b = H.rod_points(side)
    # compensator end: pin along x, head at the rear; wheel end: pin along z, head on top
    for p, axis in ((a, (-1, 0, 0)), (b, (0, 0, 1))):
        fr = A.AF * Plane(origin=p, z_dir=axis).location
        add("clevis-pin", fr, explode=ex([*axis] if axis[2] else BACK, 8, 40))
        tail = fr * Location((0, 0, -pin_len / 2 + 2.2)) * Rot(90, 0, 0) * Location((0, 0, -9.0))
        add("rod-split-pin", tail, explode=ex(DOWN if axis[2] else FWD, 8, 30))
    add("rod-lh" if side > 0 else "rod-rh", explode=ex(DOWN, 9, 90))
for part in ("comp-split-pin", "comp-washer-outer", "comp-anti-rattle-washer"):
    add(part, explode=ex(BACK, 9.5, 40))
for part in ("comp-lever-outer", "comp-bush", "comp-lever-inner", "comp-washer-inner"):
    add(part, groups=["comp"])
INSTANCES = I
