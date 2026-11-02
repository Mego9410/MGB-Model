"""Handbrake, early layout (Haynes Ch 9 Fig 9.10 items 1-29 and A, printed p153; Sec 4 adjustment p148, Sec 16
removal p154): the lever on the right of the tunnel, the cable to the compensating levers on the axle, and the two
rods out to the levers on the backplates (parts/brakes/rear.py, `brake_layout.HB_LEVER_END`).

Car frame for the lever and cable (mgb.brake_layout HB_*), axle frame AF for the compensator and rods (its fulcrum
is P7's pin on the rear of the banjo bowl, `rear_axle_layout.BALANCE_PIVOT`, pointing rearward with a split pin
hole).

Forms (Fig 9.10):
- handle (2): flat steel lever, its rear end round the pivot with the pivot spigot welded through it, cranked up
  to the grip (3) at the front with the release knob (5) and its spring (6) in the end; the pawl rod (4) along the
  handle's outer face to the pawl (7) on a pin near the pivot.
- ratchet plate (9): pressed plate on the tunnel wall (three bolts), the toothed sector the pawl drops into and the
  spigot's bush; washers (8, 10) either side.
- operating lever (11): on the spigot's squared inner end inside the tunnel, its lower end a fork carrying the
  trunnion (20); the cable's threaded inner end through it with the brass adjusting nut (21) in front and the
  cable spring (22) and washers (23, 24) behind.
- cable (19): the outer from the front abutment A along the floor beside the tunnel, up the heel board ahead of
  the axle, over the right-hand tube (clip 29) and behind the bowl to the outer compensating lever; the inner on
  through to the inner lever. Clip 26 holds it under the floor.
- compensator: inner and outer compensating levers (14, 15) hanging from the fulcrum pin with the lever bush (16)
  between them, plain and anti-rattle washers (13, 17, 18), split pin; scissor action: cable inner and outer pull
  the levers' cable tabs together, each lever's tip pulls its rod outward (the left rod from lever 14, the right
  from 15).
- rods with forked ends, clevis pins (25) and split pins at both ends.
"""
from __future__ import annotations

import math

from build123d import Location, Part, Plane, Rot

from mgb import brake_layout as B, fasteners as F, rear_axle_layout as A, shapes as Sh
from mgb.brake_parts import (IN, box, chamfered_hex, flat_bar, lab, plain_washer, ring, rod, spring_washer, split_pin,
                             tube_rod, xcyl, xprism, ycyl, yprism, zc)
from mgb.poly2d import circle_pts, hull, rounded

PX, PY, PZ = B.HB_PIVOT
GX, _, GZ = B.HB_GRIP
TH = B.HB_HANDLE_T
TW = B.TUNNEL_SIDE_Y
PLATE_Y = (TW - B.HB_PLATE_T, TW)               # ratchet plate on the tunnel wall
WASH_T = 1.5
SPIGOT_R = 7.0
OPL = B.OP_LEVER_Y
TRUNNION = (PX, OPL, PZ - B.OP_LEVER_LEN)
CABLE_INNER_R = 1.6
CABLE_OUTER_R = 4.0


def _pt(r, a):
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


# =================================================================================================
# lever assembly (1-11)
# =================================================================================================
def _handle_path():
    """(x, z) centre line of the handle from the pivot to the grip end: forward, then cranked up to the grip."""
    return [(PX, PZ), (PX + 120.0, PZ + 10.0), (PX + 175.0, PZ + 55.0), (GX, GZ)]


def handle(spec) -> Part:
    pts = [(x, PY, z) for x, z in _handle_path()]
    h = flat_bar(pts, 22.0, TH, 40.0, up=(0, 1, 0))
    h = h + ycyl(16.0, PY - TH / 2, PY + TH / 2, PX, PZ)                      # rear end round the pivot
    h = h + ycyl(SPIGOT_R, PY + TH / 2 - 0.01, OPL - 9.0 + 0.01, PX, PZ)    # spigot welded through it
    s = SPIGOT_R * 0.75
    h = h + box(PX - s, PX + s, OPL - 9.0, OPL - 4.0 + 0.01, PZ - s, PZ + s)  # squared for the operating lever
    h = h + ycyl(3.97, OPL - 4.0, OPL + 6.0, PX, PZ)                        # threaded 5/16 end for the nut
    # pawl pivot pin (inner face) and the guide lugs for the pawl rod (outer face)
    px_, pz_ = PAWL_PIVOT
    h = h + ycyl(2.5, PY + TH / 2 - 0.01, PLATE_Y[0], px_, pz_)
    for xg in (PX + 70.0, PX + 140.0):
        zg = _z_on_handle(xg)
        h = h + box(xg - 4.0, xg + 4.0, PY - TH / 2 - 3.5, PY - TH / 2 + 0.01, zg + 5.0, zg + 11.0) - \
            xcyl(1.8, xg - 5, xg + 5, PY - TH / 2 - 2.0, zg + 8.0)
    return lab(h, spec)


def _z_on_handle(x):
    pts = _handle_path()
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def _grip_axis():
    (x0, z0), (x1, z1) = _handle_path()[-2:]
    d = (x1 - x0, 0.0, z1 - z0)
    L = math.hypot(d[0], d[2])
    return (x1, PY, z1), (d[0] / L, 0.0, d[2] / L)


def grip(spec) -> Part:
    """Item 3: moulded grip over the front of the handle, ribbed, open at the end for the knob."""
    L = spec.nom("length")
    e, d = _grip_axis()
    g = Sh.revolved([(9.5, -L), (13.0, -L + 4.0), (13.0, -6.0), (12.0, 0.0), (7.5, 0.0), (7.5, -6.0), (9.5, -10.0)])
    for k in range(8):
        g = g - ring(12.6, 14.0, -L + 12.0 + 9.0 * k, -L + 13.5 + 9.0 * k)
    g = g - box(-3.2, 3.2, -11.5, 11.5, -L - 1, -8.0)                     # slot for the flat handle
    return lab(Plane(origin=e, z_dir=d, x_dir=(0, 1, 0)).location * g, spec)


def knob(spec) -> Part:
    """Item 5: release button in the end of the grip."""
    e, d = _grip_axis()
    k = Sh.revolved([(0, -8.0), (6.8, -8.0), (6.8, 2.0), (6.0, 4.0), (0, 4.5)])
    return lab(Plane(origin=e, z_dir=d).location * k, spec)


def knob_spring(spec) -> Part:
    """Item 6: spring behind the knob inside the grip."""
    e, d = _grip_axis()
    s = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), 22.0, 6).moved(Location((0, 0, -30.0)))
    return lab(Plane(origin=e, z_dir=d, x_dir=(0, 1, 0)).location * s, spec)


def pawl_rod(spec) -> Part:
    """Item 4: rod from the knob back along the handle's outer face, through the guide lugs, hooked to the pawl."""
    e, d = _grip_axis()
    yo = PY - TH / 2 - 2.0
    tx, tz = PAWL_TAIL
    pts = [(e[0] - 30.0 * d[0], yo, e[2] - 30.0 * d[2]), (PX + 175.0, yo, PZ + 63.0), (PX + 140.0, yo, _z_on_handle(PX + 140.0) + 8.0),
           (PX + 70.0, yo, _z_on_handle(PX + 70.0) + 8.0), (tx + 6.0, yo, tz + 1.0), (tx, yo, tz), (tx, PAWL_Y[1], tz)]
    return lab(rod(pts, spec.nom("diameter") / 2, 6.0), spec)


PAWL_Y = (PY + TH / 2 + 0.05, PLATE_Y[0] - 0.05)          # in the plane of the ratchet sector, between handle and plate
PAWL_PIVOT = (PX + 42.0 * math.cos(math.radians(8.0)), PZ + 42.0 * math.sin(math.radians(8.0)))
PAWL_TAIL = (PX + 47.0 * math.cos(math.radians(22.0)), PZ + 47.0 * math.sin(math.radians(22.0)))
SECTOR = (30.0, 33.0, -5.0, 45.0)                         # teeth: root and tip radii about the pivot, angles from +x up


def pawl(spec) -> Part:
    """Item 7: pawl on its pin on the handle's inner side, its tooth on the ratchet sector (off position: the
    sector's lower end), the tail hooked to the pawl rod."""
    cx, cz = PAWL_PIVOT
    tx, tz = PAWL_TAIL
    tip = (PX + 33.3 * math.cos(math.radians(1.0)), PZ + 33.3 * math.sin(math.radians(1.0)))
    pts = circle_pts(cx, cz, 5.0, 16) + circle_pts(tx, tz, 3.2, 12) + circle_pts(tip[0], tip[1], 1.0, 8)
    p = yprism(hull(pts), *PAWL_Y) - ycyl(2.6, PAWL_Y[0] - 1, PAWL_Y[1] + 1, cx, cz) - ycyl(1.1, PAWL_Y[0] - 1, PAWL_Y[1] + 1, tx, tz)
    return lab(p, spec)


def ratchet_plate(spec) -> Part:
    """Item 9: plate on the tunnel wall: the spigot bush, three bolt lugs and the toothed sector, centred on the
    pivot, standing proud of the plate toward the handle in the pawl's plane."""
    y0, y1 = PLATE_Y
    out = rounded([(PX - 34.0, PZ - 40.0), (PX + 26.0, PZ - 40.0), (PX + 38.0, PZ + 4.0), (PX + 28.0, PZ + 30.0),
                   (PX - 30.0, PZ + 26.0)], 6.0, 3)
    p = yprism(out, y0, y1)
    p = p + ycyl(11.0, y1 - 0.01, y1 + 4.0, PX, PZ)                           # bush boss into the tunnel wall
    r0, r1, a0, a1 = SECTOR
    n = 20
    teeth = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        r = r1 if k % 2 == 0 else r0
        teeth.append((PX + r * math.cos(a), PZ + r * math.sin(a)))
    inner = [(PX + 22.0 * math.cos(math.radians(a1 - (a1 - a0) * k / 8)), PZ + 22.0 * math.sin(math.radians(a1 - (a1 - a0) * k / 8)))
             for k in range(9)]
    p = p + yprism(teeth + inner, PAWL_Y[0], y0 + 0.01)
    p = p - ycyl(SPIGOT_R + 0.3, y0 - 6, y1 + 6, PX, PZ)
    for x, z in ratchet_bolts():
        p = p - ycyl(3.3, y0 - 1, y1 + 1, x, z)
    return lab(p, spec)


def ratchet_bolts():
    return [(PX - 26.0, PZ - 32.0), (PX + 22.0, PZ - 32.0), (PX - 22.0, PZ + 15.0)]


def ratchet_bolt(spec) -> Part:
    return lab(F.hex_bolt("1/4", spec.nom("length") / IN), spec)


def lever_washer(which):
    """Items 8, 10: washers on the spigot (handle side of the plate, and inside the tunnel under the lever)."""
    def build(spec) -> Part:
        t = spec.nom("thickness")
        if which == "outer":
            y1 = PY + TH / 2 + t
            return lab(ycyl(12.0, PY + TH / 2, y1, PX, PZ) - ycyl(SPIGOT_R + 0.3, PY, y1 + 1, PX, PZ), spec)
        y0 = OPL - 4.0                                     # between the operating lever and its nut
        return lab(ycyl(9.0, y0, y0 + t, PX, PZ) - ycyl(4.2, y0 - 1, y0 + t + 1, PX, PZ), spec)
    return build


def operating_lever(spec) -> Part:
    """Item 11: on the spigot's square inside the tunnel, down to a fork carrying the trunnion."""
    y0, y1 = OPL - 9.0, OPL - 4.0
    tx, ty, tz = TRUNNION
    pts = circle_pts(PX, PZ, 12.0, 20) + circle_pts(tx, tz + 18.0, 9.0, 16)
    p = yprism(hull(pts), y0, y1)
    s = SPIGOT_R * 0.75 + 0.15
    p = p - box(PX - s, PX + s, y0 - 1, y1 + 1, PZ - s, PZ + s)
    fork = box(tx - 9.0, tx + 9.0, ty - 12.0, ty + 12.0, tz - 9.0, tz + 12.0) - box(tx - 10, tx + 10, ty - 7.5, ty + 7.5, tz - 10, tz + 8.0)
    fork = fork + box(tx - 9.0, tx + 9.0, y0, y1, tz + 8.0, tz + 22.0)
    p = p + fork - ycyl(4.1, ty - 13, ty + 13, tx, tz)
    return lab(p, spec)


def lever_nut(spec) -> Part:
    return lab(Location((PX, OPL - 4.0 + WASH_T, PZ)) * Rot(-90, 0, 0) * F.hex_nut("5/16"), spec)


def trunnion(spec) -> Part:
    """Item 20: pin in the operating lever's fork with the cable's cross hole."""
    tx, ty, tz = TRUNNION
    t = ycyl(4.0, ty - 7.4, ty + 7.4, tx, tz) + ycyl(5.0, ty - 13.5, ty - 12.0, tx, tz) + ycyl(5.0, ty + 12.0, ty + 13.5, tx, tz)
    t = t + ycyl(4.0, ty - 12.01, ty - 7.39, tx, tz) + ycyl(4.0, ty + 7.39, ty + 12.01, tx, tz)
    t = t - xcyl(CABLE_INNER_R + 0.6, tx - 6, tx + 6, ty, tz)
    return lab(t, spec)


def adjusting_nut(spec) -> Part:
    """Item 21: brass nut on the inner's threaded end, in front of the trunnion (Sec 4 para 2)."""
    tx, ty, tz = TRUNNION
    n = chamfered_hex(11.1, 8.0) - zc(2.4, -1, 9)
    return lab(Location((tx + 4.6, ty, tz)) * Rot(0, 90, 0) * n, spec)


def cable_spring(spec) -> Part:
    """Item 22: spring on the inner behind the trunnion, against washers 23, 24."""
    tx, ty, tz = TRUNNION
    ax = B.CABLE_ABUTMENT[0]
    L = tx - 6.0 - 1.5 - (ax + 8.0 + 1.5)
    s = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, L / 4.0)
    return lab(Location((ax + 8.0 + 1.5, ty, tz)) * Rot(0, 90, 0) * s, spec)


def cable_washer(which):
    def build(spec) -> Part:
        tx, ty, tz = TRUNNION
        t = spec.nom("thickness")
        x0 = tx - 6.0 - t if which == "front" else B.CABLE_ABUTMENT[0] + 8.0
        return lab(xcyl(6.0, x0, x0 + t, ty, tz) - xcyl(CABLE_INNER_R + 0.4, x0 - 1, x0 + t + 1, ty, tz), spec)
    return build


# =================================================================================================
# cable (19) and clips (26, 29)
# =================================================================================================
def comp_cable_points():
    """AF points of the cable tabs on the levers: Cb (outer's ferrule seat, outer lever) and Ca (inner end,
    inner lever)."""
    y0, z0 = A.BALANCE_PIVOT
    return (B.CABLE_X, y0 - 8.0, B.CABLE_Z), (B.CABLE_X, y0 + 8.0, B.CABLE_Z)


def outer_points():
    """Car-frame route of the cable outer from the front abutment A to the outer lever's tab."""
    ax, ay, az = B.CABLE_ABUTMENT
    fy, fz = B.CABLE_FLOOR
    cb, _ = comp_cable_points()
    cy = B.CABLE_CLIP_Y
    pts = [(ax, ay, az), (ax - 50.0, ay, az), (ax - 110.0, fy, fz), (A.AX + 420.0, fy, fz)]
    pts += [A.car(p) for p in [(170.0, cy + 40.0, 10.0), (60.0, cy, 58.0), (-20.0, cy, 58.0), (-85.0, cy + 60.0, 30.0),
                               (B.CABLE_X - 12.0, -150.0, B.CABLE_Z + 20.0), (B.CABLE_X, -70.0, B.CABLE_Z),
                               (cb[0], cb[1] - 6.0, cb[2])]]
    return pts


def cable(spec) -> Part:
    """Item 19 (outer): sheath with crimped ferrules at each end."""
    pts = outer_points()
    c = tube_rod(pts, CABLE_OUTER_R, CABLE_INNER_R + 0.3, 60.0)
    for a, b in ((pts[0], pts[1]), (pts[-1], pts[-2])):
        d = [b[i] - a[i] for i in range(3)]
        c = c + Plane(origin=a, z_dir=d).location * (zc(5.2, 0.0, 14.0) - zc(CABLE_INNER_R + 0.3, -1, 15))
    return lab(c, spec)


def cable_inner(spec) -> Part:
    """Item 19 (inner): the exposed ends: the threaded front end from the abutment through the trunnion and nut,
    and the rear end from the outer lever's tab across to the inner lever's tab with its nipple."""
    tx, ty, tz = TRUNNION
    ax = B.CABLE_ABUTMENT[0]
    f = xcyl(CABLE_INNER_R, ax - 2.0, tx + 22.0, ty, tz)
    cb, ca = comp_cable_points()
    r = ycyl(CABLE_INNER_R * 0.8, cb[1] - 8.0, ca[1] + 2.0, cb[0], cb[2]) + ycyl(3.2, ca[1] + 1.5, ca[1] + 8.0, ca[0], ca[2])
    return lab(f + A.AF * r, spec)


def floor_clip(spec) -> Part:
    """Item 26: P-clip round the outer under the floor (P11 screws it to the floor), behind the abutment."""
    ax, ay, az = B.CABLE_ABUTMENT
    fy, fz = B.CABLE_FLOOR
    x = A.AX + 900.0
    c = xcyl(CABLE_OUTER_R + 1.4, x - 6, x + 6, fy, fz) - xcyl(CABLE_OUTER_R + 0.1, x - 7, x + 7, fy, fz)
    c = c + box(x - 6, x + 6, fy - 1.0, fy + 1.0, fz + CABLE_OUTER_R, fz + CABLE_OUTER_R + 12.0)
    c = c + box(x - 6, x + 6, fy - 1.0, fy + 16.0, fz + CABLE_OUTER_R + 10.5, fz + CABLE_OUTER_R + 12.0)
    c = c - zc(2.6, fz, fz + 20, x, fy + 9.0)
    return lab(c, spec)


def axle_clip(spec) -> Part:
    """Item 29: clip round the right-hand tube holding the outer on top of it."""
    y = B.CABLE_CLIP_Y
    w = spec.nom("width")
    band = Location((0, y + w / 2, 0)) * Rot(90, 0, 0) * ring(A.TUBE_R, A.TUBE_R + 1.2, 0.0, w)
    xs = 20.0
    loop = ycyl(CABLE_OUTER_R + 1.4, y - w / 2, y + w / 2, xs, 58.0) - ycyl(CABLE_OUTER_R + 0.1, y - w, y + w, xs, 58.0)
    web = box(xs - 2.5, xs + 2.5, y - w / 2, y + w / 2, A.TUBE_R - 1.0, 58.0 - CABLE_OUTER_R) - ycyl(A.TUBE_R, y - w, y + w, 0, 0)
    return lab(A.AF * (band + loop + web), spec)


# =================================================================================================
# compensator (12-18) on P7's fulcrum pin, rods and clevis pins (25)
# =================================================================================================
Y0, Z0 = A.BALANCE_PIVOT


def comp_lever(which):
    """Items 14, 15: plate hanging from the pin, its tip splayed to the rod's fork pin, a tab bent across to the
    cable line (the inner lever's tab takes the inner's nipple, the outer lever's the outer's ferrule)."""
    def build(spec) -> Part:
        x0, x1 = B.COMP_LEVER_X[which]
        tip = B.comp_tip(which)
        cb, ca = comp_cable_points()
        c = ca if which == "inner" else cb
        pts = circle_pts(Y0, Z0, 12.0, 20) + circle_pts(tip[1], tip[2], 7.0, 16) + circle_pts(c[1], c[2], 6.0, 12)
        from mgb.brake_parts import xprism as xp
        L = xp(hull(pts), x0, x1)
        L = L - xcyl(6.35 + 0.25, x0 - 1, x1 + 1, Y0, Z0) - xcyl(4.1, x0 - 1, x1 + 1, tip[1], tip[2])
        # tab across to the cable line (thickness along y), slotted for the inner
        tx0, tx1 = (min(x0, B.CABLE_X - 6.0), max(x1, B.CABLE_X + 6.0))
        tab = box(tx0, tx1, c[1] - 1.25, c[1] + 1.25, c[2] - 7.0, c[2] + 7.0)
        tab = tab - box(B.CABLE_X - 1.9, B.CABLE_X + 1.9, c[1] - 2, c[1] + 2, c[2] - 8.0, c[2] + 0.1) - \
            ycyl(CABLE_INNER_R + 0.3, c[1] - 2, c[1] + 2, B.CABLE_X, c[2])
        return lab(A.AF * (L + tab), spec)
    return build


def comp_bush(spec) -> Part:
    """Item 16: bush between the levers on the pin."""
    x0, x1 = B.COMP_LEVER_X["inner"][0], B.COMP_LEVER_X["outer"][1]
    return lab(A.AF * (xcyl(10.0, x1, x0, Y0, Z0) - xcyl(6.6, x1 - 1, x0 + 1, Y0, Z0)), spec)


def comp_washer(which):
    """Items 13 (between the boss and the inner lever), 17 (anti-rattle) and 18 (outside the outer lever)."""
    def build(spec) -> Part:
        t = spec.nom("thickness")
        x_in = B.COMP_LEVER_X["inner"][1]
        x_out = B.COMP_LEVER_X["outer"][0]
        x0 = {"inner": x_in, "anti-rattle": x_out - t, "outer": x_out - 2 * t}[which]
        x1 = x0 + t if which != "inner" else -104.0
        lo, hi = min(x0, x1), max(x0, x1)
        w = xcyl(10.5, lo, hi, Y0, Z0) - xcyl(6.6, lo - 1, hi + 1, Y0, Z0)
        if which == "anti-rattle":
            w = w - box(lo - 1, hi + 1, Y0 + 6.0, Y0 + 11.0, Z0 - 0.6, Z0 + 0.6)
        return lab(A.AF * w, spec)
    return build


def comp_split_pin(spec) -> Part:
    L = spec.nom("length")
    return lab(A.AF * Location((-129.0, Y0 + L / 2 + 1.0, Z0)) * Rot(90, 0, 0) * split_pin(spec.nom("diameter"), L), spec)


def _fork(p, rod_dir, pin_axis, gap):
    """Forked rod end at pin centre p: two cheeks either side of the pin across `gap`, a boss on the rod side."""
    fr = Plane(origin=p, z_dir=pin_axis, x_dir=rod_dir).location
    f = box(-8.0, 26.0, -6.5, 6.5, -gap / 2 - 3.0, gap / 2 + 3.0) - box(-9.0, 9.0, -7, 7, -gap / 2, gap / 2)
    f = f + zc(6.5, -gap / 2 - 3.0, -gap / 2) + zc(6.5, gap / 2, gap / 2 + 3.0)
    f = f - zc(4.1, -gap, gap)
    f = f + Location((26.0, 0, 0)) * Rot(0, 90, 0) * zc(5.0, 0.0, 12.0)
    return fr * f


def rod_points(side):
    """AF: (compensator pin, wheel lever pin) for the left (side 1) or right rod."""
    tip = B.comp_tip("inner" if side > 0 else "outer")
    hx, hy, hz = B.HB_LEVER_END
    return tip, (hx, side * hy, hz)


def brake_rod(side):
    def build(spec) -> Part:
        a, b = rod_points(side)
        d = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(c * c for c in d))
        u = [c / L for c in d]
        r = spec.nom("diameter") / 2
        body = Plane(origin=a, z_dir=u).location * zc(r, 30.0, L - 30.0)
        fa = _fork(a, u, (1, 0, 0), 5.6)
        fb = _fork(b, [-c for c in u], (0, 0, 1), 5.6)
        # locknut on the adjustable (wheel) end
        nut = Plane(origin=b, z_dir=[-c for c in u]).location * (chamfered_hex(11.1, 6.0, 38.5) - zc(3.2, 37, 46))
        return lab(A.AF * (body + fa + fb + nut), spec)
    return build


def clevis_pin(where):
    """Item 25: clevis pin with its split pin hole: at the compensator (pin along x) or a wheel lever (along z)."""
    def build(spec) -> Part:
        L = spec.nom("length")
        p = Sh.revolved([(0, -L / 2), (3.95, -L / 2), (3.95, L / 2), (6.0, L / 2), (6.0, L / 2 + 2.2), (0, L / 2 + 2.2)])
        p = p - Location((0, 0, -L / 2 + 2.2)) * Rot(90, 0, 0) * zc(0.9, -6, 6)
        return lab(p, spec)
    return build


def rod_split_pin(spec) -> Part:
    return lab(split_pin(spec.nom("diameter"), spec.nom("length")), spec)


PARTS = {
    "brakes.handbrake.handle": {"build": handle},
    "brakes.handbrake.grip": {"build": grip},
    "brakes.handbrake.pawl-rod": {"build": pawl_rod},
    "brakes.handbrake.knob": {"build": knob},
    "brakes.handbrake.knob-spring": {"build": knob_spring},
    "brakes.handbrake.pawl": {"build": pawl},
    "brakes.handbrake.washer-handle": {"build": lever_washer("outer")},
    "brakes.handbrake.ratchet-plate": {"build": ratchet_plate},
    "brakes.handbrake.ratchet-bolt": {"build": ratchet_bolt},
    "brakes.handbrake.washer-lever": {"build": lever_washer("inner")},
    "brakes.handbrake.operating-lever": {"build": operating_lever},
    "brakes.handbrake.lever-nut": {"build": lever_nut},
    "brakes.handbrake.trunnion": {"build": trunnion},
    "brakes.handbrake.adjusting-nut": {"build": adjusting_nut},
    "brakes.handbrake.cable-spring": {"build": cable_spring},
    "brakes.handbrake.cable-washer-front": {"build": cable_washer("front")},
    "brakes.handbrake.cable-washer-rear": {"build": cable_washer("rear")},
    "brakes.handbrake.cable": {"build": cable},
    "brakes.handbrake.cable-inner": {"build": cable_inner},
    "brakes.handbrake.floor-clip": {"build": floor_clip},
    "brakes.handbrake.axle-clip": {"build": axle_clip},
    "brakes.handbrake.comp-lever-inner": {"build": comp_lever("inner")},
    "brakes.handbrake.comp-lever-outer": {"build": comp_lever("outer")},
    "brakes.handbrake.comp-bush": {"build": comp_bush},
    "brakes.handbrake.comp-washer-inner": {"build": comp_washer("inner")},
    "brakes.handbrake.comp-anti-rattle-washer": {"build": comp_washer("anti-rattle")},
    "brakes.handbrake.comp-washer-outer": {"build": comp_washer("outer")},
    "brakes.handbrake.comp-split-pin": {"build": comp_split_pin},
    "brakes.handbrake.rod-lh": {"build": brake_rod(1)},
    "brakes.handbrake.rod-rh": {"build": brake_rod(-1)},
    "brakes.handbrake.clevis-pin": {"build": clevis_pin("any")},
    "brakes.handbrake.rod-split-pin": {"build": rod_split_pin},
}
