"""Gearbox casing with the bellhousing, front cover, side cover, plugs, studs, the overdrive
adaptor and the bellhousing fixings (Haynes Ch 6 Fig 6.3; Sec 4 and 11).

Everything is built in the gearbox frame (mgb.gearbox_layout GF) and placed with it.

Explode stages follow Haynes, numbered across the whole gearbox (gearbox_shafts,
gearbox_selectors and gearbox_remote use the same sequence):
  Sec 11 para 3  overdrive off the adaptor: its gasket                        order 1
  (Sec 4 paras 2-4: dipstick and remote control housing, gearbox_remote)      orders 2-4
  Sec 4 para 6   adaptor nuts and washers off, the adaptor pulled back         orders 7-8
  Sec 4 para 7   side cover bolts and washers out, cover and gasket off        orders 10-11
  Sec 4 para 9   detent block dowels with the block                           order 16
  Sec 4 para 11  front cover nuts and washers off, the cover and gasket        orders 24-25
  Sec 3 / Ch 1   first of all the gearbox comes off the engine: bellhousing
                 nuts, washers and bolts out (the casing stays put as the base)   order 0.5
"""
import math

from build123d import Location, Rot

from mgb import gearbox_layout as G
from parts.gearbox import casing as C

ID = "gearbox.casing"
NAME = "Casing, bellhousing, covers and overdrive adaptor"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.3"}, {"figure": "6.4"}], "section": 4}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"adaptor": {"axis": BACK, "order": 8, "distance_mm": 230},
          "side-cover": {"axis": LEFT, "order": 11, "distance_mm": 120},
          "front-cover": {"axis": FWD, "order": 25, "distance_mm": 150}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.casing." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF


def at(x, y, z):
    return GF * Location((x, y, z))


TG = 0.3048                       # front cover gasket
SGT, SCT = 0.8, 2.0               # side cover gasket and cover thickness

add("od-gasket", at(0, 0, C.AD_D1), groups=["adaptor"], explode=ex(BACK, 1, 120))
add("casing", GF)

# adaptor on the rear face, its studs and nuts; the overdrive studs in its rear bosses
add("adaptor-gasket", at(0, 0, G.CASE_LEN), groups=["adaptor"], explode=ex(FWD, 9, 40))
add("adaptor", GF, groups=["adaptor"])
for u, l in C.REAR_STUDS:
    add("rear-stud", at(u, l, G.CASE_LEN - 14.0))
    add("adaptor-washer", at(u, l, C.AD_D0 + 12.0), explode=ex(BACK, 7, 60))
    add("adaptor-nut", at(u, l, C.AD_D0 + 14.0), explode=ex(BACK, 7, 90))
for k, a in enumerate(G.OD_STUD_ANGLES):
    x, y = G.OD_STUD_R * math.cos(math.radians(a)), G.OD_STUD_R * math.sin(math.radians(a))
    add("od-stud-long" if k == G.OD_STUD_LONG else "od-stud", at(x, y, C.AD_D1 - 20.0), groups=["adaptor"])

# side cover: one bolt has the fibre and plain washers (Sec 4 para 7)
add("side-cover-gasket", at(0, 0, 0), groups=["side-cover"], explode=ex(LEFT, 12, 40))
add("side-cover", at(0, SGT, 0), groups=["side-cover"])
face = C.SIDE_FACE + SGT + SCT
for k, (u, d) in enumerate(C.SC_BOLTS):
    if k == C.SC_FIBRE:
        add("fibre-washer", at(u, face, d) * Rot(-90, 0, 0), explode=ex(LEFT, 10, 50))
        add("plain-washer", at(u, face + 1.6, d) * Rot(-90, 0, 0), explode=ex(LEFT, 10, 65))
        add("side-cover-bolt", at(u, face + 3.25, d) * Rot(90, 0, 0), explode=ex(LEFT, 10, 95))
    else:
        add("side-cover-washer", at(u, face, d) * Rot(-90, 0, 0), explode=ex(LEFT, 10, 50))
        add("side-cover-bolt", at(u, face + 1.6, d) * Rot(90, 0, 0), explode=ex(LEFT, 10, 80))
u, d = C.SC_SCREW
add("side-cover-screw-washer", at(u, face + 4.0, d) * Rot(-90, 0, 0), explode=ex(LEFT, 10, 50))
add("side-cover-screw", at(u, face + 6.0, d) * Rot(90, 0, 0), explode=ex(LEFT, 10, 80))

# plugs and the detent block dowels
add("welch-plug", at(G.CASE_TOP + 1.0, C.DIP_HOLE[1], C.DIP_HOLE[2]) * Rot(0, 90, 0), explode=ex(UP, 2, 40))
add("drain-plug", at(C.DRAIN[0] - 3.0, C.DRAIN[1], C.DRAIN[2]) * Rot(0, 90, 0), explode=ex(DOWN, 2, 50))
for u, l in C.BLOCK_DOWELS:
    add("block-dowel", at(u, l, G.CASE_LEN - 7.0), explode=ex(BACK, 16, 70))

# front cover on its studs (Sec 4 para 11)
add("front-cover-gasket", at(0, 0, -TG), groups=["front-cover"], explode=ex(FWD, 26, 20))
add("front-cover", at(0, 0, -TG), groups=["front-cover"])
add("front-oil-seal", at(0, 0, C.SLEEVE[0] - TG), groups=["front-cover"], explode=ex(FWD, 50, 40))
z_nut = -TG - C.FC_T - 2.0
for u, l in C.FC_STUDS:
    add("front-stud", at(u, l, 14.0) * Rot(180, 0, 0))
    add("front-washer", at(u, l, z_nut) * Rot(180, 0, 0), explode=ex(FWD, 24, 60))
    add("front-nut", at(u, l, z_nut - 2.0) * Rot(180, 0, 0), explode=ex(FWD, 24, 90))

# bellhousing to the engine rear plate: bolt heads on the bosses, washers and nuts on the engine side
from parts.engine.block import plates as P                                     # noqa: E402
from mgb import spec as S                                                     # noqa: E402
from pathlib import Path                                                      # noqa: E402
_EP = {s.id: s for s in S.load_file(Path(__file__).resolve().parent.parent / "specs" / "engine" / "block" / "end-plate.yaml")}
PLATE_T = _EP["engine.block.rear-plate"].nom("thickness")
z_plate = C.BELL_D - PLATE_T
for k, (u, l) in enumerate(C.BELL_HOLES):
    kind = "long" if k >= 6 else ("medium" if k in (0, 5) else "short")
    z_head = C.BELL_D + (46.0 if kind == "long" else C.BOSS_L)
    add(f"bell-bolt-{kind}", at(u, l, z_head) * Rot(180, 0, 0), explode=ex(BACK, 0.5, 100))
    add("bell-washer", at(u, l, z_plate) * Rot(180, 0, 0), explode=ex(FWD, 0.5, 40))
    add("bell-nut", at(u, l, z_plate - 2.4) * Rot(180, 0, 0), explode=ex(FWD, 0.5, 70))
INSTANCES = I
