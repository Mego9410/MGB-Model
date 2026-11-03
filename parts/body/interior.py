"""Interior and trim (Haynes Ch 12 Sec 3, 29, 47, 54; Fig 12.19 early facia, printed p233; Ch 6 Fig 6.3 items 161-166):
the facia panel built round P10's instrument and switch datums with its crash roll and glovebox lid, the two seats
(frames, runners, cushions, squabs), the carpets, the door trim pads with the inner handles and window winders, the
door top cappings, the gear lever grommet and retainer and the gearbox dipstick plug, the spare wheel clamp.

Drawn in place in the car frame. Trim black (vinyl), carpets black (carpet).
"""
from __future__ import annotations

import math

from build123d import Axis, Compound, Location, Rot

from mgb import body_geom as G, body_layout as BL, body_shell as B, body_shell_layout as S, gearbox_layout as GL
from mgb import underbody_layout as U
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, ycyl, yprism, zcyl, zprism, zrev
from mgb.elec_shapes import tryfillet
from parts.body import closures as C, panels as Pn, structure as St

H = S.z_of


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


# ---- facia ------------------------------------------------------------------------------------------------------------
# The early facia as on Oliver's car (photos 01, 04, 16, 17, 22): a black crinkle-finish steel panel across the car
# under a padded crash roll; on the left the glovebox lid with its lock at the top left and a chrome strip along its
# foot; the centre panel with two round heater knobs on the left, a chrome-edged plaque (plain, no lettering) and under
# it three toggle switches and the ignition, the push-pull knob beside it, the dual oil/water gauge on the right of
# the plaque with the small knob above it; the driver's binnacle cowl round the speedometer (left) and tachometer
# (right) over the column, the fuel gauge further right and the overdrive toggle at the outer end. The panel's rear
# face is P10's FACIA_X; every hole is on P10's datums (mgb/body_layout.py, moved by P11b to the photos).
FX = BL.FACIA_X
FACIA_W = 610.0                              # half-width at the door shut faces
FACIA_H = (712.0, 892.0)                     # lower and upper edges above the road at the centre
FACIA_SWEEP = 0.0                            # flat across (the crash roll and door cappings meet its ends)
SIZE = {"tachometer": 40.0, "speedometer": 40.0, "fuel-gauge": 26.0, "dual-gauge": 26.0}
SW_R = {"panel-lamp": 5.5, "map-lamp": 5.5, "ignition": 10.0}
GLOVE = (250.0, 575.0, 735.0, 868.0)        # (y0, y1, h0, h1) glovebox on the passenger side (left, RHD car)
PLAQUE = (BL.PLAQUE_Y, BL.PLAQUE_Z, 214.0, 74.0)   # centre (y, z), width, height
HEATER_KNOBS = [(BL.HEATER_KNOB_Y, z) for z in BL.HEATER_KNOB_Z]
BINNACLE = (BL.INSTRUMENTS["speedometer"][0], BL.INSTRUMENTS["tachometer"][0], BL.IP_Z)


def _fx(y):
    """Facia rear face x at y (flat across the centre, swept back at the ends)."""
    t = max(abs(y) - 420.0, 0.0) / (FACIA_W - 420.0)
    return FX - FACIA_SWEEP * t * t


def _facia_outline():
    """Front elevation (y, z) of the panel: the top edge under the crash roll, following the scuttle's camber, the
    lower edge straight across with the ends rounded."""
    top = [(y, H(FACIA_H[1] - 24.0 * (y / FACIA_W) ** 2)) for y in [FACIA_W * k / 10 for k in range(10, -11, -1)]]
    bot = [(-FACIA_W, H(FACIA_H[0] + 20.0)), (FACIA_W, H(FACIA_H[0] + 20.0))]
    return B.fillet_poly(top + bot, [40.0] + [0] * 19 + [40.0, 30.0, 30.0], 5)


def facia(spec):
    """Facia panel (Fig 12.19 item 1; Oliver's photos 04, 16, 22): the pressed steel panel at FACIA_X, its ends
    curving back to the doors, with the holes for P10's instruments and switches, the glovebox opening on the left,
    the binnacle's and plaque's fixing holes, the heater control holes, a turned flange along the foot and the fixing
    plates at the ends (items 3, 4). Finished in black crinkle (vinyl_black)."""
    x0 = FX - BL.FACIA_T
    p = xprism(_facia_outline(), x0, FX)
    for k, (y, z) in BL.INSTRUMENTS.items():
        p = p - xcyl(SIZE[k] + 0.5, x0 - 60, FX + 5, y, z)
    for k, (y, z) in BL.SWITCHES.items():
        p = p - xcyl(SW_R.get(k, 6.2), x0 - 60, FX + 5, y, z)
    for y, z in HEATER_KNOBS:
        p = p - xcyl(5.0, x0 - 5, FX + 5, y, z)
    y0, y1, h0, h1 = GLOVE
    p = p - xprism(G.rounded_rect(y0, y1, H(h0), H(h1), 14.0), x0 - 60, FX + 5)
    flange = box(x0, x0 + 22.0, -420.0, 420.0, H(FACIA_H[0] + 20.0), H(FACIA_H[0] + 21.2))
    plates = [box(_fx(s * FACIA_W) - 30.0, _fx(s * FACIA_W), s * FACIA_W - (1.2 if s > 0 else 0.0), s * FACIA_W + (0.0 if s > 0 else 1.2),
                  H(FACIA_H[0] + 30.0), H(FACIA_H[1] - 40.0)) for s in (1, -1)]
    return _c([p, flange] + plates, spec)


def centre_panel(spec):
    """Centre switch panel (Oliver's photos 16, 22): a raised black panel on the facia from the heater knobs to the
    dual gauge, carrying the plaque, the switches and the ignition (its holes on P10's datums)."""
    y0, y1 = BL.HEATER_KNOB_Y + 40.0, BL.INSTRUMENTS["dual-gauge"][0] - 40.0
    x0 = FX - BL.FACIA_T - 3.0
    p = xprism(G.rounded_rect(y1, y0, H(FACIA_H[0] + 28.0), H(FACIA_H[1] - 30.0), 16.0), x0, FX - BL.FACIA_T)
    for k, (y, z) in BL.SWITCHES.items():               # clear of the switches' nuts and bezels on the facia
        if y1 < y < y0:
            p = p - xcyl(16.0 if k == "ignition" else 12.5, x0 - 5, FX + 5, y, z)
    k = "dual-gauge"
    p = p - xcyl(SIZE[k] + 6.0, x0 - 5, FX + 5, *BL.INSTRUMENTS[k])
    for y, z in HEATER_KNOBS:
        p = p - xcyl(5.0, x0 - 5, FX + 5, y, z)
    return _l(p, spec)


def plaque(spec):
    """Facia plaque (Oliver's photo 16): a rectangle with a polished chrome edge on the centre panel above the
    switches; plain (the badge on it is not modelled)."""
    y, z, w, h = PLAQUE
    x0 = FX - BL.FACIA_T - 3.0
    rim = xprism(G.rounded_rect(y - w / 2, y + w / 2, z - h / 2, z + h / 2, 6.0), x0 - 5.0, x0) - \
        xprism(G.rounded_rect(y - w / 2 + 5.0, y + w / 2 - 5.0, z - h / 2 + 5.0, z + h / 2 - 5.0, 3.0), x0 - 6.0, x0 + 1.0)
    from build123d import Axis
    rim = tryfillet(rim, rim.edges().filter_by_position(Axis.X, x0 - 5.5, x0 - 4.5), 1.8)
    return _l(rim, spec)


def plaque_field(spec):
    """The plaque's black field inside its chrome edge."""
    y, z, w, h = PLAQUE
    x0 = FX - BL.FACIA_T - 3.0
    return _l(xprism(G.rounded_rect(y - w / 2 + 5.0, y + w / 2 - 5.0, z - h / 2 + 5.0, z + h / 2 - 5.0, 3.0), x0 - 3.0, x0), spec)


def heater_knob(k):
    def build(spec):
        """Heater control knob (Oliver's photos 16, 22): a round black knob with a fluted rim and a chrome centre, on
        its spindle through the centre panel (the air and temperature controls of the Smiths heater)."""
        y, z = HEATER_KNOBS[k]
        x0 = FX - BL.FACIA_T - 3.0
        from mgb.chassis_geom import xrev
        body = xrev([(0.0, 0.0), (23.0, 0.0), (23.0, -6.0), (21.0, -18.0), (12.0, -24.0), (0.0, -24.0)])
        for j in range(12):                                   # flutes round the rim
            a = math.radians(30.0 * j)
            body = body - xcyl(2.6, -20.0, -1.0, 23.0 * math.cos(a), 23.0 * math.sin(a))
        p = body.moved(Location((x0, y, z)))
        return _l(p, spec)
    return build


def heater_knob_cap(spec):
    """Chrome centre caps of the two heater knobs."""
    x0 = FX - BL.FACIA_T - 3.0
    from mgb.chassis_geom import xrev
    caps = [xrev([(0.0, -22.0), (9.0, -22.0), (8.0, -28.0), (0.0, -29.0)]).moved(Location((x0, y, z))) for y, z in HEATER_KNOBS]
    return _c(caps, spec)


def binnacle(spec):
    """Driver's binnacle cowl (Oliver's photos 01, 04, 17, 22): the hooded surround of the speedometer and the
    tachometer over the column, standing 45 mm back from the facia, its top projecting a further 18 mm as a visor;
    the dial panel inside carries the two instruments' holes."""
    ya, yb, z = BINNACLE
    yc, half = (ya + yb) / 2, abs(ya - yb) / 2 + 56.0
    x0 = FX - BL.FACIA_T
    outer = B.fillet_poly([(yc - half, z - 56.0), (yc + half, z - 56.0), (yc + half, z + 60.0), (yc - half, z + 60.0)],
                          [24.0, 24.0, 44.0, 44.0], 6)
    inner = B.fillet_poly([(yc - half + 9.0, z - 47.0), (yc + half - 9.0, z - 47.0), (yc + half - 9.0, z + 51.0),
                           (yc - half + 9.0, z + 51.0)], [18.0, 18.0, 36.0, 36.0], 6)
    shell = xprism(outer, x0 - 45.0, x0) - xprism(inner, x0 - 46.0, x0 + 1.0)
    visor = xprism(outer, x0 - 63.0, x0 - 44.0) & box(x0 - 64.0, x0, yc - half - 1, yc + half + 1, z + 34.0, z + 61.0)
    visor = visor - xprism(inner, x0 - 64.0, x0)
    return _c([shell, visor], spec)


ROLL_W = S.SCREEN_HALF_W - 12.0               # the roll's ends stop inside the screen pillars (not seen from outside)


def crash_roll(spec):
    """Crash roll (Fig 12.19 item 21; Oliver's photos 01, 04, 22): the padded black roll along the facia's top from
    door to door under the screen, curving back at its ends to the door shut faces."""
    ys = [-ROLL_W + 2 * ROLL_W * k / 16 for k in range(17)]
    pts = [(_fx(y) - 24.0, y, H(FACIA_H[1] - 24.0 * (y / FACIA_W) ** 2) + 2.0) for y in ys]
    r = swept_rod(pts, 27.0)
    cut = box(FX - 80.0, FX + 60.0, -FACIA_W - 60, FACIA_W + 60, H(FACIA_H[1]) - 40.0, H(FACIA_H[1]) + 60.0)
    return _l(r & cut, spec)


def glovebox_lid(spec):
    """Glovebox lid (Fig 12.19 item 7; Oliver's photos 04, 22) closing the opening, its lock at the top left."""
    y0, y1, h0, h1 = GLOVE
    x = _fx((y0 + y1) / 2)
    p = xprism(G.rounded_rect(y0 + 2, y1 - 2, H(h0) + 2, H(h1) - 2, 12.0), FX - 6.0, FX - 1.5)
    p = p + xcyl(7.0, FX - 12.0, FX - 6.0, y1 - 70.0, H(h1) - 30.0)
    return _l(p, spec)


def glovebox_strip(spec):
    """Chrome strip along the glovebox lid's foot (Oliver's photos 04, 22)."""
    y0, y1, h0, h1 = GLOVE
    s = xprism(G.rounded_rect(y0 + 12.0, y1 - 12.0, H(h0) + 24.0, H(h0) + 30.0, 2.5), FX - 9.0, FX - 6.0)
    return _l(s, spec)


def console(spec):
    """Centre console (Oliver's photos 04, 22): the black panel from under the centre switch panel down to the
    tunnel, carrying the radio speaker grille."""
    xt = FX - 20.0
    zt = H(FACIA_H[0] + 20.0)
    zb = St.TUNNEL[1][4] + 4.0
    w = 120.0
    p = box(xt - 4.0, xt, -w, w, zb, zt)
    sides = [box(xt, FX + 60.0, s * w - (1.2 if s > 0 else 0.0), s * w + (0.0 if s > 0 else 1.2), zb, zt) for s in (1, -1)]
    gy, gz, gw, gh = 0.0, (zt + zb) / 2 + 10.0, 150.0, 112.0
    p = p - xprism(_chamfered(gy, gz, gw - 6.0, gh - 6.0, 22.0), xt - 6, xt + 2)
    return _c([p] + sides, spec)


def _chamfered(y, z, w, h, c):
    return [(y - w / 2 + c, z - h / 2), (y + w / 2 - c, z - h / 2), (y + w / 2, z - h / 2 + c), (y + w / 2, z + h / 2 - c),
            (y + w / 2 - c, z + h / 2), (y - w / 2 + c, z + h / 2), (y - w / 2, z + h / 2 - c), (y - w / 2, z - h / 2 + c)]


def speaker_grille(spec):
    """Radio speaker grille in the console (Oliver's photos 04, 22): an octagonal (chamfered rectangle) chrome frame
    round a fine mesh of horizontal bars."""
    xt = FX - 20.0
    zt = H(FACIA_H[0] + 20.0)
    zb = St.TUNNEL[1][4] + 4.0
    gy, gz, gw, gh = 0.0, (zt + zb) / 2 + 10.0, 150.0, 112.0
    frame = xprism(_chamfered(gy, gz, gw, gh, 24.0), xt - 9.0, xt - 4.0) - xprism(_chamfered(gy, gz, gw - 14.0, gh - 14.0, 19.0), xt - 10.0, xt - 3.0)
    bars = []
    zz = gz - gh / 2 + 9.0
    while zz < gz + gh / 2 - 8.0:
        bars.append(box(xt - 6.0, xt - 4.5, gy - gw / 2 + 6.0, gy + gw / 2 - 6.0, zz - 0.8, zz + 0.8))
        zz += 3.6
    mesh = G.fuse(bars) & xprism(_chamfered(gy, gz, gw - 12.0, gh - 12.0, 20.0), xt - 8.0, xt - 3.0)
    return _c([frame, mesh], spec)


# ---- seats ------------------------------------------------------------------------------------------------------------
# Black vinyl seats with red piping (Oliver's photos 04, 22): a crowned cushion with a fluted centre panel and bolstered
# sides, a squab with a rounded top; piping along the cushion's top edge and round the squab's face.
SEAT_Y = 385.0                               # between the floor's runner captive nuts (y 300 and 470)
SEAT_W = 430.0
CUSH_X = (-1080.0, -1420.0)
CUSH_H = (274.0, 364.0)
SQUAB_RAKE = 12.0
SQUAB_LEN = 590.0
SQUAB_T = 100.0


def _rr_wire(x0, x1, y0, y1, z, r, n=4):
    from build123d import Vector, Wire
    pts = B.fillet_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r, n)
    return Wire.make_polygon([Vector(a, b, z) for a, b in pts], close=True)


def _cushion_solid(side):
    from build123d import Solid
    y = side * SEAT_Y
    x0, x1 = CUSH_X[1], CUSH_X[0]
    h0, h1 = H(CUSH_H[0]), H(CUSH_H[1])
    w = SEAT_W / 2
    secs = [(h0, 0.0, 30.0), (h0 + 40.0, 4.0, 40.0), (h1 - 18.0, 0.0, 44.0), (h1 - 4.0, 14.0, 40.0), (h1, 30.0, 30.0)]
    wires = [_rr_wire(x0 + d, x1 - d, y - w + d, y + w - d, z, r) for z, d, r in secs]
    return Solid.make_loft(wires, ruled=False)


def seat_cushion(side):
    def build(spec):
        """Seat cushion (Haynes Sec 54; Oliver's photos 04, 22): a sprung, padded cushion in black vinyl, crowned and
        rolled at the edges, the fluted centre panel between two bolsters."""
        c = _cushion_solid(side)
        y = side * SEAT_Y
        for k in range(-3, 4):                                   # flutes across the centre panel
            yy = y + k * 40.0
            c = c - box(CUSH_X[1] + 50.0, CUSH_X[0] - 50.0, yy - 2.0, yy + 2.0, H(CUSH_H[1]) - 4.0, H(CUSH_H[1]) + 2.0)
        for yy in (y - 150.0, y + 150.0):                        # bolster seams
            c = c - box(CUSH_X[1] + 30.0, CUSH_X[0] - 30.0, yy - 2.5, yy + 2.5, H(CUSH_H[1]) - 6.0, H(CUSH_H[1]) + 2.0)
        return _l(c, spec)
    return build


def _squab_loc(side):
    return Location((CUSH_X[1] + 110.0, side * SEAT_Y, H(CUSH_H[0] + 40.0))) * Rot(0, -SQUAB_RAKE, 0)   # clear of the heelboard


def _squab_local():
    from build123d import Solid
    w = SEAT_W / 2
    secs = [(0.0, 0.0, 30.0), (40.0, -4.0, 36.0), (SQUAB_LEN - 90.0, 0.0, 44.0), (SQUAB_LEN - 30.0, 30.0, 40.0),
            (SQUAB_LEN, 80.0, 20.0)]
    from build123d import Vector, Wire
    wires = []
    for z, d, r in secs:
        pts = B.fillet_poly([(-SQUAB_T + d * 0.6, -w + d), (0.0 - d * 0.4, -w + d), (0.0 - d * 0.4, w - d), (-SQUAB_T + d * 0.6, w - d)],
                            min(r, (SQUAB_T - d) / 2.2), 4)
        wires.append(Wire.make_polygon([Vector(a, b, z) for a, b in pts], close=True))
    return Solid.make_loft(wires, ruled=False)


def seat_squab(side):
    def build(spec):
        """Seat squab (back), raked back over the hood well, rounded at the top, fluted in the centre panel, on a
        hinged frame."""
        s = _squab_local()
        for k in range(-3, 4):
            s = s - box(-3.0, 2.0, k * 40.0 - 2.0, k * 40.0 + 2.0, 70.0, SQUAB_LEN - 110.0)
        return _l(_squab_loc(side) * s, spec)
    return build


def seat_piping(side):
    def build(spec):
        """Red piping (Oliver's photos 04, 22): round the cushion's top edge and round the squab's face and top."""
        y = side * SEAT_Y
        w = SEAT_W / 2
        hz = H(CUSH_H[1]) - 14.0
        loop = B.fillet_poly([(CUSH_X[1] + 2.0, y - w + 2.0), (CUSH_X[0] - 2.0, y - w + 2.0), (CUSH_X[0] - 2.0, y + w - 2.0),
                              (CUSH_X[1] + 2.0, y + w - 2.0)], 42.0, 5)
        cush = swept_rod([(a, b, hz) for a, b in loop + loop[:1]], 3.2)
        sq = B.fillet_poly([(-2.0, -w + 4.0), (-2.0, w - 4.0)], 0.0)
        pts = [(-4.0, -w + 2.0, 40.0), (-4.0, -w + 2.0, SQUAB_LEN - 90.0), (-20.0, -w + 22.0, SQUAB_LEN - 22.0),
               (-30.0, 0.0, SQUAB_LEN - 4.0), (-20.0, w - 22.0, SQUAB_LEN - 22.0), (-4.0, w - 2.0, SQUAB_LEN - 90.0), (-4.0, w - 2.0, 40.0)]
        squab = _squab_loc(side) * swept_rod(pts, 3.2)
        return _c([cush, squab], spec)
    return build


def seat_frame(side):
    def build(spec):
        """Seat frame and runners: the tubular cushion pan frame, the squab's side hinges, two runners on the floor's
        captive nuts (St.floor_half), the adjuster bar."""
        y = side * SEAT_Y
        zf = U.FLOOR_Z + St.T
        parts = []
        for yy in (y - 85.0, y + 85.0):                          # runners on the nuts at |y| 300 and 470
            r = box(-1320.0, -1030.0, yy - 12.0, yy + 12.0, zf, zf + 22.0) - box(-1321.0, -1029.0, yy - 10.5, yy + 10.5, zf + 1.5, zf + 20.5)
            for xn in (-1060.0, -1290.0):
                r = r - zcyl(4.4, zf - 1, zf + 3, xn, yy)
            parts.append(r)
        zp = H(CUSH_H[0]) - 2.0
        loop = [(CUSH_X[0] - 15.0, y - SEAT_W / 2 + 20.0, zp), (CUSH_X[0] - 15.0, y + SEAT_W / 2 - 20.0, zp),
                (CUSH_X[1] + 15.0, y + SEAT_W / 2 - 20.0, zp), (CUSH_X[1] + 15.0, y - SEAT_W / 2 + 20.0, zp),
                (CUSH_X[0] - 15.0, y - SEAT_W / 2 + 20.0, zp)]
        parts.append(swept_rod(loop, 8.0))
        for yy in (y - 85.0, y + 85.0):                          # legs from the runners to the pan
            for xx in (-1060.0, -1290.0):
                parts.append(rod((xx, yy, zf + 20.0), (xx, yy, zp - 6.0), 7.0))
        parts.append(rod((-1030.0, y - 100.0, zf + 26.0), (-1010.0, y - 30.0, zf + 26.0), 4.0))   # adjuster bar
        return _c(parts, spec)
    return build


# ---- carpets -------------------------------------------------------------------------------------------------------
CT = 6.0


def floor_carpet(side):
    def build(spec):
        """Floor carpet on the floor half and the toe board, bound edges, the heel pad."""
        zf = U.FLOOR_Z + St.T + 0.2
        yi = St.tunnel_halfwidth(-1000.0, zf) + 2.0
        c = box(U.HEELBOARD_X + 3.0, U.TOE_FOOT[0], yi, S.SILL_INNER_Y - 2.0, zf + 7.2, zf + 7.2 + CT)
        (xf, _), (xt, zt) = U.TOE_FOOT, U.TOE_TOP
        toe = G.sheet_y([(xt - 3.0, zt + 1.5), (xf + 2.0, zf + 7.2 + CT)], -CT, 150.0, S.SILL_INNER_Y - 2.0, 2.0)
        pad = box(-700.0, -560.0, 250.0, 450.0, zf + 7.2 + CT, zf + 7.2 + CT + 2.0)
        return _c([St._side(c, side), St._side(toe, side), St._side(pad, side)], spec)
    return build


def tunnel_carpet(spec):
    """Tunnel carpet moulded over the tunnel from the toe boards to the heelboard, the gear lever's opening."""
    secs = [st for st in St.TUNNEL if st[0] < -470.0]
    from build123d import Solid, Wire, Vector
    wires = []
    for st in [(-472.0,) + St.TUNNEL[1][1:]] + secs:
        prof = St.tunnel_profile(st, flange=3.0)[6:-6]
        band = G.band(prof, -CT)
        wires.append(Wire.make_polygon([Vector(st[0], y, z) for y, z in band], close=True))
    c = Solid.make_loft(wires, ruled=True)
    if not c.is_valid:
        c = c.fix()
    lx = _lever_x()
    c = c - zprism(G.obround(lx - 10.0, 0.0, 130.0, 90.0), -200.0, 100.0)
    return _l(c, spec)


def _lever_x():
    z = St.TUNNEL[3][4]
    return GL.LEVER_BALL[0] + (GL.KNOB[0] - GL.LEVER_BALL[0]) * (z - GL.LEVER_BALL[2]) / (GL.KNOB[2] - GL.LEVER_BALL[2])


def rear_carpet(spec):
    """Carpets on the heelboard and the tonneau floor (lifted to reach the battery access covers, photo 2.1)."""
    z = U.TONNEAU_Z + St.T + 4.5
    floor = box(S.REAR_BULKHEAD_X + 2.0, U.HEELBOARD_X - 2.0, -St.RWH_Y + 2.0, St.RWH_Y - 2.0, z, z + CT)
    hb = box(U.HEELBOARD_X + St.T + 0.5, U.HEELBOARD_X + St.T + 0.5 + CT, -S.SILL_INNER_Y + 4.0, S.SILL_INNER_Y - 4.0,
             U.FLOOR_Z + 20.0, U.TONNEAU_Z)
    hb = hb - box(U.HEELBOARD_X, U.HEELBOARD_X + 20.0, -U.TUNNEL_Y - 8.0, U.TUNNEL_Y + 8.0, U.FLOOR_Z, -190.0)
    return _c([floor, hb], spec)


# ---- door trim ----------------------------------------------------------------------------------------------------------
def door_card_sd(side):
    def f(X, Y, Z):
        return B.sd_and(Pn.door_sd(X, Y, Z, side) + S.GAP / 2 + 16.0, Z - H(C.WAIST_H - 30.0), H(S.DOOR_BOTTOM_H + 30.0) - Z)
    return f


def door_card(side):
    def build(spec):
        """Door trim pad (Sec 29, early Sports Tourer): a hardboard panel covered in vinyl on the inner panel, its
        pocket, held by clips round its edge."""
        def make():
            return B.skin_sdf(door_card_sd(side), 3.0, shift=(0.0, -side * (C.DOOR_IN + 1.2), 0.0))
        c = Compound(G.solids([B.disk_cached(f"door-card-{side}", make, extra_sources=("parts/body/interior.py", "parts/body/closures.py",
                                                                                       "parts/body/panels.py"))]))
        c.label = spec.id
        return c
    return build


def _card_y(side, x, h):
    return side * (S.side_y(x, h) - C.DOOR_IN - 1.2 - 4.0)


def inner_handle(side):
    def build(spec):
        """Inner door handle (Fig 12.13 item 21, early cars) on its escutcheon, toward the door's rear."""
        x, h = S.DOOR_REAR_X + 200.0, 720.0
        y = _card_y(side, x, h)
        esc = ycyl(22.0, min(y, y - side * 6.0), max(y, y - side * 6.0), x, H(h))
        lever = rod((x, y - side * 6.0, H(h)), (x + 90.0, y - side * 14.0, H(h) - 8.0), 6.0)
        return _c([esc, lever], spec)
    return build


def winder(side):
    def build(spec):
        """Window regulator handle (Fig 12.17 item 11, handle and finisher) on the regulator's spindle."""
        x, h = -1180.0, 560.0
        y = _card_y(side, x, h)
        boss = ycyl(18.0, min(y, y - side * 10.0), max(y, y - side * 10.0), x, H(h))
        arm = rod((x, y - side * 10.0, H(h)), (x + 25.0, y - side * 12.0, H(h) + 70.0), 6.0)
        knob = ycyl(9.0, min(y - side * 12.0, y - side * 40.0), max(y - side * 12.0, y - side * 40.0), x + 25.0, H(h) + 70.0)
        return _c([boss, arm, knob], spec)
    return build


def door_capping(side):
    def build(spec):
        """Door top capping: the padded vinyl roll along the door's top over the glass slot."""
        xs = [S.DOOR_FRONT_X - 8.0 - k * (S.DOOR_FRONT_X - S.DOOR_REAR_X - 16.0) / 8 for k in range(9)]
        pts = [(x, side * (S.side_y(x, C.WAIST_H - 30.0) - C.DOOR_IN + 6.0), H(C.WAIST_H - 6.0)) for x in xs]
        return _l(swept_rod(pts, 13.0), spec)
    return build


# ---- tunnel fittings ------------------------------------------------------------------------------------------------
def lever_grommet(spec):
    """Gear lever grommet (Fig 6.3 item 161): a rubber cone from the tunnel's aperture up the lever."""
    lx = _lever_x()
    z = St.TUNNEL[3][4]
    g = zrev([(18.0, 0.0), (58.0, 0.0), (58.0, 6.0), (26.0, 40.0), (14.0, 62.0), (11.0, 62.0), (22.0, 38.0), (52.0, 4.0),
              (18.0, 4.0)])
    from mgb import gearbox_layout as GLY
    tilt = math.degrees(math.atan2(GLY.KNOB[0] - GLY.LEVER_BALL[0], GLY.KNOB[2] - GLY.LEVER_BALL[2]))
    return _l(Location((lx, 0.0, z + 1.0)) * Rot(0, tilt, 0) * g, spec)


def grommet_retainer(spec):
    """Grommet retainer ring (Fig 6.3 items 162-166) with its four screws to the tunnel."""
    lx = _lever_x()
    z = St.TUNNEL[3][4]
    ring = zprism(G.obround(lx - 10.0, 0.0, 150.0, 110.0), z + 1.0, z + 3.0) - zprism(G.obround(lx - 10.0, 0.0, 116.0, 76.0), z, z + 4.0)
    screws = [zcyl(4.0, z + 3.0, z + 5.0, lx - 10.0 + dx, dy) for dx, dy in ((-75.0, -48.0), (-75.0, 48.0), (55.0, -48.0), (55.0, 48.0))]
    return _c([ring] + screws, spec)


def dipstick_plug(spec):
    """Rubber plug over the gearbox dipstick hole in the tunnel (Ch 6 Sec 2 para 1)."""
    x = -560.0
    z = St.TUNNEL[1][4]
    g = zrev([(0.0, 0.0), (26.0, 0.0), (26.0, 4.0), (20.0, 4.0), (20.0, 9.0), (0.0, 9.0)])
    return _l(Location((x, 60.0, z - 6.0)) * g, spec)


# ---- spare wheel clamp ------------------------------------------------------------------------------------------------
SPARE_TOP = U.BOOT_FLOOR_Z + St.T + 152.0


def spare_clamp(spec):
    """Spare wheel clamp: a stud from the boot floor through the wheel's centre, a clamp bar across the hub and the
    wing nut."""
    x, y = St.SPARE_X, St.SPARE_Y
    zb = U.BOOT_FLOOR_Z + St.T
    stud = zcyl(4.8, zb - 4.0, SPARE_TOP + 30.0, x, y)
    bar = box(x - 70.0, x + 70.0, y - 14.0, y + 14.0, SPARE_TOP - 8.0, SPARE_TOP - 3.0)
    nut = zcyl(11.0, SPARE_TOP - 3.0, SPARE_TOP + 8.0, x, y) + box(x - 28.0, x + 28.0, y - 3.0, y + 3.0, SPARE_TOP, SPARE_TOP + 20.0)
    return _c([stud, bar, nut], spec)


PARTS = {
    "body.interior.facia": {"build": facia},
    "body.interior.centre-panel": {"build": centre_panel},
    "body.interior.plaque": {"build": plaque},
    "body.interior.plaque-field": {"build": plaque_field},
    "body.interior.heater-knob-upper": {"build": heater_knob(0)},
    "body.interior.heater-knob-lower": {"build": heater_knob(1)},
    "body.interior.heater-knob-caps": {"build": heater_knob_cap},
    "body.interior.binnacle": {"build": binnacle},
    "body.interior.glovebox-strip": {"build": glovebox_strip},
    "body.interior.console": {"build": console},
    "body.interior.speaker-grille": {"build": speaker_grille},
    "body.interior.crash-roll": {"build": crash_roll},
    "body.interior.glovebox-lid": {"build": glovebox_lid},
    "body.interior.tunnel-carpet": {"build": tunnel_carpet},
    "body.interior.rear-carpet": {"build": rear_carpet},
    "body.interior.lever-grommet": {"build": lever_grommet},
    "body.interior.grommet-retainer": {"build": grommet_retainer},
    "body.interior.dipstick-plug": {"build": dipstick_plug},
    "body.rear.spare-clamp": {"build": spare_clamp},
}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.interior.seat-cushion-{n}"] = {"build": seat_cushion(s_)}
    PARTS[f"body.interior.seat-squab-{n}"] = {"build": seat_squab(s_)}
    PARTS[f"body.interior.seat-frame-{n}"] = {"build": seat_frame(s_)}
    PARTS[f"body.interior.seat-piping-{n}"] = {"build": seat_piping(s_)}
    PARTS[f"body.interior.floor-carpet-{n}"] = {"build": floor_carpet(s_)}
    PARTS[f"body.interior.door-card-{n}"] = {"build": door_card(s_)}
    PARTS[f"body.interior.inner-handle-{n}"] = {"build": inner_handle(s_)}
    PARTS[f"body.interior.winder-{n}"] = {"build": winder(s_)}
    PARTS[f"body.interior.door-capping-{n}"] = {"build": door_capping(s_)}


# ---- tools in the boot ------------------------------------------------------------------------------------------
TOOL_Z = U.BOOT_FLOOR_Z + St.T


def jack(spec):
    """Side-lift jack stowed on the boot floor beside the spare: the base, the screw pillar, the lifting arm that
    enters the sill's jacking socket (St.jack_socket) and the folding handle."""
    x, y = -2560.0, -330.0
    base = box(x - 60.0, x + 60.0, y - 45.0, y + 45.0, TOOL_Z, TOOL_Z + 6.0)
    pillar = rod((x, y, TOOL_Z + 6.0), (x - 330.0, y, TOOL_Z + 30.0), 14.0)
    screw = rod((x - 20.0, y, TOOL_Z + 30.0), (x - 300.0, y, TOOL_Z + 50.0), 8.0)
    arm = box(x - 200.0, x - 170.0, y + 14.0, y + 120.0, TOOL_Z + 12.0, TOOL_Z + 38.0)
    return _c([base, pillar, screw, arm], spec)


def hammer(spec):
    """Copper and hide mallet for the wire wheels' knock-off spinners, in the boot."""
    x, y = -2790.0, -200.0
    head = ycyl(26.0, y - 55.0, y + 55.0, x, TOOL_Z + 27.0)
    handle = rod((x, y, TOOL_Z + 27.0), (x + 280.0, y + 20.0, TOOL_Z + 14.0), 12.0)
    return _c([head, handle], spec)


def boot_carpet(spec):
    """Black boot carpet (Oliver's photo 26) on the boot floor behind the axle kick-up, between the wheel houses, cut
    round the spare wheel's locating ring and the clamp stud."""
    zb = U.BOOT_FLOOR_Z + St.T + 0.3
    x0, x1 = U.REAR_PANEL_X + 8.0, U.ARCH_X[1] - 8.0
    c = box(x0, x1, -St.RWH_Y + 4.0, St.RWH_Y - 4.0, zb, zb + CT)
    c = c - zcyl(146.0, zb - 1, zb + CT + 1, St.SPARE_X, St.SPARE_Y)
    return _l(c, spec)


PARTS["body.rear.boot-carpet"] = {"build": boot_carpet}
PARTS["body.rear.jack"] = {"build": jack}
PARTS["body.rear.hammer"] = {"build": hammer}
