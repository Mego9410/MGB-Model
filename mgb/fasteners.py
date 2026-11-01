"""Unified-thread fasteners (UNF / UNC) from the standard tables.

The 1963 MGB uses UNF threads for most fixings, UNC into some castings.
Dimensions in inches from:
  thread pitch     ANSI/ASME B1.1 (Unified inch screw threads)
  bolt heads       ANSI/ASME B18.2.1, finished hex bolt / hex cap screw
  nuts             ANSI/ASME B18.2.2, finished hex nut
  plain washers    SAE pattern plain washers (ANSI B18.22.1, type A narrow)
Every part built here carries those references as source S.

Two detail levels: `true_thread=True` sweeps a 60-degree thread form along a
helix (detail view); otherwise the thread is a plain cylinder at the major
diameter (car view), with the thread data kept on the spec card.
"""
from __future__ import annotations

import math

from build123d import (Align, add, Edge, Face, Solid, Wire, Axis, BuildPart, BuildSketch, Cylinder, Helix, Location, Mode,
                       Part, Plane, Polygon, RegularPolygon, chamfer, extrude, sweep)

IN = 25.4

# size: (major dia in, UNF tpi, UNC tpi)
THREADS = {
    "1/4": (0.250, 28, 20), "5/16": (0.3125, 24, 18), "3/8": (0.375, 24, 16),
    "7/16": (0.4375, 20, 14), "1/2": (0.500, 20, 13), "9/16": (0.5625, 18, 12),
    "5/8": (0.625, 18, 11),
}
# size: (across flats, head height) for finished hex bolts / cap screws
BOLT_HEAD = {
    "1/4": (7 / 16, 5 / 32), "5/16": (1 / 2, 13 / 64), "3/8": (9 / 16, 15 / 64),
    "7/16": (5 / 8, 9 / 32), "1/2": (3 / 4, 5 / 16), "9/16": (13 / 16, 23 / 64),
    "5/8": (15 / 16, 25 / 64),
}
# size: (across flats, thickness) for finished hex nuts
NUT = {
    "1/4": (7 / 16, 7 / 32), "5/16": (1 / 2, 17 / 64), "3/8": (9 / 16, 21 / 64),
    "7/16": (11 / 16, 3 / 8), "1/2": (3 / 4, 7 / 16), "9/16": (7 / 8, 31 / 64),
    "5/8": (15 / 16, 35 / 64),
}
# size: (inside dia, outside dia, thickness) SAE plain washers
WASHER = {
    "1/4": (0.281, 0.625, 0.065), "5/16": (0.344, 0.688, 0.065), "3/8": (0.406, 0.812, 0.065),
    "7/16": (0.469, 0.922, 0.065), "1/2": (0.531, 1.062, 0.095), "9/16": (0.594, 1.188, 0.095),
    "5/8": (0.656, 1.312, 0.095),
}
SOURCES = {
    "thread": "ANSI/ASME B1.1 Unified inch screw threads",
    "bolt": "ANSI/ASME B18.2.1 finished hex bolt",
    "nut": "ANSI/ASME B18.2.2 finished hex nut",
    "washer": "SAE plain washer, ANSI B18.22.1 type A narrow",
}


def pitch_mm(size: str, series: str = "UNF") -> float:
    d, unf, unc = THREADS[size]
    return IN / (unf if series == "UNF" else unc)


def _hex_prism(af_mm: float, height: float) -> Part:
    with BuildPart() as p:
        with BuildSketch():
            RegularPolygon(af_mm / math.sqrt(3), 6, major_radius=True)  # flats on +/-Y
        extrude(amount=height)
        # 30-degree chamfer on the top corners, as on a finished hex
        chamfer(p.edges().filter_by(Axis.Z, reverse=True).group_by(Axis.Z)[-1],
                length=af_mm * 0.04)
    return p.part


def _thread(major_mm: float, pitch: float, length: float) -> Part:
    """60-degree V thread swept on a helix, fused to a minor-diameter core.

    Built in standalone (algebra) mode: call it outside any builder context.
    """
    h = 0.866025 * pitch                     # fundamental triangle height
    minor = major_mm - 1.25 * h              # unified external minor diameter (basic)
    r0 = minor / 2
    tooth_h = (major_mm - minor) / 2
    half = pitch * 0.5 * 0.92                # leave a small root land
    helix = Edge.make_helix(pitch, length - pitch, r0 - 0.01)
    prof = Face(Wire.make_polygon([(r0 - 0.02, 0, -half), (r0 + tooth_h, 0, -pitch * 0.06),
                                   (r0 + tooth_h, 0, pitch * 0.06), (r0 - 0.02, 0, half)], close=True))
    thread = sweep(prof, path=helix, is_frenet=True)
    core = Solid.make_cylinder(r0, length)
    return core + thread


def hex_bolt(size: str, length_in: float, series: str = "UNF", thread_len_in: float | None = None,
             true_thread: bool = False) -> Part:
    """Hex bolt, head underside at z = 0, shank along +Z."""
    d = THREADS[size][0] * IN
    af, hh = (v * IN for v in BOLT_HEAD[size])
    L = length_in * IN
    tl = min(L, (thread_len_in or (2 * THREADS[size][0] + 0.25)) * IN)
    thread = _thread(d, pitch_mm(size, series), tl) if true_thread else None
    with BuildPart() as b:
        add(_hex_prism(af, hh).moved(Location((0, 0, -hh))))
        if true_thread:
            if L - tl > 0:
                Cylinder(d / 2, L - tl, align=(Align.CENTER, Align.CENTER, Align.MIN))
            add(thread.moved(Location((0, 0, L - tl))))
        else:
            Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = b.part
    part.label = f"bolt-{series}-{size.replace('/', '_')}x{length_in}"
    return part


def hex_nut(size: str, series: str = "UNF") -> Part:
    d = THREADS[size][0] * IN
    af, t = (v * IN for v in NUT[size])
    with BuildPart() as n:
        add(_hex_prism(af, t))
        Cylinder(d / 2 * 0.92, t, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    part = n.part
    part.label = f"nut-{series}-{size.replace('/', '_')}"
    return part


def plain_washer(size: str) -> Part:
    i, o, t = (v * IN for v in WASHER[size])
    with BuildPart() as w:
        Cylinder(o / 2, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(i / 2, t, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    part = w.part
    part.label = f"washer-{size.replace('/', '_')}"
    return part


def across_flats(part: Part) -> float:
    """Measured distance between opposite flats of a hex (flats normal to Y)."""
    return part.bounding_box().size.Y
