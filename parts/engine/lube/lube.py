"""Lubrication: sump, gasket, drain plug, oil pump and drive, strainer, early full-flow
oil filter (Haynes Fig 1.1), external oil pipe, relief valve and dipstick.

Built in the engine frame (absolute positions from mgb.lube_layout) except the small
round parts, which are built about Z at the origin and placed by the assembly.
"""
import math

from build123d import (Align, Axis, Box, Cylinder, Location, Part, Plane, Polygon, Pos, Rot, Sphere, Torus, extrude,
                       fillet, sweep)

from mgb import block_section as B, fasteners as F, probes, shapes as Sh, lube_layout as L

BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def _l(p, spec):
    p.label = spec.id
    return p


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=BASE).moved(Location(((x0 + x1) / 2, (y0 + y1) / 2, z0)))


def zcyl(r, z0, z1, x=0.0, y=0.0):
    return Cylinder(r, z1 - z0, align=BASE).moved(Location((x, y, z0)))


def _try_fillet(p, edges, r):
    try:
        return fillet(edges, r)
    except Exception:  # noqa: BLE001 - keep the sharp shape if the kernel refuses
        return p


# ---- sump ------------------------------------------------------------------------------------
def _sump_solid(grow, top, deep, shallow):
    """Outer (grow > 0) or inner shape of the pressed sump."""
    hw = 114.0 + grow
    x0, x1 = -L.B_HALF + 8 - grow, L.B_HALF - 8 + grow
    deep_part = box(L.SUMP_STEP_X - grow, x1, -hw, hw, top - deep, top + 0.01)
    shallow_part = box(x0, L.SUMP_STEP_X + 30, -hw, hw, top - shallow, top + 0.01)
    s = deep_part + shallow_part
    s = _try_fillet(s, s.edges().filter_by(Axis.Z), 14.0 + grow)
    s = _try_fillet(s, s.edges().group_by(Axis.Z)[0], 12.0 + max(grow, 0))
    return s


def sump(spec) -> Part:
    """Pressed steel sump: flat flange on the cork gasket, a deep well under the crank
    and a shallow tail at the rear, drain plug boss in the floor (photo 55.4)."""
    t = spec.nom("sheet_thickness")
    top = L.SUMP_TOP
    from mgb import electrical_layout as EZ
    outer = _sump_solid(t, top, L.SUMP_DEPTH, L.SUMP_SHALLOW) - EZ.recess_cylinder()
    inner = _sump_solid(0.0, top + 1, L.SUMP_DEPTH + 1 - t, L.SUMP_SHALLOW + 1 - t) - EZ.recess_cylinder(t)
    s = outer - inner
    flange = box(-L.B_HALF + 1, L.B_HALF - 1, -B.FLANGE_HW, B.FLANGE_HW, top - t, top)
    flange = _try_fillet(flange, flange.edges().filter_by(Axis.Z), 10.0)
    flange = flange - box(-L.B_HALF + 9, L.B_HALF - 9, -113, 113, top - t - 1, top + 1)
    s = s + (flange - EZ.recess_cylinder())   # P10: the flange and wall are relieved round the starter yoke
    for x, y in L.sump_bolts():
        s = s - zcyl(4.2, top - t - 1, top + 1, x, y)
    # stiffening swage round the deep well
    for sgn in (-1, 1):
        s = s + box(L.SUMP_STEP_X + 10, L.B_HALF - 30, sgn * (114 + t) - 1.2, sgn * (114 + t) + 1.2,
                    top - 40, top - 34)
    dx, dy = spec.nom("drain_x"), 0.0
    s = s + zcyl(14.0, L.SUMP_FLOOR - t - 6, L.SUMP_FLOOR - t + 0.5, dx, dy)      # drain boss
    s = s - zcyl(7.9, L.SUMP_FLOOR - t - 7, L.SUMP_FLOOR + 1, dx, dy)
    return _l(s, spec)


def sump_gasket(spec) -> Part:
    t = spec.nom("thickness")
    g = box(-L.B_HALF + 1, L.B_HALF - 1, -B.FLANGE_HW, B.FLANGE_HW, L.SUMP_TOP, L.SUMP_TOP + t)
    g = _try_fillet(g, g.edges().filter_by(Axis.Z), 10.0)
    g = g - box(-L.B_HALF + 10, L.B_HALF - 10, -111, 111, L.SUMP_TOP - 1, L.SUMP_TOP + t + 1)
    from mgb import electrical_layout as EZ
    g = g - EZ.recess_cylinder()
    for x, y in L.sump_bolts():
        g = g - zcyl(4.2, L.SUMP_TOP - 1, L.SUMP_TOP + t + 1, x, y)
    return _l(g, spec)


# ---- oil pump (Hobourn-Eaton rotor type) -------------------------------------------------------
def pump_body(spec) -> Part:
    """Cast body with a three-stud flange, the rotor pocket below the drive spindle and
    the inlet boss facing the strainer."""
    h = spec.nom("body_height")
    top = L.PUMP_TOP
    x, y = L.DRIVE_X, L.DRIVE_Y
    fx, fy = L.PUMP_FLANGE
    flange = zcyl(28.0, top - 9, top, fx, fy)
    for sx, sy in L.pump_studs():
        flange = flange + zcyl(8.5, top - 9, top, sx, sy)
    body = zcyl(spec.nom("rotor_pocket_diameter") / 2 + 4, top - h, top - 8, x, y)
    body = _try_fillet(body, body.edges().group_by(Axis.Z)[0], 3.0)
    inlet = Cylinder(9.0, 26, rotation=(90, 0, 0)).moved(Location((x, y - 22, top - h + 12)))
    p = flange + body + inlet
    for sx, sy in L.pump_studs():
        p = p - zcyl(4.2, top - 10, top + 1, sx, sy)
    p = p - zcyl(6.4, top - 20, top + 1, x, y)                              # spindle bore
    p = p - zcyl(spec.nom("rotor_pocket_diameter") / 2, top - h - 1, top - h + 14, x, y)   # rotor pocket
    p = p - Cylinder(6.0, 30, rotation=(90, 0, 0)).moved(Location((x, y - 26, top - h + 12)))
    return _l(p, spec)


def pump_cover(spec) -> Part:
    x, y = L.DRIVE_X, L.DRIVE_Y
    h = spec.nom("thickness")
    zb = L.PUMP_TOP - spec.nom("body_bottom")
    c = zcyl(spec.nom("diameter") / 2, zb - h, zb, x, y)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        c = c - zcyl(2.6, zb - h - 1, zb + 1, x + 21 * math.cos(a), y + 21 * math.sin(a))
    return _l(c, spec)


def _lobed(n, r_mean, amp, samples=120):
    pts = []
    for k in range(samples):
        a = 2 * math.pi * k / samples
        r = r_mean + amp * math.cos(n * a)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def inner_rotor(spec) -> Part:
    """Four-lobe inner rotor (Fig 1.20). Frame: axis Z, base at z = 0."""
    t = spec.nom("thickness")
    r = extrude(Polygon(*_lobed(4, 13.0, 3.0), align=None), t) - Cylinder(6.4, t * 3)
    return _l(r, spec)


def outer_rotor(spec) -> Part:
    """Five-lobe outer rotor that runs eccentric round the inner one (Fig 1.20)."""
    t, od = spec.nom("thickness"), spec.nom("outside_diameter")
    r = Cylinder(od / 2, t, align=BASE) - extrude(Polygon(*_lobed(5, 17.0, 3.2), align=None), t * 3).moved(
        Location((0, 0, -t)))
    return _l(r, spec)


def pump_spindle(spec) -> Part:
    """Drive shaft from the camshaft skew gear down into the pump (Haynes Sec 21)."""
    L_ = spec.nom("length")
    s = Sh.cyl(spec.nom("diameter"), L_)
    gear = Cylinder(7.0, 16, align=BASE).moved(Location((0, 0, L_ - 16)))
    for k in range(12):
        gear = gear - (Location((0, 0, L_ - 8)) * Rot(0, 0, 30 * k) * Location((7.0, 0, 0)) * Rot(25, 0, 0)
                       * Box(2.2, 3.0, 22))
    return _l(s + gear, spec)


# ---- strainer (photo 55.2) ------------------------------------------------------------------------
def strainer(spec) -> Part:
    """Gauze bowl on the sump floor with its pick-up pipe to the pump inlet."""
    d = spec.nom("diameter")
    x, y = L.DRIVE_X + 58, L.DRIVE_Y - 66          # under the deep well, clear of the shallow tail
    z0 = L.SUMP_FLOOR + 6
    bowl = zcyl(d / 2, z0, z0 + 14, x, y)
    bowl = _try_fillet(bowl, bowl.edges().group_by(Axis.Z)[0], 6.0)
    bowl = bowl - zcyl(d / 2 - 1.2, z0 + 1.2, z0 + 15, x, y)
    lid = zcyl(d / 2 - 1, z0 + 12, z0 + 14, x, y)
    for k in range(10):                                                     # gauze perforations
        a = math.radians(36 * k)
        lid = lid - zcyl(4.0, z0 + 11, z0 + 15, x + 34 * math.cos(a), y + 34 * math.sin(a))
    flange = box(x - 13, x + 13, y - 13, y + 13, z0 + 14, z0 + 17)                 # triangular flange area
    # pick-up pipe: up from the bowl, across to the pump inlet
    iz = L.PUMP_TOP - spec.nom("pump_inlet_drop")
    path_pts = [(x, y, z0 + 17), (x, y, iz), (L.DRIVE_X, L.DRIVE_Y - 35, iz)]
    pipe = _tube_path(path_pts, 6.5)
    centre = zcyl(5.0, z0 - 4, z0 + 20, x, y)                                     # centre bolt and nut
    return _l(bowl + lid + flange + pipe + centre, spec)


def _tube_path(pts, r, wall=None):
    """Pipe through straight points with 12 mm bend radii, as a solid rod (thin pipes
    read as solid at this scale)."""
    from build123d import Circle, FilletPolyline
    path = FilletPolyline(*pts, radius=12.0)
    start = path.position_at(0)
    prof = Plane(origin=start, z_dir=path.tangent_at(0)) * Circle(r)
    return sweep(prof, path=path)


# ---- oil filter, early type (Fig 1.1) ----------------------------------------------------------------
def filter_head(spec) -> Part:
    """Cast head bolted to the right-hand pad: flange to the block, body bending outward
    and down to the bowl seat, inlet union boss at the rear."""
    px, py, pz = L.FILTER_PAD
    ay = L.FILTER_AXIS_Y
    flange = box(px - 30, px + 30, py - 10, py, pz - 22, pz + 22)
    flange = _try_fillet(flange, flange.edges().filter_by(Axis.Y), 8.0)
    arm = box(px - 22, px + 22, ay, py - 6, pz - 18, pz + 14)
    arm = _try_fillet(arm, arm.edges().filter_by(Axis.Y), 10.0)
    seat_top = pz - 18
    seat = zcyl(spec.nom("seat_diameter") / 2, seat_top - 14, seat_top + 32, px, ay)
    seat = _try_fillet(seat, seat.edges().group_by(Axis.Z)[-1], 8.0)
    union = Cylinder(10.0, 28, rotation=(0, 90, 0)).moved(Location((px - 38, ay + 14, pz)))
    h = flange + arm + seat + union
    h = h - zcyl(spec.nom("seat_diameter") / 2 - 6, seat_top - 15, seat_top - 6, px, ay)   # seal groove recess
    h = h - zcyl(4.2, seat_top - 15, seat_top + 33, px, ay)                    # centre bolt thread
    for dz in (-14, 14):
        h = h - Cylinder(4.2, 30, rotation=(90, 0, 0)).moved(Location((px + (dz * 1.4), py - 5, pz + dz * 0.3)))
    h = h - Cylinder(6.0, 40, rotation=(0, 90, 0)).moved(Location((px - 38, ay + 14, pz)))
    return _l(h, spec)


def _bowl_top():
    return L.FILTER_PAD[2] - 18 - 14


def filter_case(spec) -> Part:
    """Pressed bowl hanging below the head, rolled lip at the top, the centre bolt
    entering through the bottom."""
    d, h = spec.nom("diameter"), spec.nom("height")
    px, ay = L.FILTER_PAD[0], L.FILTER_AXIS_Y
    top = _bowl_top()
    c = zcyl(d / 2, top - h, top, px, ay)
    c = _try_fillet(c, c.edges().group_by(Axis.Z)[0], 10.0)
    c = c - zcyl(d / 2 - 1.2, top - h + 1.2, top + 1, px, ay)
    c = c + (zcyl(d / 2 + 2.0, top - 6, top, px, ay) - zcyl(d / 2 - 0.5, top - 7, top + 1, px, ay))   # lip
    c = c + zcyl(9, top - h - 3, top - h + 2, px, ay)                           # bolt boss
    c = c - zcyl(4.2, top - h - 4, top - h + 3, px, ay)
    return _l(c, spec)


def filter_element(spec) -> Part:
    """Pleated felt element."""
    d, h = spec.nom("diameter"), spec.nom("height")
    px, ay = L.FILTER_PAD[0], L.FILTER_AXIS_Y
    top = _bowl_top() - 4
    pleats = extrude(Polygon(*_lobed(28, d / 2 - 2, 2.0, 224), align=None), h).moved(Location((px, ay, top - h)))
    e = pleats - zcyl(12.0, top - h - 1, top + 1, px, ay)
    e = e + (zcyl(d / 2 + 1, top - 1.5, top, px, ay) - zcyl(12, top - 2, top + 1, px, ay))
    e = e + (zcyl(d / 2 + 1, top - h, top - h + 1.5, px, ay) - zcyl(12, top - h - 1, top - h + 2, px, ay))
    return _l(e, spec)


def filter_centre_bolt(spec) -> Part:
    px, ay = L.FILTER_PAD[0], L.FILTER_AXIS_Y
    hb = F.hex_bolt("5/16", spec.nom("length") / 25.4)
    bottom = _bowl_top() - spec.nom("case_height") - 3
    return _l(Location((px, ay, bottom)) * hb, spec)


def ring(spec) -> Part:
    """Rubber sealing ring or washer about Z at the origin."""
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t), spec)


def filter_spring(spec) -> Part:
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("length"), 5, 1), spec)


def pressure_plate(spec) -> Part:
    d, t = spec.nom("diameter"), spec.nom("thickness")
    p = Sh.revolved([(4.4, 0), (d / 2, 0), (d / 2, t), (12, t), (10, t + 3), (4.4, t + 3)])
    return _l(p, spec)


# ---- external oil pipe (Fig 1.16 item 6) --------------------------------------------------------
def oil_pipe(spec) -> Part:
    """From the pump outlet union at the right rear of the crankcase forward to the
    filter head inlet, with banjo unions at both ends."""
    px, py, pz = L.FILTER_PAD
    ay = L.FILTER_AXIS_Y
    start = (-205.0, B.wall_y(-232.0, -1) - 14, -232.0)
    end = (px - 52, ay + 14, pz)
    r = spec.nom("outside_diameter") / 2
    pts = [start, (start[0] + 20, start[1] - 4, start[2]), (-150.0, start[1] - 10, -214.0),
           (end[0] - 40, end[1] + 2, end[2]), end]
    pipe = _tube_path(pts, r)
    banjo = lambda c: Cylinder(10.0, 14, rotation=(90, 0, 0)).moved(Location(c))   # noqa: E731
    return _l(pipe + banjo((start[0], start[1] + 4, start[2])) + Cylinder(9.0, 14, rotation=(0, 90, 0)).moved(
        Location((end[0] + 4, end[1], end[2]))), spec)


# ---- relief valve (Haynes Sec 17) ------------------------------------------------------------------------
def domed_nut(spec) -> Part:
    """Large domed hexagonal nut on the left rear boss. Frame: axis Z, seat at z = 0."""
    af = spec.nom("across_flats")
    from build123d import RegularPolygon
    hexp = extrude(RegularPolygon(af / math.sqrt(3), 6), 14)
    dome = Sphere(af / 2).moved(Location((0, 0, 12))) & Box(af * 2, af * 2, af, align=BASE).moved(Location((0, 0, 12)))
    p = hexp + dome + Sh.cyl(af * 0.6, 12, z0=-12)
    return _l(p, spec)


def relief_spring(spec) -> Part:
    return _l(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), spec.nom("fitted_length"), 11, 1),
              spec)


def relief_cup(spec) -> Part:
    d, L_ = spec.nom("diameter"), spec.nom("length")
    c = Sh.revolved([(0, 0), (d / 2 - 1.5, 0), (d / 2, 2), (d / 2, L_), (d / 2 - 1, L_), (d / 2 - 1, 3), (0, 3)])
    return _l(c, spec)


# ---- dipstick ---------------------------------------------------------------------------------------------
def dipstick(spec) -> Part:
    """Flat blade on a rod with a ring handle, entering the right-hand side (Haynes Sec 2)."""
    ex, ey, ez = L.DIPSTICK_ENTRY
    d = L.DIPSTICK_DIR
    Ltot = spec.nom("length")
    start = (ex - d[0] * 46, ey - d[1] * 46, ez - d[2] * 46)
    pl = Plane(origin=start, z_dir=d)
    rod = pl.location * Cylinder(2.4, Ltot, align=BASE)
    blade = pl.location * Box(9.0, 1.6, 90, align=BASE).moved(Location((0, 0, Ltot - 90)))
    stopper = pl.location * Cylinder(6.5, 10, align=BASE).moved(Location((0, 0, 30)))
    handle = Plane(origin=start, x_dir=(1, 0, 0), z_dir=(0, -d[2], d[1])).location * Torus(13.0, 2.2)
    handle = handle.moved(Location((-d[0] * 14, -d[1] * 14, -d[2] * 14)))
    marks = None
    for k in range(2):                                                     # MAX and MIN notches
        m = pl.location * Box(10, 2.4, 1.2, align=BASE).moved(Location((0, 0, Ltot - 40 - 22 * k)))
        marks = m if marks is None else marks + m
    return _l(rod + blade + stopper + handle - marks, spec)


def nut(size):
    return lambda spec: _l(F.hex_nut(size), spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def stud(spec) -> Part:
    return _l(Sh.chamfered_cyl(spec.nom("thread_diameter"), spec.nom("length"), 0.6), spec)


def drain_plug(spec) -> Part:
    from build123d import RegularPolygon
    af = spec.nom("across_flats")
    p = extrude(RegularPolygon(af / math.sqrt(3), 6), 9) + Sh.cyl(spec.nom("thread_diameter"), 14, z0=-14)
    return _l(p, spec)


NUT = {"across_flats": F.across_flats, "thickness": lambda p: probes.bbox_size(p, "z")}

PARTS = {
    "engine.lube.sump": {"build": sump},
    "engine.lube.sump-gasket": {"build": sump_gasket},
    "engine.lube.sump-bolt": {"build": bolt("5/16")},
    "engine.lube.sump-bolt-washer": {"build": ring},
    "engine.lube.drain-plug": {"build": drain_plug},
    "engine.lube.drain-plug-washer": {"build": ring},
    "engine.lube.pump-body": {"build": pump_body},
    "engine.lube.pump-cover": {"build": pump_cover},
    "engine.lube.pump-inner-rotor": {"build": inner_rotor},
    "engine.lube.pump-outer-rotor": {"build": outer_rotor},
    "engine.lube.pump-spindle": {"build": pump_spindle},
    "engine.lube.pump-gasket": {"build": ring},
    "engine.lube.pump-stud": {"build": stud},
    "engine.lube.pump-nut": {"build": nut("5/16"), "probes": NUT},
    "engine.lube.strainer": {"build": strainer},
    "engine.lube.filter-head": {"build": filter_head},
    "engine.lube.filter-case": {"build": filter_case},
    "engine.lube.filter-element": {"build": filter_element},
    "engine.lube.filter-centre-bolt": {"build": filter_centre_bolt},
    "engine.lube.filter-head-seal": {"build": ring},
    "engine.lube.filter-bolt-seal": {"build": ring},
    "engine.lube.filter-steel-washer": {"build": ring},
    "engine.lube.filter-spring": {"build": filter_spring},
    "engine.lube.filter-plate": {"build": pressure_plate},
    "engine.lube.filter-head-bolt": {"build": bolt("5/16")},
    "engine.lube.oil-pipe": {"build": oil_pipe},
    "engine.lube.relief-nut": {"build": domed_nut},
    "engine.lube.relief-washer": {"build": ring},
    "engine.lube.relief-spring": {"build": relief_spring},
    "engine.lube.relief-cup": {"build": relief_cup},
    "engine.lube.dipstick": {"build": dipstick},
}
