"""Battery carriers, the 12 V battery, clamp and cables (Haynes Ch 10 Sec 2, photo 2.1).

Explode stages follow Sec 2 para 1: the earth lead off first, then the positive cable, the
clamp nuts, J-bolts and clamp plate, and the battery lifted out; the carriers stay in the body.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import body_layout as BL, spec as S

ID = "electrical.battery"
NAME = "Battery, carriers and cables"
PARENT = "electrical"
HAYNES = {"figures": [], "section": 2}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / "battery.yaml")}
UP = [0, 0, 1]
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.battery." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
cx, cy = BL.BATTERY_BOX_X, -BL.BATTERY_BOX_Y
TURN = Location((cx, cy, 0)) * Rot(0, 0, 180) * Location((-cx, -cy, 0))
add("earth-cable", O, explode=ex(UP, 1, 160))
add("floor-bolt", Location((cx + BL.BATTERY_BOX_INNER[0] / 2 - 1.6 - 0.0, cy + BL.BATTERY_BOX_INNER[1] / 2 - 34.0,
                            BL.TONNEAU_FLOOR_Z - 26.0)) * Rot(0, 90, 0) * Location((0, 0, -0.01)), explode=ex([-1, 0, 0], 0.5, 50))
add("positive-cable", O, explode=ex(UP, 2, 200))
add("j-bolt", O, explode=ex(UP, 3, 260))
add("j-bolt", TURN, explode=ex(UP, 3, 260))
add("clamp", O, explode=ex(UP, 3.5, 300))
add("battery", O, explode=ex(UP, 4, 330))
add("carrier", O)
add("carrier", Location((0, 2 * BL.BATTERY_BOX_Y, 0)))
INSTANCES = I
