"""Opening panels' frames and fittings (Haynes Ch 12): door frames (inner panel and shut faces), hinges, wind-up glass,
quarter-lights, locks, strikers and the early pull handles (Sec 21, 27, 32-39, Figs 12.13 and 12.15); the bonnet's
inner frame, hinges, stay, lock pin and safety catch (Sec 6); the boot lid's inner frame, hinges, lock and handle
(Sec 25-26, Fig 12.12).

Frames that follow the skins are the outer surface trimmed to a band inside the shut lines and moved inward
(mgb.body_shell skin_sdf shift); the rest is drawn in place in the car frame.
"""
from __future__ import annotations

import math

import numpy as np
from build123d import Compound, Face, Location, Rot, thicken

from mgb import body_geom as G, body_layout as BL, body_shell as B, body_shell_layout as S, side_glass_layout as SG
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, ycyl, yprism, zcyl, zprism
from parts.body import panels as Pn
from parts.body import structure as St

H = S.z_of
AND, OR = B.sd_and, B.sd_or
G2 = S.GAP / 2


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


def _cached(name, fn):
    return B.disk_cached(name, fn, extra_sources=("parts/body/closures.py", "parts/body/panels.py"))


def mirror(p, side):
    from build123d import Plane
    return p if side > 0 else p.mirror(Plane.XZ)


# =====================================================================================================================
# doors
# =====================================================================================================================
WAIST_H = SG.WAIST_H                         # door top inner edge (below the roll) where the glass slot is
DOOR_IN = 72.0                               # inner panel this far inboard of the skin
GLASS_TOP_H = SG.GLASS_TOP_H                 # the glass runs 8 mm up into the hood's edge (P11b QA); the quarter-light's top
QL_TOP_H = SG.QL_TOP_H                       # rail 16 mm lower, at 1144 (Oliver's scan: 1150)
QL_POST_X = SG.ql_post_x(QL_TOP_H)          # quarter-light's rear post (divider) centre line at the top; it leans back
                                             # 15 deg, its foot 70 mm further forward (mgb.side_glass_layout)
GLASS_T = 4.0


DOOR_APERTURES = [(-1010.0, -1260.0, 420.0, 700.0), (-1330.0, -1560.0, 380.0, 640.0)]   # (x0, x1, h0, h1)


def door_inner_sd(side):
    def f(X, Y, Z):
        holes = OR(*[B.sd_poly(X, Z, G.rounded_rect(x1, x0, H(h0), H(h1), 40.0)) for x0, x1, h0, h1 in DOOR_APERTURES])
        return AND(Pn.door_sd(X, Y, Z, side) + G2 + 10.0, Z - H(WAIST_H - 12.0), -holes)
    return f


def _door_x(h, rear):
    lean = S.DOOR_REAR_LEAN * (h - S.DOOR_BOTTOM_H) / (1100.0 - S.DOOR_BOTTOM_H)
    return (S.DOOR_REAR_X + G2 + 8.0 + lean) if rear else (S.door_front_x(h) - G2 - 8.0)   # front: the curved shut line


def door_frame(side):
    def build(spec):
        """Door frame: the inner panel parallel to the skin (72 mm inboard) with the two access apertures, the
        regulator's and remote control's holes (Fig 12.15 items 2, 4, 5), the front and rear shut faces and the bottom
        closing the box to the skin's turned edges, the waist reinforcement under the glass slot, the hinge tapping
        plates' bolt holes at the front and the lock's screw holes at the rear."""
        def make():
            inner = B.skin_sdf(door_inner_sd(side), 1.0, shift=(0.0, -side * DOOR_IN, 0.0))
            parts = list(inner.solids())
            hs = [S.DOOR_BOTTOM_H + 10.0 + k * (WAIST_H - 22.0 - S.DOOR_BOTTOM_H) / 10 for k in range(11)]
            for rear in (False, True):
                if rear:
                    pts = [(S.side_y(_door_x(h, rear), h) - 1.5 - DOOR_IN, H(h)) for h in hs]
                    pts += [(S.side_y(_door_x(h, rear), h) - 1.5, H(h)) for h in reversed(hs)]
                    x = _door_x(S.DOOR_BOTTOM_H, rear)
                    face = xprism(pts, x - 0.6, x + 0.6)
                else:                                   # follows the front shut line's curve (QA fix 1)
                    xh = lambda h: _door_x(h, False) + 0.6                                     # noqa: E731
                    face = St.shut_face(xh, lambda h: S.side_y(xh(h), h) - 1.5 - DOOR_IN,
                                        lambda h: S.side_y(xh(h), h) - 1.5, hs, 1.2)
                for hh in (St.HINGE_H if not rear else (St.STRIKER_H,)):
                    x = _door_x(hh, rear)
                    for dz in (-18.0, 0.0, 18.0):
                        face = face - xcyl(3.4, x - 5, x + 5, S.side_y(x, hh) - 30.0, H(hh) + dz)
                parts.append(face)
            xs = [_door_x(S.DOOR_BOTTOM_H, False) - k * (_door_x(S.DOOR_BOTTOM_H, False) - _door_x(S.DOOR_BOTTOM_H, True)) / 12
                  for k in range(13)]
            hb = S.DOOR_BOTTOM_H + 8.0
            bot = [(x, S.side_y(x, hb) - 1.5) for x in xs] + [(x, S.side_y(x, hb) - 1.5 - DOOR_IN) for x in reversed(xs)]
            parts.append(zprism(bot, H(hb) - 0.6, H(hb) + 0.6))
            wx0, wx1 = _door_x(WAIST_H, False), _door_x(WAIST_H, True)
            yw = S.side_y(-1200.0, WAIST_H - 30.0) - 1.5 - DOOR_IN
            parts.append(box(wx1, wx0, yw, yw + 1.2, H(WAIST_H - 60.0), H(WAIST_H - 14.0)))
            n_in = len(inner.solids())
            clip = yprism([(x, H(h)) for x, h in B.door_outline_xz(-(G2 + 5.0))], 0.0, 1000.0)   # round the lower corners
            parts = parts[:n_in] + [p & clip for p in parts[n_in:]]
            # the shut faces, bottom and waist piece are drawn on the left:
            if side < 0:                                # mirror them for the right door (QA fix 1: they were left)
                parts = parts[:n_in] + [St._side(p, side) for p in parts[n_in:]]
            return Compound(G.solids(parts))
        c = Compound(G.solids([_cached(f"door-frame-{side}", make)]))
        c.label = spec.id
        return c
    return build


def hinge(side, which):
    def build(spec):
        """Door hinge (Sec 32): a body leaf on the hinge pillar and a door leaf on the door's front shut face, three
        screws each, knuckled on a pin along the hinge line."""
        hh = St.HINGE_H[which]
        xp = S.door_front_x(hh) - G2
        y = side * (S.side_y(xp, hh) - 30.0)
        z = H(hh)
        body = box(xp - 3.0 - 30.0, xp - 3.0, y - 14.0, y + 14.0, z - 30.0, z + 30.0)
        leaf = box(xp - 3.0, xp + 30.0, y - side * 2.0 - 1.5, y - side * 2.0 + 1.5, z - 26.0, z + 26.0)
        knuckle = zcyl(7.0, z - 28.0, z + 28.0, xp - 1.0, y + side * 12.0)
        pin = zcyl(3.2, z - 32.0, z + 32.0, xp - 1.0, y + side * 12.0)
        p = G.fuse([body, leaf, knuckle]) - zcyl(3.4, z - 40, z + 40, xp - 1.0, y + side * 12.0)
        return _c([p, pin], spec)
    return build


GLASS_REAR_X = S.DOOR_REAR_X + 14.0            # the glass's rear edge at the waist, just inside the door's rear shut face
GLASS_REAR_RAKE = 36.0                          # the rear edge leans forward this much up to the top (Oliver's photos 08, 23)


def glass_outline():
    """Door glass in side view (x, height): front edge in the quarter-light's rear post channel, leaning back 15 deg
    with the post (Oliver's scan and kf048, kf015, kf016; Haynes Fig 12.15), the top along the hood's side edge, the
    rear edge at the door's rear shut line raked forward slightly and rounded into the top (Oliver's photos 08, 09, 23;
    the glass runs the whole length of the door); it runs down inside the door to the regulator channel."""
    xf = lambda h: SG.ql_post_x(h) - 4.0
    return [(xf(520.0), 520.0), (GLASS_REAR_X, 520.0), (GLASS_REAR_X, WAIST_H + 20.0),
            (GLASS_REAR_X + GLASS_REAR_RAKE, GLASS_TOP_H - 14.0), (xf(GLASS_TOP_H), GLASS_TOP_H)]


GLASS_RADII = [0, 0, 0, 75.0, 6.0]


def glass_top_h(x):
    """Height of the door glass's top (and raked rear) edge at x, from the rounded outline: the hood's side edge
    follows it."""
    pts = B.fillet_poly(glass_outline(), GLASS_RADII)
    xr = GLASS_REAR_X
    xtop = SG.ql_post_x(GLASS_TOP_H) - 10.0      # the top front corner
    x = min(max(x, xr), xtop)
    best = None
    for (x0, h0), (x1, h1) in zip(pts, pts[1:] + pts[:1]):       # upper envelope of the outline at x
        if min(x0, x1) - 1e-6 <= x <= max(x0, x1) + 1e-6:
            h = h0 if abs(x1 - x0) < 1e-9 else h0 + (h1 - h0) * (x - x0) / (x1 - x0)
            best = h if best is None else max(best, h)
    return best


def _glass_y(h):
    """Glass plane |y| at height h: in the door's slot at the waist, leaning in with the tumblehome above it."""
    y0 = S.side_y(-1200.0, WAIST_H - 30.0) - 26.0
    return y0 - (h - WAIST_H) * math.tan(math.radians(7.0))


GLASS_BOW = 5.0                                 # the glass is curved in its height, bowed out this much between the
                                                # waist and the top (it is on the plane there)


def _glass_ys(h):
    """|y| of the curved glass's outer face line at height h."""
    t = (h - (WAIST_H + GLASS_TOP_H) / 2) / ((GLASS_TOP_H - WAIST_H) / 2)
    return _glass_y(h) + (GLASS_BOW * (1.0 - t * t) ** 2 if h > WAIST_H else 0.0)   # flat inside the door, the bow
    # starting tangent at the waist so the fitted face stays smooth (a kink there broke the thickening)


def door_glass(side):
    def build(spec):
        """Wind-up door glass (Fig 12.15 / 12.17 item 1): toughened sheet in the door's slot, raised; its lower
        channel for the regulator's arm studs (Sec 39) at the bottom edge."""
        pts = B.fillet_poly(glass_outline(), GLASS_RADII)
        g = None
        rows = []
        hs = [500.0 + (GLASS_TOP_H + 20.0 - 500.0) * k / 12 for k in range(13)]
        xa = SG.ql_post_x(500.0) + 6.0
        xs = [xa - k * (xa - GLASS_REAR_X + 10.0) / 12 for k in range(13)]
        for x in xs:
            rows.append([(x, side * _glass_ys(h), H(h)) for h in hs])
        f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        slab = thicken(f, GLASS_T)
        clip = side_prism_xz(pts, -2000.0, 2000.0)
        g = slab & clip
        yc = side * _glass_ys(540.0)
        chan = box(GLASS_REAR_X + 60.0, SG.ql_post_x(520.0) - 30.0, yc - 6.0, yc + 6.0, H(520.0) - 10.0, H(540.0))
        return _c([g, chan], spec)
    return build


def glass_channel(side):
    def build(spec):
        """Rear glass run channel inside the door (Fig 12.15): a felt-lined U channel the glass's rear edge runs in,
        from the regulator's reach up to the waist, screwed to the door's rear shut face."""
        x = GLASS_REAR_X
        parts = []
        for k in range(6):
            h0 = 540.0 + (WAIST_H - 20.0 - 540.0) * k / 6
            h1 = 540.0 + (WAIST_H - 20.0 - 540.0) * (k + 1) / 6
            yc = side * _glass_ys((h0 + h1) / 2)
            u = box(x - 6.0, x + 12.0, yc - 8.0, yc + 8.0, H(h0), H(h1) + 0.5) - \
                box(x - 7.0, x + 10.0, yc - 4.5, yc + 4.5, H(h0) - 1.0, H(h1) + 1.5)
            parts.append(u)
        return _c([G.fuse(parts)], spec)
    return build


def side_prism_xz(pts_ag, y0, y1):
    return yprism([(x, H(h)) for x, h in pts_ag], y0, y1)


QL_FRONT_Y = S.SCREEN_HALF_W + 13.0              # the frame's front edge closes on the screen pillar's rear (photos 09, 27)
QL_FRAME_INSET = (16.0, SG.QL_FRAME_W, 18.0, SG.QL_FRAME_W)   # outer frame band: bottom, rear post, top, front post
QL_SEAL_W = 2.5                                  # black rubber between the outer frame and the pivoting vent frame
#                                                  (QA fix 2: 5 -> 2.5 and glazing 3 -> 1.5, thin lines as on the car, kf048, kf044)
QL_VENT_W = 6.0                                  # the vent's slim chrome frame
QL_GLAZING_W = 1.5                               # its black glazing rubber showing round the glass
QL_VENT_R = 72.0                                 # the vent's big lower-front corner (kf048 full res, kf231, kf232: about R70)


def ql_outline():
    """Quarter-light's outer chrome frame in side view (x, height): bottom front, bottom rear, top rear, top front.
    The front edge stands behind the screen pillar's rear edge with the two rubber strips between, the rear post leans
    back 15 deg, the bottom rail sits on the door top's capping (mgb.side_glass_layout; Oliver's scan and kf048)."""
    hb, ht = SG.QL_BOTTOM_H, SG.QL_OUTER_TOP_H
    return [(SG.ql_front_x(hb), hb), (SG.ql_rear_x(hb), hb), (SG.ql_rear_x(ht), ht), (SG.ql_front_x(ht), ht)]


QL_FRONT_X = ql_outline()[0][0]


def _inset(pts, d):
    """Polygon (x, h) with edge i (pts[i] to pts[i+1]) moved inward by d[i] (a list, or one value for all)."""
    n = len(pts)
    d = d if isinstance(d, (list, tuple)) else [d] * n
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sg = 1.0 if area > 0 else -1.0
    lines = []
    for i in range(n):
        (x0, h0), (x1, h1) = pts[i], pts[(i + 1) % n]
        ln = math.hypot(x1 - x0, h1 - h0)
        ux, uh = (x1 - x0) / ln, (h1 - h0) / ln
        lines.append(((x0 - uh * sg * d[i], h0 + ux * sg * d[i]), (ux, uh)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        det = -u[0] * v[1] + u[1] * v[0]
        a = (-(q[0] - p[0]) * v[1] + (q[1] - p[1]) * v[0]) / det
        out.append((p[0] + a * u[0], p[1] + a * u[1]))
    return out


def ql_frame_inner():
    return _inset(ql_outline(), list(QL_FRAME_INSET))


def ql_vent_outline():
    return _inset(ql_frame_inner(), QL_SEAL_W)


def ql_vent_inner():
    return _inset(ql_vent_outline(), QL_VENT_W)


def ql_glass_outline():
    return _inset(ql_vent_inner(), QL_GLAZING_W)


R_OUT = [6.0, 6.0, 10.0, 6.0]                       # outer frame corners: bottom front, bottom rear, top rear, top front
R_FRAME_IN = [QL_VENT_R + QL_SEAL_W, 5.0, 5.0, 6.0]
R_VENT = [QL_VENT_R, 4.0, 4.0, 5.0]
R_VENT_IN = [QL_VENT_R - QL_VENT_W, 3.0, 3.0, 3.0]
R_GLASS = [QL_VENT_R - QL_VENT_W - QL_GLAZING_W, 2.0, 2.0, 2.0]


def _ql_s(x, h):
    """Fraction across the quarter-light at (x, h): 0 on the rear post's centre line, 1 on the front edge."""
    xp, xf = SG.ql_post_x(h), SG.ql_front_x(h)
    return (x - xp) / (xf - xp)


def ql_y(x, h, clamp=True):
    """|y| of the quarter-light's plane: on the door glass's line at the rear post, toed in at the front so its front
    edge closes on the windscreen pillar (Oliver's photos 09, 15, 27)."""
    s = _ql_s(x, h)
    if clamp:
        s = max(0.0, min(1.0, s))
    return _glass_ys(h) + (QL_FRONT_Y - _glass_ys(h)) * s


def _qp(x, h, side, dy=0.0):
    return (x, side * (ql_y(x, h) + dy), H(h))


def _ql_slab(side, dy0, dy1, s0=-0.12, s1=1.25):
    """A sheet following the quarter-light's plane, dy0..dy1 outboard of it, over the frame's whole area."""
    rows = []
    hs = [SG.QL_BOTTOM_H - 40.0 + (SG.QL_OUTER_TOP_H + 30.0 - SG.QL_BOTTOM_H + 40.0) * k / 8 for k in range(9)]
    for j in range(9):
        s = s0 + (s1 - s0) * j / 8
        row = []
        for h in hs:
            xp, xf = SG.ql_post_x(h), SG.ql_front_x(h)
            x = xp + s * (xf - xp)
            row.append((x, side * (ql_y(x, h, clamp=False) + dy0), H(h)))
        rows.append(row)
    f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
    return thicken(f, dy1 - dy0, normal_override=(0.0, side, 0.0))


def _band(side, outer, r_out, inner, r_in, dy0, dy1):
    """Flat band between two side-view outlines on the quarter-light's plane."""
    reg = side_prism_xz(B.fillet_poly(outer, r_out), -2000.0, 2000.0)
    if inner is not None:
        reg = reg - side_prism_xz(B.fillet_poly(inner, r_in), -2000.0, 2000.0)
    return _ql_slab(side, dy0, dy1) & reg


def _edge_x(poly, i, h):
    """x on edge i of a side-view polygon at height h."""
    (x0, h0), (x1, h1) = poly[i], poly[(i + 1) % len(poly)]
    return x0 + (x1 - x0) * (h - h0) / (h1 - h0)


def _ybox(side, x0, x1, y0, y1, z0, z1):
    ya, yb = side * y0, side * y1
    return box(min(x0, x1), max(x0, x1), min(ya, yb), max(ya, yb), z0, z1)


def quarter_light_frame(side):
    def build(spec):
        """Quarter-light outer frame (Sec 21; Fig 12.15 item 1 'ventilator securing nuts'): a flat chrome channel
        about 24 mm wide with rounded corners (kf048 full res, kf231, kf232), its front edge behind the screen pillar
        with the rubber strips between, the rear post leaning back 15 deg (Oliver's scan) and running on down into the
        door as the door glass's front channel to the securing nuts; the frame's opening has the vent's big rounded
        lower-front corner, filled with chrome below it. Toed in at the front to close on the pillar."""
        out, inn = ql_outline(), ql_frame_inner()
        main = _band(side, out, R_OUT, inn, R_FRAME_IN, -6.0, 5.0)
        face = _band(side, _inset(out, 1.6), [max(r - 1.6, 0.0) for r in R_OUT], _inset(inn, -1.6),
                     [r + 1.6 for r in R_FRAME_IN], 5.0, 6.6)              # the raised flat face, edges stepped back
        # the door glass's front edge runs in a slot along the rear post
        hs = [WAIST_H - 170.0, SG.QL_OUTER_TOP_H - 26.0]
        slot = side_prism_xz([(SG.ql_post_x(h) + d, h) for h, d in ((hs[0], -14.0), (hs[0], -2.5))] +
                             [(SG.ql_post_x(h) + d, h) for h, d in ((hs[1], -2.5), (hs[1], -14.0))], -2000.0, 2000.0)
        yg0, yg1 = _glass_ys(WAIST_H + 140.0) - 5.0, _glass_ys(WAIST_H + 140.0) + 5.0
        slot = slot & _ybox(side, -2000.0, 0.0, yg0 - 3.0, yg1 + 3.0, 0.0, H(2000.0))
        # the divider post's leg down inside the door: a channel on the post's lean to the securing bracket
        h0, h1 = WAIST_H - 160.0, SG.QL_BOTTOM_H + 3.0
        yl = _glass_ys(WAIST_H - 80.0)
        # its outer face kept 2 mm inside the door skin, which rolls in over the top (the leg passes the door top
        # through the glass slot)
        hs_ = [h0 + (h1 - h0) * k / 16 for k in range(17)]
        yo = [min(yl + 7.0, S.side_y(SG.ql_post_x(h), h) - 2.0) for h in hs_]
        keep = [(h, y) for h, y in zip(hs_, yo) if y > yl - 5.0]
        sec = [(yl - 7.0, H(keep[0][0]))] + [(y, H(h)) for h, y in keep] + [(yl - 7.0, H(keep[-1][0]))]
        if side < 0:
            sec = [(-y, z) for y, z in sec]
        leg = side_prism_xz([(SG.ql_post_x(h0) - 9.0, h0), (SG.ql_post_x(h0) + 9.0, h0), (SG.ql_post_x(h1) + 9.0, h1),
                             (SG.ql_post_x(h1) - 9.0, h1)], -2000.0, 2000.0) & xprism(sec, -2000.0, 0.0)
        bx = SG.ql_post_x(h0)
        bracket = _ybox(side, bx - 16.0, bx + 16.0, yl - 7.0, yl - 5.4, H(h0) - 18.0, H(h0) + 4.0)
        studs = [_ybox(side, bx + dx - 4.0, bx + dx + 4.0, yl - 13.0, yl - 5.4, H(h0) - 11.0, H(h0) - 3.0) for dx in (-9.0, 9.0)]
        # the front leg: a tongue down from the lower front corner to the ventilator's front securing nut
        xf0 = QL_FRONT_X - 30.0
        yf = ql_y(xf0, SG.QL_BOTTOM_H)
        tongue = _ybox(side, xf0 - 14.0, xf0 + 14.0, yf - 5.0, yf + 1.0, H(WAIST_H - 70.0), H(SG.QL_BOTTOM_H + 2.0))
        nut = _ybox(side, xf0 - 6.0, xf0 + 6.0, yf - 12.0, yf - 5.0, H(WAIST_H - 62.0), H(WAIST_H - 50.0))
        frame = G.fuse([main, face, leg]) - slot
        return _c([frame, bracket, tongue, nut] + studs, spec)
    return build


def _knurl_plate(side, xc, hb, w, ht, dy0, t):
    """Triangular pivot base plate, apex up, its face diamond-knurled (two sets of shallow crossing grooves)."""
    tri = [(xc - w / 2, hb), (xc + w / 2, hb), (xc + 6.0, hb + ht), (xc - 6.0, hb + ht)]
    y0 = ql_y(xc, hb + ht / 2) + dy0
    plate = side_prism_xz(B.fillet_poly(tri, [3.0, 3.0, 4.0, 4.0]), *sorted((side * y0, side * (y0 - t))))
    cuts = []
    for k in range(-5, 6):
        for sgn in (-1.0, 1.0):
            c = xc + k * 6.0
            g = [(c - 0.7 - sgn * 20.0, hb - 20.0), (c + 0.7 - sgn * 20.0, hb - 20.0), (c + 0.7 + sgn * 20.0, hb + 20.0),
                 (c - 0.7 + sgn * 20.0, hb + 20.0)]
            g = [(x, h) for x, h in g]
            cuts.append(side_prism_xz(g, *sorted((side * (y0 - t - 1.0), side * (y0 - t + 0.6)))))
    return plate - G.fuse(cuts)


def quarter_light_vent(side):
    def build(spec):
        """Quarter-light vent (Sec 21): the pivoting inner frame round the glass, a narrow chrome channel with the
        big rounded lower-front corner (about R70), on its pivots top and bottom; the chrome catch on its front post at
        mid-height (a lever with a round knob, locking onto a keeper on the outer frame); the diamond-knurled
        triangular pivot base plate on its bottom rail (Oliver's kf048 full res, kf231, kf232, kf186; Haynes Fig
        12.15)."""
        vent = _band(side, ql_vent_outline(), R_VENT, ql_vent_inner(), R_VENT_IN, -4.0, 3.5)
        vi = ql_vent_inner()
        # catch on the front post at mid-height, inboard
        hc = SG.QL_BOTTOM_H + 0.47 * (SG.QL_OUTER_TOP_H - SG.QL_BOTTOM_H)
        xc = _edge_x(ql_vent_outline(), 3, hc)
        yc = ql_y(xc, hc)
        keeper = _ybox(side, xc - 2.0, xc + 16.0, yc - 6.0, yc - 15.0, H(hc) - 13.0, H(hc) + 13.0)
        base = _ybox(side, xc - 22.0, xc + 1.0, yc - 4.0, yc - 9.0, H(hc) - 10.0, H(hc) + 10.0)
        lever = _ybox(side, xc - 52.0, xc - 4.0, yc - 15.0, yc - 18.0, H(hc) - 4.5, H(hc) + 4.5)
        pivot = ycyl(4.5, *sorted((side * (yc - 9.0), side * (yc - 19.0))), x=xc - 8.0, z=H(hc))
        knob = ycyl(6.0, *sorted((side * (yc - 18.0), side * (yc - 29.0))), x=xc - 48.0, z=H(hc))
        from mgb.elec_shapes import tryfillet
        from build123d import Axis
        knob = tryfillet(knob, knob.edges().filter_by_position(Axis.Y, *sorted((side * (yc - 29.5), side * (yc - 28.5)))), 4.0)
        # pivot base plate on the bottom rail and the pivot pins
        hb = vi[0][1]
        xb = SG.ql_post_x(hb) + 0.44 * (SG.ql_front_x(hb) - SG.ql_post_x(hb))
        plate = _knurl_plate(side, xb, hb - 3.0, 36.0, 15.0, -4.0, 2.4)
        ht = vi[2][1]
        xt = SG.ql_post_x(ht) + 0.44 * (SG.ql_front_x(ht) - SG.ql_post_x(ht))
        yb, yt = ql_y(xb, hb), ql_y(xt, ht)
        pins = [zcyl(3.5, H(SG.QL_BOTTOM_H + 2.0), H(hb + 4.0), xb, side * (yb - 6.5)),
                zcyl(3.0, H(ht - 4.0), H(SG.QL_OUTER_TOP_H - 4.0), xt, side * yt)]
        return _c([vent, keeper, base, lever, pivot, knob, plate] + pins, spec)
    return build


def quarter_light_glass(side):
    def build(spec):
        """Vent glass in the pivoting frame's glazing rubber, the big rounded lower-front corner."""
        return _l(_band(side, ql_glass_outline(), R_GLASS, None, None, -2.0, 2.0), spec)
    return build


def ql_seal(side):
    def build(spec):
        """Quarter-light rubbers (Oliver's kf048 full res, kf231, kf232): the black strip on the frame's front edge
        (the pillar's own seal, Fig 12.7 items 21-23, is body.glass.pillar-seal), the seal between the outer frame and
        the vent all round, and the vent's glazing rubber round the glass."""
        hb, ht = SG.QL_BOTTOM_H + 1.0, SG.QL_OUTER_TOP_H - 2.0
        parts = []
        for d0, d1 in ((1.0, 5.0),):                          # QA fix 2: 4 mm (was 9, a heavy black band; kf015, kf048)
            poly = [(SG.ql_front_x(hb) + d0, hb), (SG.ql_front_x(hb) + d1, hb), (SG.ql_front_x(ht) + d1, ht),
                    (SG.ql_front_x(ht) + d0, ht)]
            parts.append(_ql_slab(side, -7.0, 4.0) & side_prism_xz(B.fillet_poly(poly, [0.0, 0.0, 1.5, 1.5]), -2000.0, 2000.0))
        parts.append(_band(side, ql_frame_inner(), R_FRAME_IN, ql_vent_outline(), R_VENT, -5.0, 2.5))
        parts.append(_band(side, ql_vent_inner(), R_VENT_IN, ql_glass_outline(), R_GLASS, -3.0, 3.0))
        return _c(parts, spec)
    return build


MIRROR_H = S.DOOR_TOP_H + 90.0                  # clamp and head centre (kf015 ray-cast: head centre h about 950)
MIRROR_HEAD_X = -1065.0                         # head centre (kf015)


def _mirror_geo():
    side = -1
    h = MIRROR_H
    xp = SG.ql_post_x(h)
    yq = ql_y(xp, h)
    xh = MIRROR_HEAD_X
    yh = yq + 64.0
    return side, h, xp, yq, xh, yh


def door_mirror(spec):
    """Door mirror (Oliver's kf191-kf194, kf015, photos 08, 15, 23): a split clamp round the right-hand
    quarter-light's leaning rear post about 90 mm above the door top, its two screws on the outboard face, a short arm
    out to a ball joint and the rectangular chrome head with rounded corners and a domed back (the driver's side)."""
    side, h, xp, yq, xh, yh = _mirror_geo()
    z = H(h)
    clamp = _ybox(side, xp - 17.0, xp + 17.0, yq - 10.0, yq + 11.0, z - 20.0, z + 20.0)
    screws = [ycyl(4.0, *sorted((side * (yq + 11.0), side * (yq + 14.0))), x=xp + dx, z=z) for dx in (-9.0, 9.0)]
    arm = rod((xp, side * (yq + 10.0), z), (xh + 22.0, side * (yh - 22.0), z), 5.5)
    from build123d import Sphere
    ball = Location((xh + 22.0, side * (yh - 22.0), z)) * Sphere(8.0)
    stem = rod((xh + 22.0, side * (yh - 22.0), z), (xh + 10.0, side * yh, z), 5.0)
    head = xprism(G.rounded_rect(side * yh - 38.0, side * yh + 38.0, z - 58.0, z + 58.0, 14.0), xh - 6.0, xh + 12.0)
    from mgb.elec_shapes import tryfillet
    from build123d import Axis
    head = tryfillet(head, head.edges().filter_by_position(Axis.X, xh + 11.0, xh + 13.0), 6.0)
    back = Location((xh + 4.0, side * yh, z)) * Rot(0, 90, 0) * __import__("build123d").Cylinder(26.0, 16.0)
    return _c([clamp, arm, ball, stem, head, back] + screws, spec)


def door_mirror_glass(spec):
    side, h, xp, yq, xh, yh = _mirror_geo()
    z = H(h)
    return _l(xprism(G.rounded_rect(side * yh - 33.0, side * yh + 33.0, z - 53.0, z + 53.0, 11.0), xh - 7.5, xh - 6.0), spec)


HANDLE_REAR_X, HANDLE_FRONT_X = -1608.0, -1434.0   # kf048 ray-cast: escutcheon's rear end and the buffer's front
HANDLE_H = 790.0
HANDLE_X = 0.5 * (HANDLE_REAR_X + HANDLE_FRONT_X)
HANDLE_PIVOT_X = HANDLE_REAR_X + 20.0             # the lever's pivot inside the escutcheon (the lock's link)


def _skin_y(x, h):
    return S.side_y(x, h)


def _handle_lever_pts():
    """Lever sections (x, height centre, height, depth, standoff of its centre from the skin), rear to front."""
    out = []
    x0, x1 = HANDLE_REAR_X + 14.0, HANDLE_FRONT_X - 12.0
    for k in range(9):
        t = k / 8
        x = x0 + (x1 - x0) * t
        # thick at the escutcheon, tapering to the buffer, the top line arched and the tip curving down (kf188, kf189)
        out.append((x, HANDLE_H + 1.0 + 3.0 * math.sin(math.pi * t) * (1 - t) - 7.0 * t ** 3, 22.0 - 12.0 * t ** 0.8,
                    12.0 - 4.0 * t, 13.0 - 6.0 * t))
    return out


def pull_handle(side):
    def build(spec):
        """Exterior pull handle (Fig 12.13 item 1, early Sports Tourer; Oliver's kf048, kf187-kf189 zoomed): a
        chrome escutcheon screwed to the skin at the rear with a lower lip running forward, the lever hinged inside it
        and sweeping forward over the pressed finger recess, tapering and curving down to the rubber buffer at its
        front tip (buffer: handle-buffer)."""
        from build123d import Solid, Wire, Axis
        from mgb.elec_shapes import tryfillet
        h = HANDLE_H
        xr = HANDLE_REAR_X
        ys = _skin_y(xr + 25.0, h)
        # QA fix 2 (kf048): the escutcheon's rear end is rounded in side view (a half round over its full height), not
        # a square block
        esc = G.fuse([ycyl(14.0, *sorted((side * (ys - 2.0), side * (ys + 21.0))), x=xr + 14.0, z=H(h + 1.0)),
                      _ybox(side, xr + 14.0, xr + 34.0, ys - 2.0, ys + 21.0, H(h - 13.0), H(h + 15.0))])
        esc = tryfillet(esc, esc.edges().filter_by_position(Axis.Y, *sorted((side * (ys + 20.5), side * (ys + 21.5)))), 5.0)
        lip = _ybox(side, xr + 20.0, xr + 64.0, ys - 2.0, ys + 13.0, H(h - 14.0), H(h - 5.0))
        lip = tryfillet(lip, lip.edges().filter_by_position(Axis.X, xr + 63.5, xr + 64.5), 4.0)
        pocket = _ybox(side, xr + 18.0, xr + 40.0, ys + 4.0, ys + 18.0, H(h - 6.0), H(h + 11.0))
        wires = []
        for x, hc, ht, dp, so in _handle_lever_pts():
            yc = side * (_skin_y(x, h) + so)
            sec = G.rounded_rect(yc - dp / 2, yc + dp / 2, H(hc) - ht / 2, H(hc) + ht / 2, min(dp, ht) / 2 - 0.3, n=4)
            wires.append(Wire.make_polygon([(x, a, b) for a, b in sec], close=True))
        lever = Solid.make_loft(wires)
        pivot = zcyl(3.0, H(h - 9.0), H(h + 12.0), xr + 22.0, side * (ys + 10.0))
        screws = [ycyl(2.5, *sorted((side * (ys - 12.0), side * (ys - 1.0))), x=xr + 17.0, z=H(h + dh)) for dh in (-8.0, 8.0)]
        return _c([G.fuse([esc, lip]) - pocket, lever, pivot] + screws, spec)
    return build


def handle_buffer(side):
    def build(spec):
        """Black rubber buffer ball on the pull handle lever's front tip, resting on the skin (kf188, kf189)."""
        from build123d import Sphere
        x, hc, ht, dp, so = _handle_lever_pts()[-1]
        r = 7.0
        xb = HANDLE_FRONT_X - r + 1.0
        yb = _skin_y(xb, hc) + r + 0.3
        ball = Location((xb, side * yb, H(hc - 1.0))) * Sphere(r)
        neck = xcyl(3.0, x - 2.0, xb, side * (_skin_y(x, hc) + so), H(hc))
        return _c([ball, neck], spec)
    return build


def striker(side):
    def build(spec):
        """Striker plate on the shut pillar (Sec 27), three screws, shimmed (Fig 12.14 item 11)."""
        x = S.DOOR_REAR_X + S.GAP / 2 - 0.0
        y = side * (S.side_y(x, St.STRIKER_H) - 35.0)
        z = H(St.STRIKER_H)
        plate = box(x - 3.0, x, y - 16.0, y + 16.0, z - 32.0, z + 32.0)
        dove = box(x, x + 0.0 + 1.5, y - 6.0, y + 6.0, z - 10.0, z + 10.0)
        p = plate + dove
        for dz in (-20.0, 0.0, 20.0):
            p = p - xcyl(2.8, x - 5, x + 1, y, z + dz)
        return _l(p, spec)
    return build


# =====================================================================================================================
# bonnet
# =====================================================================================================================
def bonnet_frame_sd(X, Y, Z):
    outer = Pn.bonnet_sd(X, Y, Z) + G2 + 6.0
    inner = B.sd_poly(X, Y, B.bonnet_outline(0.0)) + G2 + 60.0
    cross = AND(np.abs(X - 180.0) - 30.0, Pn.bonnet_sd(X, Y, Z) + G2 + 6.0)
    centre = AND(np.abs(Y) - 28.0, Pn.bonnet_sd(X, Y, Z) + G2 + 6.0, X - 650.0)
    rad = AND(np.abs(X - 400.0) - 75.0, np.abs(Y) - 470.0)          # clear of the radiator's header tank (P2)
    return AND(OR(AND(outer, -inner), cross, centre), -rad)


def bonnet_frame(spec):
    """Bonnet inner frame: the stiffening frame under the skin, a perimeter band 54 mm wide following the skin 22 mm
    below it, a cross brace over the rocker cover and a centre rib to the lock pin; the hinge plates' two bolts each
    side (Sec 6 para 1) and the lock pin's boss."""
    def make():
        return B.skin_sdf(bonnet_frame_sd, 1.0, shift=(0.0, 0.0, -22.0))
    return _l(_cached("bonnet-frame", make), spec)


BH_Y = 400.0                                 # bonnet hinges


def bonnet_hinge(side):
    def build(spec):
        """Bonnet hinge (Sec 6 para 1): bracket on the scuttle's front under the bonnet's rear edge, the arm to the
        bonnet frame with two bolts, nuts and washers."""
        x0 = S.BONNET_REAR_X
        y = side * BH_Y
        zt = H(S.top_h(x0 + 30.0, BH_Y)) - 23.0
        bracket = box(x0 - 40.0, x0 - 4.0, y - 2.0, y + 2.0, zt - 70.0, zt - 10.0)
        arm = rod((x0 - 20.0, y, zt - 40.0), (x0 + 60.0, y, zt - 2.0), 5.0)
        pad = box(x0 + 40.0, x0 + 90.0, y - 14.0, y + 14.0, zt - 3.0, zt)
        pivot = ycyl(5.0, y - 8.0, y + 8.0, x0 - 20.0, zt - 40.0)
        return _c([bracket, arm, pad, pivot], spec)
    return build


def bonnet_stay(spec):
    """Bonnet stay (Sec 6 para 1: 'support it on the stay'; Oliver's photos 13, 28: a thin rod on the car's right,
    from the front of the inner wing up to the bonnet's front corner): a 5/16 in rod with its end cranked into the
    pivot bracket on the right inner wing's top near the front, the other end hooked for the bonnet's stay bracket;
    shown stowed back along the inner wing in its spring clip."""
    x0, x1 = 470.0, -120.0
    y = -St.iw_along(0.5 * (x0 + x1), 60.0, 12.0)[0]          # along the right inner wing's upper wall
    z0, z1 = St.iw_along(x0, 60.0)[1], St.iw_along(x1, 60.0)[1]
    zr = lambda x: z0 + (z1 - z0) * (x0 - x) / (x0 - x1) + 14.0
    rod_ = swept_rod([(x0, y - 14.0, z0 + 6.0), (x0 - 6.0, y - 6.0, zr(x0) - 2.0), (x0 - 40.0, y, zr(x0 - 40.0)),
                      (x1 + 30.0, y, zr(x1 + 30.0)), (x1, y, zr(x1) + 10.0), (x1 - 8.0, y, zr(x1) + 16.0)], 4.0)
    bracket = box(x0 - 18.0, x0 + 18.0, y - 20.0, y - 8.0, z0, z0 + 2.0) + box(x0 - 12.0, x0 + 12.0, y - 20.0, y - 18.0, z0, z0 + 22.0)
    bracket = bracket - ycyl(2.2, y - 22, y - 16, x0, z0 + 6.0)
    for dx in (-10.0, 10.0):
        bracket = bracket - zcyl(2.8, z0 - 1, z0 + 3, x0 + dx, y - 14.0)
    clip = box(x1 + 50.0, x1 + 62.0, y - 8.0, y + 8.0, z1, z1 + 2.0)
    for dy in (-6.0, 6.0):
        clip = clip + box(x1 + 50.0, x1 + 62.0, y + dy - 0.8, y + dy + 0.8, z1, zr(x1 + 56.0) + 3.0)
    return _c([rod_, bracket, clip], spec)


def bonnet_lock(spec):
    """Bonnet lock pin with its thimble and spring on the frame (Sec 6 para 3), and the lock with the locating cup
    on the platform (para 4, photo 6.4)."""
    zp = St.H(S.MOUTH_TOP_H) - 30.0 + 1.2
    x = 700.0
    pin = zcyl(4.0, zp + 2.0, zp + 60.0, x, 0.0)
    thimble = zcyl(9.0, zp + 40.0, zp + 58.0, x, 0.0) - zcyl(4.2, zp + 39, zp + 59, x, 0.0)
    spring = Location((x, 0.0, zp + 20.0)) * __import__("mgb.shapes", fromlist=["coil_spring"]).coil_spring(1.2, 16.0, 20.0, 6.0)
    cup = zcyl(16.0, zp, zp + 8.0, x, 0.0) - zcyl(10.0, zp - 1, zp + 9, x, 0.0)
    locknut = zprism([(x + 7.5 * math.cos(math.radians(60 * k + 30)), 7.5 * math.sin(math.radians(60 * k + 30))) for k in range(6)],
                     zp + 58.0, zp + 64.0)
    return _c([pin, thimble, spring, cup, locknut], spec)


# =====================================================================================================================
# boot lid
# =====================================================================================================================
def boot_frame_sd(X, Y, Z):
    outer = Pn.boot_sd(X, Y, Z) + G2 + 6.0
    inner = B.sd_poly(X, Y, B.boot_outline(0.0)) + G2 + 55.0
    # X-shaped brace corner to corner (Oliver's photo 14)
    x0, x1, w = S.BOOT_FRONT_X - 60.0, -2880.0, S.BOOT_W[0][1] - 60.0

    def seg(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
        return np.hypot(X - ax - t * dx, Y - ay - t * dy) - 24.0
    cross = AND(OR(seg(x0, w, x1, -w), seg(x0, -w, x1, w)), Pn.boot_sd(X, Y, Z) + G2 + 6.0)
    return OR(AND(outer, -inner), cross)


def boot_frame(spec):
    """Boot lid inner frame: perimeter band following the skin 20 mm under it and an X-shaped brace from corner to
    corner (Oliver's photo 14); the hinges' and the lock's fixings."""
    def make():
        return B.skin_sdf(boot_frame_sd, 1.0, shift=(0.0, 0.0, -20.0))
    return _l(_cached("boot-frame", make), spec)


def boot_hinge(side):
    def build(spec):
        """Boot lid hinge (Sec 26): a cranked arm from the rear deck's rear edge under the lid's front edge, two
        bolts each end."""
        x0 = S.BOOT_FRONT_X
        y = side * 400.0
        zt = H(S.top_h(x0 - 40.0, 400.0)) - 21.0
        arm = swept_rod([(x0 + 30.0, y, zt - 60.0), (x0 + 10.0, y, zt - 20.0), (x0 - 60.0, y, zt - 2.0)], 5.0)
        base = box(x0 + 20.0, x0 + 50.0, y - 14.0, y + 14.0, zt - 66.0, zt - 60.0)
        pad = box(x0 - 90.0, x0 - 50.0, y - 14.0, y + 14.0, zt - 4.0, zt - 1.0)
        return _c([arm, base, pad], spec)
    return build


# Boot handle and lock (QA fix round 1): placed by mgb.rear_fittings_layout on the lid's rear fall, square to the skin.
def _handle_frame():
    from build123d import Plane
    from mgb import rear_fittings_layout as RF
    org, xd, yd, zd = RF.skin_frame(RF.BOOT_HANDLE_X, 0.0, up=(0.0, 0.0, 1.0))
    return Location(Plane(origin=org, x_dir=xd, z_dir=zd)), org, yd, zd


def _pear(scale=1.0, n=40):
    """The handle's pear outline in its frame (u right, v up the lid): a round head 45 wide over a taper to a blunt
    point 60 mm below its top (Oliver's photo 25: 44 x 61; Fig 12.12 item 4)."""
    from mgb import rear_fittings_layout as RF
    r = RF.BOOT_HANDLE_W / 2 * scale
    top = RF.BOOT_HANDLE_H * 0.5
    cv = top - r / scale                                   # the head's centre stays put as the outline shrinks
    tip_v, tip_r = top - RF.BOOT_HANDLE_H + 4.0 * (1.0 - scale) + 9.0, 9.0 * scale   # QA fix 2: a rounded teardrop end (kf062, kf104)
    d = cv - tip_v
    a_t = math.asin(min(0.999, (r - tip_r) / d))           # the tangent from the tip circle to the head circle
    pts = []
    for k in range(n + 1):                                 # the head, from the right tangent point over the top
        a = -a_t + (math.pi + 2 * a_t) * k / n
        pts.append((r * math.cos(a), cv + r * math.sin(a)))
    for k in range(9):                                     # the tip, round from the left tangent point
        a = math.pi + a_t + (math.pi - 2 * a_t) * k / 8
        pts.append((tip_r * math.cos(a), tip_v + tip_r * math.sin(a)))
    return pts


def boot_handle(spec):
    """Boot lid handle and lock barrel (Fig 12.12 items 3, 4, 5; Oliver's photo 25, kf062, kf105, kf173): a chrome
    pear-shaped escutcheon domed off the lid, 45 wide and 60 tall, pointed at the bottom, the push-button lock barrel
    with its keyhole in the round head, tapering to a rounded end (QA fix 2: a teardrop, kf062, kf104)."""
    from build123d import Solid as So, Wire, Vector
    loc, org, yd, zd = _handle_frame()
    wires = []
    for w, sc in ((-3.0, 1.0), (0.0, 1.0), (4.0, 0.93), (7.5, 0.78), (9.5, 0.6)):
        wires.append(Wire.make_polygon([Vector(u, v, w) for u, v in _pear(sc)], close=True))
    body = So.make_loft(wires, ruled=False)
    if not body.is_valid:
        body = body.fix()
    from mgb import rear_fittings_layout as RF
    cv = RF.BOOT_HANDLE_H * 0.5 - RF.BOOT_HANDLE_W / 2
    barrel = zcyl(10.0, 5.0, 15.0, 0.0, cv) + zcyl(8.6, 15.0, 17.0, 0.0, cv)            # the push button and its rim
    barrel = barrel - box(-1.1, 1.1, cv - 4.5, cv + 1.0, 14.0, 18.0) - zcyl(2.0, 14.0, 18.0, 0.0, cv + 1.5)   # keyhole
    h = body + barrel                     # QA fix 2: no separate grip ridge; the dome itself is the teardrop (kf062, kf104)
    return _l(loc * h, spec)


def boot_lock(spec):
    """Boot lock body inside the lid behind the handle, square to the skin (Fig 12.12 item 2: the lock on its two
    securing screws, item 7 the operating lever), its claw reaching down to the striker on the rear panel's top edge
    (Sec 25)."""
    loc, org, yd, zd = _handle_frame()
    t = S.T + 7.0                                                    # under the skin, clear of the lid's curve at the flange's ends
    #                                                                  (QA fix 2: the flange showed through as a bar under the handle, kf062)
    case = box(-30.0, 30.0, -22.0, 18.0, -t - 26.0, -t - 1.6) - box(-27.0, 27.0, -19.0, 15.0, -t - 23.0, -t - 1.0)
    flange = box(-40.0, 40.0, -26.0, 24.0, -t - 1.6, -t)
    for du in (-34.0, 34.0):                                         # the lock's two securing screws (Fig 12.12 item 1)
        flange = flange - zcyl(2.8, -t - 3.0, 0.0, du, 14.0)
    # the striker's point in the handle frame: the claw reaches down to it
    hs = S.BOOT_REAR_H - 12.0
    xs = S.tail_x(0.0, hs) + 6.0
    ps = np.array([xs + 15.0, 0.0, H(hs) + 12.0]) - np.array(org)
    vs = float(ps.dot(np.array(yd)))
    ws = min(float(ps.dot(np.array(zd))), -t - 8.0)
    lever = box(-5.0, 5.0, vs + 8.0, -20.0, ws - 2.0, ws + 2.0) + box(-5.0, 5.0, -24.0, -20.0, ws - 2.0, -t - 6.0)   # item 7
    claw = box(-10.0, 10.0, vs - 6.0, vs + 8.0, ws - 8.0, ws + 6.0) - box(-4.0, 4.0, vs - 7.0, vs + 2.0, ws - 9.0, ws + 7.0)
    base = box(xs, xs + 30.0, -24.0, 24.0, H(hs) - 2.0, H(hs) + 0.2)
    for dy in (-16.0, 16.0):
        base = base - zcyl(2.8, H(hs) - 3, H(hs) + 1, xs + 15.0, dy)
    loop = swept_rod([(xs + 15.0, -9.0, H(hs)), (xs + 15.0, -9.0, H(hs) + 12.0), (xs + 15.0, 0.0, H(hs) + 18.0),
                      (xs + 15.0, 9.0, H(hs) + 12.0), (xs + 15.0, 9.0, H(hs))], 3.0)       # striker loop
    return _c([loc * case, loc * flange, loc * lever, loc * claw, base, loop], spec)


PARTS = {"body.doors.mirror": {"build": door_mirror}, "body.doors.mirror-glass": {"build": door_mirror_glass}}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.doors.frame-{n}"] = {"build": door_frame(s_)}
    PARTS[f"body.doors.hinge-lower-{n}"] = {"build": hinge(s_, 0)}
    PARTS[f"body.doors.hinge-upper-{n}"] = {"build": hinge(s_, 1)}
    PARTS[f"body.doors.glass-{n}"] = {"build": door_glass(s_)}
    PARTS[f"body.doors.quarter-light-frame-{n}"] = {"build": quarter_light_frame(s_)}
    PARTS[f"body.doors.quarter-light-glass-{n}"] = {"build": quarter_light_glass(s_)}
    PARTS[f"body.doors.quarter-light-seal-{n}"] = {"build": ql_seal(s_)}
    PARTS[f"body.doors.quarter-light-vent-{n}"] = {"build": quarter_light_vent(s_)}
    PARTS[f"body.doors.handle-buffer-{n}"] = {"build": handle_buffer(s_)}
    PARTS[f"body.doors.glass-channel-{n}"] = {"build": glass_channel(s_)}
    PARTS[f"body.doors.pull-handle-{n}"] = {"build": pull_handle(s_)}
    PARTS[f"body.doors.striker-{n}"] = {"build": striker(s_)}
    PARTS[f"body.front.bonnet-hinge-{n}"] = {"build": bonnet_hinge(s_)}
    PARTS[f"body.rear.boot-hinge-{n}"] = {"build": boot_hinge(s_)}
PARTS.update({
    "body.front.bonnet-frame": {"build": bonnet_frame},
    "body.front.bonnet-stay": {"build": bonnet_stay},
    "body.front.bonnet-lock": {"build": bonnet_lock},
    "body.rear.boot-frame": {"build": boot_frame},
    "body.rear.boot-handle": {"build": boot_handle},
    "body.rear.boot-lock": {"build": boot_lock},
})
