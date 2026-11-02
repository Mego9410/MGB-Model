"""Front suspension: lever dampers (upper arms), top trunnions, swivel pins and swivel axles, lower wishbones,
coil springs and pans, steering levers and their fixings (Haynes Ch 11 Fig 11.2 items 8-14, 19-63; Fig 11.1;
Secs 4, 5, 9, 14, 15; printed p202-205, 208, 210).

Drawn in the car frame at the left-hand (near side) corner from mgb.front_suspension_layout; every builder
takes `side` (+1 left, -1 right) and mirrors the left-hand solid for the right. The swivel axles are real
handed parts (separate ids, MGOC BTB764 RH / BTB765 LH). Fasteners are drawn at the origin along +z and
placed by the assembly.

Forms:
- damper (8): Armstrong lever-arm unit - a cast body on a flanged base with four bolt lugs, two piston bores
  across it with screwed end caps, the lid with its filler plug (Fig 11.1 item 2) and the shaft boss at the
  outboard end; the forged A-shaped arm pair on the shaft, joined by the centre (pinch) bolt, their eyes
  clamping the fulcrum pin.
- trunnion (59): the top suspension link - a boss on the swivel pin's threaded top with the cross eye for the
  fulcrum pin outboard of it, two rubber bearings (12) in the eye.
- swivel pin (46): the king pin, its base with the cross eye for the pivot bolt (30), a grub screw (48) and
  lubricator (61); cork ring (53), dust excluder tubes (54, 56) and their spring (55) between base and
  swivel axle; the swivel axle's two bushes (50, 51); steel and bronze thrust washers (57, 58) under the
  trunnion; nut (60) on top.
- swivel axle (49): one forging - the bushed pin boss with two lubricator bosses, the stub axle (taper
  bearing seats and 3/4 in thread), the flange face with three tapped pads for the dust cover screws, the
  caliper flange behind the axle with its two bolt holes (P8 datums), and the lug the steering lever bolts
  under.
- lower wishbone (20): two pressed channel arms per side with a bush housing at the inner end and the pivot
  bolt hole at the outer; the pivot (33) bolted under the crossmember with bushes (37), washers (38) and
  castellated nuts (39); the outer pivot bolt (30) through the distance tube (25), thrust washers (26), seals
  (27) and seal supports (28); the spring pan (19) between the arms on four screws.
- coil spring (14): 0.5 in wire, closed and ground ends, drawn free (9.9 in, H) and at the static laden
  length in the assembly.
- steering lever (62): forged lever from the swivel axle lug forward to the tapered eye for the tie-rod ball
  pin, two bolts (63).
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot, Torus, Vector

from mgb import fasteners as F, front_suspension_layout as L, probes, shapes as Sh
from mgb.chassis_geom import (IN, box, castellated_nut, frame_to, hexagon, lab, rod, spring_washer, tube_between,
                              xcyl, xprism, xrev, ycyl, yprism, yrev, zcyl, zprism, zrev)
from mgb.poly2d import circle_pts, hull

KF = L.kp_frame(0.0)                     # king pin frame, left-hand corner: local z up the pin


def side_of(p, side):
    return p if side > 0 else p.mirror(Plane.XZ)


def on_pin(p):
    """A solid drawn in the king pin frame (local z up the pin, 0 at the wheel-centre crossing) -> car frame."""
    return KF * p


# =================================================================================================
# lever damper (8) and its arm
# =================================================================================================
SX, SY, SZ = L.DAMPER_SHAFT
FXu, FYu, FZu = L.TOP_FULCRUM
B0 = L.DAMPER_BASE_Z
AX_ = L.DAMPER_ARM_X


def _damper_body():
    bx = [b[0] for b in L.DAMPER_BOLTS]
    by = [b[1] for b in L.DAMPER_BOLTS]
    lugs = []
    for x, y, _ in L.DAMPER_BOLTS:
        lugs += circle_pts(x, y, 10.0, 16)
    base = zprism(hull(lugs + [(SX - 30, SY - 10), (SX + 30, SY - 10), (SX - 30, SY + 18), (SX + 30, SY + 18)]), B0, B0 + 9.0)
    for x, y, _ in L.DAMPER_BOLTS:
        base = base - zcyl(5.6, B0 - 1, B0 + 10, x, y)
        base = base + zcyl(10.0, B0 + 8.9, B0 + 12.0, x, y) - zcyl(5.6, B0 + 8, B0 + 13, x, y)   # spot faces
    yc0, yc1 = min(by) - 14.0, SY - 8.0
    # the casting: a body between the two piston bores, rising to the lid
    core = box(SX - 34, SX + 34, yc0 + 6, yc1, B0 + 8.9, B0 + 74.0)
    bores = ycyl(21.0, yc0, yc1 + 4, SX - 26.0, B0 + 34.0) + ycyl(21.0, yc0, yc1 + 4, SX + 26.0, B0 + 34.0)
    caps = ycyl(17.0, yc0 - 7.0, yc0 + 0.1, SX - 26.0, B0 + 34.0) + ycyl(17.0, yc0 - 7.0, yc0 + 0.1, SX + 26.0, B0 + 34.0)
    for xx in (SX - 26.0, SX + 26.0):                                     # hexagon on each end cap
        caps = caps + Location((xx, yc0 - 7.0, B0 + 34.0)) * Rot(90, 0, 0) * hexagon(24.0, 4.0)
    shaft_boss = xcyl(25.0, SX - AX_ + 6.5, SX + AX_ - 6.5, SY, SZ)
    web = yprism([(SX - 28, B0 + 9), (SX + 28, B0 + 9), (SX + 28, SZ + 4), (SX - 28, SZ + 4)], yc1 - 2, SY)
    lid = box(SX - 36, SX + 36, yc0 + 4, yc1 + 2, B0 + 73.0, B0 + 79.0)
    body = base + core + bores + caps + shaft_boss + web + lid
    for xx in (SX - 30, SX + 30):                                         # lid screws
        for yy in (yc0 + 9, yc1 - 3):
            body = body + zcyl(4.2, B0 + 79.0, B0 + 82.5, xx, yy)
    body = body + zcyl(9.0, B0 + 79.0, B0 + 85.0, SX, (yc0 + yc1) / 2)   # filler plug boss (Fig 11.1 item 2)
    body = body + Location((SX, (yc0 + yc1) / 2, B0 + 85.0)) * hexagon(14.3, 6.0)
    for k in range(3):                                                    # cast ribs down the sides
        y = yc0 + 16 + k * 18
        body = body + yprism([(SX - 37, B0 + 9.5), (SX - 33.5, B0 + 9.5), (SX - 33.5, B0 + 70), (SX - 37, B0 + 60)], y, y + 4)
        body = body + yprism([(SX + 33.5, B0 + 9.5), (SX + 37, B0 + 9.5), (SX + 37, B0 + 60), (SX + 33.5, B0 + 70)], y, y + 4)
    return body


def _arm_pair():
    """The A-shaped forged arms, front and rear of the body, from the shaft to the fulcrum pin."""
    arms = None
    for s in (-1, 1):
        x0 = SX + s * AX_ - 6.0
        a = xprism(hull(circle_pts(SY, SZ, 21.0, 28) + circle_pts(FYu, FZu, 15.0, 24)), x0, x0 + 12.0)
        a = a - xprism(hull(circle_pts(SY + 40, SZ - 2, 4.0, 10) + circle_pts(FYu - 46, FZu + 10, 3.5, 10)), x0 + 9.0, x0 + 13.0)
        a = a - xprism(hull(circle_pts(SY + 40, SZ - 2, 4.0, 10) + circle_pts(FYu - 46, FZu + 10, 3.5, 10)), x0 - 1.0, x0 + 3.0)
        a = a - xcyl(F.THREADS["1/2"][0] * IN / 2 + 0.2, x0 - 1, x0 + 13, FYu, FZu)   # fulcrum pin eye
        arms = a if arms is None else arms + a
    # centre bolt boss half way along each arm (the "bolt in the centre of the A")
    t = 0.62
    my, mz = SY + (FYu - SY) * t, SZ + (FZu - SZ) * t
    for s in (-1, 1):
        x0 = SX + s * AX_
        arms = arms + xcyl(9.0, x0 - 6.0, x0 + 6.0, my, mz) if s < 0 else arms + xcyl(9.0, x0 - 6.0, x0 + 6.0, my, mz)
        arms = arms - xcyl(4.2, x0 - 7.0, x0 + 7.0, my, mz)
    return arms


CENTRE_BOLT = (SX, SY + (FYu - SY) * 0.62, SZ + (FZu - SZ) * 0.62)


def damper(spec, side=1) -> Part:
    d = _damper_body() + _arm_pair() + xcyl(15.0, SX - AX_ - 6.0, SX + AX_ + 6.0, SY, SZ)
    return lab(side_of(d, side), spec)


def damper_bolt(spec):
    return lab(F.hex_bolt("3/8", spec.nom("length") / IN), spec)


def sw38(spec):
    return lab(spring_washer("3/8"), spec)


def damper_centre_bolt(spec):
    return lab(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def nut516(spec):
    return lab(F.hex_nut("5/16"), spec)


def sw516(spec):
    return lab(spring_washer("5/16"), spec)


# =================================================================================================
# fulcrum pin (11), bearings (12), castellated nut (13); trunnion (59) and nut (60)
# =================================================================================================
def fulcrum_pin(spec) -> Part:
    """Along +z from the head's underside: head, plain shank, 1/2 UNF thread with split pin hole."""
    L_ = spec.nom("length")
    d = F.THREADS["1/2"][0] * IN
    p = hexagon(F.BOLT_HEAD["1/2"][0] * IN, F.BOLT_HEAD["1/2"][1] * IN, -F.BOLT_HEAD["1/2"][1] * IN)
    p = p + Sh.chamfered_cyl(d, L_, 0.8, top=True, bottom=False)
    p = p - Location((0, 0, L_ - 4.0)) * Rot(90, 0, 0) * zcyl(1.6, -10, 10)
    return lab(p, spec)


def bearing12(spec) -> Part:
    """Rubber top-hat bearing in the trunnion eye (along +z from its flange's outer face)."""
    od, idd, L_ = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    b = zrev([(idd / 2, 0), (od / 2 + 4.0, 0), (od / 2 + 4.0, 3.0), (od / 2, 3.0), (od / 2, L_), (idd / 2, L_)])
    return lab(b, spec)


def castle_nut(size, af_in):
    def b(spec):
        d = F.THREADS[size][0] * IN
        return lab(castellated_nut(af_in * IN, d * 0.95, d * 0.92), spec)
    return b


def split_pin(spec) -> Part:
    L_ = spec.nom("length")
    d = spec.nom("diameter")
    p = (Location((0, 0, 0)) * Torus(d * 0.55, d / 4)).moved(Location((-d * 0.5, 0, 0))) + xcyl(d / 4, -d * 0.5, L_, d * 0.3, 0) + xcyl(d / 4, -d * 0.5, L_ * 0.85, -d * 0.3, 0)
    return lab(p, spec)


TR_H0, TR_H1 = L.TRUNNION_H0, L.TRUNNION_TOP_H


def trunnion(spec, side=1) -> Part:
    """Item 59, drawn in the king pin frame then moved to the car frame."""
    eye_out = L.TRUNNION_EYE_OUT
    hc = L.TOP_FULCRUM_H
    t = zrev([(F.THREADS[L.PIN_THREAD][0] * IN / 2 + 0.4, TR_H0), (17.0, TR_H0), (17.0, TR_H1 - 3.0), (14.0, TR_H1),
              (F.THREADS[L.PIN_THREAD][0] * IN / 2 + 0.4, TR_H1)])
    t = on_pin(t)
    ex, ey, ez = L.TOP_FULCRUM
    half = AX_ - 6.0 - 3.0
    eye = xcyl(19.0, ex - half, ex + half, ey, ez)
    web = xprism(hull(circle_pts(ey, ez, 15.0, 20) + [(L.kp(hc)[1] - 4.0, ez - 22.0), (L.kp(hc)[1] - 4.0, ez + 12.0)]), ex - 15.0, ex + 15.0)
    t = t + eye + web
    t = t - xcyl(13.0, ex - half - 1, ex + half + 1, ey, ez)                                   # bore for the bearings
    t = t - on_pin(zcyl(F.THREADS[L.PIN_THREAD][0] * IN / 2 + 0.4, TR_H0 - 1, TR_H1 + 1))
    return lab(side_of(t, side), spec)


def pin_nut(spec):
    return lab(castellated_nut(F.NUT[L.PIN_THREAD][0] * IN, F.NUT[L.PIN_THREAD][1] * IN * 1.25,
                               F.THREADS[L.PIN_THREAD][0] * IN * 0.92), spec)


def pin_washer(spec):
    return lab(F.plain_washer(L.PIN_THREAD), spec)


# =================================================================================================
# swivel pin (46), grub screw (48), lubricator (52, 61), cork ring (53), dust excluders (54-56), bushes (50, 51),
# thrust washers (57, 58)
# =================================================================================================
def swivel_pin(spec, side=1) -> Part:
    r = L.PIN_D / 2
    rt = F.THREADS[L.PIN_THREAD][0] * IN / 2
    h0 = L.LOWER_EYE_H
    p = zrev([(0, h0), (16.0, h0), (16.0, L.PIN_BASE_TOP_H - 2.0), (14.0, L.PIN_BASE_TOP_H), (r, L.PIN_BASE_TOP_H),
              (r, TR_H0 - 0.6), (r - 1.2, TR_H0), (rt, TR_H0), (rt, L.PIN_TOP_H - 1.0), (rt - 1.0, L.PIN_TOP_H), (0, L.PIN_TOP_H)])
    p = on_pin(p)
    ex, ey, ez = L.LOWER_PIVOT
    eye = xcyl(19.0, ex - L.EYE_HALF, ex + L.EYE_HALF, ey, ez)
    p = p + eye
    p = p - xcyl(11.2, ex - L.EYE_HALF - 1, ex + L.EYE_HALF + 1, ey, ez)                     # bore for the distance tube
    p = p - on_pin(Location((0, 0, L.PIN_TOP_H - 6.0)) * Rot(90, 0, 0) * zcyl(1.6, -10, 10))  # split pin hole
    p = p + zcyl(5.0, ez - 26.0, ez - 17.0, ex + 8.0, ey)                                    # lubricator boss under the eye
    p = p - zcyl(2.6, ez - 27.0, ez - 10.0, ex + 8.0, ey)
    p = p + xcyl(6.0, ex - 14.0, ex - 4.0, ey, ez + 17.0)                                     # grub screw boss
    return lab(side_of(p, side), spec)


def grub_screw(spec):
    L_ = spec.nom("length")
    d = F.THREADS["1/4"][0] * IN
    g = zcyl(d / 2, 0, L_) - box(-d, d, -0.5, 0.5, L_ - 1.5, L_ + 1)
    return lab(g, spec)


def lubricator(spec):
    """Grease nipple: hex body, thread below, ball head (along +z from the seat face)."""
    n = hexagon(7.9, 5.0) + zcyl(3.0, -6.0, 0.01) + zcyl(2.6, 4.99, 9.0) + Location((0, 0, 10.0)) * __import__("build123d").Sphere(3.2)
    n = n - zcyl(1.0, -7, 14)
    return lab(n, spec)


def cork_ring(spec):
    return lab(Sh.tube(spec.nom("outside_diameter"), L.PIN_D + 0.4, spec.nom("thickness")), spec)


def dust_tube(spec):
    od, L_ = spec.nom("outside_diameter"), spec.nom("length")
    t = 1.0
    p = zrev([(od / 2 - t, 0), (od / 2, 0), (od / 2, L_), (L.PIN_D / 2 + 0.6, L_), (L.PIN_D / 2 + 0.6, L_ - t),
              (od / 2 - t, L_ - t)])
    return lab(p, spec)


def dust_spring(spec):
    return lab(Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), spec.nom("length"), 7.0, 0.75), spec)


def bush(spec):
    od, idd, L_ = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    b = Sh.tube(od, idd, L_) - zrev([(idd / 2 - 0.1, L_ * 0.3), (idd / 2 + 0.8, L_ * 0.3), (idd / 2 + 0.8, L_ * 0.7), (idd / 2 - 0.1, L_ * 0.7)])
    return lab(b, spec)


def thrust_washer(spec):
    return lab(Sh.tube(spec.nom("outside_diameter"), L.PIN_D + 0.3, spec.nom("thickness")), spec)


# =================================================================================================
# swivel axle (49), LH and RH; stub axle with its bearing seats and thread
# =================================================================================================
def _swivel_axle_left():
    from mgb import front_suspension_layout as Lf
    FX, FZ = Lf.FX, Lf.FZ
    h0, h1 = L.SWIVEL_H
    boss = on_pin(zrev([(13.0, h0), (26.0, h0), (26.0, h1), (13.0, h1)]))
    # lubricator bosses top and bottom (Fig 11.2 items 52; Sec 15 extra nipple on the lower bush)
    for h in (h1 - 14.0, h0 + 14.0):                                    # facing forward (Sec 15: LH lower drilling)
        p = Vector(*L.kp(h))
        boss = boss + Location((p.X + 24.0, p.Y, p.Z)) * Rot(0, 90, 0) * zcyl(6.0, -4.0, 6.0)
    # flange face plate behind the dust cover, on the stub axle root
    yf = L.SHIELD_FACE_Y
    fl = ycyl(L.SHIELD_SCREW_R + 9.0, yf - 10.0, yf - 4.0, FX, FZ)
    for a in L.SHIELD_SCREW_ANGLES:
        x, z = L.ang(L.SHIELD_SCREW_R, a)
        fl = fl + ycyl(9.0, yf - 10.0, yf, FX + x, FZ + z) - ycyl(3.2, yf - 12.0, yf + 1, FX + x, FZ + z)
    # web from the pin boss to the flange face
    web = yprism(hull(circle_pts(0.0, 0.0, 40.0, 24) + [(-30.0, 60.0), (30.0, 60.0), (-30.0, -62.0), (30.0, -62.0)]), L.KP_Y0 + 6.0, yf - 9.0)
    web = web.moved(Location((FX, 0, FZ)))
    # caliper flange (P8: outboard face CALIPER_MOUNT_FACE_Y, thickness SWIVEL_CALIPER_FLANGE_T)
    cy1 = L.CALIPER_MOUNT_FACE_Y
    cy0 = cy1 - L.SWIVEL_CALIPER_FLANGE_T
    pts = []
    for v in (-L.LUG_V, L.LUG_V):
        x, z = L.uv(L.LUG_U[0] + 8.0, v)
        pts += circle_pts(x, z, 15.0, 20)
    pts += [(-20.0, 45.0), (-20.0, -45.0)]
    cf = yprism(hull(pts), cy0, cy1).moved(Location((FX, 0, FZ)))
    for v in (-L.LUG_V, L.LUG_V):
        x, z = L.uv(L.LUG_U[0] + 8.0, v)
        cf = cf - ycyl(F.THREADS[L.CALIPER_BOLT][0] * IN / 2 + 0.4, cy0 - 1, cy1 + 1, FX + x, FZ + z)
    # stub axle (taper bearing seats, spacer journal, thread), revolved about the wheel axis
    r_in = L.IN_BRG[0] / 2
    r_out = L.OUT_BRG[0] / 2
    rt = 0.75 * IN / 2
    stub = yrev([(0, yf - 6.0), (27.0, yf - 6.0), (27.0, yf), (r_in + 3.0, yf),
                 (r_in + 3.0, L.COLLAR_Y[1] - 0.5), (r_in, L.COLLAR_Y[1]), (r_in, L.SPACER_Y[0] + 18.0),
                 (r_out + 3.0, L.OUT_BRG_Y[0] - 10.0), (r_out + 3.0, L.OUT_BRG_Y[0] - 2.0), (r_out, L.OUT_BRG_Y[0] - 1.0),
                 (r_out, L.WASHER_Y[1]),
                 (rt, L.WASHER_Y[1]), (rt, L.STUB_END_Y - 1.0), (rt - 1.0, L.STUB_END_Y), (0, L.STUB_END_Y)])
    stub = stub.moved(Location((FX, 0, FZ)))
    stub = stub - xcyl(1.8, FX - 15, FX + 15, L.STUB_END_Y - 3.5, FZ)                     # split pin hole (along x)
    stub = stub - box(FX - 1.5, FX + 1.5, L.WASHER_Y[0] - 6.0, L.STUB_END_Y + 1, FZ + rt - 2.0, FZ + rt + 1)   # washer key slot
    # steering lever lug, under the front of the swivel axle
    lz = FZ + L.ARM_PAD_H
    lug = box(FX + 14.0, L.ARM_BOLT_X[1] + 14.0, 480.0, 518.0, lz, lz + 20.0)
    lug = lug + yprism([(FX + 4.0, lz + 19.0), (L.ARM_BOLT_X[0], lz + 19.0), (FX + 4.0, lz + 56.0)], 484.0, 514.0)
    for x in L.ARM_BOLT_X:
        lug = lug - zcyl(F.THREADS["7/16"][0] * IN / 2 * 0.85, lz - 1, lz + 19.0, x, 499.0)
    s = boss + fl + web + cf + stub + lug
    # pin bore and bush counterbores
    s = s - on_pin(zcyl(12.7 + 0.05, h0 - 1, h1 + 1))
    # lubricator drillings
    for h in (h1 - 14.0, h0 + 14.0):
        p = Vector(*L.kp(h))
        s = s - Location((p.X + 24.0, p.Y, p.Z)) * Rot(0, 90, 0) * zcyl(2.6, -10.0, 8.0)
    return s


def swivel_axle(hand):
    def b(spec) -> Part:
        s = _swivel_axle_left()
        return lab(s if hand == "left" else s.mirror(Plane.XZ), spec)
    return b


def shield_screw_note():
    pass


# =================================================================================================
# lower wishbone: arms (20), pivot (33), bolts (34-36), bushes (37), washers (38), nuts (39), outer pivot bolt
# (30), nut (31), washer (32), distance tube (25), thrust washers (26), seals (27), seal supports (28),
# spring pan (19), screws (21, 22), nuts (23), washers (24)
# =================================================================================================
WI = L.WISHBONE_INNER
LP = L.LOWER_PIVOT


def arm_ends(s):
    """Inner and outer centres of the front (s +1) or rear (s -1) arm's web."""
    return ((WI[0] + s * L.WISHBONE_ARM_X, WI[1], WI[2]), (LP[0] + s * L.WISHBONE_OUT_X, LP[1], LP[2]))


ARM_T = 3.5
ARM_DEPTH = 38.0
PAN_SCREW_Y = (L.PAN_Y - 48.0, L.PAN_Y + 48.0)


def arm_x_at(s, y):
    return L.arm_x(s, y)


def wishbone_arm(spec, side=1, fore=1) -> Part:
    """Pressed channel arm: a web in a near-vertical plane, flanges turned away from the pan along the top
    and bottom edges, the bush housing at the inner end and the pivot bolt hole at the outer. `fore` +1 is
    the front arm, -1 the rear (the same pressing turned over)."""
    s = fore
    p0, p1 = arm_ends(s)
    d = Vector(*p1) - Vector(*p0)
    Lg = d.length
    loc = Location(Plane(origin=p0, x_dir=d.normalized(), z_dir=(Vector(0, 0, 1) - d.normalized() * d.normalized().Z).normalized()))
    # local frame: x along the arm, z up, y = z cross x (points toward -car x for a left arm, roughly)
    out = 1.0 if s > 0 else -1.0
    prof = hull(circle_pts(0, 0, 22.0, 24) + circle_pts(Lg, 0, 20.0, 24) + [(Lg * 0.55, -ARM_DEPTH / 2 - 4), (Lg * 0.55, ARM_DEPTH / 2 + 2)])
    web = Location((0, 0, 0)) * Rot(90, 0, 0) * zprism(prof, -ARM_T / 2, ARM_T / 2)
    a = web
    # top and bottom flanges, outward (away from the pan): local +y is car -x
    ya, yb = (-14.0, 0.0) if s > 0 else (0.0, 14.0)
    for z0_, z1_ in ((ARM_DEPTH / 2 - ARM_T, ARM_DEPTH / 2), (-ARM_DEPTH / 2, -ARM_DEPTH / 2 + ARM_T)):
        a = a + box(30.0, Lg - 26.0, ya, yb, z0_, z1_)
    # pan screw holes (two) and lightening holes along the web
    for yy in PAN_SCREW_Y:                                               # pan screw holes, on the pan's
        t = (yy - p0[1]) / (p1[1] - p0[1])
        zz = L.wishbone_z(yy) + 4.0 - (p0[2] + (p1[2] - p0[2]) * t)
        a = a - Location((Lg * t, 0, zz)) * Rot(90, 0, 0) * zcyl(4.2, -10, 10)
    a = a - Location((Lg * 0.25, 0, 0)) * Rot(90, 0, 0) * zcyl(8.0, -10, 10)
    a = a - Location((Lg * 0.88, 0, 2.0)) * Rot(90, 0, 0) * zcyl(6.0, -10, 10)
    a = a - Location((Lg, 0, 0)) * Rot(90, 0, 0) * zcyl(8.1, -10, 10)                   # pivot bolt hole
    a = loc * a
    # bush housing along car x at the inner end (welded tube)
    x0, y0, z0 = p0
    a = a - xcyl(18.0, x0 - 20, x0 + 20, y0, z0)
    a = a + xcyl(19.5, x0 - 14.0, x0 + 14.0, y0, z0) - xcyl(16.0, x0 - 15.0, x0 + 15.0, y0, z0)
    return lab(side_of(a, side), spec)


def wishbone_pivot(spec, side=1) -> Part:
    """Item 33: a forged bar along x - a flat centre drilled for the two bolts up into the crossmember, plain
    journals either side for the arms' bushes and threaded ends with split pin holes."""
    x0, y0, z0 = WI
    rt = F.THREADS["5/8"][0] * IN / 2
    p = None
    for s in (-1, 1):
        xa = x0 + s * (L.WISHBONE_ARM_X - 16.0)
        xb = x0 + s * (L.WISHBONE_ARM_X + 32.0)
        # journal for the bush and the threaded end
        jl = x0 + s * (L.WISHBONE_ARM_X + 16.0)
        j = xrev([(0, min(xa, jl)), (11.0, min(xa, jl)), (11.0, max(xa, jl)), (0, max(xa, jl))])
        te = xrev([(0, min(jl, xb)), (rt, min(jl, xb)), (rt, max(jl, xb)), (0, max(jl, xb))])
        part = (j + te).moved(Location((0, y0, z0)))
        part = part - Location((xb - s * 5.0, y0, z0)) * zcyl(1.6, -12, 12)
        p = part if p is None else p + part
    pad = box(x0 - 58.0, x0 + 58.0, y0 - 18.0, y0 + 18.0, z0 - 11.0, L.XM_BOTTOM_Z - 0.3)
    p = p + pad
    for x in L.WISHBONE_PIVOT_BOLTS:
        p = p - zcyl(5.0, z0 - 12, L.XM_BOTTOM_Z + 1, x, y0)
    return lab(side_of(p, side), spec)


def pivot_bush(spec):
    od, idd, L_ = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    b = zrev([(idd / 2, 0), (od / 2 + 3.0, 0), (od / 2 + 3.0, 2.5), (od / 2, 2.5), (od / 2, L_), (idd / 2, L_)])
    return lab(b, spec)


def washer_flat(od, idd):
    def b(spec):
        return lab(Sh.tube(od, idd, spec.nom("thickness")), spec)
    return b


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


def distance_tube(spec):
    L_ = spec.nom("length")
    return lab(Sh.tube(22.2, F.THREADS["5/8"][0] * IN + 0.3, L_), spec)


def seal27(spec):
    od = spec.nom("outside_diameter")
    p = zrev([(11.4, 0), (od / 2, 0), (od / 2, 1.5), (od / 2 - 2.0, 4.5), (13.5, 4.5), (11.4, 2.0)])
    return lab(p, spec)


def seal_support(spec):
    od = spec.nom("outside_diameter")
    p = zrev([(8.3, 0), (od / 2, 0), (od / 2, 4.0), (od / 2 - 1.0, 4.0), (od / 2 - 1.0, 1.0), (8.3, 1.0)])
    return lab(p, spec)


def pan(spec, side=1) -> Part:
    """Item 19: pressed tray between the arms; the spring seat dished down in its middle with a drain hole,
    side flanges up against the arms' inner faces with two holes each."""
    y = L.PAN_Y
    zs = L.PAN_SEAT_Z
    zt = L.wishbone_z(y) + ARM_DEPTH / 2 - 6.0
    xr = arm_x_at(-1, y) + ARM_T / 2 + 0.2
    xf = arm_x_at(1, y) - ARM_T / 2 - 0.2
    w = 58.0
    t = 2.5
    def quad(d):
        return [(arm_x_at(-1, y - w) + ARM_T / 2 + 0.3 + d, y - w + d), (arm_x_at(1, y - w) - ARM_T / 2 - 0.3 - d, y - w + d),
                (arm_x_at(1, y + w) - ARM_T / 2 - 0.3 - d, y + w - d), (arm_x_at(-1, y + w) + ARM_T / 2 + 0.3 + d, y + w - d)]
    outer = zprism(quad(0.0), zs - t, zt)
    inner = zprism(quad(t), zs, zt + 1)
    p = outer - inner
    p = p - box(xr + t + 0.01, xf - t - 0.01, y - w - 1, y + w + 1, zs + 22.0, zt + 1)     # open ends above the seat lip
    p = p + (zcyl(52.0, zs - t, zs + 0.01, (xr + xf) / 2, y) & box(xr, xf, y - w, y + w, zs - t - 1, zs + 1))
    p = p - zrev([(0, zs - t - 1), (27.0, zs - t - 1), (25.0, zs + 0.5), (0, zs + 0.5)]).moved(Location(((xr + xf) / 2, y, 0)))
    p = p + zrev([(29.0, zs - t), (33.5, zs - t), (33.5, zs + 8.0), (31.0, zs + 8.0), (31.0, zs)]).moved(Location(((xr + xf) / 2, y, 0)))
    p = p - zcyl(6.0, zs - t - 2, zs + 2, (xr + xf) / 2, y)
    # flanges: two screw holes each side (to the arms' holes)
    for fore in (-1, 1):
        for yy in PAN_SCREW_Y:
            zz = L.wishbone_z(yy) + 4.0
            xx = arm_x_at(fore, yy)
            p = p - xcyl(4.2, xx - 8, xx + 8, yy, zz)
    return lab(side_of(p, side), spec)


def coil_spring(spec, length=None) -> Part:
    free = spec.nom("free_height")
    Lg = length or free
    s = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), Lg, spec.nom("total_coils"), 0.9)
    return lab(s, spec)


# =================================================================================================
# steering lever (62), bolts (63)
# =================================================================================================
def steering_lever(spec, side=1) -> Part:
    lz = L.FZ + L.ARM_PAD_H
    bx, by, bz = L.ARM_BALL
    t = 12.0
    pts = [(L.ARM_BOLT_X[0] - 14.0, lz), (L.ARM_BOLT_X[1] + 14.0, lz), (bx - 30.0, bz + 10.0), (bx, bz)]
    path_y = 499.0
    # flat pad under the swivel axle lug, then a cranked forged arm down and forward to the eye
    p = box(L.ARM_BOLT_X[0] - 13.0, L.ARM_BOLT_X[1] + 13.0, path_y - 17.0, path_y + 17.0, lz - t, lz - 0.3)
    p = p + rod((L.ARM_BOLT_X[1] + 6.0, path_y, lz - t / 2), (bx - 14.0, by, bz + 6.0), 9.0)
    p = p + yprism(hull(circle_pts(L.ARM_BOLT_X[1] + 6.0, lz - t / 2, 6.0, 12) + circle_pts(bx - 14.0, bz + 6.0, 6.0, 12)), path_y - 8.0, path_y + 8.0)
    eye = zrev([(0, bz - 8.0), (15.0, bz - 8.0), (15.0, bz + 9.0), (0, bz + 9.0)]).moved(Location((bx, by, 0)))
    p = p + eye
    p = p - zrev([(0, bz - 9.0), (7.4, bz - 9.0), (6.1, bz + 10.0), (0, bz + 10.0)]).moved(Location((bx, by, 0)))   # taper
    for x in L.ARM_BOLT_X:
        p = p - zcyl(F.THREADS["7/16"][0] * IN / 2 + 0.3, lz - t - 1, lz + 1, x, 499.0)
    return lab(side_of(p, side), spec)


PARTS = {
    "chassis.front.damper": {"build": damper},
    "chassis.front.damper-bolt": {"build": damper_bolt},
    "chassis.front.damper-washer": {"build": sw38},
    "chassis.front.damper-centre-bolt": {"build": damper_centre_bolt},
    "chassis.front.damper-centre-nut": {"build": nut516},
    "chassis.front.damper-centre-washer": {"build": sw516},
    "chassis.front.fulcrum-pin": {"build": fulcrum_pin},
    "chassis.front.fulcrum-bearing": {"build": bearing12},
    "chassis.front.fulcrum-nut": {"build": castle_nut("1/2", 0.75)},
    "chassis.front.fulcrum-washer": {"build": sw("1/2")},
    "chassis.front.split-pin": {"build": split_pin},
    "chassis.front.trunnion": {"build": trunnion},
    "chassis.front.pin-nut": {"build": pin_nut},
    "chassis.front.pin-washer": {"build": pin_washer},
    "chassis.front.swivel-pin": {"build": swivel_pin, "probes": {}},
    "chassis.front.grub-screw": {"build": grub_screw},
    "chassis.front.lubricator": {"build": lubricator},
    "chassis.front.cork-ring": {"build": cork_ring},
    "chassis.front.dust-tube-lower": {"build": dust_tube},
    "chassis.front.dust-tube-upper": {"build": dust_tube},
    "chassis.front.dust-spring": {"build": dust_spring},
    "chassis.front.swivel-bush-upper": {"build": bush},
    "chassis.front.swivel-bush-lower": {"build": bush},
    "chassis.front.thrust-washer": {"build": thrust_washer},
    "chassis.front.floating-thrust-washer": {"build": thrust_washer,
                                             "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "chassis.front.swivel-axle-lh": {"build": swivel_axle("left")},
    "chassis.front.swivel-axle-rh": {"build": swivel_axle("right")},
    "chassis.front.wishbone-arm": {"build": wishbone_arm},
    "chassis.front.wishbone-pivot": {"build": wishbone_pivot},
    "chassis.front.pivot-bolt-34": {"build": bolt("3/8")},
    "chassis.front.pivot-nut-35": {"build": nut("3/8")},
    "chassis.front.pivot-washer-36": {"build": sw("3/8")},
    "chassis.front.pivot-bush": {"build": pivot_bush},
    "chassis.front.pivot-washer": {"build": washer_flat(38.0, 16.6)},
    "chassis.front.pivot-nut": {"build": castle_nut("5/8", 15 / 16)},
    "chassis.front.outer-pivot-bolt": {"build": bolt("5/8")},
    "chassis.front.outer-pivot-nut": {"build": nut("5/8")},
    "chassis.front.outer-pivot-washer": {"build": sw("5/8")},
    "chassis.front.distance-tube": {"build": distance_tube},
    "chassis.front.eye-thrust-washer": {"build": washer_flat(38.0, 22.6)},
    "chassis.front.eye-seal": {"build": seal27},
    "chassis.front.seal-support": {"build": seal_support},
    "chassis.front.pan": {"build": pan},
    "chassis.front.pan-screw": {"build": bolt("5/16")},
    "chassis.front.pan-nut": {"build": nut("5/16")},
    "chassis.front.pan-washer": {"build": sw("5/16")},
    "chassis.front.coil-spring": {"build": coil_spring,
                                  "probes": {"free_height": lambda p: probes.bbox_size(p, "z"),
                                             "outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "chassis.front.steering-lever": {"build": steering_lever},
    "chassis.front.lever-bolt": {"build": bolt("7/16")},
}
