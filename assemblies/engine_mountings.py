"""Front engine mountings (Haynes Ch 1 Fig 1.29 items 1-16, 39; Sec 64).

Car frame (mgb.engine_mount_layout). With the engine supported (Sec 64): the nuts off the rubbers' studs at the
crossmember, the bracket screws out, bracket and rubber off together, then apart.
  nuts and washers under the crossmember pads; on the bracket flanges         orders 80-81
  bracket screws (block, LH; through the front plate wing, RH)                  order 82
  brackets off; rubbers and packing plates off the crossmember                  orders 83-84
"""
from build123d import Location, Rot

from mgb import engine_mount_layout as M, fasteners as F
from mgb.chassis_geom import IN
from parts.engine import mountings as P

ID = "engine.mountings"
NAME = "Front engine mountings"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.29"}], "section": 64}
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "engine.mountings." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


ID_ = Location()
for s in (1, -1):
    n = list(M.n_of(s))
    add("rubber-lh" if s > 0 else "rubber-rh", ID_, explode=ex(n, 84, 120))
    add("packing-plate", ID_, explode=ex(n, 84, 60), **({} if s > 0 else {"build": {"side": -1}}))
    add("bracket-lh" if s > 0 else "bracket-rh", ID_, explode=ex(n, 83, 200))
    for dx in (-M.STUD_DX, M.STUD_DX):
        def frame(k):
            f = P.pad_frame(k)
            if s < 0:
                p = M.side(-1, M.along(M.PAD, M.N, k))
                from mgb.chassis_geom import frame_to
                f = frame_to(p, M.n_of(-1), (1.0, 0.0, 0.0))
            return f * Location((dx, 0, 0))
        top = M.STACK + M.BRACKET_T
        add("stud-washer", frame(top), explode=ex(n, 81, 60))
        add("stud-nut", frame(top + 1.6), explode=ex(n, 81, 90))
        add("stud-washer", frame(-3.0) * Rot(180, 0, 0), explode=ex([-v for v in n], 80, 60))
        add("stud-nut", frame(-3.0 - 1.6) * Rot(180, 0, 0), explode=ex([-v for v in n], 80, 90))
# left-hand bracket: two screws into the block's pad
for x, z in M.LH_SCREWS:
    y = M.PLATE_Y + M.BRACKET_T
    add("screw-washer", Location((x, y, z)) * Rot(-90, 0, 0), explode=ex([0, 1, 0], 82, 40))
    add("screw-lh", Location((x, y + 1.6, z)) * Rot(90, 0, 0), explode=ex([0, 1, 0], 82, 90))
# right-hand bracket: two screws through the front plate's wing and the bracket's tab, nuts behind
from parts.engine.block import plates as PL
for y, z in PL.MOUNT_HOLES:
    if abs(y) > 125.0:
        add("screw-rh", Location((233.2, y, z)) * Rot(0, -90, 0), explode=ex([1, 0, 0], 82, 90))
        add("nut-rh", Location((M.RH_TAB_X[0], y, z)) * Rot(0, -90, 0), explode=ex([-1, 0, 0], 82, 50))
INSTANCES = I
