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


def _nipple_dimples():
    """The raised dimples the rim is pressed into round each spoke nipple's seat (Oliver's kf184): a domed boss on the
    well's floor at every spoke's hole, standing in toward the hub (kept as separate solids)."""
    from build123d import Sphere, scale
    out = []
    for k in range(W.SPOKES):
        a = 360.0 * k / W.SPOKES
        ry = W.RIM_ROWS[0] if k % 2 == 1 else W.RIM_ROWS[1]
        d = scale(Sphere(6.5), by=(1.0, 1.0, 0.55))
        out.append(Rot(0, a, 0) * Location((0.0, ry, W.WELL_R - W.RIM_T * 0.5)) * d)
    return out


def _shell():
    y0, y1 = W.SHELL_Y
    s0, s1 = W.SPLINE_Y
    rc0, rc1 = W.INNER_CONE_R
    fy0, fr0 = W.INNER_FLANGE
    fy1, fr1 = W.OUTER_FLANGE
    prof = [(36.6, y0 + 4.5), (41.0, y0 + 4.5), (41.0, fy0 - 10.0), (fr0, fy0 - 4.0), (fr0, fy0 + 4.0), (47.0, fy0 + 12.0), (45.0, fy1 - 8.0), (fr1, fy1 - 4.0),
            (fr1, fy1 + 4.0), (fr1 - 1.5, y1 - 14.0), (fr1 - 6.0, y1 - 4.0), (36.0, y1), (25.0, y1), (23.0, y1 - 3.0),
            (W.SPLINE[1] / 2 + 0.25, s1 - 4.0), (W.SPLINE[1] / 2 + 0.25, s0), (rc1 + 0.3, s0 - 0.5), (rc0 + 0.3, 7.5),
            (36.6, 7.5)]
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
    parts = [_rim(), _shell()] + _spokes() + _nipple_dimples()
    c = Compound(children=parts)
    c.label = spec.id
    return c


# =================================================================================================
# tyre, valve
# =================================================================================================
def _tyre_section():
    """(r, y) outline of the radial's carcass under the tread, inboard bead round the crown to the outboard bead
    (unladen): the flat radial sidewall bulging to the section width a little below mid height, tight shoulders."""
    R = W.TYRE_R - W.TREAD_DEPTH
    h = W.RIM_W / 2
    b = W.BEAD_R
    sw = W.SECTION_W / 2
    tw = W.TREAD_W / 2
    r0 = b + W.FLANGE_H + 3.0
    rs = R - 20.0                                     # the shoulder's start
    pts = [(b - 0.5, C - h + 1.0), (r0, C - h - 1.0)]
    for k in range(1, 14):
        t = k / 14
        r = r0 + (rs - r0) * t
        bulge = math.sin(math.pi * t ** 0.8) ** 0.6
        pts.append((r, C - (h + 1.0 + (sw - h - 1.0) * bulge - 4.0 * t * t)))
    ye = pts[-1][1]
    for k in range(1, 9):                             # the shoulder's arc up to the crown
        a = math.radians(90.0 * k / 8)
        pts.append((rs + 20.0 * math.sin(a), ye + (C - tw + 6.0 - ye) * (1 - math.cos(a))))
    left = list(pts)
    right = [(r, 2 * C - y) for r, y in reversed(left)]
    return left + right


def _side_y(r):
    """Outboard sidewall surface (local y) at radius r."""
    sec = _tyre_section()
    n = len(sec) // 2
    side = sorted([(rr, yy) for rr, yy in sec[n:] if yy > C], key=lambda p: p[0])
    import numpy as np
    rs, ys = zip(*side)
    return float(np.interp(r, rs, ys))


TREAD_RIBS = [(-64.0, -40.0), (-32.0, -16.0), (-8.0, 8.0), (16.0, 32.0), (40.0, 64.0)]   # across the tread (v), 4 grooves


def _sidewall_text():
    """Moulded lettering on the outboard sidewall, as on Oliver's tyres (kf182-185, kf229): FALKEN, SINCERA SN832
    ECORUN and the size; letter tops outward, reading clockwise seen from outside."""
    from build123d import Align, Text
    out = []
    runs = [("FALKEN", 15.0, 0.0, 262.0), ("SINCERA SN832", 16.0, 150.0, 262.0), ("ECORUN", 8.0, 112.0, 268.0),
            ("165/80R14 85T", 8.5, -120.0, 266.0)]
    for word, fs, ac, rt in runs:
        adv = [0.38 * fs if ch == " " else 0.66 * fs for ch in word]
        L = sum(adv)
        s0 = -L / 2
        for ch, w in zip(word, adv):
            sc = s0 + w / 2
            s0 += w
            if ch == " ":
                continue
            a = math.radians(ac - math.degrees(sc / rt))
            x, z = rt * math.sin(a), rt * math.cos(a)
            right = (-math.cos(a), 0.0, math.sin(a))
            y = _side_y(rt)
            t = extrude(Text(ch, font_size=fs, align=(Align.CENTER, Align.CENTER)), 2.8, dir=(0, 0, 1))
            loc = Plane(origin=(x, y - 2.0, z), x_dir=right, z_dir=(0.0, 1.0, 0.0)).location
            out.append(loc * t)
    return out


def tyre(spec) -> Part:
    """165/80R14 85T radial as on Oliver's car (Falken Sincera SN832 Ecorun, kf182-185, kf229): the carcass, the rim
    guard rib, four straight circumferential grooves between three continuous ribs and two blocked shoulders, the
    moulded lettering on the outboard sidewall."""
    sec = _tyre_section()
    from build123d import Axis, Face, Wire, offset, revolve
    from mgb.poly2d import ccw
    face = Face(Wire.make_polygon([(r, 0.0, y) for r, y in ccw(sec)], close=True))
    inner = offset(face, -9.0)
    body = Rot(-90, 0, 0) * (revolve(face, Axis.Z) - revolve(inner, Axis.Z))
    solids = [body]
    for s_ in (1, -1):                                 # rim guard rib on each sidewall
        rr = W.BEAD_R + W.FLANGE_H + 8.0
        y = C + s_ * (W.RIM_W / 2 + 6.0)
        solids.append(yrev([(rr, y - 1.8), (rr + 4.0, y - 1.8), (rr + 4.0, y + 1.8), (rr, y + 1.8)]))
    R0 = W.TYRE_R - W.TREAD_DEPTH - 0.5
    R1 = W.TYRE_R
    for v0, v1 in TREAD_RIBS[1:-1]:                    # the three continuous ribs
        crown = lambda v: 2.5 * (v / (W.TREAD_W / 2)) ** 2
        solids.append(yrev([(R0, C + v0), (R1 - crown(v0) - 0.8, C + v0), (R1 - crown((v0 + v1) / 2), C + (v0 + v1) / 2),
                            (R1 - crown(v1) - 0.8, C + v1), (R0, C + v1)]))
    n = W.TREAD_PITCHES
    pitch = 2 * math.pi * (R1 - 3.0) / n
    for k in range(n):                                  # the shoulder blocks, wrapping round the shoulder
        a = 360.0 * k / n
        for v0, v1 in (TREAD_RIBS[0], TREAD_RIBS[-1]):
            vo = v0 - 8.0 if v0 < 0 else v0
            vi = v1 if v0 < 0 else v1 + 8.0
            poly = [(-pitch / 2 + 2.0, vo), (pitch / 2 - 2.0, vo), (pitch / 2 - 2.0, vi), (-pitch / 2 + 2.0, vi)]
            blk = zprism(poly, R0, R1 - 3.2)
            blk = blk - box(-0.5, 0.5, vo - 1, vi + 1, R1 - 6.0, R1)               # sipe across the block
            solids.append(Rot(0, a, 0) * Location((0, C, 0)) * blk)
    solids += _sidewall_text()
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
DOME_H = 17.0                                     # the spinner's domed face above the boss's shoulder (kf184, kf229)


def _dome_y(rho):
    """Local y of the spinner's dome surface at radius rho."""
    y0, y1 = W.SPINNER_Y
    r = W.SPINNER_BOSS_R
    Rs = (r * r + DOME_H * DOME_H) / (2 * DOME_H)
    return y1 - 12.0 + (math.sqrt(max(Rs * Rs - rho * rho, 0.0)) - (Rs - DOME_H))


def _dome_letters(words, rho=25.0, fs=4.2):
    """Letters round the dome's edge: [(text, centre angle)], tops outward, reading clockwise seen from outside, each
    letter laid on the dome's surface."""
    from build123d import Align, Text
    y0, y1 = W.SPINNER_Y
    r = W.SPINNER_BOSS_R
    Rs = (r * r + DOME_H * DOME_H) / (2 * DOME_H)
    out = []
    for word, ac in words:
        adv = [0.4 * fs if ch == " " else 0.72 * fs for ch in word]
        L = sum(adv)
        s0 = -L / 2
        for ch, w in zip(word, adv):
            sc = s0 + w / 2
            s0 += w
            if ch == " ":
                continue
            a = math.radians(ac - math.degrees(sc / rho))
            x, z = rho * math.sin(a), rho * math.cos(a)
            right = (-math.cos(a), 0.0, math.sin(a))
            # dome normal at rho: radial outward tilted from +y
            tilt = math.asin(min(rho / Rs, 0.99))
            n = (math.sin(tilt) * math.sin(a), math.cos(tilt), math.sin(tilt) * math.cos(a))
            t = extrude(Text(ch, font_size=fs, align=(Align.CENTER, Align.CENTER)), 1.4, dir=(0, 0, 1))
            yd = _dome_y(rho)
            loc = Plane(origin=(x - n[0] * 0.9, yd - n[1] * 0.9, z - n[2] * 0.9), x_dir=right, z_dir=n).location
            out.append(loc * t)
    return out


def spinner(hand, side_word):
    def b(spec) -> Part:
        """Two-eared knock-on spinner (Oliver's kf182-185, kf229): the boss with the 12 tpi thread inside and the cone
        face on the wheel, a smooth domed face, two flat tapered ears swept back toward the wheel - deep at the boss,
        narrowing to a rounded tip - and round the dome's edge UNDO with the undoing arrow and the side lettered."""
        y0, y1 = W.SPINNER_Y
        r = W.SPINNER_BOSS_R
        n = 12
        dome = [(r * (1 - k / n) ** 0.9 if k < n else 0.0, _dome_y(r * (1 - k / n) ** 0.9 if k < n else 0.0)) for k in range(n + 1)]
        boss = yrev([(28.0, y0), (r, y0 + 3.0), (r, y1 - 12.0)] + dome[1:] + [(0.0, y1 - 16.0), (20.5, y1 - 16.0),
                                                                            (20.5, y0 + 6.0), (24.0, y0)])
        t0 = A.EXT_THREAD_Y[0] - A.EXT_COLLAR_Y[0]
        th = handed_thread(A.EXT_THREAD_D + 0.3, A.EXT_TPI, A.EXT_THREAD_Y[1] - A.EXT_THREAD_Y[0], hand)
        boss = boss - Location((0, t0, 0)) * Rot(-90, 0, 0) * th
        boss = boss - ycyl(A.EXT_THREAD_D / 2 - 1.7, t0 - 1.0, y1 - 16.9)
        span = W.SPINNER_SPAN / 2
        sweep_back = 16.0                                     # the tips' outer faces this much nearer the wheel
        k = sweep_back / (span - r)
        phi = math.degrees(math.atan(k))
        for s_ in (1, -1):
            prof = hull(circle_pts(s_ * (r - 6.0), 0.0, 20.0, 24) + circle_pts(s_ * (span - 8.0), 0.0, 7.5, 16))
            ear = yprism([(x, z) for x, z in prof], y0 + 6.0, y1 - 10.0)
            cut = Location((s_ * (r - 2.0), 0.0, 0.0)) * Rot(0, 0, -s_ * phi) * box(0.0 if s_ > 0 else -300.0, 300.0 if s_ > 0 else 0.0,
                                                                                    y1 - 10.0, y1 + 100.0, -60.0, 60.0)
            ear = ear - cut
            back = Location((s_ * (r - 2.0), 0.0, 0.0)) * Rot(0, 0, s_ * phi * 0.4) * box(0.0 if s_ > 0 else -300.0, 300.0 if s_ > 0 else 0.0,
                                                                                         y0 - 100.0, y0 + 6.0, -60.0, 60.0)
            ear = ear - back
            boss = boss + ear
        sgn = 1 if hand == "right" else -1
        letters = _dome_letters([("UNDO", 30.0 * sgn), ("UNDO", -30.0 * sgn), (side_word + " SIDE", 180.0)])
        # the arrow at the top between the two UNDOs, the way the spinner undoes
        from build123d import Polygon
        arrow = extrude(Polygon((0, 0), (sgn * 4.5, 2.6), (sgn * 4.5, 0.9), (sgn * 11.0, 0.9), (sgn * 11.0, -0.9), (sgn * 4.5, -0.9),
                                (sgn * 4.5, -2.6), align=None), 1.4, dir=(0, 0, 1))
        tilt = math.asin(min(25.0 / ((r * r + DOME_H * DOME_H) / (2 * DOME_H)), 0.99))
        arrow = Plane(origin=(0.0, _dome_y(25.0) - 0.9, 25.0), x_dir=(-1.0, 0.0, 0.0),
                      z_dir=(0.0, math.cos(tilt), math.sin(tilt))).location * arrow.moved(Location((-sgn * 5.5, 0, 0)))
        from build123d import Compound
        c = Compound(children=[boss, arrow] + letters)
        c.label = spec.id
        return c
    return b


PARTS = {
    "wheels.road-wheels.wheel": {"build": wire_wheel},
    "wheels.road-wheels.tyre": {"build": tyre, "probes": {"overall_diameter": lambda p: p.bounding_box().size.Z,
                                                          "section_width": lambda p: _extent(p, "Y")}},
    "wheels.road-wheels.valve": {"build": valve},
    "wheels.road-wheels.spinner-lh": {"build": spinner("right", "LEFT")},
    "wheels.road-wheels.spinner-rh": {"build": spinner("left", "RIGHT")},
}


def _extent(p, ax):
    vals = [getattr(v, ax) for v in p.vertices()]
    return max(vals) - min(vals)
