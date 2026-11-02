"""Road wheels: 4 1/2J x 14 60-spoke centre-lock wire wheel, 5.60-14 crossply tyre with its tube valve, and the
two-eared knock-on spinners, handed (Haynes Ch 11 specifications, printed p203; Sec 30; MGOC Spares wire wheels
and spinners).

Drawn in the wheel frame of mgb.wheel_layout (origin on the axis at the hub's inner cone, +y outboard); the
assembly places one wheel, tyre and spinner on each hub. The spoke and tread solids are kept as separate solids
in one compound (no boolean fusing) so the meshes stay light.

Forms: the rim - a 4 1/2J well-base rim (flanges, bead seats, the drop centre carrying the 60 spoke nipples, the
valve hole); the hub shell - the inner cone that seats on the hub, the 42 mm series splines inside, the two spoke
flanges and the outer cone the spinner bears on; the 60 spokes laced tangentially, inner flange to the rim's outer
row and outer flange to the inner row, alternately leading and trailing; the tyre - bead, sidewall with its rim
guard rib and the moulded lettering band, rounded shoulders, and a tread of five zig-zag ribs with sipes; the
spinner - a boss with the 12 tpi thread inside, the cone face on the wheel, two ears for the copper mallet,
"UNDO" with an arrow and the side ("LEFT" / "RIGHT") lettered on the face.
"""
from __future__ import annotations

import math

from build123d import Compound, Location, Part, Plane, Rot, Text, Vector, extrude

from mgb import gears as GR, probes, rear_axle_layout as A, wheel_layout as W
from mgb.chassis_geom import IN, box, lab, rod, ycyl, yprism, yrev, zcyl, zprism, zrev
from mgb.poly2d import circle_pts, hull
from parts.axle.casing import handed_thread

C = W.CENTRE_PLANE


def _pol(r, a_deg, y):
    """Point at radius r, angle a from the top toward the front, local y."""
    a = math.radians(a_deg)
    return (r * math.sin(a), y, r * math.cos(a))


# =================================================================================================
# wheel: rim, hub shell, spokes, nipples
# =================================================================================================
def _rim():
    h = W.RIM_W / 2
    b = W.BEAD_R
    t = W.RIM_T
    ft = b + W.FLANGE_H
    # outer surface of the section, from the inboard flange edge across to the outboard one
    outer = [(ft, C - h - 3.0), (ft + 2.0, C - h - 6.5), (b + 6.0, C - h - 8.0), (b, C - h - 2.5), (b, C - h + 2.0),
             (b + 1.2, C - h + 16.0), (b + 1.2, C - W.WELL_W / 2 - 6.0), (W.WELL_R, C - W.WELL_W / 2 + 4.0),
             (W.WELL_R, C + W.WELL_W / 2 - 4.0), (b + 1.2, C + W.WELL_W / 2 + 6.0), (b + 1.2, C + h - 16.0),
             (b, C + h - 2.0), (b, C + h + 2.5), (b + 6.0, C + h + 8.0), (ft + 2.0, C + h + 6.5), (ft, C + h + 3.0)]
    # the sheet: the contour above, thickened both sides by half the rim's gauge
    from build123d import Axis, Face, Side, Wire, revolve
    cont = Wire.make_polygon([(r - t / 2, 0.0, y) for r, y in outer], close=False)
    face = Face(cont.offset_2d(t / 2, side=Side.BOTH, closed=False))
    rim = Rot(-90, 0, 0) * revolve(face, Axis.Z)
    # valve hole
    vx, _, vz = _pol(W.WELL_R, W.VALVE_ANGLE, 0)
    rim = rim - Location((vx, C, vz)) * Rot(0, W.VALVE_ANGLE, 0) * zcyl(4.2, -10, 10)
    return rim


def _shell():
    y0, y1 = W.SHELL_Y
    s0, s1 = W.SPLINE_Y
    rc0, rc1 = W.INNER_CONE_R
    fy0, fr0 = W.INNER_FLANGE
    fy1, fr1 = W.OUTER_FLANGE
    prof = [(36.6, y0 + 1.0), (41.0, y0 + 1.0), (41.0, fy0 - 10.0), (fr0, fy0 - 4.0), (fr0, fy0 + 4.0), (40.0, fy0 + 10.0), (35.0, fy1 - 14.0), (fr1, fy1 - 4.0),
            (fr1, fy1 + 4.0), (31.0, fy1 + 10.0), (31.0, y1 - 3.0), (28.5, y1), (25.0, y1), (23.0, y1 - 3.0),
            (W.SPLINE[1] / 2 + 0.25, s1 - 4.0), (W.SPLINE[1] / 2 + 0.25, s0), (rc1 + 0.3, s0 - 0.5), (rc0 + 0.3, 5.0),
            (36.6, 5.0)]
    sh = yrev(prof)
    # internal splines: teeth standing in from the bore to the hub's minor diameter
    n, dmaj, dmin = W.SPLINE
    sh = sh + Location((0, s0, 0)) * Rot(-90, 0, 0) * _internal_teeth(n, dmaj, dmin, s1 - s0 - 4.0)
    # spoke holes in the flanges
    for k in range(W.SPOKES):
        a = 360.0 * k / W.SPOKES
        fy, fr = (W.INNER_FLANGE if k % 2 else W.OUTER_FLANGE)
        x, _, z = _pol(fr - 4.0, a + _lace(k), 0)
        sh = sh - Location((x, fy, z)) * Rot(-90, 0, 0) * zcyl(1.9, -7.0, 7.0)
    return sh


def _internal_teeth(n, dmaj, dmin, length):
    """Spline teeth inside the shell (local z), standing in from the major to the minor diameter."""
    ring = zcyl(dmaj / 2 + 0.3, 0, length) - GR.spline_shaft(n, dmaj + 0.2, dmin + 0.3, length + 2.0).moved(Location((0, 0, -1.0)))
    return ring


def _lace(k):
    """Tangential offset of spoke k's hub end from its rim hole: alternately leading and trailing."""
    return W.LACE_ANGLE if (k // 2) % 2 else -W.LACE_ANGLE


def _spokes():
    out = []
    for k in range(W.SPOKES):
        a = 360.0 * k / W.SPOKES
        inner = k % 2 == 1                                        # inner flange spoke -> rim outer row
        fy, fr = (W.INNER_FLANGE if inner else W.OUTER_FLANGE)
        ry = W.RIM_ROWS[0] if inner else W.RIM_ROWS[1]
        p0 = _pol(fr - 4.0, a + _lace(k), fy)
        p1 = _pol(W.NIPPLE_R - 10.0, a, ry)
        v = Vector(*p1) - Vector(*p0)
        sp = rod(p0, p1, W.SPOKE_D / 2)
        head = Location(p0) * __import__("build123d").Sphere(W.SPOKE_D * 0.85)
        nip_a = Vector(*p1) - v.normalized() * 2.0
        nip_b = Vector(*p1) + v.normalized() * 12.5
        nip = rod(tuple(nip_a), tuple(nip_b), 2.3)
        out += [sp, head, nip]
    return out


def wire_wheel(spec) -> Part:
    parts = [_rim(), _shell()] + _spokes()
    c = Compound(children=parts)
    c.label = spec.id
    return c


# =================================================================================================
# tyre, valve
# =================================================================================================
def _tyre_section():
    """(r, y) outline of the tyre's carcass, inboard bead round the crown to the outboard bead (unladen)."""
    R = W.TYRE_R - W.TREAD_DEPTH
    h = W.RIM_W / 2
    b = W.BEAD_R
    sw = W.SECTION_W / 2
    tw = W.TREAD_W / 2
    pts = []
    # bead (inboard), against the rim flange
    pts += [(b - 0.5, C - h + 1.0), (b + W.FLANGE_H + 3.0, C - h - 1.0)]
    # sidewall: bulging out to the section width at mid height
    mid = (b + W.FLANGE_H + R) / 2 - 8.0
    for k in range(1, 12):
        t = k / 12
        r = b + W.FLANGE_H + 3.0 + (R - 18.0 - (b + W.FLANGE_H + 3.0)) * t
        yy = C - (h + 1.0 + (sw - h - 1.0) * math.sin(math.pi * t) ** 0.8)
        pts.append((r, yy))
    # shoulder and crown
    for k in range(0, 9):
        a = math.radians(90.0 * k / 8)
        pts.append((R - 18.0 + 18.0 * math.sin(a), C - tw - 6.0 + 6.0 * (1 - math.cos(a)) + (sw - tw - 6.0) * 0 - 0.0))
    pts = pts[:-1]
    left = list(pts)
    right = [(r, 2 * C - y) for r, y in reversed(left)]
    inner = []
    return left + [(R, C - tw), (R, C + tw)] + right


def tyre(spec) -> Part:
    sec = _tyre_section()
    # the carcass: the section outline, hollowed 9 mm inside it (a closed casing; the beads sit in the rim)
    from build123d import Axis, Face, Wire, offset, revolve
    from mgb.poly2d import ccw
    face = Face(Wire.make_polygon([(r, 0.0, y) for r, y in ccw(sec)], close=True))
    inner = offset(face, -9.0)
    body = Rot(-90, 0, 0) * (revolve(face, Axis.Z) - revolve(inner, Axis.Z))
    solids = [body]
    # rim guard rib and lettering band on each sidewall
    for s in (1, -1):
        rr = W.BEAD_R + W.FLANGE_H + 10.0
        y = C + s * (W.RIM_W / 2 + 6.5)
        solids.append(yrev([(rr, y - 1.6), (rr + 4.0, y - 1.6), (rr + 4.0, y + 1.6), (rr, y + 1.6)]))
    # tread: five zig-zag ribs of blocks with grooves between and sipes across
    R0 = W.TYRE_R - W.TREAD_DEPTH - 0.5
    R1 = W.TYRE_R
    n = W.TREAD_PITCHES
    pitch = 2 * math.pi * (R1 - 3.0) / n
    tw = W.TREAD_W
    ribs = W.TREAD_RIBS
    groove = 4.5
    rib_w = (tw - groove * (ribs - 1)) / ribs
    for k in range(n):
        a = 360.0 * k / n
        zig = 3.0 if k % 2 else -3.0
        for j in range(ribs):
            v0 = -tw / 2 + j * (rib_w + groove)
            v1 = v0 + rib_w
            # each block a parallelogram: its fore and aft edges slant one way, the next pitch the other (zig-zag)
            u0, u1 = -pitch / 2 + 0.6, pitch / 2 - 0.6
            sl = zig if j % 2 == 0 else -zig
            poly = [(u0 - sl, v0), (u1 - sl, v0), (u1 + sl, v1), (u0 + sl, v1)]
            if j in (0, ribs - 1):                                   # shoulder blocks run round the shoulder
                ext = 7.0 if j == 0 else -7.0
                poly = [(u0 - sl, v0 - (7.0 if j == 0 else 0.0)), (u1 - sl, v0 - (7.0 if j == 0 else 0.0)),
                        (u1 + sl, v1 + (7.0 if j == ribs - 1 else 0.0)), (u0 + sl, v1 + (7.0 if j == ribs - 1 else 0.0))]
            blk = zprism([(x, y) for x, y in poly], R0, R1 - (1.2 if j in (0, ribs - 1) else 0.0))
            blk = blk - box(-0.6, 0.6, (v0 + v1) / 2 - rib_w * 0.3, (v0 + v1) / 2 + rib_w * 0.3, R1 - 3.5, R1 + 1)   # sipe
            # local frame: x along the circumference, y across (car y), z radial; then turned to angle a about y
            blk = Rot(0, a, 0) * Location((0, C, 0)) * blk
            solids.append(blk)
    c = Compound(children=solids)
    c.label = spec.id
    return c


def valve(spec) -> Part:
    """Tube valve stem through the rim's valve hole, with its cap (drawn in the wheel frame)."""
    L_ = spec.nom("length")
    v = zrev([(0, 0), (4.0, 0), (4.0, L_ - 8.0), (3.0, L_ - 8.0), (3.0, L_), (0, L_)])
    v = v + zrev([(0, -3.0), (9.0, -3.0), (9.0, 0.01), (0, 0.01)])
    vx, _, vz = _pol(W.WELL_R + 0.5, W.VALVE_ANGLE, 0)
    v = Location((vx, C, vz)) * Rot(0, W.VALVE_ANGLE + 180.0, 0) * v
    return lab(v, spec)


# =================================================================================================
# spinner (two-eared knock-on), handed
# =================================================================================================
def spinner(hand, side_word):
    def b(spec) -> Part:
        y0, y1 = W.SPINNER_Y
        r = W.SPINNER_BOSS_R
        boss = yrev([(28.0, y0), (r, y0 + 3.0), (r, y1 - 8.0), (r - 6.0, y1), (0.0, y1), (0.0, y1 - 4.0), (20.5, y1 - 4.0),
                     (20.5, y0 + 6.0), (24.0, y0)])
        # internal thread, cut with the hub's own thread form (major + 0.3, as the rear bearing nuts)
        t0 = A.EXT_THREAD_Y[0] - A.EXT_COLLAR_Y[0]
        th = handed_thread(A.EXT_THREAD_D + 0.3, A.EXT_TPI, A.EXT_THREAD_Y[1] - A.EXT_THREAD_Y[0], hand)
        boss = boss - Location((0, t0, 0)) * Rot(-90, 0, 0) * th
        boss = boss - ycyl(A.EXT_THREAD_D / 2 - 1.7, t0 - 1.0, y1 - 3.9)
        # two ears, swept back toward the wheel and thickened at the tips for the mallet
        span = W.SPINNER_SPAN / 2
        for s in (1, -1):
            prof = hull(circle_pts(s * (r - 4.0), 0.0, 12.0, 16) + circle_pts(s * (span - 9.0), 0.0, 9.0, 16))
            ear = yprism([(x, z) for x, z in prof], y0 + 6.0, y1 - 10.0)
            ear = ear + yprism([(x, z) for x, z in hull(circle_pts(s * (span - 9.0), 0.0, 9.5, 16))], y0 + 4.0, y1 - 8.0)
            boss = boss + ear
        # lettering on the face: UNDO with an arrow, and the side
        face_y = y1
        txt = Text("UNDO", font_size=7.0)
        word = Text(side_word, font_size=5.0)
        letters = extrude(txt, 0.8).moved(Location((0, 7.0, 0))) + extrude(word, 0.8).moved(Location((0, -8.0, 0)))
        # arrow: direction of undoing (anticlockwise seen from outside for a right-hand thread)
        sgn = 1 if hand == "right" else -1
        arrow = extrude(__import__("build123d").Polygon((0, 0), (sgn * 6.0, 3.0), (sgn * 6.0, 1.0), (sgn * 14.0, 1.0),
                                                        (sgn * 14.0, -1.0), (sgn * 6.0, -1.0), (sgn * 6.0, -3.0), align=None), 0.8)
        letters = letters + arrow.moved(Location((-sgn * 7.0, 0.0, 0)))
        boss = boss + Location((0, face_y - 0.2, 0)) * Rot(-90, 0, 0) * Rot(0, 0, 0) * letters.moved(Location((0, 0, 0)))
        return lab(boss, spec)
    return b


PARTS = {
    "wheels.road-wheels.wheel": {"build": wire_wheel},
    "wheels.road-wheels.tyre": {"build": tyre, "probes": {"overall_diameter": lambda p: _extent(p, "Z"),
                                                          "section_width": lambda p: _extent(p, "Y")}},
    "wheels.road-wheels.valve": {"build": valve},
    "wheels.road-wheels.spinner-lh": {"build": spinner("right", "LEFT")},
    "wheels.road-wheels.spinner-rh": {"build": spinner("left", "RIGHT")},
}


def _extent(p, ax):
    vals = [getattr(v, ax) for v in p.vertices()]
    return max(vals) - min(vals)
