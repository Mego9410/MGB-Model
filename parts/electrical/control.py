"""Engine-bay electrical units on the inner wings and bulkhead: Lucas RB340 control box, 4FJ
two-fuse block, flasher unit, overdrive relay, overdrive vacuum (throttle) switch and the two
Lucas horns with their brackets. Haynes Ch 10 Sec 8-10 and Fig 10.2 (RB340, printed p166),
Sec 33 and photo 33.1 (fuse block, printed p172), Sec 42 (flasher), Sec 50 (horns), Fig 10.26
(early wiring); Ch 6 Sec 16 and Fig 6.19 (overdrive electrics).

Each unit is built in its own mounting frame: local z out of the panel it bolts to, local y up,
local x along the panel; mgb.body_layout gives the positions and the assembly the frames.
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import elec_shapes as X, fasteners as F, poly2d as P2, shapes as Sh
from mgb.elec_shapes import box, hull_xy, label, polar, rev, tryfillet, xc, yc, zc


def _blade(x, y, z, L=8.0):
    """Lucar spade terminal pointing down (-y) from (x, y, z)."""
    return box(x - 3.2, x + 3.2, y - L, y, z - 0.4, z + 0.4)


def control_box(spec) -> Part:
    """RB340 (Fig 10.2): moulded base with two fixing lugs, the pressed cover held by its
    spring clip (item 7) over the cut-out and the current and voltage regulators, and the row
    of Lucar terminals (B, B, D, WL, F, E) along the bottom edge."""
    w, h, d = spec.nom("width"), spec.nom("height"), spec.nom("depth")
    base = box(-w / 2, w / 2, -h / 2, h / 2, 0.0, 9.0)
    base = tryfillet(base, base.edges().filter_by(Axis.Z), 5.0)
    for s in (-1, 1):                                                   # fixing lugs
        lug = hull_xy([(s * (w / 2 + 9.0), 0.0, 8.0), (s * (w / 2 - 6.0), 0.0, 14.0)], 0.0, 5.0)
        base = base + lug - zc(3.0, -1, 7, s * (w / 2 + 9.0), 0.0)
    cover = box(-w / 2 + 4.0, w / 2 - 4.0, -h / 2 + 10.0, h / 2 - 3.0, 9.0, d)
    cover = tryfillet(cover, cover.edges().group_by(Axis.Z)[-1], 9.0)
    cover = cover - box(-w / 2 + 6.0, w / 2 - 6.0, -h / 2 + 12.0, h / 2 - 5.0, 8.0, d - 1.6)
    for k in range(3):                                                  # stiffening ribs pressed in the top
        cover = cover + box(-w / 2 + 14.0, w / 2 - 14.0, -h / 2 + 22.0 + 14.0 * k, -h / 2 + 24.0 + 14.0 * k, d - 1.0, d + 0.6)
    clip = box(-4.0, 4.0, -h / 2 + 4.0, h / 2 - 1.0, d - 0.2, d + 1.2) + box(-4.0, 4.0, h / 2 - 4.0, h / 2 - 1.0, 9.0, d + 1.2)
    c = base + cover + clip
    for k in range(6):                                                  # terminal row along the bottom edge
        x = -w / 2 + 12.0 + k * (w - 24.0) / 5
        c = c + box(x - 5.0, x + 5.0, -h / 2 - 2.0, -h / 2 + 6.0, 0.0, 14.0) + _blade(x, -h / 2 - 2.0, 9.0)
    return label(c, spec)


def fuse_block(spec) -> Part:
    """Lucas 4FJ (photo 33.1): moulded base with terminals A1-A2 and A3-A4, two 35 A
    cartridge fuses in their spring clips, the two spare fuses in the holders on the base and
    the moulded cover."""
    w, h = spec.nom("width"), spec.nom("height")
    base = box(-w / 2, w / 2, -h / 2, h / 2, 0.0, 7.0)
    base = tryfillet(base, base.edges().filter_by(Axis.Z), 4.0)
    for s in (-1, 1):
        base = base - zc(2.6, -1, 8, s * (w / 2 - 6.0), 0.0)
    for yy in (-9.0, 9.0):                                              # fuses (glass cartridges, brass caps)
        base = base + Location((0, yy, 13.0)) * Rot(0, 90, 0) * (zc(3.2, -14.0, 14.0) + zc(3.6, -16.0, -10.0) + zc(3.6, 10.0, 16.0))
        for s in (-1, 1):                                               # spring clips and terminal screws
            base = base + box(s * 13.0 - 2.5, s * 13.0 + 2.5, yy - 4.0, yy + 4.0, 7.0, 15.0)
            base = base + zc(2.6, 7.0, 11.0, s * 22.0, yy) + _blade(s * 22.0, yy - 3.0, 9.0, 6.0)
    cov = box(-w / 2 + 2.0, w / 2 - 2.0, -h / 2 + 2.0, h / 2 - 2.0, 7.0, 21.0)
    cov = tryfillet(cov, cov.edges().group_by(Axis.Z)[-1], 4.0)
    cov = cov - box(-w / 2 + 3.6, w / 2 - 3.6, -h / 2 + 3.6, h / 2 - 3.6, 6.0, 19.4)
    return label(base + cov, spec)


def flasher(spec) -> Part:
    """Flasher unit: 'a small cylindrical metal container' (Sec 42 para 1), its spade
    terminals (B, L) in the moulded base, held in a spring clip screwed to the panel."""
    r = spec.nom("diameter") / 2
    L = spec.nom("length")
    f = Location((0, 0, r + 3.0)) * Rot(90, 0, 0) * (rev([(0, -L / 2), (r - 2.0, -L / 2), (r, -L / 2 + 2.0), (r, L / 2 - 6.0),
                                                           (r + 0.6, L / 2 - 5.0), (r + 0.6, L / 2), (0, L / 2)]))
    for dx in (-5.0, 5.0):
        f = f + box(dx - 3.2, dx + 3.2, -L / 2 - 8.0, -L / 2, r + 2.6, r + 3.4)
    clip = box(-r - 2.0, r + 2.0, -6.0, 6.0, 0.0, 1.2) + (Location((0, 0, r + 3.0)) * Rot(90, 0, 0) * Sh.tube(2 * r + 2.4, 2 * r + 0.2, 12.0, -6.0)
                                                         - box(-r - 3, r + 3, -7, 7, r + 3.0, 2 * r + 9.0))
    clip = clip - zc(2.0, -1, 3, 0, 0)
    return label(f + clip, spec)


def relay(spec) -> Part:
    """Overdrive relay (MGOC 142169, 'rectangular metal can'): can on a base plate with a
    single fixing tab, four Lucar terminals out of the base."""
    w, h, d = spec.nom("width"), spec.nom("height"), spec.nom("depth")
    can = box(-w / 2, w / 2, -h / 2, h / 2, 1.5, d)
    can = tryfillet(can, can.edges().group_by(Axis.Z)[-1], 3.0)
    plate = box(-w / 2 - 1.0, w / 2 + 1.0, -h / 2 - 1.0, h / 2 + 12.0, 0.0, 1.5)
    plate = plate - zc(2.6, -1, 3, 0, h / 2 + 6.0)
    r = can + plate
    for k in range(4):
        x = -w / 2 + 7.0 + k * (w - 14.0) / 3
        r = r + box(x - 3.2, x + 3.2, -h / 2 - 9.0, -h / 2 + 1.0, d / 2 - 0.4, d / 2 + 0.4)
        r = r + box(x - 4.0, x + 4.0, -h / 2 - 1.5, -h / 2 + 0.01, 4.0, d - 4.0)
    return label(r, spec)


def vacuum_switch(spec) -> Part:
    """Overdrive vacuum (throttle) switch on the bulkhead: drum body with its diaphragm
    cover, the vacuum pipe nipple and two terminals, on a fixing bracket."""
    r = spec.nom("diameter") / 2
    b = box(-24.0, 24.0, -10.0, 10.0, 0.0, 1.5)
    b = b - zc(2.6, -1, 3, -18.0, 0) - zc(2.6, -1, 3, 18.0, 0)
    body = zc(r, 1.5, 22.0) + rev([(0, 22.0), (r + 2.0, 22.0), (r + 2.0, 25.0), (r - 3.0, 31.0), (0, 31.0)])
    body = body + zc(2.8, 31.0, 44.0) - zc(1.4, 30.0, 45.0)              # vacuum nipple
    for dx in (-6.0, 6.0):
        body = body + Location((dx, -r + 2.0, 12.0)) * Rot(90, 0, 0) * zc(1.6, 0.0, 9.0)
    return label(b + body, spec)


def horn(spec) -> Part:
    """Lucas horn (9H12 type, Sec 50 and p162): drum body with the domed cover over the
    diaphragm held by its screw and strap, the trumpet slots in the cover rim, the two
    terminals at the back, on its flexible stalk bracket. Built with the sounding face toward
    +z (forward), the bracket foot below."""
    r = spec.nom("diameter") / 2
    d = spec.nom("depth")
    body = rev([(0, 0), (r * 0.55, 0), (r * 0.9, d * 0.35), (r, d * 0.55), (r, d * 0.8), (r - 2.0, d * 0.8), (0, d * 0.8)])
    cover = rev([(0, d * 0.78), (r + 1.5, d * 0.78), (r + 1.5, d * 0.86), (r * 0.6, d), (0, d * 1.02)])
    for k in range(12):                                                 # sound slots round the cover rim
        a = 30.0 * k
        cover = cover - (Rot(0, 0, a) * box(r * 0.72, r * 0.9, -2.0, 2.0, d * 0.83, d * 1.02))
    cover = cover + zc(5.0, d * 0.95, d * 1.04) + zc(2.0, d * 1.04, d * 1.08)                # adjusting screw boss
    h = body + cover
    for dx in (-8.0, 8.0):                                              # terminals on the back
        h = h + Location((dx, 6.0, 0.0)) * (zc(2.0, -9.0, 0.5) + zc(4.0, -3.0, 0.5))
    stalk = box(-6.0, 6.0, -r - 30.0, -r * 0.3, d * 0.2, d * 0.2 + 3.0)
    foot = box(-14.0, 14.0, -r - 34.0, -r - 30.0, 0.0, d * 0.4)
    foot = foot - (Location((0, -r - 32.0, d * 0.2)) * Rot(90, 0, 0) * zc(4.2, -5, 5))
    h = h + stalk + foot
    return label(h, spec)


def screw(size, length_in):
    def build(spec) -> Part:
        return label(F.hex_bolt(size, length_in), spec)
    return build


PARTS = {
    "electrical.control.control-box": {"build": control_box},
    "electrical.control.fuse-block": {"build": fuse_block},
    "electrical.control.flasher": {"build": flasher},
    "electrical.control.relay": {"build": relay},
    "electrical.control.vacuum-switch": {"build": vacuum_switch},
    "electrical.control.horn": {"build": horn},
    "electrical.control.panel-screw": {"build": screw("1/4", 0.5)},
    "electrical.control.horn-bolt": {"build": screw("5/16", 0.75)},
}
