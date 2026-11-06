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
    x0, y0, z0 = MX - 10.0, MY + 70.0, MZ + 8.0 - 8.0 - t       # under the gearbox, the yoke through its opening
    plate = hull_xy([(-GEAR_R - 2.0, 20.0, 9.0), (GEAR_R + 2.0, 20.0, 9.0), (0.0, GEAR_R + 4.0, 9.0), (0.0, 80.0, 18.0)], 0.0, t)
    plate = plate - box(-31.5, 31.5, 1.0, 57.0, -1.0, t + 1.0)
    for x, y in ((-GEAR_R - 2.0, 20.0), (GEAR_R + 2.0, 20.0), (0.0, GEAR_R + 4.0)):
        plate = plate - zc(2.8, -1, t + 1, x, y)
    leg = box(-24.0, 24.0, 80.0, 80.0 + t, 0.0, 60.0)
    for x in (-14.0, 14.0):
        leg = leg - (Location((x, 80.0, 40.0)) * Rot(90, 0, 0) * zc(3.3, -5, 5))
    return label(Location((x0, y0, z0)) * (plate + leg), spec)


def rack_casing(which):
    """Items 13, 14 and 15: the outer casings the rack runs in, from the motor to the left
    wheelbox, between the wheelboxes, and the extension beyond the right one. QA fix round 1: re-routed to the
    spindles' measured positions (BL.WIPER_SPINDLE_XY): from the motor's outlet the casing runs inboard, climbs in an
    S-bend and enters the left wheelbox from outboard, square to it."""
    def build(spec) -> Part:
        d = spec.nom("outside_diameter")
        a, b = _wb_centre(0), _wb_centre(1)
        if which == "motor":
            ox, oy, oz = OUTLET
            ym = (oy - 12.0 + a[1] + 14.0) / 2
            pts = [(ox, oy - 12.0, oz), (ox, ym, oz), ((ox + a[0]) / 2, ym, a[2]), (a[0], a[1] + 14.0, a[2])]
            c = X.cable(pts, d, 28.0, hollow=1.0)
        elif which == "between":
            pts = [(a[0], a[1] - 14.0, a[2]), (a[0], a[1] - 40.0, a[2]), (a[0], a[1] - 90.0, a[2] - 6.0), (b[0], b[1] + 90.0, b[2] - 6.0),
                   (b[0], b[1] + 40.0, b[2]), (b[0], b[1] + 14.0, b[2])]
            c = X.cable(pts, d, 60.0, hollow=1.0)
        else:
            pts = [(b[0], b[1] - 14.0, b[2]), (b[0], b[1] - 40.0, b[2]), (b[0] + 10.0, b[1] - 170.0, b[2] - 20.0)]
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
    w = w - zc(13.6, -5.0, 5.0) - zc(4.4, -6.0, 23.0)                     # gear chamber and spindle bore
    w = w - Rot(90, 0, 0) * zc(4.1, -27.0, 27.0)                       # casing entries, the rack passing through
    return label(_wb_loc(0) * w, spec)


def _wb_loc(k):
    c = _wb_centre(k)
    return Plane(origin=c, x_dir=(AX[2], 0, -AX[0]), z_dir=AX).location


# QA fix round 1 (Oliver's keyframes kf195-202, kf076): the spindle shows only as a low boss on the scuttle - the rubber
# washer, a chrome bush and nut - with the chrome arm head pushed down over its splines; P10 had a 34 mm post.
SEAT = WB_DROP                                      # the skin, along the spindle axis from the wheelbox centre
HEAD = (SEAT + 8.0, SEAT + 21.0)                    # arm head's underside and top (kf202: a low chunky head)


def spindle(spec) -> Part:
    """Item 17: spindle and gear; the gear meshing the rack in the wheelbox, the splined top
    for the arm, with the rubber tube (18), the rubber washer (20) and the nut (19) on the
    scuttle, then the chrome bush; the splines stop inside the arm head."""
    s = zc(11.0, -4.0, 4.0) + zc(4.0, 0.0, SEAT + 19.0)
    for k in range(20):
        s = s + (Rot(0, 0, 18.0 * k) * box(10.5, 13.0, -1.0, 1.0, -4.0, 4.0))
    s = s + zc(4.6, SEAT + 9.0, SEAT + 18.0)                       # splines (inside the arm head)
    s = s + zc(10.0, SEAT - 1.0, SEAT + 1.0)                       # rubber washer on the scuttle
    s = s + Location((0, 0, SEAT + 1.0)) * extrude(RegularPolygon(9.0, 6), 3.5)   # wheelbox nut
    s = s + rev([(0, SEAT + 4.5), (8.0, SEAT + 4.5), (8.0, SEAT + 6.5), (6.5, SEAT + 8.0), (0, SEAT + 8.0)])   # bush
    return label(_wb_loc(0) * s, spec)


ARM_REACH = 212.0                                   # spindle to the blade's centre across the car (kf201: the left
                                                    # blade's centre ~65 mm left of the screen's centre rod)
BLADE_UP = 0.12                                     # blade rubber's line up the glass (kf195, kf201: just above the rail)


def blade_frame(k):
    """(origin on the glass at the blade's centre, unit y along the blade, unit outward glass normal) for spindle k;
    the blade follows the glass (mgb.body_shell_layout.screen_pt) wherever the screen sits."""
    from mgb import body_shell_layout as SL
    import numpy as np
    y = SP[k][1] + BL.WIPER_PARK_SIDE * ARM_REACH
    p = np.array(SL.screen_pt(y, BLADE_UP))
    dy = np.array(SL.screen_pt(y + 5.0, BLADE_UP)) - np.array(SL.screen_pt(y - 5.0, BLADE_UP))
    dv = np.array(SL.screen_pt(y, BLADE_UP + 0.02)) - np.array(SL.screen_pt(y, BLADE_UP - 0.02))
    n = np.cross(dy, dv)
    n = n / np.linalg.norm(n) * (1.0 if n[0] > 0 else -1.0)
    ty = dy / np.linalg.norm(dy)
    return p, ty, n


def blade_loc(k):
    """Location of blade k: rubber's edge on the glass, frame square to it."""
    import numpy as np
    p, ty, n = blade_frame(k)
    return Plane(origin=tuple(p + n * 8.0), x_dir=tuple(np.cross(ty, n)), z_dir=tuple(n)).location


def arm(spec, side=1) -> Part:
    """Item 22: arm, the early push-on type (Sec 52 para 3) in chrome (kf195-202): a chunky head over the spindle's
    splines with its cross-head clamp screw on top and the rounded pivot end, the spring channel running from the
    head, then the flat stainless rod up onto the glass to the blade's centre clip. Built for the left (side 1) or
    right (side -1) spindle in the car frame, parked toward the off side."""
    import numpy as np
    k = 0 if side > 0 else 1
    wb = _wb_loc(0) if k == 0 else Location((0, SP[1][1] - SP[0][1], 0)) * _wb_loc(0)
    park = BL.WIPER_PARK_SIDE
    head = box(-9.0, 9.0, -10.0, 22.0, HEAD[0], HEAD[1])
    head = tryfillet(head, head.edges().filter_by(Axis.Z), 6.0)
    head = tryfillet(head, head.edges().group_by(Axis.Z)[-1], 2.5)
    head = head - zc(1.6, HEAD[1] - 1.0, HEAD[1] + 1.0) - box(-0.5, 0.5, -3.0, 3.0, HEAD[1] - 0.8, HEAD[1] + 1) \
        - box(-3.0, 3.0, -0.5, 0.5, HEAD[1] - 0.8, HEAD[1] + 1)                 # cross-head clamp screw
    head = head + Location((0, -10.0, (HEAD[0] + HEAD[1]) / 2)) * Rot(90, 0, 0) * zc(5.5, -1.0, 2.5)   # pivot end
    if park < 0:
        head = Rot(0, 0, 180) * head
    head = wb * head
    p, ty, n = blade_frame(k)
    clip = p + n * 22.0                                        # over the blade's centre clip
    rp = (wb * Location((0, park * 20.0, (HEAD[0] + HEAD[1]) / 2))).position
    root = np.array((rp.X, rp.Y, rp.Z))
    d = clip - root
    L = float(np.linalg.norm(d))
    u = d / L
    mid = root + u * min(70.0, 0.35 * L)
    chan = X.cable([tuple(root), tuple(mid)], 8.0, 10.0)
    rod = X.cable([tuple(mid - u * 4.0), tuple(clip - u * 6.0), tuple(clip - n * 6.0)], 4.6, 6.0)
    return label(head + chan + rod, spec)


def blade(spec) -> Part:
    """Item 23 and rubber 24: the blade's frame of bridges and claws holding the rubber, with
    the centre clip the arm's end engages (Sec 52 para 2). Lies on the glass along the screen."""
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


def washer_jet(spec) -> Part:
    """Windscreen washer jet (QA fix round 1; kf195, kf199, kf202, triangulated at x -535, y +355): a small chrome
    dome with its nozzle turned toward the screen, on a threaded stem through the scuttle with the tube's spigot under
    it. Built about its own axis; jet_loc places it square to the skin at BL.WASHER_JETS."""
    d = spec.nom("diameter")
    j = rev([(0, -0.5), (d / 2, -0.5), (d / 2, 1.5), (d / 2 - 1.5, 4.5), (d / 4, 7.0), (0, 7.5)])
    j = j + Location((-1.5, 0, 5.0)) * Rot(0, -60, 0) * zc(2.0, 0.0, 4.5)     # nozzle toward the screen (-x)
    j = j - Location((-1.5, 0, 5.0)) * Rot(0, -60, 0) * zc(0.6, 1.0, 5.0)
    j = j + zc(3.0, -16.0, -0.5) + zc(1.8, -30.0, -16.0)                      # stem and tube spigot
    return label(j, spec)


def jet_loc(k):
    x, y, z = BL.WASHER_JETS[k]
    _, nrm = BL.skin_point(x, y)
    return Plane(origin=(x, y, z), x_dir=(nrm[2], 0.0, -nrm[0]), z_dir=nrm).location


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
    "electrical.wipers.washer-jet": {"build": washer_jet},
}
