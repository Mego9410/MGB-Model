"""Bright work and fittings (Haynes Ch 12 Sec 7, 10, 14; Fig 12.1, printed p218): the early chrome bumpers with their
overriders (rubber-faced), spring bars and rear mounting brackets; the early grille: a chrome surround (a wide,
shallow rounded rectangle whose top follows the bonnet's front edge) filled with fine vertical slats, the lower rail,
the centre bar under a plain shield badge (no lettering); the scuttle's slatted air intake; the wing and door chrome
strips; the number plates (blank) and their plinths; the boot lid badge (a plain octagon).

Forms and positions from Oliver's photos 05, 10, 15, 18, 20, 24, 27 and the profile photo 29 (scaled on the
wheelbase); sizes derived (D). The bumpers follow the body's plan outline at their height (mgb.body_shell_layout),
standing a set gap off it, so they wrap round the corners to the wheel arches as on the car.
Drawn in place in the car frame.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Compound, Location, Solid, Vector, Wire

from mgb import body_geom as G, body_layout as BL, body_shell_layout as S, car_layout as CL
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, ycyl, zcyl, zprism
from parts.body import structure as St

H = S.z_of


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


# ---- bumpers ----------------------------------------------------------------------------------------------------------
# Blade centre heights and depths (profile photo 29: front blade 350-405 above the road, rear 430-495; Oliver's photos
# 10, 18): the front blade's face stands 48 mm off the valance at the centre, the rear 70 mm off the rear panel; both
# wrap round the corners and run back along the sides to the wheel arches (photo 29: front ends X 518, rear X -2742).
FRONT_BAR_H = (356.0, 404.0)
REAR_BAR_H = (430.0, 495.0)
BAR_DEPTH = 44.0
FRONT_GAP, REAR_GAP = 34.0, 34.0
FRONT_END_X, REAR_END_X = 528.0, -2745.0
OVR_FRONT_Y = 330.0                          # front overriders (Oliver's photos 10, 15)
OVR_H = {"front": (282.0, 520.0), "rear": (395.0, 605.0)}


def _plan_outline(h, front, gap, n=121):
    """The body's plan outline at height h, offset outward by gap: [(x, y)] from the right-hand end round the nose
    (or tail) to the left-hand end, from plan rays about a point inside the body."""
    cx = 380.0 if front else -2620.0
    pts = []
    for k in range(n):
        a = math.radians(-100.0 + 200.0 * k / (n - 1))
        dx, dy = (math.cos(a), math.sin(a)) if front else (-math.cos(a), -math.sin(a))
        f = lambda t: S.F(cx + dx * t, dy * t, np.full_like(t, h))        # noqa: E731
        t = S._root(f, 0.0, 1300.0)
        pts.append((cx + dx * t, dy * t))
    out = []
    for k in range(n):                       # offset along the outline's normal
        a, b = pts[max(k - 1, 0)], pts[min(k + 1, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = (ty / L, -tx / L) if front else (ty / L, -tx / L)
        out.append((pts[k][0] + nx * gap, pts[k][1] + ny * gap))
    return out


def _bar_path(front):
    h = sum(FRONT_BAR_H if front else REAR_BAR_H) / 2
    pts = _plan_outline(h, front, FRONT_GAP if front else REAR_GAP)
    end = FRONT_END_X if front else REAR_END_X
    keep = [p for p in pts if (p[0] > end if front else p[0] < end)]
    # smooth the path a little (it follows a smooth body but the offset doubles small wiggles)
    xs = np.array([p[0] for p in keep]); ys = np.array([p[1] for p in keep])
    for _ in range(3):
        xs[1:-1] = (xs[:-2] + 2 * xs[1:-1] + xs[2:]) / 4
        ys[1:-1] = (ys[:-2] + 2 * ys[1:-1] + ys[2:]) / 4
    return list(zip(xs.tolist(), ys.tolist()))


def bar_face_x(y, front=True):
    """x of the bumper blade's face at y (on the straight front or rear run)."""
    path = _bar_path(front)
    best = min(path, key=lambda p: abs(p[1] - y))
    return best[0]


def _bar_section(h0, h1):
    """Blade section (u back from the face, h up): a convex face with rolled top and bottom edges returning behind
    to a flange."""
    hm, hh = (h0 + h1) / 2, (h1 - h0) / 2
    pts = []
    for k in range(15):
        t = -math.pi / 2 + math.pi * k / 14
        pts.append((10.0 * (1 - math.cos(t)), hm + hh * math.sin(t)))
    pts += [(BAR_DEPTH * 0.5, h1 - 3.0), (BAR_DEPTH * 0.5 + 2.0, h1 - 6.0), (14.0, hm + hh * 0.6), (14.0, hm - hh * 0.6),
            (BAR_DEPTH * 0.5 + 2.0, h0 + 6.0), (BAR_DEPTH * 0.5, h0 + 3.0)]
    return pts


def _bar(front):
    hs = FRONT_BAR_H if front else REAR_BAR_H
    sec = _bar_section(*hs)
    path = _bar_path(front)
    idx = np.linspace(0, len(path) - 1, 41).round().astype(int)
    wires = []
    for k in idx:
        a, b = path[max(k - 1, 0)], path[min(k + 1, len(path) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty)
        nx, ny = (-ty / L, tx / L) if front else (-ty / L, tx / L)      # inward (behind the face)
        x, y = path[k]
        wires.append(Wire.make_polygon([Vector(x + nx * u, y + ny * u, H(h)) for u, h in sec], close=True))
    b = Solid.make_loft(wires, ruled=False)
    if not b.is_valid:
        b = b.fix()
    return b


def front_bar(spec):
    """Front bumper bar (Fig 12.1 item 1): the chrome blade following the nose 48 mm off it and wrapping round the
    corners back to the wheel arches; holes for the overriders' studs and the spring bars' bolts."""
    b = _bar(True)
    zc = H(sum(FRONT_BAR_H) / 2)
    for y in (-OVR_FRONT_Y, OVR_FRONT_Y, -St.LEG_STEP_Y, St.LEG_STEP_Y):
        x = bar_face_x(y)
        b = b - xcyl(4.4, x - 60.0, x - 6.0, y, zc)
    return _l(b, spec)


def rear_bar(spec):
    """Rear bumper bar (Fig 12.1 item 23), as the front, 70 mm off the rear panel."""
    b = _bar(False)
    zc = H(sum(REAR_BAR_H) / 2)
    for y in (-BL.OVERRIDER_Y, BL.OVERRIDER_Y, -470.0, 470.0):
        x = bar_face_x(y, False)
        b = b - xcyl(4.4, x + 6.0, x + 60.0, y, zc)
    return _l(b, spec)


def _overrider(x_face, y, h0, h1, front):
    """Overrider (Fig 12.1 items 11, 26, 27; Oliver's photo 10): a tall chrome bullet standing proud of the blade,
    rounded at the top, narrowing toward the bottom, with a groove down its face for the rubber strip."""
    sgn = 1.0 if front else -1.0
    wires = []
    n = 11
    for k in range(n):
        t = k / (n - 1)
        h = h0 + (h1 - h0) * t
        bulge = 62.0 * (0.55 + 0.45 * math.sin(math.pi * min(t * 1.25, 1.0) * 0.9 + 0.2)) * (1.0 if t < 0.82 else max(0.3, 1 - (t - 0.82) / 0.18 * 0.7))
        hw = 30.0 * (0.72 + 0.28 * math.sin(math.pi * t)) * (1.0 if t < 0.85 else max(0.35, 1 - (t - 0.85) / 0.15 * 0.65))
        pts = []
        for j in range(20):
            a = 2 * math.pi * j / 20
            u = bulge * max(math.cos(a), 0.0) ** 0.7 - 16.0 * max(-math.cos(a), 0.0)
            v = hw * math.sin(a)
            pts.append(Vector(x_face - sgn * 62.0 + sgn * u, y + v, H(h)))
        wires.append(Wire.make_polygon(pts, close=True))
    o = Solid.make_loft(wires, ruled=False)
    if not o.is_valid:
        o = o.fix()
    hm = (h0 + h1) / 2
    groove = box(x_face - 7.0, x_face + 7.0, y - 6.5, y + 6.5, H(h0 + 40.0), H(h1 - 35.0)) if front else \
        box(x_face - 7.0, x_face + 7.0, y - 6.5, y + 6.5, H(h0 + 40.0), H(h1 - 35.0))
    return o - groove


def _ovr_face(which, side):
    if which == "front":
        y = side * OVR_FRONT_Y
        return CL.FRONT_X - 2.0, y
    y = side * BL.OVERRIDER_Y
    return CL.REAR_X + 40.0, y


def front_overrider(side):
    def build(spec):
        x, y = _ovr_face("front", side)
        h0, h1 = OVR_H["front"]
        o = _overrider(x, y, h0, h1, True)
        o = o - xcyl(4.4, x - 90.0, x - 40.0, y, H(sum(FRONT_BAR_H) / 2))
        return _l(o, spec)
    return build


def rear_overrider(side):
    def build(spec):
        """Rear overrider with the number plate lamp's two screw holes in its inner face (P10 NUMBER_LAMP)."""
        x, y = _ovr_face("rear", side)
        h0, h1 = OVR_H["rear"]
        o = _overrider(x, y, h0, h1, False)
        nx, ny, nz = BL.NUMBER_LAMP
        for dx in (-14.0, 14.0):
            o = o - ycyl(1.8, min(side * (ny - 6.0), side * (ny + 30.0)), max(side * (ny - 6.0), side * (ny + 30.0)),
                         nx + dx, nz)
        return _l(o, spec)
    return build


def overrider_rubber(which):
    def build(spec):
        """Rubber face strip in the overrider's groove (Oliver's photo 10), drawn on the car's centre line at the
        overrider's face; the assembly places it on the left and right overriders."""
        h0, h1 = OVR_H[which]
        x = CL.FRONT_X - 2.0 if which == "front" else CL.REAR_X + 40.0
        r = box(x - 6.0, x + 3.0, -5.5, 5.5, H(h0 + 44.0), H(h1 - 39.0)) if which == "front" else \
            box(x - 3.0, x + 6.0, -5.5, 5.5, H(h0 + 44.0), H(h1 - 39.0))
        from mgb.elec_shapes import tryfillet
        r = tryfillet(r, r.edges(), 2.5)
        return _l(r, spec)
    return build


def front_spring_bar(side):
    def build(spec):
        """Front spring bar (Fig 12.1 items 2, 3): a flat spring steel blade from the bumper's back to the chassis
        leg's front end, two bolts at the leg (St.front_leg) and one at the bar."""
        y = side * St.LEG_STEP_Y
        x1 = bar_face_x(St.LEG_STEP_Y) - BAR_DEPTH * 0.5 - 2.0
        x0 = 655.0
        zc = H(sum(FRONT_BAR_H) / 2)
        blade = box(x0, x1 - 40.0, y - 3.0, y + 3.0, St.LEG_BOT + 2.0, St.LEG_TOP - 2.0)
        drop = rod((x1 - 46.0, y, (St.LEG_BOT + St.LEG_TOP) / 2), (x1 - 4.0, y, zc), 6.0)
        foot = box(x1 - 6.0, x1, y - 22.0, y + 22.0, zc - 22.0, zc + 22.0)
        p = G.fuse([blade, drop, foot])
        for zz in (St.LEG_BOT + 15.0, St.LEG_TOP - 12.0):
            p = p - ycyl(5.0, y - 5, y + 5, 660.0, zz)
        return _l(p, spec)
    return build


def rear_bracket(side):
    def build(spec):
        """Rear bumper mounting bracket (Fig 12.1 item 34) from the rear rail's end to the bar, bolts both ends."""
        y = side * 470.0
        x0 = bar_face_x(470.0, False) + BAR_DEPTH * 0.5 + 2.0
        x1 = -2880.0
        zc = H(sum(REAR_BAR_H) / 2)
        p = box(x0, x1, y - 3.0, y + 3.0, zc - 22.0, zc + 22.0)
        p = p + box(x1 - 40.0, x1, y - 3.0, y + 3.0, -215.0, zc + 22.0)
        return _l(p, spec)
    return build


# ---- grille -----------------------------------------------------------------------------------------------------------
GRILLE_FACE_X = S.MOUTH_BACK_X + 22.0         # front of the surround (Oliver's photos 05, 10: the surround stands at the nose)
SURROUND_W = 26.0                            # the surround's chrome frame


def _mouth_prism(grow, x0, x1):
    return xprism(S.mouth_outline(grow=grow), x0, x1)


def grille_surround(spec):
    """Grille surround (Sec 7; Oliver's photo 10): the chrome frame round the opening, its face rolled (a half-round
    lip on a flat), set into the nose; the three top steady brackets' tabs behind it."""
    xf = GRILLE_FACE_X
    outer = _mouth_prism(SURROUND_W - 13.0, xf - 30.0, xf - 6.0)
    lip = _mouth_prism(SURROUND_W - 15.0, xf - 6.0, xf)
    inner = _mouth_prism(-13.0, xf - 40.0, xf + 2.0)
    ring = (outer + lip) - inner
    tabs = [box(xf - 70.0, xf - 30.0, y - 10.0, y + 10.0, H(S.MOUTH_TOP_H) - 10.0, H(S.MOUTH_TOP_H) - 7.0)
            for y in (-250.0, 0.0, 250.0)]
    return _c([ring] + tabs, spec)


def grille_slats(spec):
    """The early grille's fine vertical slats (Sec 7; Oliver's photos 10, 15), set back in the surround on a top and
    a bottom rail."""
    xf = GRILLE_FACE_X - 22.0
    clip = _mouth_prism(-12.0, xf - 14.0, xf + 2.0)
    slats = []
    y = -S.MOUTH_Y + 8.0
    while y <= S.MOUTH_Y - 8.0:
        if abs(y) > 16.0:
            slats.append(box(xf - 12.0, xf, y - 1.1, y + 1.1, H(S.MOUTH_BOT_H), H(S.MOUTH_TOP_H + 20.0)))
        y += 14.5
    rails = [box(xf - 14.0, xf - 9.0, -S.MOUTH_Y, S.MOUTH_Y, h - 3.0, h + 3.0)
             for h in (H(S.MOUTH_BOT_H) + 14.0, H(S.MOUTH_TOP_H) - 10.0)]
    g = G.fuse(slats + rails) & clip
    return _l(g, spec)


def grille_rail(spec):
    """The grille's lower chrome rail across the opening just above the bumper (Oliver's photo 10)."""
    xf = GRILLE_FACE_X - 8.0
    h = S.MOUTH_BOT_H + 18.0
    pts = [(-S.MOUTH_Y + 30.0, H(h - 9.0)), (S.MOUTH_Y - 30.0, H(h - 9.0)), (S.MOUTH_Y - 30.0, H(h + 9.0)),
           (-S.MOUTH_Y + 30.0, H(h + 9.0))]
    r = xprism(pts, xf - 18.0, xf)
    from mgb.elec_shapes import tryfillet
    r = tryfillet(r, r.edges().filter_by_position(__import__("build123d").Axis.X, xf - 1, xf + 1), 5.0)
    return _l(r & _mouth_prism(-5.0, xf - 30.0, xf + 2.0), spec)


def grille_bar(spec):
    """Centre bar of the grille under the badge."""
    xf = GRILLE_FACE_X - 4.0
    b = box(xf - 26.0, xf, -11.0, 11.0, H(S.MOUTH_BOT_H), H(S.MOUTH_TOP_H))
    from mgb.elec_shapes import tryfillet
    b = tryfillet(b, b.edges().filter_by_position(__import__("build123d").Axis.X, xf - 1, xf + 1), 4.0)
    return _l(b & _mouth_prism(-6.0, xf - 30.0, xf + 2.0), spec)


def _shield(w, h, n=10):
    """Shield outline in (y, z) about its top centre: flat top, straight sides, curving to a point below."""
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, -h * 0.45)]
    for k in range(1, n):
        t = k / n
        pts.append((w / 2 * (1 - t) ** 1.3, -h * 0.45 - h * 0.55 * math.sin(t * math.pi / 2)))
    pts.append((0.0, -h))
    for k in range(n - 1, 0, -1):
        t = k / n
        pts.append((-w / 2 * (1 - t) ** 1.3, -h * 0.45 - h * 0.55 * math.sin(t * math.pi / 2)))
    pts.append((-w / 2, -h * 0.45))
    return pts


def grille_badge(spec):
    """Shield badge at the top centre of the surround (Oliver's photo 10; a plain shield, no lettering): a chrome
    rim round a raised field."""
    xf = GRILLE_FACE_X + 2.0
    top = H(S.MOUTH_TOP_H + 40.0)
    out = [(y, top + z) for y, z in _shield(58.0, 76.0)]
    fld = [(y, top - 4.0 + z) for y, z in _shield(46.0, 64.0)]
    b = xprism(out, xf - 10.0, xf) + xprism(fld, xf, xf + 2.5)
    return _l(b, spec)


def scuttle_vent(spec):
    """Scuttle air intake (Oliver's photos 15, 27): a chrome slatted grille on the scuttle top at the windscreen
    base, ahead of the wiper spindles, over the heater intake."""
    xb, hb = S.screen_base(0.0)
    x0, x1 = xb + 40.0, xb + 95.0
    parts = []
    for k in range(-6, 7):
        y = k * 22.0
        parts.append(box(x0, x1, y - 2.0, y + 2.0, H(S.top_h(x0, y)) - 2.0, H(S.top_h(x0, y)) + 3.0))
    frame = box(x0 - 4.0, x1 + 4.0, -150.0, 150.0, H(S.top_h(x0, 0.0)) - 2.0, H(S.top_h(x0, 0.0)) + 1.5) - \
        box(x0, x1, -142.0, 142.0, H(S.top_h(x0, 0.0)) - 5.0, H(S.top_h(x0, 0.0)) + 5.0)
    return _c(parts + [frame], spec)


def boot_badge(spec):
    """Badge on the boot lid above the handle (Oliver's photos 06, 24: a plain octagon, no lettering)."""
    h = S.BOOT_REAR_H + 115.0
    x = S.tail_x(0.0, h)
    pts = [(0.0 + 26.0 * math.cos(math.pi / 8 + k * math.pi / 4), H(h) + 26.0 * math.sin(math.pi / 8 + k * math.pi / 4))
           for k in range(8)]
    b = xprism(pts, x - 6.0, x + 3.0)
    return _l(b, spec)


# ---- side strips ------------------------------------------------------------------------------------------------------
# Strip line (profile photo 29): 690 above the road behind the headlamp, rising to 712 at the rear lamp plinth.
STRIP_RISE = [(560.0, 0.0), (-700.0, 4.0), (-1600.0, 10.0), (-2300.0, 17.0), (-2780.0, 22.0)]


def strip_h(x):
    return S.H_M + S._interp(STRIP_RISE, x)


def _strip(x0, x1, side):
    n = max(3, int(abs(x1 - x0) / 120.0))
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    pts = [(x, side * (S.side_y(x, strip_h(x)) - 0.6), H(strip_h(x))) for x in xs]
    return swept_rod(pts, 3.4)


STRIP_SPANS = {"front": (555.0, S.DOOR_FRONT_X + 3.0), "door": (S.DOOR_FRONT_X - 4.0, S.DOOR_REAR_X + 4.0),
               "rear": (S.DOOR_REAR_X - 4.0, -2790.0)}


def strip(which, side):
    def build(spec):
        """Chrome side strip on the wing or door along the strip line, clipped on studs; continuous from behind the
        headlamp to the rear lamp plinth (profile photo 29; Oliver's photos 09, 23)."""
        x0, x1 = STRIP_SPANS[which]
        return _l(_strip(x0, x1, side), spec)
    return build


# ---- number plates ------------------------------------------------------------------------------------------------
PLATE_W, PLATE_H = 520.0, 111.0
FRONT_PLATE_H0 = FRONT_BAR_H[0] - PLATE_H + 4.0      # just under the blade (Oliver's photos 10, 15)
REAR_PLATE_H0 = REAR_BAR_H[1] + 12.0                 # on the rear panel above the blade (photos 18, 24)


def _front_plate_x():
    return bar_face_x(0.0) - 26.0                    # plate face just behind the blade's face (Oliver's photo 10)


def front_plinth(spec):
    """Front number plate plinth: a pressed bracket on the valance under the bumper's centre carrying the plate."""
    x = _front_plate_x()
    p = box(x - 3.0, x, -PLATE_W / 2 - 6.0, PLATE_W / 2 + 6.0, H(FRONT_PLATE_H0) - 6.0, H(FRONT_PLATE_H0 + PLATE_H) + 6.0)
    xv = S.nose_x(0.0, FRONT_PLATE_H0 + 50.0)
    legs = [box(xv - 6.0, x - 3.0, y - 12.0, y + 12.0, H(FRONT_PLATE_H0 + 40.0), H(FRONT_PLATE_H0 + 64.0)) for y in (-150.0, 150.0)]
    return _c([p] + legs, spec)


def front_plate(spec):
    x = _front_plate_x()
    plate = box(x, x + 2.0, -PLATE_W / 2, PLATE_W / 2, H(FRONT_PLATE_H0), H(FRONT_PLATE_H0 + PLATE_H))
    rim = box(x + 2.0, x + 3.0, -PLATE_W / 2, PLATE_W / 2, H(FRONT_PLATE_H0), H(FRONT_PLATE_H0 + PLATE_H)) - \
        box(x + 1.0, x + 4.0, -PLATE_W / 2 + 6.0, PLATE_W / 2 - 6.0, H(FRONT_PLATE_H0) + 6.0, H(FRONT_PLATE_H0 + PLATE_H) - 6.0)
    return _c([plate, rim], spec)


def _rear_plate_x():
    return S.tail_x(0.0, REAR_PLATE_H0 + PLATE_H / 2) - 6.0


def rear_plinth(spec):
    """Rear number plate plinth on the rear panel between the overriders, under the plate lamps."""
    x = _rear_plate_x()
    p = box(x, x + 3.0, -PLATE_W / 2 - 10.0, PLATE_W / 2 + 10.0, H(REAR_PLATE_H0) - 8.0, H(REAR_PLATE_H0 + PLATE_H) + 8.0)
    return _l(p, spec)


def rear_plate(spec):
    x = _rear_plate_x()
    plate = box(x - 2.0, x, -PLATE_W / 2, PLATE_W / 2, H(REAR_PLATE_H0), H(REAR_PLATE_H0 + PLATE_H))
    rim = box(x - 3.0, x - 2.0, -PLATE_W / 2, PLATE_W / 2, H(REAR_PLATE_H0), H(REAR_PLATE_H0 + PLATE_H)) - \
        box(x - 4.0, x - 1.0, -PLATE_W / 2 + 6.0, PLATE_W / 2 - 6.0, H(REAR_PLATE_H0) + 6.0, H(REAR_PLATE_H0 + PLATE_H) - 6.0)
    return _c([plate, rim], spec)


PARTS = {
    "body.brightwork.front-bar": {"build": front_bar},
    "body.brightwork.rear-bar": {"build": rear_bar},
    "body.brightwork.overrider-rubber-front": {"build": overrider_rubber("front")},
    "body.brightwork.overrider-rubber-rear": {"build": overrider_rubber("rear")},
    "body.brightwork.grille-surround": {"build": grille_surround},
    "body.brightwork.grille-slats": {"build": grille_slats},
    "body.brightwork.grille-rail": {"build": grille_rail},
    "body.brightwork.grille-bar": {"build": grille_bar},
    "body.brightwork.grille-badge": {"build": grille_badge},
    "body.brightwork.scuttle-vent": {"build": scuttle_vent},
    "body.brightwork.boot-badge": {"build": boot_badge},
    "body.brightwork.front-plinth": {"build": front_plinth},
    "body.brightwork.front-plate": {"build": front_plate},
    "body.brightwork.rear-plinth": {"build": rear_plinth},
    "body.brightwork.rear-plate": {"build": rear_plate},
}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.brightwork.front-overrider-{n}"] = {"build": front_overrider(s_)}
    PARTS[f"body.brightwork.rear-overrider-{n}"] = {"build": rear_overrider(s_)}
    PARTS[f"body.brightwork.front-spring-bar-{n}"] = {"build": front_spring_bar(s_)}
    PARTS[f"body.brightwork.rear-bracket-{n}"] = {"build": rear_bracket(s_)}
    for w in ("front", "door", "rear"):
        PARTS[f"body.brightwork.strip-{w}-{n}"] = {"build": strip(w, s_)}
