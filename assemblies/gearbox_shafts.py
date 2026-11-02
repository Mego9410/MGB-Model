"""Gearbox shafts and gears: first motion shaft, mainshaft with its gears and synchronisers,
laygear and layshaft, reverse idler (Haynes Ch 6 Fig 6.3 items 35-44, 83-114; Fig 6.6).

Built in the gearbox frame (mgb.gearbox_layout GF) and placed with it. Explode stages follow
Haynes (numbering shared across the gearbox assemblies):
  Sec 4 para 10/22  reverse shaft locating screw and tab washer out               order 23
  Sec 4 para 11     shims off with the front cover; reverse gear and shaft out     orders 25-26
  Sec 4 paras 12-13 layshaft drifted out forward, laygear lowered                  orders 27-28
  Sec 4 para 14     mainshaft, centre bearing and housing out of the back          order 29
  Sec 4 para 15     first motion shaft tapped forward; laygear lifted out          orders 30-31
  Sec 5 para 7      first motion shaft nut and lock washer; bearing and ring off   orders 32-33
  Sec 5 paras 9-12  3rd/4th synchroniser off; locking washer and peg; third gear,
                    its bush, the interlocking ring, second gear and bush, baulk
                    ring, first gear and its synchroniser                          orders 34-43
  Sec 5 para 22     laygear rollers, rings and distance tube out                    order 45
"""
from build123d import Location, Rot

from mgb import gearbox_layout as G
from parts.gearbox import shafts as SH

ID = "gearbox.shafts"
NAME = "Shafts, gears and synchromesh"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.3"}, {"figure": "6.6"}], "section": 5}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"reverse": {"axis": LEFT, "order": 26, "distance_mm": 150},
          "laygear": {"axis": DOWN, "order": 28, "distance_mm": 25},
          "laygear-out": {"axis": LEFT, "order": 31, "distance_mm": 190},
          "mainshaft": {"axis": BACK, "order": 29, "distance_mm": 330},
          "fms": {"axis": FWD, "order": 30, "distance_mm": 260},
          "syn34": {"axis": FWD, "order": 34, "distance_mm": 380},
          "syn12": {"axis": FWD, "order": 43, "distance_mm": 110},
          "ctr": {"axis": BACK, "order": 44, "distance_mm": 90}}
MS = ["mainshaft"]
LG = ["laygear", "laygear-out"]


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.shafts." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF


def radial_dir(theta):
    """Car-frame unit vector outward from the mainshaft at a gearbox-frame angle (from up toward left)."""
    import math
    t = math.radians(theta)
    return [0.0, math.sin(t), math.cos(t)]


def balls(group_hub, z, angles, order):
    for k, th in enumerate(angles):
        add("synchro-spring", GF * Rot(0, 0, th) * Location((18.0, 0, z)) * Rot(0, 90, 0), groups=MS + [group_hub],
            explode=ex(radial_dir(th), order, 30))
        add("synchro-ball", GF * Rot(0, 0, th) * Location((29.6, 0, z)), groups=MS + [group_hub],
            explode=ex(radial_dir(th), order, 50))


# ---- reverse ----------------------------------------------------------------------------------------
add("reverse-screw", GF, explode=ex(UP, 23, 60))
add("reverse-tab-washer", GF, explode=ex(UP, 23, 35))
add("reverse-shaft", GF, groups=["reverse"], explode=ex(BACK, 25.5, 120))
add("reverse-gear", GF, groups=["reverse"])
add("reverse-bush", GF, groups=["reverse"], explode=ex(FWD, 46, 60))

# ---- layshaft and laygear ---------------------------------------------------------------------------
add("layshaft", GF, explode=ex(FWD, 27, 300))
add("laygear", GF, groups=LG)
add("lay-thrust-front", GF, groups=LG, explode=ex(FWD, 45, 30))
add("lay-thrust-rear", GF, groups=LG, explode=ex(BACK, 45, 30))
for z0, L in SH.ROLLER_SETS:
    add("lay-needles", GF * Location((0, 0, z0)), groups=LG, explode=ex(FWD if z0 < 100 else BACK, 45.5, 60))
add("lay-distance-tube", GF, groups=LG, explode=ex(FWD, 46, 120))
add("lay-ring", GF, groups=LG, explode=ex(FWD, 45, 50))
add("lay-ring", GF * Location((0, 0, G.LAY_ENDS[1] - 3.1 - (G.LAY_ENDS[0] + 2.1))), groups=LG, explode=ex(BACK, 45, 50))

# ---- first motion shaft -----------------------------------------------------------------------------
F = ["fms"]
add("first-motion-shaft", GF, groups=F)
add("fms-needles", GF, groups=F, explode=ex(BACK, 31.5, 60))
add("fms-shim", GF, explode=ex(FWD, 25, 40))
add("fms-bearing", GF, groups=F, explode=ex(FWD, 33, 70))
add("fms-ring", GF, groups=F, explode=ex(FWD, 33, 95))
add("fms-lock-washer", GF, groups=F, explode=ex(FWD, 32, 50))
add("fms-nut", GF, groups=F, explode=ex(FWD, 32, 80))

# ---- mainshaft --------------------------------------------------------------------------------------
add("mainshaft", GF, groups=MS)
add("oil-restrictor", GF, groups=MS, explode=ex(FWD, 46, 40))
add("centre-bearing", GF, groups=MS + ["ctr"])
add("bearing-housing", GF, groups=MS + ["ctr"], explode=ex(BACK, 44.5, 40))
add("housing-peg", GF, groups=MS + ["ctr"], explode=ex(BACK, 44.5, 70))
add("mainshaft-clip", GF, groups=MS, explode=ex(BACK, 43.5, 60))
# 3rd/4th synchroniser (slid off as one, Sec 5 para 9)
S34 = MS + ["syn34"]
add("baulk-ring-34", GF, groups=S34, explode=ex(FWD, 35, 45))
add("synchro-hub-34", GF, groups=S34)
add("coupling-sleeve", GF, groups=S34, explode=ex(FWD, 35, 20))
add("baulk-ring-34-rear", GF, groups=S34, explode=ex(BACK, 35, 40))
balls("syn34", sum(G.SYN34) / 2, [120.0, 240.0, 360.0], 35.5)
# third gear retention (Fig 6.6) and the gears
add("third-gear-washer", GF, groups=MS, explode=ex(FWD, 36, 320))
add("peg", GF, groups=MS, explode=ex(UP, 36.5, 30))
add("peg-spring", GF, groups=MS, explode=ex(UP, 36.5, 20))
add("third-gear", GF, groups=MS, explode=ex(FWD, 37, 280))
add("third-gear-bush", GF, groups=MS, explode=ex(FWD, 38, 245))
add("interlock-ring", GF, groups=MS, explode=ex(FWD, 39, 220))
add("second-gear", GF, groups=MS, explode=ex(FWD, 40, 195))
add("second-gear-bush", GF, groups=MS, explode=ex(FWD, 41, 165))
add("baulk-ring-2", GF, groups=MS, explode=ex(FWD, 42, 140))
S12 = MS + ["syn12"]
add("synchro-hub-12", GF, groups=S12)
add("first-gear", GF, groups=S12, explode=ex(UP, 43.5, 70))
balls("syn12", (G.G1[0] + G.G1_TEETH[1]) / 2, [120.0, 240.0, 360.0], 43.7)
add("rear-thrust-washer", GF, groups=MS, explode=ex(BACK, 43.2, 40))
INSTANCES = I
