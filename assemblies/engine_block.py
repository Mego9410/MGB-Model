"""Cylinder block and crank train, Haynes Fig 1.8 (with Fig 1.13 big-end parts).

Engine frame (mgb.engine_layout): X forward, Y to the car's left, Z up, head joint
face at z = 0. Shown at No 1 TDC on compression. Explode stages follow Haynes:
  head studs and covers off                                   orders 1-2
  Sec 24  big-end caps off; pistons and rods out of the top     orders 3-5
  Sec 25  main caps off; crankshaft out                        orders 6-8
  Sec 14  pushrods and tappets out                             order 9
  Sec 23  camshaft out of the front; bearings                  orders 10-11
"""
import math
from pathlib import Path

from build123d import Location, Plane, Rot, Vector

from mgb import block_section as BLK, engine_layout as E, spec as S
from mgb.head_layout import layout as head_layout

ID = "engine.block"
NAME = "Cylinder block and crank train"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.8"}, {"figure": "1.13"}], "section": 25}

ROOT = Path(__file__).resolve().parent.parent
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)
SP = {s.id: s for f in (ROOT / "specs" / "engine" / "block").glob("*.yaml") for s in S.load_file(f)}

UP, DOWN, FWD, BACK, LEFT, RIGHT = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
GROUPS = {f"piston-{c}": {"axis": UP, "order": 4, "distance_mm": 330} for c in range(1, 5)}
GROUPS.update({f"cap-{c}": {"axis": DOWN, "order": 3, "distance_mm": 95} for c in range(1, 5)})
GROUPS.update({f"main-{k}": {"axis": DOWN, "order": 7, "distance_mm": 150} for k in range(3)})
GROUPS["crank"] = {"axis": DOWN, "order": 8, "distance_mm": 330}
GROUPS["rear-plate"] = {"axis": BACK, "order": 1.6, "distance_mm": 150}


def ex(axis, order, d):
    return {"axis": axis, "order": order, "distance_mm": d}


def at(x, y, z, rx=0, ry=0, rz=0):
    return Location((x, y, z)) * Rot(rx, ry, rz)


def on_plane(origin, z_dir, x_dir=(1, 0, 0)):
    return Plane(origin=origin, x_dir=x_dir, z_dir=z_dir).location


I, _n = [], {}


def add(part, loc, **opts):
    pid = part if part.startswith("engine.") else "engine.block." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, opts))


cz, deck, sz = EL.crank_z, EL.deck_z, EL.sump_z
X0, X1 = -SP["engine.block.casting"].nom("length") / 2, SP["engine.block.casting"].nom("length") / 2

# ---- casting, head studs ---------------------------------------------------------
add("casting", at(0, 0, 0))
for num, x, y, kind in HL.head_studs:
    add("engine.head.head-stud-long" if kind == "pedestal" else "engine.head.head-stud", at(x, y, -20),
        explode=ex(UP, 1, 260))

# ---- crankshaft and main bearings -------------------------------------------------
add("crankshaft", at(0, 0, cz), groups=["crank"])
for k, mx in enumerate(EL.main_x):
    M = [f"main-{k}"]
    add("main-bearing-shell", at(mx, 0, cz), groups=M, explode=ex(DOWN, 7.5, 25))
    add("main-bearing-shell", at(mx, 0, cz, rx=180), groups=["crank"], explode=ex(UP, 8.5, 0.01), label=False)
    add("main-cap", at(mx, 0, cz), groups=M)
    studs = "main-cap-stud-rear" if k == 2 else "main-cap-stud"
    for sy in (-48, 48):
        add(studs, at(mx, sy, cz - 56), explode=ex(DOWN, 6.5, 230))
        add("main-cap-washer", at(mx, sy, cz - 43.65), explode=ex(DOWN, 6, 30))
        add("main-cap-nut", at(mx, sy, cz - 53.2), explode=ex(DOWN, 6, 45))
    if k in (0, 2):
        add("main-cap-seal", at(mx + (17 if k == 0 else -17), 0, cz - 30), groups=M, explode=ex(FWD if k == 0 else BACK, 7.5, 30))
for side in (-1, 1):
    xw = side * 16.2
    add("thrust-washer", at(xw, 0, cz), groups=["main-1"], explode=ex([side, 0, 0], 7.5, 25))
    add("thrust-washer", at(xw, 0, cz, rx=180), groups=["crank"], explode=ex([side, 0, 0], 8.5, 25), label=False)

# ---- pistons and connecting rods --------------------------------------------------
n = Vector(0, math.sin(math.radians(45)), math.cos(math.radians(45)))   # angular split normal
t = Vector(0, n.Z, -n.Y)
pitch = (47.655 + 2 * 1.6) / 2 + 7
GROOVE_BOTTOMS = [7.1, 11.3, 15.5, 22.1]   # below the crown: top, 2nd, 3rd, scraper
for c, x in enumerate(EL.cyl_x, start=1):
    a = math.radians(EL.pin_angle[c])
    pin = Vector(x, 0, cz + EL.throw * math.cos(a))
    pz = E.piston_z(EL, c)
    P, C = [f"piston-{c}"], [f"cap-{c}"]
    add("connecting-rod", at(pin.X, pin.Y, pin.Z), groups=P, explode=ex(DOWN, 5, 40))
    add("big-end-shell", at(pin.X, pin.Y, pin.Z, rx=180), groups=P, explode=ex(DOWN, 5, 20), label=c == 1)
    add("connecting-rod-cap", at(pin.X, pin.Y, pin.Z), groups=C)
    add("big-end-shell", at(pin.X, pin.Y, pin.Z), groups=C, explode=ex(DOWN, 3.5, 22), label=False)
    add("big-end-lockwasher", on_plane(pin - n * 17.9, -n, t), groups=C, explode=ex(DOWN, 2.6, 30))
    for s in (-1, 1):
        bolt_at = pin + t * (s * pitch) - n * 17.9
        add("big-end-bolt", on_plane(bolt_at, n), groups=C, explode=ex(DOWN, 2.5, 55))
    add("piston", at(x, 0, pz), groups=P)
    add("gudgeon-pin", at(x, 0, pz), groups=P, explode=ex(FWD if c <= 2 else BACK, 5, 75))
    add("gudgeon-clamp-bolt", at(x, 20.5, pz + 6, rx=90), groups=P, explode=ex(LEFT, 4.5, 45))
    crown = pz + E.COMPRESSION_HEIGHT
    for ring, zb, dz in (("piston-ring-top", GROOVE_BOTTOMS[0], 70), ("piston-ring-taper", GROOVE_BOTTOMS[1], 55),
                         ("piston-ring-taper", GROOVE_BOTTOMS[2], 40), ("piston-ring-scraper", GROOVE_BOTTOMS[3], 25)):
        add(ring, at(x, 0, crown - zb), groups=P, explode=ex(UP, 5, dz), label=c == 1)

# ---- camshaft, bearings, tappets, pushrods ----------------------------------------------
add("camshaft", at(0, EL.cam_y, EL.cam_z), explode=ex(FWD, 10, 330))
for name, x in zip(("cam-bearing-front", "cam-bearing-centre", "cam-bearing-rear"), EL.cam_journal_x):
    add(name, at(x, EL.cam_y, EL.cam_z), explode=ex(FWD, 11, 130))
cam_base_r = SP["engine.block.camshaft"].nom("base_circle_diameter") / 2
for tx, ty in EL.tappet_xy:
    tz = EL.cam_z + cam_base_r
    add("tappet", at(tx, ty, tz), explode=ex(LEFT, 9, 95))
    add("pushrod", at(tx, ty, tz + 6.0), explode=ex(UP, 9, 300))

# ---- tappet side covers (manifold side) ------------------------------------------------
TC = SP["engine.block.tappet-cover"]
gy = EL.chest_y + 1.5                                    # gasket face round each chest opening
for cx in (HL.pitch, -HL.pitch):
    add("tappet-cover-gasket", at(cx, gy, EL.chest_z), explode=ex(LEFT, 1.5, 25))
    add("tappet-cover", at(cx, gy + 3.0, EL.chest_z), explode=ex(LEFT, 1.5, 50))
    add("tappet-cover-bolt", at(cx, gy + 3.0 + TC.nom("depth"), EL.chest_z, rx=90), explode=ex(LEFT, 1, 80))

# ---- front plate (Fig 1.8 items 28-33) ------------------------------------------------------
_spec = __import__("importlib.util").util.spec_from_file_location("plates", ROOT / "parts" / "engine" / "block" / "plates.py")
PL = __import__("importlib.util").util.module_from_spec(_spec)
_spec.loader.exec_module(PL)
FP_T = SP["engine.block.front-plate"].nom("thickness")
add("front-plate-gasket", at(X1, 0, 0), explode=ex(FWD, 2, 30))
add("front-plate", at(X1 + 0.8, 0, 0), explode=ex(FWD, 2, 60))
for y, z in PL.FRONT_SCREWS:
    add("front-plate-spring-washer", at(X1 + 0.8 + FP_T, y, z, ry=90), explode=ex(FWD, 1, 70))
    add("front-plate-screw", at(X1 + 2.8 + FP_T, y, z, ry=-90), explode=ex(FWD, 1, 95))
by, bz = PL.FRONT_BOLT
add("front-plate-bolt", at(X1 + 0.8 + FP_T, by, bz, ry=-90), explode=ex(FWD, 1, 95))
add("front-plate-nut", at(X1 + 0.8, by, bz, ry=-90), explode=ex(BACK, 1, 40))

# ---- rear end plate (Haynes Sec 22 and 53) ---------------------------------------------------
RP_T = SP["engine.block.rear-plate"].nom("thickness")
RG_T = SP["engine.block.rear-plate-gasket"].nom("thickness")
rp_back = X0 - RG_T - RP_T                               # gearbox face of the plate
add("rear-plate-gasket", at(X0 - RG_T, 0, 0), groups=["rear-plate"], explode=ex(BACK, 1.8, 25))
add("rear-plate", at(rp_back, 0, 0), groups=["rear-plate"])
for sz_, pts in (("small", PL.REAR_SCREWS_5_16), ("large", PL.REAR_SCREWS_3_8)):
    tw = SP[f"engine.block.rear-plate-washer-{sz_}"].nom("thickness")
    for y, z in pts:
        add(f"rear-plate-washer-{sz_}", at(rp_back - 1.6 - tw, y, z, ry=90), explode=ex(BACK, 1.2, 70))
        add(f"rear-plate-screw-{sz_}", at(rp_back - 1.6 - tw, y, z, ry=90), explode=ex(BACK, 1.2, 110))
RT = SP["engine.block.rear-seal-retainer"].nom("thickness")
add("rear-seal-retainer", at(rp_back, 0, cz), explode=ex(BACK, 1.4, 60))
for k in range(6):
    a_ = math.radians(30 + 60 * k)
    add("rear-seal-retainer-bolt", at(rp_back - RT, PL.RETAINER_BOLT_R * math.cos(a_), cz + PL.RETAINER_BOLT_R * math.sin(a_), ry=90),
        explode=ex(BACK, 1.3, 90), label=k == 0)

# ---- plugs, dowels, studs, drain tap -------------------------------------------------------
add("core-plug-rear", at(X0 + 4, 0, -60, ry=-90), explode=ex(BACK, 1, 40))
add("plug-gallery", at(X0 + 6, 40, -160, ry=-90), explode=ex(BACK, 1, 40))
add("plug-small", at(X1 - 6, -50, -30, ry=90), explode=ex(FWD, 1, 40))
add("plug-small", at(X0 + 6, -80, -250, ry=-90), explode=ex(BACK, 1, 40))
for y in (-60, 60):
    add("plug-rear-lower", at(X0 + 6, y, -280, ry=-90), explode=ex(BACK, 1, 40))
add("plug-front", at(X1 - 6, 70, -200, ry=90), explode=ex(FWD, 1, 40))
# left rear, beside the relief valve boss (Fig 1.8 items 7 and 8); faces from the casting
py = BLK.wall_y(BLK.PLUG7_Z, 1) + 8
add("plug-side-washer", at(-178, py, BLK.PLUG7_Z, rx=-90), explode=ex(LEFT, 1, 25))
add("plug-side", at(-178, py + 1.5, BLK.PLUG7_Z, rx=-90), explode=ex(LEFT, 1, 45))
for y in (-90, 90):
    add("dowel-rear", at(X0 + 8, y, cz, ry=-90), explode=ex(BACK, 1, 35))
for y in (-80, 80):
    add("dowel-front", at(X1 - 8, y, -40, ry=90), explode=ex(FWD, 1, 35))
add("drain-tap-washer", at(X1 - 18, BLK.YL + 6, -48, rx=-90), explode=ex(LEFT, 1, 25))
add("drain-tap", at(X1 - 18, BLK.YL + 7.5, -48, rx=-90), explode=ex(LEFT, 1, 50))
add("stud-side", at(70, BLK.wall_y(BLK.FUEL_PUMP_Z, 1) + 3, BLK.FUEL_PUMP_Z, rx=-90), explode=ex(LEFT, 1, 50))
add("stud-rear", at(-201, BLK.YL + 1, -155, rx=-90), explode=ex(LEFT, 1, 50))

INSTANCES = I
