"""Interior and trim (Haynes Ch 12 Sec 3, 29, 47, 54; Fig 12.19 early facia, printed p233; Ch 6 Fig 6.3 items 161-166):
the facia panel built round P10's instrument and switch datums with its crash roll and glovebox lid, the two seats
(frames, runners, cushions, squabs), the carpets, the door trim pads with the inner handles and window winders, the
door top cappings, the gear lever grommet and retainer and the gearbox dipstick plug, the spare wheel clamp.

Drawn in place in the car frame. Trim black (vinyl), carpets black (carpet).
"""
from __future__ import annotations

import math

from build123d import Axis, Compound, Location, Plane, Rot

from mgb import body_geom as G, body_layout as BL, body_shell as B, body_shell_layout as S, car_layout as CL, gearbox_layout as GL
from mgb import cockpit_layout as CK, throttle_layout as TL, underbody_layout as U
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
    p = p - xcyl(TL.CHOKE_HOLE_R, x0 - 60, FX + 5, *TL.CHOKE_KNOB[1:])     # choke control (fuel.choke)
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
    p = p - xcyl(TL.CHOKE_HOLE_R, x0 - 5, FX + 5, *TL.CHOKE_KNOB[1:])     # the choke control's bush (its bezel on the face)
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


FACIA_FRAME = Rot(0, -90, 0)                  # local z toward the driver, x up, y the car's left (as the instruments)


def plaque_badge(spec):
    """The plaque's chrome MG badge (Oliver's kf122, kf145 zoomed): the MG octagon - its edge and letters - with three
    chrome speed lines on each side, the middle line the longest, on the black field."""
    from parts.chassis import steering as STG
    y, z, w, h = PLAQUE
    x0 = FX - BL.FACIA_T - 3.0 - 3.0                  # the field's face
    af = 40.0
    octo = STG._octagon(af + 5.0, 0.0, 1.4) - STG._octagon(af, -1.0, 2.4)
    letters = STG._mg_letters(22.0, 0.0, 1.2)
    lines = []
    for k, (dv, L) in enumerate(((-7.0, 50.0), (0.0, 62.0), (7.0, 50.0))):   # (height across the badge, length)
        for s_ in (1, -1):
            u0 = af / 2 + 2.0
            # in the badge frame: x up, y the car's left; the lines run across (y)
            lines.append(box(dv - 1.4, dv + 1.4, s_ * u0 if s_ > 0 else -u0 - L, u0 + L if s_ > 0 else -u0, 0.0, 1.2))
    from build123d import Compound
    loc = Location((x0, y, z)) * FACIA_FRAME
    c = Compound(children=[loc * p for p in [octo, letters] + lines])
    c.label = spec.id
    return c


KNOB_FACE = 14.0                              # heater knob's face proud of the centre panel


def heater_knob(k):
    def build(spec):
        """Heater control knob (Oliver's photos 16, 22): a round black knob with a fluted rim and a chrome centre, on
        its spindle through the centre panel (the air and temperature controls of the Smiths heater)."""
        y, z = HEATER_KNOBS[k]
        x0 = FX - BL.FACIA_T - 3.0
        from mgb.chassis_geom import xrev
        body = xrev([(0.0, 0.0), (23.0, 0.0), (23.0, -KNOB_FACE + 2.0), (21.5, -KNOB_FACE), (0.0, -KNOB_FACE)])
        for j in range(16):                                   # flutes round the rim
            a = math.radians(22.5 * j)
            body = body - xcyl(2.4, -KNOB_FACE - 1.0, -1.0, 23.6 * math.cos(a), 23.6 * math.sin(a))
        for j in range(6):                                    # raised vanes across the face (kf145)
            body = body + Rot(30.0 + 60.0 * j, 0, 0) * box(-KNOB_FACE - 2.2, -KNOB_FACE + 0.5, -1.6, 1.6, 10.0, 20.5)
        p = body.moved(Location((x0, y, z)))
        return _l(p, spec)
    return build


HEATER_WORDS = (("WARM", "COLD"), ("AIR", "OFF"))


def heater_knob_print(spec):
    """White lettering round the heater knobs' faces (Oliver's kf145: WARM legible on the upper knob; the other
    words are the Smiths heater's control positions, assumed)."""
    from build123d import Align, Compound, Text, extrude
    x0 = FX - BL.FACIA_T - 3.0
    out = []
    for (y, z), words in zip(HEATER_KNOBS, HEATER_WORDS):
        for word, ang in zip(words, (60.0, -60.0)):
            t = extrude(Text(word, font_size=4.2, align=(Align.CENTER, Align.CENTER)), 0.3, dir=(0, 0, 1))
            a = math.radians(ang)
            # driver's view (u right, v up) on the knob's face 6 mm proud of the panel, round its rim at r 16
            u, v = -15.5 * math.sin(a), 15.5 * math.cos(a)
            t = Location((u, v, KNOB_FACE + 0.02)) * Rot(0, 0, ang) * t
            out.append(Location((x0, y, z)) * FACIA_FRAME * Rot(0, 0, -90) * t)
        for j in range(5):                                  # position ticks along the rim
            a = math.radians(-30.0 + 15.0 * j + 180.0)
            out.append(Location((x0, y, z)) * FACIA_FRAME * Rot(0, 0, -90) *
                       Location((19.5 * math.sin(a), 19.5 * math.cos(a), KNOB_FACE + 0.02)) * Rot(0, 0, -math.degrees(a)) * box(-0.5, 0.5, -1.8, 1.8, 0.0, 0.3))
    c = Compound(children=out)
    c.label = spec.id
    return c


def heater_knob_cap(spec):
    """Chrome centre caps of the two heater knobs."""
    x0 = FX - BL.FACIA_T - 3.0
    from mgb.chassis_geom import xrev
    caps = [xrev([(0.0, -KNOB_FACE + 0.2), (9.0, -KNOB_FACE + 0.2), (8.0, -KNOB_FACE - 5.0), (0.0, -KNOB_FACE - 6.0)]).moved(Location((x0, y, z)))
            for y, z in HEATER_KNOBS]
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


GLOVE_LOCK = ((GLOVE[0] + GLOVE[1]) / 2, GLOVE[3] - 30.0)     # mid-width near the top (Oliver's kf128, kf143, kf145)
GLOVE_STRIP_H = GLOVE[2] + 0.57 * (GLOVE[3] - GLOVE[2])      # chrome strip across the lid, 57 % up it (kf143, kf145)


def glovebox_lid(spec):
    """Glovebox lid (Fig 12.19 item 7; Oliver's kf128, kf143, kf145) closing the opening, the lock's hole mid-width
    near its top."""
    y0, y1, h0, h1 = GLOVE
    p = xprism(G.rounded_rect(y0 + 2, y1 - 2, H(h0) + 2, H(h1) - 2, 12.0), FX - 6.0, FX - 1.5)
    p = p - xcyl(7.5, FX - 7.0, FX, GLOVE_LOCK[0], H(GLOVE_LOCK[1]))
    return _l(p, spec)


def glovebox_lock(spec):
    """The glovebox lid's chrome lock: a domed bezel round the barrel with its key slot."""
    yl, hl = GLOVE_LOCK
    from mgb.chassis_geom import xrev
    b = xrev([(0.0, 0.0), (7.4, 0.0), (11.0, -2.0), (10.0, -4.5), (6.0, -6.0), (0.0, -6.0)])
    b = b - box(-7.0, -5.0, -1.0, 1.0, -4.0, 4.0)
    return _l(b.moved(Location((FX - 6.0, yl, H(hl)))), spec)


def glovebox_strip(spec):
    """Chrome strip across the glovebox lid about 57 % up it (Oliver's kf143, kf145)."""
    y0, y1, h0, h1 = GLOVE
    s = xprism(G.rounded_rect(y0 + 10.0, y1 - 10.0, H(GLOVE_STRIP_H) - 2.6, H(GLOVE_STRIP_H) + 2.6, 2.5), FX - 9.0, FX - 6.0)
    return _l(s, spec)


def facia_end_fittings(side):
    """Positions on the facia's left end beside the door (Oliver's kf127, kf128, kf154)."""
    return (FACIA_W - 22.0, 798.0), (FACIA_W - 22.0, 826.0)


def facia_end_dome(spec):
    """The chrome domed fitting on the facia's left end beside the door (Oliver's kf127, kf128, kf154)."""
    (yd, hd), _ = facia_end_fittings(1)
    from mgb.chassis_geom import xrev
    d = xrev([(0.0, 0.0), (11.0, 0.0), (10.5, -3.0), (7.0, -7.0), (0.0, -8.5)])
    return _l(d.moved(Location((FX - BL.FACIA_T, yd, H(hd)))), spec)


def facia_end_knob(spec):
    """The small black knob above it."""
    _, (yk, hk) = facia_end_fittings(1)
    from mgb.chassis_geom import xrev
    k = xrev([(0.0, 0.0), (3.0, 0.0), (3.0, -6.0), (6.5, -8.0), (6.5, -16.0), (5.0, -18.0), (0.0, -18.0)])
    return _l(k.moved(Location((FX - BL.FACIA_T, yk, H(hk)))), spec)


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


def _grille():
    xt = FX - 20.0
    zt = H(FACIA_H[0] + 20.0)
    zb = St.TUNNEL[1][4] + 4.0
    return xt, zt, zb, (0.0, (zt + zb) / 2 + 10.0, 150.0, 112.0)


def speaker_grille(spec):
    """Radio speaker grille's chrome frame in the console (Oliver's kf122, kf145): an octagonal (chamfered rectangle)
    frame; the mesh inside is speaker-mesh."""
    xt, zt, zb, (gy, gz, gw, gh) = _grille()
    frame = xprism(_chamfered(gy, gz, gw, gh, 24.0), xt - 9.0, xt - 4.0) - xprism(_chamfered(gy, gz, gw - 14.0, gh - 14.0, 19.0), xt - 10.0, xt - 3.0)
    return _l(frame, spec)


def speaker_mesh(spec):
    """The grille's fine mesh: close vertical ribs in a champagne-silver finish (Oliver's kf122, kf145 zoomed)."""
    xt, zt, zb, (gy, gz, gw, gh) = _grille()
    ribs = []
    yy = gy - gw / 2 + 7.0
    while yy < gy + gw / 2 - 7.0:
        ribs.append(box(xt - 6.5, xt - 4.5, yy - 0.7, yy + 0.7, gz - gh / 2 + 6.0, gz + gh / 2 - 6.0))
        yy += 2.6
    back = box(xt - 4.5, xt - 3.8, gy - gw / 2 + 6.0, gy + gw / 2 - 6.0, gz - gh / 2 + 6.0, gz + gh / 2 - 6.0)
    mesh = G.fuse(ribs + [back]) & xprism(_chamfered(gy, gz, gw - 12.0, gh - 12.0, 20.0), xt - 8.0, xt - 3.0)
    return _l(mesh, spec)


def _console_controls():
    """(y, z) of the console's three controls round the grille (Oliver's kf122, kf145): a small black knob top left,
    a black pull knob bottom right, a small chrome toggle bottom left (the driver's left is the car's left)."""
    xt, zt, zb, (gy, gz, gw, gh) = _grille()
    return {"knob": (gy + gw / 2 - 4.0, gz + gh / 2 + 12.0), "pull": (gy - gw / 2 + 4.0, gz - gh / 2 - 14.0),
            "toggle": (gy + gw / 2 - 4.0, gz - gh / 2 - 14.0)}


def console_knobs(spec):
    """The console's black knobs: the small round knob top left and the pull knob bottom right."""
    xt = FX - 20.0
    c = _console_controls()
    from mgb.chassis_geom import xrev
    k1 = xrev([(0.0, 0.0), (3.0, 0.0), (3.0, -4.0), (7.0, -5.0), (7.0, -12.0), (5.5, -14.0), (0.0, -14.0)]).moved(Location((xt - 4.0, *c["knob"])))
    k2 = xrev([(0.0, 0.0), (2.5, 0.0), (2.5, -10.0), (6.5, -12.0), (7.0, -20.0), (5.0, -22.0), (0.0, -22.0)]).moved(Location((xt - 4.0, *c["pull"])))
    return _c([k1, k2], spec)


def console_toggle(spec):
    """The console's small chrome toggle switch: its bush and locking ring and the lever."""
    xt = FX - 20.0
    y, z = _console_controls()["toggle"]
    from mgb.chassis_geom import xrev
    b = xrev([(0.0, 0.0), (8.0, 0.0), (8.0, -2.5), (5.0, -2.5), (5.0, -8.0), (0.0, -8.0)])
    lever = rod((-8.0, 0.0, 0.0), (-24.0, 0.0, 4.0), 1.8)
    return _l((b + lever).moved(Location((xt - 4.0, y, z))), spec)


DASH_TOP_W = 500.0                             # inside the doors' top corners


def dash_top(spec):
    """Padded black top of the scuttle from the crash roll forward to the screen's foot (Oliver's kf121, kf143; his
    scan, 900-930 above the road from x -800 to -600): a thin vinyl pad over the scuttle's top surface."""
    from build123d import Solid, Vector, Wire
    n = 14
    W = DASH_TOP_W
    ys = [-W + 2 * W * k / n for k in range(n + 1)]
    xr = FX - 24.0
    xf = max(S.screen_base(0.0)[0], S.screen_base(W)[0]) - 35.0
    wires = []
    for k in range(7):
        x = xr + (xf - xr) * k / 6
        top = [(y, H(S.top_h(x, y)) + 7.0) for y in ys]
        bot = [(y, H(S.top_h(x, y)) + 0.4) for y in reversed(ys)]
        wires.append(Wire.make_polygon([Vector(x, a, b) for a, b in top + bot], close=True))
    pad = Solid.make_loft(wires, ruled=True)
    plan = [(xr, -W), (xr, W)] + [(S.screen_base(y)[0] - 35.0, y) for y in reversed(ys)]
    pad = pad & zprism(plan, H(800.0), H(1000.0))
    return _l(pad, spec)


# ---- seats ------------------------------------------------------------------------------------------------------------
# Black leather seats with red piping, as on Oliver's car (kf075, kf120, kf129-135, kf140; his body scan, sections at
# y -350 and 385): a deep cushion rising from about 405 mm above the road at the squab to a rolled front edge at about
# 512, with a piped centre panel of six fore-and-aft pleats, a plain front roll and plain bolsters; a shield-shaped
# squab raked back 24 deg (its front face from about x -1440 at the cushion to -1640 at the top, 885 above the road),
# its top rounded to a large radius, a piped centre panel of six vertical pleats in its lower two-thirds under a plain
# upper panel, piping round the face and a top roll piped on both edges.
SEAT_Y = 380.0                               # between the floor's runner captive nuts (y 300 and 470)
SEAT_W = 400.0                               # inside the sill carpet and the rear loom along the sill
CUSH_X = (-1000.0, -1432.0)                  # front edge, rear edge
CUSH_TOP = [(-1432.0, 405.0), (-1300.0, 432.0), (-1150.0, 468.0), (-1075.0, 497.0), (-1035.0, 510.0), (-1000.0, 505.0)]
CUSH_BOT = ((-1000.0, 352.0), (-1432.0, 300.0))
CUSH_PANEL = (130.0, -1408.0, -1140.0)       # centre panel half-width and fore/aft extent (the front roll ahead of it, kf140)
SQUAB_RAKE = 24.0
SQUAB_BASE = (-1440.0, 420.0)                # front face's foot (x, height above the road), over the heelboard's step
SQUAB_LEN = 520.0
SQUAB_T = (96.0, 78.0)                       # thickness at the foot and under the top roll
SQUAB_TOP_R = 150.0
SQUAB_PANEL = (125.0, 40.0, 335.0)           # centre panel half-width, foot and head (up the squab)
PLEAT_N = 6


def cush_top(x):
    """Height above the road of the cushion's top at x."""
    xs, hs = zip(*CUSH_TOP)
    return float(__import__("numpy").interp(x, xs, hs))


def _squab_outline(d=0.0):
    """Front elevation (u across, w up the squab) of the shield-shaped squab, inset d."""
    w2 = SEAT_W / 2 - d
    top = SQUAB_LEN - d
    pts = [(-w2 + 8.0, d), (w2 - 8.0, d), (w2, 120.0), (w2, top - SQUAB_TOP_R), (w2 - 30.0, top), (-w2 + 30.0, top), (-w2, top - SQUAB_TOP_R),
           (-w2, 120.0)]
    return B.fillet_poly(pts, [12.0, 12.0, 0.0, SQUAB_TOP_R - d * 0.5, 60.0, 60.0, SQUAB_TOP_R - d * 0.5, 0.0], 8)


def _cushion_solid(side):
    y = side * SEAT_Y
    w = SEAT_W / 2
    (xf, hf), (xr, hr) = CUSH_BOT
    prof = [(xr, H(hr)), (xf, H(hf)), (xf, H(470.0))] + [(x, H(h)) for x, h in reversed(CUSH_TOP)]
    prof = B.fillet_poly(prof, [6.0, 10.0, 0.0] + [0.0] * (len(CUSH_TOP) - 2) + [36.0, 10.0], 6)
    c = yprism(prof, y - w, y + w)
    plan = B.fillet_poly([(xr, y - w), (xf, y - w), (xf, y + w), (xr, y + w)], [16.0, 46.0, 46.0, 16.0], 6)
    c = c & zprism(plan, H(250.0), H(560.0))
    c2 = tryfillet(c, c.edges().filter_by(Axis.X), 18.0)          # round the top's side edges (the welts)
    return c2


def _top_band(x0, x1, dz0, dz1, n=14):
    """(x, z) band following the cushion top from x0 to x1, dz0..dz1 about it."""
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    return [(x, H(cush_top(x)) + dz0) for x in xs] + [(x, H(cush_top(x)) + dz1) for x in reversed(xs)]


def _pleat_ys(side):
    y = side * SEAT_Y
    hw = CUSH_PANEL[0]
    return [y - hw + 2 * hw * k / PLEAT_N for k in range(1, PLEAT_N)]


def seat_cushion(side):
    def build(spec):
        """Seat cushion (Haynes Sec 54; Oliver's kf075, kf131, kf140; scan sections): a deep sprung cushion in black
        leather rising to a rolled front edge, the centre panel of six fore-and-aft pleats (sewn grooves between
        them), plain bolsters each side, the plain front roll ahead of the panel."""
        c = _cushion_solid(side)
        _, x0, x1 = CUSH_PANEL
        for yy in _pleat_ys(side):                                # the pleats' sewn grooves
            c = c - yprism(_top_band(x0 + 6.0, x1 - 6.0, -3.0, 6.0), yy - 1.3, yy + 1.3)
        for yy in (side * SEAT_Y - CUSH_PANEL[0], side * SEAT_Y + CUSH_PANEL[0]):   # panel seams (piped)
            c = c - yprism(_top_band(x0, x1, -3.5, 6.0), yy - 2.2, yy + 2.2)
        w = SEAT_W / 2
        c = c - xprism([(side * SEAT_Y - w - 1, H(cush_top(x1)) - 4.0), (side * SEAT_Y + w + 1, H(cush_top(x1)) - 4.0),
                        (side * SEAT_Y + w + 1, H(cush_top(x1)) + 8.0), (side * SEAT_Y - w - 1, H(cush_top(x1)) + 8.0)],
                       x1 - 2.2, x1 + 2.2)                         # front roll seam, across the cushion (kf140)
        return _l(c, spec)
    return build


def _squab_loc(side):
    return Location((SQUAB_BASE[0], side * SEAT_Y, H(SQUAB_BASE[1]))) * Rot(0, -SQUAB_RAKE, 0)


def _squab_local():
    """Squab in its own frame: front face on x 0 (x forward), y across, z up the squab; thicker at the foot."""
    t0, t1 = SQUAB_T
    out = _squab_outline()
    body = xprism(out, -t0, 0.0)
    taper = yprism([(-t0 - 5.0, -5.0), (5.0, -5.0), (5.0, SQUAB_LEN + 5.0), (-t1, SQUAB_LEN + 5.0), (-t0, 200.0)], -SEAT_W, SEAT_W)
    body = body & taper
    body = tryfillet(body, body.edges().filter_by_position(Axis.X, -0.5, 0.5), 24.0)
    return body


def _squab_pleat_us():
    hw = SQUAB_PANEL[0]
    return [-hw + 2 * hw * k / PLEAT_N for k in range(1, PLEAT_N)]


def seat_squab(side):
    def build(spec):
        """Seat squab (back): the shield-shaped back raked 24 deg, its rounded top, the piped centre panel of six
        vertical pleats in the lower two-thirds under a plain upper panel, on a hinged frame (Oliver's kf075, kf130,
        kf135)."""
        s = _squab_local()
        hw, w0, w1 = SQUAB_PANEL
        for u in _squab_pleat_us():
            s = s - box(-2.5, 4.0, u - 1.3, u + 1.3, w0 + 4.0, w1 - 4.0)
        for u in (-hw, hw):
            s = s - box(-3.0, 4.0, u - 2.2, u + 2.2, w0, w1)
        s = s - box(-3.0, 4.0, -hw, hw, w1 - 2.2, w1 + 2.2)
        s = s - box(-3.0, 4.0, -hw, hw, w0 - 2.2, w0 + 2.2)
        return _l(_squab_loc(side) * s, spec)
    return build


def seat_piping(side):
    def build(spec):
        """Red piping (Oliver's kf075, kf131, kf140): on the cushion round its top edge, along both sides of the centre
        panel and across the front roll's seam; on the squab round the face, round the centre panel and along both
        edges of the top roll."""
        y = side * SEAT_Y
        w = SEAT_W / 2
        rp = 2.0                          # QA fix 2: thinner piping (kf129, kf131)
        _, x0, x1 = CUSH_PANEL
        parts = []
        for yy in (y - CUSH_PANEL[0], y + CUSH_PANEL[0]):
            xs = [x0 + (x1 - x0) * k / 12 for k in range(13)]
            parts.append(swept_rod([(x, yy, H(cush_top(x)) - 0.8) for x in xs], rp))
        parts.append(rod((x1, y - w + 6.0, H(cush_top(x1)) - 5.0), (x1, y + w - 6.0, H(cush_top(x1)) - 5.0), rp))   # across
        xs = [CUSH_X[1] + 30.0 + (CUSH_X[0] - 60.0 - CUSH_X[1]) * k / 14 for k in range(15)]
        for yy in (y - w + 4.0, y + w - 4.0):                    # the welts along the top's side edges
            parts.append(swept_rod([(x, yy, H(cush_top(x)) - 12.0) for x in xs], rp))
        # squab: round the face (inset), round the panel, the top roll's two edges
        face = _squab_outline(20.0)
        loop = [(1.0, u, ww) for u, ww in face]
        loc = _squab_loc(side)
        parts.append(loc * swept_rod(loop + loop[:1], rp))
        hw, w0, w1 = SQUAB_PANEL
        parts.append(loc * swept_rod([(1.0, -hw, w0), (1.0, -hw, w1), (1.0, hw, w1), (1.0, hw, w0), (1.0, -hw, w0)], rp))
        roll = [(u, ww) for u, ww in _squab_outline(4.0) if ww > SQUAB_LEN - SQUAB_TOP_R - 30.0]
        roll.sort(key=lambda p: p[0])
        t1 = SQUAB_T[1]
        parts.append(loc * swept_rod([(-t1 + 6.0, u, ww - 6.0) for u, ww in roll], rp))
        return _c(parts, spec)
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
        (xf, hf), (xr, hr) = CUSH_BOT

        def zp(x):                                              # the cushion pan under the sloping cushion
            return H(hr + (hf - hr) * (x - xr) / (xf - xr)) - 2.0
        loop = [(CUSH_X[0] - 15.0, y - SEAT_W / 2 + 20.0), (CUSH_X[0] - 15.0, y + SEAT_W / 2 - 20.0),
                (CUSH_X[1] + 15.0, y + SEAT_W / 2 - 20.0), (CUSH_X[1] + 15.0, y - SEAT_W / 2 + 20.0)]
        loop = [(a, b, zp(a)) for a, b in loop + loop[:1]]
        parts.append(swept_rod(loop, 8.0))
        for yy in (y - 85.0, y + 85.0):                          # legs from the runners to the pan
            for xx in (-1060.0, -1290.0):
                parts.append(rod((xx, yy, zf + 20.0), (xx, yy, zp(xx) - 6.0), 7.0))
        parts.append(rod((-1030.0, y - 100.0, zf + 26.0), (-1010.0, y - 30.0, zf + 26.0), 4.0))   # adjuster bar
        return _c(parts, spec)
    return build


# ---- carpets -------------------------------------------------------------------------------------------------------
CT = 6.0


CARPET_Y = S.SILL_INNER_Y - 4.0 - CT - 0.4      # floor carpets' outer edge, against the sill carpet


def floor_carpet(side):
    def build(spec):
        """Floor carpet on the floor half and the toe board (Oliver's kf151, kf153: black, its edges bound in black
        vinyl - the binding is floor-binding)."""
        zf = U.FLOOR_Z + St.T + 0.2
        yi = St.tunnel_halfwidth(-1000.0, zf) + 2.0
        c = box(U.HEELBOARD_X + 3.0, U.TOE_FOOT[0], yi, CARPET_Y, zf + 7.2, zf + 7.2 + CT)
        (xf, _), (xt, zt) = U.TOE_FOOT, U.TOE_TOP
        toe = G.sheet_y([(xt - 3.0, zt + 1.5), (xf + 2.0, zf + 7.2 + CT)], -CT, 150.0, CARPET_Y, 2.0)
        return _c([St._side(c, side), St._side(toe, side)], spec)
    return build


HEEL_MAT = (-700.0, -530.0, -475.0, -245.0)     # (x0, x1, y0, y1): the driver's heel mat under the pedals (kf151), outboard of the tunnel


def bulkhead_felt(spec):
    """Black felt over the bulkhead's cabin face in both footwells (Oliver's kf145, kf151: black behind the pedals,
    where the body colour would show): a copy of the bulkhead panel 3 mm into the cabin, with all its holes for the
    pedal box, pedal arms, column, harness and pipes, from the toe boards up under the scuttle."""
    class _Id:
        id = spec.id
    b = St.bulkhead(_Id())
    f = b.moved(Location((-3.0, 0.0, 0.0)))
    f = f & box(St.BH_X - 7.0, St.BH_X - St.T - 0.2, -S.SILL_INNER_Y + 7.5, S.SILL_INNER_Y - 7.5, U.TOE_TOP[1] + 2.0, FELT_TOP)
    # cut round the fittings bolted to the bulkhead's cabin face: the column's toe mount and the accelerator's bracket
    from pathlib import Path
    from mgb import spec as SP
    from parts.fuel import throttle as TH
    br = TH.pedal_bracket(SP.load_all(Path(__file__).resolve().parents[2] / "specs")["fuel.throttle.pedal-bracket"])
    for q in (St.column_toe_mount(_Id()), br):
        bb = q.bounding_box()
        f = f - box(bb.min.X - 3.0, bb.max.X + 3.0, bb.min.Y - 3.0, bb.max.Y + 3.0, bb.min.Z - 3.0, bb.max.Z + 3.0)
    # QA fix 2 (kf151: the body colour still showed above the pedals): on up under the shelf and over the upper face's
    # cabin side to the scuttle, with the upper face's openings (heater, screws, wiper motor, bonnet cable) and the
    # shelf's drain tubes left clear
    yc = min(St.BH_STEP_Y, S.SILL_INNER_Y - 7.5)
    zs = St.Z_SHELF
    under = box(St.BH2_X - St.T - 3.0, St.BH_X - St.T - 0.2, -yc, yc, zs - 3.0, zs - 0.2)
    for yy in (-430.0, 430.0):
        under = under - zcyl(11.0, zs - 4.0, zs + 1.0, St.BH2_X + 40.0, yy)
    ys = [-yc + 2 * yc * k / 16 for k in range(17)]
    prof = [(yc, zs - 3.0)] + [(y, St._upper_top_z(y) - St.T - 3.0) for y in reversed(ys)] + [(-yc, zs - 3.0)]
    face = xprism(prof, St.BH2_X - St.T - 3.0, St.BH2_X - St.T - 0.2)
    top = [(y, St._upper_top_z(y)) for y in ys]               # and under the upper face's flange turned back at the top
    face = G.fuse([face] + [xprism([(a[0], a[1] - St.T - 3.0), (b[0], b[1] - St.T - 3.0), (b[0], b[1] - St.T - 0.2),
                                    (a[0], a[1] - St.T - 0.2)], St.BH2_X - 40.0, St.BH2_X - St.T - 2.9)
                            for a, b in zip(top, top[1:])])
    zh = zs + 60.0
    face = face - box(St.BH2_X - 10.0, St.BH2_X + 5.0, -175.0, 110.0, zh - 25.0, zh + 110.0)       # heater opening, screws
    mx, my, mz = BL.WIPER_MOTOR
    face = face - box(St.BH2_X - 10.0, St.BH2_X + 5.0, my - 80.0, yc + 5.0, zs + St.T + 2.0, mz + 80.0)
    face = face - xcyl(9.0, St.BH2_X - 10.0, St.BH2_X + 5.0, 470.0, H(700.0))
    return _c([f, under, face], spec)


FELT_TOP = St.Z_SHELF - 0.5                    # QA fix 2: up to the shelf (was -20, which left red showing, kf151)


def heel_mat(spec):
    """Black ribbed rubber heel mat on the driver's floor carpet under the pedals (Oliver's kf151: about 330 x 200)."""
    x0, x1, y0, y1 = HEEL_MAT
    z = U.FLOOR_Z + St.T + 0.2 + 7.2 + CT
    m = zprism(G.rounded_rect(x0, x1, y0, y1, 10.0), z, z + 3.0)
    for k in range(1, 12):                                       # shallow ribs across it
        xx = x0 + (x1 - x0) * k / 12
        m = m - box(xx - 1.2, xx + 1.2, y0 + 14.0, y1 - 14.0, z + 2.0, z + 4.0)
    return _l(m, spec)


def floor_binding(side):
    def build(spec):
        """Black vinyl binding along the floor carpets' exposed edges: the rear edge at the heelboard, the toe carpet's
        top edge at the bulkhead (Oliver's kf151, kf153)."""
        zf = U.FLOOR_Z + St.T + 0.2 + 7.2 + CT
        yi = St.tunnel_halfwidth(-1000.0, zf) + 2.0
        (xf, _), (xt, zt) = U.TOE_FOOT, U.TOE_TOP
        rear = ycyl(3.5, yi + 10.0, CARPET_Y - 2.0, U.HEELBOARD_X + St.T + CT + 4.5, zf - 2.0)
        top = ycyl(3.5, 160.0, CARPET_Y - 2.0, xt - 5.0, zt + 1.0)
        return _c([St._side(rear, side), St._side(top, side)], spec)
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


def _cockpit_w(x):
    """Half-width of the cockpit opening at x (body_shell_layout COCKPIT_W, without the corner rounding)."""
    import numpy as np
    xs, ws = zip(*sorted(S.COCKPIT_W))
    return float(np.interp(x, xs, ws))


SHELF_TOP = U.TONNEAU_Z + St.T + 5.5          # the shelf carpet's underside (clear of the battery covers' rims)
STEP_TOP = U.HEEL_STEP_Z
REAR_WALL_X = min(S.REAR_BULKHEAD_X, S.COCKPIT_REAR_X) + 0.4   # the rear wall trim's back face
QUARTER_IN = 14.0                             # side trim boards this far inside the cockpit opening's edge
ARCH_R = 430.0 + St.T                         # the wheel houses' arched band, outside (structure.rear_wheelhouse)


def _quarter_y(x):
    return _cockpit_w(x) - QUARTER_IN


def _hump_top(x):
    """Top of the rear wheel house's band at x (car z), or None ahead of it."""
    d = x - CL.REAR_AXLE_X
    if abs(d) >= ARCH_R:
        return None
    return CL.WHEEL_Z + math.sqrt(ARCH_R * ARCH_R - d * d)


def _hump_x():
    """x where the band's carpet rises through the shelf's carpet."""
    z = SHELF_TOP + CT
    return CL.REAR_AXLE_X + math.sqrt(max(ARCH_R ** 2 - (z - CL.WHEEL_Z) ** 2, 0.0))


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or math.dist(p, out[-1]) > 0.05:
            out.append(p)
    return out


def rear_carpet(spec):
    """Black carpet behind the seats (Oliver's kf134, kf156, kf157; QA fix round 1): over the heelboard's lower riser,
    the step under the squabs' feet and the tunnel's carry-on through it, up the upper riser and over the shelf
    (tonneau floor, lifted to reach the battery access covers, Haynes photo 2.1) out to the side trim, ahead of the
    wheel house humps."""
    yo = CARPET_Y
    hb, sf = U.HEELBOARD_X + St.T, U.SHELF_FRONT_X + St.T
    tun = _dedupe(St.tunnel_profile(St.TUNNEL[-1], flange=0.0))
    tun_poly = xprism(tun, sf - 20.0, hb + 40.0)
    parts = []
    lower = box(hb + 0.3, hb + 0.3 + CT, -yo, yo, U.FLOOR_Z + St.T + 7.2, STEP_TOP + CT) - \
        xprism(G.band(tun, -CT - 0.5), hb - 1.0, hb + 20.0) - xprism(tun, hb - 1.0, hb + 20.0)
    parts.append(lower)
    step = box(sf + 0.3, hb + 0.3, -yo, yo, STEP_TOP + 0.3, STEP_TOP + 0.3 + CT) - xprism(St.tunnel_hump(STEP_TOP, 0.4)[0], sf, hb + 1.0)
    parts.append(step)
    above = _dedupe(St._tunnel_above(STEP_TOP))
    hump = xprism(St.tunnel_hump(STEP_TOP, CT + 0.4)[0], sf + 0.3, hb + 0.3) - xprism(St.tunnel_hump(STEP_TOP, 0.4)[0], sf, hb + 1.0)
    parts.append(hump)                                                        # the tunnel's carry-on
    riser = box(sf + 0.3, sf + 0.3 + CT, -yo, yo, STEP_TOP, SHELF_TOP + CT) - xprism(G.band(above, -CT - 0.5), sf - 1, sf + 20)
    riser = riser - xprism(above + [(-130.0, STEP_TOP - 5.0), (130.0, STEP_TOP - 5.0)], sf - 1, sf + 20)
    parts.append(riser)
    xh = _hump_x()
    parts.append(box(REAR_WALL_X + 3.5, sf + 0.3, -St.RWH_Y + CT + 0.6, St.RWH_Y - CT - 0.6, SHELF_TOP, SHELF_TOP + CT))   # the shelf
    qy = min(_quarter_y(x) for x in (sf, xh)) - 1.0
    for s_ in (1, -1):                                        # out to the side trim ahead of the humps
        parts.append(St._side(box(xh, sf + 0.3, St.RWH_Y + 2.0, qy, SHELF_TOP, SHELF_TOP + CT), s_))
    return _c(parts, spec)


def arch_carpet(side):
    def build(spec):
        """Carpet over the rear wheel house's hump where it rises through the shelf at the cockpit's rear corner
        (Oliver's kf134, kf156): over the arched band out to the side trim and down its inner wall to the shelf."""
        xh = _hump_x()
        x0 = REAR_WALL_X + 3.5
        qy = min(_quarter_y(x) for x in (x0, xh)) - 1.0
        ax, az = CL.REAR_AXLE_X, CL.WHEEL_Z
        band = ycyl(ARCH_R + 0.3 + CT, St.RWH_Y - CT, qy, ax, az) - ycyl(ARCH_R + 0.3, St.RWH_Y - CT - 1, qy + 1, ax, az)
        band = band & box(x0, xh + 1.0, St.RWH_Y - CT - 1, qy + 1, SHELF_TOP, SHELF_TOP + 2000.0)
        n = 16
        arc = [(x0 + (xh - x0) * k / n, az + math.sqrt(max(ARCH_R ** 2 - (x0 + (xh - x0) * k / n - ax) ** 2, 0.0)))
               for k in range(n + 1)]
        wall = yprism([(xh, SHELF_TOP), (x0, SHELF_TOP)] + arc, St.RWH_Y - CT - 0.3, St.RWH_Y - 0.3)
        return _l(St._side(G.fuse([band, wall]), side), spec)
    return build


def kick_panel(side):
    def build(spec):
        """Kick panel (Oliver's kf121, kf128, kf151, kf153): a black vinyl-covered board closing the footwell's side
        from the bulkhead back to the hinge pillar's shut line, from the sill carpet up under the scuttle, over the
        hinge pillar's kick plate."""
        y0 = S.SILL_INNER_Y - 4.0
        xf = S.DOOR_FRONT_X - S.GAP / 2
        zf = U.FLOOR_Z + St.T + 7.2
        zs = H(St.TREAD_H) + CT + 0.6                                 # above the sill carpet's tread
        board = box(xf + 2.0, St.BH_X - 4.0, y0 - 3.0, y0, zs, FELT_TOP)      # under the bulkhead's upper panel
        return _l(St._side(board, side), spec)
    return build


def sill_cover(side):
    def build(spec):
        """Carpet over the inner sill (Oliver's kf128, kf131, kf151): down its cockpit face from the tread to the
        floor carpet, over the tread out to the door's shut line, with a black vinyl-bound edge (the binding is the
        part's outer roll)."""
        yi = S.SILL_INNER_Y
        x0, x1 = U.SHELF_FRONT_X + St.T + CT + 0.5, St.BH_X - 4.0
        zt = H(St.TREAD_H)
        from mgb import wiring_layout as WL
        zf = WL.SILL_Z + 14.0                                       # over the rear loom run along the sill's foot
        face = box(x0, x1, yi - 4.0 - CT, yi - 4.0, zf, zt + CT + 0.3)
        face = face - box(WL.HEEL_X - 12.0, WL.HEEL_X + 12.0, yi - 5.0 - CT, yi - 3.0, zf - 1.0, zt + CT + 1.0)   # the loom's climb
        xa, xb = S.DOOR_REAR_X + 6.0, S.DOOR_FRONT_X - 6.0
        top = box(xa, xb, yi - 4.0 - CT, St.SILL_OUT_Y - 3.0, zt + St.T + 0.3, zt + St.T + 0.3 + CT)
        edge = xcyl(4.0, xa, xb, St.SILL_OUT_Y - 4.0, zt + St.T + 0.3 + CT / 2)
        return _l(St._side(G.fuse([face, top, edge]), side), spec)
    return build


def quarter_trim(side):
    def build(spec):
        """Rear quarter trim (Oliver's kf069, kf075, kf134): black vinyl boards lining the cockpit's side from the shut
        pillar back round the rear corner, QUARTER_IN inside the opening's edge (body_shell cockpit_outline), from the
        sill (ahead of the shelf) or the shelf and wheel house hump up under the rim roll, and a finisher down the shut
        pillar's inboard edge."""
        x0 = S.DOOR_REAR_X - 8.0
        pts = [(x, y) for x, y in B.cockpit_outline(-QUARTER_IN) if x < x0 and y * side > St.RWH_Y + 8.0]
        pts.sort(key=lambda p: -p[0])
        pts = [(x0, side * _quarter_y(x0))] + pts
        dense = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            n = max(1, int(math.dist((xa, ya), (xb, yb)) / 25.0))
            dense += [(xa + (xb - xa) * k / n, ya + (yb - ya) * k / n) for k in range(n)]
        dense.append(pts[-1])
        sf = U.SHELF_FRONT_X + St.T + CT

        def zb(x):
            z = H(St.TREAD_H) if x > sf else SHELF_TOP + CT
            ht = _hump_top(x)
            return max(z, ht + 0.3 + CT) if ht is not None and x <= sf else z

        def zt(x, y):
            return H(S.top_h(x, abs(y) + QUARTER_IN - 2.0) - 16.0)
        boards = []
        for (xa, ya), (xb, yb) in zip(dense, dense[1:]):
            L = math.dist((xa, ya), (xb, yb))
            if L < 0.5:
                continue
            za0, zb0, za1, zb1 = zb(xa), zb(xb), zt(xa, ya), zt(xb, yb)
            if min(za1 - za0, zb1 - zb0) < 5.0:
                continue
            ang = math.degrees(math.atan2(yb - ya, xb - xa))
            # the board's face in its own (u along it, v up) plane, 3 mm thick toward the cockpit's outside
            seg = yprism([(0.0, za0), (L, zb0), (L, zb1), (0.0, za1)], 0.0, 3.0)
            boards.append(Location((xa, ya, 0.0)) * Rot(0, 0, ang) * seg)
        fin = box(x0 - 2.0, x0 + 6.0, S.SILL_INNER_Y - 4.0, _quarter_y(x0) + 3.0, H(St.TREAD_H), H(S.top_h(x0, _quarter_y(x0)) - 16.0))
        return _c(boards + [St._side(fin, side)], spec)
    return build


def rear_wall_trim(spec):
    """Rear wall trim (Oliver's kf134, kf156, kf157): a black vinyl board across the back of the cockpit on the rear
    bulkhead, from the shelf (and the humps at the corners) up under the deck's edge."""
    x = REAR_WALL_X
    qy = _quarter_y(x + 10.0) - 3.0
    ht = _hump_top(x + 2.0)
    zh = (ht + 0.3 + CT) if ht is not None else SHELF_TOP + CT
    n = 20
    ys = [-qy + 2 * qy * k / n for k in range(n + 1)]
    top = [(y, H(S.top_h(x + 3.0, abs(y)) - 28.0)) for y in ys]
    bot = [(qy, zh), (St.RWH_Y, zh), (St.RWH_Y, SHELF_TOP + CT), (-St.RWH_Y, SHELF_TOP + CT), (-St.RWH_Y, zh), (-qy, zh)]
    poly = bot + top
    return _l(xprism(poly, x, x + 3.0), spec)


# ---- door trim ----------------------------------------------------------------------------------------------------------
# The door card as on Oliver's car (kf128, kf131, kf137): one black vinyl hardboard panel over the whole inner face from
# the sill to under the capping, a red-piped seam across it about 22 % down (mgb.cockpit_layout CARD_SEAM_H) with two
# stitched lines in the panel above, the chrome inner release lever at the front top under the capping, the window
# winder at the front just below the seam, the chrome-ended black pull handle mid-door below the seam. The card is a
# flat board where the door's inner panel is upright (inboard of the regulator and remote control plates behind it,
# parts/body/mechanisms.py) and follows the tumblehome above and below.
CARD_T = 3.0
CARD_TOP_H = C.WAIST_H - 10.0                 # tucked up into the capping roll
CARD_BOT_H = S.DOOR_BOTTOM_H + 8.0


def _card_flat_y():
    from parts.body import mechanisms as M
    return M.inner_y(*M.QUAD_PIVOT) - 0.6


def card_face_y(h):
    """|y| of the door card's cockpit face at height h (the most inboard of the door's length)."""
    xs = [S.DOOR_FRONT_X - 20.0 - k * (S.DOOR_FRONT_X - S.DOOR_REAR_X - 40.0) / 6 for k in range(7)]
    yo = min(min(S.side_y(x, h) for x in xs) - C.DOOR_IN - 1.4, _card_flat_y())
    ycap = min(S.side_y(x, C.WAIST_H - 30.0) for x in xs) - C.DOOR_IN + 6.0      # the capping roll's centre line
    return max(yo, ycap - 8.0) - CARD_T


def _card_yz():
    hs = [CARD_BOT_H + (CARD_TOP_H - CARD_BOT_H) * k / 40 for k in range(41)]
    return [(card_face_y(h) + CARD_T, H(h)) for h in hs] + [(card_face_y(h), H(h)) for h in reversed(hs)]


def _card_y(side, x, h):
    return side * card_face_y(h)


def door_card(side):
    def build(spec):
        """Door trim pad (Sec 29, early Sports Tourer; Oliver's kf128, kf131): the black vinyl-covered hardboard over
        the inner panel's whole face, the seam's groove across it, held by clips round its edge."""
        out = [(x, H(h)) for x, h in B.door_outline_xz(-10.0)]
        card = xprism(_card_yz(), S.DOOR_REAR_X - 200.0, S.DOOR_FRONT_X + 50.0) & yprism(out, 400.0, 800.0)
        card = card & box(S.DOOR_REAR_X - 200.0, S.DOOR_FRONT_X + 50.0, 400.0, 800.0, H(CARD_BOT_H) - 1, H(CARD_TOP_H) + 1)
        return _l(St._side(card, side), spec)
    return build


def _card_line(side, h, d, x0=None, x1=None):
    """Points along the card face at height h, d mm proud of it, between the door's ends."""
    x0 = x0 if x0 is not None else S.DOOR_REAR_X + 28.0
    x1 = x1 if x1 is not None else S.DOOR_FRONT_X - 26.0
    return [(x0 + (x1 - x0) * k / 6, side * (card_face_y(h) - d), H(h)) for k in range(7)]


def door_card_piping(side):
    def build(spec):
        """Red piping in the card's seam across the door (Oliver's kf128, kf131)."""
        return _l(swept_rod(_card_line(side, CK.CARD_SEAM_H, 0.0), 1.6), spec)          # QA fix 2: thin (kf129, kf131)
    return build


def door_card_stitch(side):
    def build(spec):
        """The two stitched lines across the card's upper panel (black thread in a pressed groove, drawn as a fine
        raised line)."""
        return _c([swept_rod(_card_line(side, h, 0.1), 0.9) for h in CK.CARD_STITCH_H], spec)
    return build


def inner_handle(side):
    def build(spec):
        """Inner door release (Fig 12.13 item 21, early cars; Oliver's kf128, kf131): a chrome lever at the card's
        front top under the capping, pivoted on its round escutcheon at the front and lying back along the door."""
        x, h = CK.INNER_HANDLE
        y = abs(_card_y(side, x, h))
        esc = ycyl(14.0, y - 4.0, y + 0.5, x, H(h)) + ycyl(9.0, y - 9.0, y - 3.9, x, H(h))
        lever = rod((x, y - 8.0, H(h)), (x - 70.0, y - 10.0, H(h) - 6.0), 4.0)
        tip = ycyl(5.5, y - 13.0, y - 7.0, x - 72.0, H(h) - 6.0)
        return _c([St._side(p, side) for p in (esc, lever, tip)], spec)
    return build


def winder(side):
    def build(spec):
        """Window regulator handle (Fig 12.17 item 11, handle and finisher; Oliver's kf128, kf131) on the regulator's
        spindle at the door's front below the seam: the escutcheon, the chrome crank pointing down and back, the
        knob."""
        x, h = CK.WINDER
        y = abs(_card_y(side, x, h))
        esc = ycyl(26.0, y - 3.0, y + 0.3, x, H(h))                                       # escutcheon (Fig 12.17 item 9)
        washer = ycyl(14.0, y - 4.5, y - 3.0, x, H(h))                                    # fibre washer (10)
        boss = esc + washer + ycyl(16.0, y - 12.0, y - 4.5, x, H(h))
        arm = rod((x, y - 10.0, H(h)), (x - 30.0, y - 12.0, H(h) - 72.0), 6.0)
        knob = ycyl(9.0, y - 40.0, y - 12.0, x - 30.0, H(h) - 72.0)
        return _c([St._side(p, side) for p in (boss, arm, knob)], spec)
    return build


def pull_handle(side):
    def build(spec):
        """Door pull handle (Oliver's kf128, kf131): a black grip between two chrome end bosses screwed through the
        card, mid-door below the seam. This part is the grip."""
        x, h = CK.PULL_HANDLE
        L = CK.PULL_HANDLE_L
        y = abs(_card_y(side, x, h))
        grip = rod((x + L / 2 - 10.0, y - 24.0, H(h)), (x - L / 2 + 10.0, y - 24.0, H(h)), 7.5)
        return _l(St._side(grip, side), spec)
    return build


RIM_W, RIM_H = 30.0, 13.0                      # the rim roll's section: flat, flush with the deck's edge (kf070, kf134)


def cockpit_rim(spec):
    """Cockpit rim trim (Oliver's kf069, kf070, kf134, kf156): a flat padded black vinyl roll on the cockpit opening's
    edge behind the doors and round the rear of the cockpit, its top flush with the deck and wing tops, wrapping over
    the edge into the cockpit (QA fix round 1: was a round tube standing proud)."""
    from build123d import FilletPolyline, Plane as Pl, RectangleRounded, Transition, Vector, Wire, sweep
    pts = B.cockpit_outline(-RIM_W / 2 + 4.0)
    xr = S.DOOR_REAR_X - 14.0
    path = [(x, y) for x, y in pts if x < xr]
    left = sorted([p for p in path if p[1] > 0], key=lambda p: -p[0])
    right = sorted([p for p in path if p[1] <= 0], key=lambda p: p[0])
    out = []
    for x, y in left + right:
        q = (x, y, H(S.top_h(x, abs(y) + RIM_W / 2 - 4.0)) - RIM_H / 2 + 0.6)
        if not out or math.dist(q, out[-1]) > 12.0:
            out.append(q)
    try:
        vs = [Vector(*p) for p in out]
        wire = Wire(FilletPolyline(*vs, radius=20.0).edges())
        t = wire.tangent_at(0)
        prof = Pl(vs[0], x_dir=(0, 0, 1), z_dir=t) * RectangleRounded(RIM_H, RIM_W, 5.5)
        r = sweep(prof, path=wire, transition=Transition.ROUND)
        if not r.is_valid:
            raise ValueError("invalid sweep")
    except Exception:
        r = swept_rod(out, RIM_H / 2 + 1.0)
    return _l(r, spec)


CAP_H = C.WAIST_H - 6.0                       # capping roll's centre height
CAP_R = 13.0


def _capping_pts(side, dy=0.0, dz=0.0):
    xs = [S.DOOR_FRONT_X - 8.0 - k * (S.DOOR_FRONT_X - S.DOOR_REAR_X - 16.0) / 8 for k in range(9)]
    # QA fix 2 (kf129, kf131): 10 mm further inboard, over the card's top edge, so no body colour shows between them
    return [(x, side * (S.side_y(x, C.WAIST_H - 30.0) - C.DOOR_IN - 4.0 - dy), H(CAP_H) + dz) for x in xs]


def door_capping(side):
    def build(spec):
        """Door top capping: the padded vinyl roll along the door's top over the glass slot."""
        return _l(swept_rod(_capping_pts(side), CAP_R), spec)
    return build


def door_capping_piping(side):
    def build(spec):
        """Red piping along the capping's inboard top edge (Oliver's kf128, kf131)."""
        return _l(swept_rod(_capping_pts(side, 9.5, 9.5), 1.6), spec)                    # QA fix 2: thin (kf129, kf131)
    return build


# ---- tunnel fittings ------------------------------------------------------------------------------------------------
def lever_grommet(spec):
    """Gear lever gaiter (Fig 6.3 item 161; Oliver's kf122, kf145): a short black rubber bellows filling the chrome
    retainer's oval opening, three convolutions narrowing to a collar on the lever."""
    lx = _lever_x()
    z = St.TUNNEL[3][4]
    prof = [(16.0, 0.0), (38.5, 0.0), (38.5, 4.0), (30.0, 9.0), (34.0, 14.0), (24.0, 21.0), (28.0, 26.0), (18.0, 33.0),
            (20.0, 37.0), (12.5, 43.0), (12.5, 50.0), (10.5, 50.0), (10.5, 44.0), (16.0, 37.0), (14.0, 33.0), (24.0, 26.0),
            (20.0, 21.0), (30.0, 14.0), (26.0, 9.0), (34.0, 4.0), (16.0, 4.0)]
    g = zrev(prof)
    from build123d import scale
    g = scale(g, by=(1.45, 1.0, 1.0))                            # oval, as the retainer's opening (116 x 76)
    from mgb import gearbox_layout as GLY
    tilt = math.degrees(math.atan2(GLY.KNOB[0] - GLY.LEVER_BALL[0], GLY.KNOB[2] - GLY.LEVER_BALL[2]))
    return _l(Location((lx - 10.0, 0.0, z + 1.0)) * Rot(0, tilt * 0.5, 0) * g, spec)


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
    "body.interior.speaker-mesh": {"build": speaker_mesh},
    "body.interior.console-knobs": {"build": console_knobs},
    "body.interior.console-toggle": {"build": console_toggle},
    "body.interior.dash-top": {"build": dash_top},
    "body.interior.heel-mat": {"build": heel_mat},
    "body.interior.bulkhead-felt": {"build": bulkhead_felt},
    "body.interior.glovebox-lock": {"build": glovebox_lock},
    "body.interior.facia-end-dome": {"build": facia_end_dome},
    "body.interior.facia-end-knob": {"build": facia_end_knob},
    "body.interior.plaque-badge": {"build": plaque_badge},
    "body.interior.heater-knob-print": {"build": heater_knob_print},
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
    PARTS[f"body.interior.floor-binding-{n}"] = {"build": floor_binding(s_)}
    PARTS[f"body.interior.door-card-{n}"] = {"build": door_card(s_)}
    PARTS[f"body.interior.inner-handle-{n}"] = {"build": inner_handle(s_)}
    PARTS[f"body.interior.winder-{n}"] = {"build": winder(s_)}
    PARTS[f"body.interior.door-capping-{n}"] = {"build": door_capping(s_)}
    PARTS[f"body.interior.door-capping-piping-{n}"] = {"build": door_capping_piping(s_)}
    PARTS[f"body.interior.door-card-piping-{n}"] = {"build": door_card_piping(s_)}
    PARTS[f"body.interior.door-card-stitch-{n}"] = {"build": door_card_stitch(s_)}
    PARTS[f"body.interior.pull-handle-{n}"] = {"build": pull_handle(s_)}
PARTS["body.interior.cockpit-rim"] = {"build": cockpit_rim}
PARTS["body.interior.rear-wall-trim"] = {"build": rear_wall_trim}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.interior.kick-panel-{n}"] = {"build": kick_panel(s_)}
    PARTS[f"body.interior.sill-cover-{n}"] = {"build": sill_cover(s_)}
    PARTS[f"body.interior.quarter-trim-{n}"] = {"build": quarter_trim(s_)}
    PARTS[f"body.interior.arch-carpet-{n}"] = {"build": arch_carpet(s_)}


# ---- inertia-reel seat belts -------------------------------------------------------------------------------------------
# As on Oliver's car (kf069, kf070, kf130, kf132, kf135, kf136, kf140, kf156, kf157): a black reel with a grey end cap on
# each rear wheel house hump in the cockpit's rear corners, the grey webbing up and forward to the upper anchor's loop
# at the top of the cockpit's side just behind the door, down past the squab's outer side to the lower anchor on the
# sill; the buckles on short stalks from the step beside the tunnel between the seats, their red release buttons.
BELT_W = 48.0
BELT_T = 1.6


def _belt_pts(side):
    """Reel centre, upper anchor, lower anchor and buckle base (car frame) for the seat on `side`."""
    xr = _hump_x() - 85.0                                    # on the hump's front slope, clear of the corner trim
    yr = side * (St.RWH_Y + 50.0)
    zr = max(_hump_top(x) for x in (xr - 50.0, xr + 50.0)) + CT + 47.0
    xa = S.DOOR_REAR_X - 44.0
    ya = side * (_quarter_y(xa) - 8.0)
    za = H(S.top_h(xa, abs(ya)) - 78.0)
    xl = S.DOOR_REAR_X - 40.0                                # stowed: hanging down the side trim to the sill's tread
    yl = side * (S.SILL_INNER_Y + 22.0)
    zl = H(St.TREAD_H) + 6.0
    xb = SQUAB_BASE[0] - 30.0
    yb = side * (St.TUNNEL[-1][1] + 28.0)
    zb = STEP_TOP + 0.3 + CT
    return (xr, yr, zr), (xa, ya, za), (xl, yl, zl), (xb, yb, zb)


def _strap(p0, p1, across, w=BELT_W, t=BELT_T):
    """Flat strap from p0 to p1, its width along `across` (made square to the run)."""
    from build123d import Align, Box, Vector
    a, b = Vector(*p0), Vector(*p1)
    d = (b - a)
    L = d.length
    z = d.normalized()
    x = Vector(*across)
    x = (x - z * x.dot(z)).normalized()
    return Plane(origin=a, x_dir=x, z_dir=z).location * Box(w, t, L, align=(Align.CENTER, Align.CENTER, Align.MIN))


def belt_reel(side):
    def build(spec):
        """Inertia reel: the black drum housing on its bracket on the wheel house hump, the axis fore and aft."""
        (xr, yr, zr), *_ = _belt_pts(side)
        drum = xcyl(34.0, xr - 42.0, xr + 42.0, yr, zr)
        bracket = box(xr - 50.0, xr + 50.0, yr - 30.0, yr + 30.0, zr - 44.0, zr - 40.0) + \
            box(xr - 46.0, xr - 42.0, yr - 30.0, yr + 30.0, zr - 44.0, zr + 10.0) + box(xr + 42.0, xr + 46.0, yr - 30.0, yr + 30.0, zr - 44.0, zr + 10.0)
        return _c([drum, bracket], spec)
    return build


def belt_reel_cap(side):
    def build(spec):
        """The reel's grey mechanism cap on its front end."""
        (xr, yr, zr), *_ = _belt_pts(side)
        from mgb.chassis_geom import xrev
        cap = xrev([(0.0, 0.0), (36.0, 0.0), (36.0, 6.0), (30.0, 12.0), (12.0, 16.0), (12.0, 22.0), (0.0, 22.0)])
        return _l(cap.moved(Location((xr + 46.0, yr, zr))), spec)
    return build


def belt_webbing(side):
    def build(spec):
        """Grey webbing: off the reel's top, up and forward to the upper anchor's loop, down past the squab's outer side
        to the lower anchor on the sill."""
        (xr, yr, zr), (xa, ya, za), (xl, yl, zl), _ = _belt_pts(side)
        top = (xr, yr, zr + 34.0 + BELT_T)
        a1 = (xa - 6.0, ya - side * 8.0, za + 10.0)
        s1 = _strap(top, a1, (0.0, 1.0, 0.0))
        s2 = _strap((xa, ya - side * 10.0, za - 10.0), (xl, yl, zl + 8.0), (1.0, 0.0, 0.0), w=40.0)
        return _c([s1, s2], spec)
    return build


def belt_anchors(side):
    def build(spec):
        """The upper anchor's bolt, plate and webbing loop on the cockpit's side, and the lower anchor plate and bolt on
        the sill."""
        _, (xa, ya, za), (xl, yl, zl), _ = _belt_pts(side)
        ys = 1 if side > 0 else -1
        plate = box(xa - 22.0, xa + 22.0, ya - 2.0, ya + 2.0, za - 26.0, za + 26.0)
        loop = box(xa - 30.0, xa + 30.0, ya - ys * 14.0 - 3.0, ya - ys * 14.0 + 3.0, za - 8.0, za + 8.0) + \
            box(xa - 6.0, xa + 6.0, min(ya, ya - ys * 14.0), max(ya, ya - ys * 14.0), za - 6.0, za + 6.0)
        bolt = ycyl(11.0, min(ya, ya - ys * 8.0), max(ya, ya - ys * 8.0), xa, za + 18.0)
        low = box(xl - 30.0, xl + 30.0, yl - 18.0, yl + 18.0, zl - 6.0, zl - 2.0) + zcyl(11.0, zl - 2.0, zl + 6.0, xl, yl)
        return _c([plate, loop, bolt, low], spec)
    return build


def belt_buckle(side):
    def build(spec):
        """Buckle on its stalk from the step beside the tunnel between the seats: the black sleeved stalk leaning up
        and back, the moulded buckle housing at its top."""
        *_, (xb, yb, zb) = _belt_pts(side)
        top = (xb - 40.0, yb, zb + 150.0)
        stalk = rod((xb, yb, zb), top, 8.0)
        foot = box(xb - 22.0, xb + 22.0, yb - 16.0, yb + 16.0, zb, zb + 4.0)
        d = (top[0] - xb, 0.0, top[2] - zb)
        loc = Plane(origin=top, x_dir=(0.0, 1.0, 0.0), z_dir=d).location
        housing = loc * box(-17.0, 17.0, -9.0, 9.0, 0.0, 70.0)
        return _c([stalk, foot, housing], spec)
    return build


def belt_button(side):
    def build(spec):
        """The buckle's red release button on its face (Oliver's kf130, kf140)."""
        *_, (xb, yb, zb) = _belt_pts(side)
        top = (xb - 40.0, yb, zb + 150.0)
        d = (top[0] - xb, 0.0, top[2] - zb)
        loc = Plane(origin=top, x_dir=(0.0, 1.0, 0.0), z_dir=d).location
        return _l(loc * box(-11.0, 11.0, -6.5, 6.5, 69.8, 75.0), spec)      # on the housing's top end
    return build


for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.interior.belt-reel-{n}"] = {"build": belt_reel(s_)}
    PARTS[f"body.interior.belt-reel-cap-{n}"] = {"build": belt_reel_cap(s_)}
    PARTS[f"body.interior.belt-webbing-{n}"] = {"build": belt_webbing(s_)}
    PARTS[f"body.interior.belt-anchors-{n}"] = {"build": belt_anchors(s_)}
    PARTS[f"body.interior.belt-buckle-{n}"] = {"build": belt_buckle(s_)}
    PARTS[f"body.interior.belt-button-{n}"] = {"build": belt_button(s_)}


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
