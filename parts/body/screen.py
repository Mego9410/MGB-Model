"""Windscreen (Haynes Ch 12 Sec 18, Figs 12.7-12.9, printed p224-225): the curved glass in its glazing rubber, the RH
and LH pillars with their feet bolted through the scuttle sides, the top rail, the bottom rail on the scuttle, the
centre rod and its brackets, and the interior mirror clamped on the centre rod. Geometry from mgb.body_shell_layout (screen_*).
"""
from __future__ import annotations

import math

from build123d import Compound, Face, Location, Solid, Vector, Wire, thicken

from mgb import body_geom as G, body_shell as B, body_shell_layout as S, side_glass_layout as SG
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, yprism, zcyl

H = S.z_of
GLASS_T = 6.0                               # laminated screen (D)
W = S.SCREEN_HALF_W - 9.0                   # glass edge inside the pillars' channels (no light past it)


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


GLASS_CORNER_R = 55.0                       # the glass's top corners (Oliver's kf046, kf231, kf080: rounded, the frame bending
                                            # into the pillars on about R55)


def _side_clip(margin):
    """Region ahead of the pillars' rear edges (side view) where it lies within the castings' width, so the glass's and
    rails' ends do not show behind the castings."""
    hs = [700.0, 1300.0]
    pts = [(SG.pillar_rear_x(hs[0]) + margin, hs[0]), (0.0, hs[0]), (0.0, hs[1]), (SG.pillar_rear_x(hs[1]) + margin, hs[1])]
    yi = SG.PILLAR_Y_IN - 0.5
    return yprism([(x, H(h)) for x, h in pts], -2000.0, 2000.0) + box(-3000.0, 1000.0, -yi, yi, -1000.0, 3000.0)


def glass(spec):
    """Windscreen glass (Fig 12.7 item 14): curved in plan, raked, in the glazing rubber (15); its top corners rounded
    on about R55 (QA fix round 1: kf046, kf231, kf080) and its side edges kept inside the pillar castings."""
    rows = []
    ys = sorted(set([-W + 2 * W * k / 32 for k in range(33)] +                 # close enough to follow the base's sweep
                    [sg * (W - GLASS_CORNER_R * (1.0 - math.cos(math.pi / 2 * k / 6))) for sg in (-1.0, 1.0)
                     for k in range(1, 6)]))                                   # and denser through the rounded corners
    for y in ys:
        (xb, hb), (xt, ht) = S.screen_base(y), S.screen_top(y)
        ln = math.hypot(xt - xb, ht - hb)
        rv = GLASS_CORNER_R / ln
        dy = abs(y) - (W - GLASS_CORNER_R)
        vmax = 0.994 - (rv * (1.0 - math.sqrt(max(0.0, 1.0 - (dy / GLASS_CORNER_R) ** 2))) if dy > 0 else 0.0)
        rows.append([S.screen_pt(y, 0.006 + (vmax - 0.006) * j / 10) for j in range(11)])
    f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
    g = thicken(f, GLASS_T)
    return _l(g & _side_clip(5.0), spec)


def _edge(v, ys, off=0.0):
    return [tuple(a + b for a, b in zip(S.screen_pt(y, v), (0.0, 0.0, off))) for y in ys]


def _channel(path, across, w_in, w_out, t, r=3.5):
    """Chrome frame section swept along path (car points): a flat channel w_in over the glass edge and w_out beyond it
    (across(point) gives the in-plane direction away from the glass), t thick normal to the glass, its corners
    rounded r (Oliver's photos 09, 27: the frame is a flat chrome band about 30 mm wide round the glass)."""
    wires = []
    for i, p in enumerate(path):
        q0, q1 = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        tng = Vector(*q1) - Vector(*q0)
        tng = tng.normalized()
        a = Vector(*across(p))
        a = (a - tng * a.dot(tng)).normalized()
        n = tng.cross(a).normalized()
        sec = []
        for (ca, cb, a0) in ((w_out - r, t / 2 - r, 0.0), (-w_in + r, t / 2 - r, 90.0), (-w_in + r, -t / 2 + r, 180.0),
                             (w_out - r, -t / 2 + r, 270.0)):
            for k in range(4):
                ang = math.radians(a0 + 90.0 * k / 3)
                sec.append(Vector(*p) + a * (ca + r * math.cos(ang)) + n * (cb + r * math.sin(ang)))
        wires.append(Wire.make_polygon(sec, close=True))
    return Solid.make_loft(wires, ruled=False)


def _up(y):
    (xb, hb), (xt, ht) = S.screen_base(y), S.screen_top(y)
    return (xt - xb, 0.0, ht - hb)


def top_rail(spec):
    """Top rail (Fig 12.7 item 4): flat chrome channel over the glass's top edge from pillar to pillar (about 26 mm
    deep, Oliver's photos 09, 27), the hood's front fastener brackets (6) underneath; its ends run into the pillar
    castings' R55 bends."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    r = _channel(_edge(1.0, ys), lambda p: _up(p[1]), 12.0, 16.0, 13.0) & _side_clip(2.0)
    brackets = [box(S.screen_top(y)[0] - 30.0, S.screen_top(y)[0] - 10.0, y - 20.0, y + 20.0, H(S.screen_top(y)[1]) - 6.0,
                    H(S.screen_top(y)[1]) + 2.0) for y in (-330.0, 330.0)]
    return _c([r] + brackets, spec)


def bottom_rail(spec):
    """Bottom rail (Fig 12.7 item 5) on the scuttle under the glass, its seal (18) closing it to the scuttle."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    rail = _channel(_edge(0.0, ys), lambda p: tuple(-c for c in _up(p[1])), 12.0, 10.0, 12.0)
    return _c([rail], spec)


def bottom_seal(spec):
    """Bottom rail's seal (Fig 12.7 item 18): the black rubber strip closing the rail to the scuttle, standing out
    below the chrome all along the screen's foot (Oliver's photos 09, 15, 27 and scan)."""
    ys = [-S.SCREEN_HALF_W + 2 * S.SCREEN_HALF_W * k / 16 for k in range(17)]
    pts = []
    for (x, y, z) in _edge(0.0, ys):                 # a bead on the scuttle along the rail's front foot
        xs = x + 13.0
        pts.append((xs, y, S.z_of(S.top_h(xs, y)) + 3.0))
    return _c([swept_rod(pts, 9.0)], spec)


def _foot_h(x):
    """Height of the wing / scuttle top under the pillar's foot at x."""
    return S.top_h(x, S.SCREEN_HALF_W)


def pillar_outline():
    """Pillar casting in side view (x, height), left side: the rear edge parallel to the quarter-light's front, the
    front (glass-side) edge leaning further so it tapers to the top, where it rounds into the top rail; at the bottom
    the foot shoe flares forward along the wing top to a rounded nose on its rubber pad (mgb.side_glass_layout)."""
    ht = S.screen_top(S.SCREEN_HALF_W)[1] + 16.0          # the top rail's upper edge at the corner
    xr0 = SG.pillar_rear_x(880.0) - 2.0
    hb = lambda x: _foot_h(x) + SG.PAD_T
    hf = S.DOOR_TOP_H + 85.0                               # where the front edge starts to flare into the foot (kf046)
    xn = SG.SHOE_NOSE_X
    pts = [(xr0, hb(xr0)), (SG.pillar_rear_x(ht), ht), (SG.pillar_front_x(ht), ht), (SG.pillar_front_x(hf), hf),
           (xn - 18.0, hb(xn) + SG.SHOE_H), (xn, hb(xn) + SG.SHOE_H * 0.5), (xn - 4.0, hb(xn))]
    xs = [xn - 4.0 - (xn - 4.0 - xr0) * k / 8 for k in range(1, 8)]
    pts += [(x, hb(x)) for x in xs]
    radii = [2.0, 3.0, 30.0, 60.0, 14.0, 8.0, 3.0] + [0.0] * len(xs)
    return pts, radii


PILLAR_CROWN = 4.0                          # the casting's outer face bowed out this much across its width (kf231, kf232)
PILLAR_CURL_R = 55.0                         # the top rail bends into each pillar on about R55 (kf046, kf231, kf080)


def pillar(side):
    def build(spec):
        """Screen pillar (Fig 12.7 items 2, 3) as on Oliver's car (QA fix round 1): a tapered chrome casting with a
        flat outer face, about 88 mm across in side view above the foot, 75 at mid-height and 58 at the top, its rear
        edge parallel to the quarter-light's front with the rubber strips between and its front edge leaning further;
        the top rail bends into it on about R55; at the foot a shoe flares forward along the wing top to a rounded nose
        on a black rubber pad (pillar-pad); the glass's edge in a channel inside it; under the scuttle the foot's stud
        through the scuttle side to the reinforcement plate (16, 17) and packing (12, 13). Sources: kf046 gridded pair,
        kf048 full res, kf016, kf231, kf232; Oliver's body scan (the chrome reaching x -680 at h 880)."""
        from build123d import Axis, Plane
        from mgb.elec_shapes import tryfillet
        pts, radii = pillar_outline()
        prof = B.fillet_poly(pts, radii)
        yo, yi = SG.PILLAR_Y_OUT, SG.PILLAR_Y_IN
        # the outer face crowned across the casting (kf231, kf232: a convex polished face, bright from every angle): a
        # sheet bowed PILLAR_CROWN out between the rear and front edges, flat on through the foot's flare, thickened
        # inward and cut to the side-view outline
        rows = []
        hs = [S.DOOR_TOP_H - 40.0 + (S.screen_top(S.SCREEN_HALF_W)[1] + 60.0 - S.DOOR_TOP_H + 40.0) * k / 12 for k in range(13)]
        for j in range(15):
            sj = -0.2 + 3.7 * (j / 14) ** 1.6                    # across: denser over the casting, on through the flare
            row = []
            for h in hs:
                xr_, w_ = SG.pillar_rear_x(h), SG.pillar_width(h)
                c = (2.0 * sj - 1.0) / 0.75                       # smooth: bowed over the casting, level beyond
                row.append((xr_ + sj * w_, yo - PILLAR_CROWN * (1.0 - math.exp(-c ** 4)), H(h)))
            rows.append(row)
        sheet = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        slab = thicken(sheet, 10.0, normal_override=(0.0, -1.0, 0.0))
        core = yprism([(x, H(h)) for x, h in prof], yi, yo - 8.0)
        skin = slab & yprism([(x, H(h)) for x, h in prof], yi - 20.0, yo + 1.0)
        body = core
        for so in skin.solids():
            body = body + so
        # the R55 bend into the top rail (front view), and the glass's channel
        zt = H(S.screen_top(S.SCREEN_HALF_W)[1] + 16.0)
        curl = xprism(B.fillet_poly([(yi - 80.0, zt - 600.0), (yo + 2.0, zt - 600.0), (yo + 2.0, zt + 0.5), (yi - 80.0, zt + 0.5)],
                                    [0.0, 0.0, PILLAR_CURL_R, 0.0]), -1500.0, 0.0)
        body = body & curl
        rows = []
        for k in range(5):
            y = W - 60.0 + 70.0 * k / 4
            rows.append([S.screen_pt(y, -0.05 + 1.1 * j / 8) for j in range(9)])
        f = Face.make_surface_from_array_of_points(rows, tol=0.05, min_deg=1, max_deg=3)
        chan = thicken(f, GLASS_T + 2.0, both=True)
        body = body - chan
        bx, bh = S.screen_base(S.SCREEN_HALF_W)
        y = S.SCREEN_HALF_W - 2.0
        hs = _foot_h(bx - 30.0)
        stud = zcyl(4.0, H(hs - 70.0), H(hs + 2.0), bx - 30.0, y)
        plate = box(bx - 70.0, bx + 10.0, y - 22.0, y + 22.0, H(hs) - 76.0, H(hs) - 72.0)
        nut = zcyl(7.0, H(hs) - 82.0, H(hs) - 76.0, bx - 30.0, y)
        parts = [body, stud, plate, nut]
        if side < 0:
            parts = [p.mirror(Plane.XZ) for p in parts]
        return _c(parts, spec)
    return build


def pillar_seal(side):
    def build(spec):
        """Pillar seal (Fig 12.7 items 21, 22) in its retainer (23) along the pillar casting's rear edge, closing on
        the quarter-light frame's front strip (Oliver's kf048 full res, kf231, kf232: a black strip down the pillar's
        rear edge)."""
        from build123d import Plane
        pts, radii = pillar_outline()
        hb = pts[0][1] + 2.0
        ht = S.screen_top(S.SCREEN_HALF_W)[1] + 10.0
        # QA fix 2 (kf015, kf048): a thin black line, 4.5 mm (was 10.5, which read as a heavy black band)
        poly = [(SG.pillar_rear_x(hb) - 4.0, hb), (SG.pillar_rear_x(hb) + 0.5, hb), (SG.pillar_rear_x(ht) + 0.5, ht),
                (SG.pillar_rear_x(ht) - 4.0, ht)]
        seal = yprism([(x, H(h)) for x, h in B.fillet_poly(poly, [1.5, 0.0, 0.0, 2.0])], SG.PILLAR_Y_IN + 5.0, SG.PILLAR_Y_OUT - 1.0)
        zt = H(S.screen_top(S.SCREEN_HALF_W)[1] + 16.0)
        seal = seal & xprism(B.fillet_poly([(SG.PILLAR_Y_IN - 80.0, zt - 600.0), (SG.PILLAR_Y_OUT + 2.0, zt - 600.0),
                                            (SG.PILLAR_Y_OUT + 2.0, zt + 0.5), (SG.PILLAR_Y_IN - 80.0, zt + 0.5)],
                                           [0.0, 0.0, PILLAR_CURL_R, 0.0]), -1500.0, 0.0)
        if side < 0:
            seal = seal.mirror(Plane.XZ)
        return _l(seal, spec)
    return build


def pillar_pad(side):
    def build(spec):
        """Pillar grommet (Fig 12.7 items 8, 11): the black rubber pad under the pillar's foot shoe on the wing top,
        a little proud of the shoe all round (kf046, kf231)."""
        from build123d import Plane
        pts, radii = pillar_outline()
        xr0, xn = pts[0][0], SG.SHOE_NOSE_X
        xs = [xn + 1.0 - (xn + 1.0 - xr0) * k / 10 for k in range(11)]
        top = [(x, _foot_h(x) + SG.PAD_T) for x in xs]
        bot = [(x, _foot_h(x) - 1.0) for x in reversed(xs)]
        pad = yprism([(x, H(h)) for x, h in top + bot], SG.PILLAR_Y_IN - 1.5, SG.PILLAR_Y_OUT + 1.5)
        pad = pad & xprism(B.fillet_poly([(SG.PILLAR_Y_IN - 1.5, H(800.0)), (SG.PILLAR_Y_OUT + 1.5, H(800.0)),
                                          (SG.PILLAR_Y_OUT + 1.5, H(950.0)), (SG.PILLAR_Y_IN - 1.5, H(950.0))], 0.0), -1500.0, 0.0)
        if side < 0:
            pad = pad.mirror(Plane.XZ)
        return _l(pad, spec)
    return build


def _rod_ends():
    """Centre rod's ends: on the bottom rail's bracket and under the top rail's centre."""
    a = S.screen_pt(0.0, 0.0)
    b = S.screen_pt(0.0, 1.0)
    return (a[0] - 24.0, 0.0, a[2] + 4.0), (b[0] - 22.0, 0.0, b[2] - 8.0)


def _rod_at(h):
    """Point on the centre rod at height h."""
    a, b = _rod_ends()
    t = (H(h) - a[2]) / (b[2] - a[2])
    return tuple(p + (q - p) * t for p, q in zip(a, b)), t


def centre_rod(spec):
    """Centre rod (Fig 12.7 item 9) from the scuttle bracket (12) to the top rail's centre bracket, nut (10)."""
    a2, b2 = _rod_ends()
    r = rod(a2, b2, 4.0)
    lower = box(a2[0] - 16.0, a2[0] + 16.0, -12.0, 12.0, a2[2] - 6.0, a2[2] + 4.0)
    upper = box(b2[0] - 12.0, b2[0] + 12.0, -12.0, 12.0, b2[2] - 4.0, b2[2] + 8.0)
    return _c([r, lower, upper], spec)


MIRROR_H = S.SCREEN_TOP_H - 95.0               # interior mirror's centre (Oliver's scan: h about 1100 at the centre rod)
MIRROR_W, MIRROR_HT, MIRROR_D = 160.0, 55.0, 15.0   # kf080: about 160 x 55


def _mirror_geo():
    (xr, _, zr), _ = _rod_at(MIRROR_H + 18.0)        # the clamp on the rod just above the head's centre
    xf = xr - 16.0                                   # head's front (the rod side)
    return xr, zr, xf, H(MIRROR_H)


def mirror(spec):
    """Interior mirror's head (QA fix round 1): a rounded-rectangle tan plastic back about 160 x 55 hung on the
    windscreen's centre rod by its clamp (body.glass.mirror-clamp), the glass facing the driver (Oliver's kf080 zoomed:
    tan back, clamp on the rod near the head's top middle; scan: centre x about -855, h about 1100)."""
    from build123d import Axis
    from mgb.elec_shapes import tryfillet
    xr, zr, xf, zc = _mirror_geo()
    back = xprism(G.rounded_rect(-MIRROR_W / 2, MIRROR_W / 2, zc - MIRROR_HT / 2, zc + MIRROR_HT / 2, 16.0), xf - MIRROR_D, xf)
    back = tryfillet(back, back.edges().filter_by_position(Axis.X, xf - 0.1, xf + 0.1), 6.0)
    rim = xprism(G.rounded_rect(-MIRROR_W / 2 + 3.0, MIRROR_W / 2 - 3.0, zc - MIRROR_HT / 2 + 3.0, zc + MIRROR_HT / 2 - 3.0, 13.0),
                 xf - MIRROR_D - 1.0, xf - MIRROR_D + 0.5)
    return _l(back - rim, spec)


def mirror_glass(spec):
    """The interior mirror's glass in the back's rim, facing rearward."""
    xr, zr, xf, zc = _mirror_geo()
    return _l(xprism(G.rounded_rect(-MIRROR_W / 2 + 3.0, MIRROR_W / 2 - 3.0, zc - MIRROR_HT / 2 + 3.0, zc + MIRROR_HT / 2 - 3.0,
                                    13.0), xf - MIRROR_D - 0.8, xf - MIRROR_D + 0.6), spec)


def mirror_clamp(spec):
    """The interior mirror's chrome clamp round the centre rod: a split collar with its pinch screw and a stem to
    the ball joint in the head's back (kf080)."""
    from build123d import Sphere
    xr, zr, xf, zc = _mirror_geo()
    a, b = _rod_ends()
    d = tuple(q - p for p, q in zip(a, b))
    ln = math.sqrt(sum(c * c for c in d))
    u = tuple(c / ln for c in d)
    p0 = (xr - u[0] * 11.0, 0.0, zr - u[2] * 11.0)
    p1 = (xr + u[0] * 11.0, 0.0, zr + u[2] * 11.0)
    collar = rod(p0, p1, 7.0) - rod(tuple(c - 2 * k for c, k in zip(p0, u)), tuple(c + 2 * k for c, k in zip(p1, u)), 4.05)
    lug = box(xr - 4.0, xr + 4.0, 6.0, 13.0, zr - 6.0, zr + 6.0)
    screw = rod((xr, 13.0, zr), (xr, 17.0, zr), 3.2)
    stem = rod((xr - 6.0, 0.0, zr - 2.0), (xf - 2.0, 0.0, zc + 8.0), 3.5)
    ball = Location((xf + 1.0, 0.0, zc + 8.0)) * Sphere(5.5)
    return _c([collar, lug, screw, stem, ball], spec)


PARTS = {
    "body.glass.windscreen": {"build": glass},
    "body.glass.top-rail": {"build": top_rail},
    "body.glass.bottom-rail": {"build": bottom_rail},
    "body.glass.bottom-seal": {"build": bottom_seal},
    "body.glass.pillar-l": {"build": pillar(1)},
    "body.glass.pillar-r": {"build": pillar(-1)},
    "body.glass.pillar-pad-l": {"build": pillar_pad(1)},
    "body.glass.pillar-seal-l": {"build": pillar_seal(1)},
    "body.glass.pillar-seal-r": {"build": pillar_seal(-1)},
    "body.glass.pillar-pad-r": {"build": pillar_pad(-1)},
    "body.glass.centre-rod": {"build": centre_rod},
    "body.glass.mirror": {"build": mirror},
    "body.glass.mirror-glass": {"build": mirror_glass},
    "body.glass.mirror-clamp": {"build": mirror_clamp},
}
