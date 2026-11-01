"""Inlet and exhaust valves, 18G engine. Haynes Fig 1.9 / Fig 1.6, specs p22.

Revolved profile about Z. z = 0 is the combustion face; the stem runs up +Z.
"""
import math

from build123d import Axis, BuildLine, BuildPart, BuildSketch, Part, Plane, Polyline, Spline, make_face, revolve

from mgb import probes


def build_valve(spec) -> Part:
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


VALVE_PROBES = {
    "head_diameter": lambda p: probes.bbox_size(p, "x"),
    "stem_diameter": probes.longest_cylinder_diameter,
    "seat_angle": probes.largest_cone_angle,   # the seat face is the cone furthest from the axis
    "overall_length": lambda p: probes.bbox_size(p, "z"),
}

PARTS = {
    "engine.head.valve-inlet": {"build": build_valve, "probes": VALVE_PROBES},
    "engine.head.valve-exhaust": {"build": build_valve, "probes": VALVE_PROBES},
}
