"""Ignition coil, Lucas HA12, its bracket and leads (Haynes Ch 10 Sec 25 para 2; Fig 10.14).

Explode stages: leads off the coil (king lead out of the tower, the low tension lead off CB),
then the bracket bolt out and the coil and bracket away together, the pinch screw and clamp.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import electrical_layout as E, spec as S

ID = "electrical.coil"
NAME = "Ignition coil and leads"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.14"}], "section": 25}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / "coil.yaml")}
OUT = [0, -1, 0]
UP = [0, 0, 1]
GROUPS = {"coil": {"axis": OUT, "order": 3, "distance_mm": 120}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.coil." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
add("king-lead", O, explode=ex(UP, 1, 90))
add("lt-lead", O, explode=ex(UP, 1.5, 60))
bx, bz = E.COIL_BOSS
t = SP["electrical.coil.clamp"].nom("thickness")
add("bracket-bolt", Location((bx, E.BOSS_FACE_Y - t, bz)) * Rot(-90, 0, 0), explode=ex(OUT, 2, 60))
add("coil", O, groups=["coil"], explode=ex(UP, 4, 110))
add("clamp", O, groups=["coil"])
r = SP["electrical.coil.clamp"].nom("band_diameter") / 2
w = SP["electrical.coil.clamp"].nom("band_width")
zb = E.COIL_BOSS[1] - 6.0 - w / 2
add("pinch-screw", Location((E.COIL_AXIS[0] - 6.2, E.COIL_AXIS[1] - r - 7.0, zb + w / 2)) * Rot(0, 90, 0), groups=["coil"],
    explode=ex([1, 0, 0], 4.5, 50))
INSTANCES = I
