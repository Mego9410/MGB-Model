"""Rocker cover and fixings. Haynes Fig 1.6 items 54 to 60.

Cover frame: gasket face at z = 0, centred on the cover footprint; front is +X.
Cover studs pass through the top at (+/-STUD_DX, STUD_DY).
"""
from build123d import Align, Axis, Box, Location, Part, Rot, fillet

from mgb import fasteners as F, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
STUD_DX = (99.2, -94.2)     # head-frame studs at +/-96.7 less the cover centre x of -2.5 (unchanged)
STUD_DY = -15.0             # head-frame y 20 less the cover centre y of 35
FILLER_X = 140.0
BREATHER = (160.0, 55.0)    # breather spigot on the manifold-side wall near the front (cover x, height)
BREATHER_LEN = 20.0


def _l(p, spec):
    p.label = spec.id
    return p


def cover(spec) -> Part:
    L, W, H, t = (spec.nom(k) for k in ("length", "width", "height", "sheet_thickness"))
    outer = fillet(Box(L, W, H, align=BASE).edges().filter_by(Axis.Z), 18)
    outer = fillet(outer.edges().group_by(Axis.Z)[-1], 22)
    inner = fillet(Box(L - 2 * t, W - 2 * t, H - t, align=BASE).edges().filter_by(Axis.Z), 17)
    inner = fillet(inner.edges().group_by(Axis.Z)[-1], 21).moved(Location((0, 0, -0.01)))
    shell = outer - inner
    flange = Box(L + 16, W + 16, 1.6, align=BASE) - Box(L - 2, W - 2, 4, align=BASE).moved(Location((0, 0, -1)))
    flange = fillet(flange.edges().filter_by(Axis.Z).group_by(Axis.X)[0] + flange.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], 6)
    neck = Sh.tube(40, 34, 14, z0=H - 6).moved(Location((FILLER_X, 0, 0)))
    c = shell + flange + neck
    c = c - Sh.cyl(34, 20, z0=H - 10).moved(Location((FILLER_X, 0, 0)))
    for dx in STUD_DX:
        c = c - Sh.cyl(13, 20, z0=H - 10).moved(Location((dx, STUD_DY, 0)))
    # front breather spigot to the front air cleaner (Haynes Ch 1 Sec 10 para 4, Ch 3 Sec 3 para 1)
    bx, bz = BREATHER
    sp = Sh.tube(15, 11, BREATHER_LEN + 2).moved(Location((0, 0, -2)))
    c = c + (Location((bx, W / 2, bz)) * Rot(-90, 0, 0) * sp)
    c = c - (Location((bx, W / 2 - 3, bz)) * Rot(-90, 0, 0) * Sh.cyl(11, 6))
    c = c + (Location((bx, W / 2 + BREATHER_LEN - 3, bz)) * Rot(-90, 0, 0) * Sh.tube(17, 11, 2.5))   # hose bead
    # Oliver's car (engine scan, photos 13, 28): a polished cast alloy cover, longitudinal fins along the top either
    # side of a plain centre band carrying the raised MG octagon, the fins stopped round the filler and the studs
    fins = None
    for dy in (-48.0, -38.0, -28.0, 28.0, 38.0, 48.0):
        f = Box(L - 70, 4.0, 5.0, align=BASE).moved(Location((-5, dy, H - 0.6)))
        f = fillet(f.edges().group_by(Axis.Z)[-1], 1.6)
        fins = f if fins is None else fins + f
    fins = fins - Sh.cyl(46, 12, z0=H - 2).moved(Location((FILLER_X, 0, 0)))
    for dx in STUD_DX:
        fins = fins - Sh.cyl(30, 12, z0=H - 2).moved(Location((dx, STUD_DY, 0)))
    from build123d import Plane, RegularPolygon, extrude
    octa = extrude(Plane.XY.offset(H - 0.6) * RegularPolygon(22, 8), 4.0)
    c = c + fins + octa.moved(Location((-60.0, 0, 0)))
    return _l(c, spec)


def filler_cap(spec) -> Part:
    d, h = spec.nom("diameter"), spec.nom("height")
    p = Sh.revolved([(0, 0), (17, 0), (17, 6), (d / 2, 6), (d / 2, 10), (d / 2 - 4, h), (0, h)])
    return _l(p, spec)


def cover_gasket(spec) -> Part:
    t, w = spec.nom("thickness"), spec.nom("width")
    L, W = 395.0, 122.0
    outer = fillet(Box(L + w, W + w, t, align=BASE).edges().filter_by(Axis.Z), 22)
    inner = fillet(Box(L - w, W - w, t + 2, align=BASE).edges().filter_by(Axis.Z), 14).moved(Location((0, 0, -1)))
    return _l(outer - inner, spec)


def bush(spec) -> Part:
    od, id_, h = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("height")
    p = Sh.revolved([(id_ / 2, 0), (12.5 / 2, 0), (12.5 / 2, h - 3), (od / 2, h - 3), (od / 2, h), (id_ / 2, h)])
    return _l(p, spec)


def cup_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    p = Sh.revolved([(id_ / 2, 3), (id_ / 2 + 3, 3), (od / 2, 0), (od / 2, t), (id_ / 2 + 3, 3 + t), (id_ / 2, 3 + t)])
    return _l(p, spec)


def nut(spec) -> Part:
    return _l(F.hex_nut("1/4"), spec)


def bracket(spec) -> Part:
    L, w, t = spec.nom("length"), spec.nom("width"), spec.nom("thickness")
    flat = Sh.slot_plate(w * 1.6, w, t)
    leg = Box(t, w, L * 0.6, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((w * 0.8 - t, 0, 0)))
    arm = Box(L * 0.55, w, t, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((w * 0.8 - t, 0, L * 0.6 - t)))
    b = flat + leg + arm
    b = b - Sh.cyl(6.8, t * 3, z0=-t)
    b = b - Sh.cyl(9.0, t * 3, z0=L * 0.6 - 2 * t).moved(Location((w * 0.8 + L * 0.3, 0, 0)))
    return _l(b, spec)


PARTS = {
    "engine.head.rocker-cover": {"build": cover},
    "engine.head.filler-cap": {"build": filler_cap},
    "engine.head.rocker-cover-gasket": {"build": cover_gasket},
    "engine.head.rocker-cover-bush": {"build": bush},
    "engine.head.rocker-cover-washer": {"build": cup_washer},
    "engine.head.rocker-cover-nut": {"build": nut, "probes": {
        "across_flats": F.across_flats, "thickness": lambda p: probes.bbox_size(p, "z")}},
    "engine.head.rocker-cover-bracket": {"build": bracket},
}
