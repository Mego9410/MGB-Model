"""Differential carrier (nose piece) and the pinion with its bearings, three-quarter floating banjo axle
(Haynes Ch 8 Fig 8.1 items 7, 8, 12-17, 27 (pinion), 30-39; Sec 7, Sec 8, printed p142-145).

Drawn in the axle frame of mgb.rear_axle_layout (origin on the axle centre, car axes); the pinion
axis runs fore and aft 1 in below the axle centre (hypoid offset, D).

Forms (Fig 8.1 item 13): a cast carrier - the round flange on the case studs with its spigot into
the banjo opening, the tapering nose with four ribs carrying the two pinion bearing cups and the
oil seal, and behind the flange two saddles with lightening windows holding the differential
bearings under two caps on studs (the caps shown with the carrier as item 13). Pinion (item 27):
spiral-toothed head, bearing seats, splines and the thread for the flange nut. Flange (item 37):
splined hub running in the seal, a recessed face for the nut, four holes on the propeller shaft
pitch circle with ears behind. Dust cover (item 36): pressed steel shield on the flange.
"""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Location, Part, Rot, extrude

from mgb import bearings as BR, bevel as BV, fasteners as F, gears as GR, probes, rear_axle_layout as A, shapes as Sh
from mgb.poly2d import circle_pts, hull
from parts.axle.casing import xrev, yrev
from parts.gearbox import casing as C
from parts.propshaft.shaft import ring, xcyl, xprism, ycyl, yprism

IN = 25.4
zc, box = C.zc, C.box
PZ = A.PINION_Z
PINION_PHASE = -22.5                          # teeth in mesh with the crown wheel (least overlap, interference check)


def _l(p, spec):
    p.label = spec.id
    return p


def on_pinion(p):
    """Something drawn about the x axis, moved onto the pinion axis."""
    return Location((0, 0, PZ)) * p


def along_pinion(p, x0):
    """A part drawn along +z from 0, turned forward along the pinion axis from station x0."""
    return Location((x0, 0, PZ)) * Rot(0, 90, 0) * p


def keep_in_opening(p, x0=-60.0, x1=A.CARRIER_FLANGE[0] + 0.01):
    """Everything behind the flange must pass through the banjo opening."""
    return p & xcyl(A.OPENING_R - 0.7, x0, x1)


# =================================================================================================
# carrier casting (item 13) and its caps
# =================================================================================================
BASE_OUT = [(0, 82.0), (101.0, 82.0), (101.0, 97.0), (80.0, 115.0), (62.0, 130.0), (0, 130.0)]   # about the axle axis
BASE_IN = [(0, 50.0), (96.0, 50.0), (96.0, 60.0), (76.0, 80.0), (66.0, 86.0), (54.0, 94.0), (50.0, 96.0), (40.0, 97.5), (0, 97.5)]
NOSE_OUT = [(0, 105.0), (66.0, 105.0), (66.0, 112.0), (60.0, 125.0), (52.0, 145.0), (46.0, 168.0), (44.0, 238.0),
            (41.0, 246.0), (41.0, 268.0), (38.0, 272.0), (38.0, A.NOSE_END_X - 0.8), (37.2, A.NOSE_END_X), (0, A.NOSE_END_X)]
NOSE_IN = [(0, 70.0), (60.0, 70.0), (60.0, 96.0), (A.RBRG[1] / 2, 100.0), (A.RBRG[1] / 2, A.RBRG_X[1]),
           (28.0, A.RBRG_X[1] + 2.0), (28.0, A.FBRG_X[0]), (A.FBRG[1] / 2, A.FBRG_X[0]), (A.FBRG[1] / 2, A.FBRG_X[1]),
           (26.0, A.FBRG_X[1]), (26.0, A.SEAL_X[0]), (A.SEAL[1] / 2, A.SEAL_X[0]), (A.SEAL[1] / 2, A.NOSE_END_X + 1),
           (0, A.NOSE_END_X + 1)]


def _saddle(side, cap=False):
    y0, y1 = A.SADDLE_Y
    if cap:
        prof = [(0.0, -58.0), (0.0, 58.0), (-30.0, 58.0), (A.CAP_X[0], 32.0), (A.CAP_X[0], -32.0), (-30.0, -58.0)]
        s = yprism(prof, y0, y1)
        s = keep_in_opening(s)
        for z in (A.CAP_STUD_Z, -A.CAP_STUD_Z):
            s = s - xcyl(5.0, A.CAP_X[0] - 1, 1.0, (y0 + y1) / 2, z)
            s = s - xcyl(9.5, A.CAP_X[0] - 1, A.CAP_X[0] + 0.6, (y0 + y1) / 2, z)          # spot face
        s = s - Location((A.CAP_X[0] - 0.2, (y0 + y1) / 2 + 6.0, 20.0)) * Rot(0, 90, 0) * Cylinder(1.0, 1.0)   # punch marks
    else:
        prof = [(0.0, -62.0), (0.0, 62.0), (30.0, 72.0), (70.0, 96.0), (A.CARRIER_FLANGE[0] + 2.0, 96.0),
                (A.CARRIER_FLANGE[0] + 2.0, -96.0), (70.0, -96.0), (30.0, -72.0)]
        s = yprism(prof, y0, y1)
        s = keep_in_opening(s, -1.0, A.CARRIER_FLANGE[0] + 2.0)
        s = s - yprism([(36.0, -44.0), (36.0, 44.0), (62.0, 66.0), (62.0, -66.0)], y0 - 1, y1 + 1)     # lightening window
        for z in (A.CAP_STUD_Z, -A.CAP_STUD_Z):
            s = s - xcyl(4.78, -1.0, 26.0, (y0 + y1) / 2, z)
    s = s - ycyl(A.DIFF_BRG[1] / 2, y0 - 1, A.DIFF_BRG_Y[1] + A.PACKING_T)
    s = s - ycyl(34.0, y0 - 1, y1 + 1)
    return s if side > 0 else s.mirror(__import__("build123d").Plane.XZ)


def carrier(spec) -> Part:
    f0, f1 = A.CARRIER_FLANGE
    c = xrev([(96.5, f0), (A.RING_R, f0), (A.RING_R, f1 - 0.8), (A.RING_R - 0.8, f1), (96.5, f1)])
    c = c + xrev([(96.5, 60.0), (A.OPENING_R - 0.7, 60.0), (A.OPENING_R - 0.7, f0 + 0.01), (96.5, f0 + 0.01)])   # spigot
    nose = xrev(NOSE_OUT)
    # four ribs along the nose
    rib_env = xrev([(r + 5.0, x) for r, x in NOSE_OUT[2:9]] + [(0, 236.0), (0, 112.0)])
    for a in (0, 90, 180, 270):
        nose = nose + (rib_env & (Rot(a, 0, 0) * box(112.0, 245.0, -3.0, 3.0, 0.0, 130.0)))
    nose = on_pinion(nose) + xrev(BASE_OUT)
    c = c + nose
    for s in (1, -1):
        c = c + _saddle(s)
    # inside: crown wheel space behind the nose, pinion bores, seal bore
    c = c - on_pinion(xrev(NOSE_IN))
    c = c - xrev(BASE_IN)
    for a in A.CASE_STUD_ANGLES:
        y, z = A.CASE_STUD_R * math.sin(math.radians(a)), A.CASE_STUD_R * math.cos(math.radians(a))
        c = c - xcyl(4.3, f0 - 1, f1 + 1, y, z)
    # cast-in mark on the nose side
    c = c - Location((180.0, -45.5, PZ)) * Rot(90, 0, 0) * Box(22.0, 7.0, 1.0)
    return _l(c, spec)


def bearing_cap(spec) -> Part:
    """A cap on the left saddle (the assembly mirrors it for the right)."""
    return _l(_saddle(1, cap=True), spec)


def gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = xrev([(A.OPENING_R - 0.5, A.CASE_FACE_X), (A.RING_R, A.CASE_FACE_X), (A.RING_R, A.CASE_FACE_X + t), (A.OPENING_R - 0.5, A.CASE_FACE_X + t)])
    for a in A.CASE_STUD_ANGLES:
        y, z = A.CASE_STUD_R * math.sin(math.radians(a)), A.CASE_STUD_R * math.cos(math.radians(a))
        g = g - xcyl(4.3, A.CASE_FACE_X - 1, A.CASE_FACE_X + 2, y, z)
    return _l(g, spec)


def cap_stud(spec) -> Part:
    d = F.THREADS[A.CAP_STUD][0] * IN
    L = spec.nom("length")
    s = Sh.chamfered_cyl(d, L, 0.7)
    p = IN / 24
    for z0, n in ((1.5, 12), (L - 18.0, 14)):
        for k in range(n):
            s = s - ring(d / 2 - 0.5, d / 2 + 1, z0 + k * p, z0 + k * p + 0.45 * p)
    return _l(s, spec)


def nut(size):
    def b(spec):
        return _l(F.hex_nut(size), spec)
    return b


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


# =================================================================================================
# pinion (27), thrust washer (30), bearings (31, 33), spacer (32), shim (34), seal (35), dust cover
# (36), flange (37), nut (38), spring washer (39)
# =================================================================================================
def pinion_bevel():
    return BV.Bevel(A.Z_PINION, A.CROWN_PITCH_R * A.Z_PINION / A.Z_CROWN, A.PITCH_ANGLE_PINION, A.FACE_W, 5.6, 2.7,
                    spiral_deg=35.0, hand=-1, sections=4)


def pinion(spec) -> Part:
    bv = pinion_bevel()
    h0, h1 = bv.cone_pt(0.0, -2.4), bv.cone_pt(A.FACE_W, -2.4)
    hb = A.PINION_HEEL_X - A.CROWN_PITCH_R                      # head back face behind the heel pitch plane
    # head body in the gear frame (z toward the apex, i.e. rearward)
    head = Sh.revolved([(0, -hb), (h0[0] + 1.0, -hb), (h0[0], h0[1]), (h1[0], h1[1]), (h1[0] - 2.0, h1[1] + 1.0), (0, h1[1] + 1.0)])
    g = BV.gear(bv, head, PINION_PHASE)
    g = Location((A.CROWN_PITCH_R, 0, PZ)) * Rot(0, -90, 0) * g
    # shank, forward along the pinion axis
    r_rb, r_fb = A.RBRG[0] / 2, A.FBRG[0] / 2
    n, dmaj, dmin = A.PINION_SPLINE
    sp0, sp1 = A.FBRG_X[1], A.PINION_RECESS[1] - 2.0
    th0, th1 = sp1, A.PINION_NUT_X[1] + 2.0
    shank = xrev([(0, A.PINION_HEEL_X - 0.5), (r_rb, A.PINION_HEEL_X - 0.5), (r_rb, A.RBRG_X[1]), (r_fb + 1.0, A.RBRG_X[1] + 0.3), (r_fb + 1.0, A.FBRG_X[0] - 3.0),
                  (r_fb, A.FBRG_X[0]), (r_fb, A.FBRG_X[1]), (dmin / 2, A.FBRG_X[1] + 0.5), (dmin / 2, sp1), (9.2, th0 + 0.5),
                  (9.2, th1 - 0.8), (8.4, th1), (0, th1)])
    g = g + on_pinion(shank)
    g = g + along_pinion(GR.spline_shaft(n, dmaj, dmin, sp1 - sp0 - 3.0), sp0 + 1.0)
    p = IN / 16
    k = 0
    while th0 + 1.5 + k * p < th1 - 1.0:
        x = th0 + 1.5 + k * p
        g = g - on_pinion(xrev([(8.7, x), (9.6, x), (9.6, x + 0.45 * p), (8.7, x + 0.45 * p)]))
        k += 1
    return _l(g, spec)


def thrust_washer(spec) -> Part:
    t = spec.nom("thickness")
    return _l(on_pinion(xrev([(A.RBRG[0] / 2 + 0.1, A.PINION_HEEL_X), (27.0, A.PINION_HEEL_X), (27.0, A.PINION_HEEL_X + t),
                               (A.RBRG[0] / 2 + 0.1, A.PINION_HEEL_X + t)])), spec)


def rear_bearing(spec) -> Part:
    b = BR.taper_roller(*A.RBRG)
    return _l(along_pinion(b, A.RBRG_X[0]), spec)


def front_bearing(spec) -> Part:
    b = BR.taper_roller(*A.FBRG)
    b = Location((0, 0, A.FBRG[2])) * Rot(180, 0, 0) * b                       # large ends face each other's outside
    return _l(along_pinion(b, A.FBRG_X[0]), spec)


def spacer(spec) -> Part:
    x0, x1 = A.SPACER_X
    s = xrev([(16.5, x0), (21.5, x0), (21.5, x0 + 8.0), (19.5, x0 + 16.0), (19.5, x1 - 16.0), (21.0, x1 - 8.0),
              (21.0, x1), (16.5, x1)])
    return _l(on_pinion(s), spec)


def shim(spec) -> Part:
    t = spec.nom("thickness")
    return _l(on_pinion(xrev([(A.FBRG[0] / 2 + 0.1, A.SPACER_X[1]), (22.0, A.SPACER_X[1]), (22.0, A.SPACER_X[1] + t),
                               (A.FBRG[0] / 2 + 0.1, A.SPACER_X[1] + t)])), spec)


def oil_seal(spec) -> Part:
    ri, ro, w = A.SEAL[0] / 2, A.SEAL[1] / 2, A.SEAL[2]
    x0 = A.SEAL_X[0]
    s = xrev([(ro - 1.8, x0), (ro, x0), (ro, x0 + w), (ri + 3.0, x0 + w), (ri + 3.0, x0 + w - 1.0), (ro - 1.8, x0 + w - 1.0)])
    s = s + xrev([(ri, x0 + 2.0), (ri + 4.5, x0 + 0.8), (ro - 1.8, x0 + 0.8), (ro - 1.8, x0 + w - 1.0), (ri + 4.0, x0 + w - 1.0),
                  (ri + 0.8, x0 + 5.5)])                                          # lip toward the inside (Sec 7 para 6)
    s = s + xrev([(ri + 4.6, x0 + 2.8), (ri + 6.8, x0 + 2.8), (ri + 6.8, x0 + 5.0), (ri + 4.6, x0 + 5.0)])   # garter spring
    return _l(on_pinion(s), spec)


DC_X = A.NOSE_END_X + 1.5


def dust_cover(spec) -> Part:
    """Pressed steel end cover on the flange hub, its skirt over the end of the nose."""
    t = spec.nom("thickness")
    c = xrev([(A.SEAL[0] / 2 + 0.05, DC_X), (43.5, DC_X), (43.5, DC_X - 13.0), (43.5 - t, DC_X - 13.0), (43.5 - t, DC_X - t),
              (A.SEAL[0] / 2 + 0.05, DC_X - t)])
    c = c + xrev([(A.SEAL[0] / 2 + 0.05, DC_X - 0.01), (25.0, DC_X - 0.01), (25.0, DC_X + 2.0), (A.SEAL[0] / 2 + 0.05, DC_X + 2.0)])
    return _l(on_pinion(c), spec)


def flange(spec) -> Part:
    face = A.PINION_FLANGE_FACE_X
    d0 = A.PINION_FLANGE_DISC[0]
    rr, rf = A.PINION_RECESS
    R = A.PINION_FLANGE_R
    rs = A.SEAL[0] / 2
    f = xrev([(15.3, A.FBRG_X[1]), (rs - 0.8, A.FBRG_X[1]), (rs, A.FBRG_X[1] + 0.8), (rs, DC_X + 2.0), (rs + 2.0, DC_X + 2.0),
              (22.0, DC_X + 6.0), (24.0, d0 - 8.0), (30.0, d0 - 1.5), (R - 3.0, d0), (R, d0 + 1.5), (R, face), (rr, face),
              (rr, rf), (13.0, rf)])
    pcd = A.PINION_FLANGE_PCD / 2
    for a in A.PINION_FLANGE_HOLES:
        y, z = pcd * math.sin(math.radians(a)), pcd * math.cos(math.radians(a))
        f = f + xcyl(8.5, d0 - 5.0, d0 + 0.5, y, z)
    for a in A.PINION_FLANGE_HOLES:
        y, z = pcd * math.sin(math.radians(a)), pcd * math.cos(math.radians(a))
        f = f - xcyl(4.15, d0 - 6.0, face + 1.0, y, z)
    n, dmaj, dmin = A.PINION_SPLINE
    f = on_pinion(f) - along_pinion(GR.spline_bore(n, dmaj, dmin, rf - A.FBRG_X[1]), A.FBRG_X[1])
    return _l(f, spec)


def pinion_nut(spec) -> Part:
    """Item 38: 3/4 UNF thin locknut (MGOC FNZ612) in the flange recess."""
    from build123d import RegularPolygon
    af = spec.nom("across_flats")
    h = A.PINION_NUT_X[1] - A.PINION_NUT_X[0]
    n = extrude(RegularPolygon(af / math.sqrt(3), 6), h)
    n = n & Sh.revolved([(0, -0.1), (af / 2 + 0.3, -0.1), (af / math.sqrt(3) + 0.5, 1.2), (af / math.sqrt(3) + 0.5, h - 1.2),
                         (af / 2 + 0.3, h + 0.1), (0, h + 0.1)])
    n = n - zc(9.53, -1, h + 1)
    for k in range(4):
        z = 0.8 + k * IN / 16
        n = n + ring(8.9, 9.6, z, z + 0.7)
    return _l(along_pinion(n, A.PINION_NUT_X[0]), spec)


def pinion_washer(spec) -> Part:
    t = spec.nom("thickness")
    w = Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), t)
    w = w - Location((10.0, 0, t / 2)) * Rot(0, 0, 20) * Box(10.0, 1.4, t + 1)
    return _l(along_pinion(w, A.PINION_RECESS[1]), spec)


def _flange_d(p):
    bb = p.bounding_box()
    return bb.size.Y


PARTS = {
    "axle.carrier.carrier": {"build": carrier},
    "axle.carrier.bearing-cap": {"build": bearing_cap},
    "axle.carrier.gasket": {"build": gasket, "probes": {"thickness": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.carrier-nut": {"build": nut("5/16")},
    "axle.carrier.carrier-washer": {"build": C.spring_washer, "probes": C.WASHER},
    "axle.carrier.cap-stud": {"build": cap_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "axle.carrier.cap-plain-washer": {"build": washer, "probes": C.WASHER},
    "axle.carrier.cap-spring-washer": {"build": C.spring_washer, "probes": C.WASHER},
    "axle.carrier.cap-nut": {"build": nut("3/8")},
    "axle.carrier.pinion": {"build": pinion},
    "axle.carrier.pinion-thrust-washer": {"build": thrust_washer, "probes": {"thickness": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.rear-pinion-bearing": {"build": rear_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "y")}},
    "axle.carrier.bearing-spacer": {"build": spacer},
    "axle.carrier.pinion-shim": {"build": shim, "probes": {"thickness": lambda p: probes.bbox_size(p, "x")}},
    "axle.carrier.front-pinion-bearing": {"build": front_bearing, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "y")}},
    "axle.carrier.pinion-seal": {"build": oil_seal, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "y")}},
    "axle.carrier.dust-cover": {"build": dust_cover},
    "axle.carrier.pinion-flange": {"build": flange, "probes": {"diameter": _flange_d}},
    "axle.carrier.pinion-nut": {"build": pinion_nut},
    "axle.carrier.pinion-washer": {"build": pinion_washer},
}
