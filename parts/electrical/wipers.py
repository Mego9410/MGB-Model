"""Windscreen wipers, single speed Lucas DR3A: motor and gearbox on its bracket, the rack in its
casings, two wheelboxes with their spindles, nuts and rubber washers, the arms and blades.
Haynes Ch 10 Sec 52-55 and Fig 10.17 (printed p183), specs printed p162. Item numbers are
Fig 10.17. Positions: mgb/body_layout.py (WIPER_*).
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import body_layout as BL, elec_shapes as X, fasteners as F, poly2d as P2, shapes as Sh
from mgb.elec_shapes import box, hull_xy, label, polar, rev, tryfillet, xc, yc, zc

MX, MY, MZ = BL.WIPER_MOTOR
GEAR_R = 42.0
OUTLET = (MX + 10.0, MY - 70.0, MZ + 8.0)          # where the rack leaves the crosshead guide (car frame)
SP = BL.WIPER_SPINDLES                              # [left, right]
AX = BL.WIPER_AXIS
WB_DROP = 30.0                                      # wheelbox centre below the spindle top's seat
TUBE_Z = SP[0][2] - WB_DROP


def _wb_centre(k):
    x, y, z = SP[k]
    return (x - AX[0] * WB_DROP, y, z - AX[2] * WB_DROP)


def motor(spec) -> Part:
    """Items 1-6: the die-cast gearbox body with its round gear chamber, the crosshead guide
    channel running to the rack outlet, the cover plate with four screws and the parking
    switch (6); the field coil yoke (5) under it with the commutator end bracket and its two
    through-bolts. Built in the car frame, gearbox flat on top, yoke hanging below."""
    t = 16.0
    gb = hull_xy([(0.0, 0.0, GEAR_R + 4.0), (-4.0, -70.0, 15.0), (14.0, -70.0, 12.0)], 0.0, t)
    gb = tryfillet(gb, gb.edges().filter_by(Axis.Z), 4.0)
    cover = X.poly_xy(P2.hull(P2.circle_pts(0.0, 0.0, GEAR_R + 2.0, 32) + P2.circle_pts(0.0, -62.0, 10.0, 12)), t, t + 3.0)
    for x, y in ((GEAR_R - 2.0, 18.0), (-GEAR_R + 2.0, 18.0), (GEAR_R - 6.0, -26.0), (-GEAR_R + 6.0, -26.0)):
        cover = cover + zc(3.0, t + 3.0, t + 5.0, x, y)
    sw = zc(24.0, t + 3.0, t + 12.0, 6.0, 8.0) + zc(18.0, t + 12.0, t + 15.0, 6.0, 8.0)   # parking (limit) switch
    sw = sw - box(4.0, 8.0, -12.0, 28.0, t + 13.0, t + 16.0)
    yoke = box(-30.0, 30.0, 2.0, 56.0, -96.0, 1.0)                    # field coil yoke under the gearbox
    yoke = tryfillet(yoke, yoke.edges().filter_by(Axis.Z), 9.0)
    endb = rev([(0, -104.0), (16.0, -104.0), (22.0, -96.0), (0, -96.0)]).moved(Location((0, 29.0, 0)))
    m = gb + cover + sw + yoke + endb
    for x in (-18.0, 18.0):
        m = m + zc(2.2, -100.0, -94.0, x, 29.0)
    m = m + Location((10.0, -70.0, t / 2)) * Rot(90, 0, 0) * zc(7.0, 0.0, 12.0)      # rack outlet boss and nut
    m = m + Location((10.0, -82.0, t / 2)) * Rot(90, 0, 0) * extrude(RegularPolygon(9.0, 6), 8.0)
    for k, (x, y) in enumerate(((-GEAR_R - 2.0, 20.0), (GEAR_R + 2.0, 20.0), (0.0, GEAR_R + 4.0))):
        m = m + zc(6.0, 0.0, t, x, y) - zc(2.6, -1, t + 1, x, y)       # bracket screw bosses
    loc = Location((MX - 10.0, MY + 70.0, MZ + 8.0 - t / 2))
    return label(loc * m, spec)


def bracket(spec) -> Part:
    """Item 8: the motor bracket, bolted to the scuttle side by three screws (9-11; Sec 54
    para 1) with the motor hung from it."""
    t = spec.nom("thickness")
    x0, y0, z0 = MX - 10.0, MY + 70.0, MZ + 8.0 + 8.0 + 3.0
    plate = hull_xy([(-GEAR_R - 2.0, 20.0, 9.0), (GEAR_R + 2.0, 20.0, 9.0), (0.0, GEAR_R + 4.0, 9.0), (0.0, 80.0, 18.0)], 0.0, t)
    for x, y in ((-GEAR_R - 2.0, 20.0), (GEAR_R + 2.0, 20.0), (0.0, GEAR_R + 4.0)):
        plate = plate - zc(2.8, -1, t + 1, x, y)
    leg = box(-24.0, 24.0, 80.0, 80.0 + t, 0.0, 60.0)
    for x in (-14.0, 14.0):
        leg = leg - (Location((x, 80.0, 40.0)) * Rot(90, 0, 0) * zc(3.3, -5, 5))
    return label(Location((x0, y0, z0)) * (plate + leg), spec)


def rack_casing(which):
    """Items 13, 14 and 15: the outer casings the rack runs in, from the motor to the left
    wheelbox, between the wheelboxes, and the extension beyond the right one."""
    def build(spec) -> Part:
        d = spec.nom("outside_diameter")
        a, b = _wb_centre(0), _wb_centre(1)
        if which == "motor":
            ox, oy, oz = OUTLET
            pts = [(ox, oy - 12.0, oz), (ox, oy - 60.0, oz), (a[0] - 20.0, a[1] + 120.0, a[2] - 40.0), (a[0], a[1] + 30.0, a[2]),
                   (a[0], a[1] + 14.0, a[2])]
        elif which == "between":
            pts = [(a[0], a[1] - 14.0, a[2]), (a[0], a[1] - 60.0, a[2] - 6.0), (b[0], b[1] + 60.0, b[2] - 6.0),
                   (b[0], b[1] + 14.0, b[2])]
        else:
            pts = [(b[0], b[1] - 14.0, b[2]), (b[0], b[1] - 40.0, b[2] - 3.0), (b[0] + 10.0, b[1] - 170.0, b[2] - 20.0)]
        c = X.cable(pts, d, 60.0, hollow=1.0)
        return label(c, spec)
    return build


def wheelbox(spec) -> Part:
    """Item 16: wheelbox under the spindle, the casings clamped in its two entries by the
    cover plate screws (21; Sec 54 para 2). Built at the left spindle along its axis."""
    w = Box(26.0, 34.0, 22.0)
    w = tryfillet(w, w.edges().filter_by(Axis.Y), 3.0)
    w = w + Rot(90, 0, 0) * zc(6.5, -26.0, 26.0)                      # casing entries either side
    w = w + Location((0, 0, 11.0)) * zc(9.0, 0.0, 10.0)               # spindle boss up through the scuttle
    w = w + Location((0, 0, -12.5)) * Box(30.0, 36.0, 3.0)            # cover plate
    for x, y in ((-11.0, -14.0), (11.0, 14.0)):
        w = w + Location((x, y, -14.0)) * zc(2.8, -3.0, 0.0)
    return label(_wb_loc(0) * w, spec)


def _wb_loc(k):
    c = _wb_centre(k)
    return Plane(origin=c, x_dir=(AX[2], 0, -AX[0]), z_dir=AX).location


def spindle(spec) -> Part:
    """Item 17: spindle and gear; the gear meshing the rack in the wheelbox, the splined top
    for the arm, with the rubber tube (18), the rubber washer (20) and the nut (19) on the
    scuttle."""
    s = zc(12.0, -4.0, 4.0) + zc(4.0, 0.0, WB_DROP + 30.0)
    for k in range(20):
        s = s + (Rot(0, 0, 18.0 * k) * box(11.5, 13.5, -1.0, 1.0, -4.0, 4.0))
    s = s + zc(4.6, WB_DROP + 18.0, WB_DROP + 28.0)                   # splines
    s = s + zc(9.5, WB_DROP - 2.0, WB_DROP + 0.5)                     # rubber washer seat
    s = s + Location((0, 0, WB_DROP + 0.5)) * extrude(RegularPolygon(9.5, 6), 6.0)   # wheelbox nut
    s = s + zc(7.5, WB_DROP + 6.5, WB_DROP + 16.0)                    # bush
    return label(_wb_loc(0) * s, spec)


def arm(spec) -> Part:
    """Item 22: arm, a spring-loaded pressed steel arm on the splined spindle (pull-off early
    type, Sec 52 para 3), lying along the base of the screen in the parked position."""
    L = spec.nom("length")
    head = zc(9.0, 0.0, 16.0) + Location((0, 0, 8.0)) * Box(22.0, 18.0, 14.0) - zc(4.6, -1, 10.0)
    head = tryfillet(head, head.edges().filter_by(Axis.Z), 3.0)
    channel = box(-6.0, 6.0, 0.0, 70.0, 10.0, 16.0) - box(-4.6, 4.6, 6.0, 72.0, 9.0, 14.6)
    rod = X.cable([(0, 68.0, 13.0), (0, 120.0, 11.0), (0, L, 8.0)], 5.0, 20.0)
    end = X.cable([(0, L - 1.0, 8.0), (0, L + 6.0, 6.0), (0, L + 6.0, 1.0)], 4.0, 3.0)
    a = head + channel + rod + end
    return label(Location((0, 0, WB_DROP + 28.0)) * a, spec)


def blade(spec) -> Part:
    """Item 23 and rubber 24: the blade's frame of bridges and claws holding the rubber, with
    the centre clip the arm's end engages (Sec 52 para 2). Lies along the arm."""
    L = spec.nom("length")
    rub = box(-1.5, 1.5, -L / 2, L / 2, -8.0, 0.0) + box(-3.0, 3.0, -L / 2, L / 2, -1.0, 1.5)
    main = box(-5.0, 5.0, -L / 4, L / 4, 7.0, 10.0) + box(-5.0, -3.8, -L / 4, L / 4, 2.0, 10.0) + box(3.8, 5.0, -L / 4, L / 4, 2.0, 10.0)
    sub = None
    for s in (-1, 1):
        y0 = s * L * 0.30
        b = box(-4.0, 4.0, y0 - L * 0.17, y0 + L * 0.17, 4.0, 6.5)
        for yy in (y0 - L * 0.15, y0 + L * 0.15):
            b = b + box(-4.0, 4.0, yy - 3.0, yy + 3.0, 0.5, 4.0)           # claws
        b = b + box(-2.0, 2.0, y0 - 3.0, y0 + 3.0, 6.0, 8.0)
        sub = b if sub is None else sub + b
    clip = box(-5.0, 5.0, -8.0, 8.0, 10.0, 12.0)
    return label(rub + main + sub + clip, spec)


PARTS = {
    "electrical.wipers.motor": {"build": motor},
    "electrical.wipers.bracket": {"build": bracket},
    "electrical.wipers.casing-motor": {"build": rack_casing("motor")},
    "electrical.wipers.casing-between": {"build": rack_casing("between")},
    "electrical.wipers.casing-extension": {"build": rack_casing("extension")},
    "electrical.wipers.wheelbox": {"build": wheelbox},
    "electrical.wipers.spindle": {"build": spindle},
    "electrical.wipers.arm": {"build": arm},
    "electrical.wipers.blade": {"build": blade, "probes": {"length": lambda p: p.bounding_box().size.Y}},
}
