"""Bright work and fittings (Haynes Ch 12 Sec 7, 10, 14; Fig 12.1, printed p218): the early chrome bumpers with their
overriders (rubber-faced), spring bars and rear mounting brackets; the early grille: a chrome surround (a wide,
shallow rounded rectangle whose top follows the bonnet's front edge) filled with fine vertical slats, the lower rail,
the centre bar under a plain shield badge (no lettering); the scuttle's slatted air intake; the wing and door chrome
strips; the number plates (blank: the characters are Oliver's call, PLAN) on the front plinth and straight on the rear
panel; the boot lid's chrome MG octagon (raised letters on a red field) and M-G-B letter badge; the hood pegs on the rear
deck and the tonneau studs on the rear wing tops (QA fix round 1, rear fittings: mgb.rear_fittings_layout).

Forms and positions from Oliver's photos 05, 10, 15, 18, 20, 24, 27 and the profile photo 29 (scaled on the
wheelbase); sizes derived (D). The bumpers follow the body's plan outline at their height (mgb.body_shell_layout),
standing a set gap off it, so they wrap round the corners to the wheel arches as on the car.
Drawn in place in the car frame.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Compound, Location, Plane, Rot, Solid, Vector, Wire

from mgb import body_geom as G, body_layout as BL, body_shell_layout as S, car_layout as CL, grille_layout as GL
from mgb import rear_fittings_layout as RF
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, ycyl, zcyl, zprism, zrev
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
FRONT_BAR_H = (352.0, 406.0)                 # QA fix round 1: the face 54 tall, the sloping top face rising to 415
REAR_BAR_H = (438.0, 503.0)                  # Oliver's photos 14, 18, 25 (QA, scaled on the plate: 416-481 above his road)
# + 22 mm: his car sits about 22 mm lower at the back than the model's standard ride height, so on the body the rear
# fittings stand 22 mm higher (Oliver's scan, registered on the body: blade 446-493, overrider tops 605-609, plate 531-642)
BAR_DEPTH = 44.0
FRONT_GAP, REAR_GAP = 54.0, 34.0
# the blades bow out at the middle (Oliver's scan: front blade face 830-850 at the centre and 770-780 at |y| 500, rear
# -3025..-3031 at the centre and -2975..-2988 at |y| 500; the overriders at x 834-844 and -3042..-3048, the published
# overall length 153.2 in over them)
FRONT_BOW, REAR_BOW = 25.0, 36.0
FRONT_END_X, REAR_END_X = 528.0, CL.bx(-2785.0)   # rear ends: Oliver's scan (right-hand end about x -2785; QA fix round 1)
OVR_FRONT_Y = 345.0                          # front overriders (QA fix round 1: scan +/-350, kf029 within 10 of 330)
OVR_FRONT_H = (336.0, 536.0)                 # front overrider bottom and top (QA fix round 1: scan front elevation 336-522;
#                                              kf213, kf220 against the slats put the top about 15 mm higher)
FRONT_BAR_BOLT = (500.0, 384.0)              # |y|, h of the domed bolt heads near the blade's corners (kf212, kf222, kf224)
OVR_H = {"front": (292.0, 519.0), "rear": (417.0, 600.0)}   # tops: photos 15 and 14, 18 (QA)


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
        g = gap(pts[k][1]) if callable(gap) else gap
        out.append((pts[k][0] + nx * g, pts[k][1] + ny * g))
    return out


def _bar_path(front):
    h = sum(FRONT_BAR_H if front else REAR_BAR_H) / 2
    base, bow = (FRONT_GAP, FRONT_BOW) if front else (REAR_GAP, REAR_BOW)
    pts = _plan_outline(h, front, lambda y: base + bow * max(0.0, 1.0 - (y / 620.0) ** 2))
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


def _front_bar_section(h0, h1):
    """Front blade section (QA fix round 1; Oliver's keyframes kf210, kf212, kf218, kf219): a tall, nearly flat face
    with a slight forward bulge and rolled top and bottom edges, then a wide top face sloping back 35 mm and rising a
    little, its edge turned down behind; the flange returns inside."""
    hm, hh = (h0 + h1) / 2, (h1 - h0) / 2
    pts = [(16.0, h0 + 6.0), (8.0, h0 - 1.5), (3.0, h0 - 0.5), (0.8, h0 + 2.0)]
    for k in range(9):                                   # the face, bulging 2.5 mm at its middle
        hf = h0 + 5.0 + (h1 - h0 - 10.0) * k / 8
        sgm = (hf - hm) / hh
        pts.append((-2.5 * (1 - sgm * sgm), hf))
    pts += [(0.8, h1 - 2.0), (3.0, h1 + 1.5), (7.0, h1 + 4.0), (38.0, h1 + 16.0), (40.5, h1 + 14.0), (39.5, h1 + 9.0),
            (14.0, h1 - 6.0), (14.0, h0 + 12.0)]
    return pts


def _bar(front):
    hs = FRONT_BAR_H if front else REAR_BAR_H
    sec = _front_bar_section(*hs) if front else _bar_section(*hs)
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
    for side in (1, -1):                                 # the corner bolts' holes, square to the face
        p, n = _bar_face_frame(side * FRONT_BAR_BOLT[0])
        b = b - (Location(Plane(origin=(p[0], p[1], H(FRONT_BAR_BOLT[1])), z_dir=(n[0], n[1], 0.0))) * zcyl(4.2, -20.0, 5.0))
    return _l(b, spec)


def _bar_face_frame(y):
    """(point on the front blade's face path nearest y, outward unit normal in plan)."""
    path = _bar_path(True)
    k = min(range(len(path)), key=lambda i: abs(path[i][1] - y))
    a, c = path[max(k - 1, 0)], path[min(k + 1, len(path) - 1)]
    tx, ty = c[0] - a[0], c[1] - a[1]
    L = math.hypot(tx, ty)
    n = (ty / L, -tx / L)
    if n[0] < 0:
        n = (-n[0], -n[1])
    return path[k], n


def front_bar_bolt(spec, side=1):
    """Domed bolt head on the front blade's face near each corner (QA fix round 1, Oliver's keyframes kf212, kf222,
    kf224): a chrome dome head, square to the face, its shank through the blade to the bracket behind."""
    p, n = _bar_face_frame(side * FRONT_BAR_BOLT[0])
    d = spec.nom("head_diameter")
    head = zrev([(0.0, -1.0), (d / 2, -1.0), (d / 2, 0.5), (d / 2 - 1.5, 2.6), (d / 4, 4.2), (0.0, 4.6)]) + zcyl(3.9, -24.0, -1.0)
    loc = Location(Plane(origin=(p[0], p[1], H(FRONT_BAR_BOLT[1])), z_dir=(n[0], n[1], 0.0)))
    return _l(loc * head, spec)


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
    o = _rake(o, x_face, h0, front)
    groove = box(x_face - 7.0, x_face + 7.0, y - 6.5, y + 6.5, H(h0 + 40.0), H(h1 - 35.0)) if front else \
        box(x_face - 7.0, x_face + 7.0, y - 6.5, y + 6.5, H(h0 + 40.0), H(h1 - 35.0))
    return o - _rake(groove, x_face, h0, front)


OVR_RAKE = 8.0                                # deg: the overriders lean in at the top (Oliver's photos 05, 09, 10, 23)


def _rake(p, x_face, h0, front):
    a = -OVR_RAKE if front else OVR_RAKE
    return Location((x_face, 0.0, H(h0))) * Rot(0, a, 0) * Location((-x_face, 0.0, -H(h0))) * p


def _ovr_face(which, side):
    if which == "front":
        y = side * OVR_FRONT_Y
        return CL.FRONT_X + 20.0, y         # the raked top at FRONT_X + 6 (Oliver's scan 834-844)
    y = side * BL.OVERRIDER_Y
    return CL.REAR_X + 4.0, y               # the raked top at REAR_X + 18 (Oliver's scan -3042..-3048)


# front overrider profile (QA fix round 1; Oliver's keyframes kf213, kf214, kf220, kf028 and the scan's front elevation):
# plain chrome, no rubber - a tall bullet standing on the blade: a full rounded foot below the blade, swelling widest
# about the blade's top, then narrowing up to a round top 2-2.5 blade heights above the blade, the top drawn back
# toward the blade. (t up the overrider, half-width, front ahead of the blade's face, back behind it)
OVR_FRONT_PROFILE = [(0.0, 6.0, 6.0, -4.0), (0.04, 20.0, 18.0, -10.0), (0.1, 29.0, 30.0, -16.0), (0.2, 34.0, 38.0, -20.0),
                     (0.3, 35.5, 42.0, -22.0), (0.42, 35.0, 43.0, -22.0), (0.55, 32.0, 41.0, -22.0), (0.68, 28.0, 36.0, -20.0),
                     (0.8, 23.0, 29.0, -17.0), (0.9, 17.0, 21.0, -12.0), (0.96, 11.0, 13.0, -7.0), (1.0, 3.0, 4.0, -2.0)]


def _front_overrider(y):
    x0 = bar_face_x(y)
    h0, h1 = OVR_FRONT_H
    wires = []
    for t, hw, fwd, back in OVR_FRONT_PROFILE:
        h = h0 + (h1 - h0) * t
        pts = []
        for j in range(40):
            a = 2 * math.pi * j / 40
            c, sn = math.cos(a), math.sin(a)
            u = (fwd if c > 0 else -back) * (abs(c) ** 0.85) * (1 if c > 0 else -1)
            pts.append(Vector(x0 + u, y + hw * (abs(sn) ** 0.9) * (1 if sn >= 0 else -1), H(h)))
        wires.append(Wire.make_polygon(pts, close=True))
    o = Solid.make_loft(wires, ruled=False)
    if not o.is_valid:
        o = o.fix()
    return o


def front_overrider(side):
    def build(spec):
        """Front overrider (Fig 12.1 item 11; QA fix round 1): plain chrome, bulbous, on its stud through the blade."""
        y = side * OVR_FRONT_Y
        o = _front_overrider(y)
        x = bar_face_x(y)
        o = o - xcyl(4.4, x - 30.0, x - 12.0, y, H(sum(FRONT_BAR_H) / 2))
        return _l(o, spec)
    return build


# Rear overrider (QA fix round 1; Oliver's photo 25 telephoto scaled on the plate, keyframes kf165, kf168, kf171, kf173,
# kf176 and his scan): plain chrome, no rubber face. In elevation narrow at the rounded top (about 40 mm) swelling to a
# bulbous foot (88 mm) below the blade; in side view the rear face stands nearly upright (the bulb at REAR_X + 4, the top
# at REAR_X + 18 in the scan) and the top runs forward to the rear panel as a deep narrow hood that carries the plate lamp.
# Tables against t, 0 at the foot (OVR_H rear h0) to 1 at the top: half-width, rear face and front face (x - REAR_X).
R_OVR_HW = [(0.0, 16.0), (0.04, 31.0), (0.11, 40.5), (0.20, 41.0), (0.29, 39.5), (0.42, 35.0), (0.55, 29.5),
            (0.68, 24.5), (0.82, 20.0), (0.92, 15.5), (0.97, 11.0), (1.0, 5.0)]   # photo 25 zoomed (2.9 px/mm)
R_OVR_REAR = [(0.0, 34.0), (0.05, 15.0), (0.15, 6.0), (0.30, 4.0), (0.50, 7.0), (0.70, 11.0), (0.85, 15.0), (0.93, 21.0),
              (0.98, 38.0), (1.0, 56.0)]
R_OVR_FRONT = [(0.0, 44.0), (0.10, 70.0), (0.30, 86.0), (0.50, 95.0), (0.70, 101.0), (0.90, 102.0), (0.97, 98.0), (1.0, 90.0)]


def _rear_overrider(y, h0, h1):
    tt = np.concatenate([[0.004, 0.015, 0.035, 0.065], np.linspace(0.10, 0.90, 13), [0.935, 0.965, 0.985, 0.996]])
    wires = []
    for t in tt:
        hw = float(np.interp(t, *zip(*R_OVR_HW)))
        xr = CL.REAR_X + float(np.interp(t, *zip(*R_OVR_REAR)))
        xf = CL.REAR_X + float(np.interp(t, *zip(*R_OVR_FRONT)))
        xm, L = (xr + xf) / 2, (xf - xr) / 2
        # round the foot and the top over in side view as well as in elevation (photo 25, kf168: no flat ends)
        cap = 1.0
        if t > 0.86:
            cap = math.sqrt(max(0.0, 1.0 - ((t - 0.86) / 0.14) ** 2))
        elif t < 0.12:
            cap = math.sqrt(max(0.0, 1.0 - ((0.12 - t) / 0.12) ** 2))
        cap = max(cap, 0.14)
        L = L * cap
        xm = xr + L if t < 0.5 else xm                     # the foot keeps its rear face, the top its centre
        hw = hw * (cap ** 0.35 if t < 0.12 else 1.0)
        z = H(h0 + (h1 - h0) * t)
        pts = []
        for j in range(24):
            a = 2 * math.pi * j / 24
            c, sn = math.cos(a), math.sin(a)
            fx = math.copysign(abs(c) ** (0.8 if c > 0 else 0.4), c)       # c > 0: the rounded rear; c < 0: the squarer front
            fy = math.copysign(abs(sn) ** (0.85 if c > 0 else 0.6), sn)
            pts.append(Vector(xm - L * fx, y + hw * fy, z))
        wires.append(Wire.make_polygon(pts, close=True))
    o = Solid.make_loft(wires, ruled=False)
    if not o.is_valid:
        o = o.fix()
    return o


def rear_overrider(side):
    def build(spec):
        """Rear overrider (Fig 12.1 items 26, 27): plain chrome, narrow rounded top, bulbous foot, the top running
        forward to the rear panel; the stud hole for the bar and the number plate lamp's two screw holes in its inner
        face (Haynes Ch 10 Sec 37 para 1: two screws to nuts and distance pieces inside the overrider)."""
        y = side * BL.OVERRIDER_Y
        h0, h1 = OVR_H["rear"]
        o = _rear_overrider(y, h0, h1)
        x = bar_face_x(BL.OVERRIDER_Y, False)
        o = o - xcyl(4.4, x + 6.0, x + 60.0, y, H(sum(REAR_BAR_H) / 2))
        nx, ny, nz = BL.NUMBER_LAMP
        for dx in (-10.0, 10.0):
            o = o - ycyl(1.8, min(side * (ny - 4.0), side * (ny + 30.0)), max(side * (ny - 4.0), side * (ny + 30.0)),
                         nx + dx, nz + 10.0)
        return _l(o, spec)
    return build


def overrider_rubber(which):
    def build(spec):
        """Rubber face strip in the overrider's groove (Oliver's photo 10), drawn on the car's centre line at the
        overrider's face; the assembly places it on the left and right overriders."""
        h0, h1 = OVR_H[which]
        x = CL.FRONT_X + 20.0 if which == "front" else CL.REAR_X + 4.0
        r = box(x - 6.0, x + 3.0, -5.5, 5.5, H(h0 + 44.0), H(h1 - 39.0)) if which == "front" else \
            box(x - 3.0, x + 6.0, -5.5, 5.5, H(h0 + 44.0), H(h1 - 39.0))
        from mgb.elec_shapes import tryfillet
        r = tryfillet(r, r.edges(), 2.5)
        return _l(_rake(r, x, h0, which == "front"), spec)
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


# ---- grille (QA fix round 1: mgb.grille_layout) ------------------------------------------------------------------------
# Oliver's car (scan front elevation, keyframes kf216, kf218-220): a heavy rolled chrome surround with an arched top
# and big corner radii (no flanges at the top corners), the slats on a 22 mm pitch with rounded fronts and tops standing
# on its bottom bar (no separate lower rail: what looks like one is the grille reflected in the bumper's top face), the
# centre bar carrying the MG badge proud of the bonnet's lip, and the two club badges on brackets from the bottom bar.
GRILLE_FACE_X = S.MOUTH_BACK_X + 22.0         # the nose skin's x round the opening at the centre (kept for the plinth)


def _nose(y, h):
    """x of the nose skin at (|y|, h) within the grille's span (the implicit outer surface, opening ignored)."""
    return S.nose_x(min(abs(y), GL.SURR_HW - 6.0), h)


def _surround_path():
    """3D centre line of the rolled bar: the outline inset by its radius, following the nose in plan."""
    pts = GL.resample(GL.surround_outline(-GL.SURR_BAR_R), 18.0)
    xs = np.array([_nose(y, h) for y, h in pts])
    for _ in range(6):                                   # the bar is smoother than the implicit nose's small ripples
        xs = (np.roll(xs, 1) + 2 * xs + np.roll(xs, -1)) / 4
    return [(float(x) + GL.SURR_PROUD - GL.SURR_BAR_R, y, H(h)) for x, (y, h) in zip(xs, pts)]


def grille_surround(spec):
    """Grille surround (Sec 7; QA fix round 1, mgb.grille_layout): the rolled chrome bar swept round the opening along
    the nose's curve in plan, its arched top under the bonnet's lip, with the three top steady brackets' tabs."""
    from build123d import Edge
    pts = _surround_path()
    n = len(pts)
    loop = Edge.make_spline([Vector(*p) for p in pts], periodic=True)
    lo = min(range(n), key=lambda k: abs(pts[k][1]) + (0.0 if pts[k][2] < H(500.0) else 1e6))   # mid bottom
    hi = min(range(n), key=lambda k: abs(pts[k][1]) + (0.0 if pts[k][2] > H(500.0) else 1e6))   # mid top
    ring = []
    for a, b in ((lo, hi), (hi, lo)):                    # two halves lofted through round sections square to the loop
        wires = []                                       # (OCC's pipe sweep fails on this path)
        for k in range(a, b + 1 if b > a else b + n + 1):
            p = Vector(*pts[k % n])
            t = loop.tangent_at(loop.param_at_point(p))
            xd = (Vector(1, 0, 0) - t * t.X).normalized()
            wires.append(Wire.make_circle(GL.SURR_BAR_R, Plane(origin=p, x_dir=xd, z_dir=t)))
        half = Solid.make_loft(wires, ruled=False)
        ring.append(half if half.is_valid else half.fix())
    tabs = [box(_nose(y, 560.0) - 50.0, _nose(y, 560.0) - 12.0, y - 10.0, y + 10.0, H(GL.top_h(y, -GL.SURR_BAR_R)) - 2.0,
                H(GL.top_h(y, -GL.SURR_BAR_R)) + 1.0) for y in (-250.0, 0.0, 250.0)]
    return _c(ring + tabs, spec)


def grille_surround_flange(spec):
    """Grille surround mounting panel (QA fix round 1): a body-coloured ring set back behind the bar, out to the body's
    grille opening (mouth_outline), which is still larger than the car's surround at the top corners and the bottom;
    it stands in for the nose panel round the surround until the body opening follows grille_layout.surround_outline."""
    outer = xprism(S.mouth_outline(grow=10.0), GRILLE_FACE_X - 40.0, GRILLE_FACE_X - 26.0)
    inner = xprism([(y, H(h)) for y, h in GL.surround_outline(-GL.SURR_BAR_R)], GRILLE_FACE_X - 45.0, GRILLE_FACE_X - 21.0)
    return _l(outer - inner, spec)


def _slat(y, h0, h1, w, depth, set_back):
    """One slat: a strip with a half-round front, its top end rounded, standing at y."""
    xf = _nose(y, 510.0) - set_back
    r = w / 2
    sec = [(xf - depth, y - r), (xf - r, y - r)] + \
        [(xf - r + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 9)[1:-1]] + \
        [(xf - r, y + r), (xf - depth, y + r)]
    s = zprism(sec, H(h0), H(h1) - r)
    from build123d import Sphere
    s = s + xcyl(r, xf - depth, xf - r, y, H(h1) - r) + Sphere(r).moved(Location((xf - r, y, H(h1) - r)))
    return s


def grille_slats(spec):
    """The early grille's vertical slats (Sec 7; QA fix round 1): 36 chrome strips on a 22 mm pitch either side of
    the centre bar, 6 mm across with half-round fronts and rounded tops, 18 mm deep (from an angle they close up as on
    the car), standing on the surround's bottom bar and running up behind its top."""
    inner = GL.surround_outline(-2 * GL.SURR_BAR_R + 3.0)
    slats = []
    for k in range(1, 40):
        for sgn in (1, -1):
            y = sgn * k * GL.SLAT_PITCH
            if abs(y) > GL.SURR_HW - 2 * GL.SURR_BAR_R - 6.0:
                continue
            h0 = GL.SURR_BOT_H + GL.SURR_BAR_R - 4.0
            h1 = GL.top_h(y, -GL.SURR_BAR_R) + 2.0
            # inside the rounded corners the slat stops at the inner edge of the bar
            ins = _inner_span(inner, y)
            if ins is None:
                continue
            h0, h1 = max(h0, ins[0] - 6.0), min(h1, ins[1] + 8.0)
            if h1 - h0 < 20.0:
                continue
            slats.append(_slat(y, h0, h1, GL.SLAT_W, GL.SLAT_DEPTH, GL.SLAT_SET_BACK))
    return _c(slats, spec)


def _inner_span(outline, y):
    """(lowest, highest) h of a closed outline at y, or None."""
    hs = []
    m = len(outline)
    for i in range(m):
        (y0, h0), (y1, h1) = outline[i], outline[(i + 1) % m]
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            hs.append(h0 + (h1 - h0) * (y - y0) / (y1 - y0))
    return (min(hs), max(hs)) if len(hs) >= 2 else None


def grille_bar(spec):
    """Centre bar of the grille (kf216, kf218): a wider chrome bar with a rounded front from the bottom bar up under the
    badge, standing a little ahead of the slats."""
    h0 = GL.SURR_BOT_H + GL.SURR_BAR_R - 4.0
    h1 = GL.BADGE_H[0] + 30.0
    return _l(_slat(0.0, h0, h1, 12.0, 16.0, GL.SLAT_SET_BACK - 5.0), spec)


def _badge_outline(inset=0.0):
    """MG grille badge outline (y, h) (kf216, kf218: a shield with a flat top, clipped top corners, near-vertical sides
    and a pointed foot), inset by inset."""
    w, (hb, ht) = GL.BADGE_W / 2 - inset, (GL.BADGE_H[0] + inset * 1.6, GL.BADGE_H[1] - inset)
    c = 6.0
    side = ht - (ht - hb) * 0.42
    pts = [(-w + c, ht), (w - c, ht), (w, ht - c), (w - 3.0, side)]
    for k in range(1, 8):
        t = k / 8
        pts.append(((w - 3.0) * (1 - t) ** 1.25, side - (side - hb) * math.sin(t * math.pi / 2)))
    pts.append((0.0, hb))
    for k in range(7, 0, -1):
        t = k / 8
        pts.append((-(w - 3.0) * (1 - t) ** 1.25, side - (side - hb) * math.sin(t * math.pi / 2)))
    pts += [(-w + 3.0, side), (-w, ht - c)]
    return pts


def _badge_face_x():
    return _nose(0.0, 610.0) + GL.BADGE_PROUD - 12.0


def _oct_yz(cy, ch, r, rot=22.5):
    return [(cy + r * math.cos(math.radians(rot + 45 * k)), ch + r * math.sin(math.radians(rot + 45 * k))) for k in range(8)]


BADGE_OCT = (GL.BADGE_H[1] - 31.0, 22.0)        # octagon centre h and radius (kf216: it fills the badge's upper part)


def _stroke(a, b, w):
    """A letter stroke (y, h) from a to b, w wide, as a quad."""
    dy, dh = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dy, dh)
    ny, nh = -dh / L * w / 2, dy / L * w / 2
    return [(a[0] + ny, a[1] + nh), (b[0] + ny, b[1] + nh), (b[0] - ny, b[1] - nh), (a[0] - ny, a[1] - nh)]


def _mg_letters(cy, ch, s, x0, x1):
    """Raised chrome M and G of the octagon badge, scaled by s (letter height 2 s), centred at (cy, ch)."""
    w = 0.32 * s
    my = cy - 0.55 * s
    M = [((my - 0.42 * s, ch - s), (my - 0.42 * s, ch + s)), ((my - 0.42 * s, ch + s), (my, ch - 0.15 * s)),
         ((my, ch - 0.15 * s), (my + 0.42 * s, ch + s)), ((my + 0.42 * s, ch + s), (my + 0.42 * s, ch - s))]
    gy = cy + 0.55 * s
    arc = []
    for k in range(10):
        a = math.radians(40 + 280 * k / 9)
        arc.append((gy + 0.48 * s * math.cos(a), ch + s * math.sin(a)))
    G_ = [(arc[i], arc[i + 1]) for i in range(len(arc) - 1)] + [((gy + 0.48 * s * math.cos(math.radians(320)), ch - 0.7 * s),
                                                                (gy + 0.48 * s * math.cos(math.radians(320)), ch)),
                                                               ((gy + 0.05 * s, ch), (gy + 0.5 * s, ch))]
    out = []
    for a, b in M + G_:
        out.append(xprism(_stroke(a, b, w), x0, x1))
    return out


def grille_badge(spec):
    """MG badge on the grille's centre bar (Sec 7; QA fix round 1, kf216, kf218, kf219): a chrome shield frame with
    clipped top corners standing proud of the bonnet's lip, the octagon's chrome border and the raised chrome MG,
    on a stem down to the centre bar. The enamel is in grille-badge-field (black) and grille-badge-octagon (red)."""
    xf = _badge_face_x()
    sh = [(y, H(h)) for y, h in _badge_outline()]
    body = xprism(sh, xf - 7.0, xf - 1.5) + (xprism(sh, xf - 1.5, xf) - xprism([(y, H(h)) for y, h in _badge_outline(3.0)],
                                                                               xf - 2.0, xf + 1.0))
    oh, orr = BADGE_OCT
    ring = xprism([(y, H(h)) for y, h in _oct_yz(0.0, oh, orr + 1.8)], xf - 2.0, xf - 0.2) - \
        xprism([(y, H(h)) for y, h in _oct_yz(0.0, oh, orr)], xf - 3.0, xf + 1.0)
    letters = _mg_letters(0.0, H(oh), 10.5, xf - 1.5, xf + 0.4)
    stem = box(_nose(0.0, 560.0) - 10.0, xf - 6.0, -6.0, 6.0, H(GL.BADGE_H[0] + 12.0), H(GL.BADGE_H[0] + 40.0))
    return _c([body, ring, stem] + letters, spec)


def grille_badge_field(spec):
    """The badge's black enamel field round the octagon."""
    xf = _badge_face_x()
    oh, orr = BADGE_OCT
    f = xprism([(y, H(h)) for y, h in _badge_outline(2.6)], xf - 2.2, xf - 1.2) - \
        xprism([(y, H(h)) for y, h in _oct_yz(0.0, oh, orr + 1.6)], xf - 3.0, xf)
    return _l(f, spec)


def grille_badge_octagon(spec):
    """The badge's red enamel octagon under the chrome MG."""
    xf = _badge_face_x()
    oh, orr = BADGE_OCT
    return _l(xprism([(y, H(h)) for y, h in _oct_yz(0.0, oh, orr + 0.2)], xf - 2.2, xf - 1.0), spec)


# ---- club badges on the grille (QA fix round 1) -------------------------------------------------------------------------
def _club_x(name):
    y, h, d = GL.CLUB_BADGES[name]
    return _nose(y, h) + 8.0


def _club_bracket(name):
    """Flat chrome strap from the badge's foot down to a clamp on the surround's bottom bar (kf216: two screws)."""
    y, h, d = GL.CLUB_BADGES[name]
    xf = _club_x(name)
    hb = GL.SURR_BOT_H + GL.SURR_BAR_R
    strap = box(xf - 6.0, xf - 3.0, y - 8.0, y + 8.0, H(hb - 4.0), H(h - d / 2 + 10.0))
    clamp = box(xf - 8.0, xf - 2.5, y - 13.0, y + 13.0, H(hb - 8.0), H(hb + 12.0))
    out = [strap, clamp]
    for dy in (-7.0, 7.0):
        out.append(xcyl(2.4, xf - 2.5, xf - 1.0, y + dy, H(hb + 4.0)))
    return out


def club_badge_hmc(spec):
    """Heritage Motor Centre Gaydon 1924-1999 club badge (off side; Oliver's keyframes kf216, kf218): a round badge in a
    chrome rim - the green enamel ring (lettered on the car), a bright inner ring round the yellow octagon with its red
    border and red M G - and the GAYDON tab below, on a chrome strap with a two-screw clamp on the bottom bar. Chrome
    here; the enamels are club-badge-hmc-ring (green), -centre (yellow) and -mg (red)."""
    y, h, d = GL.CLUB_BADGES["hmc"]
    xf = _club_x("hmc")
    rim = xcyl(d / 2, xf - 4.0, xf, y, H(h)) - xcyl(d / 2 - 2.5, xf - 4.5, xf + 1.0, y, H(h))
    back = xcyl(d / 2 - 0.5, xf - 5.5, xf - 4.0, y, H(h))
    inner = xcyl(20.5, xf - 4.0, xf - 0.6, y, H(h)) - xcyl(18.0, xf - 4.5, xf + 1.0, y, H(h))
    tab = box(xf - 4.0, xf - 1.2, y - 17.0, y + 17.0, H(h - d / 2 - 9.0), H(h - d / 2 + 4.0))
    return _c([rim, back, inner, tab] + _club_bracket("hmc"), spec)


def club_badge_hmc_ring(spec):
    """The HMC badge's green enamel ring (its lettering is not modelled)."""
    y, h, d = GL.CLUB_BADGES["hmc"]
    xf = _club_x("hmc")
    return _l(xcyl(d / 2 - 2.0, xf - 4.0, xf - 1.3, y, H(h)) - xcyl(20.0, xf - 5.0, xf, y, H(h)), spec)


def club_badge_hmc_centre(spec):
    """The HMC badge's yellow enamel octagon behind the red MG."""
    y, h, d = GL.CLUB_BADGES["hmc"]
    xf = _club_x("hmc")
    return _l(xprism([(yy, H(hh)) for yy, hh in _oct_yz(y, h, 15.5)], xf - 4.0, xf - 1.6) +
              xcyl(18.2, xf - 4.0, xf - 2.6, y, H(h)), spec)


def club_badge_hmc_mg(spec):
    """The HMC badge's red enamel: the octagon's border and the M G on the yellow (kf218)."""
    y, h, d = GL.CLUB_BADGES["hmc"]
    xf = _club_x("hmc")
    border = xprism([(yy, H(hh)) for yy, hh in _oct_yz(y, h, 17.0)], xf - 2.0, xf - 1.0) - \
        xprism([(yy, H(hh)) for yy, hh in _oct_yz(y, h, 15.0)], xf - 3.0, xf)
    return _c([border] + _mg_letters(y, H(h), 7.5, xf - 1.8, xf - 0.9), spec)


def aa_badge(spec):
    """AA badge (near side; kf218-220): the winged chrome badge - wings across the top, a round body with the two
    open chrome A's over yellow enamel, the maker's tab below - on its strap and clamp from the bottom bar."""
    y, h, d = GL.CLUB_BADGES["aa"]
    xf = _club_x("aa")
    r = d / 2 - 6.0
    body = xcyl(r + 3.0, xf - 4.0, xf - 0.5, y, H(h)) - xcyl(r, xf - 4.5, xf + 1.0, y, H(h))
    back = xcyl(r + 2.5, xf - 5.5, xf - 4.0, y, H(h))
    out = [body, back]
    for s_ in (-1.0, 1.0):                                   # the two A's, side by side, sharing a foot
        ay = y + s_ * 0.36 * r
        top, foot = (ay, h + 0.78 * r), h - 0.82 * r
        out.append(xprism([(yy, H(hh)) for yy, hh in _stroke(top, (ay - 0.42 * r, foot), 6.5)], xf - 2.0, xf + 0.6))
        out.append(xprism([(yy, H(hh)) for yy, hh in _stroke(top, (ay + 0.42 * r, foot), 6.5)], xf - 2.0, xf + 0.6))
        out.append(xprism([(yy, H(hh)) for yy, hh in _stroke((ay - 0.24 * r, h - 0.2 * r), (ay + 0.24 * r, h - 0.2 * r), 4.0)],
                          xf - 2.0, xf + 0.6))
    wing = []
    for k in range(9):                                       # wings spreading from a central boss over the body
        t = k / 8
        wing.append((y - d / 2 + 4.0 + (d - 8.0) * t, h + r + 6.0 + 7.0 * math.sin(math.pi * t) ** 0.6))
    wing += [(y + d / 2 - 10.0, h + r - 1.0), (y - d / 2 + 10.0, h + r - 1.0)]
    out.append(xprism([(yy, H(hh)) for yy, hh in wing], xf - 4.0, xf - 1.0))
    out.append(xcyl(5.0, xf - 4.0, xf + 0.5, y, H(h + r + 9.0)))
    out.append(box(xf - 4.0, xf - 1.0, y - 9.0, y + 9.0, H(h - r - 14.0), H(h - r + 1.0)))          # maker's tab
    return _c(out + _club_bracket("aa"), spec)


def aa_badge_enamel(spec):
    """The AA badge's yellow enamel behind the letters."""
    y, h, d = GL.CLUB_BADGES["aa"]
    xf = _club_x("aa")
    return _l(xcyl(d / 2 - 5.5, xf - 4.0, xf - 1.6, y, H(h)), spec)


# ---- scuttle vent (QA fix round 1) --------------------------------------------------------------------------------
# Oliver's keyframes kf195-202 (close-ups) and the kf076+kf088+kf092 triangulation (BL.SCUTTLE_VENT_*): a chrome
# frame on the scuttle top 20-30 mm behind the bonnet's rear edge, its outline a long trapezoid with rounded ends (the
# front edge longer, the ends leaning inboard toward the screen: tight corners at the front, wide sweeps at the back),
# eight openings between seven bars that fan with the ends (the outer ones leaning most), a pressed perforated mesh in
# each cell. Built in the skin's tangent frame at the vent centre (u forward, v = car y, w along the skin normal); the
# top is bent about a long axis to follow the scuttle's crown, so the frame stands the same height along its length.
VENT_HALF = (BL.SCUTTLE_VENT_LEN / 2 + 4.0, BL.SCUTTLE_VENT_LEN / 2 - 14.5)   # front, rear corner half-lengths (the ends
#                                                lean ~17 deg; the rounding takes 4 off the tips)
VENT_RIM = 9.0                                   # chrome rim width front and back (kf198, kf199: about a quarter of a cell)
VENT_BARS, VENT_BAR_W = 7, 6.5
VENT_TOP = 6.0                                   # frame top above the skin (kf199, kf202: a low bezel)


def _vent_frame():
    """(Location of the vent's tangent frame, crown radius of the skin across it)."""
    x = BL.SCUTTLE_VENT_X
    z0, n = BL.skin_point(x, 0.0)
    zt, _ = BL.skin_point(x, VENT_HALF[0])
    sag = max((z0 - zt) * n[2], 0.3)
    R = VENT_HALF[0] ** 2 / (2.0 * sag)
    t = (n[2], 0.0, -n[0])
    return Location(Plane(origin=(x, 0.0, z0), x_dir=t, z_dir=(n[0], 0.0, n[2]))), R


def _vent_outline(grow=0.0):
    """Plan outline (u, v) of the vent's frame, grown by grow (negative: the inner edge of the rim)."""
    d = BL.SCUTTLE_VENT_DEPTH / 2 + grow
    af, ar = VENT_HALF[0] + grow * 1.05, VENT_HALF[1] + grow * 0.95
    lean = (VENT_HALF[0] - VENT_HALF[1]) / BL.SCUTTLE_VENT_DEPTH
    af, ar = af - (BL.SCUTTLE_VENT_DEPTH / 2 - d) * lean, ar + (BL.SCUTTLE_VENT_DEPTH / 2 - d) * lean
    from mgb.body_shell import fillet_poly
    rf, rr = max(12.0 + grow * 0.6, 3.0), max(30.0 + grow * 0.6, 6.0)
    pts = [(d, -af), (d, af), (-d, ar), (-d, -ar)]
    return fillet_poly(pts, [rf, rf, rr, rr], 8)


def _vent_bar(k, w0, w1):
    """Bar k (0..VENT_BARS-1) as a prism: centre line v = vk + u * s, leaning with the ends in proportion to vk."""
    half_in = (VENT_HALF[0] + VENT_HALF[1]) / 2 - VENT_RIM - 5.0
    pitch = 2 * half_in / (VENT_BARS + 1)
    vk = (k - (VENT_BARS - 1) / 2) * pitch
    s = (VENT_HALF[0] - VENT_HALF[1]) / BL.SCUTTLE_VENT_DEPTH * vk / half_in
    d = BL.SCUTTLE_VENT_DEPTH / 2 + 2.0
    hw = VENT_BAR_W / 2
    pts = [(d, vk + d * s - hw), (d, vk + d * s + hw), (-d, vk - d * s + hw), (-d, vk - d * s - hw)]
    return zprism(pts, w0, w1)


def _crown(R, w_top, u0=-60.0, u1=60.0):
    """Solid under a long cylinder about the u axis whose top is w_top on the centre line (follows the crown)."""
    return xcyl(R, u0, u1, 0.0, w_top - R)


def _openings(w0, w1):
    out = zprism(_vent_outline(-VENT_RIM), w0, w1)
    for k in range(VENT_BARS):
        out = out - _vent_bar(k, w0 - 1.0, w1 + 1.0)
    return out


def scuttle_vent(spec):
    """Scuttle air intake grille (QA fix round 1, Oliver's keyframes kf195-202 and the triangulated position): the
    chrome frame with its rim and seven fanned bars round eight cells, standing 6 mm proud of the scuttle."""
    loc, R = _vent_frame()
    frame = zprism(_vent_outline(), -8.0, VENT_TOP + 2.0) & _crown(R, VENT_TOP)
    frame = frame - _openings(-9.0, VENT_TOP + 3.0)
    from mgb.elec_shapes import tryfillet
    top = [e for e in frame.edges() if e.center().Z > VENT_TOP - 1.2]
    frame = tryfillet(frame, top, 1.6)
    return _l(loc * frame, spec)


def scuttle_vent_mesh(spec):
    """The perforated mesh in the vent's cells (kf198, kf201: round holes on a close hexagonal pitch, dark grey), 5 mm
    under the frame's top; the scuttle skin is not cut (body shell), so the cells are shallow."""
    loc, R = _vent_frame()
    plate = _openings(-9.0, 3.0) & _crown(R, 1.4) - _crown(R, 0.9)
    holes = []
    pitch, r = 5.2, 1.5
    for i in range(-40, 41):
        for j in range(-8, 9):
            v = i * pitch + (pitch / 2 if j % 2 else 0.0)
            u = j * pitch * 0.866
            if abs(u) < BL.SCUTTLE_VENT_DEPTH / 2 - VENT_RIM - 2.0 and abs(v) < VENT_HALF[0] - VENT_RIM - 4.0:
                holes.append(zcyl(r, -3.0, 4.0, u, v))
    plate = plate - Compound(holes)
    return _l(loc * plate, spec)


def scuttle_vent_intake(spec):
    """The dark heater air intake seen through the mesh (drawn as a thin black backing in the cells)."""
    loc, R = _vent_frame()
    return _l(loc * (_openings(-9.0, 3.0) & _crown(R, 0.8) - _crown(R, 0.3)), spec)


# ---- boot lid badges (QA fix round 1) ------------------------------------------------------------------------------
# Drawn in the badge's own frame (u to the right seen from behind, v forward up the lid, w out of the skin) and bent to
# the lid's fall: each element is its outline extruded along w, cut to a slab between two cylinders about an axis
# along u at the lid's radius of curvature (mgb.rear_fittings_layout), so the badge sits down on the curved lid.
def _seg(a, b, w):
    """Polygon of a straight stroke of width w from a to b (square ends)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(a[0] + nx, a[1] + ny), (a[0] - nx, a[1] - ny), (b[0] - nx, b[1] - ny), (b[0] + nx, b[1] + ny)]


def _rect(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def _ell(cu, cv, ru, rv, a0=0.0, a1=360.0, n=24):
    return [(cu + ru * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cv + rv * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + (0 if a1 - a0 >= 360.0 else 1))]


def _octagon(across):
    r = across / 2 / math.cos(math.pi / 8)
    return [(r * math.cos(math.pi / 8 + k * math.pi / 4), r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]


def _uvw(polys, w0, w1, cut=()):
    """Union of the outlines extruded from w0 to w1, less the `cut` outlines (badge frame, mm)."""
    from mgb.elec_shapes import poly_xy
    from mgb.poly2d import ccw
    out = None
    for p in polys:
        e = poly_xy(ccw(p), w0, w1)
        out = e if out is None else out + e
    for p in cut:
        out = out - poly_xy(ccw(p), w0 - 1.0, w1 + 1.0)
    return out


def _on_lid(x, solid_uvw, w_lo, w_hi):
    """Bend a badge element drawn flat (w from w_lo to w_hi above the skin) onto the lid at station x, centre line."""
    from build123d import Cylinder, Plane
    org, xd, yd, zd = RF.skin_frame(x, 0.0)
    R = RF.lid_curvature_r(x)
    slab = Location((0.0, 0.0, -R)) * Rot(0, 90, 0) * Cylinder(R + w_hi, 300.0)
    slab = slab - Location((0.0, 0.0, -R)) * Rot(0, 90, 0) * Cylinder(R + w_lo, 302.0)
    tall = solid_uvw & slab
    return Location(Plane(origin=org, x_dir=xd, z_dir=zd)) * tall


# MG octagon (Oliver's photo 06 square on, 10 px/mm on the 100 mm octagon, its height foreshortened to 92 %: the frame
# 4.5 mm wide; the M's left stem short, its right stem and the G's stem the full inner height; strokes 5.5 mm).
MG_M = [_rect(-36.5, -31.0, -19.6, 19.6), _seg((-33.8, 19.0), (-21.5, -5.5), 5.6), _seg((-21.5, -5.5), (-8.5, 22.0), 5.6),
        _rect(-10.5, -5.0, -36.4, 36.0)]
MG_G = [_rect(5.5, 10.8, -36.4, 36.0), _rect(5.5, 19.5, 30.6, 36.0), _seg((17.6, 33.4), (33.4, 7.6), 5.6),
        _rect(20.0, 36.0, -3.8, 1.6), _rect(30.8, 36.0, -18.0, 1.6), _seg((33.4, -16.6), (23.8, -33.8), 5.6),
        _rect(5.5, 26.5, -36.4, -31.0)]
BADGE_FRAME_W = 4.5


def boot_badge(spec):
    """MG octagon badge on the boot lid (Oliver's photos 06, 25; kf062, kf104, kf105): a chrome octagon frame round a
    red enamel field with the raised chrome M and G, 100 mm across, on the lid's fall at x -2720 (the scan's top
    view), its two pins through the lid. The field is the separate boot-badge-field part (its own finish)."""
    a = RF.BADGE_ACROSS
    frame = _uvw([_octagon(a)], -4.0, 3.0, cut=[_octagon(a - 2 * BADGE_FRAME_W)])
    letters = _uvw(MG_M + MG_G, 0.0, 3.0)
    b = _on_lid(RF.BADGE_X, frame, -4.0, 3.0) + _on_lid(RF.BADGE_X, letters, 0.6, 2.8)
    return _l(b, spec)


def boot_badge_field(spec):
    """The MG badge's red enamel field inside the chrome octagon (Oliver's photo 06)."""
    a = RF.BADGE_ACROSS
    f = _uvw([_octagon(a - 2 * BADGE_FRAME_W + 0.4)], -4.0, 1.0)
    return _l(_on_lid(RF.BADGE_X, f, -4.0, 1.0), spec)


def _script_letters():
    """M-G-B letter badge outlines (photo 06: seriffed capitals 12 mm tall on a thin bar through their middles, 58 mm
    over all): M centred u -21, G at 0, B at +21."""
    m = [_rect(-28.6, -27.2, -6.0, 6.0), _seg((-27.9, 6.0), (-21.0, -6.0), 2.4), _seg((-21.0, -6.0), (-14.6, 6.0), 1.2),
         _rect(-15.2, -13.2, -6.0, 6.0), _rect(-30.0, -25.8, -6.0, -5.2), _rect(-16.8, -11.6, -6.0, -5.2),
         _rect(-30.0, -27.2, 5.2, 6.0), _rect(-15.2, -11.6, 5.2, 6.0)]
    b = [_rect(15.2, 17.2, -6.0, 6.0), _rect(13.8, 21.0, 5.0, 6.0), _rect(13.8, 21.5, -0.6, 0.6), _rect(13.8, 22.0, -6.0, -5.0)]
    return m, b


def _script_rings():
    """The G and the B's bowls: (outer, inner) outline pairs."""
    g = (_ell(0.0, 0.0, 6.0, 6.0, n=32), _ell(0.0, 0.0, 4.2, 4.6, n=32))
    b1 = (_ell(21.0, 2.9, 3.4, 3.1, -90.0, 90.0, 12) + [(17.0, 6.0), (17.0, -0.2)], _ell(21.0, 2.9, 1.8, 1.9, -90.0, 90.0, 12)
          + [(17.0, 4.8), (17.0, 1.0)])
    b2 = (_ell(21.6, -3.0, 3.9, 3.0, -90.0, 90.0, 12) + [(17.0, 0.0), (17.0, -6.0)], _ell(21.6, -3.0, 2.2, 1.9, -90.0, 90.0, 12)
          + [(17.0, -1.1), (17.0, -4.9)])
    return [g, b1, b2]


def boot_script(spec):
    """Chrome M-G-B letter badge on the lid ahead of the octagon (Oliver's photo 06; centred x -2655, the scan's top
    view): seriffed capitals on a thin bar, pinned through the lid."""
    m, bstem = _script_letters()
    el = _uvw(m + bstem, 0.0, 2.2)
    for outer, inner in _script_rings():
        el = el + _uvw([outer], 0.0, 2.2, cut=[inner])
    el = el - _uvw([_ell(3.6, 3.6, 4.2, 3.4, n=16)], -1.0, 3.0)                     # the G's mouth, upper right
    el = el + _uvw([_rect(1.4, 5.8, -1.4, -0.2), _rect(4.6, 5.9, -5.0, -0.2)], 0.0, 2.2)    # the G's bar and spur
    bar = _uvw([_rect(-13.5, 15.5, -0.7, 0.7)], 0.0, 1.4)                            # the bar through the middles
    return _l(_on_lid(RF.SCRIPT_X, el + bar, -2.0, 2.2), spec)


# ---- hood pegs and tonneau studs (QA fix round 1) ----------------------------------------------------------------------
def _placed(x, y, solid):
    from build123d import Plane
    org, xd, yd, zd = RF.skin_frame(x, y)
    return Location(Plane(origin=org, x_dir=xd, z_dir=zd)) * solid


def hood_peg(side):
    def build(spec):
        """Hood peg on the rear deck (kf071, kf105; the scan's top view): a chrome shell-shaped dome, 34 x 22 mm and
        12 high, its open lip facing forward for the hood frame's rear rail to hook under; two screws into the deck."""
        from build123d import Solid as So, scale
        from mgb.chassis_geom import box as bx_
        d = scale(So.make_sphere(1.0), by=(11.0, 17.0, 12.0))           # frame: u across, v forward, w out
        d = d & bx_(-20, 20, -20, 20, -3.0, 20)
        d = d - (Location((0.0, 9.0, 0.0)) * scale(So.make_sphere(1.0), by=(7.5, 11.0, 6.5)))    # the hook's mouth
        x, y = RF.hood_peg_points()[0 if side > 0 else 1]
        return _l(_placed(x, y, d), spec)
    return build


def tonneau_studs(side):
    def build(spec):
        """Three tonneau studs on the rear wing top round the cockpit's rear corner (kf071, kf105): a flanged collar,
        a waisted neck and a domed head, chrome."""
        from mgb.chassis_geom import zcyl as zc_
        from build123d import Solid as So
        head = (Location((0, 0, 8.6)) * So.make_sphere(4.0)) & zc_(4.5, 8.6, 13.0)
        stud = zc_(5.0, -2.0, 1.2) + zc_(3.6, 1.2, 4.5) + zc_(2.2, 4.5, 8.8) + head
        return _c([_placed(x, y, stud) for x, y in RF.tonneau_stud_points(side)], spec)
    return build


# ---- side strips ------------------------------------------------------------------------------------------------------
# Strip line: mgb.body_layout SIDE_STRIP_H (QA fix 1: 679 above the road at x 400, 711 at -600, 713-718 on the doors,
# 718-724 on the rear wings; Oliver's keyframes and scan). The strip is a flat-faced chrome moulding about 14 mm tall
# (kf048, kf016: not a round rod), its face a little crowned, its top and bottom edges rolled.
STRIP_SEC = [(0.0, -7.0), (2.2, -7.0), (3.8, -6.1), (4.6, -4.4), (4.9, -2.0), (5.0, 0.0), (4.9, 2.0), (4.6, 4.4),
             (3.8, 6.1), (2.2, 7.0), (0.0, 7.0)]          # (out from the skin, up) mm
STRIP_SEAT = 0.6                                          # the back sits this far into the skin


def strip_h(x):
    return S._interp(BL.SIDE_STRIP_H, x)


def _strip(x0, x1, side, taper=(False, False)):
    """The strip from x0 to x1 along the strip line on one side: the section lofted along the skin, its ends square
    (door strips: square-cut caps) or tapered over the last 30 mm (the front end behind the headlamp, the rear end at
    the lamp's rim)."""
    n = max(4, int(abs(x1 - x0) / 60.0))
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    L = abs(x1 - x0)
    for e, x in ((0, x0), (1, x1)):
        if taper[e]:
            d = 1.0 if x1 < x0 else -1.0
            xs += [x + (d if e else -d) * t for t in (6.0, 14.0, 22.0)]
    xs = sorted(set(round(v, 3) for v in xs), reverse=x1 < x0)
    wires = []
    for x in xs:
        h = strip_h(x)
        y = S.side_y(x, h)
        dy = (S.side_y(x - 2.0, h) - S.side_y(x + 2.0, h)) / 4.0          # dy/dx along the car (toward the rear)
        nx, ny = dy, 1.0
        k = math.hypot(nx, ny)
        nx, ny = nx / k, ny / k
        f = 1.0
        for e, xe in ((0, x0), (1, x1)):
            if taper[e]:
                f = min(f, 0.35 + 0.65 * min(abs(x - xe) / 30.0, 1.0))
        pts = []
        for o, u in STRIP_SEC:
            oo = (o * f) - STRIP_SEAT
            pts.append(Vector(x + nx * oo, side * (y + ny * oo), H(h) + u * (0.55 + 0.45 * f)))
        wires.append(Wire.make_polygon(pts, close=True))
    return Solid.make_loft(wires, ruled=False)


STRIP_CAP = 21.0                              # the rear strip's tapered end runs on to the lamp's chrome rim (QA fix
                                              # round 1: kf176, kf178, photo 25; the rim at x -2836..-2840 at the strip line)
STRIP_SPANS = {"front": (555.0, S.door_front_x(strip_h(-700.0)) + 3.0),
               "door": (S.door_front_x(strip_h(-700.0)) - 4.0, S.DOOR_REAR_X + 20.0),     # sides-glass 17: ends 20 short
               "rear": (S.DOOR_REAR_X - 4.0, CL.bx(-2820.0) - 0.6 * STRIP_CAP)}           # rear 12: to the lamp's rim
STRIP_TAPER = {"front": (True, False), "door": (False, False), "rear": (False, True)}


def strip(which, side):
    def build(spec):
        """Chrome side strip on the wing or door along the strip line, clipped on studs; continuous from behind the
        headlamp to the rear lamp's rim, where the rear strip ends in a tapered cap (profile photo 29; Oliver's photos
        09, 23, 25; kf176, kf178)."""
        x0, x1 = STRIP_SPANS[which]
        return _l(_strip(x0, x1, side, STRIP_TAPER[which]), spec)
    return build


# ---- number plates ------------------------------------------------------------------------------------------------
PLATE_W, PLATE_H = 520.0, 111.0
FRONT_PLATE_H0 = FRONT_BAR_H[0] - PLATE_H + 4.0      # just under the blade (Oliver's photos 10, 15)
REAR_PLATE_H0 = 529.0                                # on the rear panel above the blade (photos 14, 18, 24)


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


REAR_PLATE_SCREW_Y = 206.0                           # two screws through the plate into the panel, mid-height, 54 mm in from
                                                     # each end (kf165, kf168, kf171 scaled on the 111 mm plate)


def _rear_plate_x():
    """Back face of the rear plate: straight on the rear panel (no plinth: Oliver's photo 25, kf062, kf165-173), at the
    panel's most rearward point under it so the plate stands clear of the panel everywhere."""
    xs = [S.tail_x(y, h) for y in (0.0, PLATE_W / 2 - 10.0) for h in (REAR_PLATE_H0 + 8.0, REAR_PLATE_H0 + PLATE_H / 2,
                                                                       REAR_PLATE_H0 + PLATE_H - 8.0)]
    return min(xs) - 0.3


def rear_plate(spec):
    """Rear number plate (blank: the characters are Oliver's call, PLAN), black, 2 mm, straight on the rear panel."""
    x = _rear_plate_x()
    plate = box(x - 2.0, x, -PLATE_W / 2, PLATE_W / 2, H(REAR_PLATE_H0), H(REAR_PLATE_H0 + PLATE_H))
    for y in (-REAR_PLATE_SCREW_Y, REAR_PLATE_SCREW_Y):
        plate = plate - xcyl(2.2, x - 3.0, x + 1.0, y, H(REAR_PLATE_H0 + PLATE_H / 2))
    return _l(plate, spec)


def rear_plate_trim(spec):
    """The rear plate's thin silver border, 3.5 mm in from its edge, and its two silver dome-headed screws (Oliver's
    photo 25; kf062, kf165, kf168)."""
    x = _rear_plate_x() - 2.0
    z0, z1 = H(REAR_PLATE_H0), H(REAR_PLATE_H0 + PLATE_H)
    rim = box(x - 0.6, x + 0.2, -PLATE_W / 2 + 3.5, PLATE_W / 2 - 3.5, z0 + 3.5, z1 - 3.5) - \
        box(x - 1.0, x + 0.5, -PLATE_W / 2 + 6.0, PLATE_W / 2 - 6.0, z0 + 6.0, z1 - 6.0)
    from build123d import Solid as So
    heads = []
    for y in (-REAR_PLATE_SCREW_Y, REAR_PLATE_SCREW_Y):
        zc = H(REAR_PLATE_H0 + PLATE_H / 2)
        dome = So.make_sphere(4.8).moved(Location((x + 2.6, y, zc))) & box(x - 3.0, x + 0.2, y - 6, y + 6, zc - 6, zc + 6)
        heads.append(dome + xcyl(1.9, x, x + 12.0, y, zc))
    return _c([rim] + heads, spec)


PARTS = {
    "body.brightwork.front-bar": {"build": front_bar},
    "body.brightwork.front-bar-bolt": {"build": front_bar_bolt},
    "body.brightwork.rear-bar": {"build": rear_bar},
    "body.brightwork.grille-surround": {"build": grille_surround},
    "body.brightwork.grille-slats": {"build": grille_slats},
    "body.brightwork.grille-surround-flange": {"build": grille_surround_flange},
    "body.brightwork.grille-bar": {"build": grille_bar},
    "body.brightwork.grille-badge": {"build": grille_badge},
    "body.brightwork.grille-badge-field": {"build": grille_badge_field},
    "body.brightwork.grille-badge-octagon": {"build": grille_badge_octagon},
    "body.brightwork.club-badge-hmc": {"build": club_badge_hmc},
    "body.brightwork.club-badge-hmc-ring": {"build": club_badge_hmc_ring},
    "body.brightwork.club-badge-hmc-centre": {"build": club_badge_hmc_centre},
    "body.brightwork.club-badge-hmc-mg": {"build": club_badge_hmc_mg},
    "body.brightwork.aa-badge": {"build": aa_badge},
    "body.brightwork.aa-badge-enamel": {"build": aa_badge_enamel},
    "body.brightwork.scuttle-vent": {"build": scuttle_vent},
    "body.brightwork.scuttle-vent-mesh": {"build": scuttle_vent_mesh},
    "body.brightwork.scuttle-vent-intake": {"build": scuttle_vent_intake},
    "body.brightwork.boot-badge": {"build": boot_badge},
    "body.brightwork.boot-badge-field": {"build": boot_badge_field},
    "body.brightwork.boot-script": {"build": boot_script},
    "body.brightwork.front-plinth": {"build": front_plinth},
    "body.brightwork.front-plate": {"build": front_plate},
    "body.brightwork.rear-plate-trim": {"build": rear_plate_trim},
    "body.brightwork.rear-plate": {"build": rear_plate},
}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.brightwork.front-overrider-{n}"] = {"build": front_overrider(s_)}
    PARTS[f"body.brightwork.rear-overrider-{n}"] = {"build": rear_overrider(s_)}
    PARTS[f"body.brightwork.front-spring-bar-{n}"] = {"build": front_spring_bar(s_)}
    PARTS[f"body.brightwork.rear-bracket-{n}"] = {"build": rear_bracket(s_)}
    PARTS[f"body.brightwork.hood-peg-{n}"] = {"build": hood_peg(s_)}
    PARTS[f"body.brightwork.tonneau-studs-{n}"] = {"build": tonneau_studs(s_)}
    for w in ("front", "door", "rear"):
        PARTS[f"body.brightwork.strip-{w}-{n}"] = {"build": strip(w, s_)}
