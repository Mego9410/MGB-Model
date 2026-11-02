"""Fuel pipes and flexible hoses from the tank to the pump and on to the engine bay feed union (Haynes Ch 3 Sec 5,
Sec 12 para 3; MGOC Spares fuel lines).

Explode stages: the pump's inlet and outlet pipes come off first, "undoing the nuts" (Sec 5 para 4, order 1), the
fuel pipe union at the tank (Sec 12 para 3, order 2), then the clips and the pipes down off the body (orders 3-4).
"""
import math

from build123d import Location, Plane, Vector

from mgb import fuel_supply_layout as L
from parts.fuel import supply as P

ID = "fuel.supply"
NAME = "Fuel pipes, tank to carburettors"
PARENT = "fuel"
HAYNES = {"figures": [], "section": 5}
UP, DOWN = [0, 0, 1], [0, 0, -1]
GROUPS = {}

I, _n = [], {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc, **o):
    pid = "fuel.supply." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def unit(a, b):
    v = Vector(b) - Vector(a)
    return tuple(v.normalized())


O = Location((0, 0, 0))
add("tank-hose", O, explode=ex(DOWN, 2, 90))
add("tank-pipe", O, explode=ex(DOWN, 4, 140))
add("pump-hose", O, explode=ex(UP, 1, 90))
add("feed-pipe", O, explode=ex(DOWN, 4, 180))

# union nuts: tank stub, hose to tank pipe, pump inlet, pump outlet, hose to main pipe
h = L.TANK_HOSE
add("union-nut", Location(Plane(origin=Vector(h[0]) - Vector(13.0, 0, 0), z_dir=(1, 0, 0))), explode=ex(DOWN, 2, 110))
add("union-nut", Location(Plane(origin=h[-1], z_dir=unit(h[-2], h[-1]))), explode=ex(DOWN, 2, 110))
it = L.INLET_TIP
add("union-nut", Location(Plane(origin=(it[0] - 12.0, it[1], it[2]), z_dir=(1, 0, 0))), explode=ex([-1, 0, 0], 1, 60))
ot = L.OUTLET_TIP
add("union-nut", Location(Plane(origin=(ot[0], ot[1], ot[2] + 3.0), z_dir=(0, 0, -1))), explode=ex(UP, 1, 110))
ph = L.PUMP_HOSE
add("union-nut", Location(Plane(origin=ph[-1], z_dir=unit(ph[-2], ph[-1]))), explode=ex(UP, 1, 110))
end = L.MAIN_ROUTE[-1]
add("pipe-union", Location(Plane(origin=(end[0] - 4.0, end[1], end[2]), z_dir=(1, 0, 0))), explode=ex(DOWN, 4, 180))


def seg_dir(route, p):
    best = None
    for a, b in zip(route, route[1:]):
        ab = Vector(b) - Vector(a)
        t = max(0.0, min(1.0, (Vector(p) - Vector(a)).dot(ab) / ab.dot(ab)))
        d = (Vector(a) + ab * t - Vector(p)).length
        if best is None or d < best[0]:
            best = (d, tuple(ab.normalized()))
    return best[1]


STANDOFF = {"main": None, "tank": None}
for name, route in (("main", L.MAIN_ROUTE), ("tank", L.TP_ROUTE)):
    for pt, n in L.CLIPS[name]:
        d = seg_dir(route, pt)
        nz = Vector(n)
        # distance from the pipe centre to the body face the clip screws to
        if name == "main":
            so = 10.0 if n == (0, 0, 1) else L.BULK_X - L.CL.BULKHEAD_X
        else:
            so = 9.0 if abs(pt[2] - (L.U.ARCH_Z - 9.0)) < 1 else 12.0
        loc = Location(Plane(origin=pt, x_dir=d, z_dir=n))
        add("p-clip", loc, build={"standoff": so}, explode=ex(DOWN, 3, 60))
        yv = nz.cross(Vector(d))
        foot = Vector(pt) + yv * (-8.0) + nz * (so - 0.9)
        add("clip-screw", Location(Plane(origin=tuple(foot), z_dir=tuple(-nz))), explode=ex(DOWN, 3, 90))
INSTANCES = I
