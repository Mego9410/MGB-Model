"""Brake master cylinder and pedal box (Haynes Ch 9 Fig 9.11; Secs 17-18; the box after Fig 9.16 and Sec 19).

The cylinder is placed in its own frame on the pedal box's mounting wall (parts.brakes.master.frame), beside the
clutch cylinder (clutch.hydraulics); the box, cover and their fixings are built in the car frame. P11 builds the
bulkhead the box bolts to.
Explode stages, in the Haynes order:
  Sec 17 para 1  the four screws and washers out, the protecting cover off                   orders 1-2
  Sec 17 paras 2-4 cap and seal off to drain; the pipe union (banjo bolt, gaskets, banjo);
                 the two bolts, nuts and washers out; the cylinder off (the pushrod comes
                 off the pedal with the brake pedal's clevis pin, brakes.pedal)              orders 3-6
  Sec 18         boot, circlip, pushrod, piston with the secondary cup, piston washer,
                 main cup, spring retainer, spring and valve out of the bore                 orders 7-9
  Sec 19 para 7  the six bolts out and the box off the bulkhead                             orders 10-11
"""
from build123d import Location, Rot

from mgb import brake_layout as B, car_layout as CL
from mgb.brake_parts import plain_washer, spring_washer
from parts.brakes import master as M

ID = "brakes.master"
NAME = "Brake master cylinder and pedal box"
PARENT = "brakes"
HAYNES = {"figures": [{"figure": "9.11"}, {"figure": "9.16"}], "section": 17}

UP, DOWN, FWD, BACK, LEFT, RIGHT = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
GROUPS = {"cover": {"axis": UP, "order": 2, "distance_mm": 330},
          "pipe": {"axis": FWD, "order": 4, "distance_mm": 60},
          "master": {"axis": UP, "order": 6, "distance_mm": 150},
          "box": {"axis": FWD, "order": 11, "distance_mm": 260}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "brakes.master." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
MC = M.frame()
MAS = ["master"]

# ---- cover -------------------------------------------------------------------------------------------
wt = plain_washer("1/4")[1]
ct = 1.0
for x, y in M.cover_screws():
    add("cover-washer", Location((x, y, B.BOX_Z[1] + ct)), explode=ex(UP, 1, 40))
    add("cover-screw", Location((x, y, B.BOX_Z[1] + ct + wt)) * Rot(180, 0, 0), explode=ex(UP, 1, 70))
add("cover", O, groups=["cover"])

# ---- master cylinder ---------------------------------------------------------------------------------
add("mc-cap", MC, groups=MAS, explode=ex(UP, 3, 60))
add("mc-cap-seal", MC, groups=MAS, explode=ex(UP, 3, 40))
add("banjo-bolt", MC, explode=ex(FWD, 4, 60))
add("gasket-outer", MC, explode=ex(FWD, 4, 40))
add("banjo", MC, groups=["pipe"])
add("gasket-inner", MC, groups=["pipe"])
swt = spring_washer("5/16")[1]
for s, bolt in ((1, "mc-bolt-long"), (-1, "mc-bolt")):
    x = s * M.BOLT_X
    z = -B.BOX_FRONT_T
    add("mc-spring-washer", MC * Location((x, 0, z)) * Rot(180, 0, 0), explode=ex(BACK, 5, 40))
    add("mc-nut", MC * Location((x, 0, z - swt)) * Rot(180, 0, 0), explode=ex(BACK, 5, 70))
    add(bolt, MC * Location((x, 0, M.FLANGE_T)) * Rot(180, 0, 0), explode=ex(FWD, 5, 60))
add("mc-body", MC, groups=MAS)
add("boot", MC, groups=MAS, explode=ex(BACK, 7, 40))
add("circlip", MC, groups=MAS, explode=ex(BACK, 7.2, 60))
add("pushrod", MC, groups=MAS, explode=ex(BACK, 7.4, 90))
add("secondary-cup", MC, groups=MAS, explode=ex(BACK, 7.6, 120))
add("piston", MC, groups=MAS, explode=ex(BACK, 7.6, 120))
add("piston-washer", MC, groups=MAS, explode=ex(BACK, 8, 105))
add("main-cup", MC, groups=MAS, explode=ex(BACK, 8, 95))
add("spring-retainer", MC, groups=MAS, explode=ex(BACK, 8.5, 85))
add("mc-spring", MC, groups=MAS, explode=ex(BACK, 8.5, 80))
add("valve", MC, groups=MAS, explode=ex(BACK, 9, 70))

# ---- pedal box ---------------------------------------------------------------------------------------
for y, z in M.box_bolts():
    add("box-bolt", Location((B.BOX_REAR_X + B.BOX_T, y, z)) * Rot(0, -90, 0), explode=ex(FWD, 10, 60))
    add("box-spring-washer", Location((CL.BULKHEAD_X - 1.0, y, z)) * Rot(0, -90, 0), explode=ex(BACK, 10, 30))
    add("box-nut", Location((CL.BULKHEAD_X - 1.0 - swt, y, z)) * Rot(0, -90, 0), explode=ex(BACK, 10, 50))
add("pedal-box", O, groups=["box"])
INSTANCES = I
