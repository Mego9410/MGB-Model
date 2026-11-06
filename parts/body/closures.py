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

from mgb import body_geom as G, body_layout as BL, body_shell as B, body_shell_layout as S
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
WAIST_H = S.DOOR_TOP_H - 6.0                             # door top inner edge (below the roll) where the glass slot is
DOOR_IN = 72.0                               # inner panel this far inboard of the skin
QL_POST_X = -1104.0                         # quarter-light's rear post (divider) at the waist
GLASS_TOP_H = 1160.0                          # the glass runs 8 mm up into the hood's edge (P11b QA); the quarter-light's top
                                              # rail 16 mm lower, at 1144 (Oliver's scan: 1150, with the taller, more upright screen)
GLASS_T = 4.0


DOOR_APERTURES = [(-1010.0, -1260.0, 420.0, 700.0), (-1330.0, -1560.0, 380.0, 640.0)]   # (x0, x1, h0, h1)


def door_inner_sd(side):
    def f(X, Y, Z):
        holes = OR(*[B.sd_poly(X, Z, G.rounded_rect(x1, x0, H(h0), H(h1), 40.0)) for x0, x1, h0, h1 in DOOR_APERTURES])
        return AND(Pn.door_sd(X, Y, Z, side) + G2 + 10.0, Z - H(WAIST_H - 12.0), -holes)
    return f


def _door_x(h, rear):
    lean = S.DOOR_REAR_LEAN * (h - S.DOOR_BOTTOM_H) / (1100.0 - S.DOOR_BOTTOM_H)
    return (S.DOOR_REAR_X + G2 + 8.0 + lean) if rear else (S.DOOR_FRONT_X - G2 - 8.0)


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
                pts = [(S.side_y(_door_x(h, rear), h) - 1.5 - DOOR_IN, H(h)) for h in hs]
                pts += [(S.side_y(_door_x(h, rear), h) - 1.5, H(h)) for h in reversed(hs)]
                x = _door_x(S.DOOR_BOTTOM_H, rear)
                face = xprism(pts, x - 0.6, x + 0.6)
                for hh in (St.HINGE_H if not rear else (St.STRIKER_H,)):
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
        xp = S.DOOR_FRONT_X - G2
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
    """Door glass in side view (x, height): front edge in the quarter-light post's channel, the top along the hood's
    side edge, the rear edge at the door's rear shut line raked forward slightly and rounded into the top (Oliver's
    photos 08, 09, 23; the glass runs the whole length of the door); it runs down inside the door to the regulator
    channel."""
    xf = QL_POST_X - 4.0
    return [(xf, 520.0), (GLASS_REAR_X, 520.0), (GLASS_REAR_X, WAIST_H + 20.0),
            (GLASS_REAR_X + GLASS_REAR_RAKE, GLASS_TOP_H - 14.0), (xf - 10.0, GLASS_TOP_H)]


GLASS_RADII = [0, 0, 0, 75.0, 6.0]


def glass_top_h(x):
    """Height of the door glass's top (and raked rear) edge at x, from the rounded outline: the hood's side edge
    follows it."""
    pts = B.fillet_poly(glass_outline(), GLASS_RADII)
    xr = GLASS_REAR_X
    xtop = QL_POST_X - 14.0                       # the top front corner (the front edge leans back 10 mm)
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
        xs = [QL_POST_X + 6.0 - k * (QL_POST_X + 6.0 - GLASS_REAR_X + 10.0) / 10 for k in range(11)]
        for x in xs:
            rows.append([(x, side * _glass_ys(h), H(h)) for h in hs])
        f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        slab = thicken(f, GLASS_T)
        clip = side_prism_xz(pts, -2000.0, 2000.0)
        g = slab & clip
        yc = side * _glass_ys(540.0)
        chan = box(GLASS_REAR_X + 60.0, QL_POST_X - 30.0, yc - 6.0, yc + 6.0, H(520.0) - 10.0, H(540.0))
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


QL_FRONT_X = -778.0                         # frame's front edge at the door top: just clear of the pillar, the seal between


def ql_outline():
    """Quarter-light (ventilator) in side view: the front edge along the screen pillar's rake, the rear post at
    QL_POST_X, the bottom on the door top."""
    xb = QL_FRONT_X                              # at the screen pillar's foot (profile photo 29)
    rake = S.pillar_rake()
    xt = xb - (QL_TOP_H - WAIST_H) * rake
    return [(xb, WAIST_H + 8.0), (QL_POST_X + 8.0, WAIST_H + 8.0), (QL_POST_X + 8.0, QL_TOP_H + 3.0), (xt, QL_TOP_H)]


QL_TOP_H = GLASS_TOP_H - 16.0                    # the frame's top under the hood's edge
QL_FRONT_Y = S.SCREEN_HALF_W + 13.0              # the frame's front edge closes on the screen pillar's rear (photos 09, 27)


def ql_y(x, h):
    """|y| of the quarter-light's plane: on the door glass's line at the rear post, toed in at the front so its front
    edge closes on the windscreen pillar (Oliver's photos 09, 15, 27)."""
    rake = S.pillar_rake()
    xfront = QL_FRONT_X - (h - WAIST_H - 8.0) * rake
    s = (x - QL_POST_X) / (xfront - QL_POST_X)
    return _glass_ys(h) + (QL_FRONT_Y - _glass_ys(h)) * max(0.0, min(1.0, s))


def _qp(x, h, side, dy=0.0):
    return (x, side * (ql_y(x, h) + dy), H(h))


def quarter_light_frame(side):
    def build(spec):
        """Quarter-light frame (Sec 21; Fig 12.15 item 1 'ventilator securing nuts'): chrome channel round the
        pivoting ventilator glass, the divider post down into the door to its two securing nuts, the pivot and catch;
        toed in at the front to close on the windscreen pillar, its rubber seal along the front edge."""
        pts = ql_outline()
        loop = pts + [pts[0]]
        yq = side * _glass_y(WAIST_H + 150.0)
        segs = []
        for a, b in zip(loop, loop[1:]):
            n = 4
            line = [_qp(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n, side) for k in range(n + 1)]
            segs.append(swept_rod(line, 6.5))
        post = rod((QL_POST_X, yq, H(WAIST_H - 160.0)), (QL_POST_X, side * _glass_y(QL_TOP_H), H(QL_TOP_H + 3.0)), 6.0)
        pivot = zcyl(4.0, H(WAIST_H + 8.0), H(WAIST_H + 30.0), QL_POST_X - 40.0, side * ql_y(QL_POST_X - 40.0, WAIST_H + 20.0))
        catch = box(QL_POST_X + 4.0, QL_POST_X + 22.0, yq - side * 14.0 - 4, yq - side * 14.0 + 4, H(WAIST_H + 150.0), H(WAIST_H + 170.0))
        return _c(segs + [post, pivot, catch], spec)
    return build


def quarter_light_glass(side):
    def build(spec):
        pts = ql_outline()
        inset = [(pts[0][0] - 12, pts[0][1] + 8), (pts[1][0] + 8, pts[1][1] + 8), (pts[2][0] + 8, pts[2][1] - 10),
                 (pts[3][0] - 2, pts[3][1] - 10)]
        a, b, c, d = inset                      # bottom front, bottom rear, top rear, top front
        rows = []
        for i in range(5):
            t = i / 4
            lo = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            hi = (d[0] + (c[0] - d[0]) * t, d[1] + (c[1] - d[1]) * t)
            rows.append([_qp(lo[0] + (hi[0] - lo[0]) * k / 4, lo[1] + (hi[1] - lo[1]) * k / 4, side, -2.0)
                         for k in range(5)])
        f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        return _l(thicken(f, 4.0), spec)
    return build


def ql_seal(side):
    def build(spec):
        """Rubber seal along the quarter-light frame's front edge against the windscreen pillar."""
        pts = ql_outline()
        a, d = pts[0], pts[3]
        line = [(a[0] + (d[0] - a[0]) * k / 4 + 10.0, side * (QL_FRONT_Y - 3.0), H(a[1] + (d[1] - a[1]) * k / 4))
                for k in range(5)]
        return _l(swept_rod(line, 6.0), spec)                  # touching both: no light between them
    return build


def door_mirror(spec):
    """Door mirror (Oliver's photos 08, 15, 23): a rectangular chrome head with rounded corners on a flat arm from a
    clamp on the right-hand quarter-light's rear post (the driver's side)."""
    side = -1
    yq = side * _glass_y(WAIST_H + 150.0)
    zc = H(WAIST_H + 190.0)
    x = QL_POST_X - 2.0
    clamp = box(x - 14.0, x + 14.0, yq - 9.0, yq + 9.0, zc - 22.0, zc + 22.0)
    ya = yq + side * 75.0
    arm = box(x - 9.0, x + 9.0, min(yq, ya), max(yq, ya), zc - 5.0, zc + 5.0)
    yh = yq + side * 95.0
    head = xprism(G.rounded_rect(yh - 38.0, yh + 38.0, zc - 58.0, zc + 58.0, 14.0), x - 6.0, x + 18.0)
    from mgb.elec_shapes import tryfillet
    from build123d import Axis
    head = tryfillet(head, head.edges().filter_by_position(Axis.X, x + 17.0, x + 19.0), 5.0)
    glass = xprism(G.rounded_rect(yh - 33.0, yh + 33.0, zc - 53.0, zc + 53.0, 11.0), x - 7.0, x - 5.5)
    pivot = rod((x, ya, zc), (x, yh - side * 30.0, zc), 6.0)
    return _c([clamp, arm, head, pivot], spec)


def door_mirror_glass(spec):
    side = -1
    yq = side * _glass_y(WAIST_H + 150.0)
    zc = H(WAIST_H + 190.0)
    x = QL_POST_X - 2.0
    yh = yq + side * 95.0
    return _l(xprism(G.rounded_rect(yh - 33.0, yh + 33.0, zc - 53.0, zc + 53.0, 11.0), x - 7.5, x - 6.0), spec)


HANDLE_X = -1518.0                           # profile photo 29: the handle at X -1428 to -1607
HANDLE_H = 790.0


def pull_handle(side):
    def build(spec):
        """Early exterior pull handle (Fig 12.13 item 1, 'outer door handle' of the early Sports Tourer, with the lock
        barrel 3 in its front boss): a chrome bar standing off the skin on two bosses, held by the spring clip (2)
        from inside."""
        x0, x1 = HANDLE_X - 55.0, HANDLE_X + 65.0
        h = HANDLE_H
        ys = lambda x: S.side_y(x, h)
        a = (x0, side * (ys(x0) + 1.0), H(h))
        b = (x1, side * (ys(x1) + 1.0), H(h))
        bar = swept_rod([(x0 - 4.0, side * (ys(x0) + 14.0), H(h)), (x0 + 20.0, side * (ys(x0) + 22.0), H(h)),
                         (x1 - 20.0, side * (ys(x1) + 22.0), H(h)), (x1 + 4.0, side * (ys(x1) + 14.0), H(h))], 6.0)
        bosses = [rod(a, (a[0], side * (ys(x0) + 16.0), a[2]), 9.0), rod(b, (b[0], side * (ys(x1) + 16.0), b[2]), 9.0)]
        barrel = rod((x1, side * (ys(x1) + 14.0), H(h)), (x1, side * (ys(x1) + 19.0), H(h)), 6.0)
        return _c([bar] + bosses + [barrel], spec)
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
    tip_v, tip_r = top - RF.BOOT_HANDLE_H + 4.0 * (1.0 - scale) + 3.5, 3.5 * scale
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
    with its keyhole in the round head and a rounded grip ridge running down to the point."""
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
    grip = So.make_loft([Wire.make_polygon([Vector(u * s_, v, w) for u, v in ((-5.0, cv - 4.0), (5.0, cv - 4.0),
                                                                           (3.0, -24.0), (-3.0, -24.0))], close=True)
                         for s_, w in ((1.0, 6.0), (0.55, 12.0))], ruled=True)
    h = body + barrel + grip
    return _l(loc * h, spec)


def boot_lock(spec):
    """Boot lock body inside the lid behind the handle, square to the skin (Fig 12.12 item 2: the lock on its two
    securing screws, item 7 the operating lever), its claw reaching down to the striker on the rear panel's top edge
    (Sec 25)."""
    loc, org, yd, zd = _handle_frame()
    t = S.T + 2.0                                                    # under the skin (the lid curves away at the flange's edges)
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
