"""SU type HP electric fuel pump, its bracket and fixings (Haynes Ch 3 Secs 4-8, Fig 3.2 (HP body items 61-75, coil
housing and contact breaker items 1-34), photos none).

The pump parts are drawn in the pump frame: origin on the axis at the body's end face, z out along the axis
(toward the end cover), x forward (car +x), y up (car +z); assemblies/fuel_pump.py places them with
mgb.fuel_supply_layout. The bracket is drawn in the car frame.
"""
from __future__ import annotations

import math

from build123d import Axis, Box, Cylinder, Location, Part, Plane, Polygon, Rot, extrude, fillet

from mgb import fasteners as F, fuel_supply_layout as L, shapes as Sh, underbody_layout as U

IN = 25.4
B0, B1 = L.BODY_S
S0, S1 = L.SANDWICH_S
C0, C1 = L.COIL_S
E0, E1 = L.COVER_S
FLANGE_R = 44.0
SCREW_PCD = 77.0
SCREW_ANGLES = [60.0 * k for k in range(6)]          # clear of the two lugs underneath
BODY_R = 30.0
COIL_R = 32.0
COVER_R = 30.0
LUG_Y = -COIL_R - 12.0                     # underside of the two cast lugs
LUG_X = 0.0


def _l(p, spec):
    p.label = spec.id
    return p


def _holes(part, z0, h, r=2.4):
    for a in SCREW_ANGLES:
        t = math.radians(a)
        part = part - Location((SCREW_PCD / 2 * math.cos(t), SCREW_PCD / 2 * math.sin(t), z0 - 1)) * Sh.cyl(2 * r, h + 2)
    return part


def _ax(s, x=0.0, y=0.0):
    return Location((x, y, s))


def pump_body(spec) -> Part:
    """Item 61: the pump body casting: the pumping chamber flange with six screw holes, the vertical outlet valve
    housing on top, the inlet boss on the rear side and the filter chamber below with its plug boss."""
    b = Sh.revolved([(0, B0), (BODY_R - 4, B0), (BODY_R, B0 + 4), (BODY_R, B1 - 10), (FLANGE_R - 4, B1 - 8),
                     (FLANGE_R, B1 - 6), (FLANGE_R, B1), (0, B1)])
    b = _holes(b, B1 - 8, 8)
    # outlet valve housing on top (local +y), inlet boss on the rear (local -x), filter chamber below
    out_boss = Location((0, 0, L.PORT_S)) * Rot(-90, 0, 0) * Sh.cyl(26.0, 44.0)
    in_boss = Location((0, 0, L.PORT_S)) * Rot(0, -90, 0) * Sh.cyl(22.0, 40.0)
    filt = Location((0, 0, L.PORT_S)) * Rot(90, 0, 0) * Sh.cyl(26.0, 42.0)
    b = b + out_boss + in_boss + filt
    b = b + Location((0, BODY_R - 2.0, (B1 + L.PORT_S) / 2)) * Box(6.0, 10.0, B1 - L.PORT_S - 8)   # rib to the flange
    b = b + Location((0, -BODY_R + 2.0, (B1 + L.PORT_S) / 2)) * Box(6.0, 10.0, B1 - L.PORT_S - 8)
    b = b - Location((0, 30.0, L.PORT_S)) * Rot(-90, 0, 0) * Sh.cyl(18.0, 20.0)          # outlet thread bore
    b = b - Location((-30.0, 0, L.PORT_S)) * Rot(0, -90, 0) * Sh.cyl(13.0, 20.0)          # inlet thread bore
    b = b - Location((0, -32.0, L.PORT_S)) * Rot(90, 0, 0) * Sh.cyl(18.0, 20.0)           # filter plug thread
    b = b - Location((0, 0, B1 - 3.0)) * Sh.cyl(56.0, 4.0)                                # pumping chamber recess
    return _l(b, spec)


def gasket(spec) -> Part:
    """Items 74 (and 35): joint washer either side of the sandwich plate."""
    g = Sh.washer(2 * FLANGE_R, 56.0, spec.nom("thickness"))
    return _l(_holes(g, 0, spec.nom("thickness")), spec)


def sandwich_plate(spec) -> Part:
    """Item 75: the sandwich plate between body and coil housing, the diaphragm's stop in its recessed face."""
    t = S1 - S0
    p = Sh.revolved([(6.0, 0), (FLANGE_R, 0), (FLANGE_R, t), (6.0, t)])
    p = p - Location((0, 0, t - 1.5)) * Sh.cyl(58.0, 2.0)
    return _l(_holes(p, 0, t), spec)


def coil_housing(spec) -> Part:
    """Item 1: the coil housing with its flange, the two cast lugs underneath (Sec 7 para 20: "the two cast lugs on
    the coil housing should be at the bottom"), the earth screw boss and the rocker pedestal seat at the end."""
    h = Sh.revolved([(0, C0), (FLANGE_R, C0), (FLANGE_R, C0 + 6), (COIL_R + 1, C0 + 6), (COIL_R, C0 + 8),
                     (COIL_R, C1 - 6), (COIL_R - 3, C1), (0, C1)])
    h = _holes(h, C0, 6)
    for s in L.LUG_S:
        lug = Location((LUG_X, (LUG_Y - COIL_R + 10) / 2, s)) * Box(22.0, -(COIL_R - 10) - LUG_Y, 14.0)
        lug = fillet(lug.edges().filter_by(Axis.Y), 3.0)
        h = h + lug - Location((LUG_X, LUG_Y - 1, s)) * Rot(-90, 0, 0) * Sh.cyl(6.4, 14.0)
    h = h + Location((COIL_R - 2, 10.0, C0 + 30)) * Box(8.0, 12.0, 12.0)                 # earth screw boss
    for k in range(2):                                                                  # cooling ribs
        h = h + Location((0, 0, C0 + 22 + 28 * k)) * Sh.tube(2 * COIL_R + 3, 2 * COIL_R - 2, 3.0)
    return _l(h, spec)


def end_cover(spec) -> Part:
    """Item 28: moulded end cover over the contact breaker, the terminal stud with its nut and insulating sleeve
    (items 29-32) on the end, the non-return vent valve (34) on top."""
    c = Sh.revolved([(0, E0), (COVER_R, E0), (COVER_R, E1 - 12), (COVER_R - 6, E1 - 3), (COVER_R - 14, E1), (0, E1)])
    c = c + Location((0, -10.0, E1)) * Sh.cyl(5.0, 10.0) + Location((0, -10.0, E1 + 6)) * Sh.cyl(10.0, 3.0)
    c = c + Location((0, -10.0, E1 - 1)) * Sh.cyl(14.0, 9.0)                             # insulating sleeve
    v = Location((0, COVER_R - 3.0, E0 + 18)) * Rot(-90, 0, 0) * (Sh.cyl(9.0, 10.0) + Location((0, 0, 10)) * Sh.cyl(5.0, 6.0))
    return _l(c + v, spec)


def sealing_band(spec) -> Part:
    """Item 33: rubber sealing band over the cover joint, taped (Sec 7 para 28)."""
    w = spec.nom("width")
    return _l(Location((0, 0, E0 - w / 2)) * Sh.tube(2 * COIL_R + 3, 2 * COIL_R + 0.2, w), spec)


def outlet_connection(spec) -> Part:
    """Item 73: outlet connection over the valve cage, hexagon and pipe thread, axis local +y at the port."""
    hx = F.hex_nut("1/2")
    hh = hx.bounding_box().size.Z
    p = Sh.cyl(17.6, 8.0) + Location((0, 0, 8.0)) * hx + Location((0, 0, 8.0 + hh)) * Sh.cyl(11.0, 22.0 - hh)
    p = p - Location((0, 0, -1)) * Sh.cyl(6.0, 40.0)
    return _l(Location((0, 44.0, L.PORT_S)) * Rot(-90, 0, 0) * p, spec)


def inlet_union(spec) -> Part:
    """Item 63: inlet connection on its washer (62), pointing to the rear (local -x)."""
    hx = F.hex_nut("7/16")
    hh = hx.bounding_box().size.Z
    p = Sh.cyl(12.6, 6.0) + Location((0, 0, 6.0)) * hx + Location((0, 0, 6.0 + hh)) * Sh.cyl(10.5, 22.0 - hh)
    p = p - Location((0, 0, -1)) * Sh.cyl(5.0, 40.0)
    return _l(Location((-40.0, 0, L.PORT_S)) * Rot(0, -90, 0) * p, spec)


def filter_plug(spec) -> Part:
    """Item 66: the filter plug under the body, with its washer (65); the gauze filter (64) inside."""
    hx = F.hex_nut("1/2")
    p = Sh.cyl(17.6, 6.0) + Location((0, 0, 6.0)) * hx
    return _l(Location((0, -42.0, L.PORT_S)) * Rot(90, 0, 0) * p, spec)


def body_screw(spec) -> Part:
    """Item 9: one of the six screws through the coil housing flange and sandwich plate into the body."""
    Ln = spec.nom("length")
    s = Sh.revolved([(0, 0), (2.0, 0), (2.0, Ln), (0, Ln)]) + Location((0, 0, Ln)) * Sh.revolved(
        [(0, 0), (3.6, 0), (3.6, 1.0), (2.8, 2.6), (0, 2.8)])
    s = s - Location((0, 0, Ln + 2.2)) * Box(8.0, 0.9, 2.0)
    return _l(s, spec)


# ---------------------------------------------------------------------------------------------------------------
# bracket and mountings (car frame)
# ---------------------------------------------------------------------------------------------------------------
HB = U.HEELBOARD_X
LUG_CAR_Z = L.PUMP_Z + LUG_Y
RUBBER_T = 6.0
BR_T = L.BRACKET_T
BR_TOP_Z = LUG_CAR_Z - RUBBER_T                       # top face of the bracket's leg
LUG_CAR_Y = [L.PUMP_Y0 - s for s in L.LUG_S]
BRACKET_BOLT_Z = BR_TOP_Z + 34.0
BRACKET_BOLT_Y = [L.PUMP_Y0 - 68.0, L.PUMP_Y0 - 112.0]


def bracket(spec) -> Part:
    """Pressed angle bracket (Sec 5 para 5: "the two bolts and spring washers ... remove the pump and bracket"):
    an upright flange on the heelboard's rear face with two bolt holes, a leg under the coil housing's lugs with
    two holes for the mounting screws, turned-down edges and a gusset at each end."""
    y0, y1 = BRACKET_BOLT_Y[0] + 12.0, BRACKET_BOLT_Y[1] - 12.0
    w = y0 - y1
    up = Location((HB - BR_T / 2, (y0 + y1) / 2, (BR_TOP_Z - BR_T + BRACKET_BOLT_Z + 16.0) / 2)) * Box(
        BR_T, w, BRACKET_BOLT_Z + 16.0 - BR_TOP_Z + BR_T)
    leg_x0, leg_x1 = HB, L.PUMP_X - 22.0
    leg = Location(((leg_x0 + leg_x1) / 2, (y0 + y1) / 2, BR_TOP_Z - BR_T / 2)) * Box(leg_x0 - leg_x1, w, BR_T)
    lip = Location((leg_x1 + BR_T / 2, (y0 + y1) / 2, BR_TOP_Z - BR_T - 1.5)) * Box(BR_T, w, 3.0)
    b = up + leg + lip
    for yy in (y0 - BR_T / 2, y1 + BR_T / 2):                                        # gussets
        pl = Plane(origin=(0, yy - BR_T / 2, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        g = extrude(pl * Polygon((HB - BR_T, -(BR_TOP_Z)), (HB - 30.0, -(BR_TOP_Z)), (HB - BR_T, -(BR_TOP_Z + 26.0)),
                                 align=None), BR_T, dir=(0, 1, 0))
        b = b + g
    for yy in BRACKET_BOLT_Y:
        b = b - Location((HB - BR_T - 1, yy, BRACKET_BOLT_Z)) * Rot(0, 90, 0) * Sh.cyl(8.4, BR_T + 2)
    for yy in LUG_CAR_Y:
        b = b - Location((L.PUMP_X, yy, BR_TOP_Z - BR_T - 1)) * Sh.cyl(6.6, BR_T + 2)
    return _l(b, spec)


def rubber_mounting(spec) -> Part:
    """The rubber block between each lug and the bracket (MGOC: "the rubber mounting block (grommet) between the
    pump and its mounting bracket"): a bobbin with a waist, drawn at the origin, axis z, base on z = 0."""
    t = spec.nom("thickness")
    m = Sh.revolved([(3.4, 0), (10.0, 0), (10.0, 1.2), (8.0, 2.0), (8.0, t - 2.0), (10.0, t - 1.2), (10.0, t), (3.4, t)])
    return _l(m, spec)


def screw(size, length_in):
    def build(spec) -> Part:
        return _l(F.hex_bolt(size, length_in), spec)
    return build


def spring_washer(spec) -> Part:
    od, idd, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, idd, t)
    return _l(w - Location((od / 2 - 1.0, 0, t / 2)) * Box(od / 2, 0.8, t + 2), spec)


PARTS = {
    "fuel.pump.body": {"build": pump_body},
    "fuel.pump.gasket": {"build": gasket},
    "fuel.pump.sandwich-plate": {"build": sandwich_plate},
    "fuel.pump.coil-housing": {"build": coil_housing},
    "fuel.pump.end-cover": {"build": end_cover},
    "fuel.pump.sealing-band": {"build": sealing_band},
    "fuel.pump.outlet-connection": {"build": outlet_connection},
    "fuel.pump.inlet-union": {"build": inlet_union},
    "fuel.pump.filter-plug": {"build": filter_plug},
    "fuel.pump.body-screw": {"build": body_screw},
    "fuel.pump.bracket": {"build": bracket},
    "fuel.pump.rubber-mounting": {"build": rubber_mounting},
    "fuel.pump.mounting-screw": {"build": screw("1/4", 0.75)},
    "fuel.pump.bracket-bolt": {"build": screw("5/16", 0.75)},
    "fuel.pump.spring-washer": {"build": spring_washer},
}
