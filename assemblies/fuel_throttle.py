"""Accelerator pedal, cable and throttle interconnection, early RHD car (Haynes Ch 3 Fig 3.10 items 38-45, Fig 3.13,
photo 17.1(b), Sec 21 and Sec 45; parts list plates 108-G2 and 108-G4). Positions: mgb.throttle_layout.

Explode stages follow the removal order of Sec 45 (paras 3-6, the later cars' cable, the nearest Haynes gives) and
Sec 21: the cable off the shaft lever (split pin, washers, swivel pin), the return springs unhooked, the outer out
of the abutment bracket and the P-clip on the pedal box cover, the split pin out at the pedal and the cable drawn
into the engine bay; the pedal off its pivot bolt, the pad off the foot plate; the guide off the bulkhead; then the
linkage: the shaft lever and the couplings slackened and the interconnecting shaft out, the throttle levers off the
spindles with their adjusting screws; the abutment bracket and the pedal stop last.
"""
from build123d import Location

from parts.fuel import throttle as P

ID = "fuel.throttle"
NAME = "Accelerator pedal, cable and throttle linkage"
PARENT = "fuel"
HAYNES = {"figures": [{"figure": "3.10"}, {"figure": "3.13"}], "section": 45}

UP, DOWN, OUT, IN_, FWD, BACK = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0]
GROUPS = {
    "cable": {"axis": UP, "order": 4, "distance_mm": 120},
    "pedal": {"axis": BACK, "order": 6, "distance_mm": 110},
    "guide": {"axis": FWD, "order": 8, "distance_mm": 70},
    "front-lever": {"axis": FWD, "order": 11, "distance_mm": 50},
    "rear-lever": {"axis": BACK, "order": 11, "distance_mm": 50},
    "stop": {"axis": [-0.9, 0, 0.45], "order": 14, "distance_mm": 70},
}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


O = Location((0, 0, 0))
I, _n = [], {}
PL = P.placements()


def add(part, loc=O, **o):
    pid = "fuel.throttle." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def each(part, **o):
    for k, loc in enumerate(PL[part]):
        oo = dict(o)
        g = oo.pop("groups_by", None)
        if g:
            oo["groups"] = [g[k]]
        add(part, loc, **oo)


# 1: the cable off the shaft lever
add("swivel-split-pin", explode=ex(IN_, 1, 40))
each("swivel-washer", explode=ex(BACK, 1.5, 30))
add("anti-rattle-washer", explode=ex(BACK, 1.6, 40))
add("swivel-pin", explode=ex(FWD, 2, 50))
# 2: return springs
each("return-spring", explode=ex(DOWN, 3, 60))
# 3-5: the cable out (outer, inner, P-clip), the split pin at the pedal
add("cover-clip-nut", explode=ex(DOWN, 3.5, 30))
add("cover-clip-screw", groups=["cable"], explode=ex(UP, 3.6, 20))
add("cover-clip", groups=["cable"])
add("cable-outer", groups=["cable"])
add("pedal-split-pin", explode=ex(OUT, 3.8, 30))
add("cable-inner", groups=["cable"], explode=ex(FWD, 4.5, 60))
# 6: the pedal off its pivot
add("pivot-nut", explode=ex(IN_, 5, 40))
add("pivot-washer", explode=ex(IN_, 5.2, 30))
add("pivot-bolt", explode=ex(OUT, 5.4, 60))
add("pedal", groups=["pedal"])
add("distance-tube", groups=["pedal"], explode=ex(IN_, 6.5, 30))
add("pad", groups=["pedal"], explode=ex([-0.82, 0, 0.57], 7, 40))
add("pedal-bracket")
# 8: the guide off the bulkhead
each("guide-nut", explode=ex(BACK, 7.5, 30))
each("guide-screw", groups=["guide"], explode=ex(FWD, 7.8, 30))
add("cable-guide", groups=["guide"])
add("guide-gasket", groups=["guide"], explode=ex(BACK, 8.5, 20))
# 9-12: the linkage (Sec 21 para 2: slacken the clamps)
add("shaft-lever-nut", explode=ex(IN_, 9, 30))
add("shaft-lever-bolt", explode=ex(OUT, 9, 30))
add("shaft-lever", explode=ex(UP, 9.5, 60))
each("coupling-nut", explode=ex(IN_, 9.6, 30))
each("coupling-bolt", explode=ex(OUT, 9.6, 30))
each("coupling", explode=ex(UP, 10, 40))
add("shaft", explode=ex(OUT, 10.5, 70))
add("throttle-lever-front", groups=["front-lever"])
add("throttle-lever-rear", groups=["rear-lever"])
each("lever-nut", groups_by=["front-lever", "rear-lever"], explode=ex(UP, 10.8, 25))
each("lever-tab-washer", groups_by=["front-lever", "rear-lever"], explode=ex(UP, 10.9, 15))
each("adjusting-screw", groups_by=["front-lever", "rear-lever"], explode=ex(UP, 12, 40))
each("adjusting-spring", groups_by=["front-lever", "rear-lever"], explode=ex(UP, 12, 25))
# 13-14: the abutment bracket, the pedal stop
each("bracket-nut", explode=ex(IN_, 13, 30))
each("bracket-screw", explode=ex(OUT, 13.2, 30))
add("abutment-bracket", explode=ex(OUT, 13.5, 60))
add("stop-locknut", groups=["stop"], explode=ex([-0.9, 0, 0.45], 14.5, 20))
add("stop-screw", groups=["stop"], explode=ex([-0.9, 0, 0.45], 14.6, 40))
each("stop-fixing-screw", groups=["stop"], explode=ex([-0.9, 0, 0.45], 13.8, 30))
each("stop-spring-washer", groups=["stop"], explode=ex([-0.9, 0, 0.45], 13.9, 20))
add("pedal-stop", groups=["stop"])
INSTANCES = I
