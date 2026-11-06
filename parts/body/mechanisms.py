"""Door, bonnet and boot mechanisms (Haynes Ch 12; printed pages 222-232): the window regulator in each door (Fig
12.15 early Sports Tourer, Fig 12.17: regulator plate with its quadrant, pinion and spindle, lift arm and
extension arm with their studs in the glass's lower channel, balance spring, arm stop and buffer, the extension's
pivot plate), the door lock with its operating link and remote control (Fig 12.13 items 1-22: lock 15, operating
link 16, remote control lock 12 with its anti-rattle sleeve 13, tension spring 18, spring clips 17), the lock housing
and barrel below the side strip (items 3-6), the chrome finisher on the door top's rear end, the striker's packing and tapping plate (items 10, 11), the door check
strap, the interior door pull (item 8) and the trim pad's clips, the door aperture seals; the bonnet's lock (Sec 6:
lock plate with its spring catch and control cable to the pull knob under the facia, the safety catch on the bonnet)
and its prop stay in its clip (photos 13, 28); the boot lid's stay in its clip, lock and striker (Sec 25, Fig 12.12)
and the boot aperture seal.

Positions follow the doors' and panels' own geometry (mgb.body_shell_layout, parts.body.closures): the glass is
shown raised, the doors, bonnet and boot lid closed. Hide body.doors.skin-* and body.interior.door-card-* in the Parts
tree to see the door mechanisms. Shapes derived (D) from the Haynes figures, Oliver's photos 08, 11, 13, 14, 28 and
the regulators and locks sold for early pull-handle cars (MGOC, Moss: AHH5810 regulator, BHH1009 lock pattern).
"""
from __future__ import annotations

import math

from build123d import Compound, Location, Rot

from mgb import body_geom as G, body_shell as B, body_shell_layout as S, cockpit_layout as CK
from mgb.chassis_geom import box, rod, swept_rod, xcyl, xprism, ycyl, yprism, zcyl, zprism
from mgb.shapes import coil_spring
from parts.body import closures as C
from parts.body import structure as St

H = S.z_of
T = 1.2


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


def _side(p, side):
    from build123d import Plane
    return p if side > 0 else p.mirror(Plane.XZ)


def ybox(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


# ---------------------------------------------------------------------------------------------------------------------
# door frame of reference (left door; the right is mirrored): the inner panel's cavity face, the glass
# ---------------------------------------------------------------------------------------------------------------------
def inner_y(x, h):
    """|y| of the door inner panel's outer face (the cavity side): 72 mm inboard of the skin."""
    return S.side_y(x, h) - C.DOOR_IN + 0.2


GLASS_BOTTOM_H = 520.0                           # the glass's lower edge, raised (closures.glass_outline)
STUD_H = 530.0                                   # the arms' studs in the lower channel
STUDS_X = (-1215.0, -1470.0)                     # front stud (extension arm), rear stud (lift arm)
SPINDLE = CK.WINDER                              # winder spindle (interior.winder; at the door's front, Oliver's kf131)
QUAD_PIVOT = (SPINDLE[0] - 70.0, SPINDLE[1] - 90.0)   # quadrant and lift arm pivot on the regulator plate
EXT_PIVOT = (-1470.0, 430.0)                     # the extension arm's pivot plate (Fig 12.15 item 5)
ARM_Y = 10.0                                     # arms' plane this far out from the inner panel
WINDER_X, WINDER_H = SPINDLE


def _arm_plane_y(x, h):
    return inner_y(x, h) + ARM_Y


def _cross(a0, a1, b0, b1):
    """Intersection of segments a and b in (x, h)."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a0, a1, b0, b1
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def regulator(side):
    def build(spec):
        """Window regulator (Fig 12.17 item 7; Fig 12.15 item 2): the pressed mounting plate bolted to the inner
        panel by four bolts, the toothed quadrant on its pivot meshing with the pinion on the winder spindle (through
        the inner panel), the coiled balance spring round the pivot (Fig 12.17: the spring at the plate)."""
        xq, hq = QUAD_PIVOT
        xs, hs = SPINDLE
        y0 = max(inner_y(xq, h) for h in (hq - 40.0, hq, hs, hs + 45.0))     # outboard of the curved panel all over
        # mounting plate: a rounded pressing round the spindle and the pivot, a raised rib, four bolt holes
        outline = G.rounded_rect(xq - 45.0, xs + 40.0, H(hq - 40.0), H(hs + 45.0), 14.0)
        plate = yprism(outline, y0, y0 + 1.6)
        rib = yprism(G.rounded_rect(xq - 20.0, xs + 18.0, H(hq + 20.0), H(hq + 34.0), 6.0), y0 + 1.6, y0 + 3.2)
        plate = plate + rib
        for dx, dh in ((-32.0, -28.0), (-32.0, 30.0), (28.0, 34.0), (28.0, -10.0)):
            px, ph = (xq + dx, hq + dh) if dx < 0 else (xs + dx, hs + dh - 30.0)
            plate = plate - ycyl(3.4, y0 - 1, y0 + 4, px, H(ph))
        # spindle bush, spindle and pinion
        bush = ycyl(9.0, y0 - 2.0, y0 + 6.0, xs, H(hs))
        spindle = ycyl(4.5, y0 - 20.0, y0 + 9.0, xs, H(hs))
        pinion = ycyl(9.0, y0 + 6.0, y0 + 10.0, xs, H(hs))
        for k in range(10):
            a = 2 * math.pi * k / 10
            pinion = pinion + ycyl(1.6, y0 + 6.0, y0 + 10.0, xs + 9.5 * math.cos(a), H(hs) + 9.5 * math.sin(a))
        # quadrant: a toothed sector on the pivot, its teeth meshing with the pinion
        rq = math.hypot(xs - xq, hs - hq) - 10.5
        ang0 = math.degrees(math.atan2(hs - hq, xs - xq))
        sector = []
        for k in range(15):
            a = math.radians(ang0 - 40.0 + 80.0 * k / 14)
            sector.append((xq + rq * math.cos(a), H(hq) + rq * math.sin(a)))
        web = [(xq, H(hq))] + sector
        quad = yprism(web, y0 + 6.0, y0 + 8.0)
        for k in range(28):
            a = math.radians(ang0 - 38.0 + 76.0 * k / 27)
            quad = quad + ycyl(1.7, y0 + 6.0, y0 + 8.0, xq + rq * math.cos(a), H(hq) + rq * math.sin(a))
        quad = quad - ycyl(22.0, y0 + 5, y0 + 9, xq + 0.55 * rq * math.cos(math.radians(ang0)),
                           H(hq) + 0.55 * rq * math.sin(math.radians(ang0)))       # lightening hole
        pivot = ycyl(7.0, y0, y0 + 12.0, xq, H(hq))
        spring = Location((xq, y0 + 3.0, H(hq))) * Rot(90, 0, 0) * coil_spring(1.0, 16.0, 6.0, 4.0)
        return _c([_side(p, side) for p in (plate, bush, spindle, pinion, quad, pivot, spring)], spec)
    return build


def _arm(a, b, y, w=16.0, t=2.5):
    """Flat steel arm between (x, h) points a and b in the plane y, rounded ends."""
    (xa, ha), (xb, hb) = a, b
    L = math.hypot(xb - xa, hb - ha)
    ang = math.degrees(math.atan2(hb - ha, xb - xa))
    bar = Location((xa, y, H(ha))) * Rot(0, -ang, 0) * Location((L / 2, 0, 0)) * \
        __import__("build123d").Box(L, t, w)
    return bar + ycyl(w / 2, y - t / 2, y + t / 2, xa, H(ha)) + ycyl(w / 2, y - t / 2, y + t / 2, xb, H(hb))


def lift_arm(side):
    def build(spec):
        """Lift arm (Fig 12.17): riveted to the quadrant at the pivot, running up and back to its stud and roller in
        the glass's lower channel (the rear stud); the scissor pivot where it crosses the extension arm."""
        y = _arm_plane_y(*QUAD_PIVOT)
        stud = (STUDS_X[1], STUD_H)
        arm = _arm(QUAD_PIVOT, stud, y)
        yg = C._glass_ys(STUD_H)
        roller = ycyl(7.0, y, yg - 3.0, stud[0], H(stud[1]))
        cx, ch = _cross(QUAD_PIVOT, stud, EXT_PIVOT, (STUDS_X[0], STUD_H))
        rivet = ycyl(5.0, y - 3.0, y + 6.0, cx, H(ch))
        return _c([_side(p, side) for p in (arm, roller, rivet)], spec)
    return build


def extension_arm(side):
    def build(spec):
        """Extension arm (Fig 12.15 item 5): from its pivot plate on the inner panel (two set screws) forward and up to
        the front stud in the glass's lower channel, crossing the lift arm on the scissor pivot."""
        y = _arm_plane_y(*EXT_PIVOT) + 3.0
        stud = (STUDS_X[0], STUD_H)
        arm = _arm(EXT_PIVOT, stud, y)
        yg = C._glass_ys(STUD_H)
        roller = ycyl(7.0, y, yg - 3.0, stud[0], H(stud[1]))
        y0 = inner_y(*EXT_PIVOT)
        plate = yprism(G.rounded_rect(EXT_PIVOT[0] - 30.0, EXT_PIVOT[0] + 30.0, H(EXT_PIVOT[1] - 30.0),
                                      H(EXT_PIVOT[1] + 30.0), 6.0), y0, y0 + 1.6)
        for dx, dh in ((-20.0, -20.0), (20.0, 20.0)):
            plate = plate - ycyl(3.0, y0 - 1, y0 + 3, EXT_PIVOT[0] + dx, H(EXT_PIVOT[1] + dh))
        pin = ycyl(6.0, y0, y + 3.0, EXT_PIVOT[0], H(EXT_PIVOT[1]))
        return _c([_side(p, side) for p in (arm, roller, plate, pin)], spec)
    return build


def arm_stop(side):
    def build(spec):
        """Regulator arm stop (Fig 12.15 item 3; Fig 12.17 item 12) with its rubber buffer (item 6) on the inner
        panel, where the lift arm comes to rest at the top of its travel."""
        x, h = QUAD_PIVOT[0] - 70.0, QUAD_PIVOT[1] + 95.0
        y0 = inner_y(x, h)
        bracket = ybox(x - 14.0, x + 14.0, y0, y0 + 14.0, H(h) - 4.0, H(h) + 4.0)
        stud = ycyl(3.0, y0 - 4.0, y0 + 2.0, x, H(h))
        buffer = ybox(x - 10.0, x + 10.0, y0 + 14.0, y0 + 26.0, H(h) - 9.0, H(h) + 9.0)
        return _c([_side(p, side) for p in (bracket, stud, buffer)], spec)
    return build


def lower_channel(side):
    def build(spec):
        """Door glass lower channel (Fig 12.17 item 3) on the glass's bottom edge with its glazing channel (2): the
        arms' studs run in its turned-over lips."""
        x0, x1 = C.GLASS_REAR_X + 40.0, C.SG.ql_post_x(GLASS_BOTTOM_H) - 24.0     # the glass's bottom edge, its front on the leaning post
        parts = []
        n = 6
        for k in range(n):
            xa = x0 + (x1 - x0) * k / n
            xb = x0 + (x1 - x0) * (k + 1) / n
            yg = C._glass_ys(GLASS_BOTTOM_H + 12.0)
            u = ybox(xa, xb + 0.5, yg - 7.0, yg + 7.0, H(GLASS_BOTTOM_H) - 10.0, H(GLASS_BOTTOM_H) + 12.0) - \
                ybox(xa - 1, xb + 1.5, yg - 5.5, yg + 5.5, H(GLASS_BOTTOM_H) - 8.5, H(GLASS_BOTTOM_H) + 13.0)
            parts.append(u)
        return _c([_side(p, side) for p in parts], spec)
    return build


LOCK_H = St.STRIKER_H


def door_lock_mech(side):
    def build(spec):
        """Door lock (Fig 12.13 item 15, early Sports Tourer): the pressed lock case on the rear shut face, its
        latch through the face, the operating link (16) from the outside handle's lever down to the lock's lever, the
        tension spring (18) and spring clips (17)."""
        x = C._door_x(LOCK_H, True) + 0.6
        yc = S.side_y(x, LOCK_H) - 35.0
        z = H(LOCK_H)
        case = ybox(x + 1.0, x + 30.0, yc - 20.0, yc + 20.0, z - 48.0, z + 48.0)
        case = case - ybox(x + 4.0, x + 31.0, yc - 17.0, yc + 17.0, z - 45.0, z + 45.0)
        flange = ybox(x, x + 1.6, yc - 26.0, yc + 26.0, z - 60.0, z + 60.0)
        for dz in (-48.0, 0.0, 48.0):
            flange = flange - xcyl(2.8, x - 1, x + 3, yc + (16.0 if dz else -16.0), z + dz)
        latch = xcyl(9.0, x - 7.0, x + 1.0, yc, z) + ybox(x - 7.0, x + 1.0, yc - 3.0, yc + 3.0, z - 14.0, z + 14.0)
        lever = ybox(x + 8.0, x + 60.0, yc - 1.5, yc + 1.5, z + 30.0, z + 40.0)
        xh = C.HANDLE_PIVOT_X                                    # outside handle lever's pivot in its escutcheon
        yh = S.side_y(xh, C.HANDLE_H) - 18.0
        link = swept_rod([(xh, yh, H(C.HANDLE_H)), (xh - 30.0, yh - 6.0, H(C.HANDLE_H) - 40.0),
                          (x + 58.0, yc, z + 38.0)], 3.0)
        spring = Location((x + 40.0, yc, z + 52.0)) * Rot(0, 90, 0) * coil_spring(0.8, 5.0, 40.0, 14.0)
        clips = [ycyl(4.0, yc - 4.0, yc + 4.0, x + 58.0, z + 38.0)]
        return _c([_side(p, side) for p in [case, flange, latch, lever, link, spring] + clips], spec)
    return build


def remote_control(side):
    def build(spec):
        """Remote control lock (Fig 12.13 item 12) with its anti-rattle sleeve (13): the inner handle's spindle
        bracket on the inner panel and the flat lever bar to the lock's lever, held by spring clips (Sec 42, 35)."""
        xi, hi = CK.INNER_HANDLE                                 # interior.inner_handle (front top, Oliver's kf131)
        y0 = inner_y(xi, hi)
        bracket = yprism(G.rounded_rect(xi - 30.0, xi + 30.0, H(hi - 34.0), H(hi + 34.0), 8.0), y0, y0 + 1.6)
        for dh in (-24.0, 24.0):
            bracket = bracket - ycyl(2.6, y0 - 1, y0 + 3, xi, H(hi + dh))     # elongated holes (Sec 35 para 3)
        spindle = ycyl(5.0, y0 - 14.0, y0 + 8.0, xi, H(hi))
        xl = C._door_x(LOCK_H, True) + 50.0
        hb = LOCK_H + 35.0                                       # along the inner panel's cavity face, out to the lock
        run = [(xi - 60.0, hi - 30.0), (xi - 160.0, hi - 70.0), (xl + 140.0, hb), (xl + 60.0, hb)]
        bar = swept_rod([(xi, y0 + 8.0, H(hi))] + [(x, inner_y(x, h) + 5.0, H(h)) for x, h in run] +
                        [(xl, S.side_y(xl, LOCK_H) - 35.0, H(hb))], 3.5)
        sleeve = swept_rod([(xi - 30.0, y0 + 10.0, H(hi - 15.0)), (xi - 70.0, y0 + 13.0, H(hi - 34.0))], 5.0)
        return _c([_side(p, side) for p in (bracket, spindle, bar, sleeve)], spec)
    return build


LOCK_BARREL_X, LOCK_BARREL_H = -1579.0, 688.0      # kf048 ray-cast: the key lock below the side strip, both doors


def _skin_loc(x, h):
    """Location on the left door skin at (x, h), local z along the skin's outward normal, local x near car x."""
    from mgb.chassis_geom import frame_to
    e = 2.0
    y = S.side_y(x, h)
    fx = (S.side_y(x + e, h) - S.side_y(x - e, h)) / (2 * e)
    fz = (S.side_y(x, h + e) - S.side_y(x, h - e)) / (2 * e)
    return frame_to((x, y, H(h)), (-fx, 1.0, -fz), xhint=(1.0, 0.0, 0.0))


def lock_barrel(side):
    def build(spec):
        """Door key lock (Fig 12.13 items 3-6) as on Oliver's car: separate from the handle, a round chrome escutcheon
        about 30 mm across, domed, on the skin below the side strip near the door's rear edge (kf048 ray-cast x -1579,
        h 688, both doors; kf189, kf190 close-ups), the barrel's face with its keyway; inside the door the housing,
        the retaining clip (5), the self-centring spring (6) and the coupling cam to the lock (Sec 35 para 2)."""
        from build123d import Axis, Cylinder, Align
        from mgb.shapes import revolved
        from mgb.elec_shapes import tryfillet
        loc = _skin_loc(LOCK_BARREL_X, LOCK_BARREL_H)
        esc = revolved([(8.6, -0.6), (15.0, -0.6), (15.0, 1.2), (13.2, 3.4), (10.6, 4.4), (8.6, 4.4)])
        barrel = Cylinder(8.4, 34.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, 3.6)))
        barrel = tryfillet(barrel, barrel.edges().filter_by_position(Axis.Z, 3.5, 3.7), 1.2)
        keyway = box(-0.9, 0.9, -5.5, 3.5, 1.8, 4.0) + box(-2.2, 2.2, 1.8, 3.5, 1.8, 4.0)
        barrel = barrel - keyway
        housing = revolved([(8.5, -30.0), (10.5, -30.0), (10.5, -1.0), (8.5, -1.0)])
        clip = box(-12.0, 12.0, -12.0, 12.0, -14.0, -12.0) - Cylinder(8.6, 6.0)
        spring = Location((0, 0, -27.0)) * coil_spring(0.7, 7.0, 8.0, 3.0)
        cam = box(-3.0, 22.0, -3.0, 3.0, -38.0, -34.0)
        return _c([_side(loc * p, side) for p in (esc, barrel, housing, clip, spring, cam)], spec)
    return build


def door_top_finisher(side):
    def build(spec):
        """Chrome end finisher at the rear of the door top (Oliver's kf187, kf188 zoomed): a pressed cap over the
        rear ends of the black capping roll and the felt glass strip, its top rounded over to the inside and its rear
        end rounded in plan, clipped on just ahead of the door's rear edge."""
        from build123d import Axis
        from mgb.elec_shapes import tryfillet
        lean = S.DOOR_REAR_LEAN * (S.DOOR_TOP_H - S.DOOR_BOTTOM_H) / (1100.0 - S.DOOR_BOTTOM_H)
        xr = S.DOOR_REAR_X + S.GAP / 2 + lean + 2.0
        xf = xr + 58.0
        xm = 0.5 * (xr + xf)
        yo = S.side_y(xm, S.DOOR_TOP_H - 16.0) + 1.4            # outside the skin just under the top's roll
        yi = S.side_y(xm, C.WAIST_H - 30.0) - C.DOOR_IN + 6.0 - 14.5
        ht = S.DOOR_TOP_H + 5.0
        out = B.fillet_poly([(yo, H(S.DOOR_TOP_H - 18.0)), (yo, H(ht)), (yi, H(ht)), (yi, H(C.WAIST_H - 16.0))],
                            [0.0, 7.0, 11.0, 0.0])
        inn = B.fillet_poly([(yo - 1.5, H(S.DOOR_TOP_H - 19.0)), (yo - 1.5, H(ht - 1.5)), (yi + 1.5, H(ht - 1.5)),
                             (yi + 1.5, H(C.WAIST_H - 17.0))], [0.0, 5.5, 9.5, 0.0])
        cap = xprism(out, xr, xf)
        cap = cap - xprism(inn, xr + 1.6, xf + 1.0)
        cap = tryfillet(cap, cap.edges().filter_by_position(Axis.X, xr - 0.1, xr + 0.1), 1.2)
        return _l(_side(cap, side), spec)
    return build


def striker_backing(side):
    def build(spec):
        """Striker packing and tapping plate (Fig 12.13 items 10, 11; Sec 27: shims behind the striker set the
        0.03-0.06 in clearance) behind the shut pillar, the striker's three screws."""
        x = S.DOOR_REAR_X + S.GAP / 2
        y = S.side_y(x, St.STRIKER_H) - 35.0
        z = H(St.STRIKER_H)
        packing = ybox(x - 4.6, x - 3.0, y - 16.0, y + 16.0, z - 32.0, z + 32.0)
        tap = ybox(x + T + 0.2, x + T + 3.2, y - 14.0, y + 14.0, z - 30.0, z + 30.0)
        screws = []
        for dz in (-20.0, 0.0, 20.0):
            packing = packing - xcyl(2.8, x - 6, x - 2, y, z + dz)
            screws.append(xcyl(4.5, x - 8.0, x - 3.0, y, z + dz) + xcyl(2.5, x - 3.0, x + T + 3.2, y, z + dz))
        return _c([_side(p, side) for p in [packing, tap] + screws], spec)
    return build


def check_strap(side):
    def build(spec):
        """Door check strap between the hinges: a steel strap on a pin in a bracket on the hinge pillar, through a
        slot in the door's front shut face, its rubber stop inside the door limiting the opening."""
        xp = S.DOOR_FRONT_X - S.GAP / 2
        h = 580.0
        y = S.side_y(xp, h) - 40.0
        z = H(h)
        bracket = ybox(xp - 30.0, xp - T, y - 12.0, y + 12.0, z - 14.0, z + 14.0)
        pin = zcyl(3.0, z - 16.0, z + 16.0, xp - 18.0, y)
        strap = ybox(xp - 22.0, xp + 70.0, y - 2.0, y + 2.0, z - 9.0, z + 9.0)
        stop = ybox(xp + 62.0, xp + 78.0, y - 9.0, y + 9.0, z - 12.0, z + 12.0)
        return _c([_side(p, side) for p in (bracket, pin, strap, stop)], spec)
    return build


def door_pull(side):
    def build(spec):
        """Interior door pull (Fig 12.13 item 8, early Sports Tourer): the two chrome end bosses screwed through the
        trim pad, mid-door below the seam (mgb.cockpit_layout PULL_HANDLE, Oliver's kf128, kf131; QA fix round 1,
        cockpit); the black grip between them is body.interior.pull-handle."""
        xc, h = CK.PULL_HANDLE
        L = CK.PULL_HANDLE_L
        from parts.body import interior as IN
        y = IN.card_face_y(h)
        out = []
        for s_ in (1, -1):
            xe = xc + s_ * L / 2
            out.append(ycyl(11.0, y - 4.0, y + 0.3, xe, H(h)))
            out.append(rod((xe, y - 4.0, H(h)), (xe - s_ * 6.0, y - 24.0, H(h)), 8.0))
            out.append(Location((xe - s_ * 6.0, y - 24.0, H(h))) * __import__("build123d").Sphere(10.0))
        return _c([_side(p, side) for p in out], spec)
    return build


def card_clips(side):
    def build(spec):
        """Trim pad clips (Sec 29): spring clips round the pad's edge into the inner panel's holes."""
        out = []
        xs = [S.DOOR_FRONT_X - 40.0 - k * (S.DOOR_FRONT_X - S.DOOR_REAR_X - 80.0) / 6 for k in range(7)]
        for x in xs:
            for h in (S.DOOR_BOTTOM_H + 45.0, C.WAIST_H - 50.0):
                y = inner_y(x, h)
                out.append(ycyl(5.0, y - 4.8, y - 3.6, x, H(h)) + ycyl(2.2, y - 3.6, y + 4.0, x, H(h)))
        return _c([_side(p, side) for p in out], spec)
    return build


def door_seal(side):
    def build(spec):
        """Door aperture seal: the rubber draught excluder on the hinge pillar, along the sill and up the shut
        pillar, the door's shut faces closing on it."""
        xf, xr = S.DOOR_FRONT_X - S.GAP / 2 - 3.0, S.DOOR_REAR_X + S.GAP / 2 + 3.0
        hb, ht = S.DOOR_BOTTOM_H + 6.0, C.WAIST_H - 30.0
        d = 30.0
        xfh = lambda h: S.door_front_x(h) - S.GAP / 2 - 3.0                       # noqa: E731 - the curved shut line
        front = [(xfh(h), S.side_y(xfh(h), h) - d, H(h)) for h in (ht, ht - 40.0, ht - 90.0, ht - 150.0, (ht + hb) / 2, hb + 30.0)]
        xs = [xf - 30.0 - k * (xf - xr - 60.0) / 6 for k in range(7)]
        bottom = [(x, S.side_y(x, hb) - d, H(hb - 8.0)) for x in xs]
        rear = [(xr, S.side_y(xr, h) - d, H(h)) for h in (hb + 30.0, (ht + hb) / 2, ht)]
        pts = front + bottom + rear
        return _l(_side(swept_rod(pts, 5.0), side), spec)
    return build


# ---------------------------------------------------------------------------------------------------------------------
# bonnet
# ---------------------------------------------------------------------------------------------------------------------
LOCK_X = 700.0                                   # bonnet lock pin and cup (structure.lock_platform's holes)


def bonnet_catch(spec):
    """Bonnet lock plate (Sec 6 para 4; Oliver's photo 13): the spring-loaded catch plate under the platform round
    the locating cup, its return spring, the release lever toward the car's left with the control cable's clamp
    screw."""
    z = H(S.MOUTH_TOP_H) - 30.0
    plate = zprism(G.rounded_rect(LOCK_X - 34.0, LOCK_X + 34.0, -46.0, 46.0, 8.0), z - 3.0, z - 1.4)
    for dy in (-32.0, 32.0):
        plate = plate - zcyl(3.3, z - 4, z, LOCK_X, dy)
    plate = plate - zcyl(10.5, z - 4, z, LOCK_X, 0.0)
    slide = zprism(G.rounded_rect(LOCK_X - 12.0, LOCK_X + 12.0, -20.0, 110.0, 5.0), z - 5.0, z - 3.0) - \
        zcyl(5.0, z - 6, z - 2, LOCK_X, 0.0)
    spring = Location((LOCK_X, -34.0, z - 8.0)) * Rot(90, 0, 0) * coil_spring(0.9, 6.0, 26.0, 8.0)
    clamp = zcyl(4.0, z - 12.0, z - 5.0, LOCK_X, 104.0) + box(LOCK_X - 6.0, LOCK_X + 6.0, 100.0, 112.0, z - 9.0, z - 5.0)
    return _c([plate, slide, spring, clamp], spec)


def _cable_route():
    """Bonnet release cable: from the catch's clamp along the left of the radiator duct, back along the left inner
    wing's top to the bulkhead, through it, and to the knob under the facia's left end (D: the cable's route; the knob
    position is a question for Oliver)."""
    z = H(S.MOUTH_TOP_H) - 30.0
    a = lambda x, b=70.0: (x, St.iw_along(x, b, 10.0)[0], St.iw_along(x, b)[1])     # along the left wing's upper wall
    return [(LOCK_X, 108.0, z - 9.0), (LOCK_X - 40.0, 200.0, z - 20.0), a(560.0), a(300.0), a(0.0), a(-380.0, 90.0),
            (-560.0, 470.0, H(700.0)), (C_KNOB[0] + 40.0, C_KNOB[1], C_KNOB[2])]


C_KNOB = (-760.0, 520.0, H(640.0))                # pull knob under the facia, left end


def bonnet_cable(spec):
    """Bonnet lock control cable (Sec 6 para 4) in its outer sheath, clamped at the lock plate, to the pull knob."""
    return _l(swept_rod(_cable_route(), 3.0), spec)


def bonnet_knob(spec):
    """Bonnet release pull knob under the facia, on its bracket."""
    x, y, z = C_KNOB
    knob = xcyl(11.0, x - 22.0, x - 4.0, y, z) + xcyl(4.0, x - 4.0, x + 40.0, y, z)
    bracket = box(x + 30.0, x + 33.0, y - 18.0, y + 18.0, z - 14.0, z + 22.0)
    return _c([knob, bracket], spec)


def bonnet_safety_catch(spec):
    """Bonnet safety catch (Sec 6 para 3): the spring-steel hook on the bonnet frame behind the lock pin, three bolts,
    catching the platform's edge until it is pushed back."""
    zt = H(S.top_h(LOCK_X - 60.0, 60.0)) - 24.0
    base = box(LOCK_X - 80.0, LOCK_X - 40.0, 40.0, 80.0, zt - 2.0, zt)
    for dx, dy in ((-70.0, 50.0), (-50.0, 50.0), (-60.0, 70.0)):
        base = base - zcyl(3.3, zt - 3, zt + 1, LOCK_X + dx, dy)
    hook = swept_rod([(LOCK_X - 60.0, 60.0, zt - 2.0), (LOCK_X - 60.0, 60.0, zt - 40.0),
                      (LOCK_X - 40.0, 60.0, zt - 62.0), (LOCK_X - 22.0, 60.0, zt - 58.0)], 2.5)
    tab = box(LOCK_X - 26.0, LOCK_X - 10.0, 52.0, 68.0, zt - 62.0, zt - 56.0)
    return _c([base, hook, tab], spec)


# ---------------------------------------------------------------------------------------------------------------------
# boot lid
# ---------------------------------------------------------------------------------------------------------------------
def boot_stay(spec):
    """Boot lid stay (Sec 26 para 1 'erect the lid stay'; Oliver's photo 11, on the left by the hinge): a formed rod
    on a pivot bracket on the lid frame's left side, shown stowed along the lid in its spring clip; its free end
    drops into the guide on the boot's left side when the lid is up."""
    y = 470.0
    xa, xb = S.BOOT_FRONT_X - 120.0, S.BOOT_FRONT_X - 520.0
    za = H(S.top_h(xa, y)) - 30.0
    zb = H(S.top_h(xb, y)) - 30.0
    bar = swept_rod([(xa, y, za), (xa - 20.0, y, za - 6.0), (xb + 30.0, y, zb - 6.0), (xb, y + 12.0, zb - 10.0)], 4.0)
    pivot = box(xa - 10.0, xa + 18.0, y - 10.0, y + 10.0, za - 4.0, za + 8.0) + ycyl(6.0, y - 12.0, y + 12.0, xa, za)
    clip = box(xb + 50.0, xb + 70.0, y - 9.0, y + 9.0, zb - 12.0, zb + 6.0) - \
        ycyl(4.6, y - 10.0, y + 10.0, xb + 60.0, zb - 6.0 + 0.0)
    return _c([bar, pivot, clip], spec)


def boot_stay_guide(spec):
    """Boot stay guide on the boot's left side panel: the slotted bracket the stay's end drops into."""
    y = 520.0
    x = S.BOOT_FRONT_X - 300.0
    z = H(S.top_h(x, y)) - 120.0
    plate = box(x - 40.0, x + 40.0, y, y + 2.0, z - 25.0, z + 25.0)
    lip = box(x - 40.0, x + 40.0, y - 14.0, y, z - 25.0, z - 23.0)
    slot = box(x - 30.0, x + 20.0, y - 15.0, y + 3.0, z - 4.0, z + 4.0)
    return _c([plate - slot, lip], spec)


def boot_seal(spec):
    """Boot aperture seal: the rubber on the opening's flange under the lid's edge, along its front, down its sides
    and across the tail under the lid's lower edge."""
    # (QA fix 1: follows the lid's new outline, its rounded front corners in plan and lower corners seen from behind)
    import math as _m
    w = lambda x: S._interp(S.BOOT_W, x) - 14.0                                   # noqa: E731
    xf = S.BOOT_FRONT_X - 14.0
    hr = S.BOOT_REAR_H + 14.0
    R = S.BOOT_REAR_R - 14.0
    zs = lambda x, y: H(S.top_h(x, abs(y))) - 24.0                                # noqa: E731
    wr = w(-2950.0)
    xs, x = [], xf - 60.0
    while S.top_h(x, wr) > hr + R + 30.0 and x > -3100.0:
        xs.append(x)
        x -= 60.0
    side_top = [(x, w(x), zs(x, w(x))) for x in xs]
    h_top = S.top_h(xs[-1], wr) - 40.0
    hs = [h_top - (h_top - (hr + R)) * k / 4 for k in range(1, 5)]
    side_down = [(S.tail_x(wr, h) + 18.0, wr, H(h)) for h in hs if h_top - (hr + R) > 60.0]
    corner = [(wr - R + R * _m.cos(a), hr + R - R * _m.sin(a)) for a in (_m.radians(30.0), _m.radians(60.0))]
    corner = [(S.tail_x(y, h) + 18.0, y, H(h)) for y, h in corner]
    rear = [(S.tail_x(y, hr) + 18.0, y, H(hr)) for y in (wr - R, 250.0, 0.0, -250.0, -(wr - R))]
    left = [(xf, 150.0, zs(xf, 150.0)), (xf - 30.0, w(xf) - 40.0, zs(xf - 30.0, w(xf) - 40.0))] + side_top + side_down + corner
    right = [(x, -y, z) for x, y, z in reversed(left)]
    path = [(xf, 6.0, zs(xf, 6.0))] + left + rear + right[:-1] + [(xf, -150.0, zs(xf, -150.0)), (xf, -6.0, zs(xf, -6.0))]   # its
    # joint at the front centre (a closed sweep would overlap itself)
    clean = [path[0]]
    for q in path[1:-1]:
        if _m.dist(q, clean[-1]) > 30.0:
            clean.append(q)
    path = clean + [path[-1]]
    return _l(swept_rod(path, 5.0), spec)


# ---------------------------------------------------------------------------------------------------------------------
PARTS = {}
for _s, _n in ((1, "l"), (-1, "r")):
    PARTS.update({
        f"body.door-mechanisms.regulator-{_n}": {"build": regulator(_s)},
        f"body.door-mechanisms.lift-arm-{_n}": {"build": lift_arm(_s)},
        f"body.door-mechanisms.extension-arm-{_n}": {"build": extension_arm(_s)},
        f"body.door-mechanisms.arm-stop-{_n}": {"build": arm_stop(_s)},
        f"body.door-mechanisms.lower-channel-{_n}": {"build": lower_channel(_s)},
        f"body.door-mechanisms.lock-{_n}": {"build": door_lock_mech(_s)},
        f"body.door-mechanisms.remote-control-{_n}": {"build": remote_control(_s)},
        f"body.door-mechanisms.lock-barrel-{_n}": {"build": lock_barrel(_s)},
        f"body.door-mechanisms.door-top-finisher-{_n}": {"build": door_top_finisher(_s)},
        f"body.door-mechanisms.striker-backing-{_n}": {"build": striker_backing(_s)},
        f"body.door-mechanisms.check-strap-{_n}": {"build": check_strap(_s)},
        f"body.door-mechanisms.door-pull-{_n}": {"build": door_pull(_s)},
        f"body.door-mechanisms.card-clips-{_n}": {"build": card_clips(_s)},
        f"body.door-mechanisms.door-seal-{_n}": {"build": door_seal(_s)},
    })
PARTS.update({
    "body.closure-fittings.bonnet-catch": {"build": bonnet_catch},
    "body.closure-fittings.bonnet-cable": {"build": bonnet_cable},
    "body.closure-fittings.bonnet-knob": {"build": bonnet_knob},
    "body.closure-fittings.bonnet-safety-catch": {"build": bonnet_safety_catch},
    "body.closure-fittings.boot-stay": {"build": boot_stay},
    "body.closure-fittings.boot-stay-guide": {"build": boot_stay_guide},
    "body.closure-fittings.boot-seal": {"build": boot_seal},
})
