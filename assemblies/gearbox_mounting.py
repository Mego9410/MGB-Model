"""Gearbox rear mounting, early cars: the two rubber mountings on the overdrive main casing and the
removable rear crossmember (Haynes Ch 1 Fig 1.29 items 17-19, 33-38; Sec 6 paras 33-35 and 38;
Ch 6 specifications).

Built in the gearbox frame (GF) at the overdrive stations; crossmember datums in
mgb.chassis_layout (P9/P11 attach the body side). Explode stages follow Ch 1 Sec 6 (the gearbox is
supported first):
  para 33  crossmember bolts out of the body                                       order 1
  para 35  the mounting nuts and washers under the crossmember; crossmember away   orders 2-3
  Sec 64   the two screws each side; the mountings off the casing                  orders 4-5
"""
from build123d import Location, Rot

from mgb import chassis_layout as K, gearbox_layout as G, overdrive_layout as O
from parts.gearbox import mounting as M

ID = "gearbox.mounting"
NAME = "Gearbox rear mountings and crossmember"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "1.29"}], "section": 6}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"crossmember": {"axis": DOWN, "order": 3, "distance_mm": 160}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.mounting." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF
EC = K.MOUNT_E


def at(u, l, e):
    return GF * Location((u, l, O.d(e)))


MIRROR = Location((0, 0, O.d(EC))) * Rot(180, 0, 0) * Location((0, 0, -O.d(EC)))   # left -> right about the vertical


add("crossmember", GF, groups=["crossmember"])
for s in (1, -1):
    side = LEFT if s > 0 else RIGHT
    # mounting, its screws into the casing pad
    add("mounting", GF if s > 0 else GF * MIRROR, explode=ex([0, s * 0.6, -0.8], 5, 120))
    yw = s * (O.MOUNT_FACE + M.PLATE_T)
    for e, u in O.MOUNT_SCREWS:
        add("mounting-screw-washer", at(u, yw, e) * Rot(-90 * s, 0, 0), explode=ex(side, 4, 40))
        add("mounting-screw", at(u, yw + s * 2.0, e) * Rot(90 * s, 0, 0), explode=ex(side, 4, 70))
    # stud: plain washer, spring washer and nut under the crossmember ear
    y = s * K.MOUNT_STUD_LEFT
    z0 = K.PAD_UP - K.XM_T
    add("stud-plain-washer", at(z0, y, EC) * Rot(0, -90, 0), explode=ex(DOWN, 2, 40))
    add("stud-washer", at(z0 - 1.65, y, EC) * Rot(0, -90, 0), explode=ex(DOWN, 2, 60))
    add("stud-nut", at(z0 - 4.05, y, EC) * Rot(0, -90, 0), explode=ex(DOWN, 2, 85))
    # crossmember screws up into the body
    zb = K.BODY_UP - K.XM_T
    for de in (-K.BOLT_DE, K.BOLT_DE):
        add("crossmember-washer", at(zb, s * K.BOLT_LEFT, EC + de) * Rot(0, -90, 0), explode=ex(DOWN, 1, 50))
        add("crossmember-screw", at(zb - 2.4, s * K.BOLT_LEFT, EC + de) * Rot(0, 90, 0), explode=ex(DOWN, 1, 90))
INSTANCES = I
