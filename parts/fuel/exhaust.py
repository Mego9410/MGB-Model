"""Early one-piece welded exhaust system and its fixings (Haynes Ch 3 Sec 46; Ch 1 photos 6.14(a), (b); photo 46.2).

The pipes, the Y-piece and the silencers are drawn in place in the car frame from the routes in
mgb.exhaust_layout (they are one welded assembly; the parts split it at the welds so each piece carries its own
spec). The small fixings are drawn at the origin and placed by assemblies/fuel_exhaust.py.
"""
from __future__ import annotations

import math

from build123d import (Axis, Box, Circle, Cylinder, Ellipse, FilletPolyline, Location, Part, Plane, Polygon, Pos,
                       Rot, SlotOverall, extrude, fillet, loft, sweep, Sketch)

from mgb import exhaust_layout as E, fasteners as F, shapes as Sh
from parts.gearbox import casing as GC
from mgb import gearbox_layout as G

IN = 25.4


def _l(p, spec):
    p.label = spec.id
    return p


def path_of(points, radius):
    for r in (radius, radius * 0.7, radius * 0.5, radius * 0.3, radius * 0.15):
        try:
            return FilletPolyline(*points, radius=r)
        except Exception:  # noqa: BLE001
            continue
    raise ValueError("no fillet radius fits")


def tube(points, od, wall=None, radius=60.0):
    """Swept tube along a polyline with filleted bends; hollow if wall is given. Tries smaller bend radii (and a
    solid section) until the sweep is valid."""
    for r in (radius, radius * 0.8, radius * 0.65, radius * 0.5, radius * 0.35, radius * 0.2):
        try:
            path = FilletPolyline(*points, radius=r)
        except Exception:  # noqa: BLE001
            continue
        pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
        profs = ([pl * (Circle(od / 2) - Circle(od / 2 - wall))] if wall else []) + [pl * Circle(od / 2)]
        for prof in profs:
            try:
                s = sweep(prof, path=path)
                if s.is_valid and s.volume > 0:
                    return s
            except Exception:  # noqa: BLE001
                continue
    raise ValueError("no sweep fits the route")


def ring_at(p, d, od, idd, w):
    """Annulus of width w centred on point p, axis along direction d."""
    return Location(Plane(origin=p, z_dir=d)) * Location((0, 0, -w / 2)) * Sh.tube(od, idd, w)


def _dir(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


# ---------------------------------------------------------------------------------------------------------------
# front pipe: twin downpipes with their flanges, the Y-piece and the pipe to the centre silencer
# ---------------------------------------------------------------------------------------------------------------
def downpipe_flange():
    """Lozenge plate, two stud holes across the car, welded round the downpipe below its spigot (photo 46.2)."""
    L, W = 2 * E.STUD_DY + 22.0, 40.0
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        # superellipse-ish lozenge: round ends at the studs, waist round the pipe
        r_end = 11.0
        pts.append(((L / 2 - r_end) * math.copysign(abs(math.cos(a)) ** 0.6, math.cos(a)) + r_end * math.cos(a),
                    (W / 2) * math.sin(a)))
    return extrude(Polygon(*pts, align=None), E.FLANGE_T)


def front_pipe(spec) -> Part:
    od, t = E.DOWN_OD, E.DOWN_T
    m = None
    for name, route in E.DOWN_ROUTES.items():
        x, y = E.OUTLETS[name]
        top = E.FLANGE_TOP_Z
        p = tube(route, od, t, radius=70.0)
        # spigot above the flange, its end flared to hold the sealing ring (photo 46.2)
        p = p + Location((x, y, top)) * Sh.tube(od + 1.6, od - 2 * t, 4.0)
        fl = Location((x, y, top - E.FLANGE_T)) * Rot(0, 0, 90) * downpipe_flange()
        fl = fl - Location((x, y, top - E.FLANGE_T - 1)) * Sh.cyl(od - 2 * t, E.FLANGE_T + 2)
        for s in (-1, 1):
            fl = fl - Location((x, y + s * E.STUD_DY, top - E.FLANGE_T - 1)) * Sh.cyl(8.6, E.FLANGE_T + 2)
        p = p + fl + Location((x, y, top - E.FLANGE_T - 2.0)) * Sh.tube(od + 5.0, od - 1.0, 2.0)   # fillet weld
        m = p if m is None else m + p
    # Y-piece: the two downpipe ends run into a pressed breeches that necks down to the system pipe
    xa = E.Y_X + 40.0
    ya = [r[-1][1] for r in E.DOWN_ROUTES.values()]
    yc, zc = (ya[0] + ya[1]) / 2, E.RUN_Z
    w = abs(ya[0] - ya[1]) + od + 4.0
    s0 = Plane(origin=(xa + 4.0, yc, zc), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)) * SlotOverall(w, od + 4.0)
    s1 = Plane(origin=(E.Y_X - 6.0, yc, zc), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)) * Ellipse((w + E.PIPE_OD) / 4 + 2.0,
                                                                                          E.PIPE_OD / 2 + 3.0)
    s2 = Plane(origin=(E.Y_X - 26.0, E.FRONT_ROUTE[0][1], zc), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)) * Circle(E.PIPE_OD / 2)
    breeches = loft([s0, s1, s2])
    m = m + breeches
    for yy in ya:   # weld beads where the downpipes enter
        m = m + ring_at((xa + 6.5, yy, zc), (1, 0, 0), od + 5.0, od - 1.0, 3.0)
    main = tube([(E.Y_X - 24.0, E.FRONT_ROUTE[0][1], zc)] + E.FRONT_ROUTE[1:], E.PIPE_OD, E.PIPE_T, radius=90.0)
    return _l(m + main, spec)


# ---------------------------------------------------------------------------------------------------------------
# silencers
# ---------------------------------------------------------------------------------------------------------------
def _yz_plane(x, y, z):
    return Plane(origin=(x, y, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))


def centre_silencer(spec) -> Part:
    """Flattened oval case (MGOC: chrome bumper cars), rolled lock seams round both end plates, two pressed
    stiffening beads round the case, a lock seam along the underside and the inlet and outlet collars."""
    x0, x1 = E.CS_X
    L, W, H = x0 - x1, E.CS_W, E.CS_H
    y, z = E.CS_Y, E.CS_Z
    case = extrude(_yz_plane(x1, y, z) * SlotOverall(W, H), L)
    for xs in (x1, x0 - 7.0):                                   # rolled end seams
        case = case + extrude(_yz_plane(xs, y, z) * (SlotOverall(W + 7.0, H + 7.0) - SlotOverall(W - 2, H - 2)), 7.0)
    for f in (1 / 3, 2 / 3):                                     # stiffening beads
        xs = x1 + f * L - 3.0
        case = case + extrude(_yz_plane(xs, y, z) * (SlotOverall(W + 4.0, H + 4.0) - SlotOverall(W - 2, H - 2)), 6.0)
    case = case + Location(((x0 + x1) / 2, y - W / 4, z - H / 2 + 0.5)) * Box(L - 16.0, 8.0, 3.0)   # lock seam
    for xs, s in ((x0, 1), (x1, -1)):                             # collars for the pipes
        case = case + Location(Plane(origin=(xs, y, z), z_dir=(s, 0, 0))) * Sh.tube(E.PIPE_OD + 3.0, E.PIPE_OD - 1.0, 22.0)
        case = case + Location(Plane(origin=(xs, y, z), z_dir=(s, 0, 0))) * Sh.tube(E.PIPE_OD + 14.0, E.PIPE_OD - 1.0, 4.0)
    return _l(case, spec)


def rear_silencer(spec) -> Part:
    """Cylindrical case (MGOC: the rear silencer was always cylindrical), rolled end seams, a lock seam along it,
    dished end plates and the inlet and outlet collars."""
    x0, x1 = E.RS_X
    L, D = x0 - x1, E.RS_D
    y, z = E.RS_Y, E.RS_Z
    ax = Location(Plane(origin=(x1, y, z), z_dir=(1, 0, 0)))
    case = ax * Sh.cyl(D, L)
    for xs in (0.0, L - 7.0):
        case = case + ax * Location((0, 0, xs)) * Sh.tube(D + 7.0, D - 2.0, 7.0)
    case = case + ax * Location((0, 0, L / 2 - 4.0)) * Sh.tube(D + 4.0, D - 2.0, 8.0)       # centre bead
    case = case + Location(((x0 + x1) / 2, y - D / 2 * 0.7, z - D / 2 * 0.7)) * Rot(45, 0, 0) * Box(L - 16.0, 8.0, 3.0)
    for xs, s in ((x0, 1), (x1, -1)):
        loc = Location(Plane(origin=(xs, y, z), z_dir=(s, 0, 0)))
        case = case + loc * Sh.revolved([(0, 0), (D / 2 - 4.0, 0), (D / 2 - 12.0, 5.0), (E.PIPE_OD / 2 + 8.0, 7.0),
                                         (0, 7.0)])                                     # dished end plate
        case = case + loc * Sh.tube(E.PIPE_OD + 3.0, E.PIPE_OD - 1.0, 24.0)
    return _l(case, spec)


def inter_pipe(spec) -> Part:
    return _l(tube(E.INTER_ROUTE, E.PIPE_OD, E.PIPE_T, radius=110.0), spec)


def tail_pipe(spec) -> Part:
    """Tail pipe from the rear silencer to the bumper line, the end cut at 45 degrees, long side underneath."""
    r = E.PIPE_OD / 2
    pts = list(E.TAIL_ROUTE)
    ex, ey, ez = pts[-1]
    pts[-1] = (ex - r - 6.0, ey, ez)
    p = tube(pts, E.PIPE_OD, E.PIPE_T, radius=60.0)
    k = math.tan(math.radians(E.TAIL_CUT_DEG))
    cut = Polygon((ex - 300.0, ez - 60.0), (ex - 60.0 * k, ez - 60.0), (ex + 60.0 * k, ez + 60.0), (ex - 300.0, ez + 60.0),
                  align=None)
    cutter = extrude(Plane.XZ.offset(-ey) * cut, 60.0, both=True)
    return _l(p - cutter, spec)


# ---------------------------------------------------------------------------------------------------------------
# manifold fixings (drawn at the origin, axis along z)
# ---------------------------------------------------------------------------------------------------------------
def sealing_ring(spec) -> Part:
    """Exhaust flange sealing ring (photo 46.2): a tapered ring on the downpipe's flared spigot, seating in the
    manifold outlet's counterbore."""
    h, od = spec.nom("height"), spec.nom("outside_diameter")
    idd = E.DOWN_OD + 2.0                 # over the spigot's flared bead
    return _l(Sh.revolved([(idd / 2, 0), (od / 2, 0), (od / 2, h * 0.6), (od / 2 - 0.8, h), (idd / 2, h)]), spec)


def stud(spec) -> Part:
    L = spec.nom("length")
    r = 5.0 / 16.0 * IN / 2
    return _l(Sh.revolved([(0, 0), (r - 0.6, 0), (r, 0.6), (r, L - 0.6), (r - 0.6, L), (0, L)]), spec)


def spring_washer(spec) -> Part:
    od, idd, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, idd, t)
    return _l(w - Location((od / 2 - 1.0, 0, t / 2)) * Box(od / 2, 0.8, t + 2), spec)


def nut(size):
    def build(spec) -> Part:
        return _l(F.hex_nut(size), spec)
    return build


def bolt(size, length_in):
    def build(spec) -> Part:
        return _l(F.hex_bolt(size, length_in), spec)
    return build


def plain_washer(size):
    def build(spec) -> Part:
        return _l(F.plain_washer(size), spec)
    return build


# ---------------------------------------------------------------------------------------------------------------
# gearbox clip (front support): flat bar bracket on the side cover bolts, strap round the pipe
# ---------------------------------------------------------------------------------------------------------------
SC_FACE_Y = GC.SIDE_FACE + 0.8 + 2.0                                   # outer face of the side cover (assemblies)
SC_HOLES = [G.GF * Location((GC.SC_BOLTS[k][0], 0, GC.SC_BOLTS[k][1])) for k in E.SIDE_COVER_BOLTS]
SC_HOLES = [(h.position.X, h.position.Z) for h in SC_HOLES]          # (x, z) of the two bolts
CX, CY, CZ = E.CLIP_PIPE
PIPE_R = E.PIPE_OD / 2
EAR_Y = (CY - 6.5, CY - 1.5)                                           # the strap's two ears side by side
TONGUE_Y = (EAR_Y[0] - E.BRACKET_T, EAR_Y[0])
EAR_Z = (CZ + PIPE_R + 0.6, CZ + PIPE_R + 22.0)
STRAP_BOLT_Z = EAR_Z[1] - 9.0


def _xz_plate(outline, y0, y1):
    """Plate in an x-z plane from y0 to y1, outline given as (x, z) points."""
    pl = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    return extrude(pl * Polygon(*[(x, -z) for x, z in outline], align=None), y1 - y0, dir=(0, 1, 0))


def gearbox_bracket(spec) -> Part:
    """3-synchro gearbox exhaust bracket (MGOC GEX7189): a flat bar under the two lowest rear side cover bolts,
    a tongue down from its middle, joggled out to the pipe, with the hole for the front support bolt."""
    t = E.BRACKET_T
    (xa, za), (xb, zb) = SC_HOLES
    top = max(za, zb) + 8.0
    bar = _xz_plate([(min(xa, xb) - 12, top), (max(xa, xb) + 12, top), (max(xa, xb) + 12, top - 24),
                     (CX + 10, top - 34), (CX - 10, top - 34), (min(xa, xb) - 12, top - 24)], SC_FACE_Y, SC_FACE_Y + t)
    for x, z in SC_HOLES:
        bar = bar - Location((x, SC_FACE_Y - 1, z)) * Rot(-90, 0, 0) * Cylinder(4.2, t + 2, align=Sh.ALIGN_BASE)
    zj = top - 34.0
    joggle = Location((CX, (SC_FACE_Y + TONGUE_Y[1]) / 2, zj - t / 2)) * Box(20.0, TONGUE_Y[1] - SC_FACE_Y, t)
    tongue = _xz_plate([(CX - 10, zj), (CX + 10, zj), (CX + 10, EAR_Z[0] + 6), (CX + 6, EAR_Z[0] + 2),
                        (CX - 6, EAR_Z[0] + 2), (CX - 10, EAR_Z[0] + 6)], TONGUE_Y[0], TONGUE_Y[1])
    br = bar + joggle + tongue
    br = br - Location((CX, TONGUE_Y[0] - 1, STRAP_BOLT_Z)) * Rot(-90, 0, 0) * Cylinder(4.2, t + 2, align=Sh.ALIGN_BASE)
    return _l(br, spec)


def gearbox_strap(spec) -> Part:
    """Exhaust strap (MGOC GEX7194): a steel band round the pipe whose ends turn up as two ears either side of
    the bracket's tongue line, pinched by the front support bolt."""
    w, t = E.STRAP_W, E.STRAP_T
    ax = Location(Plane(origin=(CX - w / 2, CY, CZ), z_dir=(1, 0, 0)))
    band = ax * Sh.tube(2 * (PIPE_R + t), 2 * PIPE_R + 0.2, w)
    band = band - Location((CX, (EAR_Y[0] + EAR_Y[1]) / 2, CZ + PIPE_R)) * Box(w + 2, EAR_Y[1] - EAR_Y[0] - 2 * t + 0.01, 3 * t)
    ears = None
    for y0 in (EAR_Y[0], EAR_Y[1] - t):
        e = _xz_plate([(CX - w / 2, EAR_Z[0]), (CX + w / 2, EAR_Z[0]), (CX + w / 2, EAR_Z[1] - 4), (CX + w / 2 - 4, EAR_Z[1]),
                       (CX - w / 2 + 4, EAR_Z[1]), (CX - w / 2, EAR_Z[1] - 4)], y0, y0 + t)
        ears = e if ears is None else ears + e
    s = band + ears
    s = s - Location((CX, EAR_Y[0] - 1, STRAP_BOLT_Z)) * Rot(-90, 0, 0) * Cylinder(4.2, EAR_Y[1] - EAR_Y[0] + 2,
                                                                                     align=Sh.ALIGN_BASE)
    return _l(s, spec)


# ---------------------------------------------------------------------------------------------------------------
# rear mounting: body bracket, bonded rubber block, pinch clamp
# ---------------------------------------------------------------------------------------------------------------
RX, RY, RZ = E.REAR_CLAMP
CLAMP_W = 25.0
EAR_TOP = RZ + PIPE_R + 34.0
RUB = (16.0, 36.0, 66.0)                                     # rubber block: thickness (y), width (x), height (z)
RUB_Z0 = RZ + PIPE_R + 10.0                                  # bottom of the block between the clamp ears
RUB_HOLES = (RUB_Z0 + 13.0, RUB_Z0 + RUB[2] - 13.0)
CLAMP_BOLT_Z = RUB_HOLES[0]
BR_T = 3.0
BR_TAB_Y = RY + RUB[0] / 2                                   # bracket tab on the block's outboard face


def rear_clamp(spec) -> Part:
    """One half of the pinch clamp: a half band round the tail pipe and a long flat ear up the side of the
    rubber block, pinched by the rear mounting pipe bolt (Sec 46 para 3)."""
    t = 2.5
    ax = Location(Plane(origin=(RX - CLAMP_W / 2, RY, RZ), z_dir=(1, 0, 0)))
    half = ax * Sh.tube(2 * (PIPE_R + t), 2 * PIPE_R + 0.2, CLAMP_W)
    half = half & Location((RX, RY - 50.0, RZ)) * Box(CLAMP_W + 2, 100.0, 100.0)      # the -y half
    y0 = RY - RUB[0] / 2 - t
    zb = RZ + math.sqrt(PIPE_R ** 2 - (RUB[0] / 2 + t) ** 2) - 1.0
    ear = _xz_plate([(RX - CLAMP_W / 2, zb), (RX + CLAMP_W / 2, zb),
                     (RX + CLAMP_W / 2, EAR_TOP - 5), (RX + CLAMP_W / 2 - 5, EAR_TOP), (RX - CLAMP_W / 2 + 5, EAR_TOP),
                     (RX - CLAMP_W / 2, EAR_TOP - 5)], y0, y0 + t)
    neck = _xz_plate([(RX - CLAMP_W / 2, RZ + 4.0), (RX + CLAMP_W / 2, RZ + 4.0), (RX + CLAMP_W / 2, RZ + PIPE_R + 2.0),
                      (RX - CLAMP_W / 2, RZ + PIPE_R + 2.0)], y0, y0 + t) - Location(Plane(origin=(RX - 20, RY, RZ),
                                                                                         z_dir=(1, 0, 0))) * Sh.cyl(2 * PIPE_R + 0.2, 40)
    c = half + ear + neck - Location(Plane(origin=(RX - 20, RY, RZ), z_dir=(1, 0, 0))) * Sh.cyl(2 * PIPE_R + 0.2, 40)
    c = c - Location((RX, y0 - 1, CLAMP_BOLT_Z)) * Rot(-90, 0, 0) * Cylinder(3.4, t + 2, align=Sh.ALIGN_BASE)
    return _l(c, spec)


def rear_mounting(spec) -> Part:
    """Bonded rubber mounting (MGOC GEX7275): a rubber block with a steel tube bonded through each end for the
    clamp bolt below and the bracket bolt above."""
    t, w, h = RUB
    blk = Location((RX, RY, RUB_Z0 + h / 2)) * Box(w, t, h)
    blk = fillet(blk.edges().filter_by(Axis.Y), 9.0)
    for z in RUB_HOLES:
        blk = blk - Location((RX, RY - t, z)) * Rot(-90, 0, 0) * Cylinder(4.5, 2 * t, align=Sh.ALIGN_BASE)
        blk = blk + Location((RX, RY - t / 2 - 0.5, z)) * Rot(-90, 0, 0) * Sh.tube(9.0, 6.6, t + 1.0)
    return _l(blk, spec)


def rear_bracket(spec) -> Part:
    """Body bracket: a pressed angle screwed up under the boot floor, its tab hanging down on the outboard face
    of the rubber block, with a flange to stiffen it."""
    zt = E.REAR_BRACKET_Z[1]
    zb = RUB_HOLES[1] - 14.0
    y0 = BR_TAB_Y
    tab = _xz_plate([(RX - 18, zb), (RX + 18, zb), (RX + 22, zt - BR_T), (RX - 22, zt - BR_T)], y0, y0 + BR_T)
    foot = Location((RX, y0 + 20.0, zt - BR_T / 2)) * Box(52.0, 40.0 + BR_T, BR_T)
    foot = fillet(foot.edges().filter_by(Axis.Z), 6.0)
    ribs = None
    for dx in (-17.0, 17.0):                                  # turned-out edges stiffen the tab
        r = Location((RX + dx, y0 + BR_T + 4.0, (zb + 14.0 + zt - BR_T) / 2)) * Box(BR_T, 8.0, zt - BR_T - zb - 14.0)
        ribs = r if ribs is None else ribs + r
    b = tab + foot + ribs
    b = b - Location((RX, y0 - 1, RUB_HOLES[1])) * Rot(-90, 0, 0) * Cylinder(3.4, BR_T + 2, align=Sh.ALIGN_BASE)
    for dx in (-14.0, 14.0):
        b = b - Location((RX + dx, y0 + 26.0, zt - BR_T - 1)) * Cylinder(3.4, BR_T + 2, align=Sh.ALIGN_BASE)
    return _l(b, spec)


PARTS = {
    "fuel.exhaust.front-pipe": {"build": front_pipe},
    "fuel.exhaust.centre-silencer": {"build": centre_silencer,
                                     "probes": {"length": lambda p: p.bounding_box().size.X - 2 * 22.0}},
    "fuel.exhaust.inter-pipe": {"build": inter_pipe,
                                "probes": {"outside_diameter": lambda p: (p & Location((-1800.0, E.IP_Y, E.IP_Z)) * Box(
                                    4.0, 120.0, 120.0)).bounding_box().size.Y}},
    "fuel.exhaust.rear-silencer": {"build": rear_silencer,
                                   "probes": {"length": lambda p: p.bounding_box().size.X - 2 * 24.0}},
    "fuel.exhaust.tail-pipe": {"build": tail_pipe},
    "fuel.exhaust.sealing-ring": {"build": sealing_ring},
    "fuel.exhaust.manifold-stud": {"build": stud, "probes": {"length": lambda p: p.bounding_box().size.Z}},
    "fuel.exhaust.flange-washer": {"build": spring_washer},
    "fuel.exhaust.flange-nut": {"build": nut("5/16")},
    "fuel.exhaust.gearbox-bracket": {"build": gearbox_bracket},
    "fuel.exhaust.gearbox-strap": {"build": gearbox_strap},
    "fuel.exhaust.strap-bolt": {"build": bolt("5/16", 1.0)},
    "fuel.exhaust.strap-washer": {"build": spring_washer},
    "fuel.exhaust.strap-nut": {"build": nut("5/16")},
    "fuel.exhaust.rear-bracket": {"build": rear_bracket},
    "fuel.exhaust.bracket-screw": {"build": bolt("1/4", 0.75)},
    "fuel.exhaust.rear-mounting": {"build": rear_mounting},
    "fuel.exhaust.rear-clamp": {"build": rear_clamp},
    "fuel.exhaust.clamp-bolt": {"build": bolt("1/4", 1.25)},
    "fuel.exhaust.mount-bolt": {"build": bolt("1/4", 1.25)},
    "fuel.exhaust.small-washer": {"build": spring_washer},
    "fuel.exhaust.small-nut": {"build": nut("1/4")},
}
