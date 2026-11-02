"""Engine-bay electrical units: control box, fuse block, flasher, overdrive relay and vacuum
switch, horns (Haynes Ch 10 Sec 8, 33, 42, 50; Fig 10.2, photo 33.1, Fig 10.26).

Explode stages: units off their panels after their screws (batteries disconnected first,
Sec 32 para 1, Sec 50 para 1): the fuse block cover, the units, the horns.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import body_layout as BL, spec as S

ID = "electrical.control"
NAME = "Control box, fuses, relays and horns"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.2"}, {"figure": "10.26"}], "section": 33}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / "control.yaml")}
GROUPS = {}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def nom(part, key):
    return SP["electrical.control." + part].nom(key)


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.control." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


RIGHT = Rot(-90, 0, 0) * Rot(0, 0, 180)        # on the right valance: local z -> +y, local y -> up
LEFT = Rot(90, 0, 0)                           # on the left valance: local z -> -y, local y -> up
BULK = Rot(0, 90, 0) * Rot(0, 0, 90)           # on the bulkhead: local z -> +x, local y -> up
IN, OUTL = [0, 1, 0], [0, -1, 0]


def screws(frame, pts, ztop, axis, order):
    for x, y in pts:
        add("panel-screw", frame * Location((x, y, ztop)) * Rot(180, 0, 0), explode=ex(axis, order, 60))


cb = Location(BL.CONTROL_BOX) * RIGHT
w = nom("control-box", "width")
add("control-box", cb, explode=ex(IN, 2, 110))
screws(cb, [(-(w / 2 + 9.0), 0.0), (w / 2 + 9.0, 0.0)], 5.0, IN, 1)
fb = Location(BL.FUSE_BOX) * RIGHT
fw = nom("fuse-block", "width")
add("fuse-block", fb, explode=ex(IN, 2, 90))
screws(fb, [(-(fw / 2 + 8.0), 0.0), (fw / 2 + 8.0, 0.0)], 4.0, IN, 1)
fl = Location(BL.FLASHER) * RIGHT
add("flasher", fl, explode=ex(IN, 2, 70))
fr = nom("flasher", "diameter") / 2
screws(fl, [(-(fr + 10.0), 0.0), (fr + 10.0, 0.0)], 1.2, IN, 1)
rl = Location(BL.OD_RELAY) * LEFT
add("relay", rl, explode=ex(OUTL, 2, 80))
screws(rl, [(0.0, nom("relay", "height") / 2 + 8.0)], 1.5, OUTL, 1)
vs = Location(BL.OD_VACUUM_SWITCH) * BULK
add("vacuum-switch", vs, explode=ex([1, 0, 0], 2, 80))
vr = nom("vacuum-switch", "diameter") / 2
screws(vs, [(-(vr + 8.0), 0.0), (vr + 8.0, 0.0)], 1.5, [1, 0, 0], 1)
r, d = nom("horn", "diameter") / 2, nom("horn", "depth")
for k, (hx, hy, hz) in enumerate(BL.HORN_POS):
    h = Location((hx, hy, hz + r + 34.0)) * BULK
    add("horn", h, explode=ex([1, 0, 0], 4, 150))
    add("horn-bolt", Location((hx - 9.0, hy, hz + 4.0)) * Rot(180, 0, 0), explode=ex([0, 0, 1], 3, 60))
INSTANCES = I
