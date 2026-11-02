"""Windscreen wipers, Lucas DR3A (Haynes Ch 10 Sec 52-55, Fig 10.17).

Explode stages follow Sec 52 and 54: the blades off the arms, the arms pulled off the splines,
the wiring and the outer casing off the gearbox, the three bracket screws and the motor with
its bracket and rack withdrawn; then the wheelbox nuts and washers and the wheelboxes and
casings out from under the facia.
"""
from build123d import Location, Rot

from mgb import body_layout as BL

ID = "electrical.wipers"
NAME = "Windscreen wipers"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.17"}], "section": 54}
UP = [0, 0, 1]
GROUPS = {"motor": {"axis": [0, 1, -0.3], "order": 4, "distance_mm": 160}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.wipers." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


import importlib.util as _u   # noqa: E402
from pathlib import Path   # noqa: E402
_s = _u.spec_from_file_location("_wip", Path(__file__).resolve().parent.parent / "parts" / "electrical" / "wipers.py")
W = _u.module_from_spec(_s)
_s.loader.exec_module(W)

O = Location((0, 0, 0))
dy = BL.WIPER_SPINDLES[1][1] - BL.WIPER_SPINDLES[0][1]
park = Rot(0, 0, 180) if BL.WIPER_PARK_SIDE < 0 else Rot(0, 0, 0)
for k in (0, 1):
    shift = Location((0, dy * k, 0))
    wb = shift * W._wb_loc(0)
    arm_len = 200.0
    tip_z = W.WB_DROP + 28.0 + 1.0
    add("blade", wb * park * Location((0, arm_len + 6.0, tip_z - 12.0)), explode=ex(UP, 1, 120))
    add("arm", wb * park, explode=ex(UP, 2, 90))
    add("spindle", shift, explode=ex(UP, 6, 60))
    add("wheelbox", shift, explode=ex([0, 0, -1], 7, 70))
add("casing-motor", O, groups=["motor"])
add("casing-between", O, explode=ex([0, 0, -1], 7.5, 90))
add("casing-extension", O, explode=ex([0, -1, 0], 7.5, 90))
add("motor", O, groups=["motor"])
add("bracket", O, groups=["motor"], explode=ex(UP, 4.2, 40))
INSTANCES = I
