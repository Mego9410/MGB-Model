"""Rocker cover and fixings. Haynes Fig 1.6 items 54 to 60.

Cover frame: gasket face at z = 0, centred on the cover footprint; front is +X.
Cover studs pass through the top at (+/-STUD_DX, STUD_DY).
"""
from build123d import Align, Axis, Box, Location, Part, fillet

from mgb import fasteners as F, probes, shapes as Sh

BASE = (Align.CENTER, Align.CENTER, Align.MIN)
STUD_DX = (99.2, -94.2)     # head-frame studs at +/-96.7 less the cover centre x of -2.5 (unchanged)
STUD_DY = -15.0             # head-frame y 20 less the cover centre y of 35
FILLER_X = 140.0


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
    # pressed stiffening ribs along the top
    for dy in (-30, 30):
        c = c + Box(L - 120, 6, 2.2, align=BASE).moved(Location((-20, dy, H - 0.6)))
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
