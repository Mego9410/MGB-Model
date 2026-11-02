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
ADJ_R = LENS_R - 2.0
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
        b = b + zc(7.0, BOWL_FRONT - 14.0, BOWL_FRONT - 1.0, x, y) - zc(2.4, BOWL_FRONT - 15, BOWL_FRONT + 1, x, y)
    b = b + zc(14.0, BOWL_FRONT - d - 6.0, BOWL_FRONT - d + 0.5) - zc(8.0, BOWL_FRONT - d - 7, BOWL_FRONT - d + 2)   # grommet
    for k in range(3):                                              # fixing screw holes in the flange
        x, y = polar(r0 + 0.5, 30.0 + 120.0 * k)
        b = b - zc(1.8, BOWL_FRONT - 3, BOWL_FRONT + 1, x, y)
    return label(b, spec)


def light_unit(spec) -> Part:
    """7 in light unit on its seating rim (Fig 10.8 items 2 and 4): domed lens with its
    moulded flutes, the reflector behind, the bulb holder or sealed beam plug at the back and
    the seating rim with the three slotted lugs over the adjusting screws."""
    lens = X.lens_dome(LENS_R, 9.0, -4.0)
    for k in range(-6, 7):                                          # vertical flutes (lens prisms)
        lens = lens - box(-LENS_R, LENS_R, k * 12.0 - 0.6, k * 12.0 + 0.6, 4.2, 6.0)
    refl = rev([(14.0, -70.0), (40.0, -60.0), (68.0, -38.0), (LENS_R - 1.0, -10.0), (LENS_R - 1.0, -4.0), (LENS_R - 3.0, -4.0),
                (LENS_R - 3.0, -9.0), (66.0, -36.0), (38.0, -58.0), (14.0, -67.0)])
    plug = zc(14.0, -84.0, -66.0) + zc(18.0, -72.0, -68.0)
    seat = Sh.tube(2 * (LENS_R + 4.0), 2 * (LENS_R - 3.0), 5.0, -12.0)
    for a in ADJ.values():                                          # slotted lugs on the seating rim
        x, y = polar(ADJ_R, a)
        lug = Rot(0, 0, a) * box(LENS_R - 10.0, LENS_R + 2.0, -8.0, 8.0, -12.0, -10.0)
        seat = seat + lug - (Rot(0, 0, a) * box(ADJ_R - 2.6, ADJ_R + 2.6, -2.4, 7.0, -13.0, -9.0))
    return label(lens + refl + plug + seat, spec)


def headlamp_rim(spec) -> Part:
    """Outer chrome rim: hooked over the lugs at the top of the lamp and snapped down, with
    the cut-out at the bottom for a screwdriver (Sec 34 paras 1 and 5)."""
    p = rev([(LENS_R - 2.0, 2.0), (LENS_R + 1.0, 6.0), (RIM_OUT - 5.0, 6.5), (RIM_OUT - 1.0, 3.0), (RIM_OUT, -2.0),
             (RIM_OUT, BOWL_FRONT), (RIM_OUT - 1.4, BOWL_FRONT), (RIM_OUT - 1.4, -2.0), (RIM_OUT - 4.0, 3.5),
             (LENS_R + 1.0, 4.0), (LENS_R - 2.0, 0.6)])
    p = p - box(RIM_OUT - 6.0, RIM_OUT + 2.0, -8.0, 8.0, BOWL_FRONT - 1, -6.0)        # cut-out at the bottom (local +x)
    return label(p, spec)


def dust_excluder(spec) -> Part:
    """Rubber dust excluder between the rim and the wing (Sec 34 para 1)."""
    return label(Sh.tube(2 * (RIM_OUT + 1.5), 2 * (RIM_OUT - 7.0), 2.0, BOWL_FRONT - 2.0), spec)


def adjusting_screw(spec) -> Part:
    """Beam setting screw (Fig 10.7 item 4) with its spring, built at the top position."""
    x, y = polar(ADJ_R, ADJ["top"])
    s = zc(2.3, BOWL_FRONT - 22.0, -9.0, x, y) + zc(4.6, -9.0, -6.5, x, y)
    s = s - (Location((x, y, -6.6)) * Box(1.0, 8.0, 1.4))
    s = s + Location((x, y, BOWL_FRONT - 0.5)) * Sh.coil_spring(0.8, 8.0, 4.5, 4.0)
    return label(s, spec)


# ---- side and flasher lamp ------------------------------------------------------------------------
def _stadium(w, h, n=14):
    r = h / 2
    pts = P2.circle_pts(-(w / 2 - r), 0.0, r, n, 90.0, 270.0) + P2.circle_pts(w / 2 - r, 0.0, r, n, -90.0, 90.0)
    return [(py, px) for px, py in pts]          # long axis along local y (across the car)


def side_body(spec) -> Part:
    """Side and flasher lamp body (photo 35.1): chrome plinth with the two bulb holders,
    held by two nuts on studs behind the wing (Sec 35 para 2)."""
    w, h = spec.nom("width"), spec.nom("height")
    p = X.poly_xy(_stadium(w, h), -10.0, 0.0)
    p = tryfillet(p, p.edges().group_by(Axis.Z)[-1], 3.0)
    p = p - X.poly_xy(_stadium(w - 8.0, h - 8.0), -4.0, 1.0)
    for dx in (-18.0, 18.0):                                        # bulb holders and studs
        p = p + zc(9.0, -9.0, -2.0, 0.0, dx) - zc(6.0, -8.0, -1.0, 0.0, dx)
        p = p + zc(2.4, -26.0, -10.0, 0.0, dx * 1.25)
    return label(p, spec)


def side_lens(colour):
    def build(spec) -> Part:
        """Lens half: clear for the side lamp (upper, local -x), amber for the flasher (lower)."""
        w, h = spec.nom("width"), spec.nom("height")
        lens = X.poly_xy(_stadium(w - 6.0, h - 6.0), -4.5, 5.0)
        lens = tryfillet(lens, lens.edges().group_by(Axis.Z)[-1], 4.0)
        half = box(-h, 0.0, -w, w, -6, 8) if colour == "clear" else box(0.0, h, -w, w, -6, 8)
        lens = lens & half
        for k in range(-3, 4):                                      # moulded ribs
            lens = lens - box(-h, h, k * 9.0 - 0.5, k * 9.0 + 0.5, 4.3, 6.0)
        return label(lens, spec)
    return build


def side_rim(spec) -> Part:
    """Chrome lens rim held by two screws (Sec 35 para 1)."""
    w, h = spec.nom("width"), spec.nom("height")
    r = X.poly_xy(_stadium(w + 1.0, h + 1.0), -1.0, 4.0) - X.poly_xy(_stadium(w - 10.0, h - 10.0), -2.0, 5.0)
    r = r - X.poly_xy(_stadium(w - 5.0, h - 5.0), -2.0, 1.5)
    for dy in (-(w / 2 - 6.0), w / 2 - 6.0):
        r = r + zc(2.8, 1.0, 5.0, 0.0, dy) - zc(1.4, -2, 6, 0.0, dy)
    return label(r, spec)


# ---- rear lamp (stop/tail and flasher) -----------------------------------------------------------
def _rear_outline(grow=0.0):
    # tall tapered lozenge, local x up, y across: wider at the top (photo 36.1)
    pts = P2.circle_pts(52.0, 0.0, 30.0 + grow, 14, -90.0, 90.0) + P2.circle_pts(-62.0, 0.0, 22.0 + grow, 14, 90.0, 270.0)
    return P2.hull(pts)


def rear_body(spec) -> Part:
    """Rear lamp body and chrome plinth (photo 36.1): two bulb holders one above the other,
    fixed by three screws (Sec 36 para 2), the lens hooked over the upper lip."""
    p = X.poly_xy(_rear_outline(3.0), -9.0, 0.0)
    p = tryfillet(p, p.edges().group_by(Axis.Z)[-1], 2.5)
    p = p - X.poly_xy(_rear_outline(-3.0), -5.0, 1.0)
    for x in (40.0, -40.0):
        p = p + zc(11.0, -8.0, -1.0, x, 0.0) - zc(8.0, -7.0, 0.0, x, 0.0)
    for x, y in ((80.0, 0.0), (-10.0, 24.0), (-10.0, -24.0)):
        p = p - zc(1.8, -10, 1, x, y)
    p = p + box(80.0, 86.0, -10.0, 10.0, 0.0, 3.0)                  # upper lip for the lens
    return label(p, spec)


def rear_lens(colour):
    def build(spec) -> Part:
        """Lens: red over the stop/tail bulb (upper), amber over the flasher (lower); one
        moulding held by the screw at the bottom (Sec 36 paras 1, 3)."""
        lens = X.poly_xy(_rear_outline(1.0), -4.0, 6.0)
        lens = tryfillet(lens, lens.edges().group_by(Axis.Z)[-1], 4.5)
        cut = 2.0
        half = box(cut, 120.0, -60, 60, -6, 9) if colour == "red" else box(-120.0, cut, -60, 60, -6, 9)
        lens = lens & half
        for k in range(-10, 12):                                    # horizontal prism ribs
            lens = lens - box(k * 8.0 - 0.6, k * 8.0 + 0.6, -60, 60, 5.0, 7.0)
        if colour == "amber":
            lens = lens + zc(4.5, 4.0, 7.0, -78.0, 0.0) - zc(1.8, -6, 8, -78.0, 0.0)   # lens screw boss
        return label(lens, spec)
    return build


# ---- number plate lamp ----------------------------------------------------------------------------
def plate_lamp(spec) -> Part:
    """Number plate lamp on the inside face of the overrider (Sec 37 para 1; photo 37.1):
    plinth, cover, lens and washer, held by two screws to nuts and distance pieces inside the
    overrider. Shines inward and down onto the plate."""
    w, h = spec.nom("width"), spec.nom("height")
    plinth = X.poly_xy(_stadium(w, h), 0.0, 4.0)
    cover = X.poly_xy(_stadium(w - 4.0, h - 4.0), 4.0, 20.0)
    cover = tryfillet(cover, cover.edges().group_by(Axis.Z)[-1], 6.0)
    cover = cover - (Location((h / 2 - 2.0, 0, 13.0)) * Rot(0, 40.0, 0) * Box(24.0, w - 14.0, 30.0))
    for dy in (-(w / 2 - 7.0), w / 2 - 7.0):
        cover = cover - zc(1.8, -1, 21, 0.0, dy) + zc(3.0, 19.0, 21.0, 0.0, dy)
    return label(plinth + cover, spec)


def plate_lens(spec) -> Part:
    w = spec.nom("width")
    lens = Location((14.0, 0, 12.0)) * Rot(0, 40.0, 0) * Box(2.5, w - 16.0, 18.0)
    return label(lens, spec)


PARTS = {
    "electrical.lamps.headlamp-bowl": {"build": headlamp_bowl},
    "electrical.lamps.light-unit": {"build": light_unit},
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
