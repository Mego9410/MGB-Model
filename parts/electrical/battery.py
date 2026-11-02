"""Battery carriers (two, as on every early car), Oliver's single 12 V battery in the right-hand
one, its clamp and J-bolts, the battery to solenoid cable and the negative earth strap.
Haynes Ch 10 Sec 2-4, photo 2.1 (printed p163), specs printed p161.

Built in the car frame from mgb.body_layout (BATTERY_*); the carriers hang under the tonneau
floor behind the seats, which P11 builds over them.
"""
import math

from build123d import Axis, Box, Location, Part, Plane, Polygon, RegularPolygon, Rot, extrude

from mgb import body_layout as BL, elec_shapes as X, electrical_layout as E, fasteners as F, shapes as Sh
from mgb.elec_shapes import box, label, rev, tryfillet, xc, yc, zc

FZ = BL.TONNEAU_FLOOR_Z
IX, IY, ID = BL.BATTERY_BOX_INNER
BX = BL.BATTERY_BOX_X
BAT = (208.0, 173.0, 197.0)                     # length, width, height (spec: BCI group 26)
JY = IY / 2 - 7.0                               # J-bolt rods in the gaps at the battery's ends
CLAMP_DX = -25.0                                # clamp bar along the battery, between the posts and the vent row
EARTH = (BX + 40.0, -BL.BATTERY_BOX_Y + IY / 2, FZ - 20.0)   # earth bolt through the box's inboard end wall
CABLE_EXIT = (BX + IX / 2, -BL.BATTERY_BOX_Y - 82.0, FZ - 8.5)   # positive cable out through the front wall


def box_centre(side):
    return (BX, side * BL.BATTERY_BOX_Y)


def _bat_dims(spec):
    return spec.nom("length"), spec.nom("width"), spec.nom("height")


def carrier(spec) -> Part:
    """Pressed steel battery box (Moss 456-271, two per car): deep tray with rounded corners,
    a swaged bead round the sides, a drain hole in the floor, the flange round the top that
    bolts up under the tonneau floor, and the two slots the clamp J-bolts hook into. Built
    for the right-hand box; the left is its mirror (assembly)."""
    t = spec.nom("sheet_thickness")
    cx, cy = box_centre(-1)
    fl = BL.BATTERY_BOX_FLANGE
    outer = box(cx - IX / 2 - t, cx + IX / 2 + t, cy - IY / 2 - t, cy + IY / 2 + t, FZ - ID - t, FZ)
    outer = tryfillet(outer, outer.edges().filter_by(Axis.Z), 10.0 + t)
    inner = box(cx - IX / 2, cx + IX / 2, cy - IY / 2, cy + IY / 2, FZ - ID, FZ + 1)
    inner = tryfillet(inner, inner.edges().filter_by(Axis.Z), 10.0)
    c = outer - inner
    for zz in (FZ - ID * 0.45,):                                       # swaged stiffening bead
        bead = box(cx - IX / 2 - t - 1.2, cx + IX / 2 + t + 1.2, cy - IY / 2 - t - 1.2, cy + IY / 2 + t + 1.2, zz - 3.0, zz + 3.0)
        bead = tryfillet(bead, bead.edges().filter_by(Axis.Z), 11.0 + t)
        c = c + (bead - inner)
    flange = box(cx - IX / 2 - fl, cx + IX / 2 + fl, cy - IY / 2 - fl, cy + IY / 2 + fl, FZ - t, FZ)
    flange = tryfillet(flange, flange.edges().filter_by(Axis.Z), 14.0)
    c = c + (flange - inner)
    for sx in (-1, 1):                                                 # flange bolt holes
        for sy in (-1, 1):
            c = c - zc(3.3, FZ - 5, FZ + 1, cx + sx * (IX / 2 + fl / 2), cy + sy * (IY / 2 - 20.0))
    for sy in (-1, 1):                                                 # slots low in the end walls for the J-bolt hooks
        c = c - box(cx + CLAMP_DX - 5.0, cx + CLAMP_DX + 5.0, cy + sy * IY / 2 - 3.0, cy + sy * IY / 2 + 3.0, FZ - ID + 12.0, FZ - ID + 26.0)
    c = c - yc(3.4, cy + IY / 2 - 2, cy + IY / 2 + 3, EARTH[0], EARTH[2])     # earth bolt hole
    c = c - xc(8.0, cx + IX / 2 - 2, cx + IX / 2 + 3, CABLE_EXIT[1], CABLE_EXIT[2])   # cable grommet hole
    c = c - zc(6.0, FZ - ID - t - 1, FZ - ID + 1, cx, cy)              # drain hole
    return label(c, spec)


def battery(spec) -> Part:
    """12 V battery (Oliver's conversion from the two 6 V Lucas SG9E): moulded case with its
    cell divisions, ribbed walls, the lid with six vent plugs and the two taper posts, positive
    at the outboard end."""
    L, W, H = _bat_dims(spec)
    cx, cy = box_centre(-1)
    z0 = FZ - ID + 6.0
    b = box(cx - W / 2, cx + W / 2, cy - L / 2, cy + L / 2, z0, z0 + H - 8.0)
    b = tryfillet(b, b.edges().filter_by(Axis.Z), 4.0)
    lid = box(cx - W / 2 + 1.0, cx + W / 2 - 1.0, cy - L / 2 + 1.0, cy + L / 2 - 1.0, z0 + H - 8.0, z0 + H)
    lid = tryfillet(lid, lid.edges().group_by(Axis.Z)[-1], 3.0)
    b = b + lid
    for k in range(1, 6):                                              # cell partitions showing on the sides
        yy = cy - L / 2 + L * k / 6
        b = b + box(cx - W / 2 - 1.0, cx + W / 2 + 1.0, yy - 1.5, yy + 1.5, z0 + 10.0, z0 + H - 14.0)
    for k in range(6):                                                 # vent plugs in a row
        yy = cy - L / 2 + L * (k + 0.5) / 6
        b = b + zc(9.0, z0 + H, z0 + H + 6.0, cx + 10.0, yy)
        b = b - box(cx + 3.0, cx + 17.0, yy - 1.0, yy + 1.0, z0 + H + 4.5, z0 + H + 7.0)
    for s in (-1, 1):                                                  # taper posts
        py = cy + s * (L / 2 - 22.0)
        b = b + rev([(0, 0), (9.5, 0), (8.0, 18.0), (0, 18.0)]).moved(Location((cx - W / 2 + 26.0, py, z0 + H)))
    return label(b, spec)


def post_xy(side):
    """(x, y, z) of the positive (+1, outboard) or negative (-1) post top."""
    L, W, H = BAT
    cx, cy = box_centre(-1)
    return (cx - W / 2 + 26.0, cy - side * (L / 2 - 22.0), FZ - ID + 6.0 + H + 18.0)


def clamp(spec) -> Part:
    """Clamp bar (MGOC 34G2065, 12 V, negative earth) along the battery top between the two
    J-bolts at its ends, a narrow channel pressing with a hole at each end."""
    L, W, H = BAT
    cx, cy = box_centre(-1)
    z = FZ - ID + 6.0 + H
    x = cx + CLAMP_DX
    hw = spec.nom("width") / 2
    c = box(x - hw, x + hw, cy - JY - 6.0, cy + JY + 6.0, z, z + 2.0)
    c = c + box(x - hw, x - hw + 1.6, cy - JY + 8.0, cy + JY - 8.0, z + 2.0, z + 8.0)
    c = c + box(x + hw - 1.6, x + hw, cy - JY + 8.0, cy + JY - 8.0, z + 2.0, z + 8.0)
    for s in (-1, 1):
        c = c - zc(3.3, z - 1, z + 3, x, cy + s * JY)
    return label(c, spec)


def j_bolt(spec) -> Part:
    """J-bolt (MGOC BHH1586): 1/4 in rod down the gap at the battery's end, its hook through the
    slot low in the box's end wall, threaded at the top through the clamp bar with its nut and
    washer. Built at the inboard (+y) end; the assembly turns the other one round."""
    L, W, H = BAT
    cx, cy = box_centre(-1)
    z = FZ - ID + 6.0 + H
    x, yr = cx + CLAMP_DX, cy + JY
    r = 3.0
    zh = FZ - ID + 19.0
    rod = zc(r, zh, z + 12.0, x, yr)
    hook = X.cable([(x, yr, zh + 0.5), (x, yr, zh - 4.0), (x, yr + 6.5, zh - 4.0), (x, yr + 6.5, zh + 2.0)], 2 * r, 2.5)
    nut = Location((x, yr, z + 3.6)) * extrude(RegularPolygon(F.NUT["1/4"][0] * 25.4 / math.sqrt(3), 6), 5.5)
    wsh = Location((x, yr, z + 2.0)) * Sh.washer(13.5, 7.0, 1.6)
    return label(rod + hook + nut + wsh, spec)


def _cable_path():
    px, py, pz = post_xy(1)
    gx, gy, gz = BL.CABLE_GROMMET
    tx, ty, tz = E.sol_terminal(1)
    cx, cy = box_centre(-1)
    wall_x = cx + IX / 2
    under = FZ - 24.0
    ex, ey, ez = CABLE_EXIT
    # off the helmet terminal sideways over the battery top, out through the box's front wall
    # under the floor, forward beside the tunnel, up through the toe board and the inner wing
    return [(px + 12.0, py, pz - 3.0), (px + 40.0, py, ez), (ex - 30.0, ey, ez), (ex + 40.0, ey, ez), (ex + 160.0, ey + 20.0, -300.0),
            (ex + 400.0, -330.0, -395.0), (gx - 120.0, gy, -395.0), (gx, gy, gz), (gx + 120.0, gy - 40.0, -200.0),
            (tx + 60.0, ty + 45.0, -150.0), (tx + 60.0, ty + 45.0, tz - 9.75), (tx + 34.0, ty + 6.0, tz - 9.75), (tx + 16.0, ty, tz - 9.75)]


def _helmet(px, py, pz):
    """Screw-on 'helmet' terminal over the taper post (MGOC: screw-fixing until February 1976)."""
    return rev([(9.9, -14.0), (14.0, -14.0), (14.0, 0.0), (9.0, 4.0), (0, 4.0), (0, 1.0), (8.5, 1.0), (9.9, -14.0)]).moved(Location((px, py, pz - 1.0)))


def positive_cable(spec) -> Part:
    """Battery to solenoid cable (MGOC AHH5449): from the positive post's screw terminal out of
    the box, forward under the floor beside the tunnel, up through the toe board into the
    engine bay and onto the solenoid's battery stud (route derived)."""
    d = spec.nom("diameter")
    c = X.cable(_cable_path(), d, 70.0)
    px, py, pz = post_xy(1)
    c = c + _helmet(px, py, pz)
    tx, ty, tz = E.sol_terminal(1)
    c = c + Location((tx, ty, tz - 10.5)) * (X.zc(7.5, 0.0, 1.5) + X.box(0.0, 17.0, -4.5, 4.5, 0.0, 1.5) - X.zc(4.1, -1, 3))
    return label(c, spec)


def earth_cable(spec) -> Part:
    """Negative earth lead (MGOC 5L924, negative earth cars): from the negative post's helmet
    terminal over the battery top to a bolt through the box's inboard end wall into the body."""
    d = spec.nom("diameter")
    px, py, pz = post_xy(-1)
    ex, ey, ez = EARTH
    pts = [(px + 12.0, py, pz - 3.0), (px + 40.0, py + 4.0, FZ - 8.5), (ex - 10.0, py + 10.0, FZ - 8.5), (ex - 10.0, ey - 7.0, FZ - 8.5),
           (ex - 10.0, ey - 7.0, ez + 2.0), (ex - 10.0, ey - 2.4, ez)]
    c = X.cable(pts, d, 10.0)
    c = c + _helmet(px, py, pz)
    c = c + Location((ex, ey - 1.6, ez)) * Rot(-90, 0, 0) * (zc(8.0, 0.0, 1.5) + box(-12.0, 0.0, -4.0, 4.0, 0.0, 1.5) - zc(3.4, -1, 3))
    return label(c, spec)


def floor_bolt(spec) -> Part:
    return label(F.hex_bolt("1/4", 0.5), spec)


PARTS = {
    "electrical.battery.carrier": {"build": carrier},
    "electrical.battery.battery": {"build": battery,
                                   "probes": {"length": lambda p: p.bounding_box().size.Y,
                                              "width": lambda p: p.bounding_box().size.X - 2.0}},
    "electrical.battery.clamp": {"build": clamp},
    "electrical.battery.j-bolt": {"build": j_bolt},
    "electrical.battery.positive-cable": {"build": positive_cable},
    "electrical.battery.earth-cable": {"build": earth_cable},
    "electrical.battery.floor-bolt": {"build": floor_bolt},
}
