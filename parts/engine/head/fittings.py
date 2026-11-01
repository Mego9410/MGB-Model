"""Head gasket, studs, nuts, plugs, thermostat housing and spark plugs.

Local frames: axis Z, base (mating face) at z = 0 unless stated.
"""
import math
from pathlib import Path

from build123d import (Align, Axis, Box, Cylinder, Location, Part, Plane, Polygon, RegularPolygon, Rot,
                       Solid, Vector, extrude, fillet)

from mgb import fasteners as F, probes, shapes as Sh, spec as S
from mgb.head_layout import layout

IN = 25.4
BASE = (Align.CENTER, Align.CENTER, Align.MIN)
CASTING = S.load(Path(__file__).resolve().parents[3] / "specs" / "engine" / "head" / "casting.yaml")


def _l(p, spec):
    p.label = spec.id
    return p


def _rod(a, b, r) -> Part:
    a, b = Vector(*a), Vector(*b)
    return Part(Solid.make_cylinder(r, (b - a).length, Plane(a, z_dir=b - a)).wrapped)


def stud(spec) -> Part:
    d, L = spec.nom("thread_diameter"), spec.nom("length")
    return _l(Sh.chamfered_cyl(d, L, d * 0.12), spec)


def gasket(spec) -> Part:
    lay = layout(CASTING)
    t = spec.nom("thickness")
    L, W = lay.x_max - lay.x_min - 6, lay.y_max - lay.y_min - 6
    g = Box(L, W, t, align=BASE).moved(Location(((lay.x_max + lay.x_min) / 2, (lay.y_max + lay.y_min) / 2, 0)))
    g = fillet(g.edges().filter_by(Axis.Z), 6.0)
    for x in lay.cyl_x:
        g = g - Cylinder(spec.nom("bore_hole") / 2, t * 3, align=BASE).moved(Location((x, 0, -t)))
        for dx in (-30, 30):
            g = g - Cylinder(5, t * 3, align=BASE).moved(Location((x + dx, -50, -t)))
    for _, x, y, _ in lay.head_studs:
        g = g - Cylinder(6.0, t * 3, align=BASE).moved(Location((x, y, -t)))
    for v in lay.valves:
        g = g - Cylinder(7.5, t * 3, align=BASE).moved(Location((v.x, lay.pushrod_y, -t)))
    return _l(g, spec)


def nut(size):
    return lambda spec: _l(F.hex_nut(size), spec)


def washer(spec) -> Part:
    return _l(Sh.washer(spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")), spec)


def spring_washer(spec) -> Part:
    od, id_, t = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("thickness")
    return _l(Sh.washer(od, id_, t) - Box(1.0, od, t * 3).moved(Location((0, od / 2, 0))), spec)


def core_plug(spec) -> Part:
    d, h = spec.nom("diameter"), spec.nom("depth")
    p = Sh.revolved([(0, 0), (d / 2 - 0.8, 0), (d / 2, 1.0), (d / 2, h), (d / 2 - 1.2, h), (d / 2 - 1.2, 1.4), (0, 2.2)])
    return _l(p, spec)


def screwed_plug(spec) -> Part:
    d, af = spec.nom("thread_diameter"), spec.nom("hex_across_flats")
    hexp = extrude(RegularPolygon(af / math.sqrt(3), 6), 7)
    return _l(hexp + Sh.cyl(d, 11, z0=-11), spec)


def blanking_plate(spec) -> Part:
    L, w, t = spec.nom("length"), spec.nom("width"), spec.nom("thickness")
    p = Sh.slot_plate(L, w, t)
    for x in (-L / 2 + w / 2, L / 2 - w / 2):
        p = p - Sh.cyl(6.8, t * 3, z0=-t).moved(Location((x, 0, 0)))
    return _l(p, spec)


def blanking_gasket(spec) -> Part:
    t = spec.nom("thickness")
    p = Sh.slot_plate(50, 30, t) - Sh.cyl(22, t * 3, z0=-t)
    for x in (-10, 10):
        p = p - Sh.cyl(6.8, t * 3, z0=-t).moved(Location((x, 0, 0)))
    return _l(p, spec)


def screw(spec) -> Part:
    return _l(F.hex_bolt("1/4", spec.nom("length") / IN), spec)


def spark_plug(spec) -> Part:
    """Champion N-9Y: 14 mm thread, 3/4 in reach below the gasket seat at z = 0, 13/16 in hex."""
    reach = spec.nom("reach")
    af = spec.nom("hex_across_flats")
    thread = Sh.cyl(14.0, reach, z0=-reach)
    nose = Sh.cyl(4.5, 2.0, z0=-reach - 2.0)
    seat = Sh.cyl(19.0, 3.0)
    hexp = extrude(RegularPolygon(af / math.sqrt(3), 6), 12).moved(Location((0, 0, 3)))
    insul = Sh.revolved([(0, 15), (9.5, 15), (8.0, 22), (6.2, 38), (5.6, 44), (0, 44)])
    term = Sh.cyl(5.0, 6.0, z0=44) + Sh.cyl(7.5, 3.0, z0=50)
    return _l(thread + nose + seat + hexp + insul + term, spec)


def distance_piece(spec) -> Part:
    h, od, id_ = spec.nom("height"), spec.nom("outside_diameter"), spec.nom("inside_diameter")
    p = Sh.tube(od, id_, h)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        p = p + Sh.cyl(16, h).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
        p = p - Sh.cyl(8.2, h * 3, z0=-h).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
    return _l(p, spec)


def thermostat_gasket(spec) -> Part:
    t = spec.nom("thickness")
    p = Sh.tube(68, 46, t)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        p = p + Sh.cyl(16, t).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
        p = p - Sh.cyl(8.2, t * 3, z0=-t).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
    return _l(p, spec)


def elbow(spec) -> Part:
    ft, dh = spec.nom("flange_thickness"), spec.nom("hose_spigot_diameter")
    flange = Sh.cyl(66, ft)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        flange = flange + Sh.cyl(16, ft).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
    neck = Sh.cyl(48, 22, z0=ft)
    spigot = _rod((0, 0, ft + 14), (55, 0, ft + 40), dh / 2)
    bead = _rod((47, 0, ft + 36.2), (50, 0, ft + 37.6), dh / 2 + 1.5)
    e = flange + neck + spigot + bead
    e = e - Sh.cyl(40, ft + 18, z0=-1) - _rod((0, 0, ft + 14), (60, 0, ft + 42.4), dh / 2 - 2.5)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        e = e - Sh.cyl(8.2, ft * 3, z0=-ft).moved(Location((26 * math.cos(a), 26 * math.sin(a), 0)))
    return _l(e, spec)


def thermostat(spec) -> Part:
    fd, bd, h = spec.nom("flange_diameter"), spec.nom("body_diameter"), spec.nom("height")
    flange = Sh.cyl(fd, 1.2)
    body = Sh.revolved([(0, -h + 6), (bd / 2 - 3, -h + 6), (bd / 2, -h + 10), (bd / 2, 0), (0, 0)])
    pin = Sh.cyl(6, 6, z0=-h)
    bridge = Box(fd * 0.75, 6, 1.5, align=BASE).moved(Location((0, 0, 9))) + \
        Box(2.5, 6, 9, align=BASE).moved(Location((fd * 0.36, 0, 0))) + \
        Box(2.5, 6, 9, align=BASE).moved(Location((-fd * 0.36, 0, 0)))
    valve = Sh.cyl(24, 3, z0=1.2)
    return _l(flange + body + pin + bridge + valve, spec)


NUT_PROBES = {"across_flats": F.across_flats, "thickness": lambda p: probes.bbox_size(p, "z")}
WASHER_PROBES = {"outside_diameter": lambda p: probes.bbox_size(p, "x"),
                 "thickness": lambda p: probes.bbox_size(p, "z")}

PARTS = {
    "engine.head.gasket": {"build": gasket},
    "engine.head.head-stud": {"build": stud},
    "engine.head.head-stud-long": {"build": stud},
    "engine.head.head-nut": {"build": nut("7/16"), "probes": NUT_PROBES},
    "engine.head.head-washer": {"build": washer, "probes": WASHER_PROBES},
    "engine.head.rocker-stud-short": {"build": stud},
    "engine.head.cover-stud": {"build": stud},
    "engine.head.thermostat-stud": {"build": stud},
    "engine.head.manifold-stud-end": {"build": stud},
    "engine.head.manifold-stud": {"build": stud},
    "engine.head.core-plug": {"build": core_plug},
    "engine.head.screwed-plug": {"build": screwed_plug},
    "engine.head.screwed-plug-washer": {"build": washer},
    "engine.head.blanking-plate": {"build": blanking_plate},
    "engine.head.blanking-plate-gasket": {"build": blanking_gasket},
    "engine.head.blanking-plate-screw": {"build": screw},
    "engine.head.blanking-plate-spring-washer": {"build": spring_washer},
    "engine.head.spark-plug": {"build": spark_plug},
    "engine.head.spark-plug-gasket": {"build": washer},
    "engine.head.thermostat-distance-piece": {"build": distance_piece},
    "engine.head.water-outlet-elbow": {"build": elbow},
    "engine.head.thermostat-gasket": {"build": thermostat_gasket},
    "engine.head.thermostat-washer": {"build": washer, "probes": WASHER_PROBES},
    "engine.head.thermostat-nut": {"build": nut("5/16"), "probes": NUT_PROBES},
    "engine.head.thermostat": {"build": thermostat},
}
