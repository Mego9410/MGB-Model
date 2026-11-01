"""Rocker shaft assembly parts. Haynes Fig 1.6 items 20 to 36.

Local frames:
  shaft, spacing spring, bush, rocker: shaft axis along X through the origin
  bracket: base at z = 0, shaft axis along X at z = height_to_shaft_centre
  rocker: valve arm toward -Y, pushrod arm (adjusting screw) toward +Y
  screws, nuts, washers: axis Z, base at z = 0
"""
import math

from build123d import (Align, Box, Cylinder, Location, Part, Plane, Polygon, Rot, Sphere, Torus,
                       extrude)

from mgb import fasteners as F, probes, shapes as Sh

IN = 25.4
TO_X = Rot(0, 90, 0)  # turns a Z-axis part onto the X axis
LOCATING_X = 48.35    # the locating bracket sits at cylinder 2


def _label(p, spec):
    p.label = spec.id
    return p


def shaft(spec) -> Part:
    L, d, b = spec.nom("length"), spec.nom("diameter"), spec.nom("bore_diameter")
    e = spec.nom("split_pin_hole_from_end")
    s = Sh.revolved([(b / 2, -L / 2), (d / 2 - 0.5, -L / 2), (d / 2, -L / 2 + 0.5),
                     (d / 2, L / 2 - 0.5), (d / 2 - 0.5, L / 2), (b / 2, L / 2)])
    for z in (-L / 2 + e + 1.2, L / 2 - e - 1.2):          # split-pin cross holes
        s = s - Cylinder(1.2, d * 2, rotation=(90, 0, 0)).moved(Location((0, 0, z)))
    s = s - Cylinder(2.6, d, rotation=(0, 90, 0)).moved(Location((-d / 2, 0, LOCATING_X)))  # locating-screw hole, top side
    return _label(TO_X * s, spec)


def plug(spec) -> Part:
    d, L = spec.nom("diameter"), spec.nom("length")
    return _label(TO_X * Sh.chamfered_cyl(d, L, 0.4, z0=-L / 2), spec)


def bracket(spec, locating=False) -> Part:
    h, w, bl = spec.nom("height_to_shaft_centre"), spec.nom("width"), spec.nom("base_length")
    bore = spec.nom("bore")
    ys, yh = -spec.nom("short_stud_offset"), spec.nom("head_stud_offset")
    base = Box(w, bl, 9, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, (ys + yh) / 2, 0)))
    # tapered web from the base up to the shaft boss
    web = extrude(Plane.YZ.offset(-w / 2 + 2) * Polygon((-14, 8), (14, 8), (9, h - 6), (-9, h - 6), align=None),
                  w - 4)
    boss = Cylinder(15, w, rotation=(0, 90, 0)).moved(Location((0, 0, h)))
    pads = [Cylinder(8.5, 9, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, y, 0)))
            for y in (ys, yh)]
    b = base + web + boss + pads[0] + pads[1]
    b = b - Cylinder(bore / 2, w + 2, rotation=(0, 90, 0)).moved(Location((0, 0, h)))
    b = b - Cylinder(5.9, 40, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, yh, -1)))
    b = b - Cylinder(4.3, 40, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, ys, -1)))
    if locating:  # tapped hole down into the shaft for the locating screw
        b = b - Cylinder(3.2, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, h + 4)))
    return _label(b, spec)


def bracket_locating(spec):
    return bracket(spec, locating=True)


def spacing_spring(spec, length=None) -> Part:
    L = length or spec.nom("free_length")
    s = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, spec.nom("total_coils"),
                       end_turns=0.5).moved(Location((0, 0, -L / 2)))
    return _label(TO_X * s, spec)


def rocker(spec) -> Part:
    wv, wp = spec.nom("valve_arm_length"), spec.nom("pushrod_arm_length")
    hw, hd = spec.nom("hub_width"), spec.nom("hub_diameter")
    hub = Cylinder(hd / 2, hw, rotation=(0, 90, 0))
    t = 11.0  # arm thickness along X
    # side profile in YZ: valve arm sweeps down to the pad above the valve tip
    arm = extrude(Plane.YZ.offset(-t / 2) * Polygon(
        (-wv - 4, -16), (-wv + 6, -16), (-6, -9), (wp - 3, -12), (wp + 6, -12), (wp + 6, -2),
        (6, 9), (-wv + 2, -6), (-wv - 5, -10), align=None), t)
    pad = Cylinder(5.5, t, rotation=(0, 90, 0)).moved(Location((0, -wv, -12.5)))
    boss = Cylinder(7.5, 14, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, wp, -14)))
    r = hub + arm + pad + boss
    r = r - Cylinder(9.5, hw + 2, rotation=(0, 90, 0))                         # bush bore
    r = r - Cylinder(3.97, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, wp, -20)))
    return _label(r, spec)


def bush(spec) -> Part:
    L, od, id_ = spec.nom("length"), spec.nom("outside_diameter"), spec.nom("inside_diameter")
    return _label(TO_X * Sh.tube(od, id_, L, z0=-L / 2), spec)


def adjusting_screw(spec) -> Part:
    d, L, bd = spec.nom("thread_diameter"), spec.nom("length"), spec.nom("ball_diameter")
    body = Sh.chamfered_cyl(d, L - bd / 2, 0.6, z0=bd / 2, bottom=False)
    ball = Sphere(bd / 2).moved(Location((0, 0, bd / 2)))
    neck = Sh.cyl(bd * 0.62, bd / 2, z0=bd * 0.25)
    s = body + ball + neck
    s = s - Box(1.4, d + 2, 2.2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, L - 2)))
    return _label(s, spec)


def hex_nut_from(spec, size) -> Part:
    return _label(F.hex_nut(size), spec)


def locating_screw(spec) -> Part:
    d, L = spec.nom("thread_diameter"), spec.nom("length")
    af, hh = 7 / 16 * IN, 5 / 32 * IN
    head = F.hex_bolt("1/4", L / IN)  # head underside at z = 0, shank up +Z
    return _label(Rot(180, 0, 0) * head, spec)  # shank down into the bracket


def lockplate(spec) -> Part:
    L, w, t = spec.nom("length"), spec.nom("width"), spec.nom("thickness")
    p = Sh.slot_plate(L, w, t) - Sh.cyl(6.6, t * 3, z0=-t).moved(Location((-L / 2 + w / 2, 0, 0)))
    tab = Box(w * 0.5, t, 5, align=(Align.CENTER, Align.MIN, Align.MIN)).moved(Location((L / 2 - 3, w / 2 - t, 0)))
    return _label(p + tab, spec)


def flat_washer(spec) -> Part:
    return _label(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    w = Sh.washer(od, id_, t) - Box(1.2, od, t * 3).moved(Location((0, od / 2, 0)))  # the split
    return _label(w, spec)


def split_pin(spec) -> Part:
    d, L = spec.nom("diameter"), spec.nom("length")
    leg = Sh.cyl(d, L - 3, z0=0)
    pin = leg.moved(Location((d / 2, 0, 0))) + leg.moved(Location((-d / 2, 0, 0)))
    eye = Part(Torus(d * 1.5, d / 2).wrapped).moved(Location((0, 0, L - 3)), )
    return _label(TO_X * (pin + Rot(90, 0, 0) * eye), spec)


def _across_flats(p):
    return F.across_flats(p)


def _nut_thickness(p):
    return probes.bbox_size(p, "z")


NUT_PROBES = {"across_flats": _across_flats, "thickness": _nut_thickness}
WASHER_PROBES = {"outside_diameter": lambda p: probes.bbox_size(p, "x"),
                 "thickness": lambda p: probes.bbox_size(p, "z")}

PARTS = {
    "engine.head.rocker-shaft": {"build": shaft, "probes": {
        "length": lambda p: probes.bbox_size(p, "x"),
        "diameter": lambda p: probes.bbox_size(p, "y")}},
    "engine.head.rocker-shaft-plug-plain": {"build": plug},
    "engine.head.rocker-shaft-plug-screwed": {"build": plug},
    "engine.head.rocker-bracket-locating": {"build": bracket_locating},
    "engine.head.rocker-bracket": {"build": bracket},
    "engine.head.rocker-spacing-spring": {"build": spacing_spring},
    "engine.head.rocker": {"build": rocker},
    "engine.head.rocker-bush": {"build": bush, "probes": {
        "inside_diameter": lambda p: min(d for d, _ in probes.cylinder_diameters(p))}},
    "engine.head.rocker-adjusting-screw": {"build": adjusting_screw},
    "engine.head.rocker-adjuster-locknut": {"build": lambda s: hex_nut_from(s, "5/16"), "probes": NUT_PROBES},
    "engine.head.rocker-locating-screw": {"build": locating_screw},
    "engine.head.rocker-lockplate": {"build": lockplate},
    "engine.head.rocker-shaft-washer": {"build": flat_washer},
    "engine.head.rocker-shaft-spring-washer": {"build": spring_washer},
    "engine.head.rocker-shaft-split-pin": {"build": split_pin},
    "engine.head.rocker-bracket-washer": {"build": flat_washer, "probes": WASHER_PROBES},
    "engine.head.rocker-bracket-spring-washer": {"build": spring_washer},
    "engine.head.rocker-bracket-nut": {"build": lambda s: hex_nut_from(s, "7/16"), "probes": NUT_PROBES},
    "engine.head.rocker-bracket-nut-small": {"build": lambda s: hex_nut_from(s, "5/16"), "probes": NUT_PROBES},
    "engine.head.rocker-bracket-washer-small": {"build": flat_washer, "probes": WASHER_PROBES},
}
