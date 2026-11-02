"""Flywheel, ring gear, spigot bush and fixings for the three-main-bearing 18G.
Haynes Sec 22, 42, 53; photos 22.4, 53.4. Outside sizes from MGB owners' sources
(see the specs). Built about the X axis: front face (toward the engine) at x = 0,
the clutch face toward -X.
"""
import math

from build123d import Box, Cylinder, Location, Part, Plane, Polygon, Rot, extrude

from mgb import fasteners as F, shapes as Sh

BOLT_R = 37.0          # matches the crankshaft flange (parts/engine/block/crank.py)


def _l(p, spec):
    p.label = spec.id
    return p


def _xdisc(r, x0, x1, y=0.0, z=0.0):
    return Cylinder(r, abs(x1 - x0), rotation=(0, 90, 0)).moved(Location(((x0 + x1) / 2, y, z)))


def _xrev(prof):
    """Revolve an (r, x) profile about the X axis, x measured rearward as negative."""
    return Rot(0, -90, 0) * Sh.revolved([(r, -x) for r, x in prof])


def flywheel(spec) -> Part:
    """Cast iron flywheel: register on the crankshaft flange, dished web, heavy rim with
    the ring gear seat on its front edge, flat clutch face, dowels and clutch bolt holes."""
    seat_r = spec.nom("ring_seat_diameter") / 2
    t_rim, t_hub = spec.nom("rim_thickness"), spec.nom("hub_thickness")
    prof = [(11.0, 0), (49.0, 0), (49.0, -4), (78.0, -10), (seat_r - 14, -10), (seat_r - 14, 0),
            (seat_r, 0), (seat_r, -t_rim), (60.0, -t_rim), (52.0, -t_hub), (11.0, -t_hub)]
    f = _xrev(prof)
    f = f - _xdisc(47.6, 1, -4.5)                                   # register over the crank flange
    for k in range(6):                                              # crankshaft bolts
        a = math.radians(30 + 60 * k)
        f = f - _xdisc(4.6, 2, -t_hub - 2, BOLT_R * math.cos(a), BOLT_R * math.sin(a))
    cb = spec.nom("clutch_bolt_circle") / 2
    for k in range(6):                                              # clutch cover bolts
        a = math.radians(60 * k)
        f = f - _xdisc(4.0, -t_rim + 14, -t_rim - 1, cb * math.cos(a), cb * math.sin(a))   # 5/16 in tapped, at the major diameter
    for k in range(3):                                              # MGB clutch dowels (mgaguru: three)
        a = math.radians(30 + 120 * k)
        f = f + _xdisc(3.2, -t_rim, -t_rim - 6, cb * math.cos(a), cb * math.sin(a))
    f = f - Box(1.2, 3, 24).moved(Location((-t_rim, 0, seat_r - 16)))  # 1/4 timing mark line
    return _l(f, spec)


def ring_gear(spec) -> Part:
    """120-tooth starter ring, shrunk on with the tooth chamfers facing the engine
    (Haynes Sec 42 para 5)."""
    n = int(spec.nom("teeth"))
    od, w = spec.nom("outside_diameter"), spec.nom("width")
    r_in = spec.nom("inside_diameter") / 2
    root = od / 2 - 5.7
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        da = 2 * math.pi / n
        for f, r in ((0.0, root), (0.18, root), (0.36, od / 2), (0.64, od / 2), (0.82, root)):
            pts.append((r * math.cos(a + da * f), r * math.sin(a + da * f)))
    teeth = extrude(Plane.YZ * Polygon(*pts, align=None), w, dir=(-1, 0, 0))
    ring = teeth - _xdisc(r_in, 1, -w - 1)
    # chamfer on the front of the teeth for the starter pinion
    cone = _xrev([(od / 2 + 1, 0.5), (od / 2 + 1, -3.0), (od / 2 - 3.5, 0.5)])
    return _l(ring - cone, spec)


def spigot_bush(spec) -> Part:
    od, id_, L = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    return _l(Rot(0, 90, 0) * Sh.tube(od, id_, L), spec)


def lock_plate(spec) -> Part:
    """Ring of tab washers under the six bolts (photo 22.4: 'lockring')."""
    t = spec.nom("thickness")
    r_o, r_i = BOLT_R + 9, BOLT_R - 9
    p = _xdisc(r_o, 0, -t) - _xdisc(r_i, 1, -t - 1)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        y, z = BOLT_R * math.cos(a), BOLT_R * math.sin(a)
        p = p - _xdisc(4.6, 1, -t - 1, y, z)
        tab_a = a + math.radians(15)
        p = p + (Location((-t - 3, (BOLT_R + 2) * math.cos(tab_a), (BOLT_R + 2) * math.sin(tab_a)))
                 * Rot(math.degrees(tab_a), 0, 0) * Box(6, 1.0, 7))
    return _l(p, spec)


def bolt(size):
    return lambda spec: _l(F.hex_bolt(size, spec.nom("length") / 25.4), spec)


PARTS = {
    "engine.flywheel.flywheel": {"build": flywheel},
    "engine.flywheel.ring-gear": {"build": ring_gear},
    "engine.flywheel.spigot-bush": {"build": spigot_bush},
    "engine.flywheel.lock-plate": {"build": lock_plate},
    "engine.flywheel.bolt": {"build": bolt("3/8")},
}
