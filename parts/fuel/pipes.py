"""Engine-bay fuel and breather pipework, 18G twin SU HS4 installation.
Haynes Ch 3 Sec 3 para 1 (rocker cover breather pipe to the front air cleaner) and
Sec 18 para 1 (fuel pipe hoses to the float chambers).

Everything is built in the engine frame from the spigot positions in mgb.carb_layout and
the rocker cover, so the hoses land on the spigots wherever those move. The fuel feed
hoses meet at a brass tee below the carburettors; the feed from the pump continues from
the union on the tee's tail when the body and fuel tank are modelled.
"""
from build123d import Circle, Cylinder, FilletPolyline, Location, Part, Plane, Vector, sweep

from mgb import carb_layout as K, shapes as Sh

CHAMBER_H = 72.0                                   # float chamber height (specs/fuel/carburettors.yaml)
FUEL_Y, FUEL_Z = 204.0, -52.0                      # run under the carburettors, clear of the jets and return springs
TEE = (0.0, FUEL_Y, FUEL_Z)
FEED_END = (-70.0, FUEL_Y, FUEL_Z - 30.0)
# rocker cover breather spigot end (engine frame): cover centre (-2.5, 35), base z 80 (assemblies/engine_head.py)
COVER_SPIGOT = (-2.5 + 160.0, 35.0 + 61.0 + 20.0, 80.0 + 55.0)


def _l(p, spec):
    p.label = spec.id
    return p


def _hose(points, r, bore, radius):
    path = None
    for rr in (radius, radius * 0.5, radius * 0.25):
        try:
            path = FilletPolyline(*points, radius=rr)
            break
        except ValueError:
            continue
    pl = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0))
    try:
        h = sweep(pl * (Circle(r) - Circle(bore)), path=path)
        if h.is_valid:
            return h
    except Exception:  # noqa: BLE001
        pass
    return sweep(pl * Circle(r), path=path)


def float_hose_points(x):
    sx, sy, sz = K.float_inlet(x, CHAMBER_H)
    s = K.side(x)
    return [(sx, sy + 8.0, sz), (sx, FUEL_Y, sz), (sx, FUEL_Y, FUEL_Z), (TEE[0] + s * 12.0, FUEL_Y, FUEL_Z)]


def breather_points():
    cx, cy, cz = COVER_SPIGOT
    tx, ty, tz = K.breather_spigot_top()
    return [(cx, cy - 12.0, cz), (cx, cy + 14.0, cz), (150.0, 240.0, 165.0), (tx + 18.0, ty, tz + 22.0),
            (tx, ty, tz + 22.0), (tx, ty, tz - 12.0)]


def feed_points():
    return [(TEE[0], FUEL_Y, FUEL_Z - 10.0), (TEE[0], FUEL_Y, FUEL_Z - 30.0), FEED_END]


def float_hose(x):
    def build(spec) -> Part:
        """Fuel hose from the float chamber lid inlet down under the instruments to the tee."""
        return _l(_hose(float_hose_points(x), spec.nom("outside_diameter") / 2, spec.nom("bore") / 2, 14.0), spec)
    return build


def feed_hose(spec) -> Part:
    """Feed hose from the tee's tail toward the pump line at the bulkhead."""
    return _l(_hose(feed_points(), spec.nom("outside_diameter") / 2, spec.nom("bore") / 2, 14.0), spec)


def breather_hose(spec) -> Part:
    """Rubber breather hose from the rocker cover spigot over the front instrument to the
    spigot on top of the front air cleaner."""
    return _l(_hose(breather_points(), spec.nom("outside_diameter") / 2, spec.nom("bore") / 2, 26.0), spec)


def tee(spec) -> Part:
    """Brass tee: two spigots along X for the float chamber hoses, the tail down to the feed."""
    L = spec.nom("length")
    t = Cylinder(5.5, L, rotation=(0, 90, 0)) + Cylinder(7.0, 10)
    t = t + Location((0, 0, -10)) * Cylinder(4.0, 20)
    for s in (-1, 1):
        t = t + Location((s * (L / 2 - 3), 0, 0)) * Cylinder(6.2, 2.0, rotation=(0, 90, 0))   # hose beads
    t = t + Location((0, 0, -18)) * Cylinder(5.0, 2.0)
    return _l(t.moved(Location(TEE)), spec)


def hose_clip(spec) -> Part:
    """Worm-drive hose clip, axis along Z, centred on the origin."""
    d, w = spec.nom("diameter"), spec.nom("width")
    c = Sh.tube(d + 1.6, d, w).moved(Location((0, 0, -w / 2)))
    housing = Location((d / 2 + 3.0, 0, 0)) * Cylinder(3.0, w + 2, rotation=(90, 0, 0))
    screw = Location((d / 2 + 3.0, 0, 0)) * Cylinder(2.0, w + 8, rotation=(90, 0, 0))
    return _l(c + housing + screw, spec)


def clip_locations(points, inset):
    """Location of a clip `inset` mm in from the first point, axis along the first leg."""
    a, b = Vector(points[0]), Vector(points[1])
    d = (b - a).normalized()
    p = a + d * inset
    return Location(Plane(origin=p, z_dir=d))


def union_nut(spec) -> Part:
    """Union nut on the end of the feed hose, axis along Z."""
    return _l(Sh.revolved([(3.0, 0), (7.0, 0), (7.0, 12), (5.0, 14), (3.0, 14)]), spec)


PARTS = {
    "fuel.pipes.float-hose-front": {"build": float_hose(K.CARB_X[0])},
    "fuel.pipes.float-hose-rear": {"build": float_hose(K.CARB_X[1])},
    "fuel.pipes.tee": {"build": tee},
    "fuel.pipes.feed-hose": {"build": feed_hose},
    "fuel.pipes.feed-union": {"build": union_nut},
    "fuel.pipes.fuel-clip": {"build": hose_clip},
    "fuel.pipes.breather-hose": {"build": breather_hose},
    "fuel.pipes.breather-clip": {"build": hose_clip},
}
