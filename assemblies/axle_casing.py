"""Rear axle case and its fittings (Haynes Ch 8 Fig 8.1 items 1, 4, 5, 9-11; Sec 2-3).

Placed at the axle frame (mgb.rear_axle_layout AF: car_layout REAR_AXLE_X, WHEEL_Z, on the
centreline). The case itself stays put; its fittings explode off it:
  Sec 2   filler/level and drain plugs out, the breather off the top          order 150
  Sec 3   rebound spindle nuts off (the straps are P9)                       order 151
  Sec 8   gear carrier studs (left in the case in practice; shown off last)    order 152
(the hubs explode first, orders 120-127, then the carrier, 130-149)
"""
import math

from build123d import Location, Rot

from mgb import rear_axle_layout as A

ID = "axle.casing"
NAME = "Axle case (banjo) and fittings"
PARENT = "axle"
HAYNES = {"figures": [{"figure": "8.1"}], "section": 3}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "axle.casing." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


AF = A.AF
add("case", AF)
for a in A.CASE_STUD_ANGLES:
    y, z = A.CASE_STUD_R * math.sin(math.radians(a)), A.CASE_STUD_R * math.cos(math.radians(a))
    add("case-stud", AF * Location((A.CASE_FACE_X - 12.0, y, z)) * Rot(0, 90, 0), explode=ex(FWD, 152, 120))
bx, by = A.BREATHER
add("breather", AF * Location((bx, by, 55.0)), explode=ex(UP, 150, 60))
fy, fz = A.FILLER
add("filler-plug", AF * Location((-124.5, fy, fz)) * Rot(0, -90, 0), explode=ex(BACK, 150, 60))
dx, dy = A.DRAIN
add("drain-plug", AF * Location((dx, dy, -132.0)) * Rot(180, 0, 0), explode=ex(DOWN, 150, 60))
for s in (1, -1):
    sx, sy, sz = A.REBOUND_SPINDLE
    y0 = sy + 9.0                                        # strap eye, plain and spring washers between (P9)
    add("spindle-nut", AF * Location((sx, s * y0, sz)) * (Rot(-90, 0, 0) if s > 0 else Rot(90, 0, 0)),
        explode=ex(LEFT if s > 0 else RIGHT, 151, 60))
INSTANCES = I
