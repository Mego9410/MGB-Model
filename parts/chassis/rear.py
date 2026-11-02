"""Rear suspension: leaf springs and their leaves, clips, centre bolt, U-bolts, locating plates, pads, damper
brackets, bump rubber pedestals and rubbers, front eyebolts and bushes, rear shackles and bushes, lever dampers
and links, rebound straps (Haynes Ch 11 Fig 11.4 items 1-35, Fig 11.5 items 1-8; Secs 8, 10; printed p202,
207-208).

Drawn in the car frame for the left-hand spring (mgb.rear_suspension_layout); parts that are not symmetric
about their own centre plane take `side` and are mirrored for the right. Leaves, plates and pads are drawn in
the spring frame (x from the centre bolt, car z, y across the spring) and placed at the spring centre.

Forms (Fig 11.4): leaves following the spring's camber with chamfered ends; the main leaf rolled into an eye at
each end; the second leaf's front end wrapped part way round the front eye; clips riveted under the third and
fourth leaves and turned up round the leaves above; the centre bolt with its nut and locknut; the locating plate
with its peg into the axle seat and its sides turned down over the spring; the ribbed rubber seating pad; the
U-bolt over the pedestal with rolled threads; the pedestal a saddle on the tube with a platform for the bump
rubber; the bracket (20) with the stud for the damper link; the shackle's pin plate with two pins and its
plain plate; top-hat rubber bushes. Fig 11.5: the damper body with its mounting flange and two bolt lugs, the
filler plug on top, the arm on its shaft and the link with rubber-bushed eyes.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot, Torus

from mgb import fasteners as F, probes, rear_axle_layout as A, rear_suspension_layout as R, shapes as Sh
from mgb.chassis_geom import (IN, box, hexagon, lab, rod, spring_washer, xcyl, xprism, xrev, ycyl, yprism, yrev, zcyl,
                              zprism, zrev)
from mgb.poly2d import circle_pts, hull

W = R.LEAF_W
T = R.LEAF_T


def side_of(p, side):
    return p if side > 0 else p.mirror(Plane.XZ)


def leaf_top_z(i, x):
    """Top of leaf i (1-based; 6 = bottom plate) at x along the spring."""
    return R.leaf_top(x) - (i - 1) * T


def _leaf_profile(i, f, r, t):
    n = 40
    xs = [-r + (f + r) * k / n for k in range(n + 1)]
    top = [(x, leaf_top_z(i, x)) for x in xs]
    bot = [(x, leaf_top_z(i, x) - t) for x in reversed(xs)]
    # chamfered (tapered) ends on the shorter leaves
    if i > 1:
        bot[0] = (bot[0][0] - 0.0, bot[0][1] + t * 0.45)
        bot[-1] = (bot[-1][0], bot[-1][1] + t * 0.45)
    return top + bot


def _leaf_solid(i, f, r, t):
    pts = _leaf_profile(i, f, r, t)
    return yprism(pts, -W / 2, W / 2)


def _eye(x):
    """Rolled eye at x (main leaf end): a ring along y round the bush."""
    cz = R.eye_centre(x)
    e = ycyl(R.EYE_R_IN + T, -W / 2, W / 2, x, cz) - ycyl(R.EYE_R_IN, -W / 2 - 1, W / 2 + 1, x, cz)
    # the leaf runs into the eye's underside: fill the joint
    sgn = 1 if x > 0 else -1
    e = e + yprism([(x - sgn * 26.0, R.leaf_top(x - sgn * 26.0)), (x, R.leaf_top(x) + 0.3), (x, R.leaf_top(x) - T),
                    (x - sgn * 26.0, R.leaf_top(x - sgn * 26.0) - T)], -W / 2, W / 2)
    return e


def leaf(i):
    def b(spec) -> Part:
        f, r = R.LEAF_HALF[i - 1]
        t = R.BOTTOM_PLATE_T if i == 6 else T
        lf = _leaf_solid(i, f - (0.0 if i > 1 else 0.0), r, t)
        if i == 1:
            lf = _leaf_solid(1, f - 4.0, r - 4.0, T) + _eye(R.FRONT_HALF) + _eye(-R.REAR_HALF)
        if i == 2:
            # military wrap: the second leaf's front end turned part way round the main leaf's eye
            cz = R.eye_centre(R.FRONT_HALF)
            ro = R.EYE_R_IN + T
            wrap = ycyl(ro + T + 0.2, -W / 2, W / 2, R.FRONT_HALF, cz) - ycyl(ro + 0.2, -W / 2 - 1, W / 2 + 1, R.FRONT_HALF, cz)
            wrap = wrap & box(R.FRONT_HALF - 2.0, R.FRONT_HALF + 40.0, -W, W, cz - 40.0, cz - 2.0)
            lf = lf + wrap
        lf = lf - zcyl(4.4, R.BOTTOM_Z - 20, R.TOP_Z + 20)                         # centre bolt hole
        if i in R.CLIPS:                                                          # rivet holes for the clips
            for fr, sg in ((R.CLIPS[i][0], 1), (R.CLIPS[i][1], -1)):
                x = sg * fr * (f if sg > 0 else r)
                lf = lf - zcyl(2.6, leaf_top_z(i, x) - t - 1, leaf_top_z(i, x) + 1, x, 0)
        return lab(lf, spec)
    return b


def clip(i):
    """Clip riveted under leaf i at its fore (sg +1) end, the arms turned up round the leaves above and over."""
    def b(spec, aft=0) -> Part:
        f, r = R.LEAF_HALF[i - 1]
        sg = -1 if aft else 1
        x = sg * R.CLIPS[i][0] * (f if sg > 0 else r)
        zb = leaf_top_z(i, x) - T
        zt = leaf_top_z(1, x)
        t = 2.0
        c = box(x - 9.0, x + 9.0, -W / 2 - t - 0.3, W / 2 + t + 0.3, zb - t, zt + t) - box(x - 10, x + 10, -W / 2 - 0.3, W / 2 + 0.3, zb, zt + 0.3)
        c = c - box(x - 10, x + 10, -W / 2 + 8.0, W / 2 - 8.0, zt, zt + t + 1)       # the turned-over tabs stop short
        c = c + zcyl(4.2, zb - t - 1.8, zb - t + 0.01, x, 0) + zcyl(2.5, zb - t, zb + 0.5, x, 0)   # rivet
        return lab(c, spec)
    return b


def centre_bolt(spec) -> Part:
    """Item 4: head on top (in the locating plate), shank down through the leaves (drawn as fitted, spring frame)."""
    d = 5.0 / 16.0 * IN
    zt = R.TOP_Z
    b = zcyl(7.0, zt, zt + 4.0) + zcyl(d / 2, R.BOTTOM_Z - 16.0, zt + 0.01)
    return lab(b, spec)


def centre_nut(thin=False):
    def b(spec) -> Part:
        n = F.hex_nut("5/16")
        if thin:
            n = n & box(-20, 20, -20, 20, -1, 4.2)
        return lab(n, spec)
    return b


# ---- locating plate (18), seating pad (19) --------------------------------------------------------------------
def locating_plate(spec) -> Part:
    """Flat plate with its sides turned down over the spring and a peg on the top (into the axle seat's hole), drawn
    with its top face at z 0 (upper plate; the lower one is the same pressing turned over)."""
    t = R.PLATE18_T
    L_ = spec.nom("length")
    p = box(-L_ / 2, L_ / 2, -W / 2 - t - 0.5, W / 2 + t + 0.5, -t, 0)
    for s in (1, -1):
        y0 = s * (W / 2 + 0.5)
        p = p + box(-L_ / 2 + 8.0, L_ / 2 - 8.0, min(y0, y0 + s * t), max(y0, y0 + s * t), -t - R.PAD19_T - 4.0, -t + 0.01)
    p = p + zcyl(5.2, -0.01, 6.0) + zcyl(5.8, -0.01, 1.2)                      # peg into the seat (11 mm hole)
    p = p - zcyl(7.5, -t - 1, -1.0)                                            # recess for the centre bolt head / nut
    return lab(p, spec)


def seating_pad(spec) -> Part:
    L_ = spec.nom("length")
    t = R.PAD19_T
    p = box(-L_ / 2, L_ / 2, -W / 2, W / 2, -t, 0)
    for k in range(-3, 4):
        p = p - box(k * 12.0 - 1.5, k * 12.0 + 1.5, -W / 2 - 1, W / 2 + 1, -1.0, 0.1)
    p = p - zcyl(8.0, -t - 1, 1)
    return lab(p, spec)


# ---- U-bolt (15), nuts (16), pedestal (17), bump rubber (32), bracket (20) -------------------------------------------
def ubolt(spec) -> Part:
    """Over the pedestal on the tube top, legs fore and aft down past the spring; drawn at the left spring's
    inboard U-bolt in the car frame relative to the axle centre line (y 0 local)."""
    r = R.UBOLT_ROD_R
    Rb = R.UBOLT_R
    z0 = R.AZ
    bend = (Location((R.AX, 0, z0)) * Rot(90, 0, 0) * Torus(Rb, r)) & box(R.AX - Rb - 20, R.AX + Rb + 20, -20, 20, z0, z0 + Rb + 20)
    u = bend
    for sx in (-1, 1):
        u = u + zcyl(r, R.UBOLT_END_Z, z0 + 0.01, R.AX + sx * Rb, 0)
        for k in range(14):                                                    # rolled thread
            z = R.UBOLT_END_Z + 2.0 + k * IN / 20
            u = u - zrev([(r - 0.5, z), (r + 1, z - 0.3), (r + 1, z + 0.3)]).moved(Location((R.AX + sx * Rb, 0, 0)))
    return lab(u, spec)


def ubolt_nut(thin=False):
    def b(spec) -> Part:
        n = F.hex_nut(R.UBOLT)
        if thin:
            n = n & box(-30, 30, -30, 30, -1, 6.0)
        return lab(n, spec)
    return b


def pedestal(spec, side=1) -> Part:
    """Item 17: saddle on the tube top under the U-bolts, two arched webs up to the bump rubber's platform."""
    y = R.SPRING_Y
    r0 = A.TUBE_R + 0.2
    t = R.PEDESTAL_T
    zt = R.PEDESTAL_TOP_Z
    sad = ycyl(r0 + t, y - 44.0, y + 44.0, R.AX, R.AZ) - ycyl(r0, y - 45, y + 45, R.AX, R.AZ)
    sad = sad & box(R.AX - 34.0, R.AX + 34.0, y - 45, y + 45, R.AZ + 14.0, R.AZ + r0 + t + 1)
    top = zcyl(30.0, zt - 4.0, zt, R.AX, y) + zcyl(27.0, zt - 0.01, zt + 3.0, R.AX, y) - zcyl(24.0, zt - 1, zt + 4, R.AX, y)
    p = sad + top
    for s in (1, -1):
        web = yprism([(R.AX - 30.0, R.AZ + 20.0), (R.AX + 30.0, R.AZ + 20.0), (R.AX + 22.0, zt - 3.9), (R.AX - 22.0, zt - 3.9)],
                     y + s * 22.0 - 1.5, y + s * 22.0 + 1.5)
        web = web - ycyl(r0, y - 50, y + 50, R.AX, R.AZ)
        p = p + web
    p = p + xprism([(y - 22.0, R.AZ + 30.0), (y + 22.0, R.AZ + 30.0), (y + 22.0, zt - 3.9), (y - 22.0, zt - 3.9)], R.AX - 1.5, R.AX + 1.5)
    p = p - xprism([(y - 14.0, R.AZ + 40.0), (y + 14.0, R.AZ + 40.0), (y + 10.0, zt - 12.0), (y - 10.0, zt - 12.0)], R.AX - 3, R.AX + 3)
    p = p - zcyl(4.2, zt - 6, zt + 4, R.AX, y)
    return lab(side_of(p, side), spec)


def bump_rubber(spec) -> Part:
    h = spec.nom("height")
    d = spec.nom("diameter")
    b = zrev([(0, 0), (d / 2, 0), (d / 2, 6.0), (d / 2 - 3.0, 9.0), (d / 2, 14.0), (d / 2 - 3.0, 22.0), (d / 2 - 1.0, 28.0),
              (d / 2 - 5.0, h - 6.0), (d / 2 - 9.0, h), (0, h)])
    b = b + zcyl(F.THREADS["5/16"][0] * IN / 2, -12.0, 0.01)
    return lab(b, spec)


def damper_bracket(spec, side=1) -> Part:
    """Item 20: plate under the lower locating plate, holes for the four U-bolt legs, a web turned down on its
    inboard side carrying the stud for the damper link."""
    y = R.SPRING_Y
    z1 = R.BRACKET_UNDER_Z + R.BRACKET_T
    z0 = R.BRACKET_UNDER_Z
    p = box(R.AX - 60.0, R.AX + 60.0, y - 46.0, y + 46.0, z0, z1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p - zcyl(6.0, z0 - 1, z1 + 1, R.AX + sx * R.UBOLT_X, y + sy * R.UBOLT_DY)
    p = p - zcyl(8.5, z0 - 1, z1 + 1, R.AX, y)                                 # centre bolt end and the plate's peg
    w0, w1 = R.BRACKET_WEB_Y
    web = yprism(hull([(R.AX - 40.0, z1), (R.LINK_X + 6.0, z1)] + circle_pts(R.LINK_X, R.LINK_LOW_Z, 15.0, 20)
                      + [(R.AX - 40.0, z0 - 4.0)]), w0, w1)
    web = web + box(R.AX - 40.0, R.LINK_X + 6.0, w0, y - 46.0 + 0.01, z0, z1)
    p = p + web
    # link stud, pointing inboard
    st = ycyl(6.35, R.LINK_Y - 16.0, w0 + 0.01, R.LINK_X, R.LINK_LOW_Z) + ycyl(9.0, w0 - 2.0, w0 + 0.01, R.LINK_X, R.LINK_LOW_Z)
    p = p + st
    return lab(side_of(p, side), spec)


# ---- front eye: bush (2), eyebolt (21), nut (22), washer (23) ---------------------------------------------------------
def eye_bush(spec) -> Part:
    """Item 2: rubber bush with steel inner and outer sleeves, flanged both sides (drawn along +z, centred)."""
    L_ = W + 2 * R.BUSH_FLANGE_T
    ro, ri = R.EYE_R_IN, 6.6
    b = zrev([(ri, -L_ / 2), (ro + 3.0, -L_ / 2), (ro + 3.0, -W / 2), (ro, -W / 2), (ro, W / 2), (ro + 3.0, W / 2), (ro + 3.0, L_ / 2),
              (ri, L_ / 2)])
    return lab(b, spec)


def bolt(size, series="UNF"):
    def b(spec):
        return lab(F.hex_bolt(size, spec.nom("length") / IN, series), spec)
    return b


def nut(size):
    def b(spec):
        return lab(F.hex_nut(size), spec)
    return b


def sw(size):
    def b(spec):
        return lab(spring_washer(size), spec)
    return b


def pw(size):
    def b(spec):
        return lab(F.plain_washer(size), spec)
    return b


# ---- rear shackle: pin plate (10), plate (11), bushes (12), nuts (13), washers (14) ------------------------------------
SH_PLATE_T = 4.0
SH_IN_Y = R.SPRING_Y - W / 2 - R.BUSH_FLANGE_T - 0.5                # inner face of the pin plate's outer side


def _shackle_outline():
    ex, ez = R.REAR_EYE[0], R.REAR_EYE[2]
    tx, tz = R.SHACKLE_TOP[0], R.SHACKLE_TOP[2]
    return hull(circle_pts(ex, ez, 14.0, 24) + circle_pts(tx, tz, 14.0, 24))


def shackle_pin_plate(spec, side=1) -> Part:
    """Item 10: inner plate with two pins welded in, pointing outboard, threaded ends."""
    y1 = SH_IN_Y
    p = yprism(_shackle_outline(), y1 - SH_PLATE_T, y1)
    yend = R.SPRING_Y + W / 2 + R.BUSH_FLANGE_T + 0.5 + SH_PLATE_T + 12.0
    for x, z in ((R.REAR_EYE[0], R.REAR_EYE[2]), (R.SHACKLE_TOP[0], R.SHACKLE_TOP[2])):
        p = p + ycyl(R.SHACKLE_PIN_D / 2, y1 - 0.01, yend, x, z)
        p = p + ycyl(R.SHACKLE_PIN_D / 2 + 2.0, y1 - SH_PLATE_T - 1.5, y1 - SH_PLATE_T + 0.01, x, z)   # weld bead
    return lab(side_of(p, side), spec)


def shackle_plate(spec, side=1) -> Part:
    y0 = R.SPRING_Y + W / 2 + R.BUSH_FLANGE_T + 0.5
    p = yprism(_shackle_outline(), y0, y0 + SH_PLATE_T)
    for x, z in ((R.REAR_EYE[0], R.REAR_EYE[2]), (R.SHACKLE_TOP[0], R.SHACKLE_TOP[2])):
        p = p - ycyl(R.SHACKLE_PIN_D / 2 + 0.3, y0 - 1, y0 + SH_PLATE_T + 1, x, z)
    return lab(side_of(p, side), spec)


def shackle_bush(spec) -> Part:
    """Item 12: top-hat rubber half bush, one from each side of an eye (drawn along +z from the flange face)."""
    L_ = W / 2
    ro, ri = R.EYE_R_IN, R.SHACKLE_PIN_D / 2 + 0.2
    b = zrev([(ri, 0), (ro + 4.0, 0), (ro + 4.0, R.BUSH_FLANGE_T), (ro, R.BUSH_FLANGE_T), (ro, R.BUSH_FLANGE_T + L_ - 0.3),
              (ri, R.BUSH_FLANGE_T + L_ - 0.3)])
    return lab(b, spec)


# ---- damper (Fig 11.5), link (2), fixings -------------------------------------------------------------------------------
SX, SZ = R.DAMPER_SHAFT[0], R.DAMPER_SHAFT[2]


def damper(spec, side=1) -> Part:
    """Fig 11.5 item 1: cast body on a mounting flange against the body side member (two bolt lugs), the piston
    bore across it, the lid with the filler plug, the shaft boss on the inboard face and the arm to the link."""
    yf = R.DAMPER_FACE_Y
    y0 = R.LINK_Y + 10.0                                   # inboard face of the shaft boss
    body = box(SX - 62.0, SX + 50.0, y0 + 12.0, yf - 6.0, SZ - 44.0, SZ + 40.0)
    body = body + xcyl(26.0, SX - 74.0, SX + 62.0, (y0 + 12.0 + yf - 6.0) / 2, SZ - 22.0)          # piston bore
    for xx in (SX - 74.0, SX + 62.0):
        body = body + Location((xx, (y0 + 12.0 + yf - 6.0) / 2, SZ - 22.0)) * Rot(0, 90 if xx > SX else -90, 0) * hexagon(30.0, 5.0)
    body = body + box(SX - 64.0, SX + 52.0, y0 + 10.0, yf - 4.0, SZ + 39.0, SZ + 45.0)              # lid
    body = body + zcyl(9.0, SZ + 44.9, SZ + 50.0, SX - 6.0, (y0 + yf) / 2) + Location((SX - 6.0, (y0 + yf) / 2, SZ + 50.0)) * hexagon(14.3, 5.0)
    # mounting flange with the two lugs
    pts = []
    for x, z in R.DAMPER_BOLTS:
        pts += circle_pts(x, z, 13.0, 18)
    pts += [(SX - 60.0, SZ - 40.0), (SX + 48.0, SZ + 38.0)]
    fl = yprism(hull(pts), yf - 8.0, yf)
    for x, z in R.DAMPER_BOLTS:
        fl = fl - ycyl(5.6, yf - 9.0, yf + 1, x, z)
    body = body + fl
    # shaft boss and arm (arm points rearward, level, to the link's upper eye)
    body = body + ycyl(22.0, y0, y0 + 12.01, SX, SZ)
    arm = yprism(hull(circle_pts(SX, SZ, 16.0, 24) + circle_pts(R.LINK_X, R.LINK_TOP_Z, 11.0, 20)), R.LINK_Y + 5.0, R.LINK_Y + 13.0)
    arm = arm + ycyl(6.35, R.LINK_Y - 12.0, R.LINK_Y + 5.01, R.LINK_X, R.LINK_TOP_Z)              # pin for the link
    body = body + arm + ycyl(10.0, R.LINK_Y + 4.0, y0 + 0.01, SX, SZ)
    return lab(side_of(body, side), spec)


def link(spec, side=1) -> Part:
    """Fig 11.5 item 2: a rod with a rubber-bushed eye at each end, on the arm's pin and the bracket's stud."""
    y = R.LINK_Y
    zt, zb = R.LINK_TOP_Z, R.LINK_LOW_Z
    l = rod((R.LINK_X, y, zb + 12.0), (R.LINK_X, y, zt - 12.0), 6.5)
    for z in (zt, zb):
        l = l + ycyl(14.0, y - 5.0, y + 5.0, R.LINK_X, z) - ycyl(6.6, y - 6, y + 6, R.LINK_X, z)
        l = l + (ycyl(11.0, y - 6.5, y + 6.5, R.LINK_X, z) - ycyl(6.6, y - 7, y + 7, R.LINK_X, z))  # rubber bush faces
    return lab(side_of(l, side), spec)


# ---- rebound strap (24), tube (25), bolt (29) -------------------------------------------------------------------------------
def rebound_strap(spec, side=1) -> Part:
    lo = R.STRAP_LOW[1]
    hi = R.STRAP_TOP[1]
    y0, y1 = A.REBOUND_SPINDLE[1] - 7.0, A.REBOUND_SPINDLE[1] + 5.0
    s = None
    for (x, _, z) in (lo, hi):
        e = ycyl(14.0, y0, y1, x, z) - ycyl(8.2, y0 - 1, y1 + 1, x, z)
        s = e if s is None else s + e
    dx, dz = hi[0] - lo[0], hi[2] - lo[2]
    Lg = math.hypot(dx, dz)
    ux, uz = dx / Lg, dz / Lg
    nx, nz = -uz, ux
    a = (lo[0] + ux * 12.0, lo[2] + uz * 12.0)
    b_ = (hi[0] - ux * 12.0, hi[2] - uz * 12.0)
    band = yprism([(a[0] + nx * 4.0, a[1] + nz * 4.0), (b_[0] + nx * 4.0, b_[1] + nz * 4.0), (b_[0] - nx * 4.0, b_[1] - nz * 4.0),
                   (a[0] - nx * 4.0, a[1] - nz * 4.0)], y0, y1)
    s = s + band
    return lab(side_of(s, side), spec)


def strap_tube(spec) -> Part:
    return lab(Sh.tube(16.0, 9.9, 12.0), spec)


PARTS = {
    "chassis.rear.main-leaf": {"build": leaf(1), "probes": {"width": lambda p: probes.bbox_size(p, "y")}},
    "chassis.rear.second-leaf": {"build": leaf(2)},
    "chassis.rear.third-leaf": {"build": leaf(3)},
    "chassis.rear.fourth-leaf": {"build": leaf(4)},
    "chassis.rear.fifth-leaf": {"build": leaf(5)},
    "chassis.rear.bottom-plate": {"build": leaf(6)},
    "chassis.rear.clip-third": {"build": clip(3)},
    "chassis.rear.clip-fourth": {"build": clip(4)},
    "chassis.rear.centre-bolt": {"build": centre_bolt},
    "chassis.rear.centre-nut": {"build": centre_nut()},
    "chassis.rear.locating-plate": {"build": locating_plate},
    "chassis.rear.seating-pad": {"build": seating_pad},
    "chassis.rear.u-bolt": {"build": ubolt},
    "chassis.rear.u-bolt-nut": {"build": ubolt_nut()},
    "chassis.rear.u-bolt-locknut": {"build": ubolt_nut(thin=True)},
    "chassis.rear.pedestal": {"build": pedestal},
    "chassis.rear.bump-rubber": {"build": bump_rubber},
    "chassis.rear.bump-nut": {"build": nut("5/16")},
    "chassis.rear.damper-bracket": {"build": damper_bracket},
    "chassis.rear.eye-bush": {"build": eye_bush},
    "chassis.rear.eyebolt": {"build": bolt(R.EYEBOLT)},
    "chassis.rear.eyebolt-nut": {"build": nut(R.EYEBOLT)},
    "chassis.rear.eyebolt-washer": {"build": sw(R.EYEBOLT)},
    "chassis.rear.shackle-pin-plate": {"build": shackle_pin_plate},
    "chassis.rear.shackle-plate": {"build": shackle_plate},
    "chassis.rear.shackle-bush": {"build": shackle_bush},
    "chassis.rear.shackle-nut": {"build": nut("1/2")},
    "chassis.rear.shackle-washer": {"build": sw("1/2")},
    "chassis.rear.damper": {"build": damper},
    "chassis.rear.link": {"build": link},
    "chassis.rear.link-nut": {"build": nut("1/2")},
    "chassis.rear.link-washer": {"build": pw("1/2")},
    "chassis.rear.damper-bolt": {"build": bolt("3/8")},
    "chassis.rear.damper-nut": {"build": nut("3/8")},
    "chassis.rear.damper-spring-washer": {"build": sw("3/8")},
    "chassis.rear.damper-plain-washer": {"build": pw("3/8")},
    "chassis.rear.rebound-strap": {"build": rebound_strap},
    "chassis.rear.strap-tube": {"build": strap_tube},
    "chassis.rear.strap-bolt": {"build": bolt("3/8")},
    "chassis.rear.strap-nut": {"build": nut("3/8")},
    "chassis.rear.strap-spring-washer": {"build": sw("3/8")},
    "chassis.rear.strap-plain-washer": {"build": pw("3/8")},
}
