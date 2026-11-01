"""Valve guides, springs, collars, shrouds, packing rings, caps, collets and clips.

Each part is built about Z with z = 0 at its lower mating face.
"""
from build123d import Box, Location, Part, Rot, Solid, Torus

from mgb import probes, shapes as Sh


def guide(spec) -> Part:
    L, od, id_, ch = (spec.nom(k) for k in ("length", "outside_diameter", "inside_diameter", "top_chamfer"))
    ro, ri = od / 2, id_ / 2
    p = Sh.revolved([(ri, 0), (ro - 0.4, 0), (ro, 0.4), (ro, L - ch), (ro - ch, L), (ri, L)])
    p.label = spec.id
    return p


def spring(spec, length=None) -> Part:
    L = length or spec.nom("free_length")
    p = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, spec.nom("total_coils"))
    p.label = spec.id
    return p


def collar(spec) -> Part:
    ro, ri = spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2
    t, st = spec.nom("thickness"), spec.nom("inner_step_height")
    rs = ri + 4.6  # inner step locates the inner spring's bore
    p = Sh.revolved([(ri, 0), (ro, 0), (ro, t), (rs, t), (rs, t + st), (ri, t + st)])
    p.label = spec.id
    return p


def shroud(spec) -> Part:
    ro, ri = spec.nom("outside_diameter") / 2, spec.nom("inside_diameter") / 2
    h, rf = spec.nom("height"), spec.nom("flange_diameter") / 2
    p = Sh.revolved([(ri, 0), (ro, 0), (ro, h - 1.0), (rf, h - 1.0), (rf, h), (ri, h)])
    p.label = spec.id
    return p


def packing_ring(spec) -> Part:
    ri, s = spec.nom("inside_diameter") / 2, spec.nom("section_diameter")
    p = Part(Torus(ri + s / 2, s / 2).wrapped).moved(Location((0, 0, s / 2)))
    p.label = spec.id
    return p


def spring_cap(spec) -> Part:
    ro, h = spec.nom("outside_diameter") / 2, spec.nom("height")
    bt, bb = spec.nom("bore_top_diameter") / 2, spec.nom("bore_bottom_diameter") / 2
    # flat spring seat underneath, domed top, tapered bore for the collets
    p = Sh.revolved([(bb, 0), (ro - 1.0, 0), (ro, 1.0), (ro, 3.0), (ro - 3.0, h * 0.55),
                     (bt + 2.0, h), (bt, h)])
    p.label = spec.id
    return p


def collet(spec) -> Part:
    """One half of a split taper collet: a cone sleeve cut in half on the XZ plane."""
    L, dt, db = spec.nom("length"), spec.nom("top_diameter"), spec.nom("bottom_diameter")
    bead = spec.nom("bead_width")
    ri = 8.7 / 2 - 0.05          # bore on the stem
    rb = ri - 0.75               # internal bead engages the groove
    zb0 = (L - bead) / 2
    ring = Sh.revolved([(ri, 0), (db / 2, 0), (dt / 2, L), (ri, L), (ri, zb0 + bead), (rb, zb0 + bead - 0.4),
                        (rb, zb0 + 0.4), (ri, zb0)])
    half = ring & Box(30, 30, 30).moved(Location((0, 15 + 0.3, L / 2)))   # leave a 0.6 mm split gap
    half.label = spec.id
    return half


def valve_clip(spec) -> Part:
    w, ri = spec.nom("wire_diameter"), spec.nom("inside_diameter") / 2
    ring = Part(Torus(ri + w / 2, w / 2).wrapped)
    gap = Box(6, ri * 2, w * 4).moved(Location((ri + w, 0, 0)))  # open C-shape
    p = (ring - gap).moved(Location((0, 0, w / 2)))
    p.label = spec.id
    return p


def _zlen(p):
    return probes.bbox_size(p, "z")


PARTS = {
    "engine.head.guide-inlet": {"build": guide, "probes": {
        "length": _zlen, "outside_diameter": lambda p: probes.bbox_size(p, "x"),
        "inside_diameter": lambda p: min(d for d, _ in probes.cylinder_diameters(p))}},
    "engine.head.guide-exhaust": {"build": guide, "probes": {
        "length": _zlen, "outside_diameter": lambda p: probes.bbox_size(p, "x"),
        "inside_diameter": lambda p: min(d for d, _ in probes.cylinder_diameters(p))}},
    "engine.head.spring-outer": {"build": spring, "probes": {"free_length": _zlen}},
    "engine.head.spring-inner": {"build": spring, "probes": {"free_length": _zlen}},
    "engine.head.spring-collar": {"build": collar},
    "engine.head.valve-shroud": {"build": shroud},
    "engine.head.packing-ring": {"build": packing_ring},
    "engine.head.spring-cap": {"build": spring_cap},
    "engine.head.collet": {"build": collet},
    "engine.head.valve-clip": {"build": valve_clip},
}
