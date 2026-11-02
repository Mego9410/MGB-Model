"""Clutch cover assembly and driven plate on the flywheel (Haynes Ch 5 Sec 4, Figs 5.1, 5.2).

Every part is built in the clutch frame (mgb.clutch_layout: local z rearward from the
flywheel friction face, x up, y left) and placed with one transform onto the crank axis.

Explode stages follow Haynes Sec 4:
  para 2   the six cover screws and spring washers out                       order 1
  para 3   the cover assembly lifted off its dowels, then the plate falls out   orders 2-3
  para 5   (dismantling) circlip and release plate off; three strap bolts out
           a turn at a time with their tab washers and clips; pressure plate out  orders 4-7
  para 6   (inspection) the driven plate opened up to show its parts            order 8
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import clutch_layout as K, spec as S
from parts.clutch.unit import LUG_ANGLES, LUG_R, LUG_Z1, CLIP_T, STRAP_T, TAB_T, RP_EAR_ANGLES, SPRING_ANGLES, T, lp

ID = "clutch.unit"
NAME = "Clutch cover assembly and driven plate"
PARENT = "clutch"
HAYNES = {"figures": [{"figure": "5.1"}, {"figure": "5.2"}], "section": 4}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "clutch" / "unit.yaml")}
BACK, FWD = [-1, 0, 0], [1, 0, 0]
GROUPS = {"cover": {"axis": BACK, "order": 2, "distance_mm": 170},
          "plate": {"axis": BACK, "order": 3, "distance_mm": 80}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def radial(deg):
    """Car-frame unit vector pointing out from the axis at a clutch-frame angle."""
    x, y, _ = lp(1.0, deg)
    return [0.0, y, x]


I, _n = [], {}


def add(part, loc, **o):
    pid = "clutch.unit." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def nom(part, key):
    return SP["clutch.unit." + part].nom(key)


CF = Location((K.FACE_X, 0.0, K.CZ)) * Rot(0, -90, 0)     # clutch frame: local z rearward, x up, y left


def turn(deg):
    """Turn a part built at clutch-frame angle 0 to angle deg (angles run from +y toward +x)."""
    return Rot(0, 0, -deg)


COVER = ["cover"]
PLATE = ["plate"]

# cover screws and spring washers on the three lobes
wt = nom("spring-washer", "thickness")
first = True
for d in K.DOWEL_ANGLES:
    for s in (-30.0, 30.0):
        x, y, _ = lp(K.BOLT_R, d + s)
        add("spring-washer", CF * Location((x, y, T)), explode=ex(BACK, 1, 40), label=first)
        add("cover-screw", CF * Location((x, y, T + wt)) * Rot(180, 0, 0), explode=ex(BACK, 1, 90), label=first)
        first = False

# the cover assembly (item 1)
add("cover", CF, groups=COVER)
add("diaphragm-spring", CF, groups=COVER)
add("release-plate", CF, groups=COVER, explode=ex(BACK, 5, 70))
add("release-plate-circlip", CF, groups=COVER, explode=ex(FWD, 4, 45))
for k, a in enumerate(RP_EAR_ANGLES):
    add("release-plate-strap", CF * turn(a - RP_EAR_ANGLES[0]), groups=COVER, label=k == 0)
add("pressure-plate", CF, groups=COVER, explode=ex(FWD, 7, 110))
for k, g in enumerate(LUG_ANGLES):
    add("pressure-plate-clip", CF * turn(g), groups=COVER, explode=ex(radial(g), 6, 35), label=k == 0)
    x, y, _ = lp(LUG_R, g)
    z = LUG_Z1 + CLIP_T + STRAP_T
    add("tab-washer", CF * Location((x, y, z)) * Rot(0, 0, 90 - g), groups=COVER, explode=ex(BACK, 6, 45), label=k == 0)
    add("strap-bolt", CF * Location((x, y, z + TAB_T)) * Rot(180, 0, 0), groups=COVER, explode=ex(BACK, 6, 80),
        label=k == 0)

# driven plate (item 7), short end of the hub toward the flywheel
add("hub", CF, groups=PLATE)
add("carrier", CF, groups=PLATE)
for k, a in enumerate(SPRING_ANGLES):
    add("damper-spring", CF * turn(a), groups=PLATE, explode=ex(radial(a), 8, 30), label=k == 0)
add("facing", CF, groups=PLATE, explode=ex(FWD, 8, 25))
add("facing", CF * Location((0, 0, K.PLATE_T)) * Rot(180, 0, 0), groups=PLATE, explode=ex(BACK, 8, 25), label=False)
INSTANCES = I
