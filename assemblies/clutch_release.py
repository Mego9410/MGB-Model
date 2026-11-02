"""Clutch release bearing and withdrawal lever on the gearbox (Haynes Ch 5 Sec 7, Fig 5.1
items 8-9, Fig 5.2 item 6, photos 7.1 and 7.3). The bellhousing itself comes in P5; its
datums are in mgb.gearbox_layout.

Explode stages follow Haynes Sec 7, with the engine and gearbox separated (para 1):
  para 2   the two spring clips turned through 90 deg and removed       order 1
           the bearing lifted out of the fork, then out of its cup        orders 2-3
  para 3   locknut and washer off, pivot bolt out                        orders 4-5
           the lever (with its bush) and the dust cover off               orders 6-7
"""
from build123d import Location, Rot

from mgb import clutch_layout as K, gearbox_layout as G

ID = "clutch.release"
NAME = "Release bearing and withdrawal lever"
PARENT = "clutch"
HAYNES = {"figures": [{"figure": "5.1"}, {"figure": "5.2"}], "section": 7}

UP, DOWN, FWD = [0, 0, 1], [0, 0, -1], [1, 0, 0]
OUT = list(G.LEVER_DIR)
GROUPS = {"bearing": {"axis": FWD, "order": 2, "distance_mm": 70},
          "lever": {"axis": FWD, "order": 6, "distance_mm": 60}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "clutch.release." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


CF = Location((K.FACE_X, 0.0, K.CZ)) * Rot(0, -90, 0)
O = Location((0, 0, 0))

add("clip", CF, explode=ex(UP, 1, 40))
add("clip", CF * Rot(0, 0, 180), explode=ex(DOWN, 1, 40), label=False)
add("cup", CF, groups=["bearing"])
add("carbon", CF, groups=["bearing"], explode=ex(FWD, 3, 40))
add("locknut", O, explode=ex(DOWN, 4, 60))
add("pivot-washer", O, explode=ex(DOWN, 4, 40))
add("pivot-bolt", O, explode=ex(UP, 5, 110))
add("lever", O, groups=["lever"])
add("bush", O, groups=["lever"], explode=ex(UP, 7, 50))
add("dust-cover", O, explode=ex(OUT, 7, 70))
INSTANCES = I
