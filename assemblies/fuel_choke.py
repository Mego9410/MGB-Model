"""Choke (mixture) control and the jet linkage, early car (Haynes Ch 3 Fig 3.10 items 46-72, Fig 3.13, Sec 21,
Sec 45 paras 12-13; Ch 12 Sec 47 para 4; parts list plate 108-G2). Positions: mgb.throttle_layout.

Explode stages follow Sec 45 paras 12-13 (choke cable: free the trunnion screw, unscrew the control's nut behind the
facia, pull the cable out through the facia and the bulkhead) and Sec 21 paras 3 and 13 (the lever-and-pin pinch
bolts slackened, the jet levers): the trunnion and wire, the nut and washer behind the facia, the control, knob and
cable out rearward, the grommet, the abutment; then the cable lever, the clamps and the rod, the jet levers and links
off their pivot bolts.
"""
from build123d import Location

from parts.fuel import choke as P

ID = "fuel.choke"
NAME = "Choke control and jet linkage"
PARENT = "fuel"
HAYNES = {"figures": [{"figure": "3.10"}, {"figure": "3.13"}], "section": 21}

UP, DOWN, OUT, IN_, FWD, BACK = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0]
GROUPS = {
    "control": {"axis": BACK, "order": 3, "distance_mm": 140},
    "linkage": {"axis": DOWN, "order": 8, "distance_mm": 60},
    "front-jet": {"axis": FWD, "order": 10, "distance_mm": 40},
    "rear-jet": {"axis": BACK, "order": 10, "distance_mm": 40},
}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
I, _n = [], {}
PL = P.placements()


def add(part, loc=O, **o):
    pid = "fuel.choke." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def each(part, groups_by=None, **o):
    for k, loc in enumerate(PL[part]):
        oo = dict(o)
        if groups_by:
            oo["groups"] = [groups_by[k * len(groups_by) // len(PL[part])]]
        add(part, loc, **oo)


# 1: the wire out of the trunnion
add("trunnion", explode=ex(FWD, 1, 30))
add("cable-inner", explode=ex(UP, 1.5, 60))
# 2-4: the control off the facia, cable out through the facia and the bulkhead
add("facia-nut", explode=ex(FWD, 2, 40))
add("facia-washer", explode=ex(FWD, 2.2, 25))
add("control", groups=["control"])
add("knob", groups=["control"], explode=ex(BACK, 3.5, 40))
add("knob-letter", groups=["control"], explode=ex(BACK, 3.5, 40))
add("cable-outer", groups=["control"], explode=ex(UP, 2.6, 60))
add("grommet", explode=ex(BACK, 4, 40))
add("abutment-nut", explode=ex(DOWN, 4.5, 20))
add("abutment-washer", explode=ex(DOWN, 4.6, 12))
add("abutment", explode=ex(UP, 5, 40))
# 6-8: cable lever, clamps, rod
each("cable-lever-nut", explode=ex(UP, 6, 20))
each("cable-lever-washer", explode=ex(UP, 6.1, 12))
each("cable-lever-bolt", explode=ex(DOWN, 6.2, 25))
add("cable-lever", groups=["linkage"], explode=ex(UP, 6.5, 40))
each("rod-clamp-nut", explode=ex(UP, 7, 20))
each("rod-clamp-washer", explode=ex(UP, 7.1, 12))
each("rod-clamp-bolt", explode=ex(DOWN, 7.2, 25))
add("rod-clamp-front", groups=["linkage"], explode=ex(BACK, 7.5, 25))
add("rod-clamp-rear", groups=["linkage"], explode=ex(FWD, 7.5, 25))
add("rod", groups=["linkage"])
# 9-11: jet levers and links off their pivots
each("link-screw", groups_by=["front-jet", "rear-jet"], explode=ex(DOWN, 9, 20))
each("pivot-bolt", groups_by=["front-jet", "rear-jet"], explode=ex(DOWN, 9.2, 25))
each("pivot-washer", groups_by=["front-jet", "rear-jet"], explode=ex(DOWN, 9.4, 15))
each("jet-lever-spring", groups_by=["front-jet", "rear-jet"], explode=ex(DOWN, 9.5, 20))
each("pivot-tube", groups_by=["front-jet", "rear-jet"], explode=ex(DOWN, 9.6, 10))
add("jet-lever-front", groups=["front-jet"])
add("jet-lever-rear", groups=["rear-jet"])
INSTANCES = I
