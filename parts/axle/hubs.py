"""Axleshafts and rear hubs for wire wheels, three-quarter floating banjo axle (Haynes Ch 8 Fig 8.1 items 2,
3, 6, 41-46, 51-55; Sec 4 paras 5-7, Sec 5, printed p142-143).

Drawn in the axle frame (mgb.rear_axle_layout) at the left-hand (near side) hub, along +y; the
assembly turns each part half round the vertical axis for the right-hand hub (a rotation, so the
threads keep their hand). Parts that differ by side - the bearing nuts (RH and LH thread) and the
hub extensions (RH and LH, whose spinner threads are handed) - are separate parts, each drawn at
the left-hand position.

Forms (Fig 8.1): hub item 51 - a bell over the bearing with the oil seal in its inner end and a
lobed flange carrying four pressed-in studs (item 52) and the tapped hole for the screw (item 46);
hub extension items 42/43 - a flange like the hub's with an O-ring groove, the inner cone the
wheel seats on, the Rudge-Whitworth splines, the spinner thread (12 tpi on cars to GHN3-30850) and
the Welch plug (item 44) in its end, splined inside for the axleshaft; axleshaft item 41 - splined
at both ends; bearing nut items 2/3 - octagonal (the eight-sided 18G152 spanner) with a faced
side; locking washer item 6 - an inner tab in the case keyway and tabs turned up on the nut.
"""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Location, Part, Plane, Rot, Torus, extrude

from mgb import bearings as BR, fasteners as F, gears as GR, probes, rear_axle_layout as A, shapes as Sh
from mgb.poly2d import circle_pts, hull
from parts.axle.casing import handed_thread, thread_frame, yrev
from parts.gearbox import casing as C
from parts.propshaft.shaft import ring, ycyl, yprism

IN = 25.4
zc, box = C.zc, C.box


def _l(p, spec):
    p.label = spec.id
    return p


def along_y(p, y0):
    """A part drawn along +z from 0, turned outward along +y from station y0."""
    return Location((0, y0, 0)) * Rot(-90, 0, 0) * p


def _pt(r, a):
    """(x, z) of a point on a circle in the hub plane, angle a from the top toward the front."""
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


def _lobed(y0, y1, r_body):
    pts = circle_pts(0, 0, r_body, 60)
    for a in A.STUD_ANGLES:
        pts += circle_pts(*_pt(A.STUD_PCD / 2, a), 13.0, 20)
    pts += circle_pts(*_pt(A.STUD_PCD / 2, A.SCREW_ANGLE), 10.0, 16)
    return yprism(hull(pts), y0, y1)


# =================================================================================================
# axleshaft (41)
# =================================================================================================
def axleshaft(spec) -> Part:
    n, dmaj, dmin = A.SHAFT_SPLINE_IN
    i0, i1 = A.SHAFT_IN_Y
    o0, o1 = A.SHAFT_SPLINE_OUT_Y
    r = A.SHAFT_D / 2
    s = yrev([(0, i0), (dmin / 2 - 0.8, i0), (dmin / 2, i0 + 0.8), (dmin / 2, i1), (r - 1.0, i1 + 3.0), (r, i1 + 12.0),
              (r, o0 - 20.0), (r + 0.8, o0 - 10.0), (dmin / 2, o0 - 1.0), (dmin / 2, o1 + 1.0), (dmin / 2 - 1.0, o1 + 2.0), (0, o1 + 2.0)])
    s = s + along_y(GR.spline_shaft(n, dmaj, dmin, i1 - i0 - 2.0), i0 + 1.0)
    s = s + along_y(GR.spline_shaft(n, dmaj, dmin, o1 - o0), o0)
    return _l(s, spec)


# =================================================================================================
# hub (51), studs (52), bearing (55), oil seal (54), O-ring (53)
# =================================================================================================
def hub(spec) -> Part:
    y0, yf = A.HUB_Y
    f0 = A.HUB_FLANGE_Y[0]
    s0, s1 = A.HUB_SEAL_Y
    h = yrev([(A.SEAL_TRACK_R + 1.5, y0), (44.0, y0), (44.0, y0 + 6.0), (48.0, y0 + 12.0), (48.0, f0), (50.0, f0),
              (50.0, yf), (A.HUB_BRG[1] / 2, yf), (A.HUB_BRG[1] / 2, A.HUB_BRG_Y[0]), (36.5, A.HUB_BRG_Y[0]), (36.5, s1),
              (2.75 * IN / 2, s1), (2.75 * IN / 2, s0), (A.SEAL_TRACK_R + 1.5, s0)])
    h = h + (_lobed(f0, yf, 54.0) - ycyl(A.HUB_BRG[1] / 2, f0 - 1, yf + 1))
    for a in A.STUD_ANGLES:
        x, z = _pt(A.STUD_PCD / 2, a)
        h = h - ycyl(6.62, f0 - 1, yf + 1, x, z)
    x, z = _pt(A.STUD_PCD / 2, A.SCREW_ANGLE)
    h = h - ycyl(3.18, f0 - 1, yf + 1, x, z)                                     # tapped 1/4 UNF for the screw
    return _l(h, spec)


def hub_stud(spec) -> Part:
    """Item 52: head under the hub flange, knurled shank pressed in, 1/2 in UNF thread (drawn along
    +z from the head's underside)."""
    L = spec.nom("length")
    d = F.THREADS[A.STUD][0] * IN
    s = Sh.revolved([(0, -4.0), (8.9, -4.0), (8.9, -0.8), (8.1, 0), (0, 0)])
    s = s + zc(d / 2 + 0.25, -0.01, A.HUB_FLANGE_Y[1] - A.HUB_FLANGE_Y[0])
    for k in range(20):                                                          # knurl
        s = s - Rot(0, 0, 18.0 * k) * box(d / 2 - 0.1, d / 2 + 1, -0.35, 0.35, 0.5, 7.0)
    s = s + Sh.chamfered_cyl(d, L - 7.99, 0.8, z0=7.99)
    p = IN / 20
    for k in range(int((L - 14.0) / p)):
        z = 14.0 + k * p
        s = s - ring(d / 2 - 0.6, d / 2 + 1, z, z + 0.45 * p)
    return _l(s, spec)


def hub_bearing(spec) -> Part:
    b = BR.ball_bearing(*A.HUB_BRG, rows=2)
    return _l(along_y(b, A.HUB_BRG_Y[0]), spec)


def hub_seal(spec) -> Part:
    ri, ro, w = spec.nom("inside_diameter") / 2, spec.nom("outside_diameter") / 2, spec.nom("width")
    y0 = A.HUB_SEAL_Y[0]
    # case outward (+y), lip inward toward the differential (Sec 5 para 4a)
    s = yrev([(ro - 1.8, y0 + w), (ro, y0 + w), (ro, y0), (ri + 3.0, y0), (ri + 3.0, y0 + 1.0), (ro - 1.8, y0 + 1.0)])
    s = s + yrev([(ri, y0 + w - 2.0), (ri + 4.5, y0 + w - 0.8), (ro - 1.8, y0 + w - 0.8), (ro - 1.8, y0 + 1.0),
                  (ri + 4.0, y0 + 1.0), (ri + 0.8, y0 + w - 5.0)])
    s = s + yrev([(ri + 4.4, y0 + w - 2.6), (ri + 6.4, y0 + w - 2.6), (ri + 6.4, y0 + w - 4.6), (ri + 4.4, y0 + w - 4.6)])
    return _l(s, spec)


ORING_R = 45.5
ORING_Y = A.EXT_FLANGE_Y[0] + 1.2


def o_ring(spec) -> Part:
    c = spec.nom("section") / 2
    return _l(Location((0, ORING_Y, 0)) * Rot(-90, 0, 0) * Torus(ORING_R, c), spec)


# =================================================================================================
# locking washer (6), bearing nuts (2, 3)
# =================================================================================================
def lockwasher(spec) -> Part:
    t = spec.nom("thickness")
    y0 = A.HUB_BRG_Y[1]
    w = ycyl(28.0, y0, y0 + t) - ycyl(A.THREAD_D / 2 + 0.3, y0 - 1, y0 + t + 1)
    w = w + box(-2.2, 2.2, y0, y0 + t, A.THREAD_D / 2 - 2.0, A.THREAD_D / 2 + 0.31)            # inner tab in the keyway
    for k in range(8):                                                            # outer tabs
        w = w + Rot(0, 22.5 + 45.0 * k, 0) * box(-3.2, 3.2, y0, y0 + t, 26.0, 29.4)
    for a in (0.0, 180.0):                                                        # two turned up against nut flats
        w = w + Rot(0, a, 0) * (box(-3.2, 3.2, y0, y0 + t, 24.0, 29.4) + box(-3.2, 3.2, y0 + t - 0.01, y0 + 9.0, 25.0, 25.0 + t))
    return _l(w, spec)


def bearing_nut(hand):
    def b(spec) -> Part:
        af = A.NUT_AF
        t = A.NUT_T
        r_c = af / 2 / math.cos(math.radians(22.5))
        from build123d import RegularPolygon
        n = extrude(RegularPolygon(r_c, 8), t)
        n = n & Sh.revolved([(0, -0.1), (af / 2 + 0.2, -0.1), (r_c + 0.6, 2.4), (r_c + 0.6, t - 1.4), (af / 2 + 0.2, t + 0.1), (0, t + 0.1)])
        n = n - zc(A.THREAD_D / 2 - 1.2, -1, t + 1)
        n = along_y(Rot(0, 0, 22.5) * n, A.NUT_Y[0])
        # groove cut with the case thread's own frame (major + 0.3 mm), so nut and case threads are in
        # phase; the right-hand nut is drawn at the left-hand hub and turned half round z by the assembly
        side = 1 if hand == "left" else -1
        th = handed_thread(A.THREAD_D + 0.3, A.THREAD_TPI, A.CASE_END_Y - A.HUB_BRG_Y[1] + 2.0, hand)
        frame = thread_frame(side) if side > 0 else Rot(0, 0, 180) * thread_frame(side)
        n = n - frame * th
        return _l(n, spec)
    return b


# =================================================================================================
# hub extension (42 RH, 43 LH), Welch plug (44), screw (46)
# =================================================================================================
def hub_extension(thread_hand):
    def b(spec) -> Part:
        f0, f1 = A.EXT_FLANGE_Y
        c0, c1 = A.EXT_COLLAR_Y
        s0, s1 = A.EXT_SPLINE_Y
        t0, t1 = A.EXT_THREAD_Y
        n, dmaj, dmin = A.EXT_SPLINE
        rc0, rc1 = A.EXT_CONE_R
        e = yrev([(30.0, f0), (55.0, f0), (55.0, f1), (rc0 + 3.0, f1), (rc0 + 3.0, c0 + 3.0), (rc0, c0 + 5.0), (rc1, c1),
                  (dmin / 2 - 0.05, c1), (dmin / 2 - 0.05, s1), (A.EXT_THREAD_D / 2 - 1.7, s1 + 0.5),
                  (A.EXT_THREAD_D / 2 - 1.7, t0 + 0.2), (13.0, t0 + 0.2), (13.0, c1), (16.0, 627.0), (30.0, 627.0)])
        e = e + _lobed(f0, f1, 54.0)
        e = e + along_y(GR.spline_shaft(n, dmaj, dmin, s1 - s0 - 1.0), s0 + 0.5)
        th = handed_thread(A.EXT_THREAD_D, A.EXT_TPI, t1 - t0, thread_hand)
        e = e + along_y(th, t0)
        e = e - ycyl(30.0, f0 - 1, 627.0)                                         # room for the bearing nut
        e = e - ycyl(16.0, 626.0, A.SHAFT_SPLINE_OUT_Y[0])
        sn, smaj, smin = A.SHAFT_SPLINE_OUT
        e = e - along_y(GR.spline_bore(sn, smaj, smin, A.SHAFT_SPLINE_OUT_Y[1] - A.SHAFT_SPLINE_OUT_Y[0]), A.SHAFT_SPLINE_OUT_Y[0])
        e = e - ycyl(13.0, A.SHAFT_SPLINE_OUT_Y[1] - 1, t1 + 1)
        e = e - ycyl(A.WELCH_D / 2 + 0.05, t1 - 3.0, t1 + 1)
        e = e - yrev([(43.6, f0 - 0.1), (47.4, f0 - 0.1), (47.4, f0 + 2.5), (43.6, f0 + 2.5)])         # O-ring groove
        for a in A.STUD_ANGLES:
            x, z = _pt(A.STUD_PCD / 2, a)
            e = e - ycyl(6.9, f0 - 1, f1 + 1, x, z)
        x, z = _pt(A.STUD_PCD / 2, A.SCREW_ANGLE)
        e = e - ycyl(3.3, f0 - 1, f1 + 1, x, z)
        e = e - Location((x, f1 + 0.01, z)) * Rot(90, 0, 0) * Sh.revolved([(0, 0), (6.5, 0), (3.3, 3.2), (0, 3.2)])   # countersink
        return _l(e, spec)
    return b


def welch_plug(spec) -> Part:
    d = spec.nom("diameter")
    t1 = A.EXT_THREAD_Y[1]
    p = Sh.revolved([(0, 0.0), (d / 2, 0.0), (d / 2, 1.5), (d / 2 - 3.0, 2.0), (0, 3.0), (0, 1.5)])
    return _l(along_y(p, t1 - 3.0), spec)


def screw(spec) -> Part:
    """Item 46: 1/4 UNF countersunk recessed screw, extension flange to hub (drawn along +z from the
    head's top face)."""
    L = spec.nom("length")
    s = Sh.revolved([(0, 0), (6.35, 0), (3.17, 3.17), (3.17, L - 0.6), (2.6, L), (0, L)])
    s = s - box(-3.5, 3.5, -0.6, 0.6, -0.1, 2.0) - box(-0.6, 0.6, -3.5, 3.5, -0.1, 2.0)        # cross recess
    return _l(s, spec)


PARTS = {
    "axle.hubs.axleshaft": {"build": axleshaft, "probes": {"diameter": lambda p: _shaft_d(p)}},
    "axle.hubs.hub": {"build": hub, "probes": {"bearing_bore": lambda p: _bore(p, A.HUB_BRG[1] / 2)}},
    "axle.hubs.hub-stud": {"build": hub_stud, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "axle.hubs.hub-bearing": {"build": hub_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x"),
                                                               "width": lambda p: probes.bbox_size(p, "y")}},
    "axle.hubs.hub-seal": {"build": hub_seal, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x"),
                                                         "inside_diameter": lambda p: 2 * min(math.hypot(v.X, v.Z) for v in p.vertices()),
                                                         "width": lambda p: probes.bbox_size(p, "y")}},
    "axle.hubs.o-ring": {"build": o_ring},
    "axle.hubs.lockwasher": {"build": lockwasher},
    "axle.hubs.bearing-nut-rh": {"build": bearing_nut("right"), "probes": {"across_flats": lambda p: _af(p)}},
    "axle.hubs.bearing-nut-lh": {"build": bearing_nut("left"), "probes": {"across_flats": lambda p: _af(p)}},
    "axle.hubs.hub-extension-rh": {"build": hub_extension("left")},
    "axle.hubs.hub-extension-lh": {"build": hub_extension("right")},
    "axle.hubs.welch-plug": {"build": welch_plug, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "axle.hubs.screw": {"build": screw, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
}


def _shaft_d(p):
    best = max((f for f in p.faces() if f.geom_type.name == "CYLINDER" and f.radius), key=lambda f: f.bounding_box().size.Y)
    return 2 * best.radius


def _bore(p, r):
    rs = [f.radius for f in p.faces() if f.geom_type.name == "CYLINDER" and f.radius and abs(f.radius - r) < 0.5]
    return 2 * min(rs, key=lambda v: abs(v - r)) if rs else 0.0


def _af(p):
    """Across the flats of the octagon: the nut's extent along x (flats normal to x after the 22.5 deg turn)."""
    return probes.bbox_size(p, "x")
