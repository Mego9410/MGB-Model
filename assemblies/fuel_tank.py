"""Early strap-mounted fuel tank, its straps and hangers, the filler and the gauge unit (Haynes Ch 3 Sec 12, 15, 16;
Fig 3.9).

Explode stages follow Sec 12 (early tourers): the filler cap off and the drain plug out (order 1), the gauge unit's
screws and the unit (Sec 16, orders 2-3), the filler hose clips loosened and the extension and seal pulled out
(orders 4-5), the strap nuts undone at the rear and the straps moved away (orders 6-7), and the tank lowered
(order 8).
"""
import math

from build123d import Location, Plane, Rot

from mgb import fuel_supply_layout as L
from parts.fuel import tank as T

ID = "fuel.tank"
NAME = "Fuel tank, filler and gauge unit"
PARENT = "fuel"
HAYNES = {"figures": [{"figure": "3.9"}], "section": 12}
UP, DOWN, LEFT, RIGHT, BACK, FWD = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]
GROUPS = {"tank": {"axis": DOWN, "order": 8, "distance_mm": 220}}

I, _n = [], {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc, **o):
    pid = "fuel.tank." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
add("tank", O, groups=["tank"])

# drain plug and washer under the tank
dx, dy = L.DRAIN
dz = T.TOP - T.depth(T.X0 - dx) - 4.0
add("drain-washer", Location((dx, dy, dz - 1.5)), groups=["tank"], explode=ex(DOWN, 1, 40))
add("drain-plug", Location((dx, dy, dz - 1.5)), groups=["tank"], explode=ex(DOWN, 1, 70))

# gauge unit on the right-hand end: ring face, gasket, unit, six screws
sx, sz = L.SENDER
ring_face = L.TANK_Y[0] - 0.5 - 3.0
gt = 1.5
add("gauge-gasket", Location(Plane(origin=(sx, ring_face, sz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))), groups=["tank"], explode=ex(RIGHT, 3, 50))
add("gauge-unit", Location(Plane(origin=(sx, ring_face - gt, sz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))), groups=["tank"],
    explode=ex(RIGHT, 3, 150))
for k in range(6):
    t = math.radians(30.0 + 60.0 * k)
    p = (sx + L.SENDER_PCD / 2 * math.cos(t), ring_face - gt - 1.6 + 9.5, sz + L.SENDER_PCD / 2 * math.sin(t))
    add("gauge-screw", Location(Plane(origin=p, z_dir=(0, -1, 0))), groups=["tank"], explode=ex(RIGHT, 2, 90))

# filler: seal in the boot floor, hose and clips, extension, cap
fx, fy = L.FILLER
CAP = Location(Plane(origin=(L.FILLER_CAP_X, L.FILLER_CAP_Y, L.FILLER_TUBE_TOP_Z), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)))
add("filler-cap", CAP, explode=ex(BACK, 1, 80))
add("filler-ring", CAP, explode=ex(BACK, 1.5, 40))
add("filler-tube", O, explode=ex(UP, 5, 120))
add("filler-hose", O, explode=ex(UP, 5, 70))
for z in (T.HOSE[0] + 8.0, T.HOSE[1] - 8.0):
    add("hose-clip", Location((fx, fy, z)), explode=ex(UP, 4, 40))
add("filler-seal", O, explode=ex(UP, 5, 30))

# straps, packing, hangers, pins, bolts
fpx, fpz = L.STRAP_PIN_FRONT
hpx, hpz = L.HANGER_PIN
foot = L.HANGER_FOOT_Z
tab = foot - 25.0
for k, ys in enumerate(L.STRAP_Y):
    S = [f"strap-{k}"]
    GROUPS[S[0]] = {"axis": DOWN, "order": 7, "distance_mm": 140}
    add("packing-strip", Location((0, ys, 0)), groups=S, explode=ex(DOWN, 7.5, 30))
    add("strap", Location((0, ys, 0)), groups=S)
    add("rear-hanger", Location((0, ys, 0)), explode=ex(DOWN, 6.5, 40))
    for px, pz, grp in ((fpx, fpz, S), (hpx, hpz, [])):
        add("clevis-pin", Location((px, ys - 20.0, pz)) * Rot(-90, 0, 0), groups=grp, explode=ex(RIGHT, 6.5, 60))
        add("pin-washer", Location((px, ys + 15.5, pz)) * Rot(-90, 0, 0), groups=grp, explode=ex(LEFT, 6.4, 40))
        add("split-pin", Location((px, ys + 18.0, pz)) * Rot(0, 90, 0), groups=grp, explode=ex(LEFT, 6.3, 60))
    add("strap-bolt", Location((L.STRAP_BOLT_X, ys, foot + 2.5)) * Rot(180, 0, 0), explode=ex(UP, 6, 80))
    add("strap-washer", Location((L.STRAP_BOLT_X, ys, tab - 0.8)) * Rot(180, 0, 0), explode=ex(DOWN, 6, 40))
    add("strap-nut", Location((L.STRAP_BOLT_X, ys, tab - 2.0)) * Rot(180, 0, 0), explode=ex(DOWN, 6, 70))
INSTANCES = I
