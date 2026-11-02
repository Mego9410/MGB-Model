"""Front crossmember and its body mountings (Haynes Ch 11 Fig 11.2 items 1-7, 15-18, 40-45; Sec 3, Sec 4).

Car frame (mgb.front_suspension_layout). Explode stages follow Ch 11 Sec 3 (removal: the nuts and washers off
the tops of the support bolts, the crossmember lowered complete) and Sec 4 (dismantling):
  Sec 3 para 2   nuts and washers (7) off the support bolts                      order 1
                 crossmember lowered away from the body                          order 2 (whole system offset)
  Sec 3 para 2   support bolts, plates and pads out                               orders 3-4
  Sec 4 para 1   rebound buffers off; spring spigots off                         orders 5-6
"""
from build123d import Location, Rot

from mgb import fasteners as F, front_suspension_layout as L

ID = "chassis.crossmember"
NAME = "Front crossmember and body mountings"
PARENT = "chassis"
HAYNES = {"figures": [{"figure": "11.2"}, {"figure": "11.1"}], "section": 3}

UP, DOWN = [0, 0, 1], [0, 0, -1]
GROUPS = {}
IN = 25.4


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "chassis.crossmember." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


SH = L.XM_SHELF_Z
NUT_T = F.NUT["7/16"][1] * IN
WASH_T = F.WASHER["7/16"][2] * IN
add("crossmember", Location())
for s in (1, -1):
    for x in L.BODY_BOLT_X:
        y = s * L.BODY_BOLT_Y
        add("upper-pad", Location((x, y, SH)), explode=ex(UP, 3, 60))
        add("plain-washer", Location((x, y, L.BODY_LEG_TOP_Z)), explode=ex(UP, 1, 50))
        add("nut", Location((x, y, L.BODY_LEG_TOP_Z + WASH_T)), explode=ex(UP, 1, 80))
        add("lower-pad", Location((x, y, SH - 3.0 - 6.0)), explode=ex(DOWN, 4, 40))
        add("plate", Location((x, y, SH - 3.0 - 6.0)) * Rot(180, 0, 0), explode=ex(DOWN, 4, 60))
        add("nut", Location((x, y, SH - 3.0 - 6.0 - 3.0 - NUT_T)), explode=ex(DOWN, 3, 80))
        add("support-bolt", Location((x, y, SH - 3.0 - 6.0 - 3.0 - NUT_T - 2.5)), explode=ex(DOWN, 3, 140))
    # spring spigot under the shelf, screws down from above, nuts and washers underneath
    add("spigot", Location((L.SPRING_X, s * L.PAN_Y, SH - 3.0)), explode=ex(DOWN, 6, 120))
    for x, y in L.SPIGOT_SCREWS:
        add("spigot-screw", Location((x, s * y, SH)) * Rot(180, 0, 0), explode=ex(UP, 6, 60))
        add("spigot-washer", Location((x, s * y, SH - 3.0 - 2.5)) * Rot(180, 0, 0), explode=ex(DOWN, 6, 150))
        add("spigot-nut", Location((x, s * y, SH - 3.0 - 2.5 - 2.0)) * Rot(180, 0, 0), explode=ex(DOWN, 6, 170))
    # rebound buffer on its distance piece on the ledge; washer and nut under the ledge
    bx, by, bz = L.REBOUND_BUFFER
    add("distance-piece", Location((bx, s * by, bz)), explode=ex(UP, 5, 40))
    add("rebound-buffer", Location((bx, s * by, bz + 5.0)), explode=ex(UP, 5, 80))
    add("buffer-washer", Location((bx, s * by, bz - 3.0)) * Rot(180, 0, 0), explode=ex(DOWN, 5, 30))
    add("buffer-nut", Location((bx, s * by, bz - 3.0 - 2.0)) * Rot(180, 0, 0), explode=ex(DOWN, 5, 50))
INSTANCES = I
