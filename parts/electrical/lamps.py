"""Exterior lamps: headlamps (Lucas 7 in, bowl, seating rim, light unit, chrome rim, beam
adjusting screws, dust excluder), front side and flasher lamps, rear stop/tail/flasher lamps
and the number plate lamps on the rear overriders. Haynes Ch 10 Sec 34-37, Figs 10.7 and 10.8
(printed p173), photos 35.1, 36.1, 37.1 (printed p173-174).

Each lamp is built in its own frame with the light shining along local +z, local x down
(headlamp, side lamp) or up (rear lamp); mgb.body_layout gives the positions.
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import elec_shapes as X, fasteners as F, poly2d as P2, shapes as Sh
from mgb.elec_shapes import box, hull_xy, label, polar, rev, sector, tryfillet, xc, yc, zc

# ---- headlamp (Lucas 7 in) ---------------------------------------------------------------------
LENS_R = 7.0 * 25.4 / 2                    # 7 in light unit
RIM_OUT = LENS_R + 10.0
ADJ = {"top": 180.0, "left": 90.0, "right": 270.0}   # local polar angles (local x = down, so 180 = up)
ADJ_R = LENS_R + 3.0
BOWL_FRONT = -14.0


def headlamp_bowl(spec) -> Part:
    """Lamp body (bowl) set into the wing nacelle: a pressed steel shell with the mounting
    flange at the front, three cups for the beam setting screws (Fig 10.7 item 4: one at the
    top for vertical, one each side for horizontal), the wiring grommet at the back."""
    d = spec.nom("depth")
    r0 = RIM_OUT - 4.0
    t = 1.2
    outer = [(0, BOWL_FRONT - d), (32.0, BOWL_FRONT - d), (58.0, BOWL_FRONT - d * 0.78), (78.0, BOWL_FRONT - d * 0.45),
             (r0 - 2.0, BOWL_FRONT - 10.0), (r0 + 2.0, BOWL_FRONT - 2.0), (r0 + 2.0, BOWL_FRONT), (0, BOWL_FRONT)]
    inner = [(0, BOWL_FRONT - d + t), (32.0 - t, BOWL_FRONT - d + t), (58.0 - t, BOWL_FRONT - d * 0.78 + t),
             (78.0 - t, BOWL_FRONT - d * 0.45 + t), (r0 - 2.0 - t, BOWL_FRONT - 10.0), (r0 - 2.0 - t, BOWL_FRONT + 1), (0, BOWL_FRONT + 1)]
    b = rev(outer) - rev(inner)
    for a in ADJ.values():                                          # adjusting screw cups
        x, y = polar(ADJ_R, a)
        b = b + zc(6.0, BOWL_FRONT - 12.0, BOWL_FRONT - 1.0, x, y) - zc(2.4, BOWL_FRONT - 13, BOWL_FRONT + 1, x, y)
    b = b + zc(14.0, BOWL_FRONT - d - 6.0, BOWL_FRONT - d + 0.5) - zc(8.0, BOWL_FRONT - d - 7, BOWL_FRONT - d + 2)   # grommet
    for k in range(3):                                              # fixing screw holes in the flange
        x, y = polar(r0 + 0.5, 30.0 + 120.0 * k)
        b = b - zc(1.8, BOWL_FRONT - 3, BOWL_FRONT + 1, x, y)
    return label(b, spec)


def light_unit(spec) -> Part:
    """7 in light unit's glass (Fig 10.8 item 4; QA fix round 1: Oliver's keyframes kf210, kf212, kf028 show a clear
    Lucas lens with the reflector and bulb plainly visible through it): a domed lens moulded on its face with bands of
    fine vertical flutes (the beam-spreading prisms), divided by three horizontal steps, the lower bands' flutes
    finer. The reflector, bulb and seating rim behind are the reflector part."""
    lens = X.lens_dome(LENS_R, 10.0, -4.0) - X.lens_dome(LENS_R - 2.5, 7.5, -4.5)
    bands = [(-LENS_R, -38.0, 4.4), (-38.0, 4.0, 5.2), (4.0, 42.0, 6.0), (42.0, LENS_R, 8.0)]   # local x is down
    cuts = []
    for x0, x1, pitch in bands:
        k = -int(LENS_R / pitch)
        while k * pitch < LENS_R:
            yk = k * pitch
            cuts.append(box(x0 + 0.6, x1 - 0.6, yk - 0.45, yk + 0.45, -6.0, 8.0))
            k += 1
    for xs in (-38.0, 4.0, 42.0):                                  # steps between the bands
        cuts.append(box(xs - 0.5, xs + 0.5, -LENS_R, LENS_R, -6.0, 8.0))
    from build123d import Compound
    skin = X.lens_dome(LENS_R, 10.0, -4.0) - X.lens_dome(LENS_R, 10.0, -4.9)    # the outer 0.9 mm of the face
    lens = lens - (Compound(cuts) & skin)
    return label(lens, spec)


def reflector(spec) -> Part:
    """The light unit's silvered reflector, bulb and seating rim (Fig 10.8 items 2 and 4; QA fix round 1): a deep
    parabolic bowl, the bulb with its shield cap in the middle (kf210, kf212), the bulb holder or plug at the back,
    and the seating rim with the three slotted lugs over the adjusting screws."""
    refl = rev([(14.0, -70.0), (40.0, -60.0), (68.0, -38.0), (LENS_R - 1.0, -10.0), (LENS_R - 1.0, -4.0), (LENS_R - 3.0, -4.0),
                (LENS_R - 3.0, -9.0), (66.0, -36.0), (38.0, -58.0), (14.0, -67.0)])
    bulb = rev([(0, -66.0), (6.0, -66.0), (6.0, -52.0), (9.5, -44.0), (10.0, -36.0), (8.0, -30.0), (0, -28.0)])
    shield = rev([(0, -31.0), (8.5, -31.0), (9.5, -27.0), (0, -25.5)])                   # the shield cap over the bulb
    plug = zc(14.0, -84.0, -66.0) + zc(18.0, -72.0, -68.0)
    seat = Sh.tube(2 * (LENS_R + 3.0), 2 * (LENS_R - 3.0), 2.0, -12.0)
    for a in ADJ.values():                                          # slotted lugs on the seating rim
        x, y = polar(ADJ_R, a)
        lug = Rot(0, 0, a) * box(LENS_R - 6.0, LENS_R + 8.0, -8.0, 8.0, -12.0, -10.0)
        seat = seat + lug - (Rot(0, 0, a) * box(ADJ_R - 2.6, ADJ_R + 2.6, -2.4, 7.0, -13.0, -9.0))
    return label(refl + bulb + shield + plug + seat, spec)


def headlamp_rim(spec) -> Part:
    """Outer chrome rim: hooked over the lugs at the top of the lamp and snapped down, with
    the cut-out at the bottom for a screwdriver (Sec 34 paras 1 and 5) and the fixing screw
    at the bottom into the wing (QA fix round 1, kf210, kf212)."""
    p = rev([(LENS_R - 2.0, 2.0), (LENS_R + 1.0, 6.0), (RIM_OUT - 5.0, 6.5), (RIM_OUT - 1.0, 3.0), (RIM_OUT, -2.0),
             (RIM_OUT, BOWL_FRONT), (RIM_OUT - 1.4, BOWL_FRONT), (RIM_OUT - 1.4, -2.0), (RIM_OUT - 4.0, 3.5),
             (LENS_R + 1.0, 4.0), (LENS_R - 2.0, 0.6)])
    p = p - box(RIM_OUT - 6.0, RIM_OUT + 2.0, -8.0, 8.0, BOWL_FRONT - 1, -6.0)        # cut-out at the bottom (local +x)
    p = p + box(RIM_OUT - 1.4, RIM_OUT + 0.6, 9.0, 17.0, BOWL_FRONT, -4.0)            # the screw's lug beside it
    scr = xc(3.0, RIM_OUT + 0.6, RIM_OUT + 2.8, 13.0, BOWL_FRONT / 2 - 2.0) + xc(1.6, RIM_OUT - 6.0, RIM_OUT + 0.6, 13.0, BOWL_FRONT / 2 - 2.0)
    scr = scr - box(RIM_OUT + 1.8, RIM_OUT + 3.0, 12.6, 13.4, BOWL_FRONT, 0.0)
    p = p - xc(1.7, RIM_OUT - 2.0, RIM_OUT + 1.0, 13.0, BOWL_FRONT / 2 - 2.0) + scr
    return label(p, spec)


def dust_excluder(spec) -> Part:
    """Rubber dust excluder between the rim and the wing (Sec 34 para 1)."""
    return label(Sh.tube(2 * (RIM_OUT - 1.7), 2 * (LENS_R + 7.5), 2.0, BOWL_FRONT + 0.05), spec)


def adjusting_screw(spec) -> Part:
    """Beam setting screw (Fig 10.7 item 4) with its spring, built at the top position."""
    x, y = polar(ADJ_R, ADJ["top"])
    s = zc(2.3, BOWL_FRONT - 11.0, -9.95, x, y) + zc(4.0, -9.95, -7.5, x, y)       # through the lug, head on its face
    s = s - (Location((x, y, -7.6)) * Box(1.0, 7.0, 1.4))
    s = s + Location((x, y, BOWL_FRONT + 0.05)) * Sh.coil_spring(0.7, 7.0, 1.9, 3.0)   # spring between bowl and lug
    return label(s, spec)


# ---- side and flasher lamp ------------------------------------------------------------------------
def _stadium(w, h, n=14):
    r = h / 2
    pts = P2.circle_pts(-(w / 2 - r), 0.0, r, n, 90.0, 270.0) + P2.circle_pts(w / 2 - r, 0.0, r, n, -90.0, 90.0)
    return [(py, px) for px, py in pts]          # long axis along local y (across the car)


def _rect(w, h, r=6.0, n=4):
    """Rounded rectangle, long axis along local y (across the car): the side and flasher lamp (Oliver's photos 10,
    20: a rectangular unit with a chrome surround)."""
    r = min(r, h / 2 - 0.5, w / 2 - 0.5)
    pts = []
    for cx, cy, a0 in ((h / 2 - r, w / 2 - r, 0.0), (-(h / 2 - r), w / 2 - r, 90.0), (-(h / 2 - r), -(w / 2 - r), 180.0),
                       (h / 2 - r, -(w / 2 - r), 270.0)):
        pts += P2.circle_pts(cx, cy, r, n, a0, a0 + 90.0)
    return pts


SIDE_TURN = 30.0                             # deg: the lamp's face turned outboard with the wing corner (QA finding 20)


def side_body(spec) -> Part:
    """Side and flasher lamp body (photo 35.1; QA fix round 1, Oliver's keyframes kf210-213): the chrome body under the
    bezel with the two bulb holders side by side, held by two nuts on studs behind the wing (Sec 35 para 2), on a
    deep back that meets the wing: the wing there turns less than the lamp's face, so the back is a wedge. Local +y is
    outboard (the assembly turns the right-hand lamp over)."""
    w, h = spec.nom("width"), spec.nom("height")
    p = X.poly_xy(_rect(w, h, 7.0), -26.0, 0.0)
    p = tryfillet(p, p.edges().group_by(Axis.Z)[-1], 2.0)
    p = p - X.poly_xy(_rect(w - 8.0, h - 8.0, 4.0), -4.0, 1.0)
    for dx in (-18.0, 18.0):                                        # bulb holders and studs
        p = p + zc(9.0, -9.0, -2.0, 0.0, dx) - zc(6.0, -8.0, -1.0, 0.0, dx)
        p = p + zc(2.4, -42.0, -26.0, 0.0, dx * 1.25)
    return label(p, spec)


SIDE_SPLIT = 0.33                            # the clear (side lamp) part takes the outboard third (kf210-213, scan)


def _side_cut(w):
    return (w - 12.0) * (0.5 - SIDE_SPLIT)


def side_lens(colour):
    def build(spec) -> Part:
        """Lens (QA fix round 1, kf210-213): clear over the side lamp (outboard third), moulded with fine horizontal
        ribs; amber over the flasher (inboard two thirds), a faceted hip-roofed prism - a ridge along its middle, the
        inboard end drawn to a point - divided by the bezel's bar."""
        w, h = spec.nom("width"), spec.nom("height")
        cut = _side_cut(w)
        if colour == "clear":
            lens = X.poly_xy(_rect(w - 12.0, h - 8.0, 3.0), 0.05, 6.0) & box(-h, h, cut + 1.5, w, -6, 8)
            for k in range(-9, 10):                                     # horizontal ribs (local x is down)
                lens = lens - box(k * 2.6 - 0.45, k * 2.6 + 0.45, -w, w, 4.6, 7.0)
            return label(lens, spec)
        from build123d import Solid, Wire, Vector
        y0, y1 = -(w - 12.0) / 2 + 1.0, cut - 1.5
        hx = (h - 8.0) / 2 - 0.5
        base = [Vector(-hx, y0 + 6.0, 0.05), Vector(-hx, y1, 0.05), Vector(hx, y1, 0.05), Vector(hx, y0 + 6.0, 0.05),
                Vector(0.0, y0 - 2.0, 0.05)]
        mid = [Vector(-hx + 2.0, y0 + 8.0, 4.0), Vector(-hx + 2.0, y1, 4.0), Vector(hx - 2.0, y1, 4.0), Vector(hx - 2.0, y0 + 8.0, 4.0),
               Vector(0.0, y0 + 1.0, 4.0)]
        top = [Vector(-1.0, y0 + 26.0, 11.0), Vector(-1.0, y1, 11.0), Vector(1.0, y1, 11.0), Vector(1.0, y0 + 26.0, 11.0),
               Vector(0.0, y0 + 24.0, 11.0)]
        lens = Solid.make_loft([Wire.make_polygon(base, close=True), Wire.make_polygon(mid, close=True),
                                Wire.make_polygon(top, close=True)], ruled=True)
        if not lens.is_valid:
            lens = lens.fix()
        return label(lens, spec)
    return build


def side_rim(spec) -> Part:
    """Chrome bezel round the lens (QA fix round 1, kf210-213): a rounded-rectangle frame with a sloping face, the
    dividing bar between the amber and clear parts, and its two screws at the ends (Sec 35 para 1)."""
    w, h = spec.nom("width"), spec.nom("height")
    outer = X.poly_xy(_rect(w + 1.0, h + 1.0, 8.0), 0.05, 6.0)
    outer = tryfillet(outer, outer.edges().group_by(Axis.Z)[-1], 3.0)
    r = outer - X.poly_xy(_rect(w - 11.0, h - 7.0, 4.0), -1.0, 7.0)
    cut = _side_cut(w)
    r = r + box(-h / 2 + 3.0, h / 2 - 3.0, cut - 1.5, cut + 1.5, 0.05, 7.0)
    for dy in (-(w / 2 - 2.8), w / 2 - 2.8):
        r = r + zc(2.6, 5.0, 7.0, 0.0, dy) - zc(1.4, -2, 8, 0.0, dy) - box(-0.3, 0.3, dy - 2.2, dy + 2.2, 6.4, 8.0)
    return label(r, spec)


# ---- rear lamp (stop/tail and flasher) -----------------------------------------------------------------------------
# QA fix round 1 (Oliver's photo 25 telephoto, kf058, kf176, kf178): no chrome bar across the lens; the lens is one
# moulding, amber over the top 37 %, red below, and across the bottom 22 % an integral rectangular red reflex block that
# stands proud (its rear face nearer upright than the 33 deg plinth, so it shows a ledge at its top); under it the rim
# ends in a chrome foot carrying the one lens screw. The outline is a gothic arch on parallel sides.
REAR_LEN, REAR_W = 292.0, 84.0                # Oliver's photos 14, 18, 25: 250 mm tall seen from behind on the 33 deg plinth
REAR_AMBER = 0.37 * REAR_LEN                  # (292 on the rake), 97 wide over the 6 mm rim; amber over the top 37 %
REAR_REFLEX = 0.22 * REAR_LEN                 # the reflex block across the bottom 22 %
REAR_ARCH = 0.37 * REAR_LEN                   # the top's arch takes the upper 37 %
REFLEX_PROUD = (2.0, 20.0)                    # the block's face stands this far proud of the lens at its foot and its top


def _rear_outline(grow=0.0, n=16):
    """Lamp outline (local x up the plinth, y across), anticlockwise: parallel sides, rounded bottom corners, a gothic
    arch at the top (two arcs tangent to the sides meeting at the point; Oliver's photo 25, kf176, kf178)."""
    L, W = REAR_LEN + 2 * grow, REAR_W + 2 * grow
    A = REAR_ARCH + grow
    xs = L / 2 - A
    R = (A * A + W * W / 4) / W                              # arc radius: tangent to the side at xs, through the point
    r = 12.0 + grow
    pts = [(-L / 2 + r - r * math.cos(math.radians(90.0 * k / 5)), -W / 2 + r - r * math.sin(math.radians(90.0 * k / 5)))
           for k in range(6)][::-1]
    pts += [(-L / 2 + r - r * math.cos(math.radians(90.0 * k / 5)), W / 2 - r + r * math.sin(math.radians(90.0 * k / 5)))
            for k in range(6)]
    pts = [pts[5 - i] for i in range(6)][::-1] + pts[6:]
    up = [(xs + A * k / n, W / 2 - R + math.sqrt(max(R * R - (A * k / n) ** 2, 0.0))) for k in range(n + 1)]
    up[-1] = (L / 2, 0.0)
    down = [(x, -y) for x, y in reversed(up[:-1])]
    return pts + up + down


def _reflex_cut():
    """Local x of the reflex block's top (the lens's red part ends here)."""
    return -REAR_LEN / 2 + REAR_REFLEX


def _foot(grow=0.0):
    """The rim's chrome foot under the reflex block (kf176, kf178): x range and its depth."""
    return -REAR_LEN / 2 - 6.0 - grow, -REAR_LEN / 2 + 14.0 + grow


def rear_body(spec) -> Part:
    """Rear lamp body and chrome rim (Sec 36; photo 36.1): two bulb holders one above the other, fixed by three
    screws (Sec 36 para 2), the lens hooked over the upper lip and held by one screw through the chrome foot at the
    bottom (para 1), the foot wrapping the reflex block's lower end (Oliver's kf176, kf178)."""
    p = X.poly_xy(_rear_outline(6.0), -9.0, 0.0)
    p = p + (X.poly_xy(_rear_outline(6.0), -0.05, 4.0) - X.poly_xy(_rear_outline(1.5), -1.0, 5.0))   # chrome rim
    p = tryfillet(p, p.edges().group_by(Axis.Z)[-1], 1.2)
    p = p - X.poly_xy(_rear_outline(-3.0), -5.0, 1.0)
    f0, f1 = _foot()
    foot = box(f0, f1, -REAR_W / 2 - 4.0, REAR_W / 2 + 4.0, -2.0, 13.0) & X.poly_xy(_rear_outline(6.0), -3.0, 14.0)
    foot = foot - box(f0 + 5.0, f1 + 1.0, -REAR_W / 2 + 0.5, REAR_W / 2 - 0.5, 4.0, 14.0)     # the cup the block sits in
    foot = tryfillet(foot, foot.edges().group_by(Axis.Z)[-1], 1.5)
    p = p + foot
    for x in (40.0, -40.0):
        p = p + zc(11.0, -8.0, -1.0, x, 0.0) - zc(8.0, -7.0, 0.0, x, 0.0)
    for x, y in ((80.0, 0.0), (-10.0, 24.0), (-10.0, -24.0)):
        p = p - zc(1.8, -10, 1, x, y)
    p = p - xc(1.8, f0 - 1.0, f0 + 7.0, 0.0, 8.0)
    p = p + (xc(4.0, f0 - 1.6, f0 + 0.05, 0.0, 8.0) - box(f0 - 2.0, f0 - 0.9, -0.5, 0.5, 4.0, 12.0))   # screw head and slot
    return label(p, spec)


def rear_lens(colour):
    def build(spec) -> Part:
        """Lens: amber over the flasher at the top 37 %, red over the stop/tail bulb below, and the integral red reflex
        block across the bottom 22 % standing proud with a fine prism grid (Oliver's photo 25, kf176, kf178; Haynes
        draws the early lamp the other way up); one moulding held by the screw at the bottom (Sec 36 paras 1, 3)."""
        lens = X.poly_xy(_rear_outline(1.0), 0.05, 9.0)
        lens = tryfillet(lens, lens.edges().group_by(Axis.Z)[-1], 4.5)
        cut = REAR_LEN / 2 - REAR_AMBER
        xr = _reflex_cut()
        half = box(cut, 180.0, -80, 80, -6, 9) if colour == "amber" else box(xr, cut, -80, 80, -6, 9)
        lens = lens & half
        for k in range(-17, 18):                                    # horizontal prism ribs
            lens = lens - box(k * 8.0 - 0.6, k * 8.0 + 0.6, -60, 60, 8.0, 10.0)
        if colour == "red":
            from build123d import Plane, Polygon, extrude
            f0, f1 = _foot()
            x0, x1 = f0 + 5.5, xr + 0.5
            t0, t1 = 9.0 + REFLEX_PROUD[0], 9.0 + REFLEX_PROUD[1]
            blk = extrude(Plane.XZ * Polygon((x0, 0.05), (x1, 0.05), (x1, t1), (x0, t0), align=None), REAR_W / 2 - 1.5,
                          both=True)
            blk = blk & X.poly_xy(_rear_outline(-0.5), -1.0, 40.0)
            blk = tryfillet(blk, blk.edges().filter_by(Axis.Y), 1.0)
            face = (t1 - t0) / (x1 - x0)                            # the face's slope along x
            for k in range(-4, 5):                                  # the reflex prism grid on the face
                blk = blk - box(x0, x1, k * 8.0 - 0.5, k * 8.0 + 0.5, t0 - 1.2, t1 + 5.0)
            for j in range(1, 8):
                xg = x0 + (x1 - x0) * j / 8
                blk = blk - box(xg - 0.5, xg + 0.5, -60, 60, t0 + face * (xg - x0) - 1.0, t1 + 5.0)
            lens = lens + blk
        return label(lens, spec)
    return build


# ---- number plate lamp ----------------------------------------------------------------------------
def plate_lamp(spec) -> Part:
    """Number plate lamp on the inside face of the overrider near its top (Sec 37 para 1; photo 37.1; Oliver's photo
    25, kf165, kf168, kf171, kf173): a chrome plinth block on the overrider and a round-ended barrel reaching in
    toward the plate, the lens under the barrel; held by two screws to nuts and distance pieces inside the overrider.
    Local frame: z inboard (toward the plate), y up, x fore and aft."""
    w, h = spec.nom("width"), spec.nom("height")
    plinth = box(-16.0, 16.0, -h / 2, h / 2, -6.0, 3.0)
    plinth = tryfillet(plinth, plinth.edges().filter_by(Axis.Z), 4.0)
    block = box(-15.0, 15.0, -h / 2 + 1.0, h / 2 - 1.0, 3.0, 26.0)
    block = tryfillet(block, block.edges().group_by(Axis.Z)[-1], 4.0)
    rb = 11.0                                                        # the barrel, its axis inboard, low on the block
    yb = -h / 2 + rb
    barrel = zc(rb, 14.0, w - rb - 18.0, 0.0, yb) + \
        (Location((0.0, yb, w - rb - 18.0)) * __import__("build123d").Sphere(rb))
    body = plinth + block + barrel
    body = body - box(-8.0, 8.0, -h / 2 - 2.0, -h / 2 + 2.5, 12.0, w - 22.0)            # the lens window underneath
    for dx in (-10.0, 10.0):
        body = body - zc(1.8, -6.5, 27.0, dx, 10.0) + zc(3.0, 25.5, 27.0, dx, 10.0)    # the two screws, heads inboard
    return label(body, spec)


def plate_lens(spec) -> Part:
    """Clear lens in the window under the lamp's barrel, shining in and down on the plate."""
    h, w = spec.nom("height"), spec.nom("width")
    return label(box(-7.6, 7.6, -h / 2 + 0.6, -h / 2 + 2.2, 12.4, w - 22.4), spec)


PARTS = {
    "electrical.lamps.headlamp-bowl": {"build": headlamp_bowl},
    "electrical.lamps.light-unit": {"build": light_unit},
    "electrical.lamps.reflector": {"build": reflector},
    "electrical.lamps.headlamp-rim": {"build": headlamp_rim},
    "electrical.lamps.dust-excluder": {"build": dust_excluder},
    "electrical.lamps.adjusting-screw": {"build": adjusting_screw},
    "electrical.lamps.side-body": {"build": side_body},
    "electrical.lamps.side-lens-clear": {"build": side_lens("clear")},
    "electrical.lamps.side-lens-amber": {"build": side_lens("amber")},
    "electrical.lamps.side-rim": {"build": side_rim},
    "electrical.lamps.rear-body": {"build": rear_body},
    "electrical.lamps.rear-lens-red": {"build": rear_lens("red")},
    "electrical.lamps.rear-lens-amber": {"build": rear_lens("amber")},
    "electrical.lamps.plate-lamp": {"build": plate_lamp},
    "electrical.lamps.plate-lens": {"build": plate_lens},
}
