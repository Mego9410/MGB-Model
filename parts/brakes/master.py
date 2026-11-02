"""Brake master cylinder (single, square supply tank) and the pedal box with its protecting cover (Haynes Ch 9
Fig 9.11 items 1-17, Secs 17-18, printed p154-155; photo 1.1, p147; the box after Fig 9.16 items 11-13, p159 and
Sec 19 paras 6-7).

The master cylinder is built in its own frame like the clutch one (parts.clutch.hydraulics: local z forward from
the mounting face, local x up, local y to the car's right) and placed by the assembly at
brake_layout (MC_Y, MC_Z) on the pedal box's mounting wall (clutch_layout.PEDAL_BOX_FACE_X). The pedal box,
cover and fixings are built in the car frame.

Forms:
- cylinder and tank (1): a cast cylinder with the two-bolt flange (longer bolt in the top hole, Sec 17 para 5)
  and a short neck, the square pressed-steel tank (Lockheed GMC150 square tank: v8register.net) brazed over the
  forward part of the cylinder with rounded vertical edges, a joint bead, the filler neck on top, and the outlet
  boss standing out of the tank's front face for the banjo connector (14), its bolt (15) and gaskets (16, 17).
- the bore internals as Fig 9.11: valve assembly (4), tapered return spring (5), spring retainer (6), main cup (7),
  piston washer (8), piston (9) with the secondary cup (10), pushrod (11) with its clevis fork and locknut,
  circlip (12) and boot (13). The bore is 3/4 in like the clutch cylinder (Moss Motors 180-757), so the piston,
  cups, washer, retainer, circlip, boot and pushrod are the clutch cylinder's forms (parts.clutch.hydraulics).
- pedal box: rear section open underneath for the pedals with the pivot bolt holes in its side walls, the
  mounting wall with the cylinder spigot and bolt holes (and a hole for the clutch pipe), front section with a
  floor (brake pipe grommet hole) and front wall, a rim round the opening, a flange round the rear edge on the
  bulkhead with six bolt holes, and the pull-off spring anchor bar with its two tabs.
- protecting cover: a pressed hood with rounded top edges and a flange on the rim, four screws and washers.
"""
from __future__ import annotations

import math

from build123d import Align, Axis, Box, Location, Part, Plane, Rot, fillet, offset

from mgb import brake_layout as B, car_layout as CL, clutch_layout as K, fasteners as F, shapes as Sh
from mgb.brake_parts import (bore, IN, box, chamfered_hex, lab, plain_washer, ring, spring_washer, xcyl, xprism, ycyl, zc,
                             zprism)
from mgb.poly2d import rounded
from parts.clutch import hydraulics as CH

# ---- master cylinder frame (local z forward from the mounting face, x up, y to the car's right) -------------
FLANGE_T = 7.0
BOLT_X = 27.0                    # flange bolts above and below the axis
SPIGOT = 12.0                    # rear spigot into the pedal box
SPIGOT_R = 14.0
CYL_R = 15.0
TANK_Z = (30.0, 102.0)           # tank along the cylinder
TANK_Y = 31.0                    # half width
TANK_X = (-17.5, 88.0)           # bottom (under the cylinder) to top
TANK_T = 1.6
TANK_CORNER = 7.0
NECK = (66.0, 15.5, 7.0)         # filler neck: z, radius, height
BOSS_Z = (TANK_Z[1] - 1.0, 114.0)
BANJO_SEAT = BOSS_Z[1]
GASKET_T = 1.6
BANJO_T = 11.0
STUB = (-1.0, 0.0)               # banjo pipe stub: straight down (local -x)
BORE_END = 98.0


def frame():
    return Plane(origin=(K.PEDAL_BOX_FACE_X, B.MC_Y, B.MC_Z), x_dir=(0, 0, 1), z_dir=(1, 0, 0)).location


def point(x, y, z):
    return tuple((frame() * Location((x, y, z))).position)


def lzc(r, z0, z1, x=0.0, y=0.0):
    return zc(r, z0, z1, x, y)


def lxc(r, x0, x1, y=0.0, z=0.0):
    """Cylinder along local x (up)."""
    return xcyl(r, x0, x1, y, z)


# =================================================================================================
# cylinder and tank (1)
# =================================================================================================
def mc_body(spec) -> Part:
    bore = spec.nom("bore") / 2
    b = lzc(SPIGOT_R, -SPIGOT, 0.01) + lzc(CYL_R, 0.0, TANK_Z[0] + 2.0)
    # two-bolt flange
    fl = zprism([(-BOLT_X - 9, -9), (-BOLT_X - 9, 9), (-12, 19), (12, 19), (BOLT_X + 9, 9), (BOLT_X + 9, -9), (12, -19),
                 (-12, -19)], 0.0, FLANGE_T)
    for s in (-1, 1):
        fl = fl + lzc(9.0, 0.0, FLANGE_T, s * BOLT_X)
    b = b + fl
    # square tank with rounded vertical edges, a joint bead round it, a raised boss under the neck
    foot = rounded([(-TANK_Y, TANK_Z[0]), (TANK_Y, TANK_Z[0]), (TANK_Y, TANK_Z[1]), (-TANK_Y, TANK_Z[1])], TANK_CORNER, 4)
    tank = xprism(foot, TANK_X[0], TANK_X[1])
    tank = fillet(tank.edges().group_by(Axis.X)[-1], 4.0)
    inner = rounded([(-TANK_Y + TANK_T, TANK_Z[0] + TANK_T), (TANK_Y - TANK_T, TANK_Z[0] + TANK_T),
                     (TANK_Y - TANK_T, TANK_Z[1] - TANK_T), (-TANK_Y + TANK_T, TANK_Z[1] - TANK_T)], TANK_CORNER - TANK_T, 4)
    bead_o = rounded([(-TANK_Y - 0.9, TANK_Z[0] - 0.9), (TANK_Y + 0.9, TANK_Z[0] - 0.9), (TANK_Y + 0.9, TANK_Z[1] + 0.9),
                      (-TANK_Y - 0.9, TANK_Z[1] + 0.9)], TANK_CORNER + 0.9, 4)
    tank = tank + (xprism(bead_o, 38.0, 41.0) - xprism(inner, 37.0, 42.0))
    tank = tank - xprism(inner, TANK_X[0] + TANK_T, TANK_X[1] - TANK_T)
    b = b + tank + lzc(CYL_R, TANK_Z[0] - 0.01, TANK_Z[1] - 1.0)          # the cylinder runs through the tank bottom
    nz, nr, nh = NECK
    b = b + lxc(nr + 5.0, TANK_X[1] - 0.5, TANK_X[1] + 1.2, 0.0, nz)
    b = b + lxc(nr, TANK_X[1] + 1.0, TANK_X[1] + nh, 0.0, nz)
    for k in range(4):                                                    # thread on the neck
        b = b + Location((TANK_X[1] + 2.2 + 1.4 * k, 0, nz)) * Rot(0, 90, 0) * Sh.revolved([(nr - 0.1, 0), (nr + 0.6, 0.35), (nr - 0.1, 0.7)])
    b = b - lxc(nr - 2.5, TANK_X[1] - 3.0, TANK_X[1] + nh + 1.0, 0.0, nz)
    # outlet boss through the tank's front face, banjo seat
    b = b + lzc(11.0, BOSS_Z[0], BOSS_Z[1]) + Sh.revolved([(0, BOSS_Z[0] - 1), (12.5, BOSS_Z[0] - 1), (11.0, BOSS_Z[0] + 1.5), (0, BOSS_Z[0] + 1.5)])
    # keel rib under the cylinder neck
    b = b + box(-CYL_R - 2.5, -CYL_R + 1.0, -3.0, 3.0, FLANGE_T - 0.01, TANK_Z[0] + 0.01)
    # bore, mouth recess for the circlip, outlet, feed and by-pass ports from the tank
    b = b - lzc(bore, -SPIGOT - 1.0, BORE_END)
    b = b - lzc(12.0, -SPIGOT - 1.0, -SPIGOT + 3.5)
    b = b - lzc(1.4, BORE_END - 1.0, BANJO_SEAT + 1.0) - lzc(4.9, BOSS_Z[1] - 10.0, BANJO_SEAT + 1.0)
    b = b - lxc(1.6, bore - 1.0, CYL_R + 1.0, 0.0, 44.0) - lxc(0.6, bore - 1.0, CYL_R + 1.0, 0.0, 52.0)
    for s in (-1, 1):
        b = b - lzc(4.2, -1.0, FLANGE_T + 1.0, s * BOLT_X)
    return lab(b, spec)


def mc_cap(spec) -> Part:
    """Item 2: fluted filler cap with the breather hole (Sec 2 para 2: keep it clear)."""
    nz, nr, nh = NECK
    z0 = TANK_X[1] + nh + 1.5
    c = Sh.revolved([(0, 0), (nr + 3.5, 0), (nr + 3.5, 5.0), (nr + 2.0, 7.0), (6.0, 8.5), (0, 8.5)]) + ring(nr + 0.9, nr + 3.5, -nh + 0.6, 0.1)
    for k in range(20):
        c = c - (Location((0, 0, -3.0)) * Rot(0, 0, 18 * k) * Location((nr + 4.1, 0, 0)) * Box(2.0, 2.4, 16.0))
    c = c - zc(0.8, -1, 10, 7.0, 0)
    return lab(Location((z0, 0, nz)) * Rot(0, 90, 0) * c, spec)


def mc_cap_seal(spec) -> Part:
    """Item 3: rubber seal under the cap."""
    nz, nr, nh = NECK
    t = spec.nom("thickness")
    return lab(Location((TANK_X[1] + nh, 0, nz)) * Rot(0, 90, 0) * Sh.washer(2 * nr + 3.0, 2 * nr - 5.0, t), spec)


def valve(spec) -> Part:
    """Item 4: valve assembly at the outlet end of the bore: a rubber seal on a stem in a spring-loaded cage
    (trap valve keeping a light pressure in the lines)."""
    b = spec.nom("diameter") / 2
    z1 = BORE_END
    v = Sh.revolved([(0, z1 - 0.01), (b - 0.6, z1 - 0.01), (b - 0.6, z1 - 3.5), (b - 2.8, z1 - 4.5), (b - 2.8, z1 - 9.5),
                     (4.0, z1 - 9.5), (4.0, z1 - 12.0), (0, z1 - 12.0)])
    for k in range(4):
        v = v - (Location((0, 0, z1 - 7.0)) * Rot(0, 0, 90 * k) * Location((b - 2.0, 0, 0)) * Box(3.0, 2.4, 4.4))
    return lab(v, spec)


def mc_spring(spec) -> Part:
    """Item 5: tapered return spring, the valve in its large end, the retainer in the small (Sec 18 para 4)."""
    z0, z1 = 35.0, BORE_END - 11.5
    return lab(Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), z1 - z0, 8).moved(Location((0, 0, z0))), spec)


def banjo(spec) -> Part:
    """Item 14: banjo connector on the outlet boss, the pipe stub brazed in pointing down."""
    z0 = BANJO_SEAT + GASKET_T
    e = zc(9.5, z0, z0 + BANJO_T) - zc(5.0, z0 - 1, z0 + BANJO_T + 1)
    e = e - ring(5.0, 6.3, z0 + 3.0, z0 + BANJO_T - 3.0)
    e = e + CH.radial(STUB[0], STUB[1], 8.0, 9.0 + 14.0, z0 + BANJO_T / 2, 3.2)
    e = e - CH.radial(STUB[0], STUB[1], 5.5, 9.0 + 14.5, z0 + BANJO_T / 2, 1.2)
    return lab(e, spec)


def banjo_bolt(spec) -> Part:
    """Item 15: hollow banjo bolt with its cross-drilling."""
    L = spec.nom("length")
    z_head = BANJO_SEAT + 2 * GASKET_T + BANJO_T
    b = Location((0, 0, z_head)) * Rot(180, 0, 0) * F.hex_bolt("3/8", L / IN)
    b = b - zc(1.8, z_head - L - 1, z_head - 3)
    b = b - Location((0, 0, BANJO_SEAT + GASKET_T + BANJO_T / 2)) * Rot(90, 0, 0) * zc(1.6, -8, 8)
    return lab(b, spec)


def gasket(which):
    def build(spec):
        z0 = BANJO_SEAT if which == "inner" else BANJO_SEAT + GASKET_T + BANJO_T
        return lab(ring(5.0, 8.5, z0, z0 + spec.nom("thickness")), spec)
    return build


def stub_end():
    """Car-frame end of the banjo's pipe stub (the pipe's start) and the pipe's direction there."""
    z = BANJO_SEAT + GASKET_T + BANJO_T / 2
    return point(STUB[0] * 23.0, STUB[1] * 23.0, z)


# =================================================================================================
# pedal box (car frame)
# =================================================================================================
X0, XW, XF = B.BOX_REAR_X, B.BOX_WALL_X, B.BOX_FRONT_X
Y0, Y1 = B.BOX_Y
Z0, Z1 = B.BOX_Z
T = B.BOX_T
BRAKE_PIPE_HOLE = (None, B.MC_Y)          # x filled from the banjo stub
CLUTCH_PIPE_R = 4.0


def _clutch_pipe_crossing():
    """Where the clutch pipe (parts.clutch.hydraulics.pipe_points) passes the mounting wall plane."""
    pts = CH.pipe_points()
    for a, b in zip(pts, pts[1:]):
        if (a[0] - XW) * (b[0] - XW) <= 0 and a[0] != b[0]:
            f = (XW - a[0]) / (b[0] - a[0])
            return tuple(a[i] + f * (b[i] - a[i]) for i in range(3))
    return (XW, pts[-1][1], pts[-1][2])


def anchor_points():
    """Car-frame anchor holes of the clutch and brake pedal pull-off springs (tabs on the anchor bar)."""
    from parts.clutch import pedal as CP
    zc_ = K.PEDAL_PIVOT[2] - 58.0
    yc = K.PEDAL_PIVOT[1] + CP.T / 2 + 4.5
    yb = B.MC_Y + B.PEDAL_T / 2 + 4.5
    return {"clutch": (B.SPRING_ANCHOR_X, yc, zc_), "brake": (B.SPRING_ANCHOR_X, yb, zc_)}


def pedal_box(spec) -> Part:
    yi0, yi1 = Y0 + T, Y1 - T
    # side walls, rear-section top, front-section floor, front wall, mounting wall
    b = box(X0, XF, Y0, Y0 + T, Z0, Z1) + box(X0, XF, Y1 - T, Y1, Z0, Z1)
    b = b + box(X0, XW, Y0, Y1, Z1 - T, Z1)
    b = b + box(XW - B.BOX_FRONT_T, XF, Y0, Y1, Z0, Z0 + T)
    b = b + box(XF - T, XF, Y0, Y1, Z0, Z1)
    b = b + box(XW - B.BOX_FRONT_T, XW, Y0, Y1, Z0, Z1 - T + 0.01)
    # rim round the front opening (flat lip turned inward at the top), cover screw holes in its corners
    rim = box(XW - 0.01, XF, Y0, Y1, Z1 - T, Z1) - box(XW + 10.0, XF - 10.0, Y0 + 10.0, Y1 - 10.0, Z1 - T - 1, Z1 + 1)
    b = b + rim
    for x, y in cover_screws():
        b = b - zc(3.2, Z1 - T - 1, Z1 + 1, x, y)
    # rear flange on the bulkhead: top and sides, with six bolt holes
    fl = box(X0, X0 + T, Y0 - B.BOX_FLANGE, Y1 + B.BOX_FLANGE, Z0, Z1 + B.BOX_FLANGE) - \
        box(X0 - 1, X0 + T + 1, Y0 + T, Y1 - T, Z0 - 1, Z1 - T)
    b = b + fl
    for y, z in box_bolts():
        b = b - xcyl(4.2, X0 - 1, X0 + T + 1, y, z)
    # stiffening swage along each side wall
    for yy in (Y0 - 1.2, Y1 + 1.2):
        b = b + (xcyl(2.2, X0 + 4.0, XF - 4.0, yy, (Z0 + Z1) / 2) & box(X0, XF, min(yy, yy + (1 if yy > Y1 else -1) * 3), max(yy, yy - (1 if yy < Y0 else -1) * 3), Z0, Z1))
    # mounting wall holes: spigots and flange bolts of both cylinders, the clutch pipe
    for (y, r) in ((K.MC_Y, 16.2), (B.MC_Y, SPIGOT_R + 0.7)):
        b = b - xcyl(r, XW - 5, XW + 1, y, B.MC_Z)
        for s in (1, -1):
            b = b - xcyl(4.2, XW - 5, XW + 1, y, B.MC_Z + s * BOLT_X)
    cx, cy, cz = _clutch_pipe_crossing()
    b = b - xcyl(CLUTCH_PIPE_R, XW - 5, XW + 1, cy, cz)
    # floor: grommet hole for the brake pipe under the banjo
    sx, sy, _ = stub_end()
    b = b - zc(6.5, Z0 - 1, Z0 + T + 1, sx, sy)
    # pivot bolt holes
    px, _, pz = B.PEDAL_PIVOT
    b = b - ycyl(6.6, Y0 - 1, Y1 + 1, px, pz)
    # spring anchor bar against the rear flange, with a tab for each pedal spring
    za = K.PEDAL_PIVOT[2] - 58.0
    b = b + box(X0 + T - 0.01, X0 + 2 * T, yi0, yi1, za - 14.0, za + 10.0)
    for name, (ax, ay, az) in anchor_points().items():
        tab = box(X0 + T, ax + 7.0, ay - 1.0, ay + 1.0, az - 7.0, az + 7.0) - ycyl(2.0, ay - 2, ay + 2, ax, az)
        b = b + tab
    return lab(b, spec)


def box_bolts():
    """(y, z) of the six box-to-bulkhead bolts in the rear flange (Sec 19 para 7)."""
    yo, yi = Y0 - B.BOX_FLANGE / 2, Y1 + B.BOX_FLANGE / 2
    zt = Z1 + B.BOX_FLANGE / 2
    return [(yo, Z0 + 12.0), (yo, (Z0 + Z1) / 2), (yi, Z0 + 12.0), (yi, (Z0 + Z1) / 2), (Y0 + 30.0, zt), (Y1 - 30.0, zt)]


def cover_screws():
    """(x, y) of the four cover screws in the rim corners (Sec 17 para 1)."""
    return [(XW + 5.0, Y0 + 5.0), (XW + 5.0, Y1 - 5.0), (XF - 5.0, Y0 + 5.0), (XF - 5.0, Y1 - 5.0)]


def cover(spec) -> Part:
    """Protecting cover over the master cylinders: a pressed hood with rounded top edges on a flange that lies
    on the box rim (Sec 17 para 1; Fig 9.16 item 13 is the later, taller form)."""
    t = spec.nom("thickness")
    inset = 9.0
    h = B.COVER_TOP_Z - Z1
    hood = Box(XF - XW - 2 * inset, Y1 - Y0 - 2 * inset, h, align=(Align.MIN, Align.MIN, Align.MIN))
    hood = fillet(hood.edges().filter_by(Axis.Z), 10.0)
    hood = fillet(hood.edges().group_by(Axis.Z)[-1], 14.0)
    shell = offset(hood, -t, openings=hood.faces().sort_by(Axis.Z)[0])
    shell = shell.moved(Location((XW + inset, Y0 + inset, Z1 + 0.6)))
    fl = box(XW, XF, Y0, Y1, Z1, Z1 + t) - box(XW + inset + t, XF - inset - t, Y0 + inset + t, Y1 - inset - t, Z1 - 1, Z1 + 2)
    c = shell + fl + box(XW + inset, XF - inset, Y0 + inset, Y1 - inset, Z1, Z1 + 0.61) - \
        box(XW + inset + t, XF - inset - t, Y0 + inset + t, Y1 - inset - t, Z1 - 1, Z1 + 2)
    for x, y in cover_screws():
        c = c - zc(3.4, Z1 - 1, Z1 + t + 1, x, y)
    # pressed stiffening rib across the top
    ztop = B.COVER_TOP_Z + 0.6
    c = c + box(XW + 40.0, XF - 40.0, (Y0 + Y1) / 2 - 6.0, (Y0 + Y1) / 2 + 6.0, ztop - 0.01, ztop + 1.4)
    return lab(c, spec)


def cover_screw(spec) -> Part:
    return lab(F.hex_bolt("1/4", spec.nom("length") / IN), spec)


def cover_washer(spec) -> Part:
    return lab(plain_washer("1/4")[0], spec)


def box_bolt(spec) -> Part:
    return lab(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def box_nut(spec) -> Part:
    return lab(F.hex_nut("5/16"), spec)


def box_spring_washer(spec) -> Part:
    return lab(spring_washer("5/16")[0], spec)


def mc_bolt(spec) -> Part:
    return lab(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def mc_nut(spec) -> Part:
    return lab(F.hex_nut("5/16"), spec)


def mc_spring_washer(spec) -> Part:
    return lab(spring_washer("5/16")[0], spec)


def _reuse(fn):
    def build(spec):
        return lab(fn(spec), spec)
    return build


PARTS = {
    "brakes.master.mc-body": {"build": mc_body, "probes": {"bore": lambda p: _bore(p, 19.05 / 2)}},
    "brakes.master.mc-cap": {"build": mc_cap},
    "brakes.master.mc-cap-seal": {"build": mc_cap_seal},
    "brakes.master.valve": {"build": valve},
    "brakes.master.mc-spring": {"build": mc_spring},
    "brakes.master.spring-retainer": {"build": _reuse(CH.mc_spring_retainer)},
    "brakes.master.main-cup": {"build": _reuse(CH.mc_main_cup)},
    "brakes.master.piston-washer": {"build": _reuse(CH.mc_piston_washer)},
    "brakes.master.piston": {"build": _reuse(CH.mc_piston)},
    "brakes.master.secondary-cup": {"build": _reuse(CH.mc_secondary_cup)},
    "brakes.master.pushrod": {"build": _reuse(CH.mc_pushrod)},
    "brakes.master.circlip": {"build": _reuse(CH.mc_circlip)},
    "brakes.master.boot": {"build": _reuse(CH.mc_boot)},
    "brakes.master.banjo": {"build": banjo},
    "brakes.master.banjo-bolt": {"build": banjo_bolt},
    "brakes.master.gasket-inner": {"build": gasket("inner")},
    "brakes.master.gasket-outer": {"build": gasket("outer")},
    "brakes.master.mc-bolt-long": {"build": mc_bolt},
    "brakes.master.mc-bolt": {"build": mc_bolt},
    "brakes.master.mc-nut": {"build": mc_nut},
    "brakes.master.mc-spring-washer": {"build": mc_spring_washer},
    "brakes.master.pedal-box": {"build": pedal_box},
    "brakes.master.cover": {"build": cover},
    "brakes.master.cover-screw": {"build": cover_screw},
    "brakes.master.cover-washer": {"build": cover_washer},
    "brakes.master.box-bolt": {"build": box_bolt},
    "brakes.master.box-nut": {"build": box_nut},
    "brakes.master.box-spring-washer": {"build": box_spring_washer},
}


_bore = bore
