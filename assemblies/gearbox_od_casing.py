"""Laycock type D overdrive casings: main casing, brake ring, rear casing and their studs, nuts and
washers; the nuts on the adaptor studs; the filter cover, drain plug and pressure plug; the
speedometer drive in the rear casing with the angle drive and the cable end (Haynes Ch 6 Fig 6.13;
Sec 2 para 5, Sec 11 paras 2-3, Sec 12 paras 4 and 9).

Built in the gearbox frame (mgb.gearbox_layout GF) at the overdrive stations of
mgb.overdrive_layout. Explode stages follow Haynes (Sec 11, then Sec 12), numbered with the
other overdrive assemblies; the main casing stays put:
  Ch 1 Sec 6 para 30  speedometer cable disconnected                              order 0.5
  Sec 11 para 3       the eight nuts and washers off the adaptor studs              order 1
  Sec 2 paras 4-5     drain plug; filter cover bolts, cover and gasket             orders 2-3
  Sec 12 para 4       the eight casing nuts a turn at a time, rear casing back,
                      then the brake ring                                            orders 40-43
  Sec 12 para 9       locking screw, then the speedometer pinion and bush            orders 90-91
"""
import math

from build123d import Location, Rot

from mgb import gearbox_layout as G, overdrive_layout as O
from parts.gearbox import od_casing as OC

ID = "gearbox.overdrive-casing"
NAME = "Overdrive casings, filter cover, plugs and speedometer drive"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.13"}, {"figure": "6.12"}, {"figure": "6.18"}], "section": 12}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"rear": {"axis": BACK, "order": 42, "distance_mm": 260},
          "speedo": {"axis": RIGHT, "order": 91, "distance_mm": 90}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.overdrive-casing." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF


def at(u, l, e):
    return GF * Location((u, l, O.d(e)))


add("main-casing", GF)
add("brake-ring", GF, explode=ex(BACK, 43, 140))
add("rear-casing", GF, groups=["rear"])

# eight nuts and spring washers on the adaptor studs, on the main casing flange (Sec 11 para 3)
fl = O.MC_FLANGE[1]
for u, l in O.OD_STUDS:
    add("od-washer", at(u, l, fl), explode=ex(BACK, 1, 50))
    add("od-nut", at(u, l, fl + 1.6), explode=ex(BACK, 1, 80))

# casing studs in the main casing, nuts and washers on the rear casing flange (Sec 12 para 4)
f1 = O.RC_FLANGE[1]
for u, l in O.CASE_STUDS:
    add("case-stud", at(u, l, O.MC_REAR_FL[0] - 3.6))
    add("case-washer", at(u, l, f1), explode=ex(BACK, 40, 60))
    add("case-nut", at(u, l, f1 + 1.6), explode=ex(BACK, 40, 90))

# filter cover on the left of the sump (Sec 2 para 5)
face = O.FILTER_FACE + 0.8 + 2.0
for u, e in OC.COVER_SCREWS:
    add("cover-washer", at(u, face, e) * Rot(-90, 0, 0), explode=ex(LEFT, 2, 50))
    add("cover-screw", at(u, face + 1.6, e) * Rot(90, 0, 0), explode=ex(LEFT, 2, 80))
add("filter-cover", GF, explode=ex(LEFT, 3, 110))
add("filter-cover-gasket", GF, explode=ex(LEFT, 3, 70))

# drain plug (Sec 2 para 4) and the pressure take-off plug
de, dl = O.DRAIN
w = 1.5
add("drain-washer", at(O.PLUG_FACE - w, dl, de) * Rot(0, 90, 0), explode=ex(DOWN, 2, 50))
add("drain-plug", at(O.PLUG_FACE - w, dl, de) * Rot(0, 90, 0), explode=ex(DOWN, 2, 90))
pe, pu = O.PLUG39
y0 = O.SUMP_LEFT[0] - 6.0
add("plug-washer", at(pu, y0 - 1.2, pe) * Rot(-90, 0, 0), explode=ex(RIGHT, 2.5, 40))
add("plug", at(pu, y0 - 1.2, pe) * Rot(-90, 0, 0), explode=ex(RIGHT, 2.5, 70))

# speedometer drive in the rear casing (Sec 12 paras 9, 15), the angle drive and the cable end
add("cable-end", GF, groups=["rear"], explode=ex(FWD, 0.5, 120))
add("angle-drive", GF, groups=["rear"], explode=ex(RIGHT, 0.6, 80))
add("lock-screw", GF, groups=["rear"], explode=ex(RIGHT, 90, 70))
add("lock-washer", GF, groups=["rear"], explode=ex(RIGHT, 90, 45))
for p in ("speedo-housing", "speedo-o-ring", "speedo-pin", "speedo-seal"):
    add(p, GF, groups=["rear", "speedo"])
add("speedo-gear", GF, groups=["rear", "speedo"], explode=ex(RIGHT, 92, 60))
INSTANCES = I
