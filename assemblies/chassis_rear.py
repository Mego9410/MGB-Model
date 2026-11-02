"""Rear suspension: leaf springs, U-bolts, plates and pads, pedestals and bump rubbers, eyebolts, shackles,
lever dampers and links, rebound straps (Haynes Ch 11 Fig 11.4 items 1-32, Fig 11.5; Secs 8, 10).

Car frame (mgb.rear_suspension_layout). Leaves, plates and pads are drawn in the spring frame and placed at
each spring's centre bolt; handed parts are built mirrored for the right (build option side -1). The rebound
spindle nut (Fig 11.4 item 26) is the axle's (axle.casing.spindle-nut). Explode stages follow Sec 8 para 1-2
and Sec 10:
  Sec 8 para 1   damper link off its bracket; rebound strap off the axle              orders 40-41
                 shackle nuts and plate; pin plate out; eyebolt out                    orders 42-44
                 U-bolt nuts and locknuts; U-bolts, bracket, plates, pads; spring down  orders 45-46
  Sec 8 para 2   clips straightened, centre bolt out, leaves apart                      orders 47-48
  Sec 10         damper bolts; damper off the side member                               orders 49-50
"""
from build123d import Location, Rot

from mgb import fasteners as F, rear_axle_layout as A, rear_suspension_layout as R
from mgb.chassis_geom import IN

ID = "chassis.rear"
NAME = "Rear suspension"
PARENT = "chassis"
HAYNES = {"figures": [{"figure": "11.4"}, {"figure": "11.5"}], "section": 8}

UP, DOWN, FWD, BACK = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0]
GROUPS = {}
for s, k in ((1, "l"), (-1, "r")):
    GROUPS[f"spring-{k}"] = {"axis": DOWN, "order": 46, "distance_mm": 220}
    GROUPS[f"damper-{k}"] = {"axis": [0, -s, 0], "order": 50, "distance_mm": 160}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "chassis.rear." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def sided(s, extra=None):
    b = {} if s > 0 else {"side": -1}
    if extra:
        b.update(extra)
    return {"build": b} if b else {}


def Y(s, p):
    return (p[0], s * p[1], p[2])


def along_y(s, p, out=True):
    """Fastener drawn along +z placed at car point p (left-hand values), pointing outboard or inboard."""
    d = s if out else -s
    return Location(Y(s, p)) * Rot(-90 if d > 0 else 90, 0, 0)


ID_ = Location()
W = R.LEAF_W
NUT716 = F.NUT["7/16"][1] * IN
for s, k in ((1, "l"), (-1, "r")):
    sp = [f"spring-{k}"]
    SF = Location((R.AX, s * R.SPRING_Y, 0))
    # ---- spring and its leaves ------------------------------------------------------------------------------
    for leaf, order in (("main-leaf", 48), ("second-leaf", 48), ("third-leaf", 48), ("fourth-leaf", 48), ("fifth-leaf", 48),
                        ("bottom-plate", 48)):
        add(leaf, SF, groups=sp, explode=ex(UP if leaf in ("main-leaf", "second-leaf") else DOWN, order,
                                            {"main-leaf": 80, "second-leaf": 40, "third-leaf": 20, "fourth-leaf": 50,
                                             "fifth-leaf": 80, "bottom-plate": 110}[leaf]))
    for c in ("clip-third", "clip-fourth"):
        add(c, SF, groups=sp, explode=ex(DOWN, 47, 30))
        add(c, SF, groups=sp, explode=ex(DOWN, 47, 30), build={"aft": 1})
    add("centre-bolt", SF, groups=sp, explode=ex(UP, 47, 120))
    add("centre-nut", SF * Location((0, 0, R.BOTTOM_Z - F.NUT["5/16"][1] * IN)), groups=sp, explode=ex(DOWN, 47, 60))
    # ---- plates, pads, bracket, U-bolts ------------------------------------------------------------------------
    add("locating-plate", SF * Location((0, 0, R.SEAT_Z)), groups=sp, explode=ex(UP, 45, 30))
    add("seating-pad", SF * Location((0, 0, R.SEAT_Z - R.PLATE18_T)), groups=sp, explode=ex(UP, 45, 18))
    add("seating-pad", SF * Location((0, 0, R.BOTTOM_Z)), groups=sp, explode=ex(DOWN, 45, 18))
    add("locating-plate", SF * Location((0, 0, R.BOTTOM_Z - R.PAD19_T - R.PLATE18_T)) * Rot(180, 0, 0), groups=sp,
        explode=ex(DOWN, 45, 36))
    add("damper-bracket", ID_, groups=sp, explode=ex(DOWN, 45, 60), **sided(s))
    for dy in (-R.UBOLT_DY, R.UBOLT_DY):
        y = s * (R.SPRING_Y + dy)
        add("u-bolt", Location((0, y, 0)), explode=ex(UP, 45, 160))
        for dx in (-R.UBOLT_X, R.UBOLT_X):
            z = R.BRACKET_UNDER_Z - NUT716
            add("u-bolt-nut", Location((R.AX + dx, y, z)), explode=ex(DOWN, 45, 120))
            add("u-bolt-locknut", Location((R.AX + dx, y, z - 6.2)), explode=ex(DOWN, 45, 150))
    # ---- pedestal and bump rubber ---------------------------------------------------------------------------------
    add("pedestal", ID_, explode=ex(UP, 45, 100), **sided(s))
    add("bump-rubber", Location((R.AX, s * R.SPRING_Y, R.PEDESTAL_TOP_Z)), explode=ex(UP, 45, 180))
    add("bump-nut", Location((R.AX, s * R.SPRING_Y, R.PEDESTAL_TOP_Z - 4.0 - F.NUT["5/16"][1] * IN)), explode=ex(UP, 45, 100))
    # ---- front eye: bush, eyebolt, washer, nut --------------------------------------------------------------------
    fx, fy, fz = R.FRONT_EYE
    add("eye-bush", Location(Y(s, R.FRONT_EYE)) * Rot(90, 0, 0), groups=sp)
    y_in = R.SPRING_Y - W / 2 - R.BUSH_FLANGE_T - 4.0
    y_out = R.SPRING_Y + W / 2 + R.BUSH_FLANGE_T + 4.0
    add("eyebolt", along_y(s, (fx, y_in, fz)), explode=ex([0, -s, 0], 44, 140))
    add("eyebolt-washer", along_y(s, (fx, y_out, fz)), explode=ex([0, s, 0], 44, 50))
    add("eyebolt-nut", along_y(s, (fx, y_out + 1.6, fz)), explode=ex([0, s, 0], 44, 80))
    # ---- rear shackle -----------------------------------------------------------------------------------------------
    sh_out = R.SPRING_Y + W / 2 + R.BUSH_FLANGE_T + 0.5 + 4.0
    add("shackle-plate", ID_, explode=ex([0, s, 0], 42, 60), **sided(s))
    add("shackle-pin-plate", ID_, explode=ex([0, -s, 0], 43, 90), **sided(s))
    for (x, z) in ((R.REAR_EYE[0], R.REAR_EYE[2]), (R.SHACKLE_TOP[0], R.SHACKLE_TOP[2])):
        add("shackle-washer", along_y(s, (x, sh_out, z)), explode=ex([0, s, 0], 42, 30))
        add("shackle-nut", along_y(s, (x, sh_out + 1.6, z)), explode=ex([0, s, 0], 42, 50))
        add("shackle-bush", along_y(s, (x, R.SPRING_Y - W / 2 - R.BUSH_FLANGE_T, z)), explode=ex([0, -s, 0], 43, 40))
        add("shackle-bush", along_y(s, (x, R.SPRING_Y + W / 2 + R.BUSH_FLANGE_T, z), out=False), explode=ex([0, s, 0], 43, 40))
    # ---- damper, link and fixings (Fig 11.5) ---------------------------------------------------------------------------
    gd = [f"damper-{k}"]
    add("damper", ID_, groups=gd, **sided(s))
    for x, z in R.DAMPER_BOLTS:
        add("damper-bolt", along_y(s, (x, R.DAMPER_FACE_Y - 8.0, z)), groups=gd, explode=ex([0, -s, 0], 49, 80))
        add("damper-plain-washer", along_y(s, (x, R.DAMPER_FACE_Y + 2.0, z)), explode=ex([0, s, 0], 49, 30))
        add("damper-spring-washer", along_y(s, (x, R.DAMPER_FACE_Y + 3.7, z)), explode=ex([0, s, 0], 49, 45))
        add("damper-nut", along_y(s, (x, R.DAMPER_FACE_Y + 5.0, z)), explode=ex([0, s, 0], 49, 60))
    add("link", ID_, groups=gd, explode=ex(DOWN, 40, 30), **sided(s))
    for z in (R.LINK_TOP_Z, R.LINK_LOW_Z):
        add("link-washer", along_y(s, (R.LINK_X, R.LINK_Y - 6.5, z), out=False), explode=ex([0, -s, 0], 40, 30))
        add("link-nut", along_y(s, (R.LINK_X, R.LINK_Y - 8.2, z), out=False), explode=ex([0, -s, 0], 40, 50))
    # ---- rebound strap -----------------------------------------------------------------------------------------------
    tx, ty, tz = R.STRAP_TOP[1]
    lx, ly, lz = R.STRAP_LOW[1]
    add("rebound-strap", ID_, explode=ex([0, s, 0], 41, 60), **sided(s))
    add("strap-tube", along_y(s, (tx, A.REBOUND_SPINDLE[1] - 7.0, tz)), explode=ex([0, s, 0], 41, 60))
    add("strap-bolt", along_y(s, (tx, A.REBOUND_SPINDLE[1] - 7.0 - 3.0, tz)), explode=ex([0, -s, 0], 41, 100))
    add("strap-plain-washer", along_y(s, (tx, A.REBOUND_SPINDLE[1] + 5.0 + 3.0, tz)), explode=ex([0, s, 0], 41, 80))
    add("strap-spring-washer", along_y(s, (tx, A.REBOUND_SPINDLE[1] + 5.0 + 4.7, tz)), explode=ex([0, s, 0], 41, 90))
    add("strap-nut", along_y(s, (tx, A.REBOUND_SPINDLE[1] + 5.0 + 6.0, tz)), explode=ex([0, s, 0], 41, 100))
    add("strap-plain-washer", along_y(s, (lx, A.REBOUND_SPINDLE[1] + 5.0, lz)), explode=ex([0, s, 0], 41, 80))
    add("strap-spring-washer", along_y(s, (lx, A.REBOUND_SPINDLE[1] + 6.65, lz)), explode=ex([0, s, 0], 41, 90))
INSTANCES = I
