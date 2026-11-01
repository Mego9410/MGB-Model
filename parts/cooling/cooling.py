"""Water pump, fan, pulley, fan belt, radiator, pressure cap, drain tap and hoses.
Haynes Ch 2 (Figs 2.2, 2.4, 2.6). Built in the engine frame (mgb.cooling_layout)
apart from small round parts.
"""
import math

from build123d import (Align, Axis, Box, Circle, Cylinder, FilletPolyline, Location, Part, Plane, Polygon, Rot,
                       extrude, fillet, sweep)

from mgb import cooling_layout as C, fasteners as F, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
X = (1, 0, 0)


def _l(p, spec):
    p.label = spec.id
    return p


def _xdisc(r, x0, x1, y=0.0, z=0.0):
    return Cylinder(r, abs(x1 - x0), rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _xrev(prof, y, z, x0):
    """Revolve an (r, dx) profile about an X axis through (y, z), starting at x0."""
    return Location((x0, y, z)) * Rot(0, 90, 0) * Sh.revolved(prof)


def _tf(p, r=6.0, edges=None):
    try:
        return fillet(edges if edges is not None else p.edges(), r)
    except Exception:  # noqa: BLE001
        return p


def _hose(points, od, wall, radius=40.0):
    for r in (radius, radius * 0.6, radius * 0.35, radius * 0.2):
        try:
            path = FilletPolyline(*points, radius=r)
            break
        except ValueError:
            continue
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    try:
        return sweep(pl * (Circle(od / 2) - Circle(od / 2 - wall)), path=path)
    except (AssertionError, ValueError):
        return sweep(pl * Circle(od / 2), path=path)          # solid if the hollow sweep fails


# ---- water pump (Fig 2.6 items 1-13) ----------------------------------------------------------------
def pump_body(spec) -> Part:
    """Cast iron body: four-bolt flange on the block, bearing housing forward, inlet
    spigot for the bottom hose, grease plug boss on top (Haynes Sec 2 para 3)."""
    y, z = C.PUMP_AXIS
    x0 = C.PUMP_FACE_X + spec.nom("gasket_allowance")
    flange = Location((x0 + 6, y, z)) * Box(12, 86, 70)
    flange = _tf(flange, 12.0, flange.edges().filter_by(Axis.X))
    volute = _xdisc(40, x0 + 10, x0 + 30, y, z)
    housing = _xrev([(0, 0), (24, 0), (20, 26), (17, 34), (0, 34)], y, z, x0 + 28)
    inlet_base = Location((x0 + 26, y - 30, z - 34)) * Box(30, 26, 34)
    d = C.PUMP_INLET_DIR
    start = (C.PUMP_INLET[0], C.PUMP_INLET[1] - d[1] * 40, C.PUMP_INLET[2] - d[2] * 40)
    spig = Plane(origin=start, z_dir=d).location * Cylinder(spec.nom("inlet_diameter") / 2, 42, align=BASE)
    bead = Plane(origin=C.PUMP_INLET, z_dir=d).location * Cylinder(spec.nom("inlet_diameter") / 2 + 1.5, 3,
                                                                  align=BASE).moved(Location((0, 0, -8)))
    grease = Location((x0 + 44, y, z + 17)) * Cylinder(6, 14, align=BASE)
    p = flange + volute + housing + inlet_base + spig + bead + grease
    p = p - (Plane(origin=start, z_dir=d).location * Cylinder(spec.nom("inlet_diameter") / 2 - 3, 46, align=BASE))
    p = p - _xdisc(8.4, x0 + 20, x0 + 70, y, z)                          # spindle bore
    for sy, sz in ((-30, 22), (30, 22), (-30, -22), (30, -22)):           # four securing bolts (Sec 9 para 5)
        p = p - _xdisc(4.4, x0 - 1, x0 + 14, y + sy, z + sz)
    return _l(p, spec)


def pump_spindle(spec) -> Part:
    """Spindle and bearing assembly (items 3 and 7) with the impeller vane (2)."""
    y, z = C.PUMP_AXIS
    x0 = C.PUMP_FACE_X + 2
    L = spec.nom("length")
    s = _xdisc(8.0, x0 + 4, x0 + L, y, z)
    bearing = _xdisc(15.0, x0 + 34, x0 + 58, y, z)
    vane = _xdisc(30.0, x0 + 6, x0 + 10, y, z)
    for k in range(6):                                                  # impeller blades
        a = math.radians(60 * k)
        vane = vane + (Location((x0 + 13, y + 16 * math.cos(a), z + 16 * math.sin(a))) * Rot(math.degrees(a), 0, 0)
                       * Box(6, 2.4, 26))
    return _l(s + bearing + vane, spec)


def pump_gasket(spec) -> Part:
    y, z = C.PUMP_AXIS
    t = spec.nom("thickness")
    g = Location((C.PUMP_FACE_X + t / 2, y, z)) * Box(t, 86, 70)
    g = _tf(g, 12.0, g.edges().filter_by(Axis.X)) - _xdisc(32, C.PUMP_FACE_X - 1, C.PUMP_FACE_X + 2, y, z)
    for sy, sz in ((-30, 22), (30, 22), (-30, -22), (30, -22)):
        g = g - _xdisc(4.4, C.PUMP_FACE_X - 1, C.PUMP_FACE_X + 2, y + sy, z + sz)
    return _l(g, spec)


def pump_pulley(spec) -> Part:
    """Pressed V pulley with its hub on the spindle (item 9); the fan bolts to its face."""
    y, z = C.PUMP_AXIS
    r = spec.nom("outside_diameter") / 2
    gw = 9.5
    xc = C.BELT_X
    prof = [(8.0, 0), (r - 13, 0), (r, gw * 0.15), (r, gw * 0.3), (r - 12, gw / 2), (r, gw * 0.7), (r, gw * 0.85),
            (r - 13, gw), (24, gw), (24, gw + 8), (8.0, gw + 8)]
    p = _xrev(prof, y, z, xc - gw / 2)
    p = p + _xdisc(16, xc - 30, xc - gw / 2, y, z) - _xdisc(8.0, xc - 31, xc + 20, y, z)   # hub
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p = p - _xdisc(3.3, xc + gw - 1, xc + gw + 10, y + 19 * math.cos(a), z + 19 * math.sin(a))
    return _l(p, spec)


def fan(spec) -> Part:
    """Three-blade steel fan (12H1058, earliest MGBs to 1974) on a four-hole spider."""
    y, z = C.PUMP_AXIS
    r = spec.nom("diameter") / 2
    x0 = C.BELT_X + 9.5 + 8
    hub = _xdisc(30, x0, x0 + 2.5, y, z)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        hub = hub - _xdisc(3.3, x0 - 1, x0 + 4, y + 19 * math.cos(a), z + 19 * math.sin(a))
    blades = None
    for k in range(3):
        a = math.radians(90 + 120 * k)
        arm = (Location((x0 + 1.2, y + (r * 0.32) * math.cos(a), z + (r * 0.32) * math.sin(a)))
               * Rot(math.degrees(a) - 90, 0, 0) * Box(2.5, 22, r * 0.42))
        blade = (Location((x0 + 8, y + (r * 0.72) * math.cos(a), z + (r * 0.72) * math.sin(a)))
                 * Rot(math.degrees(a) - 90, 0, 0) * Rot(0, 0, spec.nom("pitch_deg")) * Box(2.5, 70, r * 0.56))
        blade = _tf(blade, 0.9, blade.edges().filter_by(Axis.X))
        b = arm + blade
        blades = b if blades is None else blades + b
    return _l(hub + blades, spec)


def fan_belt(spec) -> Part:
    """V belt round the crankshaft, water pump and alternator pulleys (3/8 in early belt)."""
    w = spec.nom("width")
    outer = Plane.YZ.offset(C.BELT_X - w / 2) * Polygon(*C.belt_loop(4.0), align=None)
    inner = Plane.YZ.offset(C.BELT_X - w / 2 - 1) * Polygon(*C.belt_loop(-2.0), align=None)
    return _l(extrude(outer, w, dir=X) - extrude(inner, w + 2, dir=X), spec)


# ---- radiator (Fig 2.4) ---------------------------------------------------------------------------
def radiator(spec) -> Part:
    """Vertical-flow radiator: brass top and bottom tanks, tube-and-fin core, side
    mounting flanges, filler neck, top inlet and bottom outlet stubs, drain tap boss."""
    x0, x1 = C.RAD_CORE
    y0, y1 = C.RAD_Y
    z0, z1 = C.RAD_CORE_Z
    core = Location(((x0 + x1) / 2, 0, (z0 + z1) / 2)) * Box(x1 - x0, y1 - y0, z1 - z0)
    for k in range(40):                                       # tube ends showing on the front face
        yy = y0 + 8 + k * (y1 - y0 - 16) / 39
        core = core - Location((x1, yy, (z0 + z1) / 2)) * Box(2.0, 3.2, z1 - z0 - 10)
    top = Location(((x0 + x1) / 2, 0, (C.RAD_TOP_TANK[0] + C.RAD_TOP_TANK[1]) / 2)) * Box(
        x1 - x0 + 6, y1 - y0 + 6, C.RAD_TOP_TANK[1] - C.RAD_TOP_TANK[0])
    top = _tf(top, 14.0, top.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1])
    bot = Location(((x0 + x1) / 2, 0, (C.RAD_BOTTOM_TANK[0] + C.RAD_BOTTOM_TANK[1]) / 2)) * Box(
        x1 - x0 + 6, y1 - y0 + 6, C.RAD_BOTTOM_TANK[1] - C.RAD_BOTTOM_TANK[0])
    bot = _tf(bot, 12.0, bot.edges().filter_by(Axis.Y).group_by(Axis.Z)[0])
    r = core + top + bot
    for sgn in (-1, 1):                                       # side channels with mounting holes
        ch = Location(((x0 + x1) / 2 + 8, sgn * (y1 + 9), (C.RAD_BOTTOM_TANK[0] + C.RAD_TOP_TANK[1]) / 2)) * Box(
            x1 - x0 + 16, 12, C.RAD_TOP_TANK[1] - C.RAD_BOTTOM_TANK[0])
        for zz in (C.RAD_CORE_Z[0] + 40, C.RAD_CORE_Z[1] - 40):
            ch = ch - Cylinder(4.2, 30, rotation=(90, 0, 0)).moved(Location((x1 + 8, sgn * (y1 + 9), zz)))
        r = r + ch
    fx, fy, fz = C.FILLER
    neck = Location((fx, fy, fz)) * Cylinder(22, 22, align=BASE)
    neck = neck + Location((fx, fy, fz + 20)) * Cylinder(26, 3, align=BASE)
    overflow = Cylinder(3.5, 50, rotation=(90, 0, 0)).moved(Location((fx, fy + 30, fz + 12)))
    r = r + neck + overflow
    ix, iy, iz = C.TOP_INLET
    r = r + _xdisc(spec.nom("inlet_diameter") / 2, ix - 34, ix + 2, iy, iz) + _xdisc(spec.nom("inlet_diameter") / 2 + 1.5, ix - 30, ix - 27, iy, iz)
    ox, oy, oz = C.BOTTOM_OUTLET
    r = r + _xdisc(spec.nom("outlet_diameter") / 2, ox - 34, ox + 2, oy, oz) + _xdisc(spec.nom("outlet_diameter") / 2 + 1.5, ox - 30, ox - 27, oy, oz)
    r = r + Cylinder(9, 16, rotation=(90, 0, 0)).moved(Location(((x0 + x1) / 2, y1 + 8, C.RAD_BOTTOM_TANK[0] + 16)))
    r = r - Cylinder(5.2, 30, rotation=(90, 0, 0)).moved(Location(((x0 + x1) / 2, y1 + 8, C.RAD_BOTTOM_TANK[0] + 16)))
    r = r - Location((fx, fy, fz + 2)) * Cylinder(17, 30, align=BASE)
    return _l(r, spec)


def pressure_cap(spec) -> Part:
    d = spec.nom("diameter")
    c = Sh.revolved([(0, 0), (d / 2 - 2, 0), (d / 2, 3), (d / 2, 12), (d / 2 - 3, 16), (0, 16)])
    for k in range(2):                                          # finger grips
        c = c + Location((0, 0, 14)) * Rot(0, 0, 90 * k) * Box(d * 0.9, 5, 6, align=BASE)
    c = c + Sh.cyl(28, 10, z0=-10)
    return _l(c, spec)


def drain_tap(spec) -> Part:
    d, L = spec.nom("body_diameter"), spec.nom("length")
    body = Sh.cyl(d, L * 0.6) + Sh.cyl(d * 0.8, L * 0.4, z0=-L * 0.4)
    spout = Cylinder(3.5, 16, rotation=(0, 90, 0)).moved(Location((8, 0, L * 0.25)))
    lever = Box(4, 28, 3, align=BASE).moved(Location((0, 0, L * 0.6)))
    return _l(body + spout + lever, spec)


# ---- hoses -------------------------------------------------------------------------------------------
def top_hose(spec) -> Part:
    ex, ey, ez = C.ELBOW_OUTLET
    d = C.ELBOW_DIR
    s = (ex - d[0] * 30, ey, ez - d[2] * 30)
    ix, iy, iz = C.TOP_INLET
    pts = [s, (ex + d[0] * 22, ey, ez + d[2] * 22), (ix - 30, iy, iz)]
    return _l(_hose(pts, spec.nom("outside_diameter"), spec.nom("wall")), spec)


def bottom_hose(spec) -> Part:
    px, py, pz = C.PUMP_INLET
    d = C.PUMP_INLET_DIR
    s = (px - d[0] * 32, py - d[1] * 32, pz - d[2] * 32)
    ox, oy, oz = C.BOTTOM_OUTLET
    pts = [s, (px + d[0] * 30, py + d[1] * 30, pz + d[2] * 30), (296.0, -84.0, -196.0), (ox - 30, oy, oz)]
    return _l(_hose(pts, spec.nom("outside_diameter"), spec.nom("wall"), 34.0), spec)


def hose_clip(spec) -> Part:
    d = spec.nom("diameter")
    band = Sh.tube(d + 1.4, d, 12) + Location((d / 2 + 3, 0, 6)) * Box(8, 10, 12)
    return _l(band + Location((d / 2 + 8, 0, 6)) * Cylinder(3, 10, rotation=(0, 90, 0)), spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t) - Box(1.0, od, t * 3).moved(Location((0, od / 2, 0))), spec)


PARTS = {
    "cooling.pump-body": {"build": pump_body},
    "cooling.pump-spindle": {"build": pump_spindle},
    "cooling.pump-gasket": {"build": pump_gasket},
    "cooling.pump-bolt": {"build": bolt("5/16")},
    "cooling.pump-bolt-washer": {"build": spring_washer},
    "cooling.pump-pulley": {"build": pump_pulley},
    "cooling.fan": {"build": fan},
    "cooling.fan-screw": {"build": bolt("1/4")},
    "cooling.fan-belt": {"build": fan_belt},
    "cooling.radiator": {"build": radiator},
    "cooling.pressure-cap": {"build": pressure_cap},
    "cooling.drain-tap": {"build": drain_tap},
    "cooling.top-hose": {"build": top_hose},
    "cooling.bottom-hose": {"build": bottom_hose},
    "cooling.hose-clip": {"build": hose_clip},
}
