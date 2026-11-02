"""Rear drum brakes, Lockheed 10 x 1.75 in, on the banjo axle with wire wheels (Haynes Ch 9 Fig 9.9 items 1-26,
Secs 3, 13-15, printed p148, 151-154; photos 13.3, 13.4).

Every part is drawn in the axle frame (mgb.rear_axle_layout AF) at the left-hand (near side) wheel, |y|
outward. The assembly turns the fore-and-aft symmetric parts half round z for the right-hand wheel; the
handed parts (backplate, handbrake lever and its boot) have right-hand versions built as mirror images.

Forms:
- backplate (1): a pressing with a flat centre on the axle flange (four bolt holes), a raised annular face the
  shoes ride on with six pressed shoe platforms, radial stiffening ribs, and a rim turned back into the drum
  mouth; holes for the steady pins, the adjuster (wedge and two studs), the wheel cylinder neck and the
  handbrake lever (Fig 9.9, photo 13.3).
- shoes (5): a T-section of table and web, the bonded lining on the table, the web tips square to the
  tappet and piston slots, holes for the pull-off springs and the steady pin, a notch for the handbrake lever.
- adjuster (11-15): a cast body on the backplate with the two tappets in a cross bore and the wedge screwed
  in from behind with a square head (Sec 3 para 3, photo 3.3), two studs with nuts and spring washers.
- wheel cylinder (16-21): a cast body with a flat base on the backplate, the bore along the car with a
  piston, seal and boot at each end, the slot through which the handbrake lever passes, and a neck through the
  backplate carrying the pipe inlet and bleed screw, held by the E-clip (MGOC 17H7949).
- drum (24): cast iron with its mounting plate on the hub extension (four stud holes, the screw holes), a
  stiffening band at the mouth and ribs round the barrel; drum nuts (26) on the hub studs (wire wheels).
"""
from __future__ import annotations

import math

from build123d import Box, Location, Part, Plane, Rot, Solid, Wire, Face, extrude

from mgb import brake_layout as B, fasteners as F, probes, rear_axle_layout as A, shapes as Sh
from mgb.brake_parts import (bore, IN, box, chamfered_hex, flat_bar, hexp, lab, mirror_y, nyloc, ring, rod, spring_washer,
                             tension_spring, xcyl, xrev, ycyl, yprism, yrev, zc)
from mgb.poly2d import circle_pts, hull


def _pt(r, a):
    """(x, z) at radius r, angle a from up toward the front."""
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


def _offset(points, d):
    """Offset an open (r, y) polyline by d to its left (mitred corners)."""
    out = []
    n = len(points)
    norms = []
    for i in range(n - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        norms.append((-(y1 - y0) / L, (x1 - x0) / L))
    for i in range(n):
        if i == 0:
            nx, ny = norms[0]
        elif i == n - 1:
            nx, ny = norms[-1]
        else:
            ax, ay = norms[i - 1]
            bx, by = norms[i]
            sx, sy = ax + bx, ay + by
            L = math.hypot(sx, sy)
            sx, sy = sx / L, sy / L
            k = 1.0 / max(sx * ax + sy * ay, 0.3)
            nx, ny = sx * k, sy * k
        out.append((points[i][0] + nx * d, points[i][1] + ny * d))
    return out


def _arc_band(r0, r1, a0, a1, y0, y1, n=40):
    """Annular sector between radii r0, r1 and angles a0..a1 (from up toward the front), from y0 to y1."""
    pts = [_pt(r1, a0 + (a1 - a0) * k / n) for k in range(n + 1)] + [_pt(r0, a1 - (a1 - a0) * k / n) for k in range(n + 1)]
    return yprism(pts, y0, y1)


# =================================================================================================
# backplate (1)
# =================================================================================================
def _backplate_left():
    inner = list(B.BP_PROFILE)
    outer = _offset(inner, B.BP_T)                      # toward +y (the shoe side) for a profile running outward
    prof = inner + list(reversed(outer))
    p = yrev(prof)
    # shoe platforms (six) on the raised face, with the radial stiffening ribs between them on the back
    for a in B.PLATFORM_ANGLES + [360.0 - a for a in B.PLATFORM_ANGLES]:
        x, z = _pt(101.0, a)
        pl = Location((x, B.PLATEAU_Y - 0.2, z)) * Rot(0, -a, 0) * Rot(-90, 0, 0) * \
            Sh.slot_plate(22.0, 11.0, B.PLATFORM_H + 0.2)
        p = p + pl
    for a in (65.0, 115.0, 245.0, 295.0, 18.0, 342.0):
        x0, z0 = _pt(93.5, a)
        x1, z1 = _pt(109.0, a)
        p = p + rod([(x0, 581.0, z0), (x1, 581.0, z1)], 2.6, 1.0) - rod([(x0, 581.0 + B.BP_T, z0), (x1, 581.0 + B.BP_T, z1)], 2.4 - 0.9, 1.0)
    # a stiffening bead round the flat centre
    y1 = B.BP_FACE_Y + B.BP_T
    p = p + yrev([(67.0, y1 - 0.5), (73.0, y1 - 0.5), (71.5, y1 + 2.0), (68.5, y1 + 2.0)])
    # holes
    p = p - ycyl(30.0, 550, 600)
    for a in A.BACKPLATE_BOLT_ANGLES:
        x, z = _pt(A.BACKPLATE_BOLT_PCD / 2, a)
        p = p - ycyl(5.0, 550, 600, x, z)
    for s in (1, -1):
        p = p - ycyl(2.7, 560, 600, s * B.STEADY_R, 0.0)
        p = p - ycyl(3.4, 560, 600, s * B.ADJ_STUD_X, B.ADJ_Z)
    p = p - ycyl(4.6, 560, 600, 0.0, B.ADJ_Z)
    nx, nz = B.WC_NECK
    p = p - box(-nx / 2 - 0.6, nx / 2 + 0.6, 560, 600, B.WC_Z - nz / 2 - 0.6, B.WC_Z + nz / 2 + 0.6)
    hx, hz = B.HB_SLOT
    p = p - box(hx - 7.0, hx + 7.0, 560, 600, hz - 4.0, hz + 4.0)
    return p


def backplate(side):
    def b(spec) -> Part:
        p = _backplate_left()
        return lab(p if side > 0 else mirror_y(p), spec)
    return b


def backplate_bolt(spec) -> Part:
    """Item 2: 3/8 UNF x 2 in (MGOC BH606161); head on the backplate, shank inboard through the axle flange
    (drawn along +z from the head's underside)."""
    return lab(F.hex_bolt("3/8", spec.nom("length") / IN), spec)


def backplate_nut(spec) -> Part:
    return lab(nyloc("3/8"), spec)


def backplate_spring_washer(spec) -> Part:
    return lab(spring_washer("3/8")[0], spec)


# =================================================================================================
# shoes (5) and linings
# =================================================================================================
def shoe(spec) -> Part:
    """Front shoe (left-hand wheel): table, web and the holes; drawn in AF."""
    a0, a1 = B.SHOE_TIPS
    t = _arc_band(B.TABLE_R[0], B.TABLE_R[1], a0 + 2.0, a1 - 2.0, B.LINING_Y[0], B.LINING_Y[1])
    # web: inner edge 84 mm from the centre, tips square to the tappet and piston slots
    n = 40
    outer = [_pt(B.TABLE_R[0] + 0.3, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
    inner = []
    for k in range(n + 1):
        a = a1 - (a1 - a0) * k / n
        edge = min(a - a0, a1 - a)
        r_in = 84.0 + max(0.0, 10.0 - edge) * 1.0              # a little shallower at the tips
        inner.append(_pt(r_in, a))
    w = yprism(outer + inner, B.WEB_Y[0], B.WEB_Y[1])
    s = t + w
    # pull-off spring holes, steady pin hole, notches for the handbrake lever
    for (x, z) in (B.SPRING_TOP, (B.SPRING_BOT[0], B.SPRING_BOT[1])):
        s = s - ycyl(1.6, 580, 600, x, z)
    s = s - ycyl(2.6, 580, 600, B.STEADY_R, 0.0)
    for a in (26.6, 153.4):
        x, z = _pt(111.8, a)
        s = s - (Location((x, B.WEB_MID_Y, z)) * Box(16.0, 12.0, 12.0))
    # web tips cut square where they sit in the piston and tappet slots
    x0 = _piston_x0()
    s = s - box(-60.0, x0 + B.PISTON_L - 4.5, B.WEB_Y[0] - 1, B.WEB_Y[1] + 1, B.WC_Z - 16.0, B.WC_Z + 16.0)
    s = s - box(-60.0, x0 + B.PISTON_L - 4.5, B.WEB_Y[0] - 1, B.WEB_Y[1] + 1, B.ADJ_Z - 12.0, B.ADJ_Z + 12.0)
    return lab(s, spec)


def lining(spec) -> Part:
    a0, a1 = B.LINING_ARC
    l = _arc_band(B.LINING_R[0], B.LINING_R[1], a0, a1, B.LINING_Y[0], B.LINING_Y[1], 60)
    return lab(l, spec)


# =================================================================================================
# pull-off springs (6, 7), steady pins, springs and washers (8-10)
# =================================================================================================
def pull_off_spring(which):
    def b(spec) -> Part:
        x, z = B.SPRING_TOP if which == "adjuster" else B.SPRING_BOT
        s = tension_spring((-x, B.SPRING_Y, z), (x, B.SPRING_Y, z), spec.nom("wire_diameter"), spec.nom("outside_diameter"))
        # hooks pass through the webs
        for sx in (-x, x):
            s = s + ycyl(spec.nom("wire_diameter") / 2, B.WEB_Y[0] - 0.5, B.SPRING_Y, sx, z)
        return lab(s, spec)
    return b


def steady_pin(spec) -> Part:
    """Item 8: flat head behind the backplate, shank through the web, flattened T end the cup washer turns on
    (drawn at the front shoe: x = +STEADY_R)."""
    y_head = 581.0
    L = spec.nom("length")
    p = ycyl(4.5, y_head - 1.6, y_head, B.STEADY_R, 0.0) + ycyl(1.6, y_head - 0.01, y_head + L, B.STEADY_R, 0.0)
    p = p + box(B.STEADY_R - 3.4, B.STEADY_R + 3.4, y_head + L - 1.2, y_head + L, -1.1, 1.1)
    return lab(p, spec)


STEADY_CUP_Y = B.WEB_Y[1] + 8.0


def steady_spring(spec) -> Part:
    """Item 9: short conical-ended compression spring between the web and the cup washer."""
    L = STEADY_CUP_Y - B.WEB_Y[1]
    c = Sh.coil_spring(spec.nom("wire_diameter"), spec.nom("outside_diameter"), L, 4.0, end_turns=0.6)
    return lab(Location((B.STEADY_R, B.WEB_Y[1], 0.0)) * Rot(-90, 0, 0) * c, spec)


def steady_washer(spec) -> Part:
    """Item 10: cup washer with the slot the pin's T end turns into."""
    d = spec.nom("diameter")
    c = Sh.revolved([(0, 0), (d / 2, 0), (d / 2, 2.4), (d / 2 - 0.8, 2.4), (d / 2 - 0.8, 0.8), (0, 0.8)])
    c = c - Box(7.2, 2.6, 6.0) - zc(1.8, -1, 4)
    c = c + (Box(3.0, 2.0, 0.8).moved(Location((0, 2.2, 1.2))) + Box(3.0, 2.0, 0.8).moved(Location((0, -2.2, 1.2))))
    return lab(Location((B.STEADY_R, STEADY_CUP_Y, 0.0)) * Rot(-90, 0, 0) * c, spec)


# =================================================================================================
# adjuster (11-15)
# =================================================================================================
ADJ_Y0 = B.PLATEAU_Y


def adjuster_body(spec) -> Part:
    L, H, D = B.ADJ_BODY
    zc_ = B.ADJ_Z
    b = box(-L / 2, L / 2, ADJ_Y0, ADJ_Y0 + D, zc_ - H / 2, zc_ + H / 2)
    b = b + box(-L / 2 - 3.0, L / 2 + 3.0, ADJ_Y0, ADJ_Y0 + 3.0, zc_ - H / 2 - 1.0, zc_ + H / 2 + 1.0)     # foot flange
    b = b + ycyl(7.5, ADJ_Y0, ADJ_Y0 + D + 2.0, 0.0, zc_)                               # boss for the wedge
    # cross bore for the tappets, at the web level
    b = b - xcyl(4.6, -L / 2 - 4, L / 2 + 4, B.WEB_MID_Y, zc_)
    b = b - box(-L / 2 - 4, L / 2 + 4, B.WEB_MID_Y - 3.0, B.WEB_MID_Y + 3.0, zc_ - 4.6, zc_ + 4.6)
    b = b - ycyl(3.2, ADJ_Y0 - 1.0, B.WEB_MID_Y + 6.0, 0.0, zc_)                         # wedge thread
    # two studs out the back
    for s in (1, -1):
        b = b + ycyl(3.1, 572.0, ADJ_Y0 + 0.01, s * B.ADJ_STUD_X, zc_)
    return lab(b, spec)


def tappet(spec) -> Part:
    """Item 12: round plunger in the cross bore, inclined inner face on the wedge, slotted outer end for the
    shoe web (front tappet drawn; the rear is turned half round z about the adjuster centre)."""
    L = spec.nom("length")
    x0 = 3.0
    t = xcyl(4.4, x0, x0 + L, B.WEB_MID_Y, B.ADJ_Z)
    t = t - (Location((x0, B.WEB_MID_Y, B.ADJ_Z)) * Rot(0, 0, 0) * Rot(0, 45, 0) * Box(4.0, 12.0, 12.0))  # wedge face
    t = t - box(x0 + L - 5.0, x0 + L + 1, B.WEB_Y[0] - 0.3, B.WEB_Y[1] + 0.3, B.ADJ_Z - 6, B.ADJ_Z + 6)   # web slot
    return lab(t, spec)


def wedge(spec) -> Part:
    """Item 13: the adjuster screw: square head behind the backplate, threaded shank, conical point between the
    tappets."""
    h0, h1 = B.ADJ_WEDGE_HEAD_Y
    sq = spec.nom("square")
    w = box(-sq / 2, sq / 2, h0, h1, B.ADJ_Z - sq / 2, B.ADJ_Z + sq / 2)
    w = w + ycyl(3.15, h1 - 0.01, B.WEB_MID_Y - 4.0, 0.0, B.ADJ_Z)
    w = w + Location((0, B.WEB_MID_Y - 4.0, B.ADJ_Z)) * Rot(-90, 0, 0) * Sh.revolved([(0, 0), (4.2, 0), (1.0, 6.0), (0, 6.0)])
    for k in range(10):                                                                # thread
        y = ADJ_Y0 - 6.0 + k * 1.0
        w = w - Location((0, y, B.ADJ_Z)) * Rot(-90, 0, 0) * ring(2.8, 3.5, 0, 0.45)
    return lab(w, spec)


def adjuster_nut(spec) -> Part:
    n = F.hex_nut("1/4")
    return lab(n, spec)


def adjuster_spring_washer(spec) -> Part:
    return lab(spring_washer("1/4")[0], spec)


# =================================================================================================
# wheel cylinder (16-21)
# =================================================================================================
def wc_body(spec) -> Part:
    r = B.WC_BODY_R
    zc_, yc = B.WC_Z, B.WC_AXIS_Y
    L = B.WC_HALF_L
    b = xcyl(r, -L, L, yc, zc_) & box(-L - 1, L + 1, B.PLATEAU_Y, yc + r + 1, zc_ - r - 1, zc_ + r + 1)
    b = b + box(-L + 4.0, L - 4.0, B.PLATEAU_Y, yc, zc_ - r, zc_ + r)                   # flat base on the backplate
    for s in (1, -1):                                                                   # end lips the boots grip
        b = b + (xcyl(r + 1.2, s * L - (2.0 if s > 0 else 0.0), s * L + (0.0 if s > 0 else 2.0), yc, zc_)
                 & box(-L - 3, L + 3, B.PLATEAU_Y, yc + r + 3, zc_ - r - 3, zc_ + r + 3))
    nx, nz = B.WC_NECK
    b = b + box(-nx / 2, nx / 2, B.WC_NECK_END_Y, B.PLATEAU_Y + 0.01, zc_ - nz / 2, zc_ + nz / 2)
    b = b - box(-nx / 2 - 1, nx / 2 + 1, B.WC_CLIP_Y, B.WC_CLIP_Y + 1.6, zc_ - nz / 2 - 1, zc_ - nz / 2 + 1.2)   # clip groove
    b = b - box(-nx / 2 - 1, nx / 2 + 1, B.WC_CLIP_Y, B.WC_CLIP_Y + 1.6, zc_ + nz / 2 - 1.2, zc_ + nz / 2 + 1)
    b = b + ycyl(6.5, B.WC_NECK_END_Y - 4.0, B.WC_NECK_END_Y + 0.01, 0.0, B.WC_INLET_Z)   # inlet boss
    b = b + zc(5.5, zc_ + nz / 2 - 0.01, zc_ + nz / 2 + 7.0, 0.0, B.WC_BLEED_Y)          # bleed boss
    # bore, lever slot, ports
    b = b - xcyl(B.WC_BORE / 2, -L - 1, L + 1, yc, zc_)
    b = b - box(-L - 1, L + 1, B.HB_LEVER_Y - 5.5, yc + r + 2, zc_ - 3.0, zc_ + 3.0)
    for s in (1, -1):                                                                   # lever pivot pins
        b = b + zc(2.4, zc_ - 3.1, zc_ + 3.1, s * abs(B.HB_LEVER_PIVOT[0]), B.HB_LEVER_Y)
    b = b - ycyl(4.65, B.WC_NECK_END_Y - 5.0, B.WC_NECK_END_Y + 6.0, 0.0, B.WC_INLET_Z)
    b = b - ycyl(1.2, B.WC_NECK_END_Y, yc, 0.0, B.WC_INLET_Z)
    b = b - zc(3.1, zc_ + nz / 2 - 6.0, zc_ + nz / 2 + 7.1, 0.0, B.WC_BLEED_Y)
    return lab(b, spec)


def _piston_x0():
    return B.WC_HALF_L - B.PISTON_L + 8.0          # pistons stand 8 mm out of the body for the boots and shoe slots


def _groove():
    x0 = _piston_x0()
    return x0 + B.PISTON_L - 7.0, x0 + B.PISTON_L - 5.5


def wc_piston(spec) -> Part:
    """Item 17: piston, the outer end slotted for the shoe web (front piston drawn)."""
    r = spec.nom("diameter") / 2
    x0 = _piston_x0()
    p = xcyl(r, x0, x0 + B.PISTON_L, B.WC_AXIS_Y, B.WC_Z)
    g0, g1 = _groove()
    p = p - xcyl(r + 1, g0, g1, B.WC_AXIS_Y, B.WC_Z) + xcyl(r - 1.2, g0 - 0.1, g1 + 0.1, B.WC_AXIS_Y, B.WC_Z)   # boot groove
    p = p - box(x0 + B.PISTON_L - 5.0, x0 + B.PISTON_L + 1, B.WEB_Y[0] - 0.4, B.WEB_Y[1] + 0.4, B.WC_Z - r - 1, B.WC_Z + r + 1)
    p = p - box(x0 - 1, x0 + B.PISTON_L + 1, B.HB_LEVER_Y - 5.5, B.WC_AXIS_Y + r + 1, B.WC_Z - 3.0, B.WC_Z + 3.0)
    return lab(p, spec)


def wc_seal(spec) -> Part:
    """Item 18: cup seal, sealing lip toward the centre of the cylinder (Sec 14 para 4)."""
    r = B.WC_BORE / 2
    x0 = _piston_x0()
    s = xrev([(0.0, x0 - 4.0), (r - 1.0, x0 - 4.0), (r, x0 - 4.6), (r, x0 + 0.0), (0.0, x0 + 0.0)])
    s = s - xrev([(0.0, x0 - 4.7), (r - 2.0, x0 - 4.7), (r - 2.0, x0 - 3.0), (0.0, x0 - 3.0)])
    s = s.moved(Location((0, B.WC_AXIS_Y, B.WC_Z)))
    s = s - box(x0 - 6, x0 + 1, B.HB_LEVER_Y - 5.5, B.WC_AXIS_Y + r + 1, B.WC_Z - 3.0, B.WC_Z + 3.0)
    return lab(s, spec)


def wc_boot(spec) -> Part:
    """Item 19: rubber boot from the body's lip to the piston's groove."""
    L = B.WC_HALF_L
    r = B.WC_BODY_R
    x0 = _piston_x0()
    pr = B.WC_BORE / 2
    g0, g1 = _groove()
    o = xrev([(r + 1.3, L - 3.0), (r + 2.6, L - 3.0), (r + 2.6, L + 1.0), (pr + 2.2, g1 + 1.2), (pr - 1.2, g1 + 1.2),
              (pr - 1.2, g0), (pr + 0.9, g0), (r + 1.3, L + 0.2)])
    o = o.moved(Location((0, B.WC_AXIS_Y, B.WC_Z)))
    o = o - box(L - 4, g1 + 3, B.HB_LEVER_Y - 5.5, B.WC_AXIS_Y + r + 4, B.WC_Z - 3.0, B.WC_Z + 3.0)
    o = o - box(g0 - 1.0, g1 + 3, B.WEB_Y[0] - 0.4, B.WEB_Y[1] + 0.4, B.WC_Z - 30, B.WC_Z + 30)
    return lab(o, spec)


def wc_clip(spec) -> Part:
    """Item 20: E-clip (MGOC 17H7949) behind the backplate's raised face, its two legs in the neck's grooves."""
    nx, nz = B.WC_NECK
    t = spec.nom("thickness")
    zc_ = B.WC_Z
    y0, y1 = B.WC_CLIP_Y, B.WC_CLIP_Y + t
    c = box(-17.0, 17.0, y0, y1, zc_ - nz / 2 - 3.0, zc_ + nz / 2 + 3.0)
    c = c - box(-nx / 2 + 1.0, nx / 2 - 1.0, y0 - 1, y1 + 1, zc_ - nz / 2 - 0.5, zc_ + nz / 2 + 4.0)    # open top
    c = c - box(-nx / 2 - 0.3, nx / 2 + 0.3, y0 - 1, y1 + 1, zc_ - nz / 2 + 1.2, zc_ + nz / 2 + 4.0)
    for sx in (-1, 1):
        c = c - ycyl(2.0, y0 - 1, y1 + 1, sx * 14.0, zc_ + nz / 2 + 0.5)                           # plier holes
    return lab(c, spec)


def wc_bleed_screw(spec) -> Part:
    """Item 21: 1/4 UNF bleed screw (MGOC 513118): thread, hex, nipple."""
    zc_ = B.WC_Z + B.WC_NECK[1] / 2
    s = zc(3.1, zc_ - 5.0, zc_ + 7.0) + chamfered_hex(7.9, 5.0, zc_ + 7.0) + zc(2.5, zc_ + 12.0, zc_ + 19.0)
    s = s + Sh.revolved([(1.0, zc_ + 14.0), (3.0, zc_ + 14.0), (2.5, zc_ + 16.0), (1.0, zc_ + 16.0)])
    s = s - zc(0.9, zc_ - 6.0, zc_ + 20.0)
    return lab(s.moved(Location((0, B.WC_BLEED_Y, 0))), spec)


# =================================================================================================
# handbrake lever (22) and its boot (23)
# =================================================================================================
def _lever_left():
    pts = [(x, y, B.WC_Z) for x, y in B.HB_LEVER_PATH]
    l = flat_bar(pts, 10.0, 5.0, 6.0, up=(0, 0, 1))
    hx, hy, hz = B.HB_LEVER_END
    l = l + zc(7.0, hz - 2.5, hz + 2.5, hx, hy)
    l = l - zc(4.1, hz - 4, hz + 4, hx, hy)
    px, pz = B.HB_LEVER_PIVOT
    l = l + zc(5.5, pz - 2.5, pz + 2.5, px, B.HB_LEVER_Y) - zc(2.5, pz - 4, pz + 4, px, B.HB_LEVER_Y)
    return l


def hb_lever(side):
    def b(spec) -> Part:
        l = _lever_left()
        return lab(l if side > 0 else mirror_y(l), spec)
    return b


def _boot_left():
    hx, hz = B.HB_SLOT
    y0, y1 = 566.0, 576.0
    o = None
    for k, (w, h) in enumerate(((18.0, 13.0), (15.0, 11.0), (16.5, 12.0), (13.5, 9.5), (12.0, 8.5))):
        ya = y1 - k * (y1 - y0) / 5
        yb = ya - (y1 - y0) / 5 - 0.01
        seg = box(hx - w / 2, hx + w / 2, yb, ya, hz - h / 2, hz + h / 2)
        o = seg if o is None else o + seg
    o = o - box(hx - 5.6, hx + 5.6, y0 - 1, y1 + 1, hz - 3.0, hz + 3.0)
    return o


def hb_lever_boot(side):
    def b(spec) -> Part:
        o = _boot_left()
        return lab(o if side > 0 else mirror_y(o), spec)
    return b


# =================================================================================================
# drum (24) and drum nuts (26)
# =================================================================================================
def drum(spec) -> Part:
    R = spec.nom("internal_diameter") / 2
    y0 = B.DRUM_MOUTH_Y
    p0, p1 = B.DRUM_PLATE_Y
    Ro = B.DRUM_OUT_R
    prof = [(R, y0), (Ro + 3.5, y0), (Ro + 3.5, y0 + 7.0), (Ro, y0 + 9.0), (Ro, p1 - 4.0), (Ro - 4.0, p1),
            (37.0, p1), (37.0, p0), (R - 2.0, p0), (R, p0 - 2.0)]
    d = yrev(prof)
    for yr in (583.0, 597.0):                                                           # ribs round the barrel
        d = d + yrev([(Ro - 0.5, yr), (Ro + 2.5, yr + 1.5), (Ro + 2.5, yr + 4.5), (Ro - 0.5, yr + 6.0)])
    for a in A.STUD_ANGLES:
        x, z = _pt(A.STUD_PCD / 2, a)
        d = d - ycyl(6.9, p0 - 1, p1 + 1, x, z)
    for a in (0.0, 180.0):                                                              # drum screw holes (disc wheels)
        x, z = _pt(A.STUD_PCD / 2, a)
        d = d - ycyl(3.3, p0 - 1, p1 + 1, x, z)
    return lab(d, spec)


def drum_nut(spec) -> Part:
    """Item 26: 1/2 UNF self-locking nut on each hub stud (wire wheels; MGOC GHF225), seat at z = 0."""
    return lab(nyloc("1/2"), spec)


PARTS = {
    "brakes.rear.backplate-lh": {"build": backplate(1)},
    "brakes.rear.backplate-rh": {"build": backplate(-1)},
    "brakes.rear.backplate-bolt": {"build": backplate_bolt, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "brakes.rear.backplate-nut": {"build": backplate_nut},
    "brakes.rear.backplate-spring-washer": {"build": backplate_spring_washer},
    "brakes.rear.shoe": {"build": shoe},
    "brakes.rear.lining": {"build": lining, "probes": {"width": lambda p: probes.bbox_size(p, "y")}},
    "brakes.rear.pull-off-spring-cylinder": {"build": pull_off_spring("cylinder")},
    "brakes.rear.pull-off-spring-adjuster": {"build": pull_off_spring("adjuster")},
    "brakes.rear.steady-pin": {"build": steady_pin},
    "brakes.rear.steady-spring": {"build": steady_spring},
    "brakes.rear.steady-washer": {"build": steady_washer},
    "brakes.rear.adjuster-body": {"build": adjuster_body},
    "brakes.rear.tappet": {"build": tappet},
    "brakes.rear.wedge": {"build": wedge},
    "brakes.rear.adjuster-nut": {"build": adjuster_nut},
    "brakes.rear.adjuster-spring-washer": {"build": adjuster_spring_washer},
    "brakes.rear.wheel-cylinder": {"build": wc_body, "probes": {"bore": lambda p: _bore(p, B.WC_BORE / 2)}},
    "brakes.rear.wc-piston": {"build": wc_piston, "probes": {"diameter": lambda p: bore(p, B.WC_BORE / 2)}},
    "brakes.rear.wc-seal": {"build": wc_seal},
    "brakes.rear.wc-boot": {"build": wc_boot},
    "brakes.rear.wc-clip": {"build": wc_clip},
    "brakes.rear.wc-bleed-screw": {"build": wc_bleed_screw},
    "brakes.rear.hb-lever-lh": {"build": hb_lever(1)},
    "brakes.rear.hb-lever-rh": {"build": hb_lever(-1)},
    "brakes.rear.hb-lever-boot-lh": {"build": hb_lever_boot(1)},
    "brakes.rear.hb-lever-boot-rh": {"build": hb_lever_boot(-1)},
    "brakes.rear.drum": {"build": drum, "probes": {"internal_diameter": lambda p: _bore(p, B.DRUM_R)}},
    "brakes.rear.drum-nut": {"build": drum_nut},
}


_bore = bore
