"""Differential carrier with the pinion and the differential (Haynes Ch 8 Fig 8.1 items 7, 8, 12-39; Sec 7
pinion oil seal, Sec 8 differential assembly; the factory manual for the rest).

Placed at the axle frame (mgb.rear_axle_layout AF); every part is drawn in place in that frame,
the right-hand copies of handed parts turned half round the axle (x) axis. Explode stages:
  Sec 8 para 3   nuts and spring washers off the case studs; the carrier withdrawn
                 forward with the gasket                                              orders 130-131
  Sec 7 paras 4-5 pinion nut and spring washer, the flange, the end cover, the seal   orders 132-134
  (specialist, factory manual H.8) cap nuts and washers, the caps; the differential
                 out of the saddles; its bearings and packing washers; crown wheel
                 bolts and lockwashers, the crown wheel; peg, pinion shaft, pinions and
                 side gears with their thrust washers                                 orders 135-144
  the pinion back out of the nose with its rear bearing cone and thrust washer; the
                 spacer, shim and front bearing                                       orders 145-147
"""
import math

from build123d import Location, Rot

from mgb import rear_axle_layout as A

ID = "axle.carrier"
NAME = "Differential carrier, pinion and differential"
PARENT = "axle"
HAYNES = {"figures": [{"figure": "8.1"}], "section": 8}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"carrier": {"axis": FWD, "order": 131, "distance_mm": 420},
          "diff": {"axis": BACK, "order": 137, "distance_mm": 260},
          "crown": {"axis": LEFT, "order": 140, "distance_mm": 120},
          "pinion": {"axis": BACK, "order": 145, "distance_mm": 220}}
C, D, P = ["carrier"], ["carrier", "diff"], ["carrier", "pinion"]


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "axle.carrier." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


AF = A.AF
FLIP = Rot(180, 0, 0)                       # left-hand copy -> right-hand (half turn about the axle's x axis)

# carrier, gasket, nuts and spring washers on the case studs
add("carrier", AF, groups=C)
add("gasket", AF, groups=C, explode=ex(BACK, 131.5, 20))
for a in A.CASE_STUD_ANGLES:
    y, z = A.CASE_STUD_R * math.sin(math.radians(a)), A.CASE_STUD_R * math.cos(math.radians(a))
    add("carrier-washer", AF * Location((A.CARRIER_FLANGE[1], y, z)) * Rot(0, 90, 0), explode=ex(FWD, 130, 40))
    add("carrier-nut", AF * Location((A.CARRIER_FLANGE[1] + 2.0, y, z)) * Rot(0, 90, 0), explode=ex(FWD, 130, 70))

# bearing caps on their studs
ym = sum(A.SADDLE_Y) / 2
for s in (1, -1):
    side = AF if s > 0 else AF * FLIP
    add("bearing-cap", side, groups=C, explode=ex(BACK, 136, 90))
    for z in (A.CAP_STUD_Z, -A.CAP_STUD_Z):
        at = lambda x: AF * Location((x, s * ym, z)) * Rot(0, -90, 0)
        add("cap-stud", at(24.0), groups=C)
        add("cap-plain-washer", at(A.CAP_X[0]), groups=C, explode=ex(BACK, 135, 40))
        add("cap-spring-washer", at(A.CAP_X[0] - 1.65), groups=C, explode=ex(BACK, 135, 60))
        add("cap-nut", at(A.CAP_X[0] - 4.05), groups=C, explode=ex(BACK, 135, 80))

# pinion, its bearings, spacer, shim, seal, dust cover, flange, nut and washer
add("pinion", AF, groups=P)
add("pinion-thrust-washer", AF, groups=P)
add("rear-pinion-bearing", AF, groups=P)
add("bearing-spacer", AF, groups=C, explode=ex(FWD, 146, 140))
add("pinion-shim", AF, groups=C, explode=ex(FWD, 146.5, 170))
add("front-pinion-bearing", AF, groups=C, explode=ex(FWD, 147, 200))
add("pinion-seal", AF, groups=C, explode=ex(FWD, 134, 120))
add("dust-cover", AF, groups=C, explode=ex(FWD, 133.5, 140))
add("pinion-flange", AF, groups=C, explode=ex(FWD, 133, 160))
add("pinion-washer", AF, groups=C, explode=ex(FWD, 132, 200))
add("pinion-nut", AF, groups=C, explode=ex(FWD, 132, 230))

# differential: cage, crown wheel and its fixings, gears, bearings and packing washers
add("cage", AF, groups=D)
add("crown-wheel", AF, groups=D + ["crown"])
fy = A.CROWN_BACK_Y + 10.0                   # cage flange face the bolt heads sit on
lock_t = 0.9
for k in range(A.CROWN_BOLTS):
    a = 2 * math.pi * (k + 0.5) / A.CROWN_BOLTS
    x, z = A.CROWN_BOLT_R * math.cos(a), A.CROWN_BOLT_R * math.sin(a)
    add("crown-wheel-bolt", AF * Location((x, fy + lock_t, z)) * Rot(90, 0, 0), groups=D, explode=ex(LEFT, 139, 60))
for j in range(A.CROWN_BOLTS // 2):
    ac = 2 * math.pi * (2 * j + 1) / A.CROWN_BOLTS
    add("crown-wheel-lockwasher", AF * Location((0, fy, 0)) * Rot(-90, 0, 0) * Rot(0, 0, -math.degrees(ac)), groups=D,
        explode=ex(LEFT, 139, 40))
add("pinion-peg", AF, groups=D, explode=ex(UP, 141, 60))
add("pinion-shaft", AF, groups=D, explode=ex(FWD, 142, 160))
for s in (1, -1):
    side = AF if s > 0 else AF * FLIP
    out = LEFT if s > 0 else RIGHT
    add("diff-bearing", side, groups=D, explode=ex(out, 138, 80))
    add("packing-washer", side, groups=D, explode=ex(out, 138, 110))
    add("side-gear", side, groups=D, explode=ex(out, 144, 40))
    add("side-thrust-washer", side, groups=D, explode=ex(out, 144, 55))
for s in (1, -1):
    end = AF if s > 0 else AF * Rot(0, 0, 180)
    add("diff-pinion", end, groups=D, explode=ex(FWD if s > 0 else BACK, 143, 35))
    add("diff-pinion-thrust-washer", end, groups=D, explode=ex(FWD if s > 0 else BACK, 143, 50))
INSTANCES = I
