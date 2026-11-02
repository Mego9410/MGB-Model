"""Gearbox stay (steady) rod, three-synchromesh gearbox (Haynes Ch 1 Fig 1.29 items 20-32; Sec 6 para 33).

Car frame (mgb.chassis_layout STAY_*). Explode stages (Ch 1 Sec 6 para 33: the stay rod is detached from the gearbox
before the crossmember comes off):
  nut and washer off the pin; rod's eye off the pin                     orders 1-2 (before P5b's crossmember, order 3)
  nut, spring washer, buffers, plates and tube off the rod's rear end    order 5
  bracket screws; bracket off the crossmember; pin off the casing         orders 6-7
"""
from build123d import Location, Rot

from mgb import chassis_layout as K, fasteners as F
from mgb.chassis_geom import IN
from parts.gearbox import stay_rod as P

ID = "gearbox.stay-rod"
NAME = "Gearbox stay rod"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "1.29"}], "section": 6}

UP, DOWN, FWD, BACK = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0]
GROUPS = {"rod": {"axis": DOWN, "order": 2, "distance_mm": 80}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.stay-rod." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


Y, Z = K.STAY_Y, K.STAY_Z
PX = K.STAY_PIN[0]
WX = K.STAY_WEB_X
add("bracket", Location(), explode=ex(DOWN, 7, 90))
for x, y, z in K.STAY_BRACKET_SCREWS:
    add("bracket-washer", Location((x, y, z + 3.0)), explode=ex(UP, 6, 40))
    add("bracket-screw", Location((x, y, z + 3.0 + 1.3)) * Rot(180, 0, 0), explode=ex(UP, 6, 80))
add("rod", Location(), groups=["rod"])
add("bush", Location((PX, Y, Z + 9.0 + 2.5)) * Rot(180, 0, 0), groups=["rod"])
add("bush", Location((PX, Y, Z - 9.0 - 2.5)), groups=["rod"])
add("pin", Location(), explode=ex(UP, 7, 60))
for dx in (-14.0, 14.0):
    add("pin-screw", Location((PX + dx, Y - 6.0, K.STAY_PIN_TOP_Z - 8.0)), explode=ex(DOWN, 7, 30))
add("pin-washer", Location((PX, Y, Z - 11.5 - 1.7)), explode=ex(DOWN, 1, 30))
add("pin-nut", Location((PX, Y, Z - 11.5 - 1.7 - 8.5)), explode=ex(DOWN, 1, 60))
# rear end: plate, buffer | web | buffer, plate, washer, nut; the distance tube through the web
ROT = Rot(0, 90, 0)                       # +z -> +x
add("distance-tube", Location((WX - 14.0, Y, Z)) * ROT, explode=ex(BACK, 5, 40))
add("buffer", Location((WX + 3.0, Y, Z)) * ROT, explode=ex(FWD, 5, 30))
add("buffer-plate", Location((WX + 3.0 + 12.0, Y, Z)) * ROT, explode=ex(FWD, 5, 50))
add("buffer", Location((WX, Y, Z)) * Rot(0, -90, 0), explode=ex(BACK, 5, 30))
add("buffer-plate", Location((WX - 12.0, Y, Z)) * Rot(0, -90, 0), explode=ex(BACK, 5, 50))
add("rod-washer", Location((WX - 14.0, Y, Z)) * Rot(0, -90, 0), explode=ex(BACK, 5, 70))
add("rod-nut", Location((WX - 15.3, Y, Z)) * Rot(0, -90, 0), explode=ex(BACK, 5, 90))
INSTANCES = I
