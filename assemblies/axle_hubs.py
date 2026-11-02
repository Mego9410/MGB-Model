"""Axleshafts and rear hubs, wire wheels (Haynes Ch 8 Fig 8.1 items 2, 3, 6, 41-46, 51-55; Sec 4 paras
5-7, Sec 5).

Every part is drawn at the left-hand hub in the axle frame (mgb.rear_axle_layout AF); the right-hand
copies are turned half round the vertical axis (a rotation: the threads keep their hand). The
handed parts are separate: the right-hand hub has the RH extension (item 42, left-hand spinner
thread) and the RH-thread bearing nut (item 2); the left-hand hub the LH extension (item 43) and
the LH-thread nut (item 3). The drum and its four nuts are P8. Explode stages (each side outward):
  Sec 4 para 6   the extension flange screw out; the hub extension pulled off with
                 its Welch plug and the O-ring; the axleshaft withdrawn              orders 120-123
  Sec 5 paras 2-3 locking washer tab knocked back, the bearing nut off, the locking
                 washer; the hub drawn off with the bearing and seal; the bearing
                 and seal out of the hub                                             orders 124-127
"""
from build123d import Location, Rot

from mgb import rear_axle_layout as A
from parts.axle import hubs as H

ID = "axle.hubs"
NAME = "Axleshafts and rear hubs (wire wheels)"
PARENT = "axle"
HAYNES = {"figures": [{"figure": "8.1"}], "section": 5}

LEFT, RIGHT = [0, 1, 0], [0, -1, 0]
GROUPS = {"ext-l": {"axis": LEFT, "order": 121, "distance_mm": 260},
          "ext-r": {"axis": RIGHT, "order": 121, "distance_mm": 260},
          "hub-l": {"axis": LEFT, "order": 126, "distance_mm": 90},
          "hub-r": {"axis": RIGHT, "order": 126, "distance_mm": 90}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "axle.hubs." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


AF = A.AF
for s in (1, -1):
    F = AF if s > 0 else AF * Rot(0, 0, 180)
    out = LEFT if s > 0 else RIGHT
    k = "l" if s > 0 else "r"
    x, z = H._pt(A.STUD_PCD / 2, A.SCREW_ANGLE)
    add("screw", F * Location((x, A.EXT_FLANGE_Y[1], z)) * Rot(90, 0, 0), explode=ex(out, 120, 380))
    add("hub-extension-lh" if s > 0 else "hub-extension-rh", F, groups=[f"ext-{k}"])
    add("welch-plug", F, groups=[f"ext-{k}"], explode=ex(out, 122, 60))
    add("o-ring", F, groups=[f"ext-{k}"], explode=ex([-v for v in out], 122, 40))
    add("axleshaft", F, explode=ex(out, 123, 900))
    add("bearing-nut-lh" if s > 0 else "bearing-nut-rh", F, explode=ex(out, 124, 190))
    add("lockwasher", F, explode=ex(out, 125, 150))
    add("hub", F, groups=[f"hub-{k}"])
    for a in A.STUD_ANGLES:
        xs, zs = H._pt(A.STUD_PCD / 2, a)
        add("hub-stud", F * Location((xs, A.HUB_FLANGE_Y[0], zs)) * Rot(-90, 0, 0), groups=[f"hub-{k}"])
    add("hub-bearing", F, groups=[f"hub-{k}"], explode=ex(out, 127, 60))
    add("hub-seal", F, groups=[f"hub-{k}"], explode=ex([-v for v in out], 127, 40))
INSTANCES = I
