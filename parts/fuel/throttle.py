"""Accelerator pedal, cable and the throttle interconnection on the twin SU HS4s (early RHD car).

Haynes Ch 3 Fig 3.10 items 38-45, Fig 3.13, photo 17.1(b), Sec 21, Sec 45; factory parts list plates 108-G2 and
108-G4; Rimmer Bros GRID019709 (see specs/fuel/throttle.yaml). Every part is built in the car frame at its place in
mgb.throttle_layout, so the assembly places them all at the origin.

Kinematics as drawn (at rest): pressing the pad swings the pedal about its pivot (axis along y); the top arm moves
rearward and draws the inner out of the guide; at the carburettors the inner lifts the throttle shaft lever's swivel
pin, turning the interconnecting shaft and, through the folded clamps, both throttle spindles. Three springs from the
levers to the heat shield's lip close the throttles and return the pedal.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot

from mgb import carb_layout as K, fasteners as F, throttle_layout as T
from mgb.brake_parts import (IN, box, chamfered_hex, lab, nyloc, plain_washer, rod, spring_washer, split_pin,
                             tension_spring, tube_rod, xcyl, xprism, ycyl, yprism, zc)
from mgb.poly2d import circle_pts, hull
from mgb.chassis_geom import zcyl, zrev

PY = T.PEDAL_Y


def _bar(pts, w, plane, a0, a1, n=20):
    """Flat bar of width w through the 2D points (hulls of circles, segment by segment), extruded a0..a1 across
    `plane` ('x' = a YZ outline extruded along x, 'y' = an XZ outline extruded along y)."""
    out = None
    for a, b in zip(pts, pts[1:]):
        poly = hull(circle_pts(a[0], a[1], w / 2, n) + circle_pts(b[0], b[1], w / 2, n))
        s = xprism(poly, a0, a1) if plane == "x" else yprism(poly, a0, a1)
        out = s if out is None else out + s
    return out


def _disc(c, r, plane, a0, a1, n=32):
    poly = circle_pts(c[0], c[1], r, n)
    return xprism(poly, a0, a1) if plane == "x" else yprism(poly, a0, a1)


def _xbolt(size, length_in, x_head, y, z, toward=1):
    """Hex bolt along x, head underside at x_head, shank toward +x (toward=1) or -x."""
    b = F.hex_bolt(size, length_in)
    return Location((x_head, y, z)) * Rot(0, 90 * toward, 0) * b


def _ybolt(size, length_in, y_head, x, z, toward=1):
    b = F.hex_bolt(size, length_in)
    return Location((x, y_head, z)) * Rot(-90 * toward, 0, 0) * b


def _pan_screw(d, L, head_d=None, head_h=None):
    """Pan-head machine screw along +z from the head's underside at z 0."""
    hd = head_d or 1.9 * d
    hh = head_h or 0.65 * d
    from mgb.brake_parts import yrev
    head = zc(hd / 2, -hh, 0.0) - box(-hd, hd, -0.4, 0.4, -hh - 0.1, -hh + 0.35 * hh)   # slot
    return head + zc(d / 2, 0.0, L)


# =====================================================================================================================
# pedal, pad, bracket, pivot (cabin)
# =====================================================================================================================
def _pad_frame():
    a = math.radians(T.PAD_TILT_DEG)
    n = (-math.cos(a), 0.0, math.sin(a))                 # pad face normal: rearward, up
    up = (math.sin(a), 0.0, math.cos(a))                 # up the face
    return n, up


def _arm_points():
    n, up = _pad_frame()
    px, _, pz = T.PAD
    end = (px - n[0] * 21.0, pz - n[2] * 21.0)          # behind the foot plate (the bar's edge on its back)
    prev = (end[0] + 40.0 * up[0], end[1] + 40.0 * up[2])
    return list(T.ARM) + [prev, end]


def pedal(spec) -> Part:
    """AHC135: top arm with the cable tab, pivot boss, swaged main arm, foot plate."""
    t = spec.nom("thickness")
    y0, y1 = PY - t / 2, PY + t / 2
    px, _, pz = T.PIVOT
    cx, _, cz = T.CABLE_END
    pts = _arm_points()
    p = _bar(pts, 20.0, "y", y0, y1)
    p = p + _bar([(px, pz), (cx, cz - 12.0)], 16.0, "y", y0, y1)                # top arm above the pivot
    # cable tab: the top end turned forward square to the cable, the inner through it (split pin behind)
    tab = box(cx - 3.0, cx, PY - 9.0, y1, cz - 9.0, cz + 9.0)
    p = p + tab
    # swaged stiffening rib down the main arm, on its outboard face
    p = p + _bar(pts[1:4], 6.0, "y", y0 - 1.4, y0 + 0.01)
    # pressed boss round the pivot (the distance tube runs in it)
    p = p + ycyl(10.0, PY - 7.0, PY + 2.5, px, pz)
    # foot plate under the pad
    n, up = _pad_frame()
    pl = Plane(origin=(T.PAD[0] - n[0] * 7.0, PY, T.PAD[2] - n[2] * 7.0), x_dir=(0, 1, 0), z_dir=n)
    p = p + pl.location * zcyl(11.0, -9.0, 0.0)                   # boss for the stub (Oliver's kf151: no foot plate)
    p = p - ycyl(6.1, PY - 9.0, PY + 5.0, px, pz)                               # boss bore
    p = p - xcyl(1.2, cx - 4.0, cx + 1.0, PY, cz)                               # cable hole in the tab
    return lab(p, spec)


def pad(spec) -> Part:
    """The accelerator's foot stub on Oliver's car (kf151): a short round chromed roller on the end of the pedal's
    arm, square to the foot, where the standard car has the GPR105 rubber pad on a plate."""
    n, up = _pad_frame()
    pl = Plane(origin=(T.PAD[0] - n[0] * 7.0, PY, T.PAD[2] - n[2] * 7.0), x_dir=(0, 1, 0), z_dir=n)
    L = spec.nom("thickness")
    stub = zcyl(12.5, 0.0, L - 3.0) + zrev([(0.0, L - 3.0), (12.5, L - 3.0), (11.0, L - 0.5), (9.0, L), (0.0, L)])
    for k in range(3):                                            # knurled grooves round it
        stub = stub - (zcyl(13.0, 4.0 + 6.0 * k, 5.2 + 6.0 * k) - zcyl(12.0, 3.0 + 6.0 * k, 6.2 + 6.0 * k))
    return lab(pl.location * stub, spec)


def pedal_bracket(spec) -> Part:
    """Welded pivot bracket: flange on the bulkhead's cabin face, one cheek back to the pivot with a raised pad."""
    t = spec.nom("thickness")
    ya, yb = T.BRACKET_Y
    px, _, pz = T.PIVOT
    x0 = T.CAB
    cheek = [(x0 - 2.0, -204.0), (x0 - 2.0, -150.0), (px + 12.0, -144.0)] + \
        circle_pts(px, pz, 13.0, 16, 80.0, 250.0) + [(px - 2.0, -176.0), (x0 - 22.0, -204.0)]
    c = yprism(hull(cheek), ya, yb)
    c = c + _disc((px, pz), 9.0, "y", ya - 0.8, yb)                             # raised pad round the hole
    flange = box(x0 - t, x0, ya, ya + 20.0, -204.0, -150.0)                     # spot-welded to the panel
    c = c + flange + box(x0 - t - 2.0, x0, ya, yb, -204.0, -150.0)
    c = c - ycyl(4.2, ya - 2.0, yb + 1.0, px, pz)
    for z in (-196.0, -158.0):                                                  # spot-weld dimples
        for dy in (6.0, 15.0):
            c = c - xcyl(1.8, x0 - t - 0.4, x0 - t + 0.5, ya + dy, z)
    return lab(c, spec)


def distance_tube(spec) -> Part:
    od, id_, L = spec.nom("outside_diameter"), spec.nom("inside_diameter"), spec.nom("length")
    ya = T.BRACKET_Y[0] - 0.8                                                 # on the bracket's raised pad
    px, _, pz = T.PIVOT
    return lab(ycyl(od / 2, ya - L, ya, px, pz) - ycyl(id_ / 2, ya - L - 1, ya + 1, px, pz), spec)


def _pivot_stack():
    """y stations: bracket cheek inner face, tube end, washer end, nut end."""
    yb = T.BRACKET_Y[1]
    ya = T.BRACKET_Y[0]
    tube_end = ya - 0.8 - 14.0
    w = F.WASHER["5/16"][2] * IN
    return yb, tube_end, tube_end - w


def pivot_bolt(spec) -> Part:
    px, _, pz = T.PIVOT
    yb, _, _ = _pivot_stack()
    return lab(_ybolt("5/16", spec.nom("length") / IN, yb, px, pz, toward=-1), spec)


def pivot_washer(spec) -> Part:
    px, _, pz = T.PIVOT
    _, te, _ = _pivot_stack()
    w, wt = plain_washer("5/16")
    return lab(Location((px, te, pz)) * Rot(90, 0, 0) * w, spec)


def pivot_nut(spec) -> Part:
    px, _, pz = T.PIVOT
    _, _, we = _pivot_stack()
    return lab(Location((px, we, pz)) * Rot(90, 0, 0) * nyloc("5/16"), spec)


# ---- pedal stop on the toe board -----------------------------------------------------------------------------------
def _toe_plane(off=0.0, along=0.0):
    """Frame on the toe board's cabin face at the stop: z out of the board, x up the slope."""
    bx, bz = T.STOP_BASE
    n, u = T.TOE_N, T.TOE_U
    off = off + T.STOP_LIFT
    o = (bx + n[0] * off + u[0] * along, PY, bz + n[1] * off + u[1] * along)
    return Plane(origin=o, z_dir=(n[0], 0.0, n[1]), x_dir=(u[0], 0.0, u[1]))


def pedal_stop(spec) -> Part:
    """AHB7162: pressed plate on the toe board, two screw holes, a raised tapped boss for the stop screw."""
    from build123d import Align, Box, Cylinder
    t = spec.nom("thickness")
    pl = _toe_plane()
    plate = Location((20.0, 0, 0)) * Box(60.0, 34.0, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = plate + Cylinder(9.5, 5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))          # raised boss
    plate = plate - Location((0, 0, -1)) * Cylinder(7.0, 4.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = plate - Cylinder(3.15, 30.0)                                       # tapped 1/4 UNF
    for a in T.STOP_FIX_ALONG:
        plate = plate - Location((a, 0, 0)) * Cylinder(3.4, 10.0)
    for s in (-1, 1):                                                           # stiffening beads either side
        plate = plate + Location((24.0, s * 13.0, t)) * Box(40.0, 2.4, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return lab(pl.location * plate, spec)


def stop_screw(spec) -> Part:
    """Hex screw out of the boss, its head the stop the pedal arm meets."""
    L = spec.nom("length")
    b = F.hex_bolt("1/4", L / IN)
    pl = _toe_plane(off=T.STOP_SCREW_OUT)
    return lab(pl.location * Rot(180, 0, 0) * b, spec)


def stop_locknut(spec) -> Part:
    pl = _toe_plane(off=5.5)
    return lab(pl.location * F.hex_nut("1/4"), spec)


def stop_fixing_screw(spec) -> Part:
    """Pan-head screw, built along -z from its head (local); placed on the toe plane."""
    s = _pan_screw(spec.nom("thread_diameter"), spec.nom("length"))
    return lab(Rot(180, 0, 0) * s, spec)


def stop_spring_washer(spec) -> Part:
    w, wt = spring_washer("1/4")
    return lab(w, spec)


# =====================================================================================================================
# cable guide, cable, clip
# =====================================================================================================================
def cable_guide(spec) -> Part:
    """AHH5308: round flange on the bulkhead's engine-side face (over its gasket), a tapered nose forward holding the
    outer's ferrule, the inner's bore through, two screw lugs."""
    gx, gy, gz = T.GUIDE
    x0 = gx + 1.0                                                               # on the gasket
    r = spec.nom("flange_diameter") / 2
    from mgb.brake_parts import xrev
    g = Location((x0, gy, gz)) * xrev([(0, 0), (r, 0), (r, 3.0), (6.4, 3.0), (6.4, 5.0), (5.4, T.GUIDE_NOSE),
                                         (0, T.GUIDE_NOSE)])
    for y, z in T.GUIDE_SCREWS:
        g = g - xcyl(2.5, x0 - 1, x0 + 4, y, z)
    g = g - xcyl(1.4, x0 - 1, x0 + T.GUIDE_NOSE + 1, gy, gz)                   # inner's bore
    g = g - xcyl(3.3, x0 + T.GUIDE_NOSE - 9.0, x0 + T.GUIDE_NOSE + 1, gy, gz)   # ferrule seat
    return lab(g, spec)


def guide_gasket(spec) -> Part:
    gx, gy, gz = T.GUIDE
    t = spec.nom("thickness")
    g = xcyl(13.0, gx, gx + t, gy, gz) - xcyl(3.0, gx - 1, gx + t + 1, gy, gz)
    for y, z in T.GUIDE_SCREWS:
        g = g - xcyl(2.5, gx - 1, gx + t + 1, y, z)
    return lab(g, spec)


def guide_screw(spec) -> Part:
    """Pan-head No 10 screw along +z from its head's underside (local)."""
    return lab(_pan_screw(spec.nom("thread_diameter"), spec.nom("length")), spec)


def _small_nut(af, t, d):
    return chamfered_hex(af, t) - zc(d / 2 * 0.92, -1, t + 1)


def guide_nut(spec) -> Part:
    return lab(_small_nut(spec.nom("across_flats"), 3.2, 0.19 * IN), spec)


def ferrule(a, b):
    """Crimped ferrule on an outer's end at a (the cable comes from b): collar at a, body beyond it."""
    from mgb.brake_parts import frame
    d = [a[i] - b[i] for i in range(3)]
    f = zc(3.2, 0.0, T.FERRULE_L) + zc(3.9, 0.0, 3.0)
    return frame(a, d) * (f - zc(1.1, -1, T.FERRULE_L + 1))


def cable_outer(spec) -> Part:
    """Outer with crimped ferrules at both ends, on the THROTTLE_OUTER route."""
    pts = T.THROTTLE_OUTER
    ro = spec.nom("outside_diameter") / 2
    from mgb.elec_shapes import cable as swept
    c = swept(pts, 2 * ro, 28.0)                 # solid (a hollow sweep of this route fails)
    from mgb.brake_parts import frame
    for a, b in ((pts[0], pts[1]), (pts[-1], pts[-2])):
        c = c + ferrule(a, b)
    return lab(c, spec)


def cable_inner(spec) -> Part:
    """Exposed ends of the inner: cabin (guide to the pedal tab, barrel nipple behind it) and carburettor end
    (abutment bracket down through the swivel pin's cross hole)."""
    r = spec.nom("diameter") / 2
    gx, gy, gz = T.GUIDE
    cx, _, cz = T.CABLE_END
    cab = xcyl(r, cx - 12.0, gx + 6.0, gy, gz)
    cab = cab + xcyl(2.6, cx - 13.0, cx - 3.2, gy, gz) - ycyl(0.9, gy - 4, gy + 4, cx - 7.0, gz)   # nipple, pin hole
    fx, fy, fz = T.THROTTLE_FERRULE
    carb = zc(r, T.ACCEL_PIN[1] - 9.0, fz + 4.0, fx, fy)
    return lab(cab + carb, spec)


def pedal_split_pin(spec) -> Part:
    cx, _, cz = T.CABLE_END
    sp = split_pin(spec.nom("diameter"), 9.0)
    return lab(Location((cx - 7.0, PY - 4.5, cz)) * Rot(-90, 0, 0) * sp, spec)


def _cover_top_z():
    return T.COVER_CLIP_Z


def cover_clip(spec) -> Part:
    """PCR307: steel band round the outer, its two tails flat on the cover under the screw."""
    x, y = T.COVER_CLIP
    zt = _cover_top_z()
    pts = T.THROTTLE_OUTER
    zc_ = zt + 7.4
    # band round the outer (cable here runs roughly along y)
    band = ycyl(4.6, y - 6.0, y + 6.0, x, zc_) - ycyl(3.1, y - 7.0, y + 7.0, x, zc_)
    band = band - box(x - 6, x + 6, y - 7, y + 7, zt - 5, zc_ - 3.5)
    tail = box(x - 4.6, x + 15.0, y - 6.0, y + 6.0, zt, zt + 1.0)
    web = box(x + 2.2, x + 4.6, y - 6.0, y + 6.0, zt, zc_)
    c = band + tail + web - zc(2.8, zt - 1, zt + 2, x + T.COVER_CLIP_SCREW_DX, y)
    return lab(c, spec)


def cover_clip_screw(spec) -> Part:
    x, y = T.COVER_CLIP
    zt = _cover_top_z()
    s = _pan_screw(0.19 * IN, spec.nom("length"))
    return lab(Location((x + T.COVER_CLIP_SCREW_DX, y, zt + 1.0)) * Rot(180, 0, 0) * s, spec)


def cover_clip_nut(spec) -> Part:
    x, y = T.COVER_CLIP
    zt = _cover_top_z()
    n = _small_nut(spec.nom("across_flats"), 3.2, 0.19 * IN)
    return lab(Location((x + T.COVER_CLIP_SCREW_DX, y, zt - 1.0)) * Rot(180, 0, 0) * n, spec)


# ---- abutment bracket on the heat shield ---------------------------------------------------------------------------
def abutment_bracket(spec) -> Part:
    t = spec.nom("thickness")
    y0 = T.SHIELD_FACE_Y
    x0, x1 = T.BRACKET_X
    z0, z1 = T.BRACKET_Z
    plate = xprism([(y0, z0 + 6.0), (y0, z1), (y0 + t, z1), (y0 + t, z0 + 6.0)], x0, x1)
    plate = box(x0, x1, y0, y0 + t, z0, z1 + t)
    from mgb.brake_parts import zprism
    from mgb.poly2d import rounded
    rect = [(x0, y0), (x1, y0), (x1, T.BRACKET_FLANGE_Y), (x0, T.BRACKET_FLANGE_Y)]
    flange = zprism(rounded(rect, 6.0), z1, z1 + t) + box(x0, x1, y0, y0 + 8.0, z1, z1 + t)
    b = plate + flange
    b = b + box(x0 + 4.0, x1 - 4.0, y0 + t, y0 + t + 1.2, z1 - 8.0, z1)           # bead along the bend
    b = b + box(x1 - t, x1, y0, T.BRACKET_FLANGE_Y - 10.0, z1 - 14.0, z1)          # turned-down edge stiffener
    for x, z in T.BRACKET_SCREW_XZ:
        b = b - ycyl(3.4, y0 - 1, y0 + t + 2, x, z)
    fx, fy, _ = T.THROTTLE_FERRULE
    b = b - zc(1.6, z1 - 1, z1 + t + 1, fx, fy)                                  # throttle inner, ferrule sits on top
    cx, cy, _ = T.CHOKE_FERRULE
    b = b - zc(3.2, z1 - 1, z1 + t + 1, cx, cy)                                  # choke abutment's thread
    return lab(b, spec)


def bracket_screw(spec) -> Part:
    return lab(F.hex_bolt("1/4", spec.nom("length") / IN), spec)


def bracket_nut(spec) -> Part:
    return lab(F.hex_nut("1/4"), spec)


# =====================================================================================================================
# throttle interconnection on the carburettors
# =====================================================================================================================
def _lever_x(xc):
    return xc - K.side(xc) * T.LEVER_DX


def throttle_lever(xc):
    def build(spec) -> Part:
        """Fig 3.10 38/39: hub on the spindle's flats, arm outboard under the spindle with the adjusting screw's
        boss, the spring hole at its end."""
        t = spec.nom("thickness")
        lx = _lever_x(xc)
        s = K.side(xc)
        y, z = K.SPINDLE_Y, K.AXIS_Z
        ay, az = T.LEVER_ARM
        p = _bar([(y, z), (T.STOP_SCREW_Y, az + 1.0), (ay, az)], 11.0, "x", lx - t / 2, lx + t / 2)
        p = p + _disc((y, z), 7.5, "x", lx - t / 2 - 1.0, lx + t / 2 + 1.0)       # hub
        p = p + zc(4.6, az - 4.0, az + 6.0, lx, T.STOP_SCREW_Y)                   # adjusting screw boss
        p = p - xcyl(T.SPINDLE_R + 0.05, lx - t / 2 - 2, lx + t / 2 + 2, y, z)
        p = p - zc(2.4, az - 6.0, az + 8.0, lx, T.STOP_SCREW_Y)                   # 2BA-ish tapped hole
        p = p - xcyl(1.3, lx - 5, lx + 5, ay, az)                                  # spring hole
        return lab(p, spec)
    return build


def _flat_bore(x, y, z, L):
    """Spindle bore with the two flats the lever and nut key to."""
    r = T.SPINDLE_R
    return xcyl(r + 0.1, x - L / 2, x + L / 2, y, z) & box(x - L / 2, x + L / 2, y - r - 1, y + r + 1, z - r * 0.8, z + r * 0.8)


def lever_tab_washer(spec) -> Part:
    """Fig 3.10 43, local: on the x axis from x 0 toward -x (away from the lever), its tab down and turned over
    the lever's edge at +x."""
    t = spec.nom("thickness")
    w = xcyl(7.0, -t, 0.0) + box(-t, 0.0, -2.5, 2.5, -11.0, 0.0)
    w = w + box(-t, 4.0, -2.5, 2.5, -11.0, -11.0 + t)
    w = w - xcyl(T.SPINDLE_R + 0.15, -t - 1, 1)
    return lab(w, spec)


def lever_nut(spec) -> Part:
    """Thin nut on the spindle end, local along +z."""
    x0, x1 = T.NUT_X
    return lab(_small_nut(spec.nom("across_flats"), x1 - x0, 2 * T.SPINDLE_R), spec)


def adjusting_screw(spec) -> Part:
    """Fig 3.10 44: slotted cheese-head screw, local: tip at z 0, head on top."""
    L = spec.nom("length")
    s = zc(2.3, 0.0, L) + zc(3.8, L, L + 3.2)
    s = s - box(-4, 4, -0.45, 0.45, L + 2.0, L + 3.3)
    return lab(s, spec)


def adjusting_spring(spec) -> Part:
    """Fig 3.10 45: coil between the arm's boss and the screw head, local from z 0."""
    from mgb.brake_parts import coil
    L = T.STOP_LUG_TOP + 0.2 + _ADJ_L - (T.LEVER_ARM[1] + 6.0)
    return lab(coil(0.6, spec.nom("outside_diameter"), L, 4.0), spec)


_ADJ_L = 22.0


def coupling(spec) -> Part:
    """Folded clamp, local about the x axis, centred on x 0: a strip wrapped round the spindle end and the shaft
    end, its two ends turned up together as ears with the pinch bolt through them (Fig 3.13, 3.17)."""
    L = spec.nom("length")
    x0, x1 = -L / 2, L / 2
    ri = T.SHAFT_R + 0.05
    c = xcyl(ri + 1.4, x0, x1) - xcyl(ri, x0 - 1, x1 + 1)
    c = c - box(x0 - 1, x1 + 1, -0.6, 0.6, 0, ri + 2)                         # the fold's gap
    c = c + box(x0, x1, 0.6, 2.0, ri + 0.3, 15.5) + box(x0, x1, -2.0, -0.6, ri + 0.3, 15.5)
    c = c - ycyl(2.5, -4, 4, 0.0, T.PINCH_Z)
    return lab(c, spec)


def _small_bolt_z(d, L, af):
    """Hex bolt along +z from its head's underside (local), flats on +/-y."""
    from mgb.brake_parts import hexp
    return hexp(af, 0.35 * af, -0.35 * af) + zc(d / 2, 0.0, L)


def coupling_bolt(spec) -> Part:
    return lab(_small_bolt_z(spec.nom("thread_diameter"), spec.nom("length"), 0.375 * IN), spec)


def coupling_nut(spec) -> Part:
    return lab(_small_nut(spec.nom("across_flats"), 3.6, 0.1875 * IN), spec)


def shaft(spec) -> Part:
    r = spec.nom("diameter") / 2
    s = xcyl(r, -T.SHAFT_HALF, T.SHAFT_HALF, K.SPINDLE_Y, K.AXIS_Z)
    from build123d import chamfer
    return lab(s, spec)


def shaft_lever(spec) -> Part:
    """12H715: split hub clamped on the shaft, arm outboard and down with the swivel pin's hole, the spring hole and
    the fast idle stop tab at its foot over the choke rod."""
    y, z = K.SPINDLE_Y, K.AXIS_Z
    x = T.ACCEL_LEVER_X
    py, pz = T.ACCEL_PIN
    sy, sz = T.ACCEL_SPRING
    ry, rz = T.ROD
    foot_z = rz + T.ROD_R + T.FAST_IDLE_GAP                                    # underside of the stop tab
    foot = (ry - 2.0, foot_z + 2.0 + 4.0)
    p = _bar([(y, z), (py, pz), (sy, sz), foot], 10.0, "x", x - 1.5, x + 1.5)
    p = p + _disc((y, z), 7.5, "x", x - 4.0, x + 4.0)                          # hub
    p = p + box(x - 4.0, x + 4.0, y + 0.6, y + 4.6, z + 4.0, z + T.PINCH_Z + 4.5)   # clamp ears either side of the split
    p = p + box(x - 4.0, x + 4.0, y - 4.6, y - 0.6, z + 4.0, z + T.PINCH_Z + 4.5)
    p = p - box(x - 5, x + 5, y - 0.6, y + 0.6, z, z + T.PINCH_Z + 5.0)
    p = p - xcyl(T.SHAFT_R + 0.05, x - 5, x + 5, y, z)
    p = p - ycyl(2.5, y - 6, y + 6, x, z + T.PINCH_Z)
    p = p + box(x - 1.5, x + 6.5, ry - 7.0, ry + 3.0, foot_z, foot_z + 2.0)    # stop tab turned over the rod
    p = p - xcyl(3.1, x - 3, x + 3, py, pz)                                    # swivel pin hole
    p = p - xcyl(1.3, x - 3, x + 3, sy, sz)                                    # spring hole
    return lab(p, spec)


def shaft_lever_bolt(spec) -> Part:
    y, z = K.SPINDLE_Y, K.AXIS_Z
    b = _small_bolt_z(spec.nom("thread_diameter"), spec.nom("length"), 0.375 * IN)
    return lab(Location((T.ACCEL_LEVER_X, y + 4.6, z + T.PINCH_Z)) * Rot(90, 0, 0) * b, spec)


def shaft_lever_nut(spec) -> Part:
    y, z = K.SPINDLE_Y, K.AXIS_Z
    n = _small_nut(spec.nom("across_flats"), 3.6, 0.1875 * IN)
    return lab(Location((T.ACCEL_LEVER_X, y - 4.6, z + T.PINCH_Z)) * Rot(90, 0, 0) * n, spec)


def swivel_pin(spec) -> Part:
    """ACC5062: shouldered pin through the lever, cross-drilled for the inner, a clamp screw in its end."""
    py, pz = T.ACCEL_PIN
    x = T.ACCEL_LEVER_X
    r = spec.nom("diameter") / 2
    p = xcyl(r - 0.1, x - 9.4, x + 1.5, py, pz) + xcyl(r + 1.0, x + 1.5, x + 13.0, py, pz)
    p = p - zc(1.0, pz - 6, pz + 6, x + T.SWIVEL_DX, py)                        # cross hole for the inner
    p = p - ycyl(0.85, py - 6, py + 6, x - T.SWIVEL_PIN_X, pz)                  # split pin hole
    p = p + xcyl(2.5, x + 13.0, x + 15.0, py, pz) - box(x + 14.0, x + 15.1, py - 3, py + 3, pz - 0.4, pz + 0.4)
    return lab(p, spec)


def swivel_washer(spec) -> Part:
    w, wt = plain_washer("5/16")
    return lab(w, spec)


def anti_rattle_washer(spec) -> Part:
    py, pz = T.ACCEL_PIN
    x = T.ACCEL_LEVER_X
    wt = F.WASHER["5/16"][2] * IN
    from mgb.brake_parts import xrev
    od = spec.nom("outside_diameter")
    w = xrev([(3.2, 0.0), (od / 2, 0.8), (od / 2, 1.2), (3.2, 0.4)])
    return lab(Location((x - 1.5 - 1.2, py, pz)) * w, spec)


def swivel_split_pin(spec) -> Part:
    py, pz = T.ACCEL_PIN
    x = T.ACCEL_LEVER_X
    sp = split_pin(spec.nom("diameter"), 14.0)
    return lab(Location((x - T.SWIVEL_PIN_X, py - 4.0, pz)) * Rot(-90, 0, 0) * sp, spec)


def return_spring(spec) -> Part:
    """AEC2075, local: from the lever's hole at the origin down to the lip hole (same drop for all three)."""
    y, z = T.LEVER_ARM
    p1 = (0.0, T.SPRING_LIP_Y - y, T.LIP_Z - T.LIP_T / 2 - z)
    return lab(tension_spring((0.0, 0.0, 0.0), p1, spec.nom("wire_diameter"), spec.nom("outside_diameter"),
                              hook_axis=(1, 0, 0)), spec)



# ---- placements of the parts used more than once (local builds); every other part is built in place -------------
def _toe_loc(off, along=0.0, flip=False):
    pl = _toe_plane(off=off, along=along)
    return pl.location


def _side_locs():
    out = {}
    y, z = K.SPINDLE_Y, K.AXIS_Z
    tabs, nuts, screws, springs, coups, cbolts, cnuts = [], [], [], [], [], [], []
    for xc in (T.FRONT, T.REAR):
        s = K.side(xc)
        lx = _lever_x(xc)
        face = lx - s * (T.LEVER_T / 2 + 1.0)                                  # hub's inboard face
        rz = Rot(0, 0, 0) if s > 0 else Rot(0, 0, 180)
        tabs.append(Location((face, y, z)) * rz)
        nuts.append(Location((s * T.NUT_X[1], y, z)) * Rot(0, -90 * s, 0))
        screws.append(Location((lx, T.STOP_SCREW_Y, T.STOP_LUG_TOP + 0.2)))
        springs.append(Location((lx, T.STOP_SCREW_Y, T.LEVER_ARM[1] + 6.0)))
        xm = s * sum(T.CLAMP_X) / 2
        coups.append(Location((xm, y, z)))
        cbolts.append(Location((xm, y + 2.0, z + T.PINCH_Z)) * Rot(90, 0, 0))
        cnuts.append(Location((xm, y - 2.0, z + T.PINCH_Z)) * Rot(90, 0, 0))
    out.update({"lever-tab-washer": tabs, "lever-nut": nuts, "adjusting-screw": screws, "adjusting-spring": springs,
                "coupling": coups, "coupling-bolt": cbolts, "coupling-nut": cnuts})
    return out


def placements():
    """{short part id: [Location, ...]} for the parts built locally."""
    pl = _side_locs()
    pl["stop-fixing-screw"] = [_toe_loc(2.5 + 1.6 + 0.6, a) for a in T.STOP_FIX_ALONG]
    pl["stop-spring-washer"] = [_toe_loc(2.5, a) for a in T.STOP_FIX_ALONG]
    gx = T.GUIDE[0] + 1.0 + 3.0
    pl["guide-screw"] = [Location((gx, y, z)) * Rot(0, -90, 0) for y, z in T.GUIDE_SCREWS]
    pl["guide-nut"] = [Location((T.CAB, y, z)) * Rot(0, -90, 0) for y, z in T.GUIDE_SCREWS]
    yb = T.SHIELD_FACE_Y + T.BRACKET_T
    pl["bracket-screw"] = [Location((x, yb, z)) * Rot(90, 0, 0) for x, z in T.BRACKET_SCREW_XZ]
    pl["bracket-nut"] = [Location((x, T.SHIELD_FACE_Y - K.SHIELD_T, z)) * Rot(90, 0, 0) for x, z in T.BRACKET_SCREW_XZ]
    py, pz = T.ACCEL_PIN
    wt = F.WASHER["5/16"][2] * IN
    x0 = T.ACCEL_LEVER_X - 1.5 - 1.2                                           # behind the anti-rattle washer
    pl["swivel-washer"] = [Location((x0 - wt, py, pz)) * Rot(0, 90, 0), Location((x0 - 2 * wt, py, pz)) * Rot(0, 90, 0)]
    y, z = T.LEVER_ARM
    pl["return-spring"] = [Location((x, y, z)) for x in T.SPRING_X]
    return pl


FR, RR = T.FRONT, T.REAR
PARTS = {
    "fuel.throttle.pedal": {"build": pedal},
    "fuel.throttle.pad": {"build": pad},
    "fuel.throttle.pedal-bracket": {"build": pedal_bracket},
    "fuel.throttle.distance-tube": {"build": distance_tube},
    "fuel.throttle.pivot-bolt": {"build": pivot_bolt, "probes": {"length": lambda p: p.bounding_box().size.Y - F.BOLT_HEAD["5/16"][1] * IN}},
    "fuel.throttle.pivot-washer": {"build": pivot_washer},
    "fuel.throttle.pivot-nut": {"build": pivot_nut},
    "fuel.throttle.pedal-stop": {"build": pedal_stop},
    "fuel.throttle.stop-screw": {"build": stop_screw},
    "fuel.throttle.stop-locknut": {"build": stop_locknut},
    "fuel.throttle.stop-fixing-screw": {"build": stop_fixing_screw, "probes": {"length": lambda p: -p.bounding_box().min.Z}},
    "fuel.throttle.stop-spring-washer": {"build": stop_spring_washer},
    "fuel.throttle.cable-guide": {"build": cable_guide},
    "fuel.throttle.guide-gasket": {"build": guide_gasket},
    "fuel.throttle.guide-screw": {"build": guide_screw, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "fuel.throttle.guide-nut": {"build": guide_nut},
    "fuel.throttle.cable-outer": {"build": cable_outer},
    "fuel.throttle.cable-inner": {"build": cable_inner},
    "fuel.throttle.pedal-split-pin": {"build": pedal_split_pin},
    "fuel.throttle.cover-clip": {"build": cover_clip},
    "fuel.throttle.cover-clip-screw": {"build": cover_clip_screw},
    "fuel.throttle.cover-clip-nut": {"build": cover_clip_nut},
    "fuel.throttle.abutment-bracket": {"build": abutment_bracket},
    "fuel.throttle.bracket-screw": {"build": bracket_screw, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "fuel.throttle.bracket-nut": {"build": bracket_nut},
    "fuel.throttle.throttle-lever-front": {"build": throttle_lever(FR)},
    "fuel.throttle.throttle-lever-rear": {"build": throttle_lever(RR)},
    "fuel.throttle.lever-tab-washer": {"build": lever_tab_washer},
    "fuel.throttle.lever-nut": {"build": lever_nut},
    "fuel.throttle.adjusting-screw": {"build": adjusting_screw},
    "fuel.throttle.adjusting-spring": {"build": adjusting_spring},
    "fuel.throttle.coupling": {"build": coupling, "probes": {"length": lambda p: p.bounding_box().size.X}},
    "fuel.throttle.coupling-bolt": {"build": coupling_bolt},
    "fuel.throttle.coupling-nut": {"build": coupling_nut},
    "fuel.throttle.shaft": {"build": shaft},
    "fuel.throttle.shaft-lever": {"build": shaft_lever},
    "fuel.throttle.shaft-lever-bolt": {"build": shaft_lever_bolt},
    "fuel.throttle.shaft-lever-nut": {"build": shaft_lever_nut},
    "fuel.throttle.swivel-pin": {"build": swivel_pin},
    "fuel.throttle.swivel-washer": {"build": swivel_washer},
    "fuel.throttle.anti-rattle-washer": {"build": anti_rattle_washer},
    "fuel.throttle.swivel-split-pin": {"build": swivel_split_pin},
    "fuel.throttle.return-spring": {"build": return_spring},
}
