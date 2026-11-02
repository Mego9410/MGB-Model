"""Early one-piece welded exhaust system with its manifold fixings, gearbox clip and rear mounting (Haynes Ch 3
Sec 46; Ch 1 Sec 6 para 14, photos 6.14(a), (b); photo 46.2).

Explode stages follow Sec 46: the nuts come off at the manifold and the front support bolt out (order 1), the
rear mounting pipe bolt is loosened (order 2), and the system is withdrawn as one welded assembly (order 3), the
sealing rings coming away from the downpipes ("note the sealing rings", order 4); then the strap and clamp halves
come off the pipe and the brackets off the gearbox and the body (orders 5-7).
"""
from build123d import Location, Plane, Rot

from mgb import exhaust_layout as E
from parts.fuel import exhaust as X

ID = "fuel.exhaust"
NAME = "Exhaust system"
PARENT = "fuel"
HAYNES = {"figures": [], "section": 46}
UP, DOWN, LEFT, RIGHT, BACK = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0]
GROUPS = {"system": {"axis": DOWN, "order": 3, "distance_mm": 260}}

I, _n = [], {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc, **o):
    pid = "fuel.exhaust." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
SYS = ["system"]
for part in ("front-pipe", "centre-silencer", "inter-pipe", "rear-silencer", "tail-pipe"):
    add(part, O, groups=SYS)

# manifold joint: studs in the manifold, sealing rings on the spigots, washers and brass nuts under the flanges
fl_under = E.FLANGE_TOP_Z - E.FLANGE_T
for x, y in E.OUTLETS.values():
    add("sealing-ring", Location((x, y, E.FLANGE_TOP_Z)), groups=SYS, explode=ex(UP, 4, 45))
for x, y in E.STUDS:
    add("manifold-stud", Location((x, y, E.OUTLET_FACE_Z + 12.0 - 41.275)))
    add("flange-washer", Location((x, y, fl_under)) * Rot(180, 0, 0), explode=ex(DOWN, 1, 50))
    add("flange-nut", Location((x, y, fl_under - 2.0)) * Rot(180, 0, 0), explode=ex(DOWN, 1, 80))

# gearbox clip: bracket under the side cover bolts, strap round the pipe, the front support bolt along y
add("gearbox-bracket", O, explode=ex(LEFT, 7, 90))
add("gearbox-strap", O, groups=SYS, explode=ex(UP, 5, 70))
cx, by = E.CLIP_X, X.TONGUE_Y[0]
add("strap-bolt", Location((cx, by, X.STRAP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(RIGHT, 1, 70))
add("strap-washer", Location((cx, X.EAR_Y[1], X.STRAP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(LEFT, 1, 50))
add("strap-nut", Location((cx, X.EAR_Y[1] + 2.0, X.STRAP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(LEFT, 1, 80))

# rear mounting: bracket under the boot floor, rubber block, pinch clamp halves and their bolt
rx, ry = X.RX, X.RY
add("rear-bracket", O, explode=ex(UP, 7, 80))
for dx in (-14.0, 14.0):
    add("bracket-screw", Location((rx + dx, X.BR_TAB_Y + 26.0, E.REAR_BRACKET_Z[1] - X.BR_T)), explode=ex(DOWN, 6.5, 50))
add("rear-mounting", O, explode=ex(DOWN, 6, 60))
add("mount-bolt", Location((rx, X.BR_TAB_Y + X.BR_T, X.RUB_HOLES[1])) * Rot(90, 0, 0), explode=ex(LEFT, 5.5, 60))
add("small-washer", Location((rx, ry - X.RUB[0] / 2 - 0.5, X.RUB_HOLES[1])) * Rot(90, 0, 0), explode=ex(RIGHT, 5.5, 40))
add("small-nut", Location((rx, ry - X.RUB[0] / 2 - 2.1, X.RUB_HOLES[1])) * Rot(90, 0, 0), explode=ex(RIGHT, 5.5, 60))
add("rear-clamp", O, groups=SYS, explode=ex(RIGHT, 5, 50))
add("rear-clamp", Location((rx, ry, 0)) * Rot(0, 0, 180) * Location((-rx, -ry, 0)), groups=SYS, explode=ex(LEFT, 5, 50))
ear = ry - X.RUB[0] / 2 - 2.5
add("clamp-bolt", Location((rx, ear, X.CLAMP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(RIGHT, 2, 70))
add("small-washer", Location((rx, ry + X.RUB[0] / 2 + 2.5, X.CLAMP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(LEFT, 2, 40))
add("small-nut", Location((rx, ry + X.RUB[0] / 2 + 4.1, X.CLAMP_BOLT_Z)) * Rot(-90, 0, 0), explode=ex(LEFT, 2, 60))
INSTANCES = I
