"""Cylinder head assembly, Haynes Fig 1.6 (with Fig 1.5 layout and Fig 1.9 valve gear).

Positions come from mgb.head_layout (head frame: joint face z = 0, front +X,
manifold side +Y). Explode stages follow the Haynes removal procedure:
  Sec 12  spark plugs, thermostat housing                       orders 1-2
  Sec 10  rocker cover, gasket, rocker bracket nuts, rocker gear orders 1-5
  Sec 11  rocker gear dismantled along the shaft                 order 6
  Sec 12  head nuts, head lifted off, gasket                     orders 7-9
  Sec 13  clips, collets, caps, springs, collars; valves out     orders 19-20
  Sec 32  valve guides                                           order 21
"""
import math
from pathlib import Path

from build123d import Location, Rot

from mgb import spec as S
from mgb.head_layout import layout

ID = "engine.head"
NAME = "Cylinder head"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.6"}, {"figure": "1.9"}, {"figure": "1.5"}], "section": 12}

SPECS = Path(__file__).resolve().parent.parent / "specs" / "engine" / "head"
CAST = S.load(SPECS / "casting.yaml")
GEAR = {s.id: s for s in S.load_file(SPECS / "valve-gear.yaml")}
ROCK = {s.id: s for s in S.load_file(SPECS / "rocker-gear.yaml")}
LAY = layout(CAST)

UP = [0, 0, 1]
# The head casting stays still (as in Fig 1.6); everything else leaves it.
GROUPS = {
    "cover": {"axis": UP, "order": 2, "distance_mm": 360},
    "rocker-gear": {"axis": [0, 0.85, 1], "order": 5, "distance_mm": 270},   # up and back, clear of the valves
    "thermostat": {"axis": [0.6, 0, 1], "order": 2, "distance_mm": 60},
}
DOWN = [0, 0, -1]


def up(order, d):
    return {"axis": UP, "order": order, "distance_mm": d}


def at(x, y, z, rx=0, ry=0, rz=0):
    return Location((x, y, z)) * Rot(rx, ry, rz)


I = []   # (instance id, part id, location, options)
_n = {}


def add(part, loc, **opts):
    pid = "engine.head." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, opts))


TOP = LAY.top_z
HEAD = {}   # parts that stay in the head casting

# ---- casting, gasket, studs in the block -----------------------------------
add("casting", at(0, 0, 0), **HEAD)
add("gasket", at(0, 0, -1.6), explode={"axis": DOWN, "order": 9, "distance_mm": 60})
for num, x, y, kind in LAY.head_studs:
    if kind == "pedestal":
        add("head-stud-long", at(x, y, -20), explode={"axis": DOWN, "order": 9, "distance_mm": 170})
    else:
        add("head-stud", at(x, y, -20), explode={"axis": DOWN, "order": 9, "distance_mm": 170})
        add("head-washer", at(x, y, TOP), explode=up(7, 45))
        add("head-nut", at(x, y, TOP + 1.65), explode=up(7, 60))

# ---- valves and valve gear (Fig 1.9) ------------------------------------------
seat_z = LAY.chamber_depth                      # valve combustion face
tip_z = seat_z + 115.0                          # derived valve length
collar_z = TOP
spring_z = collar_z + 1.6
cap_z = spring_z + GEAR["engine.head.spring-outer"].nom("fitted_length")
collet_z = tip_z - 4.0 - 3.2 - 2.6              # bead centred in the groove
for v in LAY.valves:
    k = "inlet" if v.kind == "inlet" else "exhaust"
    g = GEAR[f"engine.head.guide-{k}"]
    add(f"valve-{k}", at(v.x, v.y, seat_z), **HEAD)
    add(f"guide-{k}", at(v.x, v.y, TOP + 15.875 - g.nom("length")), **HEAD)
    add("spring-collar", at(v.x, v.y, collar_z), **HEAD)
    add("valve-shroud", at(v.x, v.y, spring_z), **HEAD)
    add("spring-outer", at(v.x, v.y, spring_z), **HEAD,
        build={"length": GEAR["engine.head.spring-outer"].nom("fitted_length")})
    add("spring-inner", at(v.x, v.y, spring_z + 1.5), **HEAD,
        build={"length": GEAR["engine.head.spring-inner"].nom("fitted_length")})
    add("packing-ring", at(v.x, v.y, collet_z - 1.9), **HEAD)
    add("spring-cap", at(v.x, v.y, cap_z), **HEAD)
    add("collet", at(v.x, v.y, collet_z), **HEAD)
    add("collet", at(v.x, v.y, collet_z, rz=180), **HEAD, label=False)
    add("valve-clip", at(v.x, v.y, collet_z + 8.6), **HEAD)

# ---- rocker gear (Sec 10, 11) -------------------------------------------------
shaft_z = TOP + ROCK["engine.head.rocker-bracket"].nom("height_to_shaft_centre")
sy = LAY.shaft_y
RG = ["rocker-gear"]
half = ROCK["engine.head.rocker-shaft"].nom("length") / 2


def along(x, order=6, extra=15.0):
    """Rocker gear slides off the shaft: parts move outward along X."""
    return {"axis": [1 if x >= 0 else -1, 0, 0], "order": order, "distance_mm": 0.45 * abs(x) + extra}


add("rocker-shaft", at(0, sy, shaft_z), groups=RG, explode=None)
add("rocker-shaft-plug-plain", at(-half + 3.0, sy, shaft_z), groups=RG, explode=along(-half, 6, 30))
add("rocker-shaft-plug-screwed", at(half - 3.5, sy, shaft_z), groups=RG, explode=along(half, 6, 30))
for c, x in enumerate(LAY.cyl_x, start=1):
    part = "rocker-bracket-locating" if c == 2 else "rocker-bracket"
    add(part, at(x, sy, TOP), groups=RG, explode=along(x))
    base_top = TOP + 9.0
    hy, ssy = LAY.pushrod_y, LAY.short_stud_y
    add("rocker-bracket-washer", at(x, hy, base_top), explode=up(4, 80))
    add("rocker-bracket-spring-washer", at(x, hy, base_top + 1.65), explode=up(4, 92))
    add("rocker-bracket-nut", at(x, hy, base_top + 1.65 + 2.8), explode=up(4, 105))
    add("rocker-stud-short", at(x, ssy, TOP - 12), **HEAD)
    add("rocker-bracket-washer-small", at(x, ssy, base_top), explode=up(4, 80))
    add("rocker-bracket-nut-small", at(x, ssy, base_top + 1.65), explode=up(4, 95))
for v in LAY.valves:
    add("rocker", at(v.x, sy, shaft_z), groups=RG, explode=along(v.x))
    add("rocker-bush", at(v.x, sy, shaft_z), groups=RG, explode=along(v.x, 6, 15))
    boss_top = shaft_z
    add("rocker-adjusting-screw", at(v.x, LAY.pushrod_y, boss_top - 14 - 6), groups=RG, explode=along(v.x, 6, 15))
    add("rocker-adjuster-locknut", at(v.x, LAY.pushrod_y, boss_top), groups=RG, explode=along(v.x, 6, 15))
for x in (LAY.pitch, 0.0, -LAY.pitch):
    add("rocker-spacing-spring", at(x, sy, shaft_z), groups=RG, explode=along(x, 6, 25),
        build={"length": ROCK["engine.head.rocker-spacing-spring"].nom("fitted_length")})
loc_x = LAY.cyl_x[1]
add("rocker-lockplate", at(loc_x, sy, shaft_z + 15.0), groups=RG, explode=up(5.5, 30))
add("rocker-locating-screw", at(loc_x, sy, shaft_z + 15.9), groups=RG, explode=up(5.5, 45))
outer = LAY.valves[0].x + ROCK["engine.head.rocker"].nom("hub_width") / 2
for s in (1, -1):
    x0 = s * outer
    add("rocker-shaft-washer", at(x0, sy, shaft_z, ry=90 * s), groups=RG, explode=along(x0, 6, 40))
    add("rocker-shaft-spring-washer", at(x0 + s * 1.0, sy, shaft_z, ry=90 * s), groups=RG, explode=along(x0, 6, 50))
    add("rocker-shaft-split-pin", at(s * (half - 1.2), sy, shaft_z, rz=90), groups=RG, explode=along(x0, 6, 65))

# ---- rocker cover (Sec 10) ----------------------------------------------------
ccx, ccy = -2.5, 35.0
add("rocker-cover-gasket", at(ccx, ccy, TOP), explode=up(3, 260))
add("rocker-cover", at(ccx, ccy, TOP + 5.0), groups=["cover"], explode=None)
add("filler-cap", at(ccx + 140.0, ccy, TOP + 5.0 + 95.0 + 2.0), groups=["cover"], explode=up(3.5, 40))
cover_top = TOP + 5.0 + 95.0
for x, y in LAY.cover_studs:
    add("cover-stud", at(x, y, TOP - 12), **HEAD)
    add("rocker-cover-bush", at(x, y, cover_top - 6), groups=["cover"], explode=up(1, 25))
    add("rocker-cover-washer", at(x, y, cover_top + 3), groups=["cover"], explode=up(1, 45))
    zn = cover_top + 7.6
    if x < 0:
        add("rocker-cover-bracket", at(x, y, zn), groups=["cover"], explode=up(1, 60))
        zn += 1.6
    add("rocker-cover-nut", at(x, y, zn), groups=["cover"], explode=up(1, 80))

# ---- thermostat housing (Sec 12) ------------------------------------------------
tx, ty = LAY.thermostat
z = TOP + 6
TH = ["thermostat"]
add("thermostat-gasket", at(tx, ty, z), groups=TH, explode=up(2.2, 10))
add("thermostat-distance-piece", at(tx, ty, z + 0.8), groups=TH, explode=up(2.2, 25))
add("thermostat", at(tx, ty, z + 12.8), groups=TH, explode=up(2.2, 60))
add("thermostat-gasket", at(tx, ty, z + 14.0), groups=TH, explode=up(2.2, 75), label=False)
add("water-outlet-elbow", at(tx, ty, z + 14.8), groups=TH, explode=up(2.2, 95))
for k in range(3):
    a = math.radians(90 + 120 * k)
    sx, syy = tx + 26 * math.cos(a), ty + 26 * math.sin(a)
    add("thermostat-stud", at(sx, syy, TOP - 8), **HEAD)
    add("thermostat-washer", at(sx, syy, z + 22.8), explode=up(1, 70))
    add("thermostat-nut", at(sx, syy, z + 24.45), explode=up(1, 85))

# ---- spark plugs: axis tilted 57 deg from vertical toward the right-hand side ----
for x, y, zz in LAY.plugs:
    seat = (x, LAY.y_min - 4.0, 37.7)
    u = (0, -0.839, 0.544)
    add("spark-plug-gasket", at(*seat, rx=57), explode={"axis": list(u), "order": 1, "distance_mm": 45})
    add("spark-plug", at(seat[0], seat[1] + 1.6 * u[1], seat[2] + 1.6 * u[2], rx=57),
        explode={"axis": list(u), "order": 1, "distance_mm": 80})

# ---- manifold studs, plugs, blanking plate --------------------------------------
for x, zz, kind in LAY.manifold_studs:
    add("manifold-stud" if kind == "centre" else "manifold-stud-end", at(x, LAY.y_max - 16, zz, rx=-90),
        explode={"axis": [0, 1, 0], "order": 7, "distance_mm": 45})
RX, FX = [-1, 0, 0], [1, 0, 0]
add("core-plug", at(LAY.x_min + 4.0, 10.0, 35.0, ry=-90), explode={"axis": RX, "order": 7, "distance_mm": 35})
add("screwed-plug-washer", at(LAY.x_max, 55.0, 35.0, ry=90), explode={"axis": FX, "order": 7, "distance_mm": 25})
add("screwed-plug", at(LAY.x_max + 1.5, 55.0, 35.0, ry=90), explode={"axis": FX, "order": 7, "distance_mm": 45})
add("blanking-plate-gasket", at(LAY.x_min, -25.0, 45.0, ry=-90), explode={"axis": RX, "order": 7, "distance_mm": 15})
add("blanking-plate", at(LAY.x_min - 0.8, -25.0, 45.0, ry=-90), explode={"axis": RX, "order": 7, "distance_mm": 30})
for dz in (-10.0, 10.0):
    add("blanking-plate-spring-washer", at(LAY.x_min - 2.8, -25.0, 45.0 + dz, ry=-90),
        explode={"axis": RX, "order": 7, "distance_mm": 45})
    add("blanking-plate-screw", at(LAY.x_min - 4.4, -25.0, 45.0 + dz, ry=90),
        explode={"axis": RX, "order": 7, "distance_mm": 62})

INSTANCES = I
