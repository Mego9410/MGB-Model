"""Lucas HA12 ignition coil, its clamp bracket on the block, and the coil's leads: the HT king
lead to the distributor cap and the low tension lead to the distributor (Haynes Ch 4 Sec 1-2,
Ch 10 Sec 25 para 2 (coil and bracket off before the starter), Fig 10.14 items 6 and 7).
Built in the car frame (mgb.electrical_layout COIL_*)."""
import math

from build123d import Axis, Box, Location, Part, Plane, RegularPolygon, Rot, extrude

from mgb import electrical_layout as E, elec_shapes as X, fasteners as F, shapes as Sh
from mgb.elec_shapes import box, label, polar, rev, tryfillet, xc, yc, zc

CX, CY = E.COIL_AXIS
Z0, Z1 = E.COIL_CAN


def can(spec) -> Part:
    """The HA12: a drawn steel can with a rolled bottom and a crimped rim over the moulded
    cap; the cap carries the HT tower in the middle and the two low tension terminals
    (SW and CB, '+' and '-') on its shoulder."""
    r = spec.nom("diameter") / 2
    c = Location((CX, CY, 0)) * rev([(0, Z0), (r - 5.0, Z0), (r, Z0 + 5.0), (r, Z1 - 10.0), (r + 0.8, Z1 - 8.0),
                                     (r + 0.8, Z1 - 4.0), (r - 2.0, Z1 - 2.0), (0, Z1 - 2.0)])
    for zz in (Z0 + 30.0, Z0 + 33.0, Z1 - 14.0, Z1 - 11.0):     # pressed beads round the can, clear of the clamp
        c = c + Location((CX, CY, 0)) * Sh.tube(2 * r + 1.4, 2 * r - 2, 1.2, zz)
    cap = Location((CX, CY, 0)) * rev([(0, Z1 - 4.0), (r - 2.5, Z1 - 4.0), (r - 2.5, Z1 + 2.0), (r - 9.0, Z1 + 8.0),
                                       (11.0, Z1 + 9.0), (10.0, E.COIL_TOP_Z), (0, E.COIL_TOP_Z)])
    cap = cap - Location((CX, CY, 0)) * zc(4.0, E.COIL_TOP_Z - 14.0, E.COIL_TOP_Z + 1)
    c = c + cap
    for x, y in E.COIL_TERMINALS.values():                       # LT studs with brass nuts
        c = c + zc(2.0, Z1 + 2.0, E.COIL_TERMINAL_Z + 6.0, x, y)
        c = c + Location((x, y, E.COIL_TERMINAL_Z - 4.0)) * extrude(RegularPolygon(4.2, 6), 4.0)
    return label(c, spec)


def clamp(spec) -> Part:
    """Clamp bracket: a band round the can, pinched by a screw through its two ears, on a
    pressed arm bolted to the threaded boss on the right of the block."""
    r = spec.nom("band_diameter") / 2
    w = spec.nom("band_width")
    zb = E.COIL_BOSS[1] - 6.0 - w / 2
    band = Location((CX, CY, 0)) * Sh.tube(2 * r + 3.0, 2 * r, w, zb)
    band = band - box(CX - 1.2, CX + 1.2, CY - r - 5, CY - r + 2, zb - 1, zb + w + 1)          # split on the outboard side
    for s in (-1, 1):                                                                   # pinch ears
        band = band + box(CX + s * 1.2 + (0 if s > 0 else -5.0), CX + s * 1.2 + (5.0 if s > 0 else 0), CY - r - 12.0,
                          CY - r + 0.5, zb + 2.0, zb + w - 2.0)
    band = band - xc(3.4, CX - 8.0, CX + 8.0, CY - r - 7.0, zb + w / 2)
    fy = E.BOSS_FACE_Y
    bx, bz = E.COIL_BOSS
    t = spec.nom("thickness")
    arm = box(CX - 10.0, bx + 13.0, fy - t, fy, bz - 14.0, bz + 12.0)
    arm = tryfillet(arm, arm.edges().filter_by(Axis.Y), 5.0)
    web = box(CX - 10.0, CX + 10.0, CY + r + 1.0, fy - t + 0.1, zb, zb + w)
    c = band + arm + web
    c = c - yc(4.2, fy - t - 1, fy + 1, bx, bz)
    return label(c, spec)


def pinch_screw(spec) -> Part:
    return label(F.hex_bolt("1/4", 0.75), spec)


def bracket_bolt(spec) -> Part:
    return label(F.hex_bolt("5/16", 0.75), spec)


def _king_path():
    tx, ty = CX, CY
    a = E.DIST_AXIS
    cx, cy, cz = E.CAP_CENTRE
    # up off the tower, back outboard of the plug leads, and down onto the cap's centre along its axis
    return [(tx, ty, E.COIL_TOP_Z - 12.0), (tx, ty, E.COIL_TOP_Z + 20.0), (tx - 20.0, ty - 75.0, E.COIL_TOP_Z + 25.0),
            (cx, cy - 75.0, cz + 25.0), (cx + a[0] * 30.0, cy + a[1] * 30.0 - 8.0, cz + a[2] * 30.0),
            (cx + a[0] * 3.0, cy + a[1] * 3.0, cz + a[2] * 3.0)]


def king_lead(spec) -> Part:
    """HT lead from the coil tower to the distributor cap's centre, 7 mm PVC-covered, with the
    moulded boots at each end."""
    d = spec.nom("diameter")
    p = _king_path()
    lead = X.cable(p, d, 35.0)
    lead = lead + Location((CX, CY, E.COIL_TOP_Z + 0.05)) * rev([(0, 0), (8.0, 0), (6.0, 18.0), (0, 18.0)])
    cx, cy, cz = E.CAP_CENTRE
    a = E.DIST_AXIS
    lead = lead + Plane(origin=(cx + a[0] * 10.1, cy + a[1] * 10.1, cz + a[2] * 10.1), z_dir=a).location * \
        rev([(0, 0), (8.0, 0), (6.0, 16.0), (0, 16.0)])
    return label(lead, spec)


PARTS = {
    "electrical.coil.coil": {"build": can},
    "electrical.coil.clamp": {"build": clamp},
    "electrical.coil.pinch-screw": {"build": pinch_screw},
    "electrical.coil.bracket-bolt": {"build": bracket_bolt},
    "electrical.coil.king-lead": {"build": king_lead},
}
