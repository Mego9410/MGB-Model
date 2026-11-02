"""Laycock type D overdrive power train: clutch springs and bolts, thrust bearing and housing, cone
clutch, sun wheel, planet carrier and planets, uni-directional clutch, annulus and output shaft with
its bearings, the speedometer driving gear, spacer and shim, the rear oil seal and the coupling
flange (Haynes Ch 6 Fig 6.13; Figs 6.10-6.12, 6.16; Sec 12 paras 4-9, 13-19; Sec 15).

Built in the gearbox frame (GF) at the overdrive stations of mgb.overdrive_layout; drawn in direct
drive. Explode stages follow Haynes Sec 12 (numbering shared with the other overdrive assemblies);
the annulus and output shaft stay put:
  para 4  the four clutch springs off their bolts; the clutch with the sun wheel out   orders 44-45
  para 5  circlip 59, the sun wheel pushed out of the clutch                          orders 50-51
  para 6  circlip 58, the bearing housing with the thrust bearing (and bolts, plate)  orders 60-61
  para 7  the planet carrier lifted out; circlip and oil thrower, inner member,
          rollers, cage                                                              orders 70-75
  para 8  the needle bearing levered out                                             order 80
  para 9  split pin, nut 103 and washer, flange off, oil seal; the output shaft and
          annulus drifted forward with the larger bearing; the rear bearing out
          of the back; speedometer gear, spacer and shim                             orders 89-96
"""
import math

from build123d import Location, Rot

from mgb import gearbox_layout as G, overdrive_layout as O
from parts.gearbox import od_internals as OI

ID = "gearbox.overdrive-internals"
NAME = "Overdrive clutch, gear train, annulus and output shaft"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.13"}, {"figure": "6.12"}, {"figure": "6.16"}], "section": 12}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"clutch-sun": {"axis": FWD, "order": 45, "distance_mm": 260},
          "housing": {"axis": FWD, "order": 61, "distance_mm": 120},
          "sun": {"axis": BACK, "order": 51, "distance_mm": 60},
          "carrier": {"axis": FWD, "order": 70, "distance_mm": 150},
          "ud": {"axis": FWD, "order": 73, "distance_mm": 60},
          "flange": {"axis": BACK, "order": 91, "distance_mm": 120}}
CS = ["clutch-sun"]
HS = CS + ["housing"]


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.overdrive-internals." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF


def at(u, l, e):
    return GF * Location((u, l, O.d(e)))


# springs, bolts, retainer plate, thrust bearing and housing (Sec 12 paras 4, 6)
for u, l in O.BOLTS:
    add("clutch-spring", at(u, l, O.SPRING_E[0]), explode=ex(FWD, 44, 110))
    add("clutch-bolt", at(u, l, O.HOUSING_E[0] + 8.0), groups=HS)
add("retainer-plate", GF, groups=HS, explode=ex(FWD, 62, 40))
add("bearing-housing", GF, groups=HS)
add("thrust-bearing", GF, groups=HS, explode=ex(BACK, 62, 30))
add("housing-circlip", GF, groups=CS, explode=ex(FWD, 60, 70))

# cone clutch and sun wheel
add("clutch", GF, groups=CS)
add("sun-circlip", GF, groups=CS, explode=ex(FWD, 50, 60))
add("sun-wheel", GF, groups=CS + ["sun"])
add("steady-bush", GF, groups=CS + ["sun"], explode=ex(FWD, 52, 80))

# planet carrier with its planets, timed to the sun (Fig 6.16)
add("locating-ring", GF, groups=["carrier"], explode=ex(FWD, 71, 30))
add("planet-carrier", GF, groups=["carrier"])
for k, a in enumerate(OI.planet_angles()):
    x, y = O.PLANET_CIRCLE * math.cos(math.radians(a)), O.PLANET_CIRCLE * math.sin(math.radians(a))
    add("planet", GF * Location((x, y, 0)) * Rot(0, 0, OI.planet_phase(k)), groups=["carrier"])
    add("planet-pin", GF * Location((x, y, 0)), groups=["carrier"], explode=ex(FWD, 71.5, 60))

# uni-directional clutch (Sec 12 paras 7, 16)
add("ud-circlip", GF, explode=ex(FWD, 72, 100))
add("oil-thrower", GF, explode=ex(FWD, 72, 75))
add("ud-inner", GF, groups=["ud"], explode=ex(FWD, 73.5, 40))
for k in range(O.UD_N):
    a = math.radians(360.0 * (k + 0.6) / O.UD_N)
    add("ud-roller", GF * Location((OI.ROLLER_PC * math.cos(a), OI.ROLLER_PC * math.sin(a), 0)), groups=["ud"],
        explode={"axis": [0, math.sin(a), math.cos(a)], "order": 74, "distance_mm": 25})
add("ud-cage", GF, groups=["ud"], explode=ex(FWD, 75, 50))
add("ud-spring", GF, groups=["ud"], explode=ex(FWD, 75, 70))
add("thrust-washer", GF, explode=ex(FWD, 76, 90))

# annulus and output shaft, bearings, speedometer gear, spacer, shim; seal and flange (paras 8-9)
add("annulus", GF)
add("needle-bearing", GF, explode=ex(FWD, 80, 140))
add("front-bearing", GF, explode=ex(BACK, 93, 40))
add("speedo-drive-gear", GF, explode=ex(BACK, 95, 70))
add("spacer", GF, explode=ex(BACK, 95.5, 100))
add("shim", GF, explode=ex(BACK, 96, 120))
add("rear-bearing", GF, explode=ex(BACK, 94, 150))
add("rear-seal", GF, explode=ex(BACK, 92, 180))
add("split-pin", GF, groups=["flange"], explode=ex(UP, 89, 40))
add("flange-nut", GF, groups=["flange"], explode=ex(BACK, 90, 60))
add("flange-washer", GF, groups=["flange"], explode=ex(BACK, 90, 40))
add("flange", GF, groups=["flange"])
INSTANCES = I
