"""Steering: rack and pinion (RHD), tie-rods and ball joints, gaiters, mounting brackets and shims; the column with
its universal joint, bearings, clamps and toe board fittings; the steering wheel, nut and horn push (Haynes Ch 11
Fig 11.6 items 1-69, 72-75; Fig 11.8; Secs 12, 17-19, 23, 26, 29; printed p202-203, 209-214).

The rack parts are drawn in the car frame; the pinion, universal joint, column parts and steering wheel are drawn
along their own axis (local z up the column, local x toward "up" on the wheel) and placed by the assembly in the
column frame of mgb.steering_layout. Left and right tie-rods, gaiters and ball joints are the same parts placed
mirror-wise where they are symmetric, and built mirrored where not.

Forms (Fig 11.6): the rack housing - a tube with the pinion housing cast on its right-hand end at the column's
angle, the damper (yoke) boss under it with its cover plate and two bolts, the pinion end cover with two bolts,
the lubricator boss, and two flat pads the mounting brackets clamp on; the rack bar with its teeth on top under
the pinion; the pinion with its helical teeth and splined top; ball housings and locknuts on the rack ends; the
tie-rods with their inner balls; convoluted rubber gaiters with an inner and outer clip; the outer ball joints -
a forged body with its threaded shank, the ball pin up through the lever's taper, the boot and its retainer, the
self-locking nut, the locknut on the tie-rod; the universal joint - two yokes with pinch bolts and the journal
(spider) with four bearing cups (the early joint can be overhauled like the propeller shaft's, Sec 17 para 2);
the outer tube with its upper and lower bearings; the column clamp and the bottom bracket; the 16 1/2 in banjo
wheel - an acetate rim, three spokes of four spring-steel wires each, the black hub boss - its nut and the horn
push with the MG badge.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot, Torus, Vector

from mgb import fasteners as F, front_suspension_layout as FS, gears as GR, probes, shapes as Sh, steering_layout as S
from mgb.chassis_geom import (IN, box, castellated_nut, frame_to, hexagon, lab, rod, spring_washer, tube_between,
                              xcyl, xprism, ycyl, yprism, yrev, zcyl, zprism, zrev)
from mgb.poly2d import circle_pts, hull, rounded

RX, RZ = S.RACK_X, S.RACK_Z
HR = S.HOUSING_R


def col_frame(t):
    """Column frame at station t: origin on the axis, local z up the column, local x toward the wheel's 'up'."""
    d = Vector(*S.COLUMN_DIR)
    up = Vector(0, 0, 1) - d * d.Z
    return Location(Plane(origin=S.col(t), x_dir=up.normalized(), z_dir=d))


def side_of(p, side):
    return p if side > 0 else p.mirror(Plane.XZ)


# =================================================================================================
# rack housing (1), rack (4), pinion (13), covers and fixings
# =================================================================================================
def _pinion_axis_solid(r, t0, t1):
    return col_frame(t0) * zcyl(r, 0, t1 - t0)


def rack_housing(spec) -> Part:
    y0, y1 = S.HOUSING_Y
    h = ycyl(HR, y0, y1, RX, RZ)
    h = h + ycyl(HR + 2.5, y0, y0 + 14.0, RX, RZ) + ycyl(HR + 2.5, y1 - 14.0, y1, RX, RZ)          # end collars for the gaiters
    # pinion housing on the right, along the column axis
    ph = _pinion_axis_solid(27.0, S.PINION_HOUSING_T[0], S.PINION_HOUSING_T[1])
    ph = ph + col_frame(S.PINION_HOUSING_T[0]) * zcyl(31.0, 0, 7.0)                                   # end cover flange
    web = yprism(hull(circle_pts(RX, RZ, HR, 20) + [(S.PINION_MESH[0] - 18.0, S.PINION_MESH[2] + 6.0),
                                                     (S.PINION_MESH[0] + 22.0, S.PINION_MESH[2] + 6.0)]),
                 S.PINION_Y - 24.0, S.PINION_Y + 24.0)
    h = h + ph + web
    # damper (yoke) boss under the rack opposite the pinion, its cover flange
    h = h + zcyl(23.0, RZ - HR - 18.0, RZ, RX, S.PINION_Y) + zcyl(27.0, RZ - HR - 22.0, RZ - HR - 15.0, RX, S.PINION_Y)
    # lubricator boss on the pinion housing (Sec 2 para 3: the nipple above the steering gearbox)
    h = h + col_frame(0.0) * Location((29.0, 0, 8.0)) * Rot(0, 90, 0) * zcyl(6.5, -4.0, 6.0)
    # mounting pads for the brackets
    for s in (1, -1):
        y = s * FS.RACK_CLAMP_Y
        h = h + box(RX - 18.0, RX + 18.0, y - 13.0, y + 13.0, FS.RACK_BOSS_TOP + FS.RACK_SHIM_T, RZ)
    # bores
    h = h - ycyl(S.RACK_R + 0.8, y0 - 1, y1 + 1, RX, RZ)
    h = h - _pinion_axis_solid(19.0, S.PINION_HOUSING_T[0] - 1, S.PINION_HOUSING_T[1] + 1)
    h = h - zcyl(17.0, RZ - HR - 23.0, RZ - 2.0, RX, S.PINION_Y)
    for k in range(2):                                                   # end cover and damper cover bolt holes
        a = 90.0 + 180.0 * k
        h = h - col_frame(S.PINION_HOUSING_T[0]) * Location((24.0 * math.cos(math.radians(a)), 24.0 * math.sin(math.radians(a)), -1.0)) * zcyl(3.2, 0, 12.0)
        h = h - zcyl(3.2, RZ - HR - 23.0, RZ - HR - 8.0, RX + (21.0 if k else -21.0), S.PINION_Y)
    h = h - col_frame(0.0) * Location((29.0, 0, 8.0)) * Rot(0, 90, 0) * zcyl(2.6, -8.0, 7.0)
    return lab(h, spec)


def rack(spec) -> Part:
    r = S.RACK_R
    y0, y1 = -S.INNER_BALL_Y + 6.0, S.INNER_BALL_Y - 6.0
    b = ycyl(r, y0, y1, RX, RZ)
    # teeth on top under the pinion (straight-cut slots across a machined flat)
    b = b - box(RX - r - 1, RX + r + 1, S.PINION_Y - 75.0, S.PINION_Y + 75.0, RZ + r - 2.0, RZ + r + 1)
    p = 2 * math.pi * S.PINION_PITCH_R / S.PINION_TEETH
    n = int(150.0 / p)
    for k in range(n):
        y = S.PINION_Y - 75.0 + p * (k + 0.5)
        b = b - Location((RX, y, RZ + r - 2.0)) * Rot(0, 0, 18.0) * box(-r - 2, r + 2, -p * 0.25, p * 0.25, -4.0, 0.5)
    for s in (1, -1):                                                    # threaded ends with locking slots
        b = b - Location((RX, s * (y1 - 4.0), RZ + r - 1.0)) * box(-3.0, 3.0, -2.0, 2.0, -1.0, 2.0)
    return lab(b, spec)


def pinion(spec) -> Part:
    """Helical pinion with its shaft, drawn along +z from its lower end (local frame of the column)."""
    t0, t1 = S.PINION_T
    z0 = 0.0
    g = GR.helical(S.PINION_TEETH, 2 * S.PINION_PITCH_R / S.PINION_TEETH / math.cos(math.radians(20)), 20.0,
                   S.PINION_TEETH_T[1] - S.PINION_TEETH_T[0], hand="right")
    g = g.moved(Location((0, 0, S.PINION_TEETH_T[0] - t0)))
    sh = zrev([(0, 0), (10.0, 0), (10.0, S.PINION_TEETH_T[0] - t0 + 0.01), (0, S.PINION_TEETH_T[0] - t0 + 0.01)])
    sh = sh + zrev([(0, S.PINION_TEETH_T[1] - t0 - 0.01), (12.5, S.PINION_TEETH_T[1] - t0 - 0.01), (12.5, 52.0 - t0),
                    (9.5, 56.0 - t0), (9.5, t1 - t0 - 1.0), (8.5, t1 - t0), (0, t1 - t0)])
    sh = sh + GR.spline_shaft(18, 19.0, 17.2, 22.0).moved(Location((0, 0, t1 - t0 - 23.0)))
    sh = sh - box(-20, 20, 7.0, 20, t1 - t0 - 18.0, t1 - t0 - 9.0)          # cut-out for the pinch bolt (Sec 17 para 3)
    p = g + sh
    return lab(p, spec)


def pinion_bearing(spec) -> Part:
    from mgb import bearings as BR
    return lab(BR.ball_bearing(25.0, 47.0, 12.0), spec)


def end_cover(spec) -> Part:
    """Item 18: plate over the lower end of the pinion bore, two bolts (drawn on +z from its inner face)."""
    t = spec.nom("thickness")
    c = zprism(hull(circle_pts(0, 24, 8.0, 12) + circle_pts(0, -24, 8.0, 12) + circle_pts(0, 0, 25.0, 30)), -t, 0)
    c = c + zcyl(14.0, -t - 3.0, -t + 0.01)
    for y in (24.0, -24.0):
        c = c - zcyl(3.3, -t - 4, 1, 0, y)
    return lab(c, spec)


def damper_cover(spec) -> Part:
    t = spec.nom("thickness")
    c = zprism(hull(circle_pts(21, 0, 7.5, 12) + circle_pts(-21, 0, 7.5, 12) + circle_pts(0, 0, 24.0, 30)), -t, 0)
    for x in (21.0, -21.0):
        c = c - zcyl(3.3, -t - 1, 1, x, 0)
    return lab(c, spec)


def yoke(spec) -> Part:
    """Item 5: the damper yoke pressing the rack against the pinion, its pad (6) and spring (7) inside the boss."""
    y = zrev([(0, 0), (16.6, 0), (16.6, 18.0), (0, 18.0)]) - Location((0, 0, 18.0)) * Rot(90, 0, 0) * zcyl(S.RACK_R + 0.3, -20, 20)
    return lab(y, spec)


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


def lubricator(spec):
    n = hexagon(7.9, 5.0) + zcyl(3.0, -6.0, 0.01) + zcyl(2.6, 4.99, 9.0) + Location((0, 0, 10.0)) * __import__("build123d").Sphere(3.2)
    return lab(n - zcyl(1.0, -7, 14), spec)


# ---- mounting brackets and shims ------------------------------------------------------------------------------
def rack_bracket(spec) -> Part:
    """Strap over the housing pad, a foot each side drilled for the vertical bolt into the crossmember boss
    (drawn at the left-hand clamp, car frame)."""
    y = FS.RACK_CLAMP_Y
    zb = FS.RACK_BOSS_TOP + FS.RACK_SHIM_T
    w = 24.0
    t = 3.5
    ring = ycyl(HR + t, y - w / 2, y + w / 2, RX, RZ) - ycyl(HR + 0.05, y - w / 2 - 1, y + w / 2 + 1, RX, RZ)
    ring = ring & box(RX - 40, RX + 40, y - w, y + w, RZ - 1.0, RZ + 40)
    legs = box(RX - HR - t, RX - HR, y - w / 2, y + w / 2, zb, RZ) + box(RX + HR, RX + HR + t, y - w / 2, y + w / 2, zb, RZ)
    legs = legs - box(RX - HR - 0.01, RX - HR + 0.0, y - w, y + w, zb - 1, RZ)
    feet = box(RX - FS.RACK_BOLT_DX - 11.0, RX - HR, y - w / 2, y + w / 2, zb, zb + t) + box(RX + HR, RX + FS.RACK_BOLT_DX + 11.0, y - w / 2, y + w / 2, zb, zb + t)
    b = ring + legs + feet
    for dx in (-FS.RACK_BOLT_DX, FS.RACK_BOLT_DX):
        b = b - zcyl(4.3, zb - 1, zb + t + 1, RX + dx, y)
    return lab(b, spec)


def shim(spec) -> Part:
    y = FS.RACK_CLAMP_Y
    t = spec.nom("thickness")
    s = box(RX - FS.RACK_BOLT_DX - 11.0, RX + FS.RACK_BOLT_DX + 11.0, y - 12.0, y + 12.0, FS.RACK_BOSS_TOP, FS.RACK_BOSS_TOP + t)
    for dx in (-FS.RACK_BOLT_DX, FS.RACK_BOLT_DX):
        s = s - zcyl(4.3, FS.RACK_BOSS_TOP - 1, FS.RACK_BOSS_TOP + 1, RX + dx, y)
    s = s - zcyl(1.6, FS.RACK_BOSS_TOP - 1, FS.RACK_BOSS_TOP + 1, RX, y)      # rivet hole (73)
    return lab(s, spec)


# =================================================================================================
# ball housing (25), locknut (26), tie-rod (22), outer ball joint (30-34), nuts (35, 36), gaiter (27), clips (28, 29)
# =================================================================================================
def ball_housing(spec) -> Part:
    """On the left-hand rack end (car frame); the right is the same part turned round."""
    y0, y1 = S.BALL_HOUSING_Y
    h = ycyl(17.0, y0, y1 - 6.0, RX, RZ) + yrev([(0, y1 - 6.0), (17.0, y1 - 6.0), (11.0, y1), (0, y1)]).moved(Location((RX, 0, RZ)))
    for k in range(6):
        a = 30.0 + 60.0 * k
        h = h - Location((RX, 0, RZ)) * Rot(0, a, 0) * box(16.0, 18.0, y0 + 2.0, y1 - 8.0, -3.0, 3.0)   # spanner flats
    h = h - ycyl(S.TIE_ROD_R + 1.5, y1 - 7.0, y1 + 1, RX, RZ)
    return lab(h, spec)


def ball_locknut(spec) -> Part:
    y0 = S.HOUSING_Y[1] + 0.5
    n = ycyl(17.5, y0, y0 + 3.5, RX, RZ) - ycyl(S.RACK_R + 0.3, y0 - 1, y0 + 5, RX, RZ)
    for k in range(4):
        n = n - Location((RX, 0, RZ)) * Rot(0, 45 + 90 * k, 0) * box(14.0, 18.0, y0 - 1, y0 + 5, -2.0, 2.0)
    return lab(n, spec)


def _tie_rod_ends():
    a = (RX, S.INNER_BALL_Y, RZ)
    b = (S.OUTER_BALL[0], S.OUTER_SHANK_Y, S.OUTER_BALL[2])
    return a, b


def tie_rod(spec, side=1) -> Part:
    a, b = _tie_rod_ends()
    t = rod(a, b, S.TIE_ROD_R)
    t = t + Location(a) * __import__("build123d").Sphere(13.0)
    # rolled thread on the outer end (the ball joint screws on)
    v = Vector(*b) - Vector(*a)
    L_ = v.length
    for k in range(18):
        p = Vector(*a) + v * ((L_ - 2.0 - k * 1.27) / L_)
        t = t - frame_to(tuple(p), tuple(v)) * zrev([(S.TIE_ROD_R - 0.5, 0), (S.TIE_ROD_R + 1, -0.3), (S.TIE_ROD_R + 1, 0.3)])
    return lab(side_of(t, side), spec)


def outer_joint(spec, side=1) -> Part:
    """Item 30: forged body with its socket under the steering lever, the threaded shank toward the tie-rod, the
    ball pin up through the lever's taper; the boot (31), retainer (32) and garter spring (33) round the pin."""
    bx, by, bz = S.OUTER_BALL
    sy = S.OUTER_SHANK_Y
    body = zrev([(0, -14.0), (17.0, -14.0), (19.0, -6.0), (19.0, 6.0), (15.0, 10.0), (0, 10.0)]).moved(Location((bx, by, bz)))
    body = body + yprism(hull(circle_pts(bx, bz, 12.0, 20) + circle_pts(bx, bz - 2.0, 10.0, 16)), sy + 10.0, by)
    body = body + ycyl(11.0, sy - 0.01, sy + 26.0, bx, bz)                   # threaded socket for the tie-rod
    body = body - ycyl(S.TIE_ROD_R + 0.3, sy - 1, sy + 24.0, bx, bz)
    body = body + zcyl(15.0, bz - 17.0, bz - 13.5, bx, by)                   # pressed bottom plate
    # boot and pin
    ez = FS.ARM_BALL[2] - 8.0                                                # underside of the lever's eye
    boot = zrev([(6.5, bz + 9.0), (16.0, bz + 9.0), (17.0, bz + 13.0), (12.0, ez - 1.0), (6.5, ez - 1.0)]).moved(Location((bx, by, 0)))
    boot = boot + zrev([(16.0, bz + 8.5), (18.0, bz + 8.5), (18.0, bz + 11.5), (16.0, bz + 11.5)]).moved(Location((bx, by, 0)))
    pin = zrev([(0, bz), (7.5, bz), (7.3, ez - 0.5), (7.2, ez), (5.9, FS.ARM_BALL[2] + 9.0), (5.5, FS.ARM_BALL[2] + 9.0),
                (5.5, FS.ARM_BALL[2] + 22.0), (4.8, FS.ARM_BALL[2] + 23.0), (0, FS.ARM_BALL[2] + 23.0)]).moved(Location((bx, by, 0)))
    pin = pin + Location((bx, by, bz)) * __import__("build123d").Sphere(11.0)
    j = body + boot + pin
    return lab(side_of(j, side), spec)


def gaiter(spec, side=1) -> Part:
    """Item 27: convoluted rubber gaiter from the housing's end collar to the tie-rod (left-hand, car frame)."""
    y0 = S.HOUSING_Y[1] - 14.0
    a, b = _tie_rod_ends()
    y1 = y0 + spec.nom("length")
    n = 9
    prof = [(HR + 2.6, y0), (HR + 4.2, y0), (HR + 4.2, y0 + 12.0)]
    for k in range(n):
        f = k / (n - 1)
        r_out = HR + 6.0 - (HR + 6.0 - (S.TIE_ROD_R + 7.0)) * f
        r_in = r_out - 6.0
        yy = y0 + 14.0 + (y1 - y0 - 30.0) * k / (n - 1)
        prof += [(r_out, yy), (max(r_in, S.TIE_ROD_R + 2.0), yy + (y1 - y0 - 30.0) / (n - 1) / 2)]
    prof += [(S.TIE_ROD_R + 2.6, y1 - 12.0), (S.TIE_ROD_R + 2.6, y1), (S.TIE_ROD_R + 0.3, y1), (S.TIE_ROD_R + 0.3, y1 - 12.0)]
    inner = [(r - 1.6, y) for r, y in reversed(prof[3:-4])]
    g = yrev(prof[:-2] + [(S.TIE_ROD_R + 0.3, y1), (S.TIE_ROD_R + 0.3, y1 - 12.0)] + inner + [(HR + 2.6, y0 + 12.0)])
    # tilt to follow the tie-rod (it drops toward the outer joint)
    ang = math.degrees(math.atan2(b[2] - a[2], b[1] - a[1]))
    g = Location((RX, 0, RZ)) * Location((0, a[1], 0)) * Rot(ang, 0, 0) * Location((0, -a[1], 0)) * g
    return lab(side_of(g, side), spec)


def clip(r_in, w):
    def b(spec) -> Part:
        c = zrev([(r_in, 0), (r_in + 1.0, 0), (r_in + 1.0, w), (r_in, w)])
        c = c + Location((r_in + 1.0, 0, w / 2)) * box(0, 5.0, -3.0, 3.0, -w / 2, w / 2)
        c = c + Location((r_in + 5.0, 0, w / 2)) * Rot(0, 90, 0) * zcyl(1.6, -1.0, 7.0)
        return lab(c, spec)
    return b


def nyloc(size):
    def b(spec):
        d = F.THREADS[size][0] * IN
        n = F.hex_nut(size) + zcyl(F.NUT[size][0] * IN / 2 * 0.92, F.NUT[size][1] * IN - 0.01, F.NUT[size][1] * IN + 3.5)
        return lab(n - zcyl(d / 2 * 0.92, -1, 20), spec)
    return b


def plain_washer(size):
    def b(spec):
        return lab(F.plain_washer(size), spec)
    return b


# =================================================================================================
# universal joint (40-48), column (50, 52-54), clamps (59-69)
# =================================================================================================
UJ_R = 22.0


def uj_yoke(spec) -> Part:
    """Item 41: a split, splined boss with the pinch bolt lug and two ears with the journal cup bores (along
    +z from the boss end; the ears at the top, spanning local y)."""
    hb = 26.0
    y = zrev([(9.0, 0), (17.0, 0), (17.0, hb), (9.0, hb)])
    y = y + box(-6.0, 6.0, 12.0, 26.0, 0, hb)                                 # pinch bolt lug
    y = y - box(-1.2, 1.2, 8.0, 30.0, -1, hb + 1)                              # the split
    y = y - Location((0, 20.0, hb * 0.55)) * Rot(0, 90, 0) * zcyl(4.3, -10, 10)  # pinch bolt hole across the split
    for s in (1, -1):
        ear = box(-11.0, 11.0, s * UJ_R - 4.0, s * UJ_R + 4.0, hb - 1.0, hb + 18.0) if s > 0 else box(-11.0, 11.0, -UJ_R - 4.0, -UJ_R + 4.0, hb - 1.0, hb + 18.0)
        ear = ear + Location((0, s * UJ_R, hb + 18.0)) * Rot(90, 0, 0) * zcyl(11.0, -4.0, 4.0)
        ear = ear - Location((0, s * UJ_R, hb + 18.0)) * Rot(90, 0, 0) * zcyl(7.3, -5.0, 5.0)
        y = y + ear
    y = y + zrev([(9.0, hb - 0.01), (17.0, hb - 0.01), (14.0, hb + 4.0), (9.0, hb + 4.0)])
    y = y - GR.spline_bore(18, 19.0, 17.2, hb + 2).moved(Location((0, 0, -1.0)))
    return lab(y, spec)


def uj_spider(spec) -> Part:
    """Item 42: journal with four bearing cups (drawn at the joint centre, arms along x and y)."""
    c = box(-9.0, 9.0, -9.0, 9.0, -9.0, 9.0)
    for a in (0, 90, 180, 270):
        arm = Rot(0, 0, a) * (Location((0, 0, 0)) * Rot(0, 90, 0) * zcyl(5.5, 0, UJ_R - 4.0))
        cup = Rot(0, 0, a) * (Location((UJ_R - 5.5, 0, 0)) * Rot(0, 90, 0) * (zcyl(7.2, 0, 9.5) - zcyl(5.6, -1, 8.0)))
        c = c + arm + cup
    c = c + Location((6.0, 6.0, 6.0)) * __import__("build123d").Sphere(2.6)      # lubricator boss
    return lab(c, spec)


def inner_column(spec) -> Part:
    """Item 50 (RHD): from the joint's splines to the wheel's splined, threaded top (along +z from its lower end)."""
    L_ = S.COLUMN_TOP_T - S.COLUMN_T0
    r = S.INNER_SHAFT_R
    c = zrev([(0, 0), (8.2, 0), (8.6, 24.0), (r, 30.0), (r, L_ - 70.0), (r + 2.5, L_ - 64.0), (r + 2.5, L_ - 48.0), (11.0, L_ - 44.0),
              (11.0, L_ - 20.0), (7.1, L_ - 18.0), (7.1, L_), (0, L_)])
    c = c + GR.spline_shaft(18, 19.0, 17.2, 22.0).moved(Location((0, 0, 1.0)))
    c = c + GR.spline_shaft(36, 24.0, 22.4, 24.0).moved(Location((0, 0, L_ - 44.0)))
    c = c - box(-20, 20, 7.0, 20, 6.0, 15.0)                                   # cut-out for the joint's pinch bolt
    return lab(c, spec)


def outer_tube(spec) -> Part:
    L_ = S.OUTER_TUBE_T[1] - S.OUTER_TUBE_T[0]
    r = S.OUTER_TUBE_R
    t = Sh.tube(2 * r, 2 * r - 2.4, L_)
    t = t + zrev([(r - 1.2, L_ - 30.0), (r + 1.5, L_ - 28.0), (r + 1.5, L_), (r - 1.2, L_)])      # swaged top for the bearing
    return lab(t, spec)


def column_bearing(spec) -> Part:
    r = S.OUTER_TUBE_R
    b = zrev([(S.INNER_SHAFT_R + 0.1, 0), (r - 1.2, 0), (r - 1.2, 22.0), (r + 1.0, 22.0), (r + 1.0, 25.0),
              (S.INNER_SHAFT_R + 0.1, 25.0)])
    return lab(b, spec)


def column_clamp(spec) -> Part:
    """Item 59: two-piece clamp round the outer tube with the flange to the body bracket (drawn on the column
    axis, local x toward the wheel's up)."""
    r = S.OUTER_TUBE_R + 0.2
    w = 30.0
    c = zcyl(r + 4.0, -w / 2, w / 2) - zcyl(r, -w / 2 - 1, w / 2 + 1)
    c = c + box(r, r + 26.0, -18.0, 18.0, -w / 2, w / 2) - box(r - 1, r + 27.0, -1.0, 1.0, -w / 2 - 1, w / 2 + 1)   # flanges up
    c = c - Location((r + 16.0, 0, 0)) * Rot(90, 0, 0) * zcyl(4.3, -20, 20)
    c = c + box(r + 22.0, r + 26.0, -40.0, 40.0, -w / 2, w / 2)                # top plate to the body bracket
    for y in (-30.0, 30.0):
        c = c - Location((r + 20.0, y, 0)) * Rot(0, 90, 0) * zcyl(4.3, 0, 10.0)
    return lab(c, spec)


def bottom_bracket(spec) -> Part:
    """Item 65: plate on the toe board round the tube, two studs (drawn on the column axis)."""
    r = S.OUTER_TUBE_R + 0.3
    p = zprism(hull(circle_pts(0, 0, r + 14.0, 30) + circle_pts(0, 44.0, 9.0, 12) + circle_pts(0, -44.0, 9.0, 12)), 0, 3.0)
    p = p + zcyl(r + 3.0, -14.0, 0.01)
    p = p - zcyl(r, -15.0, 4.0)
    for y in (44.0, -44.0):
        p = p - zcyl(4.2, -1.0, 4.0, 0, y)
    return lab(p, spec)


def blanking_plate(spec) -> Part:
    r = S.OUTER_TUBE_R + 0.3
    p = zprism(hull(circle_pts(0, 0, r + 22.0, 30) + circle_pts(0, 44.0, 12.0, 12) + circle_pts(0, -44.0, 12.0, 12)), 0, 1.5)
    p = p - zcyl(r + 8.0, -1.0, 4.0)
    for y in (44.0, -44.0):
        p = p - zcyl(4.2, -1.0, 4.0, 0, y)
    return lab(p, spec)


def draught_excluder(spec) -> Part:
    r = S.OUTER_TUBE_R
    e = zrev([(r, 0), (r + 18.0, 0), (r + 18.0, 3.0), (r + 8.0, 6.0), (r + 4.0, 16.0), (r + 1.5, 26.0), (r, 26.0)])
    for k in range(3):
        z = 8.0 + k * 5.0
        e = e - zrev([(r + 10.0 - k * 2.0, z), (r + 20.0, z - 1.5), (r + 20.0, z + 1.5)])
    return lab(e, spec)


# =================================================================================================
# steering wheel (57), nut (58), horn push
# =================================================================================================
def steering_wheel(spec) -> Part:
    """Drawn on the column axis with the hub face at z 0, the rim dished toward the driver (+z); spokes of four
    wires each; local x is 'up' with the wheels straight ahead."""
    R = spec.nom("diameter") / 2 - S.RIM_SECTION[0] / 2
    a, b = S.RIM_SECTION[0] / 2, S.RIM_SECTION[1] / 2
    from build123d import Ellipse, Face, Wire, revolve, Axis
    from build123d import Plane as Pl
    rim = zrev([(R + a * math.cos(2 * math.pi * k / 28), S.DISH + b * math.sin(2 * math.pi * k / 28)) for k in range(28)])
    # finger grips under the rim
    for k in range(36):
        ang = 360.0 * k / 36
        rim = rim - Rot(0, 0, ang) * Location((R - a * 0.55, 0, S.DISH - b * 0.6)) * __import__("build123d").Sphere(2.2)
    hub = zrev([(0, -6.0), (24.0, -6.0), (30.0, 0.0), (33.0, 14.0), (27.0, 26.0), (0, 26.0)])
    hub = hub - zcyl(11.5, -7.0, 27.0) - zcyl(16.0, 6.0, 27.0)               # splined bore (drawn plain), nut recess
    w = hub + rim
    # banjo spokes: four spring steel wires each, from the hub's flange to the rim
    for ang in S.SPOKE_ANGLES:
        for k in range(S.SPOKE_WIRES):
            off = (k - (S.SPOKE_WIRES - 1) / 2) * 6.5
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            x0, y0 = 27.0, off * 0.55
            x1, y1 = R - a * 0.85, off
            w = w + rod((x0 * ca - y0 * sa, x0 * sa + y0 * ca, 10.0), (x1 * ca - y1 * sa, x1 * sa + y1 * ca, S.DISH - 2.0), 1.3)
        # the boss the wires are anchored in at the hub
        w = w + Rot(0, 0, ang) * Location((24.0, 0, 10.0)) * box(-3.0, 10.0, -12.0, 12.0, -5.0, 5.0)
    return lab(w, spec)


def wheel_nut(spec):
    d = 9.0 / 16.0 * IN
    return lab(hexagon(F.NUT["9/16"][0] * IN, F.NUT["9/16"][1] * IN) - zcyl(d / 2 * 0.92, -1, 20), spec)


def horn_push(spec) -> Part:
    """Central horn push: a domed black cap carrying the MG badge - an octagon in a bezel (drawn on +z from its
    seat in the hub)."""
    d = spec.nom("diameter")
    c = zrev([(0, 0), (d / 2, 0), (d / 2, 4.0), (d / 2 - 3.0, 9.0), (0, 11.0)])
    from build123d import RegularPolygon, extrude
    oct_ = extrude(RegularPolygon(d * 0.30, 8), 2.2).moved(Location((0, 0, 10.0)))
    oct_ = oct_ - extrude(RegularPolygon(d * 0.30 - 2.0, 8), 3.0).moved(Location((0, 0, 11.4)))
    c = c + oct_
    # raised "MG" bars inside the octagon (two blocks standing for the letters)
    for x in (-4.5, 4.5):
        c = c + box(x - 3.0, x + 3.0, -5.0, 5.0, 10.0, 12.6)
    return lab(c, spec)


PARTS = {
    "chassis.steering.rack-housing": {"build": rack_housing},
    "chassis.steering.rack": {"build": rack},
    "chassis.steering.pinion": {"build": pinion},
    "chassis.steering.pinion-bearing": {"build": pinion_bearing},
    "chassis.steering.end-cover": {"build": end_cover},
    "chassis.steering.end-cover-bolt": {"build": bolt("1/4")},
    "chassis.steering.end-cover-washer": {"build": sw("1/4")},
    "chassis.steering.damper-cover": {"build": damper_cover},
    "chassis.steering.damper-cover-bolt": {"build": bolt("1/4")},
    "chassis.steering.damper-cover-washer": {"build": sw("1/4")},
    "chassis.steering.yoke": {"build": yoke},
    "chassis.steering.lubricator": {"build": lubricator},
    "chassis.steering.bracket": {"build": rack_bracket},
    "chassis.steering.shim": {"build": shim, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "chassis.steering.rack-bolt": {"build": bolt("5/16")},
    "chassis.steering.rack-bolt-washer": {"build": sw("5/16")},
    "chassis.steering.ball-housing": {"build": ball_housing},
    "chassis.steering.ball-locknut": {"build": ball_locknut},
    "chassis.steering.tie-rod": {"build": tie_rod},
    "chassis.steering.outer-joint": {"build": outer_joint},
    "chassis.steering.joint-nut": {"build": nyloc("3/8")},
    "chassis.steering.joint-washer": {"build": plain_washer("3/8")},
    "chassis.steering.tie-rod-locknut": {"build": nut("1/2")},
    "chassis.steering.gaiter": {"build": gaiter},
    "chassis.steering.inner-clip": {"build": clip(S.HOUSING_R + 4.3, 9.0)},
    "chassis.steering.outer-clip": {"build": clip(S.TIE_ROD_R + 2.7, 7.0)},
    "chassis.steering.uj-yoke": {"build": uj_yoke},
    "chassis.steering.uj-spider": {"build": uj_spider},
    "chassis.steering.uj-bolt": {"build": bolt("5/16")},
    "chassis.steering.uj-nut": {"build": nut("5/16")},
    "chassis.steering.uj-washer": {"build": sw("5/16")},
    "chassis.steering.inner-column": {"build": inner_column},
    "chassis.steering.outer-tube": {"build": outer_tube},
    "chassis.steering.upper-bearing": {"build": column_bearing},
    "chassis.steering.lower-bearing": {"build": column_bearing},
    "chassis.steering.column-clamp": {"build": column_clamp},
    "chassis.steering.clamp-bolt": {"build": bolt("5/16")},
    "chassis.steering.clamp-nut": {"build": nut("5/16")},
    "chassis.steering.clamp-washer": {"build": sw("5/16")},
    "chassis.steering.bottom-bracket": {"build": bottom_bracket},
    "chassis.steering.blanking-plate": {"build": blanking_plate},
    "chassis.steering.bracket-nut": {"build": nut("1/4")},
    "chassis.steering.draught-excluder": {"build": draught_excluder},
    "chassis.steering.wheel": {"build": steering_wheel, "probes": {"diameter": lambda p: max(probes.bbox_size(p, "x"), probes.bbox_size(p, "y"))}},
    "chassis.steering.wheel-nut": {"build": wheel_nut},
    "chassis.steering.horn-push": {"build": horn_push},
}
