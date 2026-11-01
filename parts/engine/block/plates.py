"""Engine front plate (Haynes Fig 1.8 items 28-33) and engine rear end plate
(Haynes Sec 22, 42 and 53; photos 42.6(b) and 53.3).

Both plates are built in the engine frame's Y and Z (absolute), lying in the YZ plane
between x = 0 and x = thickness; the assembly only moves them along X.
  front plate: face toward the timing gear is +X
  rear plate:  face toward the block is +X, the gearbox side is -X
Outlines and hole patterns are derived (D) from the figure and photos; only the
screw sizes and torques are published.
"""
import math
from pathlib import Path

from build123d import Circle, Cylinder, Ellipse, Location, Part, Plane, Polygon, Pos, extrude

from mgb import block_section as B, engine_layout as E, fasteners as F, probes, shapes as Sh, spec as S, timing_layout as TL
from mgb.head_layout import layout as head_layout

ROOT = Path(__file__).resolve().parents[3]
HL = head_layout(S.load(ROOT / "specs" / "engine" / "head" / "casting.yaml"))
EL = E.layout(HL)
CZ, SZ, DECK = EL.crank_z, EL.sump_z, EL.deck_z

# ---- front plate ------------------------------------------------------------------------
# Outline traced from Fig 1.8 item 28, scaled so its camshaft hole lands on the camshaft:
# a wide right-hand wing for the engine mounting bracket, a notch in the top edge, and a
# scalloped left-hand edge round the timing cover joint.
FRONT_OUTLINE = [(-150, -16), (-40, -16), (-8, -50), (40, -38), (100, -52), (122, -70), (116, -108), (128, -150),
                 (119, -196), (130, -240), (121, -280), (110, -306), (60, -312), (-120, -312), (-136, -298),
                 (-150, -298)]
# raised (pressed) panel the timing cover seats against, and the cover's scalloped edge
TIMING_PANEL = TL.cover_outline(16.0)
FRONT_SCREWS = [(-50.0, -40.0), (88.0, -44.0), (-95.0, -290.0), (95.0, -290.0)]   # items 30/31, into the block
FRONT_BOLT = (-136.0, -30.0)                                                      # item 32 with nut 33 behind
TIMING_COVER_HOLES = TL.COVER_SCREWS
MOUNT_HOLES = [(-136, -150), (-136, -190), (-116, -150), (-116, -190)]
CRANK_OPENING = (-8.0, -245.0, 42.0, 58.0)    # centre y, z and half axes of the oval round the crank nose

# ---- rear end plate -----------------------------------------------------------------------
REAR_R = 182.0                                   # lower edge radius about the crank (flywheel housing)
STARTER = (-148.3, CZ - 70.0, 44.0)              # starter aperture, right-hand side: pinion on the 120-tooth ring (centre y, z, radius)
REAR_UPPER = [(-176, CZ + 40), (-150, -110), (-118, -40), (-60, -12), (0, -6), (60, -12), (118, -40), (150, -110),
              (176, CZ + 40), (0, CZ)]
REAR_SCREWS_5_16 = [(-58.0, -22.0), (92.0, -22.0), (-60.0, -110.0), (100.0, -110.0)]
REAR_SCREWS_3_8 = [(-100.0, -230.0), (100.0, -230.0), (-106.0, -290.0), (106.0, -290.0)]
BELL_HOLES = [(REAR_R - 10, a) for a in (150, 238, 270, 302, 335, 20)] + [(None, (-136, -96)), (None, (136, -96))]
DOWELS = [(-90.0, CZ), (90.0, CZ)]
SEAL_R = 40.0                                    # centre hole for the oil seal retaining plate
RETAINER_BOLT_R = 58.0


def _l(p, spec):
    p.label = spec.id
    return p


def _plate(points, t, x0=0.0):
    return extrude(Plane.YZ.offset(x0) * Polygon(*points, align=None), t, dir=(1, 0, 0))


def _xhole(r, y, z, x0=-5.0, x1=20.0):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _bell_points():
    pts = []
    for r, a in BELL_HOLES:
        if r is None:
            pts.append(a)
        else:
            pts.append((r * math.cos(math.radians(a)), CZ + r * math.sin(math.radians(a))))
    return pts


def front_plate(spec) -> Part:
    t = spec.nom("thickness")
    p = _plate(FRONT_OUTLINE, t) + _plate(TL.cover_outline(22.0), t)
    for y, z in TIMING_COVER_HOLES:                                      # scallops round the cover screws
        p = p + extrude(Plane.YZ * Pos(y, z) * Circle(10.0), t, dir=(1, 0, 0))
    p = p + _plate(TIMING_PANEL, 1.6, t - 0.01)                          # pressed timing cover seat
    p = p - _xhole(27.0, EL.cam_y, EL.cam_z)                             # camshaft
    p = p - extrude(Plane.YZ.offset(-5) * Pos(CRANK_OPENING[0], CRANK_OPENING[1])
                    * Ellipse(CRANK_OPENING[2], CRANK_OPENING[3]), 30, dir=(1, 0, 0))
    p = p - _xhole(12.0, -25.0, -95.0)                                   # small upper aperture
    for y, z in FRONT_SCREWS + [FRONT_BOLT]:
        p = p - _xhole(4.2, y, z)
    for y, z in TIMING_COVER_HOLES:
        p = p - _xhole(3.3, y, z)
    for y, z in MOUNT_HOLES:
        p = p - _xhole(5.2, y, z)
    for k in range(3):                                                   # camshaft locating plate bolts
        a = math.radians(90 + 120 * k)
        p = p - _xhole(3.6, EL.cam_y + 34 * math.cos(a), EL.cam_z + 34 * math.sin(a))
    (sy, sz), m = TL.tensioner_point()                                   # tensioner bolts
    v = TL.ROLLER_D / 2 + 1.0 + 44
    for u in (-24, 24):
        p = p - _xhole(4.2, sy - m[1] * u + m[0] * v, sz + m[0] * u + m[1] * v)
    return _l(p, spec)


def front_plate_gasket(spec) -> Part:
    """Joint between the plate and the block front face: the block outline, with the
    camshaft and crank openings and the screw holes."""
    t = spec.nom("thickness")
    g = _plate(B.section(DECK - 14, SZ + 2, 1.0), t)
    g = g - _xhole(30.0, EL.cam_y, EL.cam_z)
    g = g - extrude(Plane.YZ.offset(-5) * Pos(CRANK_OPENING[0], CRANK_OPENING[1])
                    * Ellipse(CRANK_OPENING[2] - 4, CRANK_OPENING[3] - 4), 30, dir=(1, 0, 0))
    for y, z in FRONT_SCREWS:
        g = g - _xhole(4.2, y, z)
    return _l(g, spec)


def _rear_outline(t, x0=0.0):

    disc = extrude(Plane.YZ.offset(x0) * Pos(0, CZ) * Circle(REAR_R), t, dir=(1, 0, 0))
    lobe = extrude(Plane.YZ.offset(x0) * Pos(STARTER[0], STARTER[1]) * Circle(STARTER[2] + 18), t, dir=(1, 0, 0))
    return disc + lobe + _plate(REAR_UPPER, t, x0)


def rear_plate(spec) -> Part:
    t = spec.nom("thickness")
    p = _rear_outline(t)
    # pressed dimples round the block screws, standing out on the gearbox side
    for y, z in REAR_SCREWS_5_16 + REAR_SCREWS_3_8:
        p = p + _xhole(11.0, y, z, -1.6, 0.01)
    # raised lip round the starter aperture
    p = p + _xhole(STARTER[2] + 6, STARTER[0], STARTER[1], -2.0, 0.01)
    p = p - _xhole(STARTER[2], STARTER[0], STARTER[1])
    p = p - _xhole(SEAL_R, 0.0, CZ)
    for y, z in REAR_SCREWS_5_16:
        p = p - _xhole(4.2, y, z)
    for y, z in REAR_SCREWS_3_8:
        p = p - _xhole(5.0, y, z)
    for y, z in _bell_points():                                          # gearbox bellhousing bolts
        p = p - _xhole(5.2, y, z)
    for y, z in DOWELS:
        p = p - _xhole(5.6, y, z)
    for k in range(6):                                                   # seal retaining plate bolts
        a = math.radians(30 + 60 * k)
        p = p - _xhole(4.2, RETAINER_BOLT_R * math.cos(a), CZ + RETAINER_BOLT_R * math.sin(a))
    return _l(p, spec)


def rear_plate_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = _plate(B.section(DECK, SZ, 8.0), t)
    g = g - _xhole(SEAL_R + 2, 0.0, CZ)
    for y, z in REAR_SCREWS_5_16:
        g = g - _xhole(4.2, y, z)
    for y, z in REAR_SCREWS_3_8:
        g = g - _xhole(5.0, y, z)
    for y, z in DOWELS:
        g = g - _xhole(5.6, y, z)
    return _l(g, spec)


def seal_retainer(spec) -> Part:
    """Early-engine oil seal retaining plate (Haynes photo 53.3): a lobed plate on the
    gearbox side of the end plate with a collar round the crankshaft tail."""

    t, od, id_ = spec.nom("thickness"), spec.nom("outside_diameter"), spec.nom("inside_diameter")
    p = extrude(Plane.YZ * Circle(od / 2), t, dir=(-1, 0, 0))
    for k in range(6):
        a = math.radians(30 + 60 * k)
        y, z = RETAINER_BOLT_R * math.cos(a), RETAINER_BOLT_R * math.sin(a)
        p = p + extrude(Plane.YZ * Pos(y, z) * Circle(11.0), t, dir=(-1, 0, 0))
        p = p - _xhole(4.2, y, z, -10, 5)
    p = p + _xhole(id_ / 2 + 8, 0, 0, -t - spec.nom("collar_length"), -t + 0.01)
    p = p - _xhole(id_ / 2, 0, 0, -40, 5)
    return _l(p, spec)


def screw(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def spring_washer(spec) -> Part:
    from build123d import Box
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t) - Box(1.0, od, t * 3).moved(Location((0, od / 2, 0))), spec)


WASH = {"outside_diameter": lambda p: probes.bbox_size(p, "x"), "thickness": lambda p: probes.bbox_size(p, "z")}

PARTS = {
    "engine.block.front-plate": {"build": front_plate},
    "engine.block.front-plate-gasket": {"build": front_plate_gasket},
    "engine.block.rear-plate": {"build": rear_plate},
    "engine.block.rear-plate-gasket": {"build": rear_plate_gasket},
    "engine.block.rear-seal-retainer": {"build": seal_retainer},
    "engine.block.rear-seal-retainer-bolt": {"build": screw("5/16")},
    "engine.block.rear-plate-screw-small": {"build": screw("5/16")},
    "engine.block.rear-plate-screw-large": {"build": screw("3/8")},
    "engine.block.rear-plate-washer-small": {"build": spring_washer},
    "engine.block.rear-plate-washer-large": {"build": spring_washer},
}

