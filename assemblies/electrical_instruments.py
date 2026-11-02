"""Instruments, warning lamps and switches, speedometer cable and the gauge pipe and capillary
(Haynes Ch 10 Sec 40, 45-47, Fig 10.9; Ch 1 Sec 6; Ch 2 Sec 15).

Explode stages: from behind the facia (Sec 46: the instruments' knurled nuts and brackets, the
cable and pipes off, the instruments out to the front); the switches' lockrings and the
switches out; the lamp holders pulled out (Sec 40 para 2).
"""
from build123d import Location, Rot

from mgb import body_layout as BL

ID = "electrical.instruments"
NAME = "Instruments and switches"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.9"}, {"figure": "10.14"}], "section": 46}
REARWARD = [-1, 0, 0]
FWD = [1, 0, 0]
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.instruments." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


FACIA = Rot(0, -90, 0)          # local z toward the driver, local x up


def at(y, z):
    return Location((BL.FACIA_X, y, z)) * FACIA


O = Location((0, 0, 0))
add("speedo-cable", O, explode=ex(FWD, 1, 120))
add("oil-pipe", O, explode=ex(FWD, 1, 120))
add("capillary", O, explode=ex(FWD, 1, 140))
add("oil-union", O, explode=ex([0, -1, 0], 1.5, 40))
add("transmitter", O, explode=ex([0, -1, 0], 1.5, 50))
SIZE = {"speedometer": "large", "tachometer": "large", "dual-gauge": "small", "fuel-gauge": "small"}
for k, (y, z) in BL.INSTRUMENTS.items():
    f = at(y, z)
    add(f"{k}-case", f, explode=ex(REARWARD, 3, 140))
    add(f"{k}-dial", f, explode=ex(REARWARD, 3, 140))
    add(f"{k}-needle", f, explode=ex(REARWARD, 3, 140))
    add(f"glass-{SIZE[k]}", f, explode=ex(REARWARD, 2, 190))
    add(f"bezel-{SIZE[k]}", f, explode=ex(REARWARD, 2, 230))
for k, (y, z) in BL.WARNING_LAMPS.items():
    f = at(y, z)
    add("warning-lamp", f, explode=ex(FWD, 4, 60))
    add({"ignition": "lens-red", "main-beam": "lens-blue", "indicator": "lens-green"}[k], f, explode=ex(FWD, 4, 60))
for k, (y, z) in BL.SWITCHES.items():
    f = at(y, z)
    if k in ("panel-lamp", "map-lamp"):
        add("pull-knob", f, explode=ex(REARWARD, 5, 60))
        add("pull-switch", f, explode=ex(FWD, 6, 70))
    elif k == "ignition":
        add("ignition-switch", f, explode=ex(FWD, 6, 80))
    else:
        add("toggle-switch", f, explode=ex(FWD, 6, 70))
INSTANCES = I
