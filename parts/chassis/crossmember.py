"""Front crossmember and its body mountings (Haynes Ch 11 Fig 11.2 items 1-7, 15-18, 40-45; Fig 11.1; Sec 3,
Sec 4; printed p204-205), drawn in the car frame (mgb.front_suspension_layout).

Forms (Fig 11.2, Fig 11.1): a pressed and welded box beam right across the car - a shallow centre section
dipped under the sump, sides that rise to the two spring towers, each tower's flat top carrying the lever
damper (four bolt holes and a large access hole), an outer shelf the front chassis leg sits on through the
rubber pads with an ear fore and aft for the two support bolts, a seam flange along the bottom edges, the
two angled engine mounting brackets welded to the front face (two holes each), two bosses for the rack
clamps, the spring opening in the underside of each tower and the holes for the wishbone pivot bolts. The
support bolts (2) pass up through the pads (3 above the shelf, 4 below it), the plate (5) and nut (6)
underneath, the plain washer and nut (7) on top of the chassis leg (Sec 3 para 2). The spring spigot (15)
is screwed under the shelf (16-18); the rebound buffer (40) stands on the shelf on its distance piece (41).
"""
from __future__ import annotations

import math

from build123d import Face, Location, Part, Rot, Wire, extrude, offset

from mgb import fasteners as F, front_suspension_layout as L, probes, shapes as Sh
from mgb.chassis_geom import (IN, box, hexagon, lab, spring_washer, xcyl, xprism, yprism, ycyl, zcyl, zprism, zrev)
from mgb.poly2d import ccw, circle_pts, hull

X0, X1 = L.XM_X
T = L.XM_T
FX = L.FX


def _top_half():
    """Top surface of the beam (|y|, z) from the centre out."""
    return [(0.0, L.XM_DIP_TOP), (150.0, L.XM_DIP_TOP), (166.0, L.XM_DIP_TOP + 12.0),
            (L.XM_TOWER_Y[0] - 12.0, L.XM_TOWER_TOP - 12.0), (L.XM_TOWER_Y[0], L.XM_TOWER_TOP),
            (L.XM_TOWER_Y[1], L.XM_TOWER_TOP), (L.XM_SHELF_Y[0], L.XM_SHELF_Z), (L.XM_SHELF_Y[1], L.XM_SHELF_Z)]


def _bottom_half():
    return [(0.0, L.XM_LOW_Z), (148.0, L.XM_LOW_Z), (192.0, L.XM_BOTTOM_Z), (300.0, L.XM_BOTTOM_Z),
            (400.0, L.XM_SHELF_Z - 30.0), (L.XM_SHELF_Y[1], L.XM_SHELF_Z - 30.0)]


def outline():
    top = _top_half()
    bot = _bottom_half()
    right_top = [(-y, z) for y, z in reversed(top)]
    left_top = top[1:]
    left_bot = list(reversed(bot))
    right_bot = [(-y, z) for y, z in bot[1:]]
    return right_top + left_top + left_bot + right_bot


def _xface(pts, x):
    return Face(Wire.make_polygon([(x, y, z) for y, z in ccw(pts)], close=True))


def _beam():
    pts = outline()
    outer = extrude(_xface(pts, X0), X1 - X0, dir=(1, 0, 0))
    inner_face = offset(_xface(pts, X0 + T), -T)
    inner = extrude(inner_face, X1 - X0 - 2 * T, dir=(1, 0, 0))
    b = outer - inner
    # seam flanges along the bottom edges, front and rear (the pressing's joint)
    bot = _bottom_half()
    full = [(-y, z) for y, z in reversed(bot)] + bot[1:]
    for xa, xb in ((X0 - 11.0, X0 + 0.2), (X1 - 0.2, X1 + 11.0)):
        band = full + [(y, z + T) for y, z in reversed(full)]
        for k in range(len(full) - 1):
            (ya, za), (yb, zb) = full[k], full[k + 1]
            seg = [(ya, za), (yb, zb), (yb, zb + T), (ya, za + T)]
            if abs(yb - ya) > 1:
                b = b + xprism(seg, xa, xb)
    return b


def top_z(y):
    """Height of the beam's top surface at |y|."""
    pts = _top_half()
    y = abs(y)
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / max(y1 - y0, 1e-9)
    return pts[-1][1]


def _engine_bracket(side):
    """Angled engine mounting bracket welded on the beam's sloping top: a pressed box under an inclined pad with two
    holes for the mounting rubber's studs (Fig 11.2: two holes each; Fig 1.29 crossmember side)."""
    a = math.radians(L.ENGINE_MOUNT_ANGLE)
    cx, cy, cz = L.ENGINE_MOUNT_PAD
    u = (math.cos(a), math.sin(a))                       # up the slope, outboard
    lo = (cy - 32 * u[0], cz - 32 * u[1])
    hi = (cy + 32 * u[0], cz + 32 * u[1])
    ys = [hi[0] + 2.0 - k * (hi[0] + 2.0 - (lo[0] - 4.0)) / 8 for k in range(9)]
    poly = [lo, hi] + [(y, min(top_z(y) + 1.5, hi[1] - 6.0)) for y in ys]
    xa, xb = cx - 28.0, cx + 28.0
    br = extrude(_xface(poly, xa), xb - xa, dir=(1, 0, 0))
    inner = offset(_xface(poly, xa + 3.0), -3.0)
    br = br - extrude(inner, xb - xa - 6.0, dir=(1, 0, 0))
    for dx in (-13.0, 13.0):
        p = (cx + dx, cy, cz)
        br = br - Location(p) * Rot(math.degrees(a), 0, 0) * zcyl(4.4, -12, 4)
    return br if side > 0 else br.mirror(__import__("build123d").Plane.XZ)


def _rack_boss(side):
    """Boss for a rack mounting bracket: a block welded to the front face with a gusset under it, two tapped holes
    fore and aft of the rack axis for the bracket's vertical bolts (Fig 11.8 item 1, Sec 20 para 6)."""
    y = side * L.RACK_CLAMP_Y
    top = L.RACK_BOSS_TOP
    xa, xb = X1 - 0.5, L.RACK_AXIS[0] + L.RACK_BOLT_DX + 12.0
    b = box(xa, xb, y - 15.0, y + 15.0, top - 12.0, top)
    b = b + yprism([(xa, top - 11.0), (xa, top - 44.0), (xa + 30.0, top - 11.0)], y - 4.0, y + 4.0)   # gusset
    for dx in (-L.RACK_BOLT_DX, L.RACK_BOLT_DX):
        b = b - zcyl(4.2, top - 13, top + 1, L.RACK_AXIS[0] + dx, y)
    return b


def _ears(side):
    """Mounting ears fore and aft on the outer shelf, with the support bolt holes; the shelf's end wall."""
    s = side
    e = box(FX - L.XM_EAR_X, FX + L.XM_EAR_X, L.XM_SHELF_Y[0] + 30.0, L.XM_SHELF_Y[1], L.XM_SHELF_Z - T, L.XM_SHELF_Z)
    for xa, xb in ((FX - L.XM_EAR_X, X0 + 0.5), (X1 - 0.5, FX + L.XM_EAR_X)):          # turned-down edges
        e = e + box(xa, xb, L.XM_SHELF_Y[1] - T, L.XM_SHELF_Y[1], L.XM_SHELF_Z - 24.0, L.XM_SHELF_Z - T + 0.1)
        e = e + box(xa, xb, L.XM_SHELF_Y[0] + 30.0, L.XM_SHELF_Y[0] + 30.0 + T, L.XM_SHELF_Z - 18.0, L.XM_SHELF_Z - T + 0.1)
    return e if s > 0 else e.mirror(__import__("build123d").Plane.XZ)


def _buffer_ledge(side):
    """Ledge welded to the tower's outer wall under the damper's front arm for the rebound buffer."""
    bx, by, bz = L.REBOUND_BUFFER
    wall_y = L.XM_TOWER_Y[1] + (L.XM_SHELF_Y[0] - L.XM_TOWER_Y[1]) * (L.XM_TOWER_TOP - bz) / (L.XM_TOWER_TOP - L.XM_SHELF_Z)
    e = box(bx - 20.0, bx + 20.0, wall_y - 6.0, by + 18.0, bz - T, bz)
    e = e + yprism([(bx - 2.0, bz - T), (bx + 2.0, bz - T), (bx + 2.0, bz - 20.0), (bx - 2.0, bz - 20.0)], wall_y - 6.0, by + 6.0)   # gusset
    e = e - zcyl(4.2, bz - 25, bz + 1, bx, by)
    return e if side > 0 else e.mirror(__import__("build123d").Plane.XZ)


def crossmember(spec) -> Part:
    c = _beam()
    for s in (1, -1):
        c = c + _ears(s) + _engine_bracket(s) + _rack_boss(s)
        # damper platform: four bolt holes, large access hole, a raised ring round it
        for x, y, z in L.DAMPER_BOLTS:
            c = c - zcyl(5.6, z - 8, z + 1, x, s * y)
        c = c - zcyl(26.0, L.XM_TOWER_TOP - 8, L.XM_TOWER_TOP + 1, FX, s * (L.DAMPER_SHAFT_Y - 40.0))
        # spring opening through the underside, the spring seat (shelf underside) left whole
        c = c - zcyl(54.0, L.XM_LOW_Z - 10, L.SPRING_TOP_Z - 0.5, L.SPRING_X, s * L.PAN_Y)
        # spigot screws, body support bolts, rebound buffer bolt
        for x, y in L.SPIGOT_SCREWS:
            c = c - zcyl(4.2, L.XM_SHELF_Z - 6, L.XM_SHELF_Z + 1, x, s * y)
        for x in L.BODY_BOLT_X:
            c = c - zcyl(6.0, L.XM_SHELF_Z - 6, L.XM_SHELF_Z + 1, x, s * L.BODY_BOLT_Y)
        c = c + _buffer_ledge(s)
        # wishbone pivot bolts up through the underside
        for x in L.WISHBONE_PIVOT_BOLTS:
            c = c - zcyl(5.0, L.XM_BOTTOM_Z - 5, L.XM_BOTTOM_Z + 8, x, s * L.WISHBONE_INNER[1])
        # brake pipe clip holes on the front face (Sec 3 para 2)
        c = c - xcyl(2.6, X1 - 5, X1 + 1, s * 300.0, L.XM_BOTTOM_Z + 40.0)
    # RHD: a tube through the right-hand tower for the steering column and its universal joint (D: the column
    # runs back from the pinion beside the engine; MGOC: LHD and RHD crossmembers differ)
    from mgb import steering_layout as SL
    from mgb.chassis_geom import tube_between, rod
    p0, p1 = SL.col(SL.t_at_x(X1 + 12.0)), SL.col(SL.t_at_x(X0 - 12.0))
    r = SL.CROSSMEMBER_TUBE_R
    env = extrude(_xface(outline(), X0), X1 - X0, dir=(1, 0, 0))
    c = c - rod(p0, p1, r + 0.6)
    c = c + (tube_between(p0, p1, r + T, r) & env)
    # drain and lightening holes in the dip
    for y in (-60.0, 0.0, 60.0):
        c = c - zcyl(9.0, L.XM_LOW_Z - 5, L.XM_LOW_Z + 8, FX, y)
    return lab(c, spec)


# ---- body mountings (2-7) -------------------------------------------------------------------------------
def support_bolt(spec) -> Part:
    """Item 2: threaded both ends (Fig 11.2), drawn along +z from its lower end."""
    L_ = spec.nom("length")
    d = F.THREADS["7/16"][0] * IN
    b = Sh.chamfered_cyl(d, L_, 0.8)
    for z0, z1 in ((4.0, 30.0), (L_ - 34.0, L_ - 3.0)):                      # thread grooves at both ends
        k = 0
        z = z0
        while z < z1:
            b = b - zrev([(d / 2 - 0.5, z), (d / 2 + 1, z - 0.3), (d / 2 + 1, z + 0.3)])
            z += IN / 20
    return lab(b, spec)


def pad(spec) -> Part:
    """Items 3, 4: square rubber mounting pad with a centre hole (along +z from 0)."""
    w, t = spec.nom("width"), spec.nom("thickness")
    p = box(-w / 2, w / 2, -w / 2, w / 2, 0, t) - zcyl(6.4, -1, t + 1)
    for k in range(4):                                                  # moulded ribs on the faces
        p = p - Rot(0, 0, 90 * k) * box(-w / 2 - 1, w / 2 + 1, w / 2 - 6.0, w / 2 - 4.5, t - 0.8, t + 1)
    return lab(p, spec)


def plate(spec) -> Part:
    w, t = spec.nom("width"), spec.nom("thickness")
    p = box(-w / 2, w / 2, -w / 2, w / 2, 0, t) - zcyl(6.0, -1, t + 1)
    p = p - box(-w / 2 - 1, w / 2 + 1, -w / 2 - 1, w / 2 + 1, t - 0.6, t + 1) + box(-w / 2 + 3, w / 2 - 3, -w / 2 + 3, w / 2 - 3, t - 0.61, t)
    return lab(p, spec)


def nut716(spec) -> Part:
    return lab(F.hex_nut("7/16"), spec)


def washer716(spec) -> Part:
    return lab(F.plain_washer("7/16"), spec)


# ---- spring spigot (15) and its screws (16-18) -----------------------------------------------------------
def spigot(spec) -> Part:
    """Pressed cup locating the spring's top coil, flange screwed under the shelf (drawn with its flange top
    at z 0, the cup hanging down)."""
    r = spec.nom("diameter") / 2
    h = spec.nom("depth")
    t = 2.5
    c = zrev([(0, -h), (r - 6.0, -h), (r, -h + 6.0), (r, -t), (54.0, -t), (54.0, 0.0), (0, 0.0)])
    c = c - zrev([(0, -h + t), (r - 6.0 - t * 0.4, -h + t), (r - t, -h + 6.0), (r - t, 1.0), (0, 1.0)])
    for x, y in L.SPIGOT_SCREWS:
        c = c - zcyl(4.2, -t - 1, 1, x - L.SPRING_X, y - L.PAN_Y)
    return lab(c, spec)


def screw516(length_in):
    def b(spec):
        return lab(F.hex_bolt("5/16", length_in), spec)
    return b


def nut516(spec):
    return lab(F.hex_nut("5/16"), spec)


def sw516(spec):
    return lab(spring_washer("5/16"), spec)


# ---- rebound buffer (40), distance piece (41), fixings (42-45) -------------------------------------------
def rebound_buffer(spec) -> Part:
    """Moulded rubber cone with a steel base plate and a stud (drawn up from its base at z 0)."""
    h = spec.nom("height")
    d = spec.nom("base_diameter")
    b = zrev([(0, 0), (d / 2, 0), (d / 2, 6.0), (d / 2 - 3.0, 9.0), (d / 2 * 0.62, h - 6.0), (d / 2 * 0.3, h), (0, h)])
    for k in range(3):                                                  # moulded rings
        z = 14.0 + 8.0 * k
        rr = d / 2 - 3.0 - (d / 2 * 0.38 - 3.0) * (z - 9.0) / (h - 15.0)
        b = b - zrev([(rr - 1.0, z), (rr + 2, z - 1.0), (rr + 2, z + 1.0)])
    b = b + zcyl(F.THREADS["5/16"][0] * IN / 2, -16.0, 0.01)   # stud through the ledge (and distance piece)
    return lab(b, spec)


def distance_piece(spec) -> Part:
    h = spec.nom("height")
    p = Sh.tube(spec.nom("diameter"), 8.4, h)
    return lab(p, spec)


PARTS = {
    "chassis.crossmember.crossmember": {"build": crossmember,
                                        "probes": {"width_over_shelves": lambda p: probes.bbox_size(p, "y")}},
    "chassis.crossmember.support-bolt": {"build": support_bolt, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "chassis.crossmember.upper-pad": {"build": pad},
    "chassis.crossmember.lower-pad": {"build": pad},
    "chassis.crossmember.plate": {"build": plate},
    "chassis.crossmember.nut": {"build": nut716},
    "chassis.crossmember.plain-washer": {"build": washer716},
    "chassis.crossmember.spigot": {"build": spigot},
    "chassis.crossmember.spigot-screw": {"build": screw516(0.75)},
    "chassis.crossmember.spigot-nut": {"build": nut516},
    "chassis.crossmember.spigot-washer": {"build": sw516},
    "chassis.crossmember.rebound-buffer": {"build": rebound_buffer},
    "chassis.crossmember.distance-piece": {"build": distance_piece},
    "chassis.crossmember.buffer-nut": {"build": nut516},
    "chassis.crossmember.buffer-washer": {"build": sw516},
}
