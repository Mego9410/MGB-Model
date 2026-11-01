"""Lubrication system, Haynes Fig 1.16 (with Fig 1.1 early filter and Fig 1.20 pump).

Engine frame (mgb.lube_layout). Explode stages follow Haynes:
  Sec 2   oil filter: centre bolt, bowl and element, then the head        orders 1-3
  Sec 20  drain plug, sump bolts, sump, gasket; strainer                   orders 4-8
  Sec 21  pump nuts, pump with its drive shaft and gasket                  orders 9-10
  Sec 34  pump cover off, rotors out                                       order 11
  Sec 17  relief valve domed nut, washers, spring and cup                  order 12
  dipstick out; external oil pipe off                                      orders 1-2
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import block_section as B, lube_layout as L, spec as S

ID = "engine.lube"
NAME = "Lubrication: sump, oil pump and filter"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.16"}, {"figure": "1.1"}, {"figure": "1.20"}], "section": 28}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "lube" / "lube.yaml")}
UP, DOWN, LEFT, RIGHT = [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]

GROUPS = {
    "sump": {"axis": DOWN, "order": 6, "distance_mm": 260},
    "filter-bowl": {"axis": DOWN, "order": 2, "distance_mm": 170},
    "pump": {"axis": DOWN, "order": 10, "distance_mm": 150},
}


def ex(axis, order, d):
    return {"axis": axis, "order": order, "distance_mm": d}


def at(x, y, z, rx=0, ry=0, rz=0):
    return Location((x, y, z)) * Rot(rx, ry, rz)


I, _n = [], {}


def add(part, loc, **opts):
    pid = "engine.lube." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, opts))


def nom(pid, key):
    return SP["engine.lube." + pid].nom(key)


# ---- sump, gasket, bolts, drain plug -----------------------------------------------------------
add("sump-gasket", at(0, 0, 0), explode=ex(DOWN, 7, 40))
add("sump", at(0, 0, 0), groups=["sump"])
st = nom("sump", "sheet_thickness")
wt = nom("sump-bolt-washer", "thickness")
flange_under = L.SUMP_TOP - st
for k, (x, y) in enumerate(L.sump_bolts()):
    add("sump-bolt-washer", at(x, y, flange_under, rx=180), explode=ex(DOWN, 5, 60), label=k == 0)
    add("sump-bolt", at(x, y, flange_under - wt, rx=180), explode=ex(DOWN, 5, 100), label=k == 0)
dx = nom("sump", "drain_x")
floor_under = L.SUMP_FLOOR - st - 6
dw = nom("drain-plug-washer", "thickness")
add("drain-plug-washer", at(dx, 0, floor_under, rx=180), explode=ex(DOWN, 4, 40))
add("drain-plug", at(dx, 0, floor_under - dw, rx=180), explode=ex(DOWN, 4, 80))

# ---- strainer and oil pump ------------------------------------------------------------------------
add("strainer", at(0, 0, 0), groups=["sump"], explode=ex(DOWN, 8, 60))
add("pump-gasket", at(*L.PUMP_FLANGE, L.PUMP_TOP - 0.5), groups=["pump"])
add("pump-body", at(0, 0, -0.5), groups=["pump"])
add("pump-cover", at(0, 0, -0.5), groups=["pump"], explode=ex(DOWN, 11, 60))
rotor_z = L.PUMP_TOP - 0.5 - nom("pump-body", "body_height") + 0.6
add("pump-inner-rotor", at(L.DRIVE_X, L.DRIVE_Y, rotor_z), groups=["pump"], explode=ex(DOWN, 11.5, 40))
add("pump-outer-rotor", at(L.DRIVE_X + 1.6, L.DRIVE_Y, rotor_z), groups=["pump"], explode=ex(DOWN, 11.5, 40))
add("pump-spindle", at(L.DRIVE_X, L.DRIVE_Y, rotor_z + 6), groups=["pump"])
for k, (x, y) in enumerate(L.pump_studs()):
    add("pump-stud", at(x, y, L.SZ + 12, rx=180), label=k == 0)
    add("pump-nut", at(x, y, L.PUMP_TOP - 9.5, rx=180), explode=ex(DOWN, 9, 70), label=k == 0)

# ---- oil filter (Fig 1.1, early type) ----------------------------------------------------------------
fx, fy, fz = L.FILTER_PAD
ay = L.FILTER_AXIS_Y
add("filter-head", at(0, 0, 0), explode=ex(RIGHT, 3, 120))
for dz in (-14, 14):
    add("filter-head-bolt", at(fx + dz * 1.4, fy - 10, fz + dz * 0.3, rx=-90), explode=ex(RIGHT, 2.5, 90), label=dz < 0)
bowl_top = fz - 18 - 14
add("filter-head-seal", at(fx, ay, bowl_top - 1.5), groups=["filter-bowl"], explode=ex(DOWN, 2.4, 20))
add("filter-case", at(0, 0, 0), groups=["filter-bowl"])
add("filter-element", at(0, 0, 0), groups=["filter-bowl"], explode=ex(UP, 2.6, 60))
case_bottom = bowl_top - nom("filter-case", "height")
add("filter-spring", at(fx, ay, case_bottom + 4), groups=["filter-bowl"], explode=ex(UP, 2.7, 30))
add("filter-plate", at(fx, ay, case_bottom + 26), groups=["filter-bowl"], explode=ex(UP, 2.8, 50))
add("filter-steel-washer", at(fx, ay, case_bottom - 3 - 1.2), groups=["filter-bowl"], explode=ex(DOWN, 1.5, 30))
add("filter-bolt-seal", at(fx, ay, case_bottom - 3 + 0.1), groups=["filter-bowl"], explode=ex(DOWN, 1.5, 20))
add("filter-centre-bolt", at(0, 0, -1.2), explode=ex(DOWN, 1, 220))
add("oil-pipe", at(0, 0, 0), explode=ex(RIGHT, 1.5, 70))

# ---- relief valve (Sec 17), left rear --------------------------------------------------------------------
rx_, ry_, rz_ = L.RELIEF
rw = nom("relief-washer", "thickness")
add("relief-washer", at(rx_, ry_, rz_, rx=-90), explode=ex(LEFT, 12.2, 30), label=True)
add("relief-washer", at(rx_, ry_ + rw, rz_, rx=-90), explode=ex(LEFT, 12.3, 40), label=False)
add("relief-nut", at(rx_, ry_ + 2 * rw, rz_, rx=-90), explode=ex(LEFT, 12, 110))
spring_l = nom("relief-spring", "fitted_length")
add("relief-spring", at(rx_, ry_ - spring_l + 2 * rw, rz_, rx=-90), explode=ex(LEFT, 12.4, 160))
add("relief-cup", at(rx_, ry_ - spring_l - 14, rz_, rx=-90), explode=ex(LEFT, 12.5, 220))

# ---- dipstick ---------------------------------------------------------------------------------------------
d = L.DIPSTICK_DIR
add("dipstick", at(0, 0, 0), explode=ex([0, -d[1], -d[2]], 1, 260))

INSTANCES = I
