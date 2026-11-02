"""Road wheels: four wire wheels with their tyres, tube valves and knock-on spinners (Haynes Ch 11 specifications,
Sec 30; spare wheel in the boot is P11).

Each wheel sits in the wheel frame of mgb.wheel_layout on its hub: front hubs (chassis.front-hubs) and rear hub
extensions (axle.hubs); the right-hand wheels are turned half round the vertical axis (rotation, so the spinners'
threads keep their hand). Explode stages (removing a wheel): spinner off (outboard), wheel and tyre pulled off the
splines, tyre off the rim.
  spinner        order 2     wheel with tyre   order 3     tyre off the rim   order 4
"""
from build123d import Location, Rot

from mgb import car_layout as CL, rear_axle_layout as A, wheel_layout as W

ID = "wheels.road-wheels"
NAME = "Road wheels, tyres and spinners"
PARENT = "wheels"
HAYNES = {"section": 30}

GROUPS = {}
CORNERS = (("fl", 1, CL.FRONT_AXLE_X, W.FRONT_SEAT_Y), ("fr", -1, CL.FRONT_AXLE_X, W.FRONT_SEAT_Y),
           ("rl", 1, CL.REAR_AXLE_X, W.REAR_SEAT_Y), ("rr", -1, CL.REAR_AXLE_X, W.REAR_SEAT_Y))
for k, s, x, y in CORNERS:
    GROUPS[f"wheel-{k}"] = {"axis": [0, s, 0], "order": 3, "distance_mm": 260}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "wheels.road-wheels." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


for k, s, x, y in CORNERS:
    WF = Location((x, s * y, CL.WHEEL_Z)) * (Rot(0, 0, 0) if s > 0 else Rot(0, 0, 180))
    out = [0, s, 0]
    add("spinner-lh" if s > 0 else "spinner-rh", WF, explode=ex(out, 2, 300))
    add("wheel", WF, groups=[f"wheel-{k}"])
    add("valve", WF, groups=[f"wheel-{k}"])
    add("tyre", WF, groups=[f"wheel-{k}"], explode=ex(out, 4, 220))
INSTANCES = I
