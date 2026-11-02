"""Hardy Spicer propeller shaft, overdrive length, non-sealed (greasable) joints, 1963 MGB (Haynes Ch 7:
Fig 7.1 items 1-16, Fig 7.4, Fig 7.5; Sec 2-4, printed p138-141; photos 5.2, 5.4a-d).

Each part is drawn in its own frame (mgb.propshaft_layout): flange yokes from their joint face
along +z, journal axis along local x; the sleeve yoke and the shaft along +z from the front joint
centre (sleeve) or from the front end of the splined stub (shaft), journal axis along local y;
joint parts (spider, cups, gaskets, retainers, circlips) about the joint centre, journal parts
along +z from the joint centre outward. The assembly places them.

Forms: flange yoke (Fig 7.1 item 2, photos 5.4b-d) - a round flange with four holes and a recessed
face, two forged ears springing from its back with round eye bosses, a groove for the circlip in
each eye; spider (Fig 7.1 item 8, photo 5.4b) - a square centre with four ground journals, a
shoulder at the root of each for the gasket, drilled for grease, a lubricator in the centre on
the shaft side; needle bearing cup (item 9) - a drawn cup with its needles; sleeve yoke (item 3) -
ears, a hexagonal boss for the lubricator (item 4, Fig 7.4), the splined sleeve threaded for the
dust cap, an arrow; shaft (item 1, Fig 7.4) - splined stub, swaged cone, tube with its bands,
the welded yoke at the rear; dust cap knurled.
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Face, Location, Part, Rot, Sphere, Wire, extrude

from mgb import fasteners as F, gears as GR, probes, propshaft_layout as P, shapes as Sh
from mgb.poly2d import circle_pts, hull
from parts.gearbox import casing as C

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
zc, box = C.zc, C.box


def _l(p, spec):
    p.label = spec.id
    return p


def ring(r0, r1, z0, z1):
    return Sh.revolved([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def xprism(pts_yz, x0, x1):
    """Prism along x of a polygon given as (y, z) points."""
    face = Face(Wire.make_polygon([(0.0, y, z) for y, z in pts_yz], close=True))
    return extrude(face, x1 - x0, dir=(1, 0, 0)).moved(Location((x0, 0, 0)))


def yprism(pts_xz, y0, y1):
    """Prism along y of a polygon given as (x, z) points."""
    face = Face(Wire.make_polygon([(x, 0.0, z) for x, z in pts_xz], close=True))
    return extrude(face, y1 - y0, dir=(0, 1, 0)).moved(Location((0, y0, 0)))


def xcyl(r, x0, x1, y=0.0, z=0.0):
    return Location((x0, y, z)) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=BASE)


def ycyl(r, y0, y1, x=0.0, z=0.0):
    return Location((x, y0, z)) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=BASE)


def _ears(axis, zc_, base_z, base_half, inner=P.EAR_IN, outer=P.EAR_OUT):
    """Two yoke ears either side of the joint along `axis` ('x' or 'y'): each a forged lug from the
    yoke base (half width base_half at z base_z) to the round eye boss at z zc_, bored for the cup
    with a circlip groove near the outside."""
    prof = hull(circle_pts(0.0, zc_, P.EYE_R, 32) + [(-base_half, base_z), (base_half, base_z)])
    out = None
    for s in (1, -1):
        a, b = (inner, outer) if s > 0 else (-outer, -inner)
        e = xprism(prof, a, b) if axis == "x" else yprism(prof, a, b)
        out = e if out is None else out + e
    out = out & zc(outer + 2.5, zc_ - 60.0, zc_ + 60.0)                        # forged ears turned round on the outside
    for s in (1, -1):
        a = s * (P.CUP_SPAN / 2 + 0.1)
        lo, hi = (a, a + s * 1.25) if s > 0 else (a + s * 1.25, a)
        if axis == "x":
            out = out - xcyl(P.CUP_D / 2, -P.EAR_OUT - 1, P.EAR_OUT + 1, 0, zc_)
            out = out - xcyl(P.CUP_D / 2 + 1.1, lo, hi, 0, zc_)
        else:
            out = out - ycyl(P.CUP_D / 2, -P.EAR_OUT - 1, P.EAR_OUT + 1, 0, zc_)
            out = out - ycyl(P.CUP_D / 2 + 1.1, lo, hi, 0, zc_)
    return out


# =================================================================================================
# flange yoke (item 2), front on the overdrive flange and rear on the pinion flange
# =================================================================================================
def flange_yoke(spec) -> Part:
    R, t, c = P.FLANGE_R, P.FLANGE_T, P.FACE_TO_JOINT
    rr, rd = P.RECESS
    disc = Sh.revolved([(0, 0), (R - 0.8, 0), (R, 0.8), (R, t - 0.6), (R - 0.6, t), (31.0, t), (27.0, t + 6.0), (0, t + 6.0)])
    y = disc + _ears("x", c, t - 0.5, 19.0)
    # web between the ears' roots, under the joint
    y = y + box(-P.EAR_IN - 0.5, P.EAR_IN + 0.5, -14.0, 14.0, t - 0.5, t + 5.5)
    y = y - zc(rr, -1.0, rd)                                                     # clearance for the companion flange nut
    y = y - Sh.revolved([(rr - 0.01, rd - 0.01), (rr + 1.5, -0.5), (rr - 0.01, -0.5)])     # chamfer into the recess
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        y = y - zc(P.HOLE_D / 2, -1.0, t + 8.0, P.PCD / 2 * math.cos(a), P.PCD / 2 * math.sin(a))
    # balance-mark scratch line on the rim (Sec 3 para 2) and the forging parting line on the ears
    y = y - box(R - 3.0, R + 1.0, -0.4, 0.4, -0.1, t + 0.1)
    return _l(y, spec)


# =================================================================================================
# universal joint: spider, needle bearing, gasket, retainer, circlip, lubricator (items 8-13)
# =================================================================================================
def spider(spec) -> Part:
    body = Box(26.0, 26.0, 20.0)
    from build123d import fillet
    try:
        body = fillet(body.edges(), 3.0)
    except Exception:
        pass
    s = body
    jr, sh = P.JOURNAL_D / 2, P.SHOULDER_R
    tip = P.CUP_SPAN / 2 - P.CUP_BASE - 0.35
    arm = Sh.revolved([(0, 10.0), (11.0, 10.0), (11.0, sh - 1.0), (10.0, sh), (jr, sh), (jr, tip - 0.6), (jr - 0.6, tip), (0, tip)])
    arm = arm - zc(1.3, sh, tip + 1)                                             # grease drilling to the cup
    for rot in (Rot(0, 90, 0), Rot(0, -90, 0), Rot(-90, 0, 0), Rot(90, 0, 0)):
        s = s + rot * arm
    # lubricator boss on the shaft side (+z), between the arms, tapped
    d = _nipple_dir()
    s = s - _along(d) * zc(1.95, 4.0, NIPPLE_SEAT + 0.5)
    return _l(s, spec)


def _nipple_dir():
    a = math.radians(40.0)
    return (math.sin(a) * math.cos(math.radians(45)), math.sin(a) * math.sin(math.radians(45)), math.cos(a))


def _along(d):
    """Rotation taking +z to the unit vector d."""
    x, y, z = d
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, z))))
    az = math.degrees(math.atan2(y, x))
    return Rot(0, 0, az) * Rot(0, tilt, 0)


NIPPLE_SEAT = 13.2


def lubricator(spec) -> Part:
    """Item 13: grease nipple screwed into the spider: thread, hex, neck, ball head (drawn along +z
    from its seat face)."""
    from build123d import RegularPolygon
    hx = extrude(RegularPolygon(5.6 / math.sqrt(3), 6), 3.0)
    hx = hx & Sh.revolved([(0, -0.1), (2.9, -0.1), (3.4, 0.5), (3.4, 2.5), (2.9, 3.1), (0, 3.1)])     # chamfered corners
    n = zc(1.9, -6.0, 0.2) + hx + Sh.revolved([(0, 2.9), (1.6, 2.9), (1.6, 6.2), (0, 6.2)])
    n = n + Location((0, 0, 7.6)) * Sphere(2.2)
    n = n - zc(0.6, 8.0, 10.5)
    return _l(n, spec)


def needle_bearing(spec) -> Part:
    """Item 9: drawn cup and its needle rollers, base at z = 0, open toward +z (the assembly turns the
    open end to the spider)."""
    ro, ri, L, b = P.CUP_D / 2, P.CUP_D / 2 - 2.6, P.CUP_LEN, P.CUP_BASE
    cup = Sh.revolved([(0, 0), (ro - 0.6, 0), (ro, 0.6), (ro, L - 0.3), (ro - 0.3, L), (ri, L), (ri, b), (0, b)])
    rd = P.ROLLER_D / 2
    pc = ri - rd + 0.06
    n = int(2 * math.pi * pc / (2 * rd * 1.04))
    for k in range(n):
        a = 2 * math.pi * k / n
        cup = cup + Sh.chamfered_cyl(2 * rd, L - b - 2.2, 0.3, z0=b + 0.6).moved(Location((pc * math.cos(a), pc * math.sin(a), 0)))
    return _l(cup, spec)


def gasket(spec) -> Part:
    """Item 11: cork gasket on the journal shoulder, z from 0 (shoulder) outward."""
    return _l(ring(P.JOURNAL_D / 2 + 0.3, 12.0, 0.0, spec.nom("thickness")), spec)


def gasket_retainer(spec) -> Part:
    """Item 12: pressed steel retainer over the gasket, its lip shrouding the gasket's edge."""
    t = 0.6
    r = Sh.revolved([(P.JOURNAL_D / 2 + 0.3, 0), (12.6, 0), (12.6, -1.8), (13.2, -1.8), (13.2, t), (P.JOURNAL_D / 2 + 0.3, t)])
    r = r + ring(12.6, 13.2, t - 0.01, 1.4)
    return _l(r, spec)


def circlip(spec) -> Part:
    """Item 10 (Fig 7.5 item 4): internal circlip in the yoke eye outside the cup, with two lugs."""
    t = spec.nom("thickness")
    ro, ri = P.CUP_D / 2 + 1.0, P.CUP_D / 2 - 1.2
    c = ring(ri, ro, 0, t)
    g = math.radians(36.0)
    c = c - Location((ri, 0, t / 2)) * Box(2 * (ro - ri) + 2, 2 * ro * math.sin(g / 2), t + 2)
    for s in (1, -1):
        a = s * (g / 2 + 0.2)
        x, y = (ri - 1.0) * math.cos(a), (ri - 1.0) * math.sin(a)
        c = c + zc(1.6, 0, t, x, y)
        c = c - zc(0.6, -1, t + 1, x, y)
    return _l(c, spec)


# =================================================================================================
# sleeve yoke (3), its lubricator (4), dust cap (5), steel and cork washers (6, 7)
# =================================================================================================
def sleeve_yoke(spec) -> Part:
    z0, z1 = P.SLEEVE_TUBE_Z
    r = P.SLEEVE_R
    body = Sh.revolved([(0, 19.0), (19.5, 19.0), (19.5, 23.0), (r, z0), (r, z1 - 0.8), (r - 0.8, z1), (0, z1)])
    y = body + _ears("y", 0.0, 22.0, 20.0)
    y = y + box(-14.0, 14.0, -P.EAR_IN - 0.5, P.EAR_IN + 0.5, 20.5, 27.0)
    # hexagonal lubricator boss on top (Fig 7.4)
    from build123d import RegularPolygon
    hb = extrude(RegularPolygon(13.0 / math.sqrt(3), 6), 6.5)
    y = y + Location((r - 2.5, 0, P.NIPPLE_Z)) * Rot(0, 90, 0) * hb
    y = y - xcyl(1.9, 10.0, r + 5.0, 0, P.NIPPLE_Z)
    # internal splines for the stub, thread for the dust cap
    n, dmaj, dmin = P.SPLINE
    b0, b1 = P.SLEEVE_BORE_Z
    y = y - GR.spline_bore(n, dmaj, dmin, b1 - b0).moved(Location((0, 0, b0)))
    y = y - zc(dmin / 2 + 0.1, b0 - 4.0, b0 + 1)
    t0, t1 = P.SLEEVE_THREAD_Z
    pitch = IN / 20
    k = 0
    while t0 + 1.0 + k * pitch < t1 - 1.0:
        z = t0 + 1.0 + k * pitch
        y = y - ring(r - 0.7, r + 1, z, z + pitch * 0.45)
        k += 1
    # alignment arrow (Sec 4 para 11) on the left of the sleeve
    y = y - Location((0, r - 0.4, 95.0)) * Rot(-90, 0, 0) * extrude(
        Face(Wire.make_polygon([(-2.5, -4.0, 0), (2.5, -4.0, 0), (0, 4.0, 0)], close=True)), 1.0)
    y = y - Location((0, r - 0.4, 85.0)) * Rot(-90, 0, 0) * Box(1.6, 10.0, 2.0)
    return _l(y, spec)


def sleeve_lubricator(spec) -> Part:
    """Item 4: straight grease nipple in the sleeve yoke boss."""
    return _l(lubricator(spec), spec)


def dust_cap(spec) -> Part:
    z0, z1 = P.CAP_Z
    ro = spec.nom("outside_diameter") / 2
    c = Sh.revolved([(P.SLEEVE_R + 0.05, z0), (ro - 0.5, z0), (ro, z0 + 0.5), (ro, z1 - 1.0), (ro - 1.0, z1),
                     (P.SPLINE[1] / 2 + 0.6, z1), (P.SPLINE[1] / 2 + 0.6, P.CORK_WASHER_Z[1] + 0.6),
                     (18.0, P.CORK_WASHER_Z[1] + 0.6), (18.0, P.SLEEVE_TUBE_Z[1] + 0.02), (P.SLEEVE_R + 0.05, P.SLEEVE_TUBE_Z[1] + 0.02)])
    for k in range(36):                                                          # knurl
        c = c - Rot(0, 0, 10.0 * k) * box(ro - 0.5, ro + 1, -0.5, 0.5, z0 + 2.0, z1 - 2.5)
    pitch = IN / 20
    t0, t1 = P.SLEEVE_THREAD_Z
    k = 0
    while t0 + 1.0 + k * pitch < t1 - 1.0:                                       # internal thread, in the sleeve's grooves
        z = t0 + 1.0 + k * pitch
        c = c + ring(P.SLEEVE_R - 0.6, P.SLEEVE_R + 0.1, z + pitch * 0.06, z + pitch * 0.39)
        k += 1
    return _l(c, spec)


def steel_washer(spec) -> Part:
    return _l(ring(P.SPLINE[1] / 2 + 0.2, 17.8, *P.STEEL_WASHER_Z), spec)


def cork_washer(spec) -> Part:
    return _l(ring(P.SPLINE[1] / 2 + 0.05, 17.8, *P.CORK_WASHER_Z), spec)


# =================================================================================================
# shaft assembly (item 1): splined stub, cone, tube, welded rear yoke; balance weights
# =================================================================================================
def shaft(spec) -> Part:
    L = P.STUB_FRONT_TO_JOINT
    n, dmaj, dmin = P.SPLINE
    st = P.STUB_SPLINE_LEN
    rt = P.TUBE_D / 2
    t0 = P.STUB_LEN + P.CONE_LEN
    t1 = t0 + P.TUBE_LEN
    ri = rt - P.TUBE_WALL
    prof = [(0, 0.8), (dmin / 2 - 0.4, 0.0), (dmin / 2, 0.8), (dmin / 2, st), (15.0, st + 1.0), (15.0, P.STUB_LEN),
            (rt, t0 - 1.0), (rt + 0.8, t0 - 1.0), (rt + 0.8, t0 + 5.0), (rt, t0 + 6.0), (rt, t1 - 6.0), (rt + 0.8, t1 - 5.0),
            (rt + 0.8, t1), (rt - 1.0, t1 + 4.0), (21.5, L - 24.0), (19.5, L - 20.0), (0, L - 20.0)]
    s = Sh.revolved(prof)
    s = s - Sh.revolved([(0, t0 + 6.0), (ri, t0 + 8.0), (ri, t1 - 6.0), (0, t1 - 8.0)])        # the tube is hollow
    sp = GR.spline_shaft(n, dmaj, dmin, st - 3.0).moved(Location((0, 0, 1.5)))
    s = s + sp
    s = s + _ears("y", L, L - 22.0, 20.0)
    s = s + box(-14.0, 14.0, -P.EAR_IN - 0.5, P.EAR_IN + 0.5, L - 27.0, L - 20.5)
    # alignment arrow on the plain neck, on the left as the sleeve's
    s = s - Location((0, 15.0 - 0.4, P.STUB_LEN - 6.0)) * Rot(-90, 0, 0) * extrude(
        Face(Wire.make_polygon([(-2.0, 3.0, 0), (2.0, 3.0, 0), (0, -3.0, 0)], close=True)), 1.0)
    return _l(s, spec)


def balance_weight(spec) -> Part:
    """Small curved steel weight spot welded to the tube where the shaft was balanced (Sec 3 para 2)."""
    rt = P.TUBE_D / 2
    t, L = spec.nom("thickness"), spec.nom("length")
    span = 34.0
    w = Sh.revolved([(rt + 0.02, 0), (rt + t, 0), (rt + t, L), (rt + 0.02, L)])
    keep = Rot(0, 0, -span / 2) * box(0, rt + t + 2, 0, 40.0, -1, L + 1)
    keep = keep & (Rot(0, 0, span / 2) * box(0, rt + t + 2, -40.0, 0, -1, L + 1))
    w = w & keep
    for z in (L * 0.3, L * 0.7):                                                 # weld spots
        w = w + Location((rt + t - 0.2, 0, z)) * Sphere(1.6)
    return _l(w, spec)


# =================================================================================================
# flange fixings (items 14-16)
# =================================================================================================
def flange_bolt(spec) -> Part:
    return _l(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def flange_nut(spec) -> Part:
    """Item 15: 5/16 UNF self-locking (nyloc) nut: hex body and the domed collar holding the nylon
    insert, seat face at z = 0."""
    from build123d import RegularPolygon
    af = 0.5 * IN
    h = spec.nom("height")
    n = extrude(RegularPolygon(af / math.sqrt(3), 6), h - 2.2)
    n = n - Sh.revolved([(af / 2 + 0.2, -0.01), (af / math.sqrt(3) + 1, -0.01), (af / math.sqrt(3) + 1, 1.2)])
    n = n + Sh.revolved([(0, h - 2.21), (af / 2 - 0.2, h - 2.21), (af / 2 - 0.9, h - 0.4), (af / 2 - 1.5, h), (0, h)])
    n = n - zc(7.94 / 2 * 0.92, -1, h + 1)
    return _l(n, spec)


WASHER = C.WASHER


def _tube_d(p):
    """Diameter of the longest cylindrical face (the tube)."""
    return max(probes.cylinder_diameters(p), key=lambda t: t[1])[0]


PARTS = {
    "propshaft.shaft.flange-yoke": {"build": flange_yoke, "probes": {"diameter": lambda p: probes.bbox_size(p, "y")}},
    "propshaft.shaft.spider": {"build": spider},
    "propshaft.shaft.needle-bearing": {"build": needle_bearing,
                                       "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "propshaft.shaft.circlip": {"build": circlip, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "propshaft.shaft.gasket": {"build": gasket, "probes": {"thickness": lambda p: probes.bbox_size(p, "z")}},
    "propshaft.shaft.gasket-retainer": {"build": gasket_retainer},
    "propshaft.shaft.lubricator": {"build": lubricator},
    "propshaft.shaft.sleeve-yoke": {"build": sleeve_yoke},
    "propshaft.shaft.sleeve-lubricator": {"build": sleeve_lubricator},
    "propshaft.shaft.dust-cap": {"build": dust_cap, "probes": {"outside_diameter": lambda p: probes.bbox_size(p, "x")}},
    "propshaft.shaft.steel-washer": {"build": steel_washer},
    "propshaft.shaft.cork-washer": {"build": cork_washer},
    "propshaft.shaft.shaft": {"build": shaft, "probes": {"tube_diameter": lambda p: _tube_d(p),
                                                         "stub_to_joint": lambda p: p.bounding_box().max.Z - P.EYE_R}},
    "propshaft.shaft.balance-weight": {"build": balance_weight},
    "propshaft.shaft.flange-bolt": {"build": flange_bolt, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "propshaft.shaft.flange-nut": {"build": flange_nut, "probes": {"height": lambda p: probes.bbox_size(p, "z")}},
    "propshaft.shaft.flange-washer": {"build": C.spring_washer, "probes": WASHER},
}
