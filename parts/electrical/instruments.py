"""Instruments, warning lamps and switches in the facia, the speedometer cable, the oil pressure
gauge pipe and the temperature gauge's capillary and thermal transmitter.
Haynes Ch 10 Sec 40, 45-48, Fig 10.9 (printed p176), Fig 10.26 (early wiring); Ch 1 Sec 6 paras
5, 8, 13 (gauge pipe, thermal transmitter); Ch 2 Sec 15 (capillary temperature gauge);
Ch 12 Sec 46 (early instruments). The facia panel itself is P11 (body), built round the
positions in mgb.body_layout (FACIA_X, INSTRUMENTS, WARNING_LAMPS, SWITCHES); the warning lamps are lenses on the
tachometer and speedometer dials, lit from bulb holders in the cases (Fig 10.26).

Facia items are built in the facia frame: local z toward the driver (car -x) from the facia's
rear face, local x up, local y the car's left; the assembly places each with one Location.
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import body_layout as BL, elec_shapes as X, electrical_layout as E, fasteners as F, shapes as Sh
from mgb.elec_shapes import box, hull_xy, label, polar, rev, sector, tryfillet, xc, yc, zc

SIZES = {"large": 80.0, "small": 52.0}       # case diameters
DEPTH = {"large": 72.0, "small": 50.0}


def _r(size):
    return SIZES[size] / 2


# ---- instrument parts -------------------------------------------------------------------------
def case(size, kind):
    def build(spec) -> Part:
        """Instrument case behind the facia: the drawn can, the clamping bracket on its two
        studs with the knurled nuts (Sec 46), the bulb holders, and at the back the drive or
        connections: speedometer cable boss, tachometer pulse lead, the oil pressure pipe union
        and temperature capillary of the dual gauge, the fuel gauge terminals."""
        r = _r(size)
        d = DEPTH[size]
        c = rev([(r - 1.5, -2.0), (r, -2.0), (r, -d + 6.0), (r - 6.0, -d), (0, -d), (0, -d + 2.0), (r - 1.5, -d + 2.0)])
        c = c + zc(r - 1.5, -d, -d + 3.0)
        br = box(-6.0, 6.0, -r - 14.0, r + 14.0, -d * 0.55 - 3.0, -d * 0.55)          # clamping bracket
        for s in (-1, 1):
            br = br + zc(2.0, -d * 0.55 - 12.0, -2.0, 0.0, s * (r + 9.0))
            br = br + Location((0, s * (r + 9.0), -d * 0.55 - 9.0)) * extrude(RegularPolygon(5.5, 18), 6.0)
        c = c + br
        holders = [E.BULB_HOLDERS["panel"]]                                            # bulb holders: panel lamp, and in
        if kind in ("speedometer", "tachometer"):                                      # the two big dials the warning lamp
            holders += [E.BULB_HOLDERS["warning"], E.BULB_HOLDERS["arrow"]]            # and the indicator arrow (P10b)
        for a in holders:
            x, y = polar(r - 8.0, a)
            c = c + zc(5.5, -d - 18.0, -d + 1.0, x, y) + zc(6.5, -d - 3.0, -d + 1.0, x, y)
        if kind == "speedometer":
            c = c + zc(9.0, -d - 14.0, -d + 1.0, 0.0, 0.0) + zc(11.0, -d - 26.0, -d - 14.0)   # cable boss, knurled nut
            for k in range(14):
                a = 360.0 * k / 14
                x, y = polar(11.0, a)
                c = c - zc(0.8, -d - 25.0, -d - 15.0, x, y)
        elif kind == "tachometer":
            c = c + zc(6.0, -d - 10.0, -d + 1.0, 8.0, 0.0)
            c = c + X.cable([(8.0, 0.0, -d - 9.0), (8.0, 0.0, -d - 30.0), (24.0, 8.0, -d - 40.0), (8.0, 16.0, -d - 30.0),
                             (8.0, 16.0, -d - 2.0)], 3.0, 6.0)                                     # pulse lead loop (Fig 10.14)
            for y in (-12.0, 24.0):                                                     # pulse lead's two pins (P10b harness)
                c = c + zc(3.2, -d - 4.0, -d + 1.0, -6.0, y) + zc(1.0, -d - 15.0, -d - 3.9, -6.0, y)
        elif kind == "dual-gauge":
            c = c + zc(6.0, -d - 12.0, -d + 1.0, 6.0, 8.0)                                     # oil pipe union
            c = c + Location((6.0, 8.0, -d - 12.0)) * extrude(RegularPolygon(7.0, 6), 6.0)
            c = c + zc(4.0, -d - 8.0, -d + 1.0, -6.0, -8.0)                                    # capillary gland
        else:
            for y in (-8.0, 8.0):
                c = c + zc(2.0, -d - 12.0, -d + 1.0, 6.0, y)
                c = c + zc(4.0, -d - 4.0, -d + 1.0, 6.0, y)
        return label(c, spec)
    return build


def bezel(size):
    def build(spec) -> Part:
        """Chrome bezel: a rolled ring that holds the glass and seats on the facia."""
        r = _r(size)
        b = rev([(r - 4.0, 6.0), (r - 1.0, 7.0), (r + 3.0, 5.5), (r + 4.5, 2.0), (r + 5.0, 0.0), (r + 2.0, 0.0), (r + 2.0, -2.0),
                 (r, -2.0), (r, 1.0), (r - 1.0, 4.0), (r - 4.0, 4.6)])
        return label(b, spec)
    return build


def glass(size):
    def build(spec) -> Part:
        r = _r(size)
        return label(X.lens_dome(r - 1.0, 2.0, 3.6), spec)
    return build


# ---- dial faces ----------------------------------------------------------------------------------------------------
# The Smiths dials of a 1963 MGB as on Oliver's car (kf121, kf148 zoomed): black faces printed in white.
#   speedometer 0-120 MPH over 270 deg (0 at the lower left, 60 at the top), figures every 10, graduations every 2 and
#     10; MPH over the trip window above the centre, the total odometer below it, HIGH BEAM at the foot;
#   tachometer 0-70 x100 RPM over 270 deg, figures every 5, graduations every 1 and 5; RPM and X 100 above the centre,
#     an amber-and-red wedge inside the scale from 5000 to 6300, IGNITION at the foot;
#   dual gauge: OIL 0-100 psi over the top half (figures every 20), WATER 90-230 F round the bottom half (90 120 160
#     190 212 230), one pivot at the centre;
#   fuel gauge: FUEL under the maker's mark, E 1/4 1/2 3/4 F across the middle on a shallow arc, the needle pivoted
#     below the centre.
# Dial geometry is drawn in the driver's view (u to the driver's right, v up) and turned into the facia frame (local x
# up, y the car's left, z toward the driver).
PRINT_T = 0.25                                        # print stands this proud of the face (so it renders as ink)
FUEL_PIVOT = 0.45                                     # fuel needle pivot above the centre (fraction of the face radius):
FUEL_SWING = 52.0                                     # the needle hangs and swings over a scale arc below it


def _uv(p):
    """Driver's view (u right, v up) -> facia frame."""
    return Rot(0, 0, -90) * p


def _txt(s, size, u, v, rot=0.0):
    """Text centred at (u, v), its baseline turned rot deg anticlockwise, on the face."""
    from build123d import Align, Text
    t = extrude(Text(s, font_size=size, align=(Align.CENTER, Align.CENTER)), PRINT_T, dir=(0, 0, 1))
    return Location((u, v, 1.0)) * Rot(0, 0, rot) * t


def _tick(theta, r0, r1, w):
    """Graduation from radius r0 to r1 at theta deg clockwise from up."""
    return Rot(0, 0, -theta) * box(-w / 2, w / 2, r0, r1, 1.0, 1.0 + PRINT_T)


def _arc(theta0, theta1, r0, r1, n=40):
    """Annular sector (clockwise from theta0 to theta1, from up) on the face."""
    pts = [(r1 * math.sin(math.radians(theta0 + (theta1 - theta0) * k / n)), r1 * math.cos(math.radians(theta0 + (theta1 - theta0) * k / n)))
           for k in range(n + 1)]
    pts += [(r0 * math.sin(math.radians(theta1 - (theta1 - theta0) * k / n)), r0 * math.cos(math.radians(theta1 - (theta1 - theta0) * k / n)))
            for k in range(n + 1)]
    return extrude(Polygon(*pts, align=None), PRINT_T, dir=(0, 0, 1)).moved(Location((0, 0, 1.0)))


def _scale_theta(kind, v):
    """Clockwise angle from up of value v on the dial's scale."""
    if kind == "speedometer":
        return -135.0 + 270.0 * v / 120.0
    if kind == "tachometer":
        return -135.0 + 270.0 * v / 70.0
    if kind == "oil":
        return -80.0 + 160.0 * v / 100.0
    if kind == "water":                                # 90 at the left round the bottom to 230 at the right
        return -100.0 - 160.0 * (v - 90.0) / 140.0
    raise KeyError(kind)


def _windows(r):
    """Trip (above the centre) and total (below) odometer windows of the speedometer, (u0, u1, v0, v1)."""
    return [(-10.0, 10.0, 0.20 * r, 0.20 * r + 6.5), (-13.0, 13.0, -0.36 * r, -0.36 * r + 6.5)]


def dial(size, kind):
    def build(spec) -> Part:
        """Dial: the black face (its print is the -print part), the speedometer's odometer windows."""
        r = _r(size)
        d = zc(r - 1.5, 0.0, 1.0)
        if kind == "speedometer":
            for u0, u1, v0, v1 in _windows(r):
                d = d - _uv(box(u0, u1, v0, v1, -1.0, 2.0))
        return label(d, spec)
    return build


def _print(size, kind):
    r = _r(size) - 1.5                                # face radius
    out = []
    ro = r - 1.2                                      # graduations' outer edge
    if kind in ("speedometer", "tachometer"):
        top, step_f, minor, mid = (120, 10, 2, 10) if kind == "speedometer" else (70, 5, 1, 5)
        v = 0
        while v <= top + 1e-6:
            th = _scale_theta(kind, v)
            major = abs(v / mid - round(v / mid)) < 1e-6
            out.append(_tick(th, ro - (5.0 if major else 2.4), ro, 1.0 if major else 0.55))
            v += minor
        out.append(_arc(-135.5, 135.5, ro - 0.35, ro + 0.35, 90))           # the scale's outer line
        fs = 4.6 if kind == "speedometer" else 4.4
        rf = ro - 9.5
        for v in range(step_f, top + 1, step_f):
            th = math.radians(_scale_theta(kind, v))
            out.append(_txt(str(v), fs, rf * math.sin(th), rf * math.cos(th)))
        if kind == "speedometer":
            out.append(_txt("MPH", 3.4, 0.0, 0.20 * r + 11.0))
            out.append(_txt("SMITHS", 1.8, 0.0, -0.36 * r - 4.0))
            out.append(_txt("HIGH BEAM", 2.4, 0.0, -0.80 * r))
            for u0, u1, v0, v1 in _windows(r):                                # window frames
                out.append(box(u0 - 0.8, u1 + 0.8, v0 - 0.8, v1 + 0.8, 1.0, 1.0 + PRINT_T) - box(u0, u1, v0, v1, 0.0, 2.0))
        else:
            out.append(_txt("RPM", 3.6, 0.0, 0.30 * r))
            out.append(_txt("X 100", 2.2, 0.0, 0.30 * r - 4.6))
            out.append(_txt("SMITHS", 1.8, 0.0, -0.42 * r))
            out.append(_txt("IGNITION", 2.4, 0.0, -0.80 * r))
    elif kind == "dual-gauge":
        for v in range(0, 101, 10):
            out.append(_tick(_scale_theta("oil", v), ro - (3.2 if v % 20 == 0 else 1.8), ro, 0.7 if v % 20 == 0 else 0.45))
        for v in range(90, 231, 10):
            out.append(_tick(_scale_theta("water", v), ro - 2.2, ro, 0.5))
        for v in (90, 120, 160, 190, 212, 230):
            out.append(_tick(_scale_theta("water", v), ro - 3.2, ro, 0.7))
        rf = ro - 6.6
        for v in range(0, 101, 20):
            th = math.radians(_scale_theta("oil", v))
            out.append(_txt(str(v), 2.7, rf * math.sin(th), rf * math.cos(th)))
        for v in (90, 120, 160, 190, 212, 230):
            th = math.radians(_scale_theta("water", v))
            out.append(_txt(str(v), 2.5, rf * math.sin(th), rf * math.cos(th)))
        out.append(_txt("OIL", 2.6, 0.0, 6.0))
        out.append(_txt("WATER", 2.6, 0.0, -6.5))
    else:                                             # fuel gauge
        pv = FUEL_PIVOT * r
        for k, s_ in enumerate(("E", "1/4", "1/2", "3/4", "F")):
            th = 180.0 + FUEL_SWING - FUEL_SWING / 2 * k
            t = math.radians(th)
            out.append(Location((0, pv, 0)) * _tick(th, 0.60 * r, 0.72 * r, 0.9 if k in (0, 2, 4) else 0.6))
            if s_ != "1/2":
                rl = 0.86 * r if len(s_) == 1 else 0.90 * r
                out.append(_txt(s_, 3.4 if len(s_) == 1 else 2.3, rl * math.sin(t), pv + rl * math.cos(t)))
        out.append(_txt("FUEL", 3.0, 0.0, 0.24 * r))
        out.append(_txt("SMITHS", 1.6, 0.0, 0.70 * r))
    return out


def dial_print(size, kind):
    def build(spec) -> Part:
        """White print on the dial: graduations, figures and legends (see the dial notes above)."""
        from build123d import Compound
        c = Compound(children=[_uv(p) for p in _print(size, kind)])
        c.label = spec.id
        return c
    return build


def tach_sector(colour):
    def build(spec) -> Part:
        """The tachometer's warning wedge inside the scale: amber from 5000 to 5500 rpm, red from 5500 to 6300."""
        r = _r("large") - 1.5
        a, b = (50.0, 55.0) if colour == "amber" else (55.0, 63.0)
        w = _arc(_scale_theta("tachometer", a), _scale_theta("tachometer", b), 0.30 * r, 0.62 * r, 16)
        return label(_uv(w), spec)
    return build


def needle(size, kind):
    def build(spec) -> Part:
        """Needle at rest: the speedometer and tachometer on their zero stops, the dual gauge's oil needle at 40 psi
        and water needle at 170 F, the fuel needle at half (as Oliver's car stood, kf121)."""
        r = _r(size)
        if kind == "fuel-gauge":                      # hanging from its pivot over the scale, at half
            f = r - 1.5
            pv, L0, L1 = FUEL_PIVOT * f, 0.22 * f, 0.68 * f
            n = Location((pv - (L0 + L1) / 2, 0, 2.6)) * Box(L1 - L0, 1.6, 0.8) + zc(1.2, 1.0, 2.6, pv - L0 - 1.0, 0.0)
            return label(n, spec)
        n = zc(4.0 if size == "large" else 3.0, 1.0, 3.5)
        if kind in ("speedometer", "tachometer"):
            ang = [138.0]
        else:
            ang = [-_scale_theta("oil", 40.0), -_scale_theta("water", 170.0)]
        for a in ang:
            L = r - 5.0 if size == "large" else r - 7.0
            n = n + (Rot(0, 0, a) * Location((L / 2 - 6.0, 0, 2.6)) * Box(L, 1.4, 0.8))
        return label(n, spec)
    return build


# ---- warning lamps and switches -----------------------------------------------------------------
def warning_lens(spec) -> Part:
    return label(X.lens_dome(4.6, 2.2, 1.6), spec)


def toggle(spec) -> Part:
    """Toggle switch (Fig 10.9 items 2, 5, 6): body behind the facia with its Lucar terminals,
    the threaded bush through the panel with the chrome locking ring, and the lever."""
    b = box(-11.0, 11.0, -8.0, 8.0, -34.0, -3.0) + zc(6.0, -3.0, 9.0)
    for y in (-4.5, 0.0, 4.5):
        b = b + box(-3.0, 3.0, y - 0.4, y + 0.4, -42.0, -34.0)
    b = b + rev([(6.2, 0.0), (10.0, 0.0), (10.0, 3.0), (6.2, 3.0)])                     # locking ring
    lever = TOGGLE_LEVER * rev([(0, 0), (2.4, 0), (1.9, 12.0), (0, 12.0)])
    return label(b + lever, spec)


TOGGLE_LEVER = Location((0, 0, 9.0)) * Rot(0, -14.0, 0)


def toggle_tip(spec) -> Part:
    """Black moulded tip on the toggle lever (Oliver's kf145)."""
    return label(TOGGLE_LEVER * rev([(0, 11.0), (1.9, 11.0), (2.8, 15.0), (2.9, 20.5), (2.0, 22.5), (0, 23.0)]), spec)


def pull_switch(spec) -> Part:
    """Pull switch (Fig 10.9 items 1 and 4): body behind the facia, the chrome shank and
    ferrule through the panel and its locking ring (the knob is a separate part)."""
    b = zc(9.0, -38.0, -3.0) + zc(5.5, -3.0, 6.0)
    b = b + rev([(5.6, 0.0), (9.5, 0.0), (9.5, 2.5), (5.6, 2.5)])
    for y in (-4.0, 4.0):
        b = b + box(-3.0, 3.0, y - 0.4, y + 0.4, -46.0, -38.0)
    b = b + zc(2.0, 6.0, 12.0)                                                         # plunger shank
    return label(b, spec)


def pull_knob(spec) -> Part:
    """Moulded knob on the pull switch shank, its spring-loaded plunger in the shank
    (Sec 45 para 4), engraved face."""
    k = rev([(0, 10.0), (11.0, 10.0), (12.5, 13.0), (12.5, 22.0), (11.0, 24.0), (0, 24.0)])
    k = k - box(-6.0, 6.0, -0.6, 0.6, 23.6, 25.0) - box(-0.6, 0.6, -6.0, 6.0, 23.6, 25.0) - zc(2.1, 9.0, 13.0)
    return label(k, spec)


def ignition_switch(spec) -> Part:
    """Ignition/starter switch (Fig 10.9 items 8-10): barrel and lock through the facia with
    the locknut, the switch body behind with the connector (Sec 45 para 2), and the key."""
    b = zc(13.0, -40.0, -3.0) + zc(10.0, -3.0, 4.0) + rev([(10.2, 0.0), (15.0, 0.0), (15.0, 3.0), (10.2, 3.0)])
    b = b + rev([(0, 4.0), (12.5, 4.0), (12.5, 7.0), (10.0, 9.0), (0, 9.0)]) - box(-1.2, 1.2, -6.0, 6.0, 7.0, 10.0)
    for y in (-6.0, 0.0, 6.0):
        b = b + box(-3.0, 3.0, y - 0.4, y + 0.4, -48.0, -40.0)
    key = box(-0.9, 0.9, -4.0, 4.0, 7.0, 30.0) + Location((0, 0, 40.0)) * Rot(0, 90, 0) * zc(11.0, -1.2, 1.2)
    key = key - Location((0, 0, 44.0)) * Rot(0, 90, 0) * zc(2.5, -2, 2)
    return label(b + key, spec)


# ---- cables and pipes (car frame) ---------------------------------------------------------------
def _facia_point(name, behind):
    y, z = BL.INSTRUMENTS[name]
    return (BL.FACIA_X + behind, y, z)


def speedo_cable(spec) -> Part:
    """Speedometer cable from the angle drive on the overdrive (P5b) to the back of the
    speedometer: outer casing with its ferrules, through the tunnel and up behind the facia.
    Route derived."""
    (ex_, ey, ez), (dx, dy, dz) = E.speedo_cable_end()
    sx, sy, sz = _facia_point("speedometer", DEPTH["large"] + 26.0)
    pts = [(ex_ - dx * 6.0, ey, ez - dz * 6.0), (ex_ + dx * 50.0, ey, ez + dz * 50.0), (ex_ + 120.0, ey - 80.0, ez + 20.0),
           (BL.BULKHEAD_X - 60.0, sy + 60.0, -150.0), (sx + 150.0, sy + 40.0, sz - 60.0), (sx + 50.0, sy, sz), (sx, sy, sz)]
    c = X.cable(pts, spec.nom("diameter"), 90.0)
    c = c + Plane(origin=(ex_, ey, ez), z_dir=(dx, dy, dz)).location * (zc(6.5, -2.0, 14.0))
    return label(c, spec)


def oil_pipe(spec) -> Part:
    """Oil pressure gauge pipe (Ch 1 Sec 6 para 5, photo 6.5): from the union on the engine's
    oil gallery back along the block, through the bulkhead and up to the dual gauge."""
    ux, uy, uz = E.OIL_UNION
    gx, gy, gz = _facia_point("dual-gauge", DEPTH["small"] + 12.0)
    gx_, gy_ = gx, gy + 6.0
    # through the bulkhead inboard of the pedal box (P8), then outboard under the scuttle above the pedals
    pts = [(ux, uy - 20.0, uz), (ux, -105.0, uz), (ux - 10.0, -142.0, -70.0), (BL.BULKHEAD_X + 20.0, -142.0, -50.0),
           (BL.BULKHEAD_X - 40.0, -142.0, -40.0), (BL.BULKHEAD_X - 130.0, -400.0, 40.0), (BL.BULKHEAD_X - 170.0, -560.0, 90.0),
           (gx_ + 120.0, gy_ - 20.0, gz - 70.0), (gx_ + 30.0, gy_, gz + 8.0), (gx_, gy_, gz + 8.0)]
    c = X.cable(pts, spec.nom("diameter"), 40.0)
    return label(c, spec)


def oil_union(spec) -> Part:
    """Union screwed into the gallery for the gauge pipe, its hexagon and the pipe nut."""
    ux, uy, uz = E.OIL_UNION
    u = Location((ux, uy, uz)) * Rot(90, 0, 0) * (zc(4.0, -4.0, 0.0) + extrude(RegularPolygon(8.0, 6), 8.0)
                                                  + zc(4.5, 8.0, 12.0) + Location((0, 0, 12.0)) * extrude(RegularPolygon(6.5, 6), 8.0))
    return label(u, spec)


def capillary(spec) -> Part:
    """Temperature gauge capillary (Ch 2 Sec 15, capillary type) from the thermal transmitter's
    gland nut on the head to the dual gauge, coiled at the gauge end."""
    tx, ty, tz = E.TEMP_BULB
    gx, gy, gz = _facia_point("dual-gauge", DEPTH["small"] + 8.0)
    gy -= 8.0
    gz -= 6.0
    pts = [(tx, ty - 14.0, tz), (tx, ty - 40.0, tz + 4.0), (tx - 40.0, -170.0, -20.0), (-150.0, -175.0, -20.0),
           (BL.BULKHEAD_X + 30.0, -152.0, -30.0), (BL.BULKHEAD_X - 40.0, -152.0, -25.0), (BL.BULKHEAD_X - 130.0, -412.0, 55.0),
           (BL.BULKHEAD_X - 170.0, -575.0, 105.0), (gx + 150.0, gy - 35.0, gz - 80.0), (gx + 20.0, gy, gz), (gx, gy, gz)]
    c = X.cable(pts, spec.nom("diameter"), 50.0)
    return label(c, spec)


def transmitter(spec) -> Part:
    """Thermal transmitter (bulb) in the head with its gland nut (Ch 1 Sec 6 para 8; Ch 2 Sec 15
    para 3: 'remove the transmitter (capillary type) by removing the gland nut')."""
    tx, ty, tz = E.TEMP_BULB
    t = Location((tx, ty, tz)) * Rot(90, 0, 0) * (zc(5.0, -16.0, 0.0) + extrude(RegularPolygon(10.0, 6), 10.0) + zc(3.0, 10.0, 15.0))
    return label(t, spec)


PARTS = {}
for _size, _kinds in (("large", ("speedometer", "tachometer")), ("small", ("dual-gauge", "fuel-gauge"))):
    for _k in _kinds:
        PARTS[f"electrical.instruments.{_k}-case"] = {"build": case(_size, _k),
                                                       "probes": {"diameter": lambda p: p.bounding_box().size.X}}
        PARTS[f"electrical.instruments.{_k}-dial"] = {"build": dial(_size, _k)}
        PARTS[f"electrical.instruments.{_k}-print"] = {"build": dial_print(_size, _k)}
        PARTS[f"electrical.instruments.{_k}-needle"] = {"build": needle(_size, _k)}
    PARTS[f"electrical.instruments.bezel-{_size}"] = {"build": bezel(_size)}
    PARTS[f"electrical.instruments.glass-{_size}"] = {"build": glass(_size)}
PARTS.update({
    "electrical.instruments.lens-red": {"build": warning_lens},
    "electrical.instruments.lens-blue": {"build": warning_lens},
    "electrical.instruments.lens-green": {"build": warning_lens},
    "electrical.instruments.toggle-switch": {"build": toggle},
    "electrical.instruments.toggle-tip": {"build": toggle_tip},
    "electrical.instruments.tach-sector-amber": {"build": tach_sector("amber")},
    "electrical.instruments.tach-sector-red": {"build": tach_sector("red")},
    "electrical.instruments.pull-switch": {"build": pull_switch},
    "electrical.instruments.pull-knob": {"build": pull_knob},
    "electrical.instruments.ignition-switch": {"build": ignition_switch},
    "electrical.instruments.speedo-cable": {"build": speedo_cable},
    "electrical.instruments.oil-pipe": {"build": oil_pipe},
    "electrical.instruments.oil-union": {"build": oil_union},
    "electrical.instruments.capillary": {"build": capillary},
    "electrical.instruments.transmitter": {"build": transmitter},
})
