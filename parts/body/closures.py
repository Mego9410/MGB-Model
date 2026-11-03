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
GLASS_TOP_H = 1092.0
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


def glass_outline():
    """Door glass in side view (x, height): front edge at the quarter-light post, rear edge raked, top edge under the
    hood; it runs down inside the door to the regulator channel."""
    xf, xr = QL_POST_X - 4.0, S.DOOR_REAR_X + 40.0
    return [(xf, 520.0), (xr, 520.0), (xr, WAIST_H + 20.0), (xr + 150.0, GLASS_TOP_H - 90.0),
            (xr + 320.0, GLASS_TOP_H - 40.0), (xf - 10.0, GLASS_TOP_H)]


def _glass_y(h):
    """Glass plane |y| at height h: in the door's slot at the waist, leaning in with the tumblehome above it."""
    y0 = S.side_y(-1200.0, WAIST_H - 30.0) - 26.0
    return y0 - (h - WAIST_H) * math.tan(math.radians(7.0))


def door_glass(side):
    def build(spec):
        """Wind-up door glass (Fig 12.15 / 12.17 item 1): toughened sheet in the door's slot, raised; its lower
        channel for the regulator's arm studs (Sec 39) at the bottom edge."""
        pts = B.fillet_poly(glass_outline(), [0, 0, 0, 60.0, 60.0, 20.0])
        g = None
        rows = []
        hs = [520.0 + (GLASS_TOP_H - 520.0) * k / 10 for k in range(11)]
        xs = [QL_POST_X - 4.0 - k * (QL_POST_X - 4.0 - S.DOOR_REAR_X - 40.0) / 10 for k in range(11)]
        for x in xs:
            rows.append([(x, side * _glass_y(h), H(h)) for h in hs])
        f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        slab = thicken(f, GLASS_T)
        clip = side_prism_xz(pts, -2000.0, 2000.0)
        g = slab & clip
        chan = box(S.DOOR_REAR_X + 80.0, QL_POST_X - 30.0, side * _glass_y(540.0) - 6.0, side * _glass_y(540.0) + 6.0,
                   H(520.0) - 10.0, H(540.0))
        return _c([g, chan & side_prism_xz(G.rect(QL_POST_X - 40, S.DOOR_REAR_X + 60, 500, 560), -2000, 2000)], spec)
    return build


def side_prism_xz(pts_ag, y0, y1):
    return yprism([(x, H(h)) for x, h in pts_ag], y0, y1)


def ql_outline():
    """Quarter-light (ventilator) in side view: the front edge along the screen pillar's rake, the rear post at
    QL_POST_X, the bottom on the door top."""
    xb = -770.0                                  # at the screen pillar's foot (profile photo 29)
    rake = math.tan(math.radians(S.SCREEN_RAKE_DEG))
    xt = xb - (GLASS_TOP_H - 8.0 - WAIST_H) * rake
    return [(xb, WAIST_H + 8.0), (QL_POST_X + 8.0, WAIST_H + 8.0), (QL_POST_X + 8.0, GLASS_TOP_H - 5.0),
            (xt, GLASS_TOP_H - 8.0)]


def quarter_light_frame(side):
    def build(spec):
        """Quarter-light frame (Sec 21; Fig 12.15 item 1 'ventilator securing nuts'): chrome channel round the
        pivoting ventilator glass, the divider post down into the door to its two securing nuts, the pivot and catch."""
        pts = ql_outline()
        loop = pts + [pts[0]]
        yq = side * _glass_y(WAIST_H + 150.0)
        segs = []
        for a, b in zip(loop, loop[1:]):
            segs.append(rod((a[0], yq, H(a[1])), (b[0], yq, H(b[1])), 6.5))
        post = rod((QL_POST_X, yq, H(WAIST_H - 160.0)), (QL_POST_X, yq, H(GLASS_TOP_H - 5.0)), 6.0)
        pivot = zcyl(4.0, H(WAIST_H + 8.0), H(WAIST_H + 30.0), QL_POST_X - 40.0, yq)
        catch = box(QL_POST_X + 4.0, QL_POST_X + 22.0, yq - side * 14.0 - 4, yq - side * 14.0 + 4, H(WAIST_H + 150.0), H(WAIST_H + 170.0))
        return _c(segs + [post, pivot, catch], spec)
    return build


def quarter_light_glass(side):
    def build(spec):
        pts = ql_outline()
        yq = side * _glass_y(WAIST_H + 150.0)
        inset = [(pts[0][0] - 12, pts[0][1] + 8), (pts[1][0] + 8, pts[1][1] + 8), (pts[2][0] + 8, pts[2][1] - 10),
                 (pts[3][0] - 2, pts[3][1] - 10)]
        g = side_prism_xz(inset, yq - 2.0, yq + 2.0)
        return _l(g, spec)
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


def door_lock(side):
    def build(spec):
        """Door lock (Fig 12.13 item 15/47) on the rear shut face, its latch engaging the striker."""
        x = _door_x(St.STRIKER_H, True)
        y = side * (S.side_y(x, St.STRIKER_H) - 35.0)
        z = H(St.STRIKER_H)
        body = box(x + 0.6, x + 40.0, y - 18.0, y + 18.0, z - 40.0, z + 40.0)
        latch = box(x - 6.0, x + 0.6, y - 8.0, y + 8.0, z - 12.0, z + 12.0)
        return _c([body, latch], spec)
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
    """Bonnet stay (Sec 6 para 1: 'support it on the stay'), stowed along the left inner wing in its clip."""
    x0, x1 = -300.0, 250.0
    y = St.IW_Y - 12.0
    z = St.inner_wing_top(0.0) - 30.0
    rod_ = rod((x0, y, z), (x1, y, z + 8.0), 4.0)
    pivot = ycyl(7.0, y - 2, y + 10, x0, z)
    clip = box(x1 - 10.0, x1 + 10.0, y - 6.0, y + 10.0, z - 6.0, z + 14.0) - ycyl(4.4, y - 10, y + 12, x1, z + 8.0)
    return _c([rod_, pivot, clip], spec)


def bonnet_lock(spec):
    """Bonnet lock pin with its thimble and spring on the frame (Sec 6 para 3), and the lock with the locating cup
    on the platform (para 4, photo 6.4)."""
    zp = St.H(S.MOUTH_TOP_H) - 30.0 + 1.2
    x = 700.0
    pin = zcyl(4.0, zp + 2.0, zp + 60.0, x, 0.0)
    thimble = zcyl(9.0, zp + 40.0, zp + 58.0, x, 0.0) - zcyl(4.2, zp + 39, zp + 59, x, 0.0)
    spring = Location((x, 0.0, zp + 20.0)) * __import__("mgb.shapes", fromlist=["coil_spring"]).coil_spring(1.2, 16.0, 20.0, 6.0)
    cup = zcyl(16.0, zp, zp + 8.0, x, 0.0) - zcyl(10.0, zp - 1, zp + 9, x, 0.0)
    lock = box(x - 30.0, x + 30.0, -40.0, 40.0, zp - 22.0, zp - 1.2)
    return _c([pin, thimble, spring, cup, lock], spec)


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


BOOT_HANDLE_X = -2905.0


def _tail_pt(y, h, off=0.0):
    return (S.tail_x(y, h) - off, y, H(h))


def boot_handle(spec):
    """Boot lid handle with the lock barrel (Fig 12.12 items 1, 2: handle and lock with its push button), chrome, on
    the lid's rear face above the number plate."""
    h = S.BOOT_REAR_H + 40.0
    pts = [_tail_pt(y, h, 14.0) for y in (-75.0, -55.0, 55.0, 75.0)]
    pts[0] = _tail_pt(-75.0, h, 2.0)
    pts[3] = _tail_pt(75.0, h, 2.0)
    bar = swept_rod(pts, 7.0)
    boss = rod(_tail_pt(0.0, h, 0.0), _tail_pt(0.0, h, 22.0), 11.0)
    button = rod(_tail_pt(0.0, h, 22.0), _tail_pt(0.0, h, 26.0), 6.0)
    return _c([bar, boss, button], spec)


def boot_lock(spec):
    """Boot lock body inside the lid's rear panel and the striker on the rear panel's top edge (Sec 25)."""
    h = S.BOOT_REAR_H + 40.0
    x = S.tail_x(0.0, h) + 30.0
    body = box(x, x + 30.0, -30.0, 30.0, H(h) - 30.0, H(h) + 20.0)
    hs = S.BOOT_REAR_H - 12.0
    xs = S.tail_x(0.0, hs) + 6.0
    strk = box(xs, xs + 22.0, -20.0, 20.0, H(hs) - 2.0, H(hs) + 0.5) + box(xs + 8.0, xs + 14.0, -8.0, 8.0, H(hs), H(hs) + 14.0)
    return _c([body, strk], spec)


PARTS = {"body.doors.mirror": {"build": door_mirror}, "body.doors.mirror-glass": {"build": door_mirror_glass}}
for s_, n in ((1, "l"), (-1, "r")):
    PARTS[f"body.doors.frame-{n}"] = {"build": door_frame(s_)}
    PARTS[f"body.doors.hinge-lower-{n}"] = {"build": hinge(s_, 0)}
    PARTS[f"body.doors.hinge-upper-{n}"] = {"build": hinge(s_, 1)}
    PARTS[f"body.doors.glass-{n}"] = {"build": door_glass(s_)}
    PARTS[f"body.doors.quarter-light-frame-{n}"] = {"build": quarter_light_frame(s_)}
    PARTS[f"body.doors.quarter-light-glass-{n}"] = {"build": quarter_light_glass(s_)}
    PARTS[f"body.doors.pull-handle-{n}"] = {"build": pull_handle(s_)}
    PARTS[f"body.doors.lock-{n}"] = {"build": door_lock(s_)}
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
