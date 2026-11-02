"""Front hubs, wire wheels (Haynes Ch 11 Fig 11.2 items 67-75, 77; Sec 13).

Drawn in the left-hand front hub frame (mgb.front_suspension_layout); `place(side)` turns the round parts half
round for the right-hand hub (threads keep their hand). Explode stages (Sec 13 para 2, each side outward):
  grease retainer out; split pin, nut, retaining washer                            orders 10-12
  hub and disc pulled off (the disc is P8's)                                       order 13
  outer bearing, shims, spacer; inner bearing, oil seal and collar out of the hub  orders 14-15
"""
from build123d import Location, Rot

from mgb import front_suspension_layout as L

ID = "chassis.front-hubs"
NAME = "Front hubs (wire wheels)"
PARENT = "chassis"
HAYNES = {"figures": [{"figure": "11.2"}], "section": 13}

GROUPS = {}
for s, k in ((1, "l"), (-1, "r")):
    GROUPS[f"hub-{k}"] = {"axis": [0, s, 0], "order": 13, "distance_mm": 220}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "chassis.front-hubs." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


for s, k in ((1, "l"), (-1, "r")):
    out = [0, s, 0]
    P = L.place(s)
    g = [f"hub-{k}"]
    add("grease-retainer", P, groups=g, explode=ex(out, 10, 120))
    add("split-pin", P, explode=ex(out, 11, 260))
    add("nut", P, explode=ex(out, 11, 200))
    add("retaining-washer", P, explode=ex(out, 12, 160))
    add("hub-lh" if s > 0 else "hub-rh", P, groups=g)
    add("outer-bearing", P, groups=g, explode=ex(out, 14, 90))
    add("shim", P, explode=ex(out, 14, 120))
    add("spacer", P, explode=ex(out, 14, 60))
    add("inner-bearing", P, groups=g, explode=ex([0, -s, 0], 15, 40))
    add("oil-seal", P, groups=g, explode=ex([0, -s, 0], 15, 60))
    add("collar", P, explode=ex([0, -s, 0], 15, 30))
INSTANCES = I
