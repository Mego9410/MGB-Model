"""Headlamps, side and flasher lamps, rear lamps and number plate lamps (Haynes Ch 10 Sec 34-37,
Figs 10.7, 10.8; photos 35.1, 36.1, 37.1).

Explode stages follow Haynes: Sec 34 the chrome rim eased off its lugs, the dust excluder, the
light unit pressed in, turned and lifted out, the beam setting screws; Sec 35 the lens screws,
lens and rubber, then the body off its two nuts; Sec 36 the lens screw and lens, then the body;
Sec 37 the cover, lens and plinth off the overrider.
"""
from build123d import Location, Rot

from mgb import body_layout as BL

ID = "electrical.lamps"
NAME = "Exterior lamps"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.7"}, {"figure": "10.8"}], "section": 34}
FWD, BACK = [1, 0, 0], [-1, 0, 0]
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.lamps." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


FRONT = Rot(0, 90, 0)            # light along +x, local x down
REAR = Rot(0, -90, 0)            # light along -x, local x up
for s in (-1, 1):
    hl = Location((BL.HEADLAMP_RIM_X, s * BL.HEADLAMP_Y, BL.HEADLAMP_Z)) * FRONT
    add("headlamp-rim", hl, explode=ex(FWD, 1, 120))
    add("dust-excluder", hl, explode=ex(FWD, 2, 80))
    add("light-unit", hl, explode=ex(FWD, 3, 60))
    for a in (0.0, 90.0, -90.0):
        add("adjusting-screw", hl * Rot(0, 0, a), explode=ex(FWD, 4, 30))
    add("headlamp-bowl", hl)
    sl = Location((BL.SIDELAMP_X, s * BL.SIDELAMP_Y, BL.SIDELAMP_Z)) * FRONT
    add("side-rim", sl, explode=ex(FWD, 5, 70))
    add("side-lens-clear", sl, explode=ex(FWD, 5.5, 50))
    add("side-lens-amber", sl, explode=ex(FWD, 5.5, 50))
    add("side-body", sl, explode=ex(FWD, 6, 25))
    rl = Location((BL.REAR_LAMP_X, s * BL.REAR_LAMP_Y, BL.REAR_LAMP_Z)) * REAR
    add("rear-lens-red", rl, explode=ex(BACK, 7, 70))
    add("rear-lens-amber", rl, explode=ex(BACK, 7, 70))
    add("rear-body", rl, explode=ex(BACK, 8, 30))
    nx, ny, nz = BL.NUMBER_LAMP
    pl = Location((nx, s * ny, nz)) * (Rot(90, 0, 0) if s > 0 else Rot(-90, 0, 0))
    inward = [0, -s, 0]
    add("plate-lens", pl, explode=ex(inward, 9, 50))
    add("plate-lamp", pl, explode=ex(inward, 9.5, 30))
INSTANCES = I
