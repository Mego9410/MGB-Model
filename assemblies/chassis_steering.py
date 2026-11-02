"""Steering gear, column and wheel, RHD (Haynes Ch 11 Fig 11.6, Fig 11.8; Secs 12, 17-19, 23, 26, 29).

Rack parts in the car frame; the pinion, joint, column and wheel parts in the column frame of
mgb.steering_layout (pinion and column on one axis, Sec 20). Explode stages follow Sec 18 (wheel), Sec 19 (column)
and Sec 23 (rack removal), then Sec 26 (rack dismantling):
  Sec 18          horn push; wheel nut; steering wheel off                        orders 60-62
  Sec 19          joint pinch bolts; clamp and bottom bracket; column out         orders 63-65
  Sec 23          ball joint nuts; joints out of the levers; rack fixing bolts;
                  brackets and shims; rack out                                    orders 66-69
  Sec 26          gaiters and clips; ball housings and tie-rods; covers;
                  pinion; rack out of the housing                                 orders 70-74
"""
from build123d import Location, Rot

from mgb import fasteners as F, front_suspension_layout as FS, steering_layout as S
from mgb.chassis_geom import IN
from parts.chassis import steering as P

ID = "chassis.steering"
NAME = "Steering gear, column and wheel (RHD)"
PARENT = "chassis"
HAYNES = {"figures": [{"figure": "11.6"}, {"figure": "11.8"}], "section": 23}

UP, DOWN, FWD, BACK = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0]
COL = list(S.COLUMN_DIR)
GROUPS = {"wheel": {"axis": COL, "order": 62, "distance_mm": 260},
          "column": {"axis": COL, "order": 65, "distance_mm": 420},
          "rack": {"axis": DOWN, "order": 69, "distance_mm": 240}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "chassis.steering." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def sided(s):
    return {"build": {"side": -1}} if s < 0 else {}


CF = P.col_frame
ID_ = Location()
RX, RZ = S.RACK_X, S.RACK_Z
MIRROR_Y = Rot(0, 0, 180)

# ---- rack and pinion ------------------------------------------------------------------------------------------
add("rack-housing", ID_, groups=["rack"])
add("rack", ID_, groups=["rack"], explode=ex([0, 1, 0], 74, 360))
add("pinion", CF(S.PINION_T[0]), groups=["rack"], explode=ex([-c for c in COL], 73, 160))
add("pinion-bearing", CF(S.PINION_TEETH_T[1] + 4.0), groups=["rack"], explode=ex(COL, 73, 120))
add("end-cover", CF(S.PINION_HOUSING_T[0]), groups=["rack"], explode=ex([-c for c in COL], 72, 80))
for y in (24.0, -24.0):
    add("end-cover-washer", CF(S.PINION_HOUSING_T[0]) * Location((0, y, -4.0)) * Rot(180, 0, 0), groups=["rack"], explode=ex([-c for c in COL], 72, 120))
    add("end-cover-bolt", CF(S.PINION_HOUSING_T[0]) * Location((0, y, -5.3)) * Rot(180, 0, 0), groups=["rack"], explode=ex([-c for c in COL], 72, 150))
zc = RZ - S.HOUSING_R - 22.0
add("yoke", Location((RX, S.PINION_Y, zc + 2.0)), groups=["rack"], explode=ex(DOWN, 72, 60))
add("damper-cover", Location((RX, S.PINION_Y, zc)), groups=["rack"], explode=ex(DOWN, 72, 100))
for dx in (-21.0, 21.0):
    add("damper-cover-washer", Location((RX + dx, S.PINION_Y, zc - 4.0)) * Rot(180, 0, 0), groups=["rack"], explode=ex(DOWN, 72, 130))
    add("damper-cover-bolt", Location((RX + dx, S.PINION_Y, zc - 5.3)), groups=["rack"], explode=ex(DOWN, 72, 160))
add("lubricator", CF(0.0) * Location((35.0, 0, 8.0)) * Rot(0, 90, 0), groups=["rack"])
for s in (1, -1):
    loc = ID_ if s > 0 else MIRROR_Y * Location((-2 * RX, 0, 0))
    # brackets, shims and bolts
    add("bracket", ID_ if s > 0 else Location((2 * RX, 0, 0)) * Rot(0, 0, 180), explode=ex(UP, 68, 60))
    add("shim", ID_ if s > 0 else Location((2 * RX, 0, 0)) * Rot(0, 0, 180), explode=ex(DOWN, 68, 30))
    for dx in (-FS.RACK_BOLT_DX, FS.RACK_BOLT_DX):
        zb = FS.RACK_BOSS_TOP + FS.RACK_SHIM_T + 3.5
        add("rack-bolt-washer", Location((RX + dx, s * FS.RACK_CLAMP_Y, zb)), explode=ex(UP, 67, 40))
        add("rack-bolt", Location((RX + dx, s * FS.RACK_CLAMP_Y, zb + 1.6)) * Rot(180, 0, 0), explode=ex(UP, 67, 90))
    # ball housing, locknut, tie-rod, gaiter and clips, outer joint, nuts
    add("ball-locknut", loc, groups=["rack"], explode=ex([0, s, 0], 71, 40))
    add("ball-housing", loc, groups=["rack"], explode=ex([0, s, 0], 71, 120))
    add("tie-rod", ID_, groups=["rack"], explode=ex([0, s, 0], 71, 140), **sided(s))
    add("gaiter", ID_, groups=["rack"], explode=ex([0, s, 0], 70, 60), **sided(s))
    y_in = S.HOUSING_Y[1] - 9.0
    add("inner-clip", Location((RX, s * y_in, RZ)) * Rot(-90 * s, 0, 0), groups=["rack"], explode=ex([0, s, 0], 70, 30))
    a, b = P._tie_rod_ends()
    yo = 417.0
    zo = a[2] + (b[2] - a[2]) * (yo - a[1]) / (b[1] - a[1])
    add("outer-clip", Location((RX, s * yo, zo)) * Rot(-90 * s, 0, 0), groups=["rack"], explode=ex([0, s, 0], 70, 30))
    add("outer-joint", ID_, explode=ex(DOWN, 66, 80), **sided(s))
    bx, by, bz = FS.ARM_BALL
    add("joint-washer", Location((bx, s * by, bz + 9.0)), explode=ex(UP, 66, 30))
    add("joint-nut", Location((bx, s * by, bz + 10.7)), explode=ex(UP, 66, 60))
    add("tie-rod-locknut", Location((b[0], s * (S.OUTER_SHANK_Y - 0.5), b[2])) * Rot(90 * s, 0, 0), groups=["rack"], explode=ex([0, -s, 0], 70, 30))

# ---- universal joint and column ---------------------------------------------------------------------------------
add("uj-yoke", CF(S.UJ_T - 44.0) * Rot(0, 0, 100), groups=["column"], explode=ex(COL, 63, 40))
add("uj-spider", CF(S.UJ_T) * Rot(0, 0, 135), groups=["column"])
add("uj-yoke", CF(S.UJ_T + 44.0) * Rot(180, 0, 190), groups=["column"], explode=ex(COL, 63, 80))
for t, rz in ((S.UJ_T - 44.0 + 26.0 * 0.55, 100), (S.UJ_T + 44.0 - 26.0 * 0.55, 190)):
    add("uj-bolt", CF(t) * Rot(0, 0, rz) * Location((-7.0, 20.0, 0)) * Rot(0, 90, 0), explode=ex(COL, 63, 20))
    add("uj-washer", CF(t) * Rot(0, 0, rz) * Location((7.0, 20.0, 0)) * Rot(0, 90, 0), explode=ex(COL, 63, 30))
    add("uj-nut", CF(t) * Rot(0, 0, rz) * Location((8.3, 20.0, 0)) * Rot(0, 90, 0), explode=ex(COL, 63, 40))
add("inner-column", CF(S.COLUMN_T0), groups=["column"], explode=ex(COL, 65, 200))
add("outer-tube", CF(S.OUTER_TUBE_T[0]), groups=["column"])
add("lower-bearing", CF(S.OUTER_TUBE_T[0] + 22.0) * Rot(180, 0, 0), groups=["column"], explode=ex([-c for c in COL], 65, 40))
add("upper-bearing", CF(S.OUTER_TUBE_T[1] - 22.0), groups=["column"], explode=ex(COL, 65, 60))
add("column-clamp", CF(S.UPPER_CLAMP_T), groups=["column"], explode=ex(DOWN, 64, 60))
r = S.OUTER_TUBE_R + 0.2
add("clamp-bolt", CF(S.UPPER_CLAMP_T) * Location((r + 16.0, -20.0, 0)) * Rot(-90, 0, 0), explode=ex(DOWN, 64, 30))
add("clamp-washer", CF(S.UPPER_CLAMP_T) * Location((r + 16.0, 20.0, 0)) * Rot(-90, 0, 0), explode=ex(DOWN, 64, 30))
add("clamp-nut", CF(S.UPPER_CLAMP_T) * Location((r + 16.0, 21.3, 0)) * Rot(-90, 0, 0), explode=ex(DOWN, 64, 30))
add("draught-excluder", CF(S.TOE_BOARD_T - 41.0), groups=["column"], explode=ex([-c for c in COL], 64, 60))
add("bottom-bracket", CF(S.TOE_BOARD_T), groups=["column"], explode=ex(COL, 64, 50))
add("blanking-plate", CF(S.TOE_BOARD_T + 3.0), groups=["column"], explode=ex(COL, 64, 70))
for y in (44.0, -44.0):
    add("bracket-nut", CF(S.TOE_BOARD_T + 4.5) * Location((0, y, 0)), explode=ex(COL, 64, 90))

# ---- steering wheel ----------------------------------------------------------------------------------------------
add("wheel", CF(S.WHEEL_T), groups=["wheel"])
add("wheel-nut", CF(S.WHEEL_T + 9.0), groups=["wheel"], explode=ex(COL, 61, 60))
add("horn-push", CF(S.WHEEL_T + 26.2), groups=["wheel"], explode=ex(COL, 60, 120))
INSTANCES = I
