"""SU type HP electric fuel pump on its bracket on the heelboard (Haynes Ch 3 Secs 5-7, Fig 3.2).

Explode stages follow Sec 5 (the pipes come off with fuel_supply): the two bracket bolts and spring washers out
and the pump and bracket away (order 1); then the pump off its rubber mountings (order 2) and dismantled as Sec 6:
the outlet connection, inlet union and filter plug (order 3), the six body screws (order 4), the body, gaskets and
sandwich plate apart from the coil housing (order 5), the sealing band and end cover (order 6).
"""
import math

from build123d import Location, Plane, Rot

from mgb import fuel_supply_layout as L, underbody_layout as U
from parts.fuel import pump as P

ID = "fuel.pump"
NAME = "Fuel pump (SU HP)"
PARENT = "fuel"
HAYNES = {"figures": [{"figure": "3.2"}], "section": 5}
UP, DOWN, BACK, FWD = [0, 0, 1], [0, 0, -1], [-1, 0, 0], [1, 0, 0]
OUT = [0, -1, 0]
GROUPS = {"pump": {"axis": BACK, "order": 1, "distance_mm": 120}, "pumpset": {"axis": UP, "order": 2, "distance_mm": 70}}

I, _n = [], {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def add(part, loc, **o):
    pid = "fuel.pump." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


PF = Location(Plane(origin=(L.PUMP_X, L.PUMP_Y0, L.PUMP_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0)))
G = ["pump", "pumpset"]
IN = [0, 1, 0]
add("body", PF, groups=G, explode=ex(IN, 5, 70))
add("gasket", PF * Location((0, 0, P.B1)), groups=G, explode=ex(IN, 5, 45))
add("sandwich-plate", PF * Location((0, 0, P.S0)), groups=G, explode=ex(IN, 5, 25))
add("gasket", PF * Location((0, 0, P.S1)), groups=G, explode=ex(IN, 5, 12))
add("coil-housing", PF, groups=G)
add("sealing-band", PF, groups=G, explode=ex(OUT, 6, 40))
add("end-cover", PF, groups=G, explode=ex(OUT, 6, 90))
add("outlet-connection", PF, groups=G, explode=ex(UP, 3, 60))
add("inlet-union", PF, groups=G, explode=ex(BACK, 3, 60))
add("filter-plug", PF, groups=G, explode=ex(DOWN, 3, 60))
for a in P.SCREW_ANGLES:
    t = math.radians(a)
    add("body-screw", PF * Location((P.SCREW_PCD / 2 * math.cos(t), P.SCREW_PCD / 2 * math.sin(t), P.C0 + 6.0 - 22.0)),
        groups=G, explode=ex(OUT, 4, 60))
for y in P.LUG_CAR_Y:
    add("rubber-mounting", Location((L.PUMP_X, y, P.BR_TOP_Z)), groups=["pump"], explode=ex(DOWN, 2, 20))
    add("mounting-screw", Location((L.PUMP_X, y, P.BR_TOP_Z - P.BR_T)), groups=["pump"], explode=ex(DOWN, 2, 50))
add("bracket", Location((0, 0, 0)), groups=["pump"])
for y in P.BRACKET_BOLT_Y:
    add("spring-washer", Location((U.HEELBOARD_X - P.BR_T - 2.0, y, P.BRACKET_BOLT_Z)) * Rot(0, 90, 0), explode=ex(BACK, 1, 40))
    add("bracket-bolt", Location((U.HEELBOARD_X - P.BR_T - 2.0, y, P.BRACKET_BOLT_Z)) * Rot(0, 90, 0), explode=ex(BACK, 1, 70))
INSTANCES = I
