"""Water pump, fan, belt, radiator and hoses (Haynes Ch 2, Figs 2.4 and 2.6).

Explode stages follow Haynes: Sec 4 drain (tap), Sec 7 hoses then radiator out
forward, Sec 9 fan and pulley bolts, fan and pulley off, pump bolts, pump and gasket.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import cooling_layout as C, spec as S

ID = "cooling.pump-radiator"
NAME = "Water pump, fan and radiator"
PARENT = "cooling"
HAYNES = {"figures": [{"figure": "2.6"}, {"figure": "2.4"}], "section": 9}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "cooling" / "cooling.yaml")}
FWD = [1, 0, 0]
GROUPS = {"radiator": {"axis": FWD, "order": 3, "distance_mm": 260},
          "pump": {"axis": FWD, "order": 8, "distance_mm": 140}}


def ex(order, d, axis=FWD):
    return {"axis": axis, "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "cooling." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
y, z = C.PUMP_AXIS
# radiator, cap, drain tap
add("radiator", O, groups=["radiator"])
fx, fy, fz = C.FILLER
add("pressure-cap", Location((fx, fy, fz + 23)), groups=["radiator"], explode=ex(1, 60, [0, 0, 1]))
add("drain-tap", Location(((C.RAD_CORE[0] + C.RAD_CORE[1]) / 2, C.RAD_Y[1] + 16, C.RAD_BOTTOM_TANK[0] + 16)) * Rot(-90, 0, 0),
    groups=["radiator"], explode=ex(1, 40, [0, 1, 0]))
# hoses and clips
add("top-hose", O, explode=ex(2, 90, [0, 0, 1]))
add("bottom-hose", O, explode=ex(2, 90, [0, -1, 0]))
ix, iy, iz = C.TOP_INLET
ox, oy, oz = C.BOTTOM_OUTLET
ex_, ey, ez = C.ELBOW_OUTLET
d = C.ELBOW_DIR
px, py, pz = C.PUMP_INLET
pd = C.PUMP_INLET_DIR
add("hose-clip", Location((ix - 22, iy, iz)) * Rot(0, 90, 0), explode=ex(1.5, 50, [0, 0, 1]))
add("hose-clip", Location((ex_ - d[0] * 14, ey, ez - d[2] * 14)) * Rot(0, 64.7, 0), explode=ex(1.5, 50, [0, 0, 1]), label=False)
add("hose-clip", Location((ox - 22, oy, oz)) * Rot(0, 90, 0), explode=ex(1.5, 50, [0, -1, 0]), label=False)
add("hose-clip", Location((px - pd[0] * 18, py - pd[1] * 18, pz - pd[2] * 18)) * Rot(-33.4, 0, 0),
    explode=ex(1.5, 50, [0, -1, 0]), label=False)
# belt, fan, pulley
add("fan-belt", O, explode=ex(4, 120, [1, 0, 0.3]))
x_fan = C.BELT_X + 9.5 + 8 + 2.5
for k in range(4):
    import math
    a = math.radians(45 + 90 * k)
    add("fan-screw", Location((x_fan, y + 19 * math.cos(a), z + 19 * math.sin(a))) * Rot(0, -90, 0),
        explode=ex(5, 90), label=k == 0)
add("fan", O, explode=ex(6, 160))
add("pump-pulley", O, explode=ex(7, 110))
# pump
for k, (sy, sz) in enumerate(((-30, 22), (30, 22), (-30, -22), (30, -22))):
    wt = SP["cooling.pump-bolt-washer"].nom("thickness")
    xf = C.PUMP_FACE_X + 0.8 + 12
    add("pump-bolt-washer", Location((xf, y + sy, z + sz)) * Rot(0, 90, 0), explode=ex(7.5, 60), label=k == 0)
    add("pump-bolt", Location((xf + wt, y + sy, z + sz)) * Rot(0, -90, 0), explode=ex(7.5, 100), label=k == 0)
add("pump-body", O, groups=["pump"])
add("pump-spindle", O, groups=["pump"], explode=ex(9, 80))
add("pump-gasket", O, explode=ex(9, 30))
INSTANCES = I
