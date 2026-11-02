"""Starter motor (Lucas M418G inertia), remote solenoid, starter cable and earth strap
(Haynes Ch 10 Sec 23-26, Fig 10.4).

Explode stages follow Haynes: Sec 25 para 1 the starter cable off the terminal; para 3 the two
bolts out and the motor lifted out of engagement and upward; Sec 26 paras 1-6: the cover band,
the drive (circlip, anchor plate, main spring, sleeves, pinion), the terminal nuts, the
through-bolts, the commutator end bracket, then the drive end bracket and the armature.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import electrical_layout as E, spec as S

ID = "electrical.starting"
NAME = "Starter motor, solenoid and cables"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.4"}, {"figure": "10.26"}], "section": 25}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / "starting.yaml")}
UP = [0, -0.35, 0.94]
FWD, BACK = [1, 0, 0], [-1, 0, 0]
GROUPS = {"motor": {"axis": UP, "order": 3, "distance_mm": 260}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.starting." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


sy, sz = E.STARTER_YZ
ST = Location((E.REAR_PLATE_FRONT_X, sy, sz)) * Rot(0, 90, 0)
M = ["motor"]
O = Location((0, 0, 0))

add("solenoid", O, explode=ex([0, -1, 0], 0.5, 120))
x_fl = E.REAR_PLATE_FRONT_X + E.FLANGE_T
sw = SP["electrical.starting.spring-washer"].nom("thickness")
for k, (by, bz) in enumerate(E.starter_bolt_points()):
    if k == 0:   # earth strap eye (1.5 mm) under the top bolt's spring washer
        add("spring-washer", Location((x_fl + 1.6, by, bz)) * Rot(0, 90, 0), explode=ex(FWD, 2, 70))
        add("mounting-bolt", Location((x_fl + 1.6 + sw, by, bz)) * Rot(0, -90, 0), explode=ex(FWD, 2, 110))
    else:
        add("mounting-bolt", Location((x_fl, by, bz)) * Rot(0, -90, 0), explode=ex(FWD, 2, 110), label=False)
add("cover-band", ST, groups=M, explode=ex(FWD, 4, 160))
add("drive-sleeve", ST, groups=M, explode=ex(BACK, 5.2, 150))
add("main-spring", ST, groups=M, explode=ex(BACK, 5, 200))
add("pinion", ST, groups=M, explode=ex(BACK, 5.4, 110))
add("terminal-post", ST, groups=M, explode=ex([0, -0.5, 0.87], 6, 60))
add("through-bolt", ST * Rot(0, 0, 45.0), groups=M, explode=ex(FWD, 6.5, 170))
add("through-bolt", ST * Rot(0, 0, 225.0), groups=M, explode=ex(FWD, 6.5, 170))
add("shaft-cap", ST, groups=M, explode=ex(FWD, 7, 130))
add("commutator-end-bracket", ST, groups=M, explode=ex(FWD, 7, 100))
add("yoke", ST, groups=M, explode=ex(FWD, 8, 50))
add("armature", ST, groups=M, explode=ex(BACK, 8.5, 60))
add("drive-end-bracket", ST, groups=M, explode=ex(BACK, 8.2, 30))
INSTANCES = I
