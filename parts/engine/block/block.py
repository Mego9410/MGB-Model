"""Cylinder block casting and its small fittings. Haynes Fig 1.8.

The casting is built directly in the engine frame (see mgb.engine_layout):
deck at z = -1.6, front +X, manifold/camshaft side +Y.
"""
import math
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Location, Part, Plane, RegularPolygon, Rot, extrude, fillet

from mgb import engine_layout as E, fasteners as F, probes, shapes as Sh, spec as S
from mgb.head_layout import layout as head_layout

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
ROOT = Path(__file__).resolve().parents[3]
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)


def _l(p, spec):
    p.label = spec.id
    return p


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=BASE).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))


def xcyl(r, x0, x1, y, z):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _text(label, size, depth):
    """Raised cast lettering, or nothing if no font is available."""
    try:
        from build123d import Text, extrude
        return extrude(Text(label, font_size=size), depth)
    except Exception:  # noqa: BLE001 - lettering is decoration only
        return None


from mgb.block_section import (CHEST_Z0, CHEST_Z1, FLANGE_HW, FUEL_PUMP_Z, LEDGE_Z, LEFT_KNEE_Z,  # noqa: E402
                                LETTER_Z, OPEN_H, OPEN_L, PLUG7_Z, RELIEF_Z, YL, YR, YR_LOW, YW, section, wall_y)


def _section(d=0.0):
    return section(EL.deck_z, EL.sump_z, d)


def _prism(points, x0, x1):
    from build123d import Plane, Polygon
    return extrude(Plane.YZ.offset(x0) * Polygon(*points, align=None), x1 - x0, dir=(1, 0, 0))


def _rounded_box(x0, x1, y0, y1, z0, z1, r, axis=Axis.Y):
    b = box(x0, x1, y0, y1, z0, z1)
    try:
        return fillet(b.edges().filter_by(axis), r)
    except Exception:  # noqa: BLE001 - fall back to a sharp box
        return b


def _yboss(r, x, z, y0, y1):
    """Round boss with its axis across the engine (along Y), from y0 to y1."""
    lo, hi = sorted((y0, y1))
    return Cylinder(r, hi - lo, rotation=(90, 0, 0)).moved(Location((x, (lo + hi) / 2, z)))


def casting(spec) -> Part:
    """Cylinder block casting. Sizes from the specs; the external form is derived (D).

    Sources for the form: Haynes Fig 1.8 (left side: proud tappet chest with two
    openings, cam tunnel shelf under it, oil pump drive pillar, fuel pump flange,
    "1800" panel, relief valve boss at the left rear - Sec 17), Haynes photo 58.4 and
    owners' photos (right side: engine number plate below the deck, side core plugs,
    gallery ledge with the distributor boss, oil filter pad, ribbed sump flange).
    """
    deck, cz, sz = EL.deck_z, EL.crank_z, EL.sump_z
    x0, x1 = -spec.nom("length") / 2, spec.nom("length") / 2
    blk = _prism(_section(), x0, x1)
    try:                                                          # cast edges, not machined ones
        blk = fillet(blk.edges().filter_by(Axis.X).filter_by_position(Axis.Z, EL.sump_z + 5, LEDGE_Z + 1), 5.0)
    except Exception:  # noqa: BLE001 - keep sharp edges if the kernel refuses
        pass

    # deck flange: a shallow machined lip round the top
    lip = box(x0 - 1.5, x1 + 1.5, YR - 2.5, YL + 2.5, deck - 9, deck)
    blk = blk + fillet(lip.edges().filter_by(Axis.Z), 8.0)
    # front face flange and the deeper rear flange that carries the engine back plate
    blk = blk + _prism(_section(3.0), x1 - 7, x1)
    rear = _prism(_section(9.0), x0, x0 + 11)
    try:
        rear = fillet(rear.edges().filter_by(Axis.X), 6.0)
    except Exception:  # noqa: BLE001
        pass
    blk = blk + rear
    # sump flange with buttress ribs up to the walls (the pocketed rail in the photos)
    rail = box(x0, x1, -FLANGE_HW, FLANGE_HW, sz, sz + 10)
    blk = blk + fillet(rail.edges().filter_by(Axis.Z), 8.0)
    band = _prism(_section(7.0), x0 + 4, x1 - 4) & box(x0, x1, -200, 200, sz + 30, sz + 37)
    blk = blk + band                                              # upper rail of the pocketed flange
    nrib = 8
    for k in range(nrib + 1):
        rx = x0 + 20 + k * (x1 - x0 - 40) / nrib
        for sgn in (-1, 1):
            w0 = abs(wall_y(sz + 37, sgn)) - 2
            rib = _prism([(sgn * w0, sz + 37), (sgn * (w0 + 9), sz + 37), (sgn * FLANGE_HW, sz + 10), (sgn * w0, sz + 10)],
                         rx - 3.5, rx + 3.5)
            blk = blk + rib
    # main bearing webs: vertical ribs on both crankcase walls
    for mx in EL.main_x:
        lt, lb = wall_y(LEFT_KNEE_Z, 1), wall_y(sz + 10, 1)
        blk = blk + _prism([(lt - 4, LEFT_KNEE_Z), (lt + 3, LEFT_KNEE_Z + 6), (lb + 4, sz + 10), (lb - 6, sz + 10)], mx - 13, mx + 13)
        rt, rb = wall_y(LEDGE_Z - 14, -1), wall_y(sz + 10, -1)
        blk = blk + _prism([(rt + 4, LEDGE_Z - 14), (rt - 3, LEDGE_Z - 14), (rb - 4, sz + 10), (rb + 6, sz + 10)], mx - 13, mx + 13)

    # ---- left side ---------------------------------------------------------------------
    cy = EL.chest_y
    panel = _rounded_box(x0 + 30, x1 - 36, YL - 2, cy, CHEST_Z1, CHEST_Z0, 10.0, Axis.Y)
    blk = blk + panel
    for cx in (HL.pitch, -HL.pitch):                       # gasket faces round the openings
        face = _rounded_box(cx - OPEN_L / 2 - 8, cx + OPEN_L / 2 + 8, cy - 1, cy + 1.5,
                            EL.chest_z - OPEN_H / 2 - 8, EL.chest_z + OPEN_H / 2 + 8, 14.0)
        blk = blk + face
    blk = blk + xcyl(32.0, x0 + 16, x1 - 16, EL.cam_y, EL.cam_z)   # cam tunnel shelf under the chest
    # oil pump drive pillar under the skew gear
    py = wall_y(-250, 1)
    pillar = Cylinder(17, EL.cam_z + 4 - (-262), align=BASE).moved(Location((EL.drive_x, py - 6, -262)))
    blk = blk + pillar + box(EL.drive_x - 17, EL.drive_x + 17, py - 14, py + 4, -272, -254)
    # fuel pump flange (blanked on the MGB) and its stud, Fig 1.8 item 12
    fp = _rounded_box(60, 108, wall_y(FUEL_PUMP_Z, 1) - 4, wall_y(FUEL_PUMP_Z, 1) + 9, FUEL_PUMP_Z - 17, FUEL_PUMP_Z + 17, 9.0)
    blk = blk + fp
    # "1800" panel near the front
    lz = LETTER_Z
    blk = blk + box(118, 188, YL - 4, wall_y(lz[0], 1) + 3, *lz)
    # relief valve boss at the left rear (Haynes Sec 17), and the rear flange pad with stud 13
    blk = blk + _yboss(15.0, -178, RELIEF_Z, 92, wall_y(RELIEF_Z, 1) + 12)
    blk = blk + _yboss(11.0, -178, PLUG7_Z, 92, wall_y(PLUG7_Z, 1) + 8)      # plug 7 boss, beside the relief valve
    blk = blk + _rounded_box(-216, -186, YL - 4, YL + 7, -170, -140, 6.0)
    # drain tap boss at the front of the left side, Fig 1.8 item 21
    blk = blk + _yboss(11.0, x1 - 18, -48, YL - 4, YL + 6)

    # ---- right side --------------------------------------------------------------------
    blk = blk + xcyl(10.0, x0 + 14, x1 - 14, YR - 6, LEDGE_Z - 4)        # main oil gallery along the ledge
    blk = blk + box(-48, 48, YR - 2.5, YR + 1, -36, -14)                 # engine number plate pad
    for px in (-160.0, -27.0):                                            # side core plug rings
        blk = blk + _yboss(25.0, px, -64, YR + 2, YR - 3)
    for px in (67.0, 124.0):                                              # small threaded bosses
        blk = blk + _yboss(11.0, px, -44, YR + 2, YR - 7)
    # distributor housing boss on the ledge, leaning out like the distributor it carries
    dist = Location((EL.drive_x, YR - 15, LEDGE_Z + 10)) * Rot(22, 0, 0) * Cylinder(21, 64)
    blk = blk + dist + _rounded_box(EL.drive_x + 22, EL.drive_x + 44, YR - 10, YR + 1, -108, -86, 5.0)
    # oil filter pad below the ledge, dipstick boss ahead of it
    fz = -185.0
    blk = blk + _rounded_box(-62, 2, wall_y(fz, -1) - 9, wall_y(fz, -1) + 6, fz - 24, fz + 24, 8.0)
    from mgb import lube_layout as LL
    dpl = Plane(origin=LL.DIPSTICK_ENTRY, z_dir=LL.DIPSTICK_DIR).location     # dipstick boss along the stick
    blk = blk + dpl * Cylinder(9.0, 22).moved(Location((0, 0, -4)))
    blk = blk + _yboss(10.0, -205, -232, wall_y(-232, -1) + 4, wall_y(-232, -1) - 10)   # oil pipe union boss
    blk = blk + box(x1 - 24, x1, YR - 22, YR, -75, -40)                  # alternator bracket lug

    lettering = _text("1800", 22, 1.6)
    if lettering is not None:   # reads front to back from the left side, raised outward
        lx = wall_y(lz[0], 1) + 3
        blk = blk + (Plane(origin=(153, lx, (lz[0] + lz[1]) / 2), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)).location * lettering)

    cut = []
    bore = spec.nom("bore")
    for x in EL.cyl_x:                                            # cylinder bores
        cut.append(Cylinder(bore / 2, 170, align=BASE).moved(Location((x, 0, deck - 168))))
        for dx in (-30, 30):                                      # deck water holes, matching the head
            cut.append(Cylinder(5, 20, align=BASE).moved(Location((x + dx, -50, deck - 19))))
    # crankcase cavities between the webs; walls stay about 10 mm thick
    cav = [(-YW + 10, sz - 1), (YW - 10, sz - 1), (YW - 10, sz + 10), (YL - 10, LEFT_KNEE_Z),
           (YL - 10, -160), (YR_LOW + 5, -160), (-YW + 10, sz + 10)]
    for a, b in ((22, 190), (-190, -22)):
        cut.append(_prism(cav, a, b))
    for mx in EL.main_x:                                          # main bearing saddles and cap seats
        cut.append(xcyl(28.8, mx - 20, mx + 20, 0, cz))
        cut.append(box(mx - 16, mx + 16, -60, 60, sz - 1, cz))
    cut.append(xcyl(24.75, x0 - 1, x1 + 1, EL.cam_y, EL.cam_z))   # camshaft tunnel
    for tx, ty in EL.tappet_xy:                                   # tappet bores and pushrod holes
        cut.append(Cylinder(10.35, 72, align=BASE).moved(Location((tx, ty, EL.cam_z + 4))))
        cut.append(Cylinder(7.5, -deck - EL.cam_z, align=BASE).moved(Location((tx, ty, EL.cam_z + 60))))
    for cx in (HL.pitch, -HL.pitch):                              # tappet chest openings
        op = _rounded_box(cx - OPEN_L / 2, cx + OPEN_L / 2, 58, cy + 4, EL.chest_z - OPEN_H / 2, EL.chest_z + OPEN_H / 2, 10.0)
        cut.append(op)
    for _, x, y, _ in HL.head_studs:                              # tapped head stud holes
        cut.append(Cylinder(5.6, 32, align=BASE).moved(Location((x, y, deck - 31))))
    for px in (-160.0, -27.0):                                    # core plugs, seated in their rings
        cut.append(_yboss(20.6, px, -64, YR + 6, YR - 4))
    for px in (67.0, 124.0):
        cut.append(_yboss(5.0, px, -44, YR + 4, YR - 9))
    cut.append(Location((EL.drive_x, YR - 15, LEDGE_Z + 10)) * Rot(22, 0, 0) * Cylinder(14.3, 70))   # distributor bore
    cut.append(dpl * Cylinder(3.4, 60))                                                          # dipstick hole
    cut.append(_yboss(5.5, -205, -232, wall_y(-232, -1) + 6, wall_y(-232, -1) - 12))             # oil pipe union
    for x, y in LL.sump_bolts():                                                                 # tapped sump bolt holes
        cut.append(Cylinder(3.6, 14, align=BASE).moved(Location((x, y, sz - 1))))
    cut.append(_yboss(6.4, -178, RELIEF_Z, 92, 130))
    cut.append(_yboss(5.6, -178, PLUG7_Z, 92, 130))                                                 # relief valve bore
    cut.append(_yboss(6.4, x1 - 18, -48, YL - 10, YL + 8))                                       # drain tap thread
    cut.append(Cylinder(5, 30, rotation=(0, 90, 0)).moved(Location((x1 - 12, YR - 11, -57))))   # bracket lug hole
    cut.append(Cylinder(14, 30, rotation=(90, 0, 0)).moved(Location((-30, wall_y(fz, -1), fz)))) # oil filter feed
    for dz in (-15, 15):
        cut.append(_yboss(3.9, -30 + dz * 1.4, fz + dz * 0.3, wall_y(fz, -1) + 2, wall_y(fz, -1) - 12))
    fy = wall_y(FUEL_PUMP_Z, 1)
    for sx in (70, 98):                                          # fuel pump flange stud holes
        cut.append(_yboss(3.2, sx, FUEL_PUMP_Z, fy - 6, fy + 12))
    cut.append(_yboss(14.0, 84, FUEL_PUMP_Z, fy - 8, fy + 12))          # pump arm aperture (blanked)
    cut.append(_yboss(3.9, -201, -155, YL - 6, YL + 10))          # stud 13 hole
    cut.append(_yboss(3.9, EL.drive_x + 33, -97, YR - 12, YR + 4))  # distributor housing clamp bolt
    for c in cut:
        blk = blk - c
    # oil pump pad inside the crankcase at the foot of the drive pillar, with the drive bore
    fx, fy = LL.PUMP_FLANGE
    pad = _rounded_box(fx - 34, fx + 30, fy - 30, YW - 2, sz, LL.PUMP_PAD_Z, 10.0, Axis.Z)
    blk = blk + pad
    blk = blk - Cylinder(7.0, EL.cam_z - sz, align=BASE).moved(Location((LL.DRIVE_X, LL.DRIVE_Y, sz - 1)))
    for px_, py_ in LL.pump_studs():
        blk = blk - Cylinder(3.6, 16, align=BASE).moved(Location((px_, py_, sz - 1)))
    for cx in (HL.pitch, -HL.pitch):                              # cover bolt bosses inside the chest
        blk = blk + _yboss(8.0, cx, EL.chest_z, 50, cy - 8)
        blk = blk - _yboss(3.9, cx, EL.chest_z, 84, cy)
    return _l(blk, spec)


def cup_plug(spec) -> Part:
    d, h = spec.nom("diameter"), spec.nom("depth")
    return _l(Sh.revolved([(0, 0), (d / 2 - 0.8, 0), (d / 2, 1.0), (d / 2, h), (d / 2 - 1.2, h),
                           (d / 2 - 1.2, 1.4), (0, 2.2)]), spec)


def pin_plug(spec) -> Part:
    d, L = spec.nom("diameter"), spec.nom("length")
    p = Sh.chamfered_cyl(d, L, 0.6) - Sh.cyl(d * 0.35, 3, z0=L - 2.5).moved(Location((0, 0, 0)))
    return _l(p, spec)


def hex_plug(spec) -> Part:
    d, af = spec.nom("thread_diameter"), spec.nom("hex_across_flats")
    return _l(extrude(RegularPolygon(af / math.sqrt(3), 6), 8) + Sh.cyl(d, 12, z0=-12), spec)


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t) - Box(1.0, od, t * 3).moved(Location((0, od / 2, 0))), spec)


def stud(spec) -> Part:
    d, L = spec.nom("thread_diameter"), spec.nom("length")
    return _l(Sh.chamfered_cyl(d, L, d * 0.12), spec)


def nut(size):
    return lambda spec: _l(F.hex_nut(size), spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def cam_bearing(spec) -> Part:
    L, od, id_ = spec.nom("length"), spec.nom("outside_diameter"), spec.nom("inside_diameter")
    return _l(Rot(0, 90, 0) * Sh.tube(od, id_, L, z0=-L / 2), spec)


def cap_seal(spec) -> Part:
    L, s = spec.nom("length"), spec.nom("section")
    return _l(Box(s, L, s, align=BASE), spec)


def dowel(spec) -> Part:
    return _l(Sh.chamfered_cyl(spec.nom("diameter"), spec.nom("length"), 0.8), spec)


def drain_tap(spec) -> Part:
    d, L = spec.nom("body_diameter"), spec.nom("length")
    body = Sh.cyl(d, L * 0.6) + Sh.cyl(d * 0.8, L * 0.4, z0=-L * 0.4)
    spout = Cylinder(3.5, 16, rotation=(0, 90, 0)).moved(Location((8, 0, L * 0.25)))
    lever = Box(4, 28, 3, align=BASE).moved(Location((0, 0, L * 0.6)))
    return _l(body + spout + lever, spec)


NUT = {"across_flats": F.across_flats, "thickness": lambda p: probes.bbox_size(p, "z")}
WASH = {"outside_diameter": lambda p: probes.bbox_size(p, "x"), "thickness": lambda p: probes.bbox_size(p, "z")}
BEARING_ID = {"inside_diameter": lambda p: min(d for d, _ in probes.cylinder_diameters(p))}

PARTS = {
    "engine.block.casting": {"build": casting},
    "engine.block.core-plug-rear": {"build": cup_plug},
    "engine.block.plug-gallery": {"build": pin_plug},
    "engine.block.plug-small": {"build": pin_plug},
    "engine.block.plug-rear-lower": {"build": pin_plug},
    "engine.block.plug-front": {"build": pin_plug},
    "engine.block.plug-side": {"build": hex_plug},
    "engine.block.plug-side-washer": {"build": washer},
    "engine.block.main-cap-stud-rear": {"build": stud},
    "engine.block.stud-side": {"build": stud},
    "engine.block.stud-rear": {"build": stud},
    "engine.block.main-cap-stud": {"build": stud},
    "engine.block.main-cap-washer": {"build": washer, "probes": WASH},
    "engine.block.main-cap-nut": {"build": nut("7/16"), "probes": NUT},
    "engine.block.cam-bearing-front": {"build": cam_bearing, "probes": BEARING_ID},
    "engine.block.cam-bearing-centre": {"build": cam_bearing, "probes": BEARING_ID},
    "engine.block.cam-bearing-rear": {"build": cam_bearing, "probes": BEARING_ID},
    "engine.block.main-cap-seal": {"build": cap_seal},
    "engine.block.dowel-rear": {"build": dowel},
    "engine.block.dowel-front": {"build": dowel},
    "engine.block.drain-tap": {"build": drain_tap},
    "engine.block.drain-tap-washer": {"build": washer},
    "engine.block.front-plate-screw": {"build": bolt("5/16")},
    "engine.block.front-plate-spring-washer": {"build": spring_washer},
    "engine.block.front-plate-bolt": {"build": bolt("5/16")},
    "engine.block.front-plate-nut": {"build": nut("5/16"), "probes": NUT},
}
