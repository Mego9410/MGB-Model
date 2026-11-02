"""Laycock type D overdrive power train: clutch bolts, springs, retainer plate, thrust bearing and
housing, cone clutch (sliding member), sun wheel, planet carrier and planets, uni-directional roller
clutch, annulus and output shaft, its bearings, the speedometer driving gear, spacer and shim, the
rear oil seal and the coupling flange with its washer and nut (Haynes Ch 6 Fig 6.13 items 51-59,
65-83, 101-103; Fig 6.10-6.12; Fig 6.16; Sec 12 paras 4-9, 13-21; Sec 15).

Built in the gearbox frame (GF) at the overdrive stations of mgb.overdrive_layout (drawn with
z = e, moved back by O.Z0). Repeated parts (bolts, springs, planets, rollers) are drawn at the
origin and placed by the assembly. The clutch is drawn in the direct drive position: the springs
hold the cone clutch back on the annulus cone (Fig 6.10).
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Polygon, Rot, Torus, extrude, Plane

from mgb import fasteners as F, gearbox_layout as G, gears as GR, overdrive_layout as O, probes, shapes as Sh
from mgb.poly2d import circle_pts, rounded
from parts.gearbox import casing as C

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
zc, box = C.zc, C.box
BETA = 12.0                                   # helix angle of the epicyclic gears (D)


def _out(p, spec):
    p = p.moved(Location((0, 0, O.Z0)))
    p.label = spec.id
    return p


def _l(p, spec):
    p.label = spec.id
    return p


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def ball_bearing(bore, od, w, n=None):
    """Deep groove ball bearing along +z from 0: rings with a groove line, balls showing in the gap."""
    ri, ro = bore / 2, od / 2
    t = (ro - ri) * 0.32
    rb = (ro - ri) * 0.3
    pc = (ri + ro) / 2
    b = ring(ri, ri + t, 0, w) + ring(ro - t, ro, 0, w)
    b = b - ring(ri + t - 0.6, ri + t + 0.1, w * 0.35, w * 0.65) - ring(ro - t - 0.1, ro - t + 0.6, w * 0.35, w * 0.65)
    n = n or max(7, int(2 * math.pi * pc / (2.3 * rb)))
    # balls between the rings
    from build123d import Sphere
    for k in range(n):
        a = 2 * math.pi * k / n
        b = b + Location((pc * math.cos(a), pc * math.sin(a), w / 2)) * Sphere(rb)
    # cage band
    b = b + ring(pc - rb * 0.55, pc + rb * 0.55, w / 2 - 0.6, w / 2 + 0.6)
    return b


# =================================================================================================
# clutch bolts, springs, plate, thrust bearing and housing (items 52-58)
# =================================================================================================
BOLT_HEAD_E = O.HOUSING_E[0] + 8.0            # bolt head underside: behind the housing lug


def clutch_bolt(spec) -> Part:
    """Item 55: screwed into the bearing housing lug with its threaded end forward through the main
    casing to the bridge piece (Sec 12 para 18): a rod threaded at both ends. Drawn from its rear
    end at the origin forward along -z."""
    L = spec.nom("length")
    r = F.THREADS[O.BOLT_SIZE][0] * IN / 2
    b = Sh.chamfered_cyl(2 * r, L, 0.5).moved(Location((0, 0, -L)))
    for z0, n in ((-L + 2.0, 14), (-10.0, 5)):                                 # thread at both ends
        for k in range(n):
            z = z0 + k * 1.058
            b = b - ring(r - 0.5, r + 1, z, z + 0.45)
    return _l(b, spec)


def clutch_spring(spec) -> Part:
    L = O.SPRING_E[1] - O.SPRING_E[0]
    s = Sh.coil_spring(spec.nom("wire"), spec.nom("outside_diameter"), L, 7.0)
    return _l(s, spec)


def retainer_plate(spec) -> Part:
    """Item 54: a flat plate over the four bolts the springs bear on (Fig 6.13: rounded outline with
    the four holes at its corners and a large centre hole)."""
    t = spec.nom("thickness")
    pts = []
    for u, l in O.BOLTS:
        pts += circle_pts(u, l, 9.0, 16)
    from mgb.poly2d import hull
    p = C.zprism(hull(pts + circle_pts(0, 0, 30.0, 36)), O.PLATE_E[0], O.PLATE_E[0] + t)
    p = p - zc(27.0, O.PLATE_E[0] - 1, O.PLATE_E[1] + 1)
    for u, l in O.BOLTS:
        p = p - zc(4.3, O.PLATE_E[0] - 1, O.PLATE_E[1] + 1, u, l)
    return _out(p, spec)


def bearing_housing(spec) -> Part:
    """Item 52: a ring holding the thrust bearing, with four lugs for the bolts (Fig 6.13)."""
    e0, e1 = O.HOUSING_E
    ro = O.TB[1] / 2
    h = Sh.revolved([(ro - 3.0, e0), (ro + 5.0, e0), (ro + 5.0, e1), (ro, e1), (ro, O.TB_E[0]), (ro - 3.0, O.TB_E[0])])
    for u, l in O.BOLTS:
        a = math.degrees(math.atan2(l, u))
        h = h + Location((u, l, e0)) * zc(7.0, 0.0, 8.0)
        h = h + Rot(0, 0, a) * box(ro + 1.0, math.hypot(u, l), -6.0, 6.0, e0, e0 + 8.0)
        h = h - zc(3.98, e0 - 1, e0 + 9, u, l)                                  # tapped for the bolt
    h = h - zc(ro, O.TB_E[0], e1 + 1)                                              # the bearing's seat
    return _out(h, spec)


def thrust_bearing(spec) -> Part:
    b = ball_bearing(O.TB[0], O.TB[1], O.TB[2])
    return _out(b.moved(Location((0, 0, O.TB_E[0]))), spec)


def circlip(r_in, r_out, t, gap_deg=40.0, lugs=True):
    """Internal or external circlip: a flat ring with a gap and two lug holes."""
    c = ring(r_in, r_out, 0, t)
    g = math.radians(gap_deg)
    c = c - Location((r_out, 0, t / 2)) * Box(2 * (r_out - r_in) + 2, 2 * r_out * math.sin(g / 2), t + 2)
    if lugs:
        for s in (1, -1):
            a = s * (g / 2 + 0.25)
            c = c + Location(((r_out + 1.5) * math.cos(a), (r_out + 1.5) * math.sin(a), 0)) * zc(2.8, 0, t)
            c = c - Location(((r_out + 1.5) * math.cos(a), (r_out + 1.5) * math.sin(a), -1)) * zc(1.0, 0, t + 2)
    return c


def circlip_58(spec) -> Part:
    r = O.CLUTCH_HUB_R[1]
    return _out(circlip(r - 0.6, r + 2.6, 1.3, lugs=False).moved(Location((0, 0, O.TB_E[0] - 1.6))), spec)


def circlip_59(spec) -> Part:
    r = O.SUN_SPLINE[2] / 2
    return _out(circlip(r - 0.4, r + 2.4, 1.2, lugs=False).moved(Location((0, 0, O.CLUTCH_HUB_E[0] - 1.6))), spec)


# =================================================================================================
# cone clutch (item 51, the sliding member) and sun wheel (65)
# =================================================================================================
def clutch(spec) -> Part:
    h0, h1 = O.CLUTCH_HUB_E
    d0, d1 = O.CLUTCH_DISC_E
    c0, c1 = O.CONE_E
    ai0, ai1 = O.ANN_CONE_R
    bo0, bo1 = O.BR_CONE_R
    lt = O.LINING_T
    rs = O.CLUTCH_HUB_R[1]
    # steel: hub (bearing seat, shoulder), disc, conical ring
    st = Sh.revolved([(O.CLUTCH_HUB_R[0] + 0.5, h0), (rs, h0), (rs, O.TB_E[1]), (rs + 4.5, O.TB_E[1]), (rs + 4.5, d0),
                      (60.0, d0), (bo0 - O.GAP - lt - 1.0, d0 + 1.0), (bo0 - O.GAP - lt, c0), (bo1 - O.GAP - lt, c1),
                      (ai1 + lt, c1), (ai0 + lt, c0), (52.0, d1), (O.CLUTCH_HUB_R[0] + 0.5, d1)])
    # bonded linings on both cone faces
    lo = Sh.revolved([(bo0 - O.GAP - lt - 0.05, c0 + 0.8), (bo0 - O.GAP, c0 + 0.8), (bo1 - O.GAP, c1 - 0.3),
                      (bo1 - O.GAP - lt - 0.05, c1 - 0.3)])
    li = Sh.revolved([(ai0 + 0.4, c0 + 0.8), (ai0 + lt + 0.05, c0 + 0.8), (ai1 + lt + 0.05, c1 - 0.3), (ai1 + 0.4, c1 - 0.3)])
    c = st + lo + li
    # oil grooves across the linings
    for k in range(16):
        a = 360.0 * k / 16
        c = c - Rot(0, 0, a) * box(bo0 - O.GAP - 0.6, bo1 + 1.0, -1.0, 1.0, c0 + 2.0, c1 - 1.0)
    # lightening / oil holes through the disc
    for k in range(8):
        a = math.radians(22.5 + 45.0 * k)
        c = c - zc(5.0, d0 - 1, d1 + 1, 44.0 * math.cos(a), 44.0 * math.sin(a))
    n, dmaj, dmin = O.SUN_SPLINE
    c = c - GR.spline_bore(n, dmaj, dmin, h1 - h0).moved(Location((0, 0, h0)))
    c = c - ring(rs - 0.6, rs + 1, O.TB_E[0] - 1.7, O.TB_E[0] - 0.3)             # circlip 58 groove
    return _out(c, spec)


def sun_wheel(spec) -> Part:
    e0, e1 = O.SUN_E
    g0, g1 = O.GEAR_E
    n, dmaj, dmin = O.SUN_SPLINE
    s = Sh.revolved([(O.SHAFT_R + 0.15, e0), (dmin / 2, e0), (dmin / 2, g0 - 4.0), (O.SUN_R - 1.0, g0 - 1.0),
                     (O.SUN_R - 1.0, g0 + 0.1), (O.SHAFT_R + 0.15, g0 + 0.1)])
    s = s + GR.spline_shaft(n, dmaj, dmin, O.SUN_SPLINE_E[1] - O.SUN_SPLINE_E[0]).moved(Location((0, 0, O.SUN_SPLINE_E[0])))
    mn = O.MOD * math.cos(math.radians(BETA))
    s = s + GR.helical(O.ZS, mn, BETA, g1 - g0, hand="right", bore=O.SHAFT_R + 0.15).moved(Location((0, 0, g0)))
    s = s - zc(O.SHAFT_R + 0.15, e0 - 1, g0 + 1.0)                              # bore on the mainshaft
    s = s - zc(O.BUSH_OD / 2, e0 - 1, O.BUSH_E[1])                              # steady bush bore
    s = s - ring(dmin / 2 - 0.5, dmaj / 2 + 1, O.CLUTCH_HUB_E[0] - 1.7, O.CLUTCH_HUB_E[0] - 0.3)   # circlip 59 groove
    for z in (70.0, 96.0):                                                       # oil holes to the bush
        s = s - Location((0, 0, z)) * Rot(0, 90, 0) * Cylinder(1.6, 40.0)
    return _out(s, spec)


def steady_bush(spec) -> Part:
    b = ring(O.SHAFT_R + 0.05, O.BUSH_OD / 2, O.BUSH_E[0], O.BUSH_E[1])
    b = b - Location((0, 0, (O.BUSH_E[0] + O.BUSH_E[1]) / 2)) * Rot(0, 90, 0) * Cylinder(1.5, 30.0)
    return _out(b, spec)


# =================================================================================================
# planet carrier (66), planets, locating ring (67)
# =================================================================================================
C0, C1 = O.CARRIER_E                         # 98 .. 134
PL0, PL1 = O.GEAR_E                          # planets 104..122
PLATE_R = 55.0
PIN_R = 6.0


def planet_angles():
    return [120.0 * k for k in range(3)]


def planet_phase(k):
    """Rotation (deg) of planet k about its own axis so its teeth mesh with the sun (tooth at 0)
    and the annulus: the timing Fig 6.16's etched lines give."""
    th = math.radians(120.0 * k)
    pitch = 2 * math.pi / O.ZS
    i = round(th / pitch)
    delta = i * pitch - th
    gap = th + math.pi - (O.ZS / O.ZP) * delta
    return math.degrees(gap - math.pi / O.ZP)


def planet_carrier(spec) -> Part:
    c = ring(19.0, PLATE_R, C0, PL0 - 0.6) + ring(O.SHAFT_R, PLATE_R, PL1 + 0.6, PL1 + 6.0)
    c = c + ring(O.SHAFT_R, 20.0, PL1 + 0.6, C1)                                   # hub on the mainshaft splines
    for k in range(3):                                                            # webs between the planets
        a = 60.0 + 120.0 * k
        c = c + Rot(0, 0, a) * box(33.0, PLATE_R - 1.0, -6.0, 6.0, PL0 - 1.0, PL1 + 1.0)
    for a in planet_angles():                                                     # pin holes, etched marks
        x, y = O.PLANET_CIRCLE * math.cos(math.radians(a)), O.PLANET_CIRCLE * math.sin(math.radians(a))
        c = c - zc(PIN_R + 0.02, C0 - 1, PL1 + 7, x, y)
        mr = PLATE_R - 1.0
        c = c - Rot(0, 0, a) * box(mr - 0.5, PLATE_R + 1, -0.35, 0.35, C0 - 1, C0 + 0.4)
    n, dmaj, dmin = G.MS_SPLINE
    c = c - GR.spline_bore(n, dmaj, dmin, C1 - PL1).moved(Location((0, 0, PL1)))
    for k in range(6):                                                            # oil holes in the front plate
        a = math.radians(60.0 * k + 30.0)
        c = c - zc(3.5, C0 - 1, PL0, 30.0 * math.cos(a), 30.0 * math.sin(a))
    return _out(c, spec)


def planet(spec) -> Part:
    """One planet wheel on its pin, drawn about its own axis (the assembly places it)."""
    mn = O.MOD * math.cos(math.radians(BETA))
    g = GR.helical(O.ZP, mn, BETA, PL1 - PL0, hand="left", bore=PIN_R + 0.15)
    g = g.moved(Location((0, 0, PL0)))
    g = g - Rot(0, 0, 0) * box(O.PLANET_R - 0.4, O.PLANET_R + 3, -0.35, 0.35, PL0, PL0 + 0.9)   # etched line
    return _l(g.moved(Location((0, 0, O.Z0))), spec)


def planet_pin(spec) -> Part:
    p = Sh.chamfered_cyl(2 * PIN_R, C1 - C0 - 6.0 + 0.0, 0.5, z0=C0)
    p = p - zc(1.5, C0 - 1, C0 + 20)                                              # oil drilling
    return _l(p.moved(Location((0, 0, O.Z0))), spec)


def locating_ring(spec) -> Part:
    """Item 67: a thin ring in front of the carrier, round the sun wheel sleeve, locating it on the
    third motion shaft (Fig 6.13 places it between the sun wheel and the carrier)."""
    r = ring(17.6, 23.0, C0 - 2.0, C0 - 0.2)
    r = r - box(20.0, 24.0, -1.5, 1.5, C0 - 3, C0)
    return _out(r, spec)


# =================================================================================================
# uni-directional clutch (68-74)
# =================================================================================================
U0, U1 = O.UD_E


def ud_inner(spec) -> Part:
    """Item 68: inner member splined on the mainshaft, twelve ramps for the rollers."""
    r_ramp = O.UD_R[0]
    poly = []
    for k in range(O.UD_N):
        a0 = 2 * math.pi * k / O.UD_N
        span = 2 * math.pi / O.UD_N
        poly += [((r_ramp + 0.2) * math.cos(a0 + span * f), (r_ramp + 0.2) * math.sin(a0 + span * f)) if f < 0.15 else
                 ((r_ramp - 1.6 * (1 - (f - 0.15) / 0.85) + 0.0) * math.cos(a0 + span * f),
                  (r_ramp - 1.6 * (1 - (f - 0.15) / 0.85)) * math.sin(a0 + span * f)) for f in (0.0, 0.1, 0.15, 0.4, 0.7, 0.99)]
    from build123d import Face, Wire
    m = extrude(Face(Wire.make_polygon([(x, y, 0) for x, y in poly], close=True)), U1 - U0).moved(Location((0, 0, U0)))
    m = m + ring(O.SHAFT_R, 22.0, U0, U1 + 0.1)
    n, dmaj, dmin = G.MS_SPLINE
    m = m - GR.spline_bore(n, dmaj, dmin, U1 - U0 + 2).moved(Location((0, 0, U0 - 1.0)))
    return _out(m, spec)


ROLLER_PC = (O.UD_R[0] + O.UD_R[1]) / 2 - 0.2


def ud_cage(spec) -> Part:
    r0, r1 = ROLLER_PC - 2.2, ROLLER_PC + 2.2
    c = ring(r0, r1, U0 - 1.0, U1 + 0.5)
    for k in range(O.UD_N):
        a = 360.0 * (k + 0.6) / O.UD_N
        c = c - Rot(0, 0, a) * box(r0 - 1, r1 + 1, -O.UD_ROLLER[0] / 2 - 0.3, O.UD_ROLLER[0] / 2 + 0.3, U0 - 0.2, U0 + O.UD_ROLLER[1] + 0.2)
    c = c + ring(r1 - 0.01, r1 + 1.5, U0 - 1.0, U0)                              # flange
    return _out(c, spec)


def ud_roller(spec) -> Part:
    d, L = O.UD_ROLLER
    return _l(Sh.chamfered_cyl(d, L, 0.4).moved(Location((0, 0, O.Z0 + U0))), spec)


def ud_spring(spec) -> Part:
    """Item 71: the wire spring in the cage that pushes the rollers up the ramps (Sec 12 para 16):
    a coiled wire ring round the cage's front flange with a tag."""
    r = ROLLER_PC + 3.0
    s = Location((0, 0, U0 - 1.6)) * Torus(r, 0.6)
    s = s + Location((r - 4.0, 0, U0 - 1.6)) * Rot(0, 90, 0) * Cylinder(0.6, 4.0, align=BASE)
    return _out(s, spec)


def circlip_72(spec) -> Part:
    r = O.UD_R[1]
    return _out(circlip(r - 2.4, r + 0.6, 1.2, lugs=False).moved(Location((0, 0, O.UD_CLIP_E))), spec)


def oil_thrower(spec) -> Part:
    """Item 73: dished washer in front of the clutch inside the annulus bore."""
    r = O.UD_R[1]
    z = O.UD_CLIP_E + 1.4
    t = Sh.revolved([(20.5, z), (r - 0.1, z), (r - 0.1, z + 0.8), (22.0, z + 1.4), (20.5, z + 1.4)])
    return _out(t, spec)


def thrust_washer(spec) -> Part:
    """Item 74 (thrust bearing / washer): between the inner member and the annulus."""
    t = spec.nom("thickness")
    return _out(ring(O.SHAFT_R + 0.6, 24.0, O.ANN_WALL_E[1] - t - 0.05, O.ANN_WALL_E[1] - 0.05), spec)


# =================================================================================================
# annulus and output shaft (75), bearings 76, 77, 81, speedo gear 78, spacer 79, shim 80, seal 82
# =================================================================================================
def annulus(spec) -> Part:
    a0 = O.ANN_E[0]
    c0, c1 = O.CONE_E
    k = (O.ANN_CONE_R[1] - O.ANN_CONE_R[0]) / (c1 - c0)
    rc0 = O.ANN_CONE_R[0] + k * (a0 - c0)
    t0, t1 = O.ANN_TEETH_E
    w0, w1 = O.ANN_WALL_E
    fb0, fb1 = O.FRONT_BRG_E
    rb0 = O.REAR_BRG_E
    tip = O.ANN_R - O.MOD
    prof = [(57.0, a0), (rc0, a0), (O.ANN_CONE_R[1], c1), (O.ANN_SHELL_R, c1 + 2.0), (O.ANN_SHELL_R, w0 + 6.0),
            (60.0, w1), (40.0, w1 + 6.0), (24.0, fb0 - 4.0), (O.OUT_BRG_FRONT[0] / 2 + 3.0, fb0 - 1.0),
            (O.OUT_BRG_FRONT[0] / 2, fb0 - 1.0), (O.OUT_BRG_FRONT[0] / 2, fb1), (14.0, fb1 + 0.5),
            (14.0, O.SHIM_E[0]), (O.OUT_BRG_REAR[0] / 2, O.SHIM_E[0]), (O.OUT_BRG_REAR[0] / 2, rb0[1]),
            (O.OUT_SPLINE[2] / 2, rb0[1] + 0.5), (O.OUT_SPLINE[2] / 2, O.SHAFT_SPLINE_E[1]),
            (9.2, O.SHAFT_THREAD_E[0] + 0.5), (9.2, O.SHAFT_THREAD_E[1] - 0.6), (8.6, O.SHAFT_THREAD_E[1]),
            (0.0, O.SHAFT_THREAD_E[1]), (0.0, O.NEEDLE_E[1] + 2.0), (O.NEEDLE_R_OUT, O.NEEDLE_E[1]),
            (O.NEEDLE_R_OUT, O.NEEDLE_E[0] - 1.0), (O.UD_R[1], w1), (O.UD_R[1], w0), (tip + 0.15, w0),
            (tip + 0.15, t0 - 1.0), (57.0, t0 - 4.0)]
    a = Sh.revolved(prof)
    # internal helical teeth: cut with a gear-shaped cutter whose teeth are the annulus's spaces
    mn = O.MOD * math.cos(math.radians(BETA))
    cutter = GR.helical(O.ZA, mn, BETA, t1 - t0, hand="left", add=1.3, ded=1.1)
    lag = math.degrees((O.GEAR_E[0] - t0) * math.tan(math.radians(BETA)) / O.ANN_R)       # same phase at the gear face
    a = a - (Rot(0, 0, 180.0 / O.ZA - lag) * cutter).moved(Location((0, 0, t0)))
    a = a - ring(O.UD_R[1] - 0.1, O.UD_R[1] + 1.0, O.UD_CLIP_E - 0.1, O.UD_CLIP_E + 1.3)      # circlip 72 groove
    # splines for the flange, thread for the nut, split pin hole; oil holes through the shell
    n, dmaj, dmin = O.OUT_SPLINE
    a = a + GR.spline_shaft(n, dmaj, dmin, O.SHAFT_SPLINE_E[1] - O.SHAFT_SPLINE_E[0] - 1.0).moved(
        Location((0, 0, O.SHAFT_SPLINE_E[0] + 0.5)))
    for k in range(4):
        z = O.SHAFT_THREAD_E[0] + 2.5 + 1.588 * 3 * k
        a = a - ring(8.9, 9.6, z, z + 0.7)
    a = a - Location((0, 0, O.SHAFT_THREAD_E[1] - 3.5)) * Rot(0, 90, 0) * Cylinder(1.5, 30.0)
    for k in range(6):
        ang = math.radians(30.0 + 60.0 * k)
        a = a - Location((68.0 * math.cos(ang), 68.0 * math.sin(ang), (t1 + w0) / 2 + 1.0)) * \
            Rot(0, 0, math.degrees(ang)) * Rot(0, 90, 0) * Cylinder(2.5, 14.0)
    return _out(a, spec)


def needle_bearing(spec) -> Part:
    r_in, r_out = O.PILOT_NEEDLE_R
    e0, e1 = O.NEEDLE_E
    b = ring(r_out - 0.6, r_out, e0, e1) + ring(r_in + 2.0, r_out - 0.59, e0, e0 + 1.0) + ring(r_in + 2.0, r_out - 0.59, e1 - 1.0, e1)
    rc = (r_in + r_out - 0.6) / 2
    nd = (r_out - 0.6 - r_in) * 0.98
    n = int(2 * math.pi * rc / (nd * 1.15))
    for k in range(n):
        a = 2 * math.pi * k / n
        b = b + Sh.chamfered_cyl(nd, e1 - e0 - 1.6, 0.2, z0=e0 + 0.8).moved(Location((rc * math.cos(a), rc * math.sin(a), 0)))
    return _out(b, spec)


def front_bearing(spec) -> Part:
    b, o, w = O.OUT_BRG_FRONT
    return _out(ball_bearing(b, o, w).moved(Location((0, 0, O.FRONT_BRG_E[0]))), spec)


def rear_bearing(spec) -> Part:
    b, o, w = O.OUT_BRG_REAR
    return _out(ball_bearing(b, o, w).moved(Location((0, 0, O.REAR_BRG_E[0]))), spec)


def speedo_drive_gear(spec) -> Part:
    """Item 78: the worm on the output shaft that drives the speedometer gear: five starts, a steep
    lead (D)."""
    e0, e1 = O.SPEEDO_E
    rp = O.SPEEDO_WORM_R - 1.8
    n = 5
    mt = 2 * rp / n
    beta = 72.0
    mn = mt * math.cos(math.radians(beta))
    w = GR.helical(n, mn, beta, e1 - e0 - 4.0, hand="right", bore=14.05, add=0.25, ded=0.3)
    w = w.moved(Location((0, 0, e0 + 2.0)))
    w = w + ring(14.05, rp - 1.0, e0, e0 + 2.01) + ring(14.05, rp - 1.0, e1 - 2.01, e1)
    return _out(w, spec)


def spacer(spec) -> Part:
    """Bush 79 (Fig 6.12 item 12, spacer): between the speedometer gear and the shim."""
    return _out(ring(14.05, 19.0, O.SPACER_E[0], O.SPACER_E[1]), spec)


def shim(spec) -> Part:
    """Thrust washer 80 (Fig 6.12 item 13, shim): selects the output shaft endfloat."""
    t = spec.nom("thickness")
    return _out(ring(O.OUT_BRG_REAR[0] / 2 + 0.05, 21.0, O.SHIM_E[0], O.SHIM_E[0] + t), spec)


def rear_seal(spec) -> Part:
    od, id_, w = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("width")
    e0 = O.SEAL_E[0]
    s = Sh.revolved([(od / 2 - 2.0, e0), (od / 2, e0), (od / 2, e0 + w), (id_ / 2 + 3.5, e0 + w), (id_ / 2 + 3.5, e0 + w - 1.2),
                     (od / 2 - 2.0, e0 + w - 1.2)])
    s = s + Sh.revolved([(id_ / 2, e0 + 2.0), (id_ / 2 + 4.5, e0 + 0.8), (od / 2 - 2.0, e0 + 0.8), (od / 2 - 2.0, e0 + w - 1.2),
                         (id_ / 2 + 4.5, e0 + w - 1.2), (id_ / 2 + 1.0, e0 + 6.0)])
    s = s + Sh.revolved([(id_ / 2 + 4.7, e0 + 3.2), (id_ / 2 + 7.0, e0 + 3.2), (id_ / 2 + 7.0, e0 + 5.6), (id_ / 2 + 4.7, e0 + 5.6)])
    return _out(s, spec)


# =================================================================================================
# coupling flange (101), washer (102), castellated nut (103), split pin
# =================================================================================================
def flange(spec) -> Part:
    f0, f1 = O.FLANGE_E
    d0, d1 = O.FLANGE_DISC_E
    rr, rf = O.FLANGE_RECESS
    R = spec.nom("diameter") / 2
    hub_r = O.SEAL_RUN_R
    f = Sh.revolved([(13.0, f0), (hub_r - 0.8, f0), (hub_r, f0 + 0.8), (hub_r, d0 - 6.0), (hub_r + 6.0, d0 - 1.5),
                     (R - 3.0, d0), (R, d0 + 1.5), (R, d1), (rr, d1), (rr, rf), (13.0, rf)])
    # four ears behind the bolt holes and the holes
    pcd = spec.nom("bolt_circle") / 2
    for k in range(O.FLANGE_BOLTS):
        a = math.radians(45.0 + 90.0 * k)
        x, y = pcd * math.cos(a), pcd * math.sin(a)
        f = f + zc(8.5, d0 - 5.0, d0 + 0.5, x, y)
    for k in range(O.FLANGE_BOLTS):
        a = math.radians(45.0 + 90.0 * k)
        x, y = pcd * math.cos(a), pcd * math.sin(a)
        f = f - zc(spec.nom("bolt_hole") / 2, d0 - 6.0, d1 + 1.0, x, y)
    n, dmaj, dmin = O.OUT_SPLINE
    f = f - GR.spline_bore(n, dmaj, dmin, rf - f0).moved(Location((0, 0, f0)))
    return _out(f, spec)


def flange_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _out(Sh.washer(od, id_, t).moved(Location((0, 0, O.WASHER_E[0]))), spec)


def flange_nut(spec) -> Part:
    """Item 103: castellated nut, 3/4 in UNF (D), six slots for the split pin (Sec 12 para 14)."""
    from build123d import RegularPolygon
    af = spec.nom("across_flats")
    e0, e1 = O.NUT_E
    h = 10.0
    n = extrude(RegularPolygon(af / math.sqrt(3), 6), h).moved(Location((0, 0, e0)))
    n = n - Sh.revolved([(af / 2 + 0.1, e0 - 0.01), (af / math.sqrt(3) + 1, e0 - 0.01), (af / math.sqrt(3) + 1, e0 + 2.0)])
    n = n + zc(af / 2 - 1.5, e0 + h - 0.01, e1)                                    # castellated crown
    for k in range(3):
        n = n - Rot(0, 0, 60.0 * k) * box(-af, af, -1.6, 1.6, e1 - 4.5, e1 + 1.0)
    n = n - zc(9.53, e0 - 1, e1 + 1)
    for k in range(4):
        z = e0 + 1.5 + 1.588 * 2 * k
        n = n + ring(9.0, 9.6, z, z + 0.7)
    return _out(n, spec)


def split_pin(spec) -> Part:
    """Through the shaft and two slots of the nut: two half-round legs (a slit cylinder) and the eye."""
    d = spec.nom("diameter")
    L = 30.0
    z = O.SHAFT_THREAD_E[1] - 3.5
    p = zc(d / 2, -L / 2, L / 2) - box(-0.15, 0.15, -d, d, -L / 2 + 1.5, L / 2 + 1)
    p = p + Location((0, 0, -L / 2 - 1.4)) * Box(d * 0.9, 2.4 * d, 3.0)
    return _out(Location((0, 0, z)) * Rot(0, 90, 0) * p, spec)


WASHER = C.WASHER

PARTS = {
    "gearbox.overdrive-internals.clutch-bolt": {"build": clutch_bolt, "probes": {"length": lambda p: -p.bounding_box().min.Z}},
    "gearbox.overdrive-internals.clutch-spring": {"build": clutch_spring},
    "gearbox.overdrive-internals.retainer-plate": {"build": retainer_plate},
    "gearbox.overdrive-internals.bearing-housing": {"build": bearing_housing},
    "gearbox.overdrive-internals.thrust-bearing": {"build": thrust_bearing,
                                                   "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-internals.housing-circlip": {"build": circlip_58},
    "gearbox.overdrive-internals.sun-circlip": {"build": circlip_59},
    "gearbox.overdrive-internals.clutch": {"build": clutch},
    "gearbox.overdrive-internals.sun-wheel": {"build": sun_wheel},
    "gearbox.overdrive-internals.steady-bush": {"build": steady_bush},
    "gearbox.overdrive-internals.planet-carrier": {"build": planet_carrier},
    "gearbox.overdrive-internals.planet": {"build": planet},
    "gearbox.overdrive-internals.planet-pin": {"build": planet_pin},
    "gearbox.overdrive-internals.locating-ring": {"build": locating_ring},
    "gearbox.overdrive-internals.ud-inner": {"build": ud_inner},
    "gearbox.overdrive-internals.ud-cage": {"build": ud_cage},
    "gearbox.overdrive-internals.ud-roller": {"build": ud_roller},
    "gearbox.overdrive-internals.ud-spring": {"build": ud_spring},
    "gearbox.overdrive-internals.ud-circlip": {"build": circlip_72},
    "gearbox.overdrive-internals.oil-thrower": {"build": oil_thrower},
    "gearbox.overdrive-internals.thrust-washer": {"build": thrust_washer},
    "gearbox.overdrive-internals.annulus": {"build": annulus},
    "gearbox.overdrive-internals.needle-bearing": {"build": needle_bearing},
    "gearbox.overdrive-internals.front-bearing": {"build": front_bearing,
                                                  "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-internals.speedo-drive-gear": {"build": speedo_drive_gear},
    "gearbox.overdrive-internals.spacer": {"build": spacer},
    "gearbox.overdrive-internals.shim": {"build": shim, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.overdrive-internals.rear-bearing": {"build": rear_bearing,
                                                 "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.overdrive-internals.rear-seal": {"build": rear_seal},
    "gearbox.overdrive-internals.flange": {"build": flange, "probes": {"diameter": lambda p: probes.bbox_size(p, "y")}},
    "gearbox.overdrive-internals.flange-washer": {"build": flange_washer},
    "gearbox.overdrive-internals.flange-nut": {"build": flange_nut},
    "gearbox.overdrive-internals.split-pin": {"build": split_pin},
}
