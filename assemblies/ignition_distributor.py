"""Distributor, its drive and housing, HT leads and plug caps (Haynes Ch 4 Fig 4.3;
Ch 1 Sec 16 and 63).

Explode stages follow Haynes: Sec 6 para 6 leads off the plugs; Sec 3 para 1 the clips
pulled away and the cap lifted off, then the rotor; Sec 6 para 7 the clamp plate bolts
out and the distributor lifted out of the housing; Sec 6 paras 8-13 the capacitor,
baseplate and contacts, the shaft and weights, the vacuum unit; then Ch 1 Sec 16 the
housing bolt, the housing and the driveshaft drawn out on a 5/16 UNF bolt.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import ignition_layout as G, spec as S

ID = "ignition.distributor"
NAME = "Distributor, drive and HT leads"
PARENT = "ignition"
HAYNES = {"figures": [{"figure": "4.3"}, {"figure": "1.26"}], "section": 6}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "ignition" / "distributor.yaml")}
AX = list(G.AXIS)
DOWN_AX = [-a for a in G.AXIS]
OUT = [0, -1, 0]
GROUPS = {"distributor": {"axis": AX, "order": 6, "distance_mm": 150},
          "housing": {"axis": AX, "order": 12, "distance_mm": 110}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def nom(part, key):
    return SP["ignition.distributor." + part].nom(key)


I, _n = [], {}


def add(part, loc, **o):
    pid = "ignition.distributor." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


D = Location(G.BOSS_TOP) * Rot(G.LEAN_DEG, 0, 0)        # distributor frame
DIST = ["distributor"]
HOUS = ["housing"]

# housing and drive
add("housing", D, groups=HOUS)
add("drive-shaft", D, explode=ex(AX, 13, 260))
add("housing-washer", D * Location((G.LUG_X, 0, G.FLANGE_T)), explode=ex(AX, 11, 50))
add("housing-bolt", D * Location((G.LUG_X, 0, G.FLANGE_T + nom("housing-washer", "thickness"))) * Rot(180, 0, 0),
    explode=ex(AX, 11, 80))
# distributor: clamp plate stays on the body so the timing is kept (Sec 6 para 7)
t = nom("clamp-plate", "thickness")
add("clamp-plate", D, groups=DIST)
add("pinch-bolt", D * Location((-8.0, -23.0, G.CLAMP_Z + 5)) * Rot(0, 90, 0), groups=DIST)
for k, sx in enumerate((-17.0, 17.0)):
    add("clamp-bolt", D * Location((sx, 12.0, G.CLAMP_Z + t)) * Rot(180, 0, 0), explode=ex(AX, 5, 60), label=k == 0)
add("body", D, groups=DIST)
add("vacuum-unit", D, groups=DIST, explode=ex([1, 0, 0], 9, 90))
add("shaft", D, groups=DIST, explode=ex(DOWN_AX, 10, 130))
add("baseplate", D, groups=DIST, explode=ex(AX, 8, 120))
add("capacitor", D, groups=DIST, explode=ex(AX, 7.5, 150))
add("rotor", D, explode=ex(AX, 4, 170))
for k, a in enumerate((0.0, 180.0)):
    add("cap-clip", D * Rot(0, 0, a), groups=DIST, explode=ex(AX, 2, 20), label=k == 0)
add("cap", D, explode=ex(AX, 3, 240))
add("brush", D, explode=ex(AX, 3, 240))
# HT leads (engine frame) and plug caps on the plug axis
for cyl in (1, 2, 3, 4):
    add(f"ht-lead-{cyl}", Location((0, 0, 0)), explode=ex(OUT, 1, 120))
for k, seat in enumerate(G.plug_seats()):
    add("plug-cap", Location(G.plug_point(seat, 44.0)) * Rot(57, 0, 0), explode=ex(G.PLUG_U, 1, 70), label=k == 0)
INSTANCES = I
