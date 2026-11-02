"""Laycock type D overdrive hydraulics and controls: operating pistons and bridge pieces, the pump
cam on the mainshaft, pump, non-return valve, relief valve, operating valve, filter, the solenoid
with its operating lever and cover (Haynes Ch 6 Fig 6.13; Figs 6.12, 6.14, 6.15, 6.17, 6.18;
Sec 2 para 5, Sec 12 paras 1-3 and 22-24, Sec 13, Sec 14).

Built in the gearbox frame (GF) at the overdrive stations of mgb.overdrive_layout. Explode stages
follow Haynes (numbering shared with the other overdrive assemblies):
  Sec 2 para 5    filter, sealing plate and magnetic rings out to the left               order 3.5
  Sec 13 para 2   cover bolts, the cover and gasket; then the solenoid and the lever       orders 5-9
  Sec 12 para 1   operating valve plug, spring, plunger and ball, then the valve           orders 10-12
  Sec 12 para 2   lockwasher tabs and nuts, the bridge pieces, the pistons                 orders 20-22
  Sec 12 para 3   non-return valve plug, spring and ball, its body, the grub screw, the
                  pump body with the plunger                                             orders 30-34
  Sec 14 para 2   relief valve plug, washer, spring, plunger, body                         orders 35-36
  (the cam, key and circlip stay on the mainshaft: shown lifting off it)                  order 100
"""
from build123d import Location, Rot

from mgb import gearbox_layout as G, overdrive_layout as O
from parts.gearbox import od_hydraulics as OH

ID = "gearbox.overdrive-hydraulics"
NAME = "Overdrive pump, valves, operating pistons and solenoid"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.13"}, {"figure": "6.14"}, {"figure": "6.17"}], "section": 12}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"filter": {"axis": LEFT, "order": 3.5, "distance_mm": 150},
          "solenoid": {"axis": RIGHT, "order": 8, "distance_mm": 110},
          "lever": {"axis": RIGHT, "order": 9.5, "distance_mm": 160},
          "pump": {"axis": DOWN, "order": 34, "distance_mm": 150},
          "relief": {"axis": DOWN, "order": 36, "distance_mm": 130},
          "pistons": {"axis": FWD, "order": 22, "distance_mm": 90}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.overdrive-hydraulics." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF


def at(u, l, e):
    return GF * Location((u, l, O.d(e)))


# filter (Sec 2 para 5)
add("sealing-plate", GF, groups=["filter"], explode=ex(LEFT, 3.6, 30))
add("magnetic-ring", GF, groups=["filter"], explode=ex(LEFT, 3.7, 20))
add("magnetic-ring", GF * Location((0, -12.0, 0)), groups=["filter"], explode=ex(LEFT, 3.7, 10))
add("filter", GF, groups=["filter"])

# lever chamber cover, solenoid, lever (Sec 13)
cf = O.CHAMBER_FACE - 0.8 - 2.0
for u, e in OH.CHAMBER_SCREWS:
    add("cover-washer", at(u, cf, e) * Rot(90, 0, 0), explode=ex(RIGHT, 5, 50))
    add("cover-screw", at(u, cf - 1.6, e) * Rot(-90, 0, 0), explode=ex(RIGHT, 5, 80))
add("cover", GF, explode=ex(RIGHT, 6, 120))
add("cover-gasket", GF, explode=ex(RIGHT, 6, 80))
f0 = O.SOL_E[0] + 0.8 + 4.0
for u, l in OH.SOL_SCREWS:
    add("solenoid-washer", at(u, l, f0) * Rot(0, 0, 0), groups=["solenoid"], explode=ex(BACK, 7, 30))
    add("solenoid-screw", at(u, l, f0 + 0.6) * Rot(180, 0, 0), groups=["solenoid"], explode=ex(BACK, 7, 55))
add("solenoid-nut", GF, explode=ex(FWD, 7.5, 40))
add("solenoid", GF, groups=["solenoid"], explode=ex(BACK, 8.2, 80))
add("solenoid-gasket", GF, groups=["solenoid"], explode=ex(BACK, 8.2, 30))
add("mills-pin", GF, groups=["lever"], explode=ex(UP, 9, 40))
add("mills-pin", GF * Location((0, O.OPVALVE[1] - O.LEVER_LEFT - 4.0, 0)), groups=["lever"], explode=ex(UP, 9, 40))
add("lever-o-ring", GF, groups=["lever"], explode=ex(RIGHT, 9.7, 30))
add("op-lever", GF, groups=["lever"])

# operating valve (Sec 12 para 1, Sec 14 paras 5-6)
add("op-plug", GF, explode=ex(UP, 10, 120))
add("op-washer", GF, explode=ex(UP, 10, 95))
add("op-spring", GF, explode=ex(UP, 11, 80))
add("op-plunger", GF, explode=ex(UP, 11, 65))
add("op-ball", GF, explode=ex(UP, 11.5, 55))
add("op-valve", GF, explode=ex(UP, 12, 40))

# pistons, bridge pieces, lockwashers and nuts (Sec 12 paras 2, 22)
b0 = O.BRIDGE_E[0]
lw = 0.9
for u, l in O.BOLTS:
    r = Rot(0, 180, 0) if l > 0 else Rot(180, 0, 0)
    add("lockwasher", at(u, l, b0) * r, explode=ex(FWD, 20, 40))
    add("bridge-nut", at(u, l, b0 - lw) * Rot(180, 0, 0), explode=ex(FWD, 20, 65))
for s in (1, -1):
    loc = GF * Location((0, s * O.CYL_LEFT, 0))
    add("bridge-piece", loc, explode=ex(FWD, 21, 50))
    add("piston", loc, groups=["pistons"])
    add("piston-o-ring", loc, groups=["pistons"], explode=ex(FWD, 22.5, 30))

# pump and non-return valve (Sec 12 para 3)
add("nrv-plug", GF, explode=ex(DOWN, 30, 110))
add("nrv-washer", GF, explode=ex(DOWN, 30, 90))
add("nrv-spring", GF, explode=ex(DOWN, 31, 75))
add("nrv-ball", GF, explode=ex(DOWN, 31, 60))
add("nrv-body", GF, explode=ex(DOWN, 32, 50))
add("grub-screw", GF, explode=ex(FWD, 33, 40))
add("pump-body", GF, groups=["pump"])
add("pump-spring", GF, groups=["pump"], explode=ex(UP, 34.5, 20))
add("pump-plunger", GF, groups=["pump"], explode=ex(UP, 34.5, 35))
add("pump-pin", GF, groups=["pump"], explode=ex(UP, 34.5, 55))

# relief valve (Sec 14 para 2)
add("relief-plug", GF, explode=ex(DOWN, 35, 100))
add("relief-washer", GF, explode=ex(DOWN, 35, 80))
add("relief-spring", GF, groups=["relief"], explode=ex(DOWN, 35.5, 20))
add("relief-plunger", GF, groups=["relief"], explode=ex(DOWN, 35.7, 10))
add("relief-body", GF, groups=["relief"])
add("relief-o-ring", GF, groups=["relief"], explode=ex(UP, 36.5, 20))

# pump cam on the mainshaft (Sec 11 para 5)
add("cam-circlip", GF, explode=ex(BACK, 100, 60))
add("cam", GF, explode=ex(UP, 101, 70))
add("key", GF, explode=ex(UP, 102, 40))
INSTANCES = I
