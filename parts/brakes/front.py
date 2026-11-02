"""Front disc brakes, Lockheed two-piston calipers on 10.75 in discs (Haynes Ch 9 Figs 9.6-9.8 items 1-18, Secs 8,
10-12, printed p146, 149-151), with the flexible hose, its locking plate, nut and washer (Fig 9.1 item 4, Sec 8).

Drawn in the left-hand front hub frame of mgb.front_suspension_layout (origin on the wheel axis at the car
centre line, car axes, |y| outward). Round parts (pistons, seals, fasteners) are drawn at the origin along +z
and placed by the assembly; the caliper halves, dust cover and hose bracket are handed: the right-hand
versions are mirror images.

Forms:
- disc (1): a hat - the centre plate with four bolt holes stands outboard (Fig 9.7), the hat wall runs back to
  the swept ring, with a heat groove where they meet and chamfered edges.
- caliper (8, Fig 9.8): two cast halves bolted together across the disc by two bridge bolts; each half a
  cylinder block (54 mm bore, the fluid seal groove and the dust seal recess in its mouth, a raised boss on
  its back), cheeks either side of the pad aperture that guide the pads, bridge bosses over the disc edge, a
  ridge carrying the pad retaining pins; the mounting half has the two tapped mounting lugs, the hose union
  and the bleed screw boss, the rim half the plug (14); the fluid crosses the joint through a sealed port
  (MGOC 17H7679 bridge seal).
- pistons (9) with the relieved face toward the hub (Fig 9.6, Sec 10 para 4), fluid seals (10), dust seals and
  retainers (11), pads (12) with anti-squeal shims (MGOC ASV101), the retaining spring clip (13) and two split
  pins (18), bleed screw (15), plug (14), caliper bolts (16) and tab washer (17).
- dust cover (5): a dished stone guard with an open sector round the caliper, pressed radial ribs and a rolled
  rim, three screws and spring washers (6, 7).
"""
from __future__ import annotations

import math

from build123d import Box, Location, Part, Plane, Rot, Torus

from mgb import fasteners as F, front_suspension_layout as L, probes, shapes as Sh
from mgb.brake_parts import (bore, IN, box, chamfered_hex, hexp, lab, lobes, mirror_y, ring, rod, spring_washer, tube_rod,
                             xcyl, xprism, ycyl, yprism, yrev, zc, zprism)
from mgb.poly2d import circle_pts, hull, rounded

DM = L.DISC_MID_Y


def _pt(r, a):
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


def P(u, v):
    """(x, z) in the hub frame of caliper coordinates u (radius, rearward) and v (up)."""
    return L.uv(u, v)


def ucyl(r, y0, y1, u, v):
    x, z = P(u, v)
    return ycyl(r, y0, y1, x, z)


def ubox(u0, u1, v0, v1, y0, y1):
    return box(-u1, -u0, y0, y1, v0, v1)


# =================================================================================================
# disc (1) and its fixings (2-4)
# =================================================================================================
def disc(spec) -> Part:
    R = spec.nom("diameter") / 2
    t = spec.nom("thickness")
    f0, f1 = DM - t / 2, DM + t / 2
    h0, h1 = L.HAT_R
    p0 = L.DISC_FACE_Y - L.DISC_PLATE_T
    prof = [(L.DISC_BORE_R, p0), (L.DISC_BORE_R, L.DISC_FACE_Y), (h1 - 2.0, L.DISC_FACE_Y), (h1, L.DISC_FACE_Y - 2.0),
            (h1, f1 + 3.0), (h1 + 3.0, f1), (R - 0.8, f1), (R, f1 - 0.8), (R, f0 + 0.8), (R - 0.8, f0), (h0, f0),
            (h0, p0 - 1.5), (h0 - 1.5, p0)]
    d = yrev(prof)
    d = d - yrev([(h1 + 4.0, f1 + 0.01), (h1 + 7.0, f1 + 0.01), (h1 + 5.5, f1 - 1.2)])          # heat groove
    for a in L.DISC_BOLT_ANGLES:
        x, z = _pt(L.DISC_BOLT_PCD / 2, a)
        d = d - ycyl(5.0, p0 - 1, L.DISC_FACE_Y + 1, x, z)
    return lab(d, spec)


def disc_bolt(spec) -> Part:
    return lab(F.hex_bolt(L.DISC_BOLT, spec.nom("length") / IN), spec)


def disc_spring_washer(spec) -> Part:
    return lab(spring_washer(L.DISC_BOLT)[0], spec)


def disc_nut(spec) -> Part:
    return lab(F.hex_nut(L.DISC_BOLT), spec)


# =================================================================================================
# dust cover (5) and its screws (6, 7)
# =================================================================================================
def _shield_left():
    y0 = L.SHIELD_FACE_Y
    T = L.SHIELD_T
    prof = [(45.0, y0), (76.0, y0), (92.0, y0 + 9.0), (128.0, y0 + 9.0), (132.0, y0 + 11.0), (133.5, y0 + 15.0),
            (133.5 - T, y0 + 15.0), (130.8, y0 + 11.6), (127.5, y0 + 9.0 + T), (91.4, y0 + 9.0 + T), (75.4, y0 + T),
            (45.0, y0 + T)]
    s = yrev(prof)
    for a in (20.0, 65.0, 110.0, 155.0, 200.0):                     # pressed radial ribs
        x0, z0 = _pt(96.0, a)
        x1, z1 = _pt(124.0, a)
        s = s + rod([(x0, y0 + 9.0 + T, z0), (x1, y0 + 9.0 + T, z1)], 2.4, 1.0) - \
            rod([(x0, y0 + 9.0, z0), (x1, y0 + 9.0, z1)], 1.3, 1.0)
    # open sector round the caliper
    a0, a1 = L.SHIELD_GAP
    pts = [(0.0, 0.0)] + [_pt(160.0, a0 + (a1 - a0) * k / 12) for k in range(13)]
    s = s - (yprism(pts, y0 - 5, y0 + 20) - ycyl(50.0, y0 - 6, y0 + 21))
    for a in L.SHIELD_SCREW_ANGLES:
        x, z = _pt(L.SHIELD_SCREW_R, a)
        s = s - ycyl(4.2, y0 - 1, y0 + 3, x, z)
    return s


def dust_cover(side):
    def b(spec) -> Part:
        s = _shield_left()
        return lab(s if side > 0 else mirror_y(s), spec)
    return b


def shield_screw(spec) -> Part:
    return lab(F.hex_bolt("5/16", spec.nom("length") / IN), spec)


def shield_washer(spec) -> Part:
    return lab(spring_washer("5/16")[0], spec)


# =================================================================================================
# caliper halves (8)
# =================================================================================================
MOUTH = L.BORE_MOUTH
HALF_OUT = MOUTH + L.HALF_DEPTH                     # |dy| of each half's outer face
BV = 54.0                                           # half body width
PAD_HALF = 36.6                                     # pad aperture, either side of the centre
BBV = 46.0                                          # bridge bolts
SEAL_GROOVE = (12.0, 15.6)                          # |dy| from the mouth inward... (distance into the bore)
TRANSFER = (132.0, -46.0)                           # (u, v) of the fluid transfer port across the joint
CLIP_T = 0.8                                        # pad retaining spring clip (spec)
PAD_TOP_U = L.PISTON_R_AT + L.PAD_H / 2 + 4.0       # top of the pads' lugs, where the clip bears
PIN_U = PAD_TOP_U + CLIP_T + 1.6 + 0.1              # pad retaining pins just over the clip (D: Fig 9.7, Sec 10 para 2)


def _half_left():
    """Mounting half (inboard), in the hub frame. The rim half is built from it."""
    y_out, y_m, y_j = DM - HALF_OUT, DM - MOUTH, DM
    u0, u1 = L.BODY_U
    b0, b1 = L.BRIDGE_U
    pu, pv = L.PISTON_R_AT, 0.0
    # cylinder block: rounded outline in (u, v)
    outline = rounded([(u0, -BV), (u1, -BV), (u1, BV), (u0, BV)], 9.0, 4)
    blk = yprism([P(u, v) for u, v in outline], y_out, y_m)
    blk = blk + ucyl(24.0, y_out - 3.0, y_out + 0.01, pu, pv)                              # boss on the back
    # cheeks guiding the pads, bridge over the disc edge, bridge bolt bosses, pin ridge
    for s in (1, -1):
        blk = blk + yprism([P(u, v) for u, v in rounded([(u0 + 30.0, s * PAD_HALF), (b1, s * PAD_HALF), (b1, s * BV),
                                                          (u0 + 30.0, s * BV)], 3.0, 2)], y_m - 0.01, y_j)
        blk = blk + ucyl(9.0, y_out + 6.0, y_j, L.BRIDGE_BOLT_U, s * BBV)
    blk = blk + yprism([P(u, v) for u, v in rounded([(u1 - 1.0, -24.0), (u1 + 6.0, -24.0), (u1 + 6.0, 24.0), (u1 - 1.0, 24.0)], 3.0, 2)],
                       y_out + 0.01, y_m)                                                  # ridge carrying the pad pins
    blk = blk + yprism([P(u, v) for u, v in [(b0, -BV), (b1, -BV), (b1, BV), (b0, BV)]], y_m - 6.0, y_m)  # bridge web outer
    blk = blk - yprism([P(u, v) for u, v in [(b0 - 30.0, -PAD_HALF), (b1 + 1, -PAD_HALF), (b1 + 1, PAD_HALF), (b0 - 30.0, PAD_HALF)]],
                       y_m - 6.5, y_j + 1)
    # bore, fluid seal groove, dust seal recess
    blk = blk - ucyl(L.PISTON_D / 2, y_m - L.BORE_DEPTH, y_m + 1, pu, pv)
    blk = blk - ucyl(L.PISTON_D / 2 + 3.2, y_m - SEAL_GROOVE[1], y_m - SEAL_GROOVE[0], pu, pv)
    blk = blk - ucyl(L.PISTON_D / 2 + 3.6, y_m - 5.5, y_m + 1, pu, pv)
    # bridge bolt holes (tapped 7/16 UNF here), pad pin holes, transfer port with the seal recess
    for s in (1, -1):
        blk = blk - ucyl(4.95, y_out + 10.0, y_j + 1, L.BRIDGE_BOLT_U, s * BBV)
        blk = blk - ucyl(1.7, y_out - 1.0, y_j + 1, PIN_U, s * L.PIN_V)
    tu, tv = TRANSFER
    blk = blk - ucyl(1.5, y_m - L.BORE_DEPTH + 3.0, y_j + 1, tu, tv)
    blk = blk - ucyl(4.6, y_j - 1.5, y_j + 1, tu, tv)
    return blk


def caliper_mounting_half_left():
    blk = _half_left()
    y_out = DM - HALF_OUT
    # mounting lugs, tapped 7/16 UNF from the inboard face
    for s in (1, -1):
        lug = yprism([P(u, v) for u, v in rounded([(L.LUG_U[0], s * L.LUG_V - 11.0), (L.BODY_U[0] + 6.0, s * L.LUG_V - 13.0),
                                                    (L.BODY_U[0] + 6.0, s * L.LUG_V + 13.0), (L.LUG_U[0], s * L.LUG_V + 11.0)], 4.0, 3)],
                     L.CALIPER_MOUNT_FACE_Y, DM - MOUTH - 2.0)
        blk = blk + lug
        blk = blk - ucyl(4.95, L.CALIPER_MOUNT_FACE_Y - 1, DM - MOUTH - 4.0, L.LUG_U[0] + 8.0, s * L.LUG_V)
    # hose union on the inboard face, bleed screw boss on top
    iu, iv = L.INLET
    blk = blk + ucyl(8.5, y_out - 6.0, y_out + 0.01, iu, iv)
    blk = blk - ucyl(4.4, y_out - 7.0, y_out + 6.0, iu, iv) - ucyl(1.4, y_out, DM - MOUTH - L.BORE_DEPTH + 2, iu, iv)
    x, z = P(118.0, BV)
    blk = blk + zc(6.8, z - 2.0, z + 7.0, x, L.BLEED_Y)
    blk = blk - zc(4.4, z - 4.0, z + 7.1, x, L.BLEED_Y) - zc(1.2, z - 18.0, z, x, L.BLEED_Y)
    return blk


def caliper_rim_half_left():
    blk = _half_left()
    y_out = DM - HALF_OUT
    # clearance for the bridge bolts with spot faces for their heads (bolts go in from the rim side)
    for s in (1, -1):
        blk = blk - ucyl(5.8, y_out - 1, DM + 1, L.BRIDGE_BOLT_U, s * BBV)
        blk = blk - ucyl(9.5, y_out - 1, y_out + 6.0, L.BRIDGE_BOLT_U, s * BBV)
    tu, tv = TRANSFER
    blk = blk + ucyl(4.6, DM - 1.5, DM + 0.01, tu, tv) - ucyl(1.5, DM - 2.0, DM + 1.0, tu, tv)  # no recess this side
    x, z = P(118.0, BV)
    blk = blk + zc(6.8, z - 2.0, z + 7.0, x, L.BLEED_Y)
    blk = blk - zc(4.4, z - 4.0, z + 7.1, x, L.BLEED_Y)
    # turn it to the outboard side of the disc
    return Location((0, 2 * DM, 0)) * blk.mirror(Plane.XZ)


def caliper_half(which, side):
    def b(spec) -> Part:
        p = caliper_mounting_half_left() if which == "mounting" else caliper_rim_half_left()
        return lab(p if side > 0 else mirror_y(p), spec)
    return b


# =================================================================================================
# round caliper parts: drawn along +z from the origin; the assembly points +z at the disc
# =================================================================================================
def piston(spec) -> Part:
    """Item 9: hollow piston, open end on the pad, its rim relieved on the hub side (local +x; Fig 9.6)."""
    r = spec.nom("diameter") / 2
    Lp = L.PISTON_L
    p = Sh.revolved([(0, 0), (r - 0.6, 0), (r, 0.6), (r, Lp - 0.6), (r - 0.6, Lp), (r - 4.0, Lp), (r - 4.0, 5.0), (0, 5.0)])
    p = p - (Location((r - 2.0, 0, Lp)) * Rot(0, 0, 0) * Box(10.0, 30.0, 3.0))           # the relieved face
    return lab(p, spec)


def fluid_seal(spec) -> Part:
    """Item 10: square-section seal in the bore groove."""
    r = L.PISTON_D / 2
    return lab(ring(r - 0.3, r + 3.1, 0.0, SEAL_GROOVE[1] - SEAL_GROOVE[0] - 0.2), spec)


def dust_seal(spec) -> Part:
    """Item 11 (seal): rubber wiper between the retainer and the piston."""
    r = L.PISTON_D / 2
    return lab(Sh.revolved([(r - 0.3, 0.0), (r + 2.4, 0.0), (r + 2.4, 3.6), (r + 0.6, 4.6), (r - 0.3, 4.6)]), spec)


def dust_seal_retainer(spec) -> Part:
    """Item 11 (retainer): pressed steel ring holding the dust seal in the mouth of the bore."""
    r = L.PISTON_D / 2
    return lab(Sh.revolved([(r + 2.5, 0.0), (r + 3.6, 0.0), (r + 3.6, 5.3), (r + 0.4, 5.3), (r + 0.4, 4.7), (r + 2.5, 4.7)]), spec)


def _pad_outline():
    w, h = L.PAD_W / 2, L.PAD_H / 2
    u0 = L.PISTON_R_AT
    pts = [(u0 - h, -w + 6.0), (u0 - h + 6.0, -w), (u0 + h, -w), (u0 + h, -14.0), (u0 + h + 4.0, -10.0), (u0 + h + 4.0, 10.0),
           (u0 + h, 14.0), (u0 + h, w), (u0 - h + 6.0, w), (u0 - h, w - 6.0)]
    return [P(u, v) for u, v in pts]


def pad(spec) -> Part:
    """Item 12 (backing plate): steel plate with a lug on its top edge the clip bears on; inboard pad drawn (its
    lining face toward +y on the disc)."""
    t = L.PAD_BACK_T
    y1 = DM - L.PAD_FACE - L.PAD_LINING_T
    return lab(yprism(_pad_outline(), y1 - t, y1), spec)


def pad_lining(spec) -> Part:
    t = spec.nom("thickness")
    y1 = DM - L.PAD_FACE
    w, h = L.PAD_W / 2 - 1.5, L.PAD_H / 2 - 1.5
    u0 = L.PISTON_R_AT
    out = rounded([(u0 - h, -w), (u0 + h, -w), (u0 + h, w), (u0 - h, w)], 4.0, 3)
    l = yprism([P(u, v) for u, v in out], y1 - t, y1)
    l = l - box(-200, 200, y1 - 3.0, y1 + 1, -1.2, 1.2)                                    # wear slot
    return lab(l, spec)


def shim(spec) -> Part:
    """Anti-squeal shim (MGOC ASV101) behind the inboard pad, with its locating tab (arrow) upward."""
    t = spec.nom("thickness")
    y1 = DM - L.PAD_FACE - L.PAD_LINING_T - L.PAD_BACK_T
    w, h = L.PAD_W / 2 - 2.0, L.PAD_H / 2 - 2.0
    u0 = L.PISTON_R_AT
    pts = [(u0 - h, -w), (u0 + h, -w), (u0 + h, -6.0), (u0 + h + 6.0, 0.0), (u0 + h, 6.0), (u0 + h, w), (u0 - h, w)]
    return lab(yprism([P(u, v) for u, v in pts], y1 - t, y1), spec)


def pad_clip(spec) -> Part:
    """Item 13: spring steel clip lying across the tops of both pads' lugs under the two retaining pins, with a
    raised bridge over the disc between the pads."""
    from mgb.brake_parts import flat_bar
    t = spec.nom("thickness")
    u = PAD_TOP_U + t / 2
    y0, y1 = DM - MOUTH + 0.6, DM + MOUTH - 0.6
    pts = [(-u, y0, 0.0), (-u, DM - 6.0, 0.0), (-(u + 2.5), DM - 3.0, 0.0), (-(u + 2.5), DM + 3.0, 0.0), (-u, DM + 6.0, 0.0),
           (-u, y1, 0.0)]
    c = flat_bar(pts, 30.0, t, 1.5, up=(1, 0, 0))
    return lab(c, spec)


def pad_pin(spec) -> Part:
    """Item 18: split pin through both halves above the pads (drawn along +z from the eye)."""
    from mgb.brake_parts import split_pin
    return lab(split_pin(spec.nom("diameter"), spec.nom("length")), spec)


def bridge_bolt(spec) -> Part:
    return lab(F.hex_bolt(L.BRIDGE_BOLT, spec.nom("length") / IN), spec)


def bridge_seal(spec) -> Part:
    """MGOC 17H7679: small rubber ring sealing the fluid port across the joint face."""
    return lab(ring(1.6, 4.5, 0.0, 1.5), spec)


def bleed_screw(spec) -> Part:
    """Item 15: 3/8 UNF bleed screw (MGOC 3H2428), seat at z = 0."""
    s = Sh.revolved([(0, -9.0), (2.6, -9.0), (4.6, -6.5), (4.6, 0.0), (0, 0.0)]) + chamfered_hex(9.5, 5.5, 0.0) + zc(3.0, 5.5, 13.0)
    s = s + Sh.revolved([(1.2, 8.0), (3.6, 8.0), (3.0, 10.0), (1.2, 10.0)])
    s = s - zc(1.0, -10.0, 14.0)
    return lab(s, spec)


def bleed_cap(spec) -> Part:
    c = zc(4.6, 7.0, 15.0) - zc(3.1, 6.5, 13.5) + Sh.revolved([(0, 15.0), (4.4, 15.0), (3.2, 16.4), (0, 16.6)])
    return lab(c, spec)


def plug(spec) -> Part:
    """Item 14: 3/8 UNF plug in the unused bleed hole, seat at z = 0."""
    p = zc(4.6, -8.0, 0.01) + chamfered_hex(9.5, 5.0, 0.0)
    return lab(p, spec)


def caliper_bolt(spec) -> Part:
    return lab(F.hex_bolt(L.CALIPER_BOLT, spec.nom("length") / IN), spec)


def tab_washer(spec) -> Part:
    """Item 17: two-hole lock tab under both caliper bolt heads, ears turned up against the flats; drawn in the
    hub frame on the inboard face of the swivel axle's caliper flange."""
    t = spec.nom("thickness")
    y1 = L.CALIPER_MOUNT_FACE_Y - L.SWIVEL_CALIPER_FLANGE_T
    uc = L.LUG_U[0] + 8.0
    outline = [P(u, v) for u, v in rounded([(uc - 9.0, -L.LUG_V - 9.0), (uc + 9.0, -L.LUG_V - 9.0), (uc + 9.0, L.LUG_V + 9.0),
                                            (uc - 9.0, L.LUG_V + 9.0)], 4.0, 3)]
    w = yprism(outline, y1 - t, y1)
    for s in (1, -1):
        w = w - ucyl(5.8, y1 - 2, y1 + 1, uc, s * L.LUG_V)
        w = w + ubox(uc + 8.0, uc + 8.0 + t, s * L.LUG_V - 4.0, s * L.LUG_V + 4.0, y1 - 9.0, y1 - t + 0.01)      # ear
    return lab(w, spec)


# =================================================================================================
# flexible hose (Sec 8; Fig 9.1 item 4) and its bracket on the body
# =================================================================================================
def _inlet_out():
    """Car-frame-free: hub-frame point and direction of the caliper union (pointing inboard)."""
    iu, iv = L.INLET
    x, z = P(iu, iv)
    return (x, DM - HALF_OUT - 6.0, z)


BRK_T = 2.5


def hose(spec, side=1) -> Part:
    """Flexible hose: crimped male end screwed into the caliper with a copper washer; the hose; the top end with
    its hex under the bracket and the threaded neck up through it, female for the pipe's union nut."""
    hx, hy, hz = L.HOSE_BRACKET
    hx -= L.FX
    hz -= L.FZ
    x0, y0, z0 = _inlet_out()
    r = spec.nom("outside_diameter") / 2
    # bottom end fitting along -y from the union face
    bot = ycyl(4.6, y0 + 1.2, y0 + 10.0, x0, z0) + Location((x0, y0 - 0.01, z0)) * Rot(90, 0, 0) * chamfered_hex(14.3, 11.0)
    bot = bot + ycyl(6.2, y0 - 33.0, y0 - 10.5, x0, z0)
    # top end fitting below and through the bracket
    top = zc(6.2, hz - 46.0, hz - 21.0, hx, hy) + chamfered_hex(15.9, 13.0, hz - 21.0).moved(Location((hx, hy, 0))) + \
        zc(5.5, hz - 8.01, hz + BRK_T + 14.0, hx, hy)
    top = top - zc(2.6, hz - 10.0, hz + BRK_T + 15.0, hx, hy)
    pts = [(x0, y0 - 32.0, z0), (x0, y0 - 60.0, z0 + 10.0), (hx, hy, hz - 110.0), (hx, hy, hz - 45.0)]
    h = rod(pts, r, 40.0) + bot + top
    return lab(h if side > 0 else mirror_y(h), spec)


def hose_copper_washer(spec) -> Part:
    x0, y0, z0 = _inlet_out()
    t = spec.nom("thickness")
    return lab(ycyl(7.0, y0, y0 + t, x0, z0) - ycyl(4.7, y0 - 1, y0 + t + 1, x0, z0), spec)


def _bracket_left():
    hx, hy, hz = L.HOSE_BRACKET
    hx -= L.FX
    hz -= L.FZ
    b = box(hx - 14.0, hx + 14.0, hy - 16.0, hy + 26.0, hz, hz + BRK_T)                     # shelf the hose end goes through
    b = b + box(hx - 14.0, hx + 14.0, hy + 26.0 - BRK_T, hy + 26.0, hz, hz + 34.0)          # flange welded to the valance
    for sx in (-1, 1):                                                                      # gussets
        x0 = hx + (12.0 if sx > 0 else -14.0)
        b = b + xprism([(hy + 6.0, hz + BRK_T - 0.01), (hy + 26.0 - BRK_T + 0.01, hz + BRK_T - 0.01),
                        (hy + 26.0 - BRK_T + 0.01, hz + 24.0)], x0, x0 + 2.0)
    b = b - zc(5.7, hz - 1, hz + BRK_T + 1, hx, hy)
    b = b - box(hx - 2.0, hx + 2.0, hy - 17.0, hy - 5.0, hz - 1, hz + BRK_T + 1)           # locking plate slot
    return b


def hose_bracket(side):
    def b(spec) -> Part:
        p = _bracket_left()
        return lab(p if side > 0 else mirror_y(p), spec)
    return b


def locking_plate(spec) -> Part:
    """Fig 9.1 item 4: square plate on the hose end's flats under the bracket so the hose cannot twist."""
    hx, hy, hz = L.HOSE_BRACKET
    hx -= L.FX
    hz -= L.FZ
    t = spec.nom("thickness")
    p = box(hx - 11.0, hx + 11.0, hy - 11.0, hy + 11.0, hz - t, hz) - (hexp(16.1, t + 2, hz - t - 1).moved(Location((hx, hy, 0))))
    p = p + box(hx - 2.0, hx + 2.0, hy - 15.0, hy - 6.0, hz - t, hz + BRK_T)                # tongue into the bracket's slot
    return lab(p, spec)


def hose_locknut(spec) -> Part:
    hx, hy, hz = L.HOSE_BRACKET
    hx -= L.FX
    hz -= L.FZ
    z0 = hz + BRK_T + 1.5
    return lab((chamfered_hex(15.9, 6.4, z0) - zc(5.6, z0 - 1, z0 + 8)).moved(Location((hx, hy, 0))), spec)


def hose_lockwasher(spec) -> Part:
    hx, hy, hz = L.HOSE_BRACKET
    hx -= L.FX
    hz -= L.FZ
    z0 = hz + BRK_T
    w = ring(5.7, 9.5, z0, z0 + 1.5)
    for k in range(10):
        w = w - (Location((0, 0, z0 + 1.2)) * Rot(0, 0, 36 * k) * Location((8.5, 0, 0)) * Box(2.5, 1.0, 1.0))
    return lab(w.moved(Location((hx, hy, 0))), spec)


PARTS = {
    "brakes.front.disc": {"build": disc, "probes": {"diameter": lambda p: probes.bbox_size(p, "x"),
                                                     "thickness": lambda p: _disc_t(p)}},
    "brakes.front.disc-bolt": {"build": disc_bolt},
    "brakes.front.disc-spring-washer": {"build": disc_spring_washer},
    "brakes.front.disc-nut": {"build": disc_nut},
    "brakes.front.dust-cover-lh": {"build": dust_cover(1)},
    "brakes.front.dust-cover-rh": {"build": dust_cover(-1)},
    "brakes.front.dust-cover-screw": {"build": shield_screw, "probes": {"length": lambda p: p.bounding_box().max.Z}},
    "brakes.front.dust-cover-spring-washer": {"build": shield_washer},
    "brakes.front.caliper-mounting-half-lh": {"build": caliper_half("mounting", 1), "probes": {"bore": lambda p: _bore(p, L.PISTON_D / 2)}},
    "brakes.front.caliper-mounting-half-rh": {"build": caliper_half("mounting", -1), "probes": {"bore": lambda p: _bore(p, L.PISTON_D / 2)}},
    "brakes.front.caliper-rim-half-lh": {"build": caliper_half("rim", 1)},
    "brakes.front.caliper-rim-half-rh": {"build": caliper_half("rim", -1)},
    "brakes.front.bridge-bolt": {"build": bridge_bolt},
    "brakes.front.bridge-seal": {"build": bridge_seal},
    "brakes.front.piston": {"build": piston, "probes": {"diameter": lambda p: probes.bbox_size(p, "y")}},
    "brakes.front.fluid-seal": {"build": fluid_seal},
    "brakes.front.dust-seal": {"build": dust_seal},
    "brakes.front.dust-seal-retainer": {"build": dust_seal_retainer},
    "brakes.front.pad": {"build": pad},
    "brakes.front.pad-lining": {"build": pad_lining},
    "brakes.front.anti-squeal-shim": {"build": shim},
    "brakes.front.pad-clip": {"build": pad_clip},
    "brakes.front.pad-pin": {"build": pad_pin},
    "brakes.front.bleed-screw": {"build": bleed_screw},
    "brakes.front.bleed-cap": {"build": bleed_cap},
    "brakes.front.plug": {"build": plug},
    "brakes.front.caliper-bolt": {"build": caliper_bolt},
    "brakes.front.tab-washer": {"build": tab_washer},
    "brakes.front.hose": {"build": hose},
    "brakes.front.hose-copper-washer": {"build": hose_copper_washer},
    "brakes.front.hose-bracket-lh": {"build": hose_bracket(1)},
    "brakes.front.hose-bracket-rh": {"build": hose_bracket(-1)},
    "brakes.front.locking-plate": {"build": locking_plate},
    "brakes.front.hose-locknut": {"build": hose_locknut},
    "brakes.front.hose-lockwasher": {"build": hose_lockwasher},
}


_bore = bore


def _disc_t(p):
    ys = sorted({round(f.center().Y, 4) for f in p.faces() if f.geom_type.name == "PLANE" and abs(abs(f.normal_at().Y) - 1) < 1e-6
                 and f.bounding_box().size.X > 250})
    return ys[-1] - ys[0] if len(ys) >= 2 else 0.0
