"""Differential: cage, crown wheel and its bolts and lockwashers, side gears ("differential wheels"),
pinions on their shaft and peg, thrust washers, bearings and packing washers (Haynes Ch 8 Fig 8.1 items
18-29, printed p143; ratio 43/11, p142).

Drawn in the axle frame of mgb.rear_axle_layout. The cage turns on the axle axis (car y); the crown
wheel is bolted to the cage's flange on the left so the pinion, turning clockwise seen from the
front, drives the wheels forward. Side gears 16 teeth and pinions 10 (D), straight bevels; crown
wheel 43 teeth, spiral (hypoid) form.

Forms (Fig 8.1): cage item 20 - one-piece with two windows, bosses for the pinion shaft, the crown
wheel flange and spigot and two bearing hubs; crown wheel item 27 - a ring with curved teeth, tapped
for eight bolts; lockwashers item 29 - tab plates under pairs of bolt heads; side gears item 21 -
splined hubs; pinions item 23 with spherical backs on domed thrust washers item 24; pinion shaft
item 25 held by the peg item 26.
"""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Location, Part, Plane, Rot, Sphere, extrude

from mgb import bearings as BR, bevel as BV, fasteners as F, gears as GR, probes, rear_axle_layout as A, shapes as Sh
from parts.gearbox import casing as C
from parts.propshaft.shaft import ring, xcyl, ycyl

IN = 25.4
zc, box = C.zc, C.box
CROWN_PHASE = 0.0
SIDE_PHASE = 0.0
PLANET_PHASE = 0.0


def _l(p, spec):
    p.label = spec.id
    return p


def to_y(p):
    """A part drawn about +z, turned so its z runs along the car's +y (the axle axis)."""
    return Rot(-90, 0, 0) * p


def to_neg_y(p):
    return Rot(90, 0, 0) * p


# =================================================================================================
# crown wheel (27), bolts (28), lockwashers (29)
# =================================================================================================
def crown_bevel():
    return BV.Bevel(A.Z_CROWN, A.CROWN_PITCH_R, 90.0 - A.PITCH_ANGLE_PINION, A.FACE_W, 1.8, 6.5, spiral_deg=30.0, hand=1)


CROWN_BORE_R = 55.05


def crown_wheel(spec) -> Part:
    bv = crown_bevel()
    hb, ht = bv.cone_pt(0, -6.2), bv.cone_pt(A.FACE_W, -6.2)
    zb = -(A.CROWN_BACK_Y - A.CROWN_HEEL_Y)
    body = Sh.revolved([(CROWN_BORE_R, zb), (96.0, zb), (96.0, hb[1] - 2.5), (hb[0] + 0.6, hb[1]), (ht[0], ht[1]),
                        (ht[0] - 3.0, ht[1] - 3.0), (CROWN_BORE_R, ht[1] - 3.0)])
    g = BV.gear(bv, body, CROWN_PHASE)
    for k in range(A.CROWN_BOLTS):                                              # tapped bolt holes from the back
        a = 2 * math.pi * (k + 0.5) / A.CROWN_BOLTS
        g = g - zc(4.78, zb - 1, zb + 14.0, A.CROWN_BOLT_R * math.cos(a), A.CROWN_BOLT_R * math.sin(a))
    g = Location((0, A.CROWN_HEEL_Y, 0)) * Rot(90, 0, 0) * g                      # teeth face the pinion (-y)
    return _l(g, spec)


FLANGE_Y = (A.CROWN_BACK_Y, A.CROWN_BACK_Y + 10.0)


def crown_bolt(spec) -> Part:
    return _l(F.hex_bolt("3/8", spec.nom("length") / IN), spec)


def lockwasher(spec) -> Part:
    """Item 29: a tab plate under two bolt heads, drawn in the plane z = 0..t with the two holes on
    the bolt circle either side of +x (the assembly turns it round the axle axis)."""
    t = spec.nom("thickness")
    r = A.CROWN_BOLT_R
    da = 2 * math.pi / A.CROWN_BOLTS
    from mgb.poly2d import hull, circle_pts
    pts = []
    for s in (-1, 1):
        pts += circle_pts(r * math.cos(s * da / 2), r * math.sin(s * da / 2), 9.0, 20)
    w = C.zprism(hull(pts), 0.0, t)
    for s in (-1, 1):
        w = w - zc(5.0, -1, t + 1, r * math.cos(s * da / 2), r * math.sin(s * da / 2))
    # tabs turned up against the bolt head flats (one per bolt, on the outside) and down over the flange edge
    for s in (-1, 1):
        a = s * da / 2
        x, y = (r + 8.9) * math.cos(a), (r + 8.9) * math.sin(a)
        w = w + Location((x, y, 0)) * Rot(0, 0, math.degrees(a)) * box(-0.6, 0.6, -4.0, 4.0, 0.0, 6.0)
    return _l(w, spec)


# =================================================================================================
# cage (20), pinion shaft (25), peg (26)
# =================================================================================================
CAGE_R = 53.0
CAVITY_R = 43.2
SHAFT_D = 0.625 * IN


def cage(spec) -> Part:
    b0, b1 = A.DIFF_BRG_Y
    rb = A.DIFF_BRG[0] / 2
    f0, f1 = FLANGE_Y
    prof = [(16.0, -b1 - 1.0), (rb - 0.6, -b1 - 1.0), (rb, -b1), (rb, -b0), (27.0, -b0 + 1.0), (29.0, -60.0), (42.0, -52.0),
            (CAGE_R, -38.0), (CAGE_R, 34.0), (CROWN_BORE_R - 0.05, 38.0), (CROWN_BORE_R - 0.05, f0), (72.0, f0),
            (72.0, f1 - 1.0), (71.0, f1), (34.0, f1), (30.0, 62.0), (27.0, b0 - 1.0), (rb, b0), (rb, b1), (rb - 0.6, b1 + 1.0),
            (16.0, b1 + 1.0)]
    c = to_y(Sh.revolved(prof))
    # pinion shaft bosses (shaft along x)
    c = c + xcyl(13.0, -56.0, 56.0)
    # inside: spherical seat for the pinion washers, flats and bores for the side gears
    cav = Sphere(CAVITY_R) + ycyl(38.0, -31.5, 31.5)
    cav = cav + ycyl(18.2, -46.0, 46.0)
    c = c - cav
    c = c - ycyl(15.6, -b1 - 2, b1 + 2)                                          # axleshafts pass through
    # two windows (top and bottom) for fitting the gears
    for z0, z1 in ((20.0, 70.0), (-70.0, -20.0)):
        c = c - box(-21.0, 21.0, -26.0, 24.0, z0, z1)
    c = c - xcyl(SHAFT_D / 2 + 0.05, -60.0, 60.0)
    c = c - zc(2.6, -9.0, 14.0, PEG_X, 0.0)                                      # peg hole through the boss
    for k in range(A.CROWN_BOLTS):
        a = 2 * math.pi * (k + 0.5) / A.CROWN_BOLTS
        c = c - ycyl(5.0, f0 - 1, f1 + 1, A.CROWN_BOLT_R * math.cos(a), A.CROWN_BOLT_R * math.sin(a))
    return _l(c, spec)


PEG_X = 46.0


def pinion_shaft(spec) -> Part:
    L = spec.nom("length")
    s = Location((-L / 2, 0, 0)) * Rot(0, 90, 0) * Sh.chamfered_cyl(SHAFT_D, L, 0.6)
    s = s - zc(2.6, -10, 10, PEG_X, 0.0)
    s = s - box(-20.0, 20.0, -SHAFT_D, SHAFT_D, SHAFT_D / 2 - 0.6, SHAFT_D)        # oil flat
    return _l(s, spec)


def peg(spec) -> Part:
    p = Location((PEG_X, 0, -SHAFT_D / 2 + 1.0)) * Sh.chamfered_cyl(5.2, spec.nom("length"), 0.4)
    return _l(p, spec)


# =================================================================================================
# side gears (21), thrust washers (22), pinions (23), thrust washers (24)
# =================================================================================================
SIDE_BACK = 30.0                                                                # |y| of the side gear back face


def side_bevel():
    return BV.Bevel(A.Z_SIDE, A.SIDE_PITCH_R, math.degrees(math.atan(A.Z_SIDE / A.Z_PLANET)), 11.0, 3.0, 3.9)


def planet_bevel():
    return BV.Bevel(A.Z_PLANET, A.PLANET_PITCH_R, math.degrees(math.atan(A.Z_PLANET / A.Z_SIDE)), 11.0, 3.0, 3.9)


def side_gear(spec) -> Part:
    """Left side gear (the right is mirrored): gear frame z toward the centre."""
    bv = side_bevel()
    h0, h1 = bv.cone_pt(0, -3.6), bv.cone_pt(11.0, -3.6)
    heel = A.SIDE_PITCH_R / (A.Z_SIDE / A.Z_PLANET)                              # |y| of the heel pitch plane
    zb = -(SIDE_BACK - heel)
    body = Sh.revolved([(13.0, zb - 16.0), (18.0, zb - 16.0), (18.0, zb), (h0[0] + 1.5, zb), (h0[0] + 1.5, h0[1] - 1.0),
                        (h0[0], h0[1]), (h1[0], h1[1]), (h1[0] - 2.0, h1[1] + 1.5), (13.0, h1[1] + 1.5)])
    g = BV.gear(bv, body, SIDE_PHASE)
    n, dmaj, dmin = A.SHAFT_SPLINE_IN
    g = g - GR.spline_bore(n, dmaj, dmin, 40.0).moved(Location((0, 0, zb - 18.0)))
    g = Location((0, heel, 0)) * Rot(90, 0, 0) * g
    return _l(g, spec)


def side_thrust_washer(spec) -> Part:
    t = spec.nom("thickness")
    return _l(to_y(ring(18.4, 36.5, SIDE_BACK, SIDE_BACK + t)), spec)


def planet(spec) -> Part:
    """A differential pinion on the +x end of the shaft (the other is turned half round): gear frame
    z toward the centre, back spherical."""
    bv = planet_bevel()
    heel = A.PLANET_PITCH_R / (A.Z_PLANET / A.Z_SIDE)                            # |x| of the heel pitch plane, 34
    h0, h1 = bv.cone_pt(0, -3.6), bv.cone_pt(11.0, -3.6)
    Rs = CAVITY_R - 1.4                                                          # spherical back
    zc0 = heel                                                                    # sphere centre in the gear frame
    back = [(r, zc0 - math.sqrt(Rs ** 2 - r ** 2)) for r in (SHAFT_D / 2 + 0.1, 12.0, 16.0, 20.0, h0[0] + 2.0)]
    body = Sh.revolved([back[0]] + back[1:] + [(h0[0] + 2.0, h0[1] - 0.6), (h0[0], h0[1]), (h1[0], h1[1]),
                                               (h1[0] - 1.5, h1[1] + 1.0), (SHAFT_D / 2 + 0.1, h1[1] + 1.0)])
    g = BV.gear(bv, body, PLANET_PHASE)
    g = g - zc(SHAFT_D / 2 + 0.1, -20, 40)
    g = Location((heel, 0, 0)) * Rot(0, -90, 0) * g
    return _l(g, spec)


def planet_thrust_washer(spec) -> Part:
    """Item 24: domed washer between a pinion's back and the cage's spherical seat."""
    t = spec.nom("thickness")
    Rs = CAVITY_R - 1.4
    r0, r1 = SHAFT_D / 2 + 0.2, 21.0
    rs = [r0 + (r1 - r0) * k / 12 for k in range(13)]
    prof = [(r, math.sqrt(Rs ** 2 - r ** 2)) for r in rs] + [(r, math.sqrt((Rs + t) ** 2 - r ** 2)) for r in reversed(rs)]
    w = Rot(0, 90, 0) * Sh.revolved(prof)
    return _l(w, spec)


# =================================================================================================
# differential bearings (18) and packing washers (19)
# =================================================================================================
def diff_bearing(spec) -> Part:
    b = BR.ball_bearing(*A.DIFF_BRG)
    return _l(to_y(b.moved(Location((0, 0, A.DIFF_BRG_Y[0])))), spec)


def packing_washer(spec) -> Part:
    t = spec.nom("thickness")
    return _l(to_y(ring(A.DIFF_BRG[0] / 2 + 1.0, A.DIFF_BRG[1] / 2 - 0.3, A.DIFF_BRG_Y[1], A.DIFF_BRG_Y[1] + t)), spec)


PARTS = {
    "axle.carrier.crown-wheel": {"build": crown_wheel, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.crown-wheel-bolt": {"build": crown_bolt, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "axle.carrier.crown-wheel-lockwasher": {"build": lockwasher},
    "axle.carrier.cage": {"build": cage},
    "axle.carrier.pinion-shaft": {"build": pinion_shaft, "probes": {"length": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.pinion-peg": {"build": peg},
    "axle.carrier.side-gear": {"build": side_gear},
    "axle.carrier.side-thrust-washer": {"build": side_thrust_washer, "probes": {"thickness": lambda p: probes.bbox_size(p, "y")}},
    "axle.carrier.diff-pinion": {"build": planet},
    "axle.carrier.diff-pinion-thrust-washer": {"build": planet_thrust_washer},
    "axle.carrier.diff-bearing": {"build": diff_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.packing-washer": {"build": packing_washer, "probes": {"thickness": lambda p: probes.bbox_size(p, "y")}},
}
