"""Banjo axle case and its fittings, three-quarter floating axle, 1963 MGB (Haynes Ch 8 Fig 8.1 items 1, 4,
5, 9, 10, 11; Sec 2-3, printed p142-143; Ch 11 Fig 11.4 for the spring and strap fixings, p207).

Drawn in the axle frame of mgb.rear_axle_layout (origin on the axle centre, car axes).

Forms (Fig 8.1 item 1): two steel pressings welded along the horizontal centre line (the seam
bead runs round the bowl and along the tubes, the serrated line in the figure); the round bowl
open at the front, a reinforcing ring welded round the opening carrying the ten gear carrier
studs; pressed necks flattening into round tubes; forged ends welded in, each with the brake
backplate flange (four lobes), the seal track, the hub bearing journal and the bearing nut
thread with a keyway for the locking washer's tab; spring seats welded under the tubes; a
bracket hanging from each tube with the rebound strap spindle (item 5 its nut; Ch 8 Sec 3 para
4); bosses for the breather on top (Sec 2 para 3), the filler/level plug on the rear face (Sec 2
para 1) and the drain plug underneath; a tab for the brake pipe three-way union and a pin for
the handbrake balance lever (Sec 3 paras 4-5).
"""
from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Face, Location, Part, Plane, Rot, Solid, Sphere, Wire, extrude

from mgb import fasteners as F, probes, rear_axle_layout as A, shapes as Sh
from mgb.poly2d import circle_pts, hull
from parts.gearbox import casing as C
from parts.propshaft.shaft import ring, xcyl, xprism, ycyl, yprism

IN = 25.4
zc, box = C.zc, C.box


def _l(p, spec):
    p.label = spec.id
    return p


def xrev(profile):
    """Revolve an (r, x) profile about the x axis."""
    return Rot(0, 90, 0) * Sh.revolved([(r, x) for r, x in profile])


def yrev(profile):
    """Revolve an (r, y) profile about the y axis."""
    return Rot(-90, 0, 0) * Sh.revolved(profile)


def handed_thread(major, tpi, length, hand):
    """External thread along +z from 0 (core at the minor diameter), right or left hand."""
    t = F._thread(major, IN / tpi, length)
    if hand == "left":
        t = t.mirror(Plane.XZ)
    return t


def on_side(p, side):
    """A solid drawn for the left (+y) side, moved to `side` by mirroring (no threads on it)."""
    return p if side > 0 else p.mirror(Plane.XZ)


# =================================================================================================
# case (item 1)
# =================================================================================================
def _bowl(off=0.0):
    prof = [(max(r - off, 0.0), x + (off if i == 0 else 0.0)) for i, (r, x) in enumerate(A.BOWL)]
    prof = [(0.0, prof[0][1])] + prof[1:] + [(0.0, A.BOWL[-1][1])]
    return xrev(prof)


def _neck(side, off=0.0):
    y0, y1 = A.NECK_Y
    w0 = Wire.make_ellipse(60.0 - off, 62.0 - off, Plane(origin=(0, side * y0, 0), x_dir=(1, 0, 0), z_dir=(0, side, 0)))
    wm = Wire.make_ellipse(46.0 - off, 47.0 - off, Plane(origin=(0, side * (y0 + 0.45 * (y1 - y0)), 0), x_dir=(1, 0, 0), z_dir=(0, side, 0)))
    w1 = Wire.make_circle(A.TUBE_R - off, Plane(origin=(0, side * y1, 0), x_dir=(1, 0, 0), z_dir=(0, side, 0)))
    return Solid.make_loft([w0, wm, w1])


def _end(side):
    """Forged tube end: taper, backplate flange, seal track, bearing journal, thread (thread added
    separately); drawn on the left and mirrored."""
    f0 = A.BACKPLATE_FACE_Y - A.BACKPLATE_FLANGE_T
    prof = [(A.CASE_BORE_R, A.TUBE_Y[1] - 12.0), (A.TUBE_R - 0.3, A.TUBE_Y[1] - 12.0), (A.TUBE_R - 0.3, A.TUBE_Y[1] + 2.0),
            (31.0, f0), (A.SEAL_TRACK_R, A.BACKPLATE_FACE_Y + 3.0), (A.SEAL_TRACK_R, A.SEAL_TRACK_Y[1]),
            (A.JOURNAL_R, A.SEAL_TRACK_Y[1]), (A.JOURNAL_R, A.HUB_BRG_Y[1] + 0.01), (A.CASE_BORE_R, A.HUB_BRG_Y[1] + 0.01)]
    e = yrev(prof)
    # backplate flange: four lobes round the bolt holes
    pts = circle_pts(0, 0, 52.0, 48)
    for a in A.BACKPLATE_BOLT_ANGLES:
        pts += circle_pts(A.BACKPLATE_BOLT_PCD / 2 * math.sin(math.radians(a)), A.BACKPLATE_BOLT_PCD / 2 * math.cos(math.radians(a)), 12.0, 20)
    fl = yprism(hull(pts), f0, A.BACKPLATE_FACE_Y)
    for a in A.BACKPLATE_BOLT_ANGLES:
        x, z = A.BACKPLATE_BOLT_PCD / 2 * math.sin(math.radians(a)), A.BACKPLATE_BOLT_PCD / 2 * math.cos(math.radians(a))
        fl = fl - ycyl(5.0, f0 - 1, A.BACKPLATE_FACE_Y + 1, x, z)
    e = e + fl - ycyl(A.CASE_BORE_R, A.TUBE_Y[1] - 20, A.CASE_END_Y + 1)
    e = on_side(e, side)
    # thread for the bearing nut, keyway for the locking washer's inner tab (at the top)
    hand = A.HUB_NUT_HAND[side]
    L = A.CASE_END_Y - A.HUB_BRG_Y[1]
    th = handed_thread(A.THREAD_D, A.THREAD_TPI, L, hand)
    th = th - zc(A.CASE_BORE_R, -1, L + 1)
    th = th - box(A.THREAD_D / 2 - 2.2, A.THREAD_D / 2 + 2, -2.4, 2.4, -1, L + 1)          # keyway
    return e + thread_frame(side) * th


def thread_frame(side):
    """Frame of the bearing nut thread on one end of the case: local z outward along the axle from
    the bearing's outer face, the keyway (local +x) at the top. The bearing nut's thread groove is
    cut with the same frame so the two threads are in phase."""
    if side > 0:
        return Location((0, A.HUB_BRG_Y[1], 0)) * Rot(-90, 0, 0) * Rot(0, 0, -90)
    return Location((0, -A.HUB_BRG_Y[1], 0)) * Rot(90, 0, 0) * Rot(0, 0, 90)


def _seat(side):
    """Spring seat welded under the tube: a pressed saddle with a flat underside and a hole for the
    locating plate's peg (Fig 11.4 items 18-19)."""
    y = A.SPRING_Y
    w = A.SPRING_W / 2 + 5.0
    zf = A.SEAT_FACE_Z
    prof = [(A.SEAT_X[0], -14.0), (A.SEAT_X[0], zf + 6.0), (A.SEAT_X[0] + 6.0, zf), (A.SEAT_X[1] - 6.0, zf),
            (A.SEAT_X[1], zf + 6.0), (A.SEAT_X[1], -14.0)]
    s = yprism(prof, y - w, y + w)
    s = s + yprism([(A.SEAT_X[0] - 4.0, -6.0), (A.SEAT_X[0] - 4.0, zf + 10.0), (A.SEAT_X[0], zf + 10.0), (A.SEAT_X[0], -6.0)], y - w, y + w)
    s = s + yprism([(A.SEAT_X[1], -6.0), (A.SEAT_X[1], zf + 10.0), (A.SEAT_X[1] + 4.0, zf + 10.0), (A.SEAT_X[1] + 4.0, -6.0)], y - w, y + w)
    s = s - ycyl(A.TUBE_R - 0.4, y - w - 1, y + w + 1)
    s = s - zc(5.5, zf - 1, zf + 7.0, 0.0, y)
    for x in (-33.0, 33.0):                                                      # fillet welds along the tube
        s = s + ycyl(2.2, y - w, y + w, x, -math.sqrt(A.TUBE_R ** 2 - 33.0 ** 2) - 1.0)
    return on_side(s, side)


def _rebound_bracket(side):
    """Bracket hanging from the tube carrying the rebound strap spindle (Fig 8.1, below the tube)."""
    sx, sy, sz = A.REBOUND_SPINDLE
    y0 = A.REBOUND_Y - 3.0
    prof = hull([(-34.0, -18.0), (26.0, -18.0), (26.0, -40.0)] + circle_pts(sx, sz, 14.0, 24))
    b = yprism(prof, y0, y0 + 6.0)
    b = b + yprism(hull([(26.0, -18.0), (32.0, -18.0), (32.0, -36.0), (sx + 10.0, sz + 10.0), (sx + 4.0, sz + 12.0)]), y0 - 10.0, y0 + 6.0)   # bent front flange
    b = b - ycyl(A.TUBE_R - 0.4, y0 - 12, y0 + 8)
    b = b + ycyl(14.0, y0 - 4.0, sy - 8.0, sx, sz)                               # boss
    b = b + ycyl(8.0, sy - 8.01, sy + 6.0, sx, sz)                               # plain shank the strap eye sits on
    b = b + ycyl(F.THREADS["3/8"][0] * IN / 2, sy + 5.99, A.REBOUND_SPINDLE_END, sx, sz)
    for k in range(9):                                                           # thread
        yy = sy + 9.0 + k * IN / 24
        b = b - Location((sx, yy, sz)) * Rot(-90, 0, 0) * (ring(4.25, 6.0, 0, 0.5))
    return on_side(b, side)


def case(spec) -> Part:
    T = A.SHELL_T
    body = _bowl()
    for s in (1, -1):
        body = body + _neck(s) + ycyl(A.TUBE_R, s * A.TUBE_Y[0] if s > 0 else -A.TUBE_Y[1], A.TUBE_Y[1] if s > 0 else -A.TUBE_Y[0])
    # reinforcing ring round the opening
    ringw = xrev([(A.OPENING_R, A.CASE_FACE_X - 8.0), (A.RING_R, A.CASE_FACE_X - 8.0), (A.RING_R, A.CASE_FACE_X),
                  (A.OPENING_R, A.CASE_FACE_X)])
    body = body + ringw
    # seam bead round the bowl and the necks and along the tubes (horizontal centre line)
    slab = box(-200, 200, -700, 700, -1.4, 1.4)
    bead = (xrev([(r + 1.6, x) for r, x in A.BOWL[1:]] + [(0, A.BOWL[-1][1]), (0, A.BOWL[1][1])]) & slab)
    for s in (1, -1):
        bead = bead + (_neck(s, -1.6) & slab)
        lo, hi = (A.NECK_Y[1], A.TUBE_Y[1] - 14.0)
        bead = bead + (ycyl(A.TUBE_R + 1.6, lo if s > 0 else -hi, hi if s > 0 else -lo) & slab)
    bead = bead - box(A.CASE_FACE_X - 9.0, 300, -300, 300, -5, 5)            # not across the ring
    body = body + bead
    # hollow it
    inner = _bowl(T)
    for s in (1, -1):
        inner = inner + _neck(s, T) + ycyl(A.TUBE_R - T, -A.TUBE_Y[1] + 10.0 if s < 0 else A.NECK_Y[0], A.TUBE_Y[1] - 10.0 if s > 0 else -A.NECK_Y[0])
    body = body - inner
    body = body - xcyl(A.OPENING_R, A.CASE_FACE_X - 40.0, A.CASE_FACE_X + 1.0)
    for a in A.CASE_STUD_ANGLES:
        y, z = A.CASE_STUD_R * math.sin(math.radians(a)), A.CASE_STUD_R * math.cos(math.radians(a))
        body = body - xcyl(F.THREADS[A.CASE_STUD][0] * IN / 2 + 0.02, A.CASE_FACE_X - 8.5, A.CASE_FACE_X + 1.0, y, z)
    # forged ends, spring seats, rebound brackets; the bore for the axleshafts right through the ends
    for s in (1, -1):
        body = body + _end(s) + _seat(s) + _rebound_bracket(s)
    body = body - ycyl(A.CASE_BORE_R, A.TUBE_Y[1] - 40.0, A.CASE_END_Y + 1) - ycyl(A.CASE_BORE_R, -A.CASE_END_Y - 1, -A.TUBE_Y[1] + 40.0)
    # breather boss (top of the right-hand neck), filler/level boss (rear), drain boss (under)
    bx, by = A.BREATHER
    body = body + zc(9.0, 40.0, 55.0, bx, by)
    body = body - zc(3.65, 30.0, 56.0, bx, by)
    fy, fz = A.FILLER
    body = body + xcyl(15.0, -123.0, -105.0, fy, fz)
    body = body - xcyl(8.0, -124.0, -104.0, fy, fz)
    dx, dy = A.DRAIN
    body = body + zc(14.0, -132.0, -116.0, dx, dy)
    body = body - zc(7.95, -133.0, -115.0, dx, dy)
    # brake pipe three-way union tab (right neck top) and the balance lever pivot pin (rear)
    px, py = A.PIPE_BRACKET
    tab = box(px - 14.0, px + 14.0, py - 11.0, py + 11.0, 40.0, 52.0)
    tab = tab - _neck(1 if py > 0 else -1, 0.0)
    tab = tab - zc(3.3, 39.0, 53.0, px, py)
    body = body + (tab & box(-200, 200, -700, 700, 30.0, 60.0))
    by_, bz = A.BALANCE_PIVOT
    body = body + xcyl(13.0, -104.0, -92.0, by_, bz) + xcyl(6.35, -132.0, -103.9, by_, bz)
    body = body - Location((-129.0, by_, bz)) * Rot(90, 0, 0) * Cylinder(1.3, 20.0)                # split pin hole
    return _l(body, spec)


# =================================================================================================
# fittings
# =================================================================================================
def case_stud(spec) -> Part:
    """Item 4: 5/16 UNF stud, screwed into the ring, threaded both ends (drawn along +z from its inner end)."""
    d = F.THREADS[A.CASE_STUD][0] * IN
    L = spec.nom("length")
    s = Sh.chamfered_cyl(d, L, 0.6)
    p = IN / 24
    for z0, n in ((1.5, 6), (L - 14.0, 9)):
        for k in range(n):
            s = s - ring(d / 2 - 0.45, d / 2 + 1, z0 + k * p, z0 + k * p + 0.45 * p)
    return _l(s, spec)


def breather(spec) -> Part:
    """Item 11 (MGOC 21H6060): threaded body, hex, domed cap over the vent holes."""
    from build123d import RegularPolygon
    b = zc(3.6, -9.0, 0.2)
    b = b + (extrude(RegularPolygon(14.3 / math.sqrt(3), 6), 6.0) & Sh.revolved([(0, -0.1), (7.6, -0.1), (8.3, 0.7), (8.3, 5.3), (7.6, 6.1), (0, 6.1)]))
    b = b + Sh.revolved([(0, 5.9), (5.0, 5.9), (5.0, 8.0), (0, 8.0)])
    b = b + Sh.revolved([(0, 8.0), (7.5, 8.0), (7.5, 10.0), (5.5, 13.0), (0, 13.6)])
    for a in (0, 90):
        b = b - Location((0, 0, 7.0)) * Rot(0, 90, a) * Cylinder(1.1, 12.0)
    b = b - zc(1.4, -10.0, 7.5)
    return _l(b, spec)


def filler_plug(spec) -> Part:
    """Item 10: hexagon headed plug with a fibre washer; seat at z = 0, thread along -z."""
    from build123d import RegularPolygon
    af = spec.nom("across_flats")
    p = extrude(RegularPolygon(af / math.sqrt(3), 6), 8.0) & Sh.revolved([(0, -0.1), (af / 2 + 0.3, -0.1), (af / 2 + 1.6, 1.0),
                                                                        (af / 2 + 1.6, 7.0), (af / 2 + 0.3, 8.1), (0, 8.1)])
    p = p + ring(7.95, 11.0, -1.5, 0.01)
    p = p + zc(7.9, -12.0, 0.2)
    for k in range(6):
        p = p - ring(7.4, 9.0, -11.0 + k * 1.59, -11.0 + k * 1.59 + 0.7)
    return _l(p, spec)


def drain_plug(spec) -> Part:
    """Item 9 (MGOC 6K499, hex-key drain plug): round head with a hexagon socket; seat at z = 0."""
    from build123d import RegularPolygon
    p = Sh.revolved([(0, 0), (11.0, 0), (11.0, 4.5), (10.0, 5.5), (0, 5.5)])
    p = p - extrude(RegularPolygon(8.0 / math.sqrt(3), 6), 4.0).moved(Location((0, 0, 2.0)))
    p = p + zc(7.9, -11.0, 0.01)
    for k in range(6):
        p = p - ring(7.4, 9.0, -10.0 + k * 1.59, -10.0 + k * 1.59 + 0.7)
    return _l(p, spec)


def spindle_nut(spec) -> Part:
    return _l(F.hex_nut("3/8"), spec)


PARTS = {
    "axle.casing.case": {"build": case, "probes": {"tube_diameter": lambda p: _tube_d(p),
                                                    "width_over_backplate_faces": lambda p: _bp_width(p)}},
    "axle.casing.case-stud": {"build": case_stud, "probes": {"length": lambda p: probes.bbox_size(p, "z")}},
    "axle.casing.breather": {"build": breather},
    "axle.casing.filler-plug": {"build": filler_plug},
    "axle.casing.drain-plug": {"build": drain_plug},
    "axle.casing.spindle-nut": {"build": spindle_nut},
}


def _tube_d(p):
    """Diameter of the tube: the cylindrical face of the case at the spring seat station."""
    best = 0.0
    for f in p.faces():
        if f.geom_type.name == "CYLINDER":
            bb = f.bounding_box()
            if f.radius and bb.size.Y > 100 and abs(f.radius - A.TUBE_R) < 0.5:
                best = max(best, 2 * f.radius)
    return best


def _bp_width(p):
    """Distance between the outer faces of the two backplate flanges (planar faces normal to y)."""
    ys = [f.center().Y for f in p.faces() if f.geom_type.name == "PLANE" and abs(abs(f.normal_at().Y) - 1) < 1e-6
          and abs(abs(f.center().Y) - A.BACKPLATE_FACE_Y) < 0.01]
    return max(ys) - min(ys) if ys else 0.0
