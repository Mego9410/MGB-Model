"""Gearbox shafts and gears, early three-synchro box (overdrive type mainshaft), 1963.
Haynes Ch 6: Fig 6.3 items 35-44, 83-114 (printed p114-115), Fig 6.6 (mainshaft gear retention,
p120); Sec 4 paras 12-15, Sec 5 paras 7-24, Sec 7 paras 1-6; photos 5.14-5.21, 7.1-7.4.

Built in the gearbox frame (mgb.gearbox_layout GF): local z rearward along the mainshaft from
the casing front face, x up, y to the car's left. The layshaft and reverse parts are built on
their own axes at their places in that frame, so every part goes in with GF alone.

Tooth counts (S, mgaguru gt102a) and the pitches and stations (D) are in gearbox_layout. The
helical gears are left hand on the mainshaft side and right hand on the laygear, so the pairs
mesh; first gear, the laygear first gear and the reverse idler are straight cut.

Forms (Fig 6.3, photos 5.14-5.21):
- first motion shaft: spigot, 23 splines for the driven plate, the plain length through the
  oil seal, the left-hand thread for the nut, the bearing seat, the 21-tooth constant mesh
  gear, the fourth gear dog teeth and synchro cone, and the bore for the needle rollers.
- mainshaft (third motion shaft, overdrive type): nose for the needle rollers, splines along
  the gear train with the hole for the third gear locking peg and the oil holes for the bushes,
  the centre bearing seat, then the long tail into the overdrive: cam seat with its Woodruff
  keyway, splines for the overdrive clutch and planet carrier, and the pilot.
- synchronisers: splined hubs with three spring-loaded balls; the 3rd/4th coupling sleeve
  with its fork groove; bronze baulk rings with three lugs and dog teeth; first gear is the
  outer member of the 1st/2nd synchroniser (Haynes item 101), with its fork collar.
- laygear: one forging, 30, 26, 20 and 11 teeth, bored for three sets of needle rollers.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Location, Part, Rot, Sphere, Torus

from mgb import gearbox_layout as G, gears as GR, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
IN = 25.4
MS, MT, BETA = G.M_SPUR, G.MT_HEL, G.BETA


def _l(p, spec):
    p.label = spec.id
    return p


def zc(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def at(z, x=0.0, y=0.0):
    return Location((x, y, z))


def helical(n, z0, z1, hand, bore=0.0, add=1.0):
    """Helical gear between stations z0 and z1, bored (as an inner wire) to radius `bore`."""
    return GR.helical(n, G.MN_HEL, BETA, z1 - z0, hand=hand, bore=bore, add=add).moved(at(z0))


def spur(n, z0, z1, bore=0.0, **kw):
    return GR.spur(n, MS, z1 - z0, bore=2 * bore, **kw).moved(at(z0))


def chamfer_ends(part, r_out, z0, z1, c=1.2):
    """Take the sharp outer corners off a gear's teeth (a cone cut at each face)."""
    cut = Sh.revolved([(r_out - c, z0 - 0.01), (r_out + 5, z0 - 0.01), (r_out + 5, z0 + c + 5)]) + \
        Sh.revolved([(r_out - c, z1 + 0.01), (r_out + 5, z1 - c - 5), (r_out + 5, z1 + 0.01)])
    return part - cut


# ---- shared sizes (D) --------------------------------------------------------------------------
FMS_SPLINE = (23, 25.0, 21.8)          # count (S, clutch hub), major, minor diameter
MS_SPLINE = (10, 35.0, 31.0)           # mainshaft gear-train splines
HUB_OUT = (24, 63.0, 58.6)             # synchro hub outer splines (3/4)
HUB12_OUT = (24, 64.0, 59.6)           # 1st/2nd hub outer splines
BUSH_R = (17.6, 21.0)
CONE4 = (27.0, 24.6)                   # fourth gear cone radius at its large and small ends
CONE3 = (27.0, 24.6)
CONE2 = (27.0, 24.6)
LAY_BORE_R = 11.0
LAYSHAFT_R = 0.6668 * IN / 2
NEEDLE_D = 2.5


# ---- first motion shaft (items 35-41) ----------------------------------------------------------
def _fms_d(x):
    return G.CASE_FRONT_X - x


SPIGOT_TIP = _fms_d(-246.0)            # the spigot runs 12 mm into the crankshaft bush (bush x -240 to -254)
SPLINE_D = (_fms_d(-276.0), _fms_d(-326.0))
THREAD_D = (-13.0, -2.5)
BORE_D = 30.0                          # needle roller bore from the rear end forward to here


def first_motion_shaft(spec) -> Part:
    sp = spec.nom("spigot_diameter") / 2
    prof = [(0, SPIGOT_TIP), (sp - 0.8, SPIGOT_TIP), (sp, SPIGOT_TIP + 0.8), (sp, SPIGOT_TIP + 12.0),
            (10.0, SPIGOT_TIP + 13.5), (10.0, SPLINE_D[0] - 6.0), (FMS_SPLINE[2] / 2, SPLINE_D[0] - 3.0),
            (FMS_SPLINE[2] / 2, SPLINE_D[1] + 2.0), (14.0, SPLINE_D[1] + 6.0), (14.0, THREAD_D[0] - 1.0),
            (16.0, THREAD_D[0]), (16.6, THREAD_D[0] + 0.6), (16.6, THREAD_D[1]), (17.5, THREAD_D[1] + 0.5),
            (17.5, G.FMS_BRG[1]), (22.0, G.FMS_BRG[1]), (22.0, G.CM_GEAR[0]), (18.0, G.CM_GEAR[0]),
            (18.0, G.CM_GEAR[1]), (0, G.CM_GEAR[1])]
    s = Sh.revolved(prof)
    s = s + GR.spline_shaft(FMS_SPLINE[0], FMS_SPLINE[1], FMS_SPLINE[2], SPLINE_D[1] - SPLINE_D[0], land=0.36).moved(
        Location((0, 0, SPLINE_D[0])) * Rot(0, 0, 180.0 / FMS_SPLINE[0]))
    # thread grooves on the nut seat (left hand: the turns run the other way, shown as rings)
    for k in range(6):
        z = THREAD_D[0] + 1.0 + 1.6 * k
        s = s - ring(16.0, 17.0, z, z + 0.7)
    s = s - Location((16.6, 0, (THREAD_D[0] + THREAD_D[1]) / 2)) * Box(2.4, 5.0, THREAD_D[1] - THREAD_D[0] + 2)   # lock washer keyway
    s = s + GR.dog_ring(28, 31.0, 22.0, G.FMS_DOG[1] - G.FMS_DOG[0], fill=0.45).moved(at(G.FMS_DOG[0]))
    s = s + GR.cone(CONE4[0], CONE4[1], G.FMS_CONE[1] - G.FMS_CONE[0], 30.0).moved(at(G.FMS_CONE[0]))
    s = s + ring(14.0, CONE4[1], G.FMS_CONE[1] - 0.01, G.FMS_END)
    s = s - zc(spec.nom("bore_diameter") / 2, BORE_D, G.FMS_END + 1)
    s = s - zc(4.0, G.FMS_END - 40, BORE_D + 0.5)                    # oil way from the bore
    # oil grooves on the cone
    for k in range(3):
        z = G.FMS_CONE[0] + 2.0 + 2.5 * k
        s = s - ring(CONE4[0] - (CONE4[0] - CONE4[1]) * (z - G.FMS_CONE[0]) / 9.0 - 0.4, 30.0, z, z + 0.6)
    s = GR.glue(s, helical(G.TEETH["constant"][0], G.CM_GEAR[0], G.CM_GEAR[1], "left", bore=18.0))
    return _l(s, spec)


def _ball_bearing(od, id_, w, n_balls, groove=None):
    """Deep groove ball bearing: outer and inner rings with the balls showing between them."""
    ro, ri = od / 2, id_ / 2
    pm = (ro + ri) / 2
    bd = (ro - ri) * 0.58
    t = (ro - ri - bd) / 2 + bd * 0.32
    outer = Sh.revolved([(ro - t, 0.5), (ro - t + 0.5, 0), (ro - 0.6, 0), (ro, 0.6), (ro, w - 0.6), (ro - 0.6, w),
                         (ro - t + 0.5, w), (ro - t, w - 0.5)])
    inner = Sh.revolved([(ri, 0.6), (ri + 0.6, 0), (ri + t - 0.5, 0), (ri + t, 0.5), (ri + t, w - 0.5),
                         (ri + t - 0.5, w), (ri + 0.6, w), (ri, w - 0.6)])
    b = outer + inner
    tor = Torus(pm, bd / 2).moved(at(w / 2))
    b = b - tor
    for k in range(n_balls):
        a = 2 * math.pi * k / n_balls
        b = b + Sphere(bd / 2 - 0.05).moved(at(w / 2, pm * math.cos(a), pm * math.sin(a)))
    # cage between the balls (a thin pressed ring each side)
    for z in (w / 2 - bd / 2 - 0.2, w / 2 + bd / 2 - 0.6):
        b = b + ring(pm - bd * 0.22, pm + bd * 0.22, z, z + 0.8)
    if groove:
        gr, gw, gz = groove
        b = b - ring(gr, ro + 1, gz, gz + gw)
    return b


def fms_bearing(spec) -> Part:
    od, id_, w = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("width")
    b = _ball_bearing(od, id_, w, 8, groove=(od / 2 - 1.6, 1.9, 0.0))
    return _l(b.moved(at(G.FMS_BRG[0])), spec)


def fms_ring(spec) -> Part:
    """Spring ring in the bearing's outer groove (Fig 6.3 item 37): it sits against the casing
    front face and the shims and front cover hold it there."""
    od = spec.nom("outside_diameter")
    r = ring(40.0 - 1.6 + 0.05, od / 2, G.FMS_BRG[0], G.FMS_BRG[0] + 1.85)
    r = r - Location((od / 2 - 2, 0, G.FMS_BRG[0] + 1)) * Box(8, 4, 4)
    return _l(r, spec)


def fms_shim(spec) -> Part:
    t = spec.nom("thickness")
    return _l(ring(33.0, 40.0, G.FMS_BRG[0] - t, G.FMS_BRG[0]), spec)


def fms_needles(spec) -> Part:
    """The loose needle rollers between the mainshaft nose and the first motion shaft bore."""
    n = int(spec.nom("count"))
    L = spec.nom("length")
    rp = 8.0 + NEEDLE_D / 2
    out = None
    for k in range(n):
        a = 2 * math.pi * k / n
        nd = Sh.chamfered_cyl(NEEDLE_D, L, 0.3).moved(at(G.FMS_END - L - 2.0, rp * math.cos(a), rp * math.sin(a)))
        out = nd if out is None else out + nd
    return _l(out, spec)


def fms_lock_washer(spec) -> Part:
    t = spec.nom("thickness")
    z0 = THREAD_D[1] - t                  # under the nut, at the end of the thread
    w = ring(17.6, 25.0, z0, z0 + t)
    w = w + Location((15.9, 0, z0 + t / 2)) * Box(2.0, 4.6, t)                         # inner tab in the keyway
    w = w + Rot(0, 0, 30) * Location((23.25 + t / 2, 0, z0 - 4.0 + t)) * Box(t, 7.0, 8.0)  # tab bent over a nut flat
    return _l(w, spec)


def fms_nut(spec) -> Part:
    """Left-hand threaded nut (MGOC 1G3584), with a seating collar toward the bearing."""
    af = spec.nom("across_flats")
    t = spec.nom("thickness")
    from build123d import RegularPolygon, extrude
    z1 = THREAD_D[1] - 1.2
    n = extrude(RegularPolygon(af / math.sqrt(3), 6, major_radius=True), t - 1.5).moved(at(z1 - t))
    n = n + zc(af / 2 - 1.0, z1 - 1.5, z1)
    n = n - Sh.revolved([(af / math.sqrt(3) + 1, z1 - t - 0.01), (af / 2 - 0.5, z1 - t - 0.01),
                         (af / math.sqrt(3) + 1, z1 - t + 3.0)])
    n = n - zc(16.65, z1 - t - 1, z1 + 1)
    return _l(n, spec)


# ---- mainshaft (third motion shaft, overdrive type) and its gears -----------------------------
NOSE = (31.0, G.FMS_END - 0.5)
SPL = (G.SYN34[0] - 1.0, G.SYN12[1] + 0.5)


def mainshaft(spec) -> Part:
    rn = 8.0
    rs = MS_SPLINE[2] / 2
    rb = spec.nom("bearing_journal") / 2
    rt = G.MS_TAIL_R
    tail_end = G.MS_PILOT_D[1]
    prof = [(0, NOSE[0]), (rn - 0.6, NOSE[0]), (rn, NOSE[0] + 0.6), (rn, NOSE[1]), (12.0, NOSE[1] + 1.0),
            (12.0, SPL[0] - 1.0), (rs, SPL[0]), (rs, SPL[1]), (17.4, SPL[1]), (17.4, G.TW97[1]),
            (rb + 1.5, G.TW97[1]), (rb + 1.5, G.CTR_BRG[0]), (rb, G.CTR_BRG[0]), (rb, G.CTR_BRG[1] + 4.0),
            (rt + 1.0, G.CTR_BRG[1] + 6.0), (rt, G.CTR_BRG[1] + 8.0),
            (rt, G.MS_SPLINE_D[0] - 2.0), (G.MS_SPLINE[2] / 2, G.MS_SPLINE_D[0]),
            (G.MS_SPLINE[2] / 2, G.MS_SPLINE_D[1]), (G.MS_PILOT_R + 1.5, G.MS_SPLINE_D[1] + 2.0),
            (G.MS_PILOT_R, G.MS_PILOT_D[0] + 3.0), (G.MS_PILOT_R, tail_end - 0.8), (G.MS_PILOT_R - 0.8, tail_end),
            (0, tail_end)]
    s = Sh.revolved(prof)
    s = s + GR.spline_shaft(MS_SPLINE[0], MS_SPLINE[1], MS_SPLINE[2], SPL[1] - SPL[0]).moved(at(SPL[0]))
    n, dmaj, dmin = G.MS_SPLINE
    s = s + GR.spline_shaft(n, dmaj, dmin, G.MS_SPLINE_D[1] - G.MS_SPLINE_D[0] - 3.0).moved(at(G.MS_SPLINE_D[0] + 1.5))
    # third gear locking peg hole (Fig 6.6 A), radial in a spline root; oil holes for the two bushes
    s = s - Location((rs - 12.0, 0, sum(G.TW98) / 2)) * Rot(0, 90, 0) * Cylinder(2.4, 20.0, align=BASE)
    for z in ((G.G3[0] + 9 + G.G3[1]) / 2, (G.G2[0] + G.G2[1]) / 2):
        s = s - Location((0, 0, z)) * Rot(0, 90, 0) * Cylinder(1.6, 40.0)
    s = s - zc(2.5, NOSE[0] - 1, (G.G2[0] + G.G2[1]) / 2)                       # axial oil drilling
    # Woodruff keyway for the overdrive pump cam (1/2 in key)
    kz = sum(G.MS_CAM_D) / 2
    s = s - Location((rt + 4.6, 0, kz)) * Rot(90, 0, 0) * Cylinder(12.7 / 2 + 2.0, 3.2)
    # circlip groove behind the cam
    s = s - ring(rt - 0.8, rt + 1, G.MS_CAM_D[1] + 1.0, G.MS_CAM_D[1] + 2.2)
    return _l(s, spec)


def oil_restrictor(spec) -> Part:
    """Small plug pressed into the nose drilling (Fig 6.3 item 96) to meter oil to the bushes."""
    r = Sh.revolved([(0.0, NOSE[0] + 0.5), (2.5, NOSE[0] + 0.5), (2.5, NOSE[0] + 6.0), (0.0, NOSE[0] + 6.0)])
    r = r - zc(0.6, NOSE[0] - 2, NOSE[0] + 6)
    return _l(r, spec)


def centre_bearing(spec) -> Part:
    od, id_, w = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("width")
    return _l(_ball_bearing(od, id_, w, 9).moved(at(G.CTR_BRG[0])), spec)


def bearing_housing(spec) -> Part:
    """Flanged housing the centre bearing is pressed into; it fits the bore in the rear wall
    and comes out with the mainshaft (Sec 4 para 14)."""
    ro = 46.0
    rf = 52.0
    z0, z1 = G.CTR_BRG[0], G.CASE_LEN
    h = Sh.revolved([(33.0, G.CTR_BRG[1]), (40.0, G.CTR_BRG[1]), (40.0, z0), (ro - 1.0, z0), (ro, z0 + 1.0),
                     (ro, z1 - 4.0), (rf, z1 - 4.0), (rf, z1), (33.0, z1)])
    h = h - zc(2.05, z1 - 4.5, z1 + 1, 48.0, 0.0)                               # hole for the locating peg
    for a in (100.0, 260.0):                                                     # extractor notches under the lip
        h = h - Location((rf * math.cos(math.radians(a)), rf * math.sin(math.radians(a)), z1 - 2)) * Box(10, 10, 4.5)
    return _l(h, spec)


def housing_peg(spec) -> Part:
    return _l(Sh.chamfered_cyl(4.0, 7.0, 0.4).moved(at(G.CASE_LEN - 7.5, 48.0, 0.0)), spec)


def mainshaft_clip(spec) -> Part:
    """Split spring clip on the mainshaft behind the centre bearing (Fig 6.4 item 51)."""
    r0 = spec.nom("inside_diameter") / 2
    z0 = G.CTR_BRG[1] + 0.2
    c = ring(r0, r0 + 2.4, z0, z0 + 3.0) - Location((r0 + 1, 0, z0 + 1.5)) * Box(5, 3, 4)
    return _l(c, spec)


# ---- 3rd/4th synchroniser (items 110-114) ---------------------------------------------------------
def synchro_hub_34(spec) -> Part:
    z0, z1 = G.SYN34
    h = ring(19.0, HUB_OUT[2] / 2, z0, z1)
    h = h + GR.spline_shaft(HUB_OUT[0], HUB_OUT[1], HUB_OUT[2], z1 - z0 - 6.0).moved(at(z0 + 3.0))
    # web recess either side
    h = h - ring(23.0, 27.0, z0 - 1, z0 + 5.0) - ring(23.0, 27.0, z1 - 5.0, z1 + 1)
    h = h - GR.spline_bore(MS_SPLINE[0], MS_SPLINE[1], MS_SPLINE[2], z1 - z0).moved(at(z0))
    # three slots for the baulk ring lugs, three radial holes for the springs and balls
    for k in range(3):
        a = 60.0 + 120.0 * k
        h = h - Rot(0, 0, a) * Location((30.5, 0, (z0 + z1) / 2)) * Box(9.0, 9.0, z1 - z0 + 2)
        b = a + 60.0
        h = h - Rot(0, 0, b) * Location((25.0, 0, (z0 + z1) / 2)) * Rot(0, 90, 0) * Cylinder(3.65, 14.0)
    return _l(h, spec)


def coupling_sleeve(spec) -> Part:
    z0, z1 = G.SYN34[0] + 2.0, G.SYN34[1] - 2.0
    zg = (z0 + z1) / 2
    ro = spec.nom("outside_diameter") / 2
    s = Sh.revolved([(HUB_OUT[1] / 2 + 0.3, z0), (ro - 1.5, z0), (ro, z0 + 1.5), (ro, zg - 4.5), (ro - 4.0, zg - 4.0),
                     (ro - 4.0, zg + 4.0), (ro, zg + 4.5), (ro, z1 - 1.5), (ro - 1.5, z1), (HUB_OUT[1] / 2 + 0.3, z1)])
    s = s - GR.spline_bore(HUB_OUT[0], HUB_OUT[1] + 0.3, HUB_OUT[2] + 0.3, z1 - z0).moved(at(z0))
    # internal groove the balls click into (neutral)
    s = s - ring(29.0, HUB_OUT[1] / 2 + 1.7, zg - 3.7, zg + 3.7)
    # pointed ends on the internal dogs
    s = s - Sh.revolved([(HUB_OUT[2] / 2, z0 - 0.01), (HUB_OUT[1] / 2 + 1.0, z0 - 0.01), (HUB_OUT[1] / 2 + 1.0, z0 + 1.6)])
    s = s - Sh.revolved([(HUB_OUT[2] / 2, z1 + 0.01), (HUB_OUT[1] / 2 + 1.0, z1 - 1.6), (HUB_OUT[1] / 2 + 1.0, z1 + 0.01)])
    return _l(s, spec)


def _cone_r(z, cz0, cz1, r0, r1):
    """Radius of a gear's synchro cone at station z (r0 at cz0, r1 at cz1), extended linearly."""
    return r0 + (r1 - r0) * (z - cz0) / (cz1 - cz0)


def _baulk_ring(z0, z1, cone, facing):
    """Bronze baulk ring: internal cone matching the gear cone (cone = (cz0, cz1, r0, r1)),
    external dog teeth and three lugs that ride in the synchro hub slots. facing = +1 when the
    lugs point rearward."""
    ri0, ri1 = _cone_r(z0, *cone) + 0.4, _cone_r(z1, *cone) + 0.4
    body = Sh.revolved([(ri0, z0), (29.0, z0), (29.0, z1), (ri1, z1)])
    body = body + (GR.dog_ring(28, 31.0, 28.5, 2.5, fill=0.45) - zc(28.6, -1, 4)).moved(at(z1 - 2.5 if facing > 0 else z0))
    zl = z1 if facing > 0 else z0 - 3.0
    for k in range(3):
        a = 60.0 + 120.0 * k
        body = body + Rot(0, 0, a) * Location((27.9, 0, zl + 1.5)) * Box(2.8, 7.5, 3.0)
    for k in range(6):                                                  # oil grooves across the cone
        a = 30.0 * k
        body = body - Rot(0, 0, a) * Location(((ri0 + ri1) / 2, 0, (z0 + z1) / 2)) * Box(2.0, 1.2, z1 - z0 + 2)
    return body


def baulk_ring_34_front(spec) -> Part:
    return _l(_baulk_ring(G.FMS_CONE[0] + 1.5, G.SYN34[0] - 0.5, (G.FMS_CONE[0], G.FMS_CONE[1], CONE4[0], CONE4[1]), +1), spec)


def baulk_ring_34_rear(spec) -> Part:
    return _l(_baulk_ring(G.SYN34[1] + 0.5, G.G3[0] + 7.0, (G.G3[0], G.G3[0] + 9.0, CONE3[1], CONE3[0]), -1), spec)


def baulk_ring_2(spec) -> Part:
    return _l(_baulk_ring2(spec), spec)


def _baulk_ring2(spec):
    z0, z1 = G.G2_TEETH[1] + 7.2, G.SYN12[0] - 0.5
    cone = (G.G2_TEETH[1] + 7.0, G.G2[1], CONE2[0], CONE2[1])
    ri0, ri1 = _cone_r(z0, *cone) + 0.4, max(_cone_r(z1, *cone) + 0.4, 21.5)
    body = Sh.revolved([(ri0, z0), (29.0, z0), (29.0, z1), (ri1, z1)])
    body = body + (GR.dog_ring(28, 31.0, 28.5, 2.5, fill=0.45) - zc(28.6, -1, 4)).moved(at(z1 - 2.5))
    for k in range(3):
        a = 60.0 + 120.0 * k
        body = body + Rot(0, 0, a) * Location((27.9, 0, z1 - 1.5)) * Box(2.8, 7.5, 3.0)
    for k in range(6):
        body = body - Rot(0, 0, 30.0 * k) * Location(((ri0 + ri1) / 2, 0, (z0 + z1) / 2)) * Box(2.0, 1.2, z1 - z0 + 2)
    return body


def spring(spec) -> Part:
    """Synchro ball spring, built radially at 0 deg in its hub hole; the assembly turns it."""
    L = spec.nom("free_length")
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, 7)
    return _l(c, spec)


def ball(spec) -> Part:
    return _l(Sphere(spec.nom("diameter") / 2), spec)


def third_gear(spec) -> Part:
    z_c0, z_d0, z_t0, z_t1 = G.G3[0], G.G3[0] + 9.0, G.G3_TEETH[0], G.G3_TEETH[1]
    n = G.TEETH["third"][0]
    g = GR.dog_ring(28, 31.0, 26.5, z_t0 - z_d0, fill=0.45).moved(at(z_d0))
    # cone forward, hollow: the locking washer sits inside it
    g = g + Sh.revolved([(24.2, z_c0), (CONE3[1], z_c0), (CONE3[0], z_d0), (24.2, z_d0)])
    g = g - zc(BUSH_R[1] + 0.05, z_d0 - 1, z_t0 + 1)
    g = g - Location((0, 0, (G.TW98[0] + G.TW98[1]) / 2)) * Rot(0, 90, 0) * Cylinder(1.6, 40.0)   # hole over the peg
    g = GR.glue(g, helical(n, z_t0, z_t1, "left", bore=BUSH_R[1] + 0.05))
    return _l(g, spec)


def third_gear_bush(spec) -> Part:
    z0, z1 = G.G3[0] + 9.0, G.G3[1]
    b = ring(MS_SPLINE[1] / 2 + 0.1, BUSH_R[1], z0, z1)
    for a in (0.0, 180.0):                                                  # tongues into the interlocking ring
        b = b + Rot(0, 0, a) * Location((19.3, 0, z1 + 1.5)) * Box(3.4, 6.0, 3.0)
    b = b - Location((19.0, 0, (z0 + z1) / 2)) * Rot(0, 90, 0) * Cylinder(1.6, 6.0)   # oil hole
    b = b - Location((19.0, 0, z0)) * Box(5, 4.0, 3.0)                                # cut-out over the peg hole
    return _l(b, spec)


def interlock_ring(spec) -> Part:
    z0, z1 = G.RING107
    r = ring(MS_SPLINE[1] / 2 + 0.1, 23.0, z0, z1)
    r = r - GR.spline_bore(MS_SPLINE[0], MS_SPLINE[1], MS_SPLINE[2], z1 - z0).moved(at(z0))
    for a in (0.0, 180.0, 90.0, 270.0):                                     # slots the bush tongues engage
        r = r - Rot(0, 0, a) * Location((19.3, 0, (z0 + z1) / 2)) * Box(3.6, 6.4, z1 - z0 + 2)
    return _l(r, spec)


def second_gear(spec) -> Part:
    n = G.TEETH["second"][0]
    z_t0, z_t1 = G.G2_TEETH
    z_d0, z_d1 = z_t1 + 3.0, z_t1 + 7.0
    g = ring(BUSH_R[1], 30.0, z_t1, z_d0 + 0.2)
    g = g + GR.dog_ring(28, 31.8, 26.5, z_d1 - z_d0, fill=0.45).moved(at(z_d0))
    g = g + Sh.revolved([(BUSH_R[1], z_d1 - 0.1), (CONE2[0], z_d1 - 0.1), (CONE2[1], G.G2[1]), (BUSH_R[1], G.G2[1])])
    g = g - zc(BUSH_R[1] + 0.05, z_t1 - 1, G.G2[1] + 1)
    g = GR.glue(g, helical(n, z_t0, z_t1, "left", bore=BUSH_R[1] + 0.05))
    return _l(g, spec)


def second_gear_bush(spec) -> Part:
    z0, z1 = G.RING107[1], G.G2[1]
    b = ring(MS_SPLINE[1] / 2 + 0.1, BUSH_R[1], z0, z1)
    for a in (90.0, 270.0):
        b = b + Rot(0, 0, a) * Location((19.3, 0, z0 - 1.5)) * Box(3.4, 6.0, 3.0)
    b = b - Location((19.0, 0, (G.G2[0] + G.G2[1]) / 2)) * Rot(0, 90, 0) * Cylinder(1.6, 6.0)
    return _l(b, spec)


def thrust_washer_3(spec) -> Part:
    """Third gear locking washer (Fig 6.6 D): splined bore, turned on the splines so a spline
    holds the peg down and the peg then locks it (Sec 5 para 19)."""
    z0, z1 = G.TW98
    w = ring(MS_SPLINE[2] / 2, spec.nom("outside_diameter") / 2, z0, z1)
    w = w - GR.spline_bore(MS_SPLINE[0], MS_SPLINE[1], MS_SPLINE[2], z1 - z0).moved(at(z0))
    w = w - Location((MS_SPLINE[1] / 2, 0, (z0 + z1) / 2)) * Box(5.0, 4.8, z1 - z0 + 2)     # peg notch (E)
    return _l(w, spec)


def peg(spec) -> Part:
    p = Sh.chamfered_cyl(spec.nom("diameter"), spec.nom("length"), 0.4)
    return _l(Location((MS_SPLINE[2] / 2 - 4.9, 0, sum(G.TW98) / 2)) * Rot(0, 90, 0) * p.moved(at(0)), spec)


def peg_spring(spec) -> Part:
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("free_length"), 6)
    return _l(Location((MS_SPLINE[2] / 2 - 11.9, 0, sum(G.TW98) / 2)) * Rot(0, 90, 0) * c, spec)


def synchro_hub_12(spec) -> Part:
    z0, z1 = G.SYN12
    h = ring(19.0, HUB12_OUT[2] / 2, z0, z1)
    h = h + GR.spline_shaft(HUB12_OUT[0], HUB12_OUT[1], HUB12_OUT[2], z1 - z0 - 2.0).moved(at(z0 + 1.0))
    h = h - GR.spline_bore(MS_SPLINE[0], MS_SPLINE[1], MS_SPLINE[2], z1 - z0).moved(at(z0))
    h = h - ring(23.0, 27.0, z1 - 12.0, z1 + 1)                                   # lightening recess at the back
    for k in range(3):
        a = 60.0 + 120.0 * k
        h = h - Rot(0, 0, a) * Location((30.5, 0, z0 + 5.0)) * Box(9.0, 9.0, 12.0)    # baulk ring lug slots
        h = h - Rot(0, 0, a + 60.0) * Location((25.0, 0, (G.G1[0] + G.G1_TEETH[1]) / 2)) * Rot(0, 90, 0) * Cylinder(3.65, 14.0)
    return _l(h, spec)


def first_gear(spec) -> Part:
    """Outer member of the 1st/2nd synchroniser (item 101): fork collar, the straight-cut
    28 teeth, internal splines on the hub, dog ends to the second gear."""
    z0, zc0, zt0, zt1 = G.G1[0], G.G1[0] + 10.0, G.G1_TEETH[0], G.G1_TEETH[1]
    n = G.TEETH["first"][0]
    g = spur(n, zt0, zt1)
    ra = GR.pitch_radius(n, MS) + MS
    g = chamfer_ends(g, ra, zt0, zt1, c=1.5)
    g = g + Sh.revolved([(30.0, z0), (40.5, z0), (41.5, z0 + 1.0), (41.5, z0 + 1.6), (37.0, z0 + 1.8), (37.0, z0 + 7.8),
                         (41.5, z0 + 8.0), (41.5, zc0), (40.0, zt0 + 0.5), (30.0, zt0 + 0.5)])
    g = g - GR.spline_bore(HUB12_OUT[0], HUB12_OUT[1] + 0.3, HUB12_OUT[2] + 0.3, zt1 - z0).moved(at(z0))
    g = g - ring(29.5, HUB12_OUT[1] / 2 + 1.5, (z0 + zt1) / 2 - 3.7, (z0 + zt1) / 2 + 3.7)   # ball groove
    return _l(g, spec)


def thrust_washer_rear(spec) -> Part:
    z0, z1 = G.TW97
    w = ring(17.55, spec.nom("outside_diameter") / 2, z0, z1)
    return _l(w, spec)


# ---- laygear (items 83-89) -----------------------------------------------------------------------
def _lay(part):
    return part.moved(Location((G.LAY_UP, 0.0, 0.0)))


def laygear(spec) -> Part:
    """One-piece laygear: the three helical gears are made bored to the body radius and glued
    to the turned body, which carries the straight-cut first gear."""
    L = G.LAY
    a0, a1 = G.LAY_ENDS
    inner = {"constant": 26.0, "third": 23.0, "second": 18.5}
    prof = [(LAY_BORE_R, a0), (19.0, a0), (20.0, a0 + 1.0), (20.0, L["constant"][0]), (inner["constant"], L["constant"][0]),
            (inner["constant"], L["constant"][1]), (22.5, L["constant"][1]), (22.5, L["third"][0]),
            (inner["third"], L["third"][0]), (inner["third"], L["third"][1]), (21.0, L["third"][1]),
            (21.0, L["second"][0]), (inner["second"], L["second"][0]), (inner["second"], L["second"][1]),
            (17.0, L["second"][1] + 1.0), (13.8, L["second"][1] + 3.0), (13.8, L["first"][0] - 0.5),
            (LAY_BORE_R, L["first"][0] - 0.5)]
    body = Sh.revolved(prof)
    g1 = spur(11, L["first"][0], L["first"][1], shift=0.35, add=0.75)
    g1 = chamfer_ends(g1, GR.pitch_radius(11, MS) + MS * 1.2, *L["first"], c=1.0)
    body = body + g1 + zc(14.5, L["first"][1] - 0.5, a1)
    body = body - zc(LAY_BORE_R, a0 - 1, a1 + 1)
    body = body - ring(LAY_BORE_R - 0.5, LAY_BORE_R + 0.8, a0 + 2.0, a0 + 3.2)
    body = body - ring(LAY_BORE_R - 0.5, LAY_BORE_R + 0.8, a1 - 3.2, a1 - 2.0)
    for key, n in (("constant", 30), ("third", 26), ("second", 20)):
        body = GR.glue(body, helical(n, L[key][0], L[key][1], "right", bore=inner[key]))
    return _l(_lay(body), spec)


def layshaft(spec) -> Part:
    """Layshaft, the front end cut away to a step that the front cover holds (Sec 7 para 4)."""
    L = spec.nom("length")
    r = spec.nom("diameter") / 2
    z0 = -2.5
    s = Sh.chamfered_cyl(2 * r, L, 0.6).moved(at(z0))
    s = s - Box(2 * r, 2 * r + 2, 3.0, align=(Align.MAX, Align.CENTER, Align.MAX)).moved(Location((-1.5, 0, 0.0)))
    return _l(_lay(s), spec)


def lay_thrust_front(spec) -> Part:
    t = spec.nom("thickness")
    w = ring(LAYSHAFT_R + 0.3, spec.nom("outside_diameter") / 2, G.LAY_ENDS[0] - t, G.LAY_ENDS[0])
    w = w + Location((spec.nom("outside_diameter") / 2 - 2.0, 0, G.LAY_ENDS[0] - t - 1.5)) * Box(3.0, 4.0, 3.0)   # tag into the case
    return _l(_lay(w), spec)


def lay_thrust_rear(spec) -> Part:
    t = spec.nom("thickness")
    w = ring(LAYSHAFT_R + 0.3, spec.nom("outside_diameter") / 2, G.LAY_ENDS[1], G.LAY_ENDS[1] + t)
    return _l(_lay(w), spec)


ROLLER_SETS = [(G.LAY_ENDS[0] + 4.0, 22.0), (G.LAY_ENDS[1] - 4.0 - 44.5, 22.0), (G.LAY_ENDS[1] - 4.0 - 22.0, 22.0)]


def lay_needles(spec) -> Part:
    """One set of loose needle rollers (early laygear: rollers loose, three sets, Sec 5 paras 22-23)."""
    n = int(spec.nom("count"))
    L = spec.nom("length")
    rp = LAYSHAFT_R + NEEDLE_D / 2 + 0.02
    out = None
    for k in range(n):
        a = 2 * math.pi * k / n
        nd = Sh.chamfered_cyl(NEEDLE_D, L, 0.3).moved(at(0, rp * math.cos(a), rp * math.sin(a)))
        out = nd if out is None else out + nd
    return _l(_lay(out), spec)


def lay_distance_tube(spec) -> Part:
    z0 = ROLLER_SETS[0][0] + ROLLER_SETS[0][1] + 0.5
    z1 = ROLLER_SETS[1][0] - 0.5
    return _l(_lay(ring(LAYSHAFT_R + 0.3, LAY_BORE_R - 0.3, z0, z1)), spec)


def lay_ring(spec) -> Part:
    """Spring ring retaining the rollers in the laygear bore (built at the front end)."""
    z = G.LAY_ENDS[0] + 2.1
    r = ring(LAY_BORE_R - 0.4, LAY_BORE_R + 0.7, z, z + 1.0) - Location((LAY_BORE_R, 0, z + 0.5)) * Box(4, 2.5, 2)
    return _l(_lay(r), spec)


# ---- reverse (items 90-94) ----------------------------------------------------------------------
REV_W = (10.5, 11.0)                   # widths of the 13- and 17-tooth gears on the idler


def _rev_phase():
    """Turn of the idler about its axis so its 17 teeth interleave with the laygear's 11 (D)."""
    th = math.degrees(math.atan2(G.REV_LEFT, G.REV_UP - G.LAY_UP))          # laygear axis to idler axis
    pitch11 = 360.0 / 11
    k = round(th / pitch11)
    delta = th - k * pitch11                                                # laygear tooth off the centre line
    gap = 360.0 / 17 / 2                                                    # idler gap centre at 0 deg turn
    return (th + 180.0) - gap + delta * 11 / 17


def _rev(part, turn=False):
    loc = Location((G.REV_UP, G.REV_LEFT, 0.0))
    if turn:
        loc = loc * Rot(0, 0, _rev_phase())
    return part.moved(loc)


def reverse_shaft(spec) -> Part:
    r = spec.nom("diameter") / 2
    z0, z1 = G.REV_SHAFT_D
    s = Sh.chamfered_cyl(2 * r, z1 - z0 - 0.5, 0.6).moved(at(z0))
    s = s - Location((r, 0, z0 + 7.0)) * Box(6.0, 2 * r + 2, 6.5)                   # cut-out for the locating screw
    return _l(_rev(s), spec)


def reverse_gear(spec) -> Part:
    z0, z1 = G.REV_POS
    nb, ns = G.TEETH["reverse"]                                                 # 17 and 13
    small = spur(ns, z0, z0 + REV_W[0], add=0.8)
    big = spur(nb, z1 - REV_W[1], z1)
    g = chamfer_ends(small, GR.pitch_radius(ns, MS) + MS * 0.8, z0, z0 + REV_W[0], c=1.5)
    g = g + chamfer_ends(big, GR.pitch_radius(nb, MS) + MS, z1 - REV_W[1], z1, c=1.2)
    g = g + zc(15.0, z0 + REV_W[0] - 0.5, z1 - REV_W[1] + 0.5)                   # groove for the selector fork
    g = g - zc(spec.nom("bore") / 2, z0 - 1, z1 + 1)
    return _l(_rev(g, turn=True), spec)


def reverse_bush(spec) -> Part:
    z0, z1 = G.REV_POS
    return _l(_rev(ring(0.625 * IN / 2 + 0.05, spec.nom("outside_diameter") / 2, z0 + 0.5, z1 - 0.5)), spec)


def reverse_screw(spec) -> Part:
    from mgb import fasteners as F
    b = F.hex_bolt("1/4", spec.nom("length") / IN)
    z = G.REV_SHAFT_D[0] + 7.0
    return _l(Location((G.REV_UP + 14.9, G.REV_LEFT, z)) * Rot(0, -90, 0) * b, spec)


def reverse_tab_washer(spec) -> Part:
    t = spec.nom("thickness")
    z = G.REV_SHAFT_D[0] + 7.0
    w = Sh.washer(14.0, 6.6, t) + Location((0, 9.0, t / 2)) * Box(7.0, 8.0, t)
    w = w + Location((0, 12.4, -3.0 + t)) * Box(7.0, t, 6.0)
    return _l(Location((G.REV_UP + 14.0, G.REV_LEFT, z)) * Rot(0, 90, 0) * w.moved(at(0)), spec)


PARTS = {
    "gearbox.shafts.first-motion-shaft": {"build": first_motion_shaft},
    "gearbox.shafts.fms-bearing": {"build": fms_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.shafts.fms-ring": {"build": fms_ring},
    "gearbox.shafts.fms-shim": {"build": fms_shim, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.shafts.fms-needles": {"build": fms_needles},
    "gearbox.shafts.fms-lock-washer": {"build": fms_lock_washer},
    "gearbox.shafts.fms-nut": {"build": fms_nut},
    "gearbox.shafts.mainshaft": {"build": mainshaft},
    "gearbox.shafts.oil-restrictor": {"build": oil_restrictor},
    "gearbox.shafts.centre-bearing": {"build": centre_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.shafts.bearing-housing": {"build": bearing_housing},
    "gearbox.shafts.housing-peg": {"build": housing_peg},
    "gearbox.shafts.mainshaft-clip": {"build": mainshaft_clip},
    "gearbox.shafts.synchro-hub-34": {"build": synchro_hub_34},
    "gearbox.shafts.coupling-sleeve": {"build": coupling_sleeve, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.shafts.baulk-ring-34": {"build": baulk_ring_34_front},
    "gearbox.shafts.baulk-ring-34-rear": {"build": baulk_ring_34_rear},
    "gearbox.shafts.synchro-spring": {"build": spring},
    "gearbox.shafts.synchro-ball": {"build": ball, "probes": {"diameter": lambda p: probes.bbox_size(p, "x")}},
    "gearbox.shafts.third-gear": {"build": third_gear},
    "gearbox.shafts.third-gear-bush": {"build": third_gear_bush},
    "gearbox.shafts.interlock-ring": {"build": interlock_ring},
    "gearbox.shafts.second-gear": {"build": second_gear},
    "gearbox.shafts.second-gear-bush": {"build": second_gear_bush},
    "gearbox.shafts.third-gear-washer": {"build": thrust_washer_3},
    "gearbox.shafts.peg": {"build": peg},
    "gearbox.shafts.peg-spring": {"build": peg_spring},
    "gearbox.shafts.baulk-ring-2": {"build": baulk_ring_2},
    "gearbox.shafts.synchro-hub-12": {"build": synchro_hub_12},
    "gearbox.shafts.first-gear": {"build": first_gear},
    "gearbox.shafts.rear-thrust-washer": {"build": thrust_washer_rear},
    "gearbox.shafts.laygear": {"build": laygear},
    "gearbox.shafts.layshaft": {"build": layshaft, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.shafts.lay-thrust-front": {"build": lay_thrust_front},
    "gearbox.shafts.lay-thrust-rear": {"build": lay_thrust_rear, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "gearbox.shafts.lay-needles": {"build": lay_needles},
    "gearbox.shafts.lay-distance-tube": {"build": lay_distance_tube},
    "gearbox.shafts.lay-ring": {"build": lay_ring},
    "gearbox.shafts.reverse-shaft": {"build": reverse_shaft},
    "gearbox.shafts.reverse-gear": {"build": reverse_gear},
    "gearbox.shafts.reverse-bush": {"build": reverse_bush},
    "gearbox.shafts.reverse-screw": {"build": reverse_screw},
    "gearbox.shafts.reverse-tab-washer": {"build": reverse_tab_washer},
}
