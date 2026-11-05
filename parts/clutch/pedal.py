"""Clutch pedal, early cars: pedal, bush, rubber pad, distance tube, return spring and clevis
pin. Haynes Ch 5 Sec 8 (removal as for the brake pedal, Ch 9) and Fig 5.3 items 1-6 (p109).

Built in the engine frame at the places in mgb.clutch_layout: the pedal swings fore and aft
about a pivot along Y in the pedal box, the master cylinder pushrod's clevis below the pivot,
the arm passing back through the bulkhead to the pad in the footwell. The pedal box itself,
its cover and the common pivot bolt belong to the body (P11).

Form from Fig 5.3 item 1: a flat pressed-steel arm with the pivot boss at the top, the
clevis hole just below it, a crank where the arm turns back toward the driver, and a foot
plate at the bottom carrying the ribbed rubber pad (item 3).
"""
import math

from build123d import Align, Box, Cylinder, FilletPolyline, Location, Part, Plane, Polygon, Rectangle, Rot, \
    Torus, extrude, sweep

from mgb import clutch_layout as K, shapes as Sh

PX, PY, PZ = K.PEDAL_PIVOT
CX, _, CZ = K.PEDAL_CLEVIS
AX, _, AZ = K.PEDAL_PAD
T = 8.0                                   # pedal arm thickness (along Y)
PAD_N = (-math.cos(math.radians(25)), 0.0, math.sin(math.radians(25)))   # foot plate faces back and a little up
SPRING_PEDAL = (PX, PZ - 70.0)            # return spring hole in the arm (x, z)
SPRING_ANCHOR = (PX - 26.0, PZ - 58.0)    # its anchor tab on the pedal box (P8: parts/brakes/master.py anchor bar) (D)


def _l(p, spec):
    p.label = spec.id
    return p


def ycyl(r, y0, y1, x, z):
    return Location((x, (y0 + y1) / 2, z)) * Cylinder(r, abs(y1 - y0), rotation=(90, 0, 0))


def _arm_points():
    end = (AX - PAD_N[0] * 16.5, AZ - PAD_N[2] * 16.5)               # behind the foot plate
    up = (-PAD_N[2], PAD_N[0])                                       # up the plate, in the XZ plane
    up = (abs(up[0]), abs(up[1]))
    prev = (end[0] + 45.0 * up[0], end[1] + 45.0 * up[1])
    return [(PX, PZ), (PX, PZ - 85.0), (PX - 70.0, PZ - 160.0), prev, end]


def pedal(spec) -> Part:
    pts = _arm_points()
    path = None
    for rr in (30.0, 15.0, 6.0):
        try:
            path = FilletPolyline(*[(x, PY, z) for x, z in pts], radius=rr)
            break
        except ValueError:
            continue
    prof = Plane(origin=path.position_at(0), z_dir=path.tangent_at(0), x_dir=(0, 1, 0)) * Rectangle(T, 24.0)
    p = sweep(prof, path=path)
    p = p + ycyl(16.0, PY - T / 2, PY + T / 2, PX, PZ)               # pivot eye
    p = p + ycyl(13.0, PY - 12.5, PY + 12.5, PX, PZ)                 # boss for the bush
    p = p + ycyl(10.0, PY - T / 2, PY + T / 2, CX, CZ)               # clevis eye
    # foot plate the pad fits over
    pl = Plane(origin=(AX, PY, AZ), x_dir=(0, 1, 0), z_dir=PAD_N)
    p = p + pl.location * Box(50.0, 62.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
    p = p + pl.location * Box(20.0, 50.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, -2.9)))   # boss joining the arm
    p = p - ycyl(spec.nom("bush_bore") / 2, PY - 20, PY + 20, PX, PZ)
    p = p - ycyl(4.1, PY - 10, PY + 10, CX, CZ)
    p = p - ycyl(2.2, PY - 10, PY + 10, *SPRING_PEDAL)
    return _l(p, spec)


def bush(spec) -> Part:
    od, id_ = spec.nom("outside_diameter"), spec.nom("inside_diameter")
    return _l(ycyl(od / 2, PY - 12.5, PY + 12.5, PX, PZ) - ycyl(id_ / 2, PY - 13, PY + 13, PX, PZ), spec)


def distance_tube(spec) -> Part:
    od, id_, L = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    return _l(ycyl(od / 2, PY - L / 2, PY + L / 2, PX, PZ) - ycyl(id_ / 2, PY - L, PY + L, PX, PZ), spec)


def pad(spec) -> Part:
    """Item 3: rubber pad over the foot plate, tapered (narrower at the top) and ribbed up its face (Oliver's kf151:
    vertical ribs, a rounded foot)."""
    from build123d import Polygon, extrude
    t = spec.nom("thickness")
    pl = Plane(origin=(AX, PY, AZ), x_dir=(0, 1, 0), z_dir=PAD_N)
    wb, wt, h = 62.0, 50.0, 72.0
    outline = [(-wb / 2, -h / 2), (wb / 2, -h / 2), (wt / 2, h / 2), (-wt / 2, h / 2)]
    from mgb.body_shell import fillet_poly
    outline = fillet_poly(outline, [16.0, 16.0, 6.0, 6.0], 6)
    body = extrude(Polygon(*outline, align=None), t + 3.5, dir=(0, 0, 1)).moved(Location((0, 0, -3.5)))
    body = body - Box(51.0, 63.0, 3.6, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -3.6)))
    for k in range(-4, 5):                                            # ribs up the tread
        body = body - Location((k * 5.4, 0.0, t)) * Box(2.2, h - 12.0, 2.4)
    return _l(pl.location * body, spec)


def return_spring(spec) -> Part:
    """Item 5: return spring hooked from the arm to the pedal box."""
    (x0, z0), (x1, z1) = SPRING_PEDAL, SPRING_ANCHOR
    L = math.hypot(x1 - x0, z1 - z0)
    wire, od = spec.nom("wire_diameter"), spec.nom("outside_diameter")
    body_L = L - 2 * od
    coil = Sh.coil_spring(wire, od, body_L, body_L / wire * 0.95, end_turns=0.5).moved(Location((0, 0, od)))
    r = od / 2 - wire / 2
    hooks = Location((r, 0, od / 2 + 0.3)) * Rot(90, 0, 0) * Torus(od / 2 - 0.3, wire / 2)
    hooks = hooks + Location((r, 0, L - od / 2 - 0.3)) * Rot(90, 0, 0) * Torus(od / 2 - 0.3, wire / 2)
    s = coil + hooks
    a = math.degrees(math.atan2(x1 - x0, z1 - z0))
    return _l(Location((x0, PY + T / 2 + od / 2, z0)) * Rot(0, a, 0) * Location((-r, 0, 0)) * s, spec)


def clevis_pin(spec) -> Part:
    """Item 6: clevis pin joining the pushrod fork to the pedal, with its split pin hole."""
    L = spec.nom("length")
    p = Sh.revolved([(0, -L / 2), (3.95, -L / 2), (3.95, L / 2), (6.5, L / 2), (6.5, L / 2 + 2.5), (0, L / 2 + 2.5)])
    p = p - Location((0, 0, -L / 2 + 2.5)) * Cylinder(0.9, 12, rotation=(90, 0, 0))
    return _l(Location((CX, PY, CZ)) * Rot(90, 0, 0) * p, spec)


PARTS = {
    "clutch.pedal.pedal": {"build": pedal},
    "clutch.pedal.bush": {"build": bush},
    "clutch.pedal.distance-tube": {"build": distance_tube},
    "clutch.pedal.pad": {"build": pad},
    "clutch.pedal.return-spring": {"build": return_spring},
    "clutch.pedal.clevis-pin": {"build": clevis_pin},
}
