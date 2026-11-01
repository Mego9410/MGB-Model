"""Inlet valve, 18G engine. Haynes Fig 1.9 item 1 / Fig 1.6 item 8, specs p22.

Built as a revolved profile about Z. z = 0 is the combustion face of the head;
the stem runs up +Z to the tip.
"""
import math

from build123d import (Axis, BuildLine, BuildPart, BuildSketch, Line, Part, Plane,
                       Polyline, Spline, make_face, revolve)

from mgb import probes

SPEC = "engine/head/valve-inlet.yaml"


def build(spec) -> Part:
    R = spec.nom("head_diameter") / 2
    r = spec.nom("stem_diameter") / 2
    L = spec.nom("overall_length")
    m = spec.nom("margin_thickness")
    fw = spec.nom("seat_face_radial_width")
    hh = spec.nom("head_height")
    seat = math.radians(spec.nom("seat_angle"))
    gw = spec.nom("collet_groove_width")
    gd = spec.nom("collet_groove_depth")
    gt = spec.nom("collet_groove_from_tip")
    tip_ch = 0.5

    face_top = (R - fw, m + fw * math.tan(seat))      # inner edge of the seat face
    blend_end = (r, hh + 12.0)                          # tulip meets the stem
    g_top, g_bot = L - gt, L - gt - gw

    with BuildPart() as valve:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline((0, 0), (R, 0), (R, m), face_top)
                # concave tulip from the seat face into the stem
                Spline(face_top, (r + 2.2, hh + 3.0), blend_end,
                       tangents=[(-math.cos(seat), math.sin(seat)), (0, 1)])
                Polyline(blend_end, (r, g_bot), (r - gd, g_bot + 0.4),
                         (r - gd, g_top - 0.4), (r, g_top),
                         (r, L - tip_ch), (r - tip_ch, L), (0, L), (0, 0))
            make_face()
        revolve(axis=Axis.Z)
    part = valve.part
    part.label = spec.id
    return part


def _stem(part):
    # the stem is the longest cylindrical face
    return probes.longest_cylinder_diameter(part)


def _seat(part):
    # the seat face is the cone furthest from the axis
    return probes.largest_cone_angle(part)


PROBES = {
    "head_diameter": lambda p: probes.bbox_size(p, "x"),
    "stem_diameter": _stem,
    "seat_angle": _seat,
    "overall_length": lambda p: probes.bbox_size(p, "z"),
}
