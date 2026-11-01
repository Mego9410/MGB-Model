"""Timing gear and cover, Haynes Fig 1.25 (with Fig 1.11 tensioner).

Engine frame (mgb.engine_layout / mgb.timing_layout). Explode stages follow Haynes
Sec 19 (removal):
  para 5-7    pulley bolt and lockwasher, pulley, Woodruff key       orders 1-3
  para 8      timing cover screws, cover and seal, gasket            orders 4-6
  para 9      oil thrower                                            order 7
  para 10     tensioner bottom plug, bolts and tab washer, tensioner orders 8-10
  para 11-12  camshaft nut and lockwasher; both wheels with chain    orders 11-12
  Sec 51/23   packing washer, keys, camshaft locating plate          orders 13-15
"""
import math
from pathlib import Path

from build123d import Location, Rot

from mgb import spec as S, timing_layout as T

ID = "engine.timing"
NAME = "Timing gear and cover"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.25"}, {"figure": "1.11"}], "section": 19}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "engine" / "timing" / "timing.yaml")}
FWD = [1, 0, 0]

GROUPS = {
    "wheels": {"axis": FWD, "order": 12, "distance_mm": 150},
    "tensioner": {"axis": FWD, "order": 10, "distance_mm": 120},
    "cover": {"axis": FWD, "order": 5, "distance_mm": 230},
}


def ex(order, d, axis=FWD):
    return {"axis": axis, "order": order, "distance_mm": d}


def at(x, y, z, rx=0, ry=0, rz=0):
    return Location((x, y, z)) * Rot(rx, ry, rz)


I, _n = [], {}


def add(part, loc, **opts):
    pid = "engine.timing." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, opts))


cy, cz = T.CAM
ky, kz = T.CRANK

# ---- camshaft locating plate (on the front plate, photo 50.5) ---------------------------------
add("locating-plate", at(T.PANEL_FACE, cy, cz, ry=90), explode=ex(15, 60))
lw_t = SP["engine.timing.locating-plate-washer"].nom("thickness")
for k in range(3):
    a = math.radians(90 + 120 * k)
    y, z = cy + 34 * math.cos(a), cz + 34 * math.sin(a)
    add("locating-plate-washer", at(T.PANEL_FACE + T.LOCATING_T, y, z, ry=90), explode=ex(14, 50), label=k == 0)
    add("locating-plate-screw", at(T.PANEL_FACE + T.LOCATING_T + lw_t, y, z, ry=-90), explode=ex(14, 80), label=k == 0)

# ---- wheels, keys and chain (lifted off together, Sec 19 para 12) --------------------------------
cam_hub = SP["engine.timing.cam-wheel"].nom("hub_length")
crank_hub = SP["engine.timing.crank-wheel"].nom("hub_length")
add("cam-wheel", at(T.CAM_HUB_X, cy, cz), groups=["wheels"])
add("crank-wheel", at(T.CRANK_HUB_X, ky, kz), groups=["wheels"])
add("chain", at(0, 0, 0), groups=["wheels"])
add("cam-key", at(T.CAM_HUB_X + cam_hub / 2, cy, cz + 11.0 + 1.6), explode=ex(13, 40, [0, 0, 1]))
add("crank-key", at(T.CRANK_HUB_X + crank_hub / 2, ky, kz + 31.75 / 2 + 1.6), explode=ex(13, 40, [0, 0, 1]))
add("packing-washer", at(T.CRANK_SHOULDER_X, ky, kz), explode=ex(13, 70))
cl_t = SP["engine.timing.cam-lockwasher"].nom("thickness")
add("cam-lockwasher", at(T.CAM_HUB_X + cam_hub, cy, cz, ry=90), explode=ex(11, 80))
add("cam-nut", at(T.CAM_HUB_X + cam_hub + cl_t, cy, cz, ry=90), explode=ex(11, 110))

# ---- tensioner (Fig 1.11), built in place ----------------------------------------------------------
for part in ("tensioner-backplate", "tensioner-body", "tensioner-slipper", "tensioner-spring", "tensioner-cylinder"):
    add(part, at(0, 0, 0), groups=["tensioner"])
(py, pz), m = T.tensioner_point()
add("tensioner-plug", at(0, 0, 0), explode=ex(8, 50, [0, m[0], m[1]]))
tab_t = SP["engine.timing.tensioner-lockwasher"].nom("thickness")
add("tensioner-lockwasher", at(0, 0, 0), explode=ex(9, 60))
run = (-m[1], m[0])
v_lug = T.ROLLER_D / 2 + 1.0 + 14 + 30
for u in (-24, 24):
    y, z = py + run[0] * u + m[0] * v_lug, pz + run[1] * u + m[1] * v_lug
    add("tensioner-bolt", at(T.PANEL_FACE + 1.6 + 8 + tab_t, y, z, ry=-90), explode=ex(9, 90), label=u < 0)

# ---- oil thrower, cover, gasket, seal, screws --------------------------------------------------------
add("oil-thrower", at(T.CRANK_HUB_X + crank_hub, ky, kz), explode=ex(7, 120))
add("cover-gasket", at(0, 0, 0), explode=ex(6, 90))
add("cover", at(0, 0, 0), groups=["cover"])
seal_x = T.COVER_INNER + T.COVER_T - 1.0
add("cover-seal", at(seal_x, ky, kz), groups=["cover"])
for k, (y, z) in enumerate(T.COVER_SCREWS):
    add("cover-screw", at(T.PANEL_FACE + 0.4 + T.COVER_T, y, z, ry=-90), explode=ex(4, 70), label=k == 0)

# ---- crankshaft pulley ------------------------------------------------------------------------------
pulley_x = T.CRANK_HUB_X + crank_hub + 5.2
pulley_l = SP["engine.timing.crank-pulley"].nom("hub_length")
pl_t = SP["engine.timing.pulley-lockwasher"].nom("thickness")
add("crank-pulley", at(pulley_x, ky, kz), explode=ex(2, 300))
add("pulley-lockwasher", at(pulley_x + pulley_l, ky, kz, ry=90), explode=ex(1, 330))
add("pulley-bolt", at(pulley_x + pulley_l + pl_t, ky, kz, ry=-90), explode=ex(1, 380))

INSTANCES = I
