"""Body shell inner structure (P11b; Haynes Ch 12 Sec 1: combined body and underframe of welded steel): floor pan
halves and transmission tunnel, toe boards, bulkhead (dash panel) with the pedal box aperture and grommets, front
chassis legs, inner wings and wheel houses, front apron and radiator duct, bonnet lock platform, sills (inner sill,
castle section, jacking sockets), hinge and shut pillars, scuttle inner panel and the screen pillar feet,
heelboard, tonneau floor with the battery access panels, rear bulkhead, rear wheel houses, boot floor with the axle
kick-up, rear chassis rails with the spring, damper, strap and bump mountings, and the brackets the earlier phases
hang from it.

Everything is drawn in place in the car frame from mgb.body_shell_layout, mgb.underbody_layout and the earlier
phases' datums (each import named where it is used). Sheet thickness 1.2 mm for the floor and structure (D: 18 swg),
1.6-2.5 mm for brackets.
"""
from __future__ import annotations

import math

from build123d import Compound, Location, Rot

from mgb import (body_geom as G, body_layout as BL, body_shell as B, body_shell_layout as S, brake_layout as BK,
                 car_layout as CL, chassis_layout as CH, clutch_layout as CLU, front_suspension_layout as FS,
                 fuel_supply_layout as FL, rear_suspension_layout as RS, steering_layout as ST, underbody_layout as U)
from mgb.chassis_geom import box, xcyl, xprism, ycyl, yprism, zcyl, zprism

T = 1.2
H = S.z_of
FLOOR_Z = U.FLOOR_Z                       # floor underside
FLOOR_TOP = U.FLOOR_Z + T


def _l(p, spec):
    p.label = spec.id
    return p


def _c(parts, spec):
    c = Compound(G.solids(parts))
    c.label = spec.id
    return c


def _side(p, side):
    return p if side > 0 else p.mirror(__import__("build123d").Plane.XZ)


# =====================================================================================================================
# transmission tunnel and floor
# =====================================================================================================================
# Tunnel stations (x, base half-width, half-width at z_mid, z_mid, top z, top half-width), cabin faces. Clears the
# bellhousing (P5a: 104 mm left / 84 mm right of the mainshaft, 92 mm above it, and the clutch lever), the overdrive
# (P5b: 141 mm right at the solenoid, 128 mm below the axis at the sump plugs), the remote housing (crank axis +157 mm)
# and the propeller shaft (P6), with P8's handbrake wall at |y| 122 (underbody_layout TUNNEL_Y) from x -1050 back.
TUNNEL = [(-398.0, 240.0, 230.0, -235.0, -52.0, 150.0), (-520.0, 234.0, 222.0, -235.0, -52.0, 140.0),
          (-640.0, 202.0, 178.0, -235.0, -52.0, 122.0), (-720.0, 182.0, 166.0, -250.0, -52.0, 116.0),
          (-880.0, 172.0, 160.0, -250.0, -52.0, 112.0), (-940.0, 160.0, 142.0, -260.0, -112.0, 92.0),
          (-1010.0, 140.0, 126.0, -280.0, -152.0, 76.0), (-1100.0, U.TUNNEL_Y, U.TUNNEL_Y, -300.0, -168.0, 72.0),
          (-1449.0, U.TUNNEL_Y, U.TUNNEL_Y, -300.0, -198.0, 72.0)]


def tunnel_profile(st, flange=24.0):
    x, wb, wm, zm, zt, wt = st
    zf = FLOOR_TOP
    pts = [(wb + flange, zf), (wb, zf), (wm, zm), (wt + 28.0, zt - 8.0), (wt, zt), (-wt, zt), (-(wt + 28.0), zt - 8.0),
           (-wm, zm), (-wb, zf), (-(wb + flange), zf)]
    return G.round_path(pts, 30.0, 5)


def tunnel_halfwidth(x, z):
    """Cabin-face half-width of the tunnel at (x, z) (linear between stations)."""
    st = TUNNEL
    for a, b in zip(st, st[1:]):
        if b[0] <= x <= a[0]:
            t = (a[0] - x) / (a[0] - b[0])
            ia = [a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t]
            wb, wm, zm = ia
            if z <= zm:
                return wb + (wm - wb) * (z - FLOOR_TOP) / (zm - FLOOR_TOP)
            return wm
    return U.TUNNEL_Y


def tunnel(spec):
    """Transmission tunnel: pressed in two lengths and welded, the front length wide and tall round the bellhousing,
    the gearbox and the overdrive, the rear length narrow over the propeller shaft; flanges spot-welded to the floor
    halves, a stiffening swage along each wall, the gear lever aperture with the grommet retainer's screw holes
    (Fig 6.3 items 161-166), the handbrake ratchet plate's three bolt holes and spigot hole in the right wall
    (P8), the speedometer cable grommet hole."""
    from build123d import Solid, Wire, Vector
    secs = []
    for st in TUNNEL:
        pts = G.band(tunnel_profile(st), T)
        secs.append(Wire.make_polygon([Vector(st[0], y, z) for y, z in pts], close=True))
    body = Solid.make_loft(secs, ruled=True)
    # gear lever aperture (P5a lever leaves the remote housing at LEVER_BALL, cranked back to the knob)
    from mgb import gearbox_layout as GL
    lx = GL.LEVER_BALL[0] + (GL.KNOB[0] - GL.LEVER_BALL[0]) * (TUNNEL[3][4] - GL.LEVER_BALL[2]) / (GL.KNOB[2] - GL.LEVER_BALL[2])
    body = body - G.zprism(G.obround(lx - 10.0, 0.0, 120.0, 80.0), TUNNEL[3][4] - 40.0, TUNNEL[3][4] + 40.0)
    for dx, dy in ((-75.0, -48.0), (-75.0, 48.0), (55.0, -48.0), (55.0, 48.0)):
        body = body - zcyl(2.2, TUNNEL[3][4] - 30, TUNNEL[3][4] + 30, lx - 10.0 + dx, dy)
    # handbrake ratchet plate bolts and spigot (right wall, y -122)
    from parts.brakes import handbrake as HBK
    for x, z in HBK.ratchet_bolts():
        body = body - ycyl(3.4, -140.0, -100.0, x, z)
    body = body - ycyl(9.0, -140.0, -100.0, BK.HB_PIVOT[0], BK.HB_PIVOT[2])
    # speedometer cable and handbrake cable exits (right wall, low)
    body = body - ycyl(9.0, -260.0, -100.0, -1060.0, -330.0)
    body = _pass_cut(body, "tunnel")
    return _l(body, spec)


def floor_half(side):
    def build(spec):
        """Floor half: flat pan from the tunnel to the inner sill, the toe board's foot at the front, the heelboard at the
        rear; turned-up flanges at the sill and the tunnel, three transverse stiffening ribs, the seat runner pads
        (four 5/16 in captive-nut holes each), two drain holes with bungs, the raised pads with captive nuts for the
        gearbox crossmember's 3/8 in screws (chassis_layout REAR_XMEMBER_BOLTS, body face z -381.2, 4.8 mm above the
        floor underside), and the clip screw holes for P8's brake pipe and P11a's fuel pipe under the floor."""
        x0, x1 = U.TOE_FOOT[0] - 2.0, U.HEELBOARD_X + 2.0
        yi = U.TUNNEL_Y + 20.0
        yo = S.SILL_INNER_Y
        pan = box(x1, x0, yi, yo, FLOOR_Z, FLOOR_TOP)
        pan = pan + box(x1, x0, yo - T, yo, FLOOR_TOP, FLOOR_TOP + 30.0)           # flange up the inner sill
        for xr in (-640.0, -1000.0, -1300.0):                                       # transverse ribs (pressed up)
            rib = G.sheet_x([(yi + 30.0, FLOOR_TOP), (yi + 40.0, FLOOR_TOP + 7.0), (yo - 40.0, FLOOR_TOP + 7.0),
                             (yo - 30.0, FLOOR_TOP)], T, xr - 14.0, xr + 14.0, 4.0)
            pan = pan + rib
        # gearbox crossmember pads (raised so the screws' face is at chassis_layout BODY_FACE_Z)
        for bx, by, bz in CH.REAR_XMEMBER_BOLTS:
            if by * side > 0:
                pad = box(bx - 30.0, bx + 30.0, abs(by) - 24.0, abs(by) + 24.0, CH.BODY_FACE_Z, CH.BODY_FACE_Z + T)
                pan = pan + pad
        out = pan
        for bx, by, bz in CH.REAR_XMEMBER_BOLTS:
            if by * side > 0:
                out = out - zcyl(5.0, FLOOR_Z - 5, FLOOR_TOP + 5, bx, abs(by))
        for xs in (-1060.0, -1290.0):                                               # seat runner captive nuts
            for ys in (300.0, 470.0):
                out = out - zcyl(4.2, FLOOR_Z - 5, FLOOR_TOP + 10, xs, ys)
        for xd in (-860.0, -1380.0):                                                # drain holes
            out = out - zcyl(10.0, FLOOR_Z - 5, FLOOR_TOP + 10, xd, 545.0)
        if side < 0:                                                                # pipe clip screw holes (P8, P11a)
            for xc_ in (-650.0, -950.0, -1250.0):
                out = out - zcyl(2.4, FLOOR_Z - 5, FLOOR_TOP + 10, xc_, -FL.FLOOR_Y)
        return _l(_side(out, side), spec)
    return build


def floor_bung(spec):
    """Rubber drain bung in the floor."""
    from mgb.chassis_geom import zrev
    return _l(zrev([(0, -6.0), (12.5, -6.0), (12.5, 0.0), (9.0, 0.0), (9.0, 3.0), (0, 3.0)]), spec)


def toe_board(side):
    def build(spec):
        """Toe board: the sloping footwell panel from the bulkhead's foot (underbody_layout TOE_TOP) down to the floor
        (TOE_FOOT), tunnel to the inner sill, with flanges; on the right the battery cable grommet hole (P10
        CABLE_GROMMET)."""
        (xf, zf), (xt, zt) = U.TOE_FOOT, U.TOE_TOP
        yi, yo = 150.0, S.SILL_INNER_Y
        prof = [(xt - 0.0, zt + 25.0), (xt, zt), (xf, FLOOR_TOP - 0.2), (xf - 30.0, FLOOR_TOP - 0.2)]
        p = G.sheet_y([(x, z) for x, z in prof], T, yi, yo, 10.0)
        if side < 0:                                                        # drawn on the left, mirrored
            gx, gy, gz = BL.CABLE_GROMMET
            nx, nz = (zt - FLOOR_TOP), -(xt - xf)                               # toe board normal (x, z)
            L = math.hypot(nx, nz)
            from mgb.chassis_geom import rod
            zg = U.toe_z(gx) + T / 2
            a = (gx - nx / L * 20, -gy, zg - nz / L * 20)
            b = (gx + nx / L * 20, -gy, zg + nz / L * 20)
            p = p - rod(a, b, 11.0)
            for name, (x, y, z), ax in harness_passes():               # dip switch leads (P10b)
                if name == "toe-dip":
                    p = p - zcyl(9.0, z - 30, z + 30, x, -y)
        return _l(_side(p, side), spec)
    return build


# =====================================================================================================================
# bulkhead and scuttle
# =====================================================================================================================
BH_X = CL.BULKHEAD_X
BH_W = 640.0                               # |y| of the bulkhead's ends at the hinge pillars


def bulkhead_top_z(y):
    """Top edge of the bulkhead under the scuttle (follows the scuttle crown 70 mm down)."""
    return H(S.top_h(BH_X - 20.0, abs(y))) - 70.0


def bulkhead_outline():
    """Bulkhead in y-z: the toe board line at the bottom, arched over the tunnel mouth, the scuttle line at the top."""
    zb = U.TOE_TOP[1]
    t0 = TUNNEL[0]
    tun = [(y, z) for y, z in tunnel_profile(t0, flange=0.0)]
    pts = [(BH_W, zb)] + [(y, max(z, zb)) for y, z in tun if abs(y) <= t0[1] + 0.1] + [(-BH_W, zb)]
    top = [(y, bulkhead_top_z(y)) for y in [-BH_W + k * (2 * BH_W) / 16 for k in range(17)]]
    return pts + top


def bulkhead(spec):
    """Bulkhead (dash panel): the engine-side face at car_layout BULKHEAD_X, from the toe boards up to the scuttle,
    across between the hinge pillars, arched over the tunnel; two horizontal stiffening swages, a flange turned back
    along the top under the scuttle; the pedal box aperture inside its flange with the six bolt holes (P8
    parts/brakes/master.py box_bolts: nuts behind the panel), the heater air opening on the centre line, the main
    harness grommet (P10 HARNESS_GROMMET), the four-way connection's bolt hole (P8 FOUR_WAY), the overdrive vacuum
    switch screw holes (P10), the column hole on the right (P9), the fuel and brake pipe clip screw holes."""
    x0 = BH_X - T
    pts = bulkhead_outline()
    p = xprism(pts, x0, BH_X)
    # stiffening swages (pressed toward the engine)
    for z in (-160.0, 60.0):
        p = p + (xprism([(-BH_W + 60.0, z - 9.0), (BH_W - 60.0, z - 9.0), (BH_W - 60.0, z + 9.0), (-BH_W + 60.0, z + 9.0)],
                        BH_X, BH_X + 3.0) - box(BH_X - 1, BH_X + 4, -250.0, 250.0, z - 12, z + 12))
    # top flange turned back into the cabin under the scuttle inner panel
    top = [(y, bulkhead_top_z(y)) for y in [-BH_W + k * (2 * BH_W) / 16 for k in range(17)]]
    for a, b in zip(top, top[1:]):
        p = p + xprism([(a[0], a[1] - T), (b[0], b[1] - T), (b[0], b[1]), (a[0], a[1])], BH_X - 40.0, BH_X)
    # pedal box aperture and bolts (P8)
    from parts.brakes import master as MS
    ap = G.rounded_rect(-328.0, -188.0, -98.0, 14.0, 10.0)
    p = p - xprism(ap, x0 - 5, BH_X + 5)
    for yp in (-215.0, -290.0):                  # the pedal arms' slots below the aperture (P8: arms cross at z -140)
        p = p - xprism(G.rounded_rect(yp - 17.0, yp + 17.0, -185.0, -96.0, 12.0), x0 - 5, BH_X + 5)
    for y, z in MS.box_bolts():
        p = p - xcyl(4.2, x0 - 5, BH_X + 5, y, z)
    # heater air opening and its four screw holes (early heater, Fig 12.27, on the bulkhead shelf)
    p = p - xprism(G.rounded_rect(-150.0, 70.0, 150.0, 225.0, 14.0), x0 - 5, BH_X + 5)
    # grommets: main harness (P10), speedometer / oil gauge / temperature capillary on the right
    hx, hy, hz = BL.HARNESS_GROMMET
    for y, z, r in ((hy, hz, 15.0), (-250.0, 105.0, 11.0), (-210.0, 105.0, 8.0), (-170.0, 105.0, 8.0)):
        p = p - xcyl(r, x0 - 5, BH_X + 5, y, z)
    fx, fy, fz = BK.FOUR_WAY
    p = p - xcyl(4.2, x0 - 5, BH_X + 5, fy, fz + 0.0)
    vx, vy, vz = BL.OD_VACUUM_SWITCH
    for dy in (-26.0, 26.0):
        p = p - xcyl(2.2, x0 - 5, BH_X + 5, vy + dy, vz)
    # steering column (P9) through the panel, right of the pedals
    p = p - xcyl(30.0, x0 - 5, BH_X + 5, _column_y_at(BH_X), _column_z_at(BH_X))
    # clip screw holes for the fuel pipe (P11a) and the brake pipes (P8) on the engine side
    for (pt, n) in FL.CLIPS["main"]:
        if abs(pt[0] - BH_X) < 30.0:
            p = p - xcyl(2.4, x0 - 5, BH_X + 5, pt[1], pt[2])
    return _l(p, spec)


def _column_z_at(x):
    """Height of the steering column axis where it crosses x (P9 COLUMN_TOE_PLATE and COLUMN_TOP_CLAMP)."""
    (x0, _, z0), (x1, _, z1) = ST.COLUMN_TOE_PLATE, ST.COLUMN_TOP_CLAMP
    return z0 + (z1 - z0) * (x - x0) / (x1 - x0)


def _column_y_at(x):
    (x0, y0, _), (x1, y1, _) = ST.COLUMN_TOE_PLATE, ST.COLUMN_TOP_CLAMP
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def column_toe_mount(spec):
    """Steering column lower mounting: a pressed cup welded to the bulkhead's cabin face, its face square to the
    column at P9's COLUMN_TOE_PLATE, with the hole for the 1 1/2 in tube and the two studs' holes for the bottom
    bracket (Fig 11.6 item 65)."""
    from mgb.chassis_geom import frame_to
    from build123d import Vector
    p0 = Vector(*ST.COLUMN_TOE_PLATE)
    p1 = Vector(*ST.COLUMN_TOP_CLAMP)
    d = (p1 - p0).normalized()
    loc = frame_to(ST.COLUMN_TOE_PLATE, (d.X, d.Y, d.Z), (0, 0, 1))
    from mgb.chassis_geom import zcyl as zc
    face = zc(46.0, -1.6, 0.0) - zc(22.0, -3.0, 2.0)
    for yy in (-32.0, 32.0):
        face = face - zc(3.3, -3.0, 2.0, 0.0, yy)
    cup = (zc(46.0, -42.0, -1.6) - zc(44.4, -43.0, -1.5)) - zc(22.0, -50.0, 0.0)
    part = loc * (face + cup)
    part = part & box(BH_X - 90.0, BH_X - T + 0.01 + 40.0, -600, 0, -400, 200)
    part = part - box(BH_X - T, BH_X + 60.0, -600, 0, -400, 200)
    return _l(part, spec)


def clutch_hose_support(spec):
    """Support for P4's pipe-to-hose bracket (clutch_layout HOSE_BRACKET): an angle welded to the bulkhead's engine
    face, its arm reaching forward under the bracket's foot with a 1/4 in screw (P9 suggested the leg; the bracket is
    160 mm inboard of it, so it is carried from the bulkhead instead)."""
    hx, hy, hz = CLU.HOSE_BRACKET
    arm = box(BH_X, hx + 22.0, hy - 14.0, hy + 14.0, hz - 22.0, hz - 20.0)
    web = box(BH_X, BH_X + 2.0, hy - 20.0, hy + 20.0, hz - 60.0, hz - 20.0)
    gus = yprism([(BH_X, hz - 60.0), (BH_X + 40.0, hz - 22.0), (BH_X, hz - 22.0)], hy - 1.0, hy + 1.0)
    p = arm + web + gus
    p = p - zcyl(3.3, hz - 30, hz - 10, hx - 8.0, hy)
    p = p - xcyl(3.3, BH_X - 1, BH_X + 3, hy, hz - 44.0)
    return _l(p, spec)


SCUTTLE_INNER_X = (BH_X - 20.0, -680.0)    # bulkhead flange to ahead of the instruments' cases (P10, 100 mm deep)
FACIA_RAIL_X = (-742.0, -712.0)             # the facia rail under the scuttle's rear edge, above the instruments


def facia_rail_z():
    """Underside and top of the facia rail: under the scuttle skin, above P10's instrument cases."""
    top = H(S.top_h(FACIA_RAIL_X[0], 380.0)) - 6.0
    return top - 26.0, top


def scuttle_inner(spec):
    """Scuttle inner panel: the closing panel under the scuttle top from the bulkhead flange back to ahead of the
    instruments, with the wiper wheelbox holes (P10 WIPER_SPINDLES), and the square-section facia rail under the
    scuttle's rear edge tying the kick panels together (MGBs Made in Australia), above the instrument cases."""
    xa, xb = SCUTTLE_INNER_X
    ys = [-600.0 + 1200.0 * k / 16 for k in range(17)]
    pts = [(y, H(S.top_h((xa + xb) / 2, abs(y))) - 58.0) for y in ys]
    plate = xprism(G.band(pts, T), xb, xa)
    for x, y, z in BL.WIPER_SPINDLES:
        plate = plate - zcyl(14.0, z - 140, z + 10, x, y)
    z0, z1 = facia_rail_z()
    r0, r1 = FACIA_RAIL_X
    ys = [-596.0 + 1192.0 * k / 24 for k in range(25)]               # the rail follows the scuttle's fall to the sides
    top = [(y, min(z1, H(S.top_h(r1, abs(y))) - 6.0)) for y in ys]
    outer = top + [(y, z - 26.0) for y, z in reversed(top)]
    inner = [(y, z - 1.2) for y, z in top[1:-1]] + [(y, z - 24.8) for y, z in reversed(top[1:-1])]
    rail = xprism(outer, r0, r1) - xprism(inner, r0 + 1.2, r1 - 1.2)
    return _c([plate, rail], spec)


def wiper_motor_bracket(spec):
    """Bracket for P10's DR3A wiper motor (WIPER_MOTOR) hung from the scuttle inner panel on the left, three
    screw holes."""
    mx, my, mz = BL.WIPER_MOTOR
    top = H(S.top_h(mx, abs(my))) - 58.0 - T
    leg = box(mx - 40.0, mx + 40.0, my + 20.0, my + 22.0, mz - 20.0, top)
    foot = box(mx - 40.0, mx + 40.0, my - 30.0, my + 22.0, top - 2.0, top)
    p = leg + foot
    for dx, dz in ((-28.0, 0.0), (28.0, 0.0), (0.0, 30.0)):
        p = p - ycyl(2.4, my + 19, my + 23, mx + dx, mz + dz)
    return _l(p, spec)


def column_top_bracket(spec):
    """Steering column upper bracket under the facia (P9 COLUMN_TOP_CLAMP, Fig 11.6 item 59 clamps to it): a pressed
    channel hung from the facia rail with the clamp's two bolt holes."""
    cx, cy, cz = ST.COLUMN_TOP_CLAMP
    rail_z = facia_rail_z()[0]
    zt = cz + 22.0
    x0 = FACIA_RAIL_X[1] - 6.0
    web = box(cx - 24.0, x0, cy - 50.0, cy + 50.0, zt, zt + 2.0)
    legs = [box(x0 - 2.0, x0, cy - 50.0, cy + 50.0, zt, rail_z), box(-762.0, -760.0, cy - 50.0, cy + 50.0, zt, rail_z)]
    p = G.fuse([web] + legs)
    for dy in (-38.0, 38.0):
        p = p - zcyl(4.2, zt - 2, zt + 4, cx, cy + dy)
    return _l(p, spec)


# =====================================================================================================================
# front structure
# =====================================================================================================================
LEG_Y = S.FRONT_LEG_Y
LEG_W = S.FRONT_LEG_W
LEG_BOT, LEG_TOP = S.FRONT_LEG_BOTTOM_Z, S.FRONT_LEG_TOP_Z


def leg_profile_xz():
    """Front chassis leg in side view: level at the crossmember (underside on P9's pads), forward to the front apron,
    back to the bulkhead, then down the toe board and under the floor to about a third of the way along the door."""
    under = FLOOR_Z - 58.0
    (xf, zf), (xt, zt) = U.TOE_FOOT, U.TOE_TOP
    bottom = [(700.0, LEG_BOT + 20.0), (330.0, LEG_BOT), (-300.0, LEG_BOT), (-500.0, under), (-1100.0, under),
              (-1130.0, FLOOR_Z - 0.5)]
    top = [(-560.0, FLOOR_Z - 0.5), (xf, FLOOR_Z - 0.5), (xt + 2.0, zt - 1.5), (-330.0, LEG_TOP), (330.0, LEG_TOP),
           (700.0, LEG_TOP + 10.0)]
    return bottom + top


# Plan line of the leg's centre: on P9's support bolts over the crossmember, stepped inboard ahead of and behind it
# where the tyre's shoulder sweeps at full lock (28 deg front in, 37 deg rear in, for the 32 ft turning circle: the
# envelope check in PLAN), back out under the toe board and the floor.
LEG_STEP_Y = 338.0
LEG_STEP_W = 62.0                          # narrower where stepped: between P8's right front pipe (y -300) and the tyre
LEG_PLAN = [(-1130.0, LEG_Y, LEG_W), (-310.0, LEG_Y, LEG_W), (-215.0, LEG_STEP_Y, LEG_STEP_W),
            (-25.0, LEG_STEP_Y, LEG_STEP_W), (48.0, LEG_Y, LEG_W), (256.0, LEG_Y, LEG_W),
            (300.0, LEG_STEP_Y, LEG_STEP_W), (700.0, LEG_STEP_Y, LEG_STEP_W)]


def leg_band(grow):
    """Plan outline of the leg (both faces), grown by `grow`."""
    left, right = [], []
    for x, y, w in LEG_PLAN:
        left.append((x, y + w / 2 + grow))
        right.append((x, y - w / 2 - grow))
    return left + list(reversed(right))


def front_leg(side):
    def build(spec):
        """Front chassis leg: box section along the side-view line, carrying the front crossmember on its two support
        bolts (P9 BODY_BOLTS: holes through bottom and top, a spacer tube between), stepped inboard ahead of and behind
        the crossmember to clear the tyre at full lock, forward to the front apron with the bumper spring bar bolt
        holes, closing plates at the ends."""
        prof = leg_profile_xz()
        outer = yprism(prof, -2000.0, 2000.0) & zprism(leg_band(0.0), -2000.0, 2000.0)
        inner = (yprism(_inset_xz(prof, T), -2000.0, 2000.0) & zprism(leg_band(-T), -2000.0, 2000.0)
                 & box(-1129.0, 699.0, -2000, 2000, -2000, 2000))
        shell = outer - inner
        yc = LEG_Y
        for x, y, z in FS.BODY_BOLTS[1]:
            shell = shell - zcyl(5.8, LEG_BOT - 5, LEG_TOP + 5, x, yc)
            shell = shell + (zcyl(8.0, LEG_BOT + T, LEG_TOP - T, x, yc) - zcyl(5.8, LEG_BOT, LEG_TOP, x, yc))
        for zz in (LEG_BOT + 15.0, LEG_TOP - 12.0):                       # bumper spring bar bolts, front end
            shell = shell - ycyl(5.0, LEG_STEP_Y - LEG_W, LEG_STEP_Y + LEG_W, 660.0, zz)
        return _l(_side(shell, side), spec)
    return build


def _inset_xz(prof, d):
    """Side-view leg outline brought in by d top and bottom (the box's top and bottom sheets)."""
    n = len(prof) // 2
    bottom = [(x, z + d) for x, z in prof[:n]]
    top = [(x, z - d) for x, z in prof[n:]]
    return bottom + top


IW_Y = S.INNER_WING_Y
IW_X0, IW_X1 = BH_X, 590.0


def inner_wing_top(x):
    """Top edge (wing bolting flange) of the inner wing at x: under the outer wing's top, inside the bonnet gap."""
    return H(S.top_h(x, IW_Y + 40.0)) - 50.0


def inner_wing(side):
    def build(spec):
        """Inner wing (engine-bay valance) and wheel house: the vertical panel at body_layout INNER_WING_Y from the
        bulkhead forward to the front apron, from the chassis leg up to a flange the outer wing bolts to; the wheel
        house arched over the tyre (420 mm radius about the front axle, clearing the tyre at bump and lock) out to
        the outer wing; an opening over the damper arm (P9: the arm sweeps over the leg between |y| 305 and 499) and
        the hose bracket hole (P9 HOSE_BRACKET); the 1/4 in screw holes for P10's control box, fuse block, flasher
        and solenoid on the right, the overdrive relay on the left."""
        y0 = IW_Y
        xs = [IW_X0 + (IW_X1 - IW_X0) * k / 20 for k in range(21)]
        top = [(x, inner_wing_top(x)) for x in xs]
        pts = [(IW_X0, LEG_TOP), (IW_X1, LEG_TOP)] + list(reversed(top))
        panel = yprism(pts, y0, y0 + T)
        # damper arm opening (P9) and the wheel's swept space under the leg top
        fx = FS.FX
        panel = panel - yprism(G.rounded_rect(fx - 150.0, fx + 150.0, LEG_TOP - 5.0, -95.0, 30.0), y0 - 5, y0 + 5)
        # the tyre's shoulder at full lock sweeps under the valance ahead of and behind the wheel (envelope check):
        # the valance's lower edge is raised there, the wheel house curving in above it
        for xa, xb in ((-255.0, -15.0), (315.0, 505.0)):
            panel = panel - yprism(G.rounded_rect(xa, xb, LEG_TOP - 5.0, -30.0, 40.0), y0 - 5, y0 + 5)
        # wheel house: an arched band over the tyre from the valance to the wing
        r = 420.0
        cx, cz = CL.FRONT_AXLE_X, CL.WHEEL_Z
        wh = ycyl(r + T, y0, 716.0, cx, cz) - ycyl(r, y0 - 1, 717.0, cx, cz)
        wh = wh & box(cx - 520.0, cx + 520.0, y0, 717.0, cz + 60.0, 2000.0)
        p = panel + wh
        # flange along the top, turned outward to the outer wing
        for a, b in zip(top, top[1:]):
            p = p + yprism([(a[0], a[1] - T), (b[0], b[1] - T), (b[0], b[1]), (a[0], a[1])], y0, y0 + 28.0)
        # hose bracket hole (P9 HOSE_BRACKET is on the valance at |y| 470: through the wheel house)
        hx, hy, hz = FS.HOSE_BRACKET
        p = p - zcyl(8.0, hz - 200, hz + 200, hx, hy)
        # electrical units' screws (P10)
        units = [BL.CONTROL_BOX, BL.FUSE_BOX, BL.FLASHER, BL.SOLENOID] if side < 0 else [BL.OD_RELAY]
        for ux, uy, uz in units:
            for dx in (-30.0, 30.0):
                p = p - ycyl(2.4, y0 - 5, y0 + 5, ux + dx, uz)
        return _l(_side(p, side), spec)
    return build


def front_apron(spec):
    """Front apron (cross panel under the grille): the vertical panel behind the bumper the horns bolt to (P10
    HORN_PANEL_X, HORN_POS), between the chassis legs' front ends, with the radiator duct's lower panel running back
    from its top edge to the radiator's front face, the duct's side panels, the grille's three bottom bolt holes
    and the bumper spring bar slots."""
    xa = BL.HORN_PANEL_X
    zt = S.z_of(S.MOUTH_BOT_H) - 6.0
    panel = box(xa, xa + T, -LEG_STEP_Y + LEG_W / 2, LEG_STEP_Y - LEG_W / 2, LEG_BOT - 60.0, zt)
    for hx, hy, hz in BL.HORN_POS:
        panel = panel - xcyl(4.2, xa - 5, xa + 5, hy, hz)
    for yy in (-300.0, 0.0, 300.0):                                     # lightening / air holes
        panel = panel - xcyl(32.0, xa - 5, xa + 5, yy * 0.5, LEG_BOT - 10.0)
    from mgb import cooling_layout as CO
    rad_front = CO.RAD_CORE[1] + 8.0
    duct_floor = box(rad_front, S.MOUTH_BACK_X - 2.0, -390.0, 390.0, zt - T, zt)
    for yy in (-160.0, 0.0, 160.0):
        duct_floor = duct_floor - zcyl(3.3, zt - 5, zt + 5, S.MOUTH_BACK_X - 20.0, yy)
    ztop = S.z_of(S.MOUTH_TOP_H) - 30.0
    sides = [box(rad_front, S.MOUTH_BACK_X - 2.0, s * 390.0 - (T if s > 0 else 0), s * 390.0 + (0 if s > 0 else T), zt, ztop)
             for s in (1, -1)]
    return _c([panel, duct_floor] + sides, spec)


def lock_platform(spec):
    """Bonnet lock platform: the cross panel over the grille opening, under the bonnet's front edge, with the lock's
    three bolt holes and the locating cup hole (Sec 6 para 4; photo 6.4) and the grille top steady brackets' three
    screw holes (Sec 7 para 1)."""
    z = S.z_of(S.MOUTH_TOP_H) - 30.0
    p = box(620.0, S.MOUTH_BACK_X - 2.0, -400.0, 400.0, z, z + T)
    p = p + box(620.0, 620.0 + T, -400.0, 400.0, z - 60.0, z)          # front flange down to the duct
    p = p - zcyl(14.0, z - 5, z + 5, 700.0, 0.0)
    for dy in (-32.0, 32.0):
        p = p - zcyl(3.3, z - 5, z + 5, 700.0, dy)
    p = p - zcyl(3.3, z - 5, z + 5, 730.0, 0.0)
    for yy in (-250.0, 0.0, 250.0):
        p = p - zcyl(2.6, z - 5, z + 5, S.MOUTH_BACK_X - 18.0, yy)
    return _l(p, spec)


# =====================================================================================================================
# sills and pillars
# =====================================================================================================================
SILL_X = (-200.0, -1830.0)
TREAD_H = 330.0
SILL_OUT_Y = 665.0


def inner_sill(side):
    def build(spec):
        """Inner sill: the vertical panel at underbody_layout SILL_Y from below the floor up to the sill tread, the tread
        turned outward to the door's shut line, the closing flange at the bottom; jacking socket hole a third of the
        way along the door ("case of the bends": the front chassis member ends at the jacking aperture level)."""
        xa, xb = SILL_X
        yi = S.SILL_INNER_Y
        zb = H(S.z_b(-1000.0)) + 4.0
        zt = H(TREAD_H)
        prof = [(yi, zb - 20.0), (yi, zt), (SILL_OUT_Y, zt), (SILL_OUT_Y, H(S.DOOR_BOTTOM_H) - 2.0)]
        p = G.sheet_x(prof, -T, xb, xa, 4.0)
        bottom = box(xb, xa, yi, S.w_b(-1000.0) - 12.0, zb - 20.0, zb - 20.0 + T)
        p = p + bottom
        p = p - ycyl(18.0, yi - 5, SILL_OUT_Y + 5, JACK_X, JACK_Z)
        return _l(_side(p, side), spec)
    return build


JACK_X = -1010.0
JACK_Z = H(230.0)


def castle(side):
    def build(spec):
        """Castle section: the reinforcing member inside the sill box, a vertical web with flanged castellations
        top and bottom spot-welded to the sill's inner and outer skins."""
        xa, xb = SILL_X
        y = (S.SILL_INNER_Y + SILL_OUT_Y) / 2 + 10.0
        zb = H(S.z_b(-1000.0)) - 14.0
        zt = H(TREAD_H) - T
        web = box(xb + 20.0, xa - 20.0, y, y + T, zb, zt)
        teeth = []
        n = 14
        for k in range(n):
            x0 = xb + 40.0 + k * (xa - xb - 80.0) / n
            teeth.append(box(x0, x0 + 45.0, y, y + 22.0, zt - T, zt))
            teeth.append(box(x0 + 50.0, x0 + 95.0, y - 22.0, y, zb, zb + T))
        p = G.fuse([web] + teeth)
        p = p - ycyl(18.0, y - 5, y + 5, JACK_X, JACK_Z)
        return _l(_side(p, side), spec)
    return build


def jack_socket(side):
    def build(spec):
        """Jacking socket: a square tube through the sill box (outer sill to inner sill) the jack's arm enters."""
        y0, y1 = S.SILL_INNER_Y, S.side_y(JACK_X, 230.0) - 0.5
        p = box(JACK_X - 15.0, JACK_X + 15.0, y0, y1, JACK_Z - 15.0, JACK_Z + 15.0)
        p = p - box(JACK_X - 12.5, JACK_X + 12.5, y0 - 1, y1 + 1, JACK_Z - 12.5, JACK_Z + 12.5)
        return _l(_side(p, side), spec)
    return build


def hinge_pillar(side):
    def build(spec):
        """Hinge (A) pillar: the box at the door's front shut line from the sill to the scuttle side, its shut face with
        the two hinges' three bolt holes each (Sec 32 para 1: the hinges bolt to the pillar), the kick panel inboard."""
        xf = S.DOOR_FRONT_X - S.GAP / 2
        hs = [TREAD_H] + [TREAD_H + (850.0 - TREAD_H) * k / 8 for k in range(1, 9)]
        outer = [(S.side_y(xf, h) - 2.0, H(h)) for h in hs]
        pts = [(S.SILL_INNER_Y, H(TREAD_H))] + outer + [(S.SILL_INNER_Y, H(850.0))]
        face = xprism(pts, xf - T, xf)
        kick = box(xf - 120.0, xf, S.SILL_INNER_Y, S.SILL_INNER_Y + T, H(TREAD_H), H(850.0))
        p = face + kick
        for hh in HINGE_H:
            for dz in (-18.0, 0.0, 18.0):
                p = p - xcyl(3.4, xf - 5, xf + 5, S.side_y(xf, hh) - 30.0, H(hh) + dz)
        return _l(_side(p, side), spec)
    return build


HINGE_H = (420.0, 735.0)
STRIKER_H = 640.0


def shut_pillar(side):
    def build(spec):
        """Shut (B) pillar: the panel at the door's rear shut line, leaning with it, the lock striker plate's three
        screw holes (Sec 27) and the drain at the foot."""
        xr = S.DOOR_REAR_X + S.GAP / 2
        hs = [TREAD_H + (850.0 - TREAD_H) * k / 8 for k in range(9)]
        lean = lambda h: S.DOOR_REAR_LEAN * (h - S.DOOR_BOTTOM_H) / (1100.0 - S.DOOR_BOTTOM_H)
        pts = [(S.SILL_INNER_Y + 20.0, H(TREAD_H))] + [(S.side_y(xr, h) - 2.0, H(h)) for h in hs] + \
              [(S.SILL_INNER_Y + 20.0, H(850.0))]
        p = xprism(pts, xr, xr + T)
        for dz in (-20.0, 0.0, 20.0):
            p = p - xcyl(3.0, xr - 5, xr + 5, S.side_y(xr, STRIKER_H) - 35.0, H(STRIKER_H) + dz)
        return _l(_side(p, side), spec)
    return build


# =====================================================================================================================
# rear structure
# =====================================================================================================================
HB_X = U.HEELBOARD_X
TON_Z = U.TONNEAU_Z
RB_X = S.REAR_BULKHEAD_X
RWH_Y = 498.0                              # rear wheel house inner walls
RAIL_Y = (RS.DAMPER_FACE_Y, 500.0)         # rear rails: inner face (P9 damper face) to outer face


def heelboard(spec):
    """Heelboard: the riser behind the seats from the floor up to the tonneau floor (rear face at underbody_layout
    HEELBOARD_X), sill to sill, with the propeller shaft's tunnel opening, a stiffening swage, the fuel pump
    bracket's two captive-nut holes (P11a parts/fuel/pump.py BRACKET_BOLT_Y/Z) and the fuel hose union's hole
    (fuel_supply_layout MAIN_START)."""
    x0 = HB_X
    yo = S.SILL_INNER_Y
    t = TUNNEL[-1]
    tun = [(y, z) for y, z in tunnel_profile(t, flange=0.0)]
    pts = [(yo, FLOOR_TOP)] + [(y, z) for y, z in tun] + [(-yo, FLOOR_TOP), (-yo, TON_Z), (yo, TON_Z)]
    p = xprism(pts, x0, x0 + T)
    p = p + (box(x0 - 3.0, x0, -yo + 40.0, yo - 40.0, -290.0, -276.0) - box(x0 - 4, x0 + 1, -t[1] - 20, t[1] + 20, -300, -270))
    from parts.fuel import pump as PU
    for y in PU.BRACKET_BOLT_Y:
        p = p - xcyl(4.2, x0 - 5, x0 + 5, y, PU.BRACKET_BOLT_Z)
    mx, my, mz = FL.MAIN_START
    p = p - xcyl(6.0, x0 - 5, x0 + 5, my, mz)
    p = _pass_cut(p, "heelboard")
    return _l(p, spec)


def tonneau_floor(spec):
    """Tonneau (rear) floor behind the seats, under which P10's two battery carriers hang (TONNEAU_FLOOR_Z): the
    floor from the heelboard to the rear bulkhead between the rear wheel houses, a rectangular access aperture over
    each carrier with the cover's quick-release screw holes (Haynes photo 2.1), the carriers' four flange bolt holes
    each, the damper access grommet holes beside them (Haynes photo 2.4) and the rear spring hanger reinforcement
    plates."""
    z = TON_Z
    p = box(RB_X, HB_X, -RWH_Y, RWH_Y, z, z + T)
    ix, iy, idp = BL.BATTERY_BOX_INNER
    fl = BL.BATTERY_BOX_FLANGE
    for s in (1, -1):
        cx, cy = BL.BATTERY_BOX_X, s * BL.BATTERY_BOX_Y
        p = p - zprism(G.rounded_rect(cx - ix / 2 + 4, cx + ix / 2 - 4, cy - iy / 2 + 4, cy + iy / 2 - 4, 12.0), z - 5, z + 5)
        for sx in (-1, 1):
            for sy in (-1, 1):
                p = p - zcyl(3.3, z - 5, z + 5, cx + sx * (ix / 2 + fl / 2), cy + sy * (iy / 2 - 20.0))
        p = p - zcyl(14.0, z - 5, z + 5, RS.DAMPER_SHAFT[0], s * 400.0)
    # pressed stiffening ribs fore and aft between the apertures
    for yy in (-60.0, 60.0):
        p = p + G.sheet_y([(HB_X - 30.0, z + T), (HB_X - 40.0, z + T + 6.0), (RB_X + 40.0, z + T + 6.0),
                           (RB_X + 30.0, z + T)], T, yy - 10.0, yy + 10.0, 3.0)
    return _l(p, spec)


def battery_cover(side):
    def build(spec):
        """Battery access cover: a flat panel over each carrier's aperture with a turned edge, held by two
        quick-release screws (Haynes photo 2.1)."""
        ix, iy, _ = BL.BATTERY_BOX_INNER
        cx, cy = BL.BATTERY_BOX_X, side * BL.BATTERY_BOX_Y
        z = TON_Z + T
        p = zprism(G.rounded_rect(cx - ix / 2 - 8, cx + ix / 2 + 8, cy - iy / 2 - 8, cy + iy / 2 + 8, 14.0), z, z + T)
        for sx in (-1, 1):
            p = p - zcyl(3.0, z - 1, z + 3, cx + sx * (ix / 2 - 2.0), cy)
        p = p + (zprism(G.rounded_rect(cx - ix / 2 + 6, cx + ix / 2 - 6, cy - iy / 2 + 6, cy + iy / 2 - 6, 10.0), z + T, z + T + 4.0)
                 - zprism(G.rounded_rect(cx - ix / 2 + 7.2, cx + ix / 2 - 7.2, cy - iy / 2 + 7.2, cy + iy / 2 - 7.2, 9.0), z + T - 1, z + T + 5.0))
        return _l(p, spec)
    return build


def rear_bulkhead(spec):
    """Rear bulkhead: the boot's front wall behind the hood stowage well, from the tonneau floor up under the rear
    deck, between the wheel houses, with a stiffening swage."""
    ztop = H(S.top_h(RB_X, 0.0)) - 40.0
    p = box(RB_X - T, RB_X, -RWH_Y, RWH_Y, TON_Z, ztop)
    p = p + (box(RB_X - T - 3.0, RB_X - T, -RWH_Y + 50.0, RWH_Y - 50.0, (TON_Z + ztop) / 2 - 10.0, (TON_Z + ztop) / 2 + 10.0))
    p = _pass_cut(p, "rear-bulkhead")
    return _l(p, spec)


def rear_wheelhouse(side):
    def build(spec):
        """Rear wheel house: the inner wall at |y| 498 from the floors up to the arch, the arched top band (430 mm
        radius about the axle: the tyre at full bump) out to the outer wing, closing the boot's sides over the
        wheels."""
        ax, az = CL.REAR_AXLE_X, CL.WHEEL_Z
        r = 430.0
        y0 = RWH_Y
        zw = -150.0
        arc = [(ax + r * math.cos(math.radians(a)), az + r * math.sin(math.radians(a))) for a in range(160, 19, -10)]
        wall = yprism([(ax + 470.0, zw), (ax - 470.0, zw)] + arc, y0, y0 + T)
        band = ycyl(r + T, y0, 714.0, ax, az) - ycyl(r, y0 - 1, 715.0, ax, az)
        band = band & box(ax - 520.0, ax + 520.0, y0, 700.0, H(S.z_b(ax) + 40.0), 2000.0)   # behind the outer skin
        return _l(_side(wall + band, side), spec)
    return build


def boot_floor(spec):
    """Boot floor: the kick-up over the axle (underside at underbody_layout ARCH_Z between ARCH_X, P9's bump strike)
    stepping down behind it to the floor over the tank (BOOT_FLOOR_Z) back to the rear panel; the filler stub's
    hole and seal seat (P11a FILLER), the spare wheel's locating ring pressing and clamp stud hole, the tank strap
    tabs (fronts on the step, P11a STRAP_PIN_FRONT) and the rear hanger tabs (HANGER_PIN), the exhaust rear
    bracket's two captive-nut holes (P11a), drain holes."""
    za, zb = U.ARCH_Z, U.BOOT_FLOOR_Z
    xa0, xa1 = RB_X, U.ARCH_X[1]
    xr = U.REAR_PANEL_X + 4.0
    yw = RWH_Y
    prof = [(RB_X, TON_Z), (RB_X - 26.0, za), (xa1, za), (xa1 - 2.0, zb), (xr, zb), (xr, zb + 40.0)]
    p = G.sheet_y(prof, T, -yw, yw, 8.0)
    # hump over the differential at the front of the kick-up, carrying P8's rear hose bracket underneath
    hx0, hx1 = HUMP_X
    p = p - box(hx1, hx0, -HUMP_Y, HUMP_Y, za - 1.0, za + T + 1.0)
    hump = box(hx1, hx0, -HUMP_Y, HUMP_Y, za, HUMP_Z + T) - box(hx1 + T, hx0 - T, -HUMP_Y + T, HUMP_Y - T, za - 1.0, HUMP_Z)
    p = p + hump
    behind = box(xr, U.ARCH_X[1] - 180.0, -690.0, -yw, zb, zb + T) + box(xr, U.ARCH_X[1] - 180.0, yw, 690.0, zb, zb + T)
    p = p + behind
    fx, fy = FL.FILLER
    p = p - zcyl(FL.FILLER_OD / 2 + 8.0, zb - 5, zb + 5, fx, fy)
    # spare wheel locating ring (pressed bead) and clamp stud
    sx, sy = SPARE_X, SPARE_Y
    ring = zcyl(142.0, zb + T, zb + T + 6.0, sx, sy) - zcyl(128.0, zb, zb + 8.0, sx, sy)
    p = p + ring
    p = p - zcyl(5.0, zb - 5, zb + 5, sx, sy)
    from parts.fuel import exhaust as EX
    for dx in (-14.0, 14.0):
        p = p - zcyl(3.4, zb - 5, zb + 5, EX.RX + dx, EX.BR_TAB_Y + 26.0)
    for xd, yd in ((-2600.0, 350.0), (-2600.0, -420.0)):
        p = p - zcyl(9.0, zb - 5, zb + 5, xd, yd)
    p = _pass_cut(p, "boot-floor")
    return _l(p, spec)


HUMP_X = (-1985.0, -2075.0)              # raised over the differential (P8 REAR_HOSE_BRACKET hangs under it)
HUMP_Y = 240.0
HUMP_Z = BK.REAR_HOSE_BRACKET[2] + 2.5
SPARE_X = -2628.0
SPARE_Y = 125.0


def tank_tabs(spec):
    """Body tabs for P11a's tank straps: two front tabs on the boot floor step with the clevis pin holes
    (STRAP_PIN_FRONT) and two rear hanger tabs under the floor (HANGER_PIN), at both straps (STRAP_Y)."""
    fx, fz = FL.STRAP_PIN_FRONT
    hx, hz = FL.HANGER_PIN
    zb = U.BOOT_FLOOR_Z
    out = []
    for ys in FL.STRAP_Y:
        for yy in (ys - 17.0, ys + 13.0):
            t = box(fx - 14.0, fx + 12.0, yy, yy + 2.0, fz - 14.0, U.ARCH_Z if fx > U.ARCH_X[1] else zb)
            t = t - ycyl(3.4, yy - 1, yy + 3, fx, fz)
            out.append(t)
            h = box(hx - 14.0, hx + 14.0, yy, yy + 2.0, hz - 14.0, zb)
            h = h - ycyl(3.4, yy - 1, yy + 3, hx, hz)
            out.append(h)
    return _c(out, spec)


def rail_bottom(x):
    """Underside of the rear chassis rail at x (side view): level behind the heelboard over the spring's front hanger,
    kicking up over the axle to P9's bump strike face (ARCH_Z), down a little to the shackle bracket at the rear."""
    pts = [(-1440.0, -300.0), (-1620.0, -266.0), (-1900.0, -246.0), (-1990.0, -190.0), (-2050.0, U.ARCH_Z),
           (-2290.0, U.ARCH_Z), (-2360.0, -205.0), (-2600.0, -210.0), (-2900.0, -212.0)]
    return S._interp(S.mono(pts), x)


def rail_top(x):
    """Top of the rear rail: under the tonneau floor, over the axle (inside the boot's side corners), then the boot
    floor's underside behind the kick-up (the rail is a channel welded under it)."""
    pts = [(-1440.0, -232.0), (-1900.0, -176.0), (-1990.0, -120.0), (-2050.0, -52.0), (-2311.0, -52.0),
           (-2340.0, U.BOOT_FLOOR_Z), (-2900.0, U.BOOT_FLOOR_Z)]
    return S._interp(S.mono(pts), x)


def rear_rail(side):
    def build(spec):
        """Rear chassis rail: top-hat box section along each side from the heelboard to the rear panel, kicked up over
        the axle; the damper's two mounting bolts through its inner face on a doubler plate (P9 DAMPER_MOUNT, along
        y), the spring's front hanger plates either side of the eye (FRONT_HANGER), the rear shackle bracket
        (SHACKLE_BRACKET), the rebound strap's bolt bracket (REBOUND_BOLT) and the bump rubber strike plate
        (BUMP_STRIKE)."""
        y0, y1 = RAIL_Y
        xs = [-1440.0 - k * 1460.0 / 40 for k in range(41)]
        bot = [(x, rail_bottom(x)) for x in xs]
        top = [(x, rail_top(x)) for x in reversed(xs)]
        outline = bot + top
        rail = yprism(outline, y0, y1) - (yprism(outline, y0 + T, y1 - T) & box(-2899.0, -1441.0, -2000, 2000, -1000, 1000))
        rail = rail - box(-2900.0, -1440.0, y0 + T, y1 - T, -1000.0, -1000.0 + 1)
        parts = [rail]
        # damper doubler plate on the inner face, down to the bolts (P9)
        (dx0, dy, dz), (dx1, _, _) = RS.DAMPER_MOUNT[1]
        dbl = box(min(dx0, dx1) - 30.0, max(dx0, dx1) + 30.0, y0 - 2.5, y0, dz - 30.0, rail_bottom((dx0 + dx1) / 2) + 40.0)
        for bx in (dx0, dx1):
            dbl = dbl - ycyl(5.0, y0 - 5, y0 + 5, bx, dz)
        parts.append(dbl)
        # front hanger plates (two, either side of the eye)
        hx, hy, hz = RS.FRONT_HANGER[1]
        for yy in (hy - 32.0, hy + 29.0):
            pl = box(hx - 40.0, hx + 40.0, yy, yy + 3.0, hz - 26.0, rail_bottom(hx) + 10.0)
            pl = pl - ycyl(6.6, yy - 1, yy + 4, hx, hz)
            parts.append(pl)
        # shackle bracket (pin along y)
        sx, sy, sz = RS.SHACKLE_BRACKET[1]
        for yy in (sy - 34.0, sy + 31.0):
            pl = box(sx - 30.0, sx + 30.0, yy, yy + 3.0, sz - 22.0, rail_bottom(sx) + 10.0)
            pl = pl - ycyl(6.6, yy - 1, yy + 4, sx, sz)
            parts.append(pl)
        # rebound strap bracket on the outer face (bolt along y)
        rx, ry, rz = RS.REBOUND_BOLT[1]
        br = box(rx - 22.0, rx + 22.0, y1, y1 + 3.0, rz - 20.0, rail_bottom(rx) + 30.0) - ycyl(5.0, y1 - 1, y1 + 4, rx, rz)
        parts.append(br)
        # bump strike plate under the rail at the axle line
        bx, by, bz = RS.BUMP_STRIKE[1]
        parts.append(box(bx - 45.0, bx + 45.0, by - 30.0, by + 30.0, bz, bz + 3.0) - box(bx - 46, bx + 46, -1, y0, bz - 1, bz + 4))
        c = Compound(G.solids(parts))
        if side < 0:
            c = c.mirror(__import__("build123d").Plane.XZ)
        c.label = spec.id
        return c
    return build


def rear_hose_bracket(spec):
    """Body bracket for P8's rear brake hose (brake_layout REAR_HOSE_BRACKET): an angle under the floor's kick-up,
    its foot with the hose's locknut hole."""
    x, y, z = BK.REAR_HOSE_BRACKET
    ztop = HUMP_Z
    p = box(x - 20.0, x + 20.0, y - 16.0, y + 16.0, z, z + 2.5) + box(x - 20.0, x + 20.0, y + 14.0, y + 16.0, z, ztop)
    p = p - zcyl(6.5, z - 1, z + 4, x, y)
    return _l(p, spec)


def handbrake_abutment(spec):
    """Handbrake cable front abutment bracket (P8 CABLE_ABUTMENT, 'A' in Fig 9.10): a bracket welded inside the
    tunnel's right wall behind the operating lever, the outer cable's ferrule hole."""
    x, y, z = BK.CABLE_ABUTMENT
    wall = -U.TUNNEL_Y
    p = box(x - 12.0, x - 9.0, wall + T, y + 14.0, z - 14.0, z + 14.0) - xcyl(4.2, x - 13, x - 8, y, z)
    p = p + box(x - 12.0, x + 30.0, wall + T, wall + T + 2.5, z - 14.0, z + 14.0)
    return _l(p, spec)


def cable_grommet(spec):
    """Rubber grommet for P10's battery cable through the toe board (CABLE_GROMMET)."""
    from mgb.chassis_geom import zrev
    gx, gy, gz = BL.CABLE_GROMMET
    g = zrev([(5.0, -6.0), (14.0, -6.0), (14.0, -3.0), (11.0, -3.0), (11.0, 3.0), (14.0, 3.0), (14.0, 6.0), (5.0, 6.0)])
    return _l(g.moved(Location((gx, gy, gz))), spec)


# ---- P10b wiring passes and clips ---------------------------------------------------------------------------------
def harness_passes():
    """(name, point, axis) where P10b's wires pass a body panel (mgb.wiring_layout routes), for the holes and
    grommets: axis is the panel's normal."""
    from mgb import wiring_layout as W
    rb_y = W.NODES["re.arch"][1]
    tx, ty, _ = W.NODES["tank.n"]
    return [("rear-bulkhead", (RB_X - T / 2, rb_y, W.NODES["re.arch"][2]), "x"),
            ("heelboard-pump", (HB_X + T / 2, -428.0, -344.0), "x"),
            ("boot-floor-tank", (tx - 4.0, ty - 6.0, U.BOOT_FLOOR_Z + T / 2), "z"),
            ("tunnel-overdrive", (-430.0, tunnel_halfwidth(-430.0, -120.0) + T / 2, -120.0), "y"),
            ("toe-dip", (-445.0, -165.0, U.toe_z(-445.0) + T / 2), "z")]


def _pass_cut(p, which, r=9.0):
    for name, (x, y, z), ax in harness_passes():
        if name.startswith(which):
            if ax == "x":
                p = p - xcyl(r, x - 8, x + 8, y, z)
            elif ax == "y":
                p = p - ycyl(r, y - 8, y + 8, x, z)
            else:
                p = p - zcyl(r, z - 8, z + 8, x, y)
    return p


def harness_grommets(spec):
    """Rubber grommets in the wiring passes (harness_passes)."""
    from mgb.chassis_geom import xrev, zrev
    prof = [(5.0, -5.0), (13.0, -5.0), (13.0, -2.0), (9.0, -2.0), (9.0, 2.0), (13.0, 2.0), (13.0, 5.0), (5.0, 5.0)]
    out = []
    for name, (x, y, z), ax in harness_passes():
        if ax == "x":
            g = xrev(prof).moved(Location((x, y, z)))
        elif ax == "z":
            g = zrev(prof).moved(Location((x, y, z)))
        else:
            g = (Rot(90, 0, 0) * zrev(prof)).moved(Location((x, y, z)))
        out.append(g)
    return _c(out, spec)


def _p_clip(x, y, z, normal, along):
    """P-clip on a panel: a 12 mm band looped round the bundle, its tab screwed to the face. normal: unit vector off
    the face; along: the bundle's direction (axis letter)."""
    from build123d import Axis
    nx, ny, nz = normal
    loop = None
    r0, r1, w = 9.0, 10.0, 12.0
    c = (x + nx * 12.0, y + ny * 12.0, z + nz * 12.0)
    if along == "x":
        loop = xcyl(r1, c[0] - w / 2, c[0] + w / 2, c[1], c[2]) - xcyl(r0, c[0] - w, c[0] + w, c[1], c[2])
    elif along == "y":
        loop = ycyl(r1, c[1] - w / 2, c[1] + w / 2, c[0], c[2]) - ycyl(r0, c[1] - w, c[1] + w, c[0], c[2])
    else:
        loop = zcyl(r1, c[2] - w / 2, c[2] + w / 2, c[0], c[1]) - zcyl(r0, c[2] - w, c[2] + w, c[0], c[1])
    tab = box(min(x, x + nx * 3.0) - (w / 2 if along == "x" else 8.0), max(x, x + nx * 3.0) + (w / 2 if along == "x" else 8.0),
              min(y, y + ny * 3.0) - (w / 2 if along == "y" else 8.0), max(y, y + ny * 3.0) + (w / 2 if along == "y" else 8.0),
              min(z, z + nz * 3.0) - (w / 2 if along == "z" else 8.0), max(z, z + nz * 3.0) + (w / 2 if along == "z" else 8.0))
    return [loop, tab]


HARNESS_CLIPS = ([(x, s * BL.INNER_WING_Y, 118.0, (0.0, -s, 0.0), "x") for s in (1, -1) for x in (-250.0, 0.0, 250.0)]
                 + [(560.0 + 20.0, y, -40.0, (1.0, 0.0, 0.0), "y") for y in (-300.0, 0.0, 300.0)]
                 + [(BL.FACIA_X + 120.0, y, 277.0 - 14.0, (0.0, 0.0, -1.0), "y") for y in (-280.0, 0.0, 280.0)]
                 + [(x, -S.SILL_INNER_Y, -350.0, (0.0, 1.0, 0.0), "x") for x in (-700.0, -1000.0, -1300.0)])


def harness_clips(spec):
    """P-clips holding P10b's harness runs to the body (HARNESS_CLIPS: inner wing tops, front panel, facia rail,
    right sill)."""
    out = []
    for x, y, z, n, a in HARNESS_CLIPS:
        out += _p_clip(x, y, z, n, a)
    return _c(out, spec)


def arch_liners(spec):
    """Wheel arch returns (D: Oliver's photos 02, 09, 23 show the arches dark inside): a band just inside each wing's
    arch opening, from the skin in toward the wheel house, finished in underseal like the wheel houses behind."""
    out = []
    for (ax, az, r) in (S.FRONT_ARCH, S.REAR_ARCH):
        for s in (1, -1):
            band = ycyl(r + 4.0, 470.0, 752.0, ax, az) - ycyl(r + 2.8, 460.0, 760.0, ax, az)
            band = band & box(ax - r - 10.0, ax + r + 10.0, 470.0, 752.0, H(S.z_b(ax) + 6.0), az + r + 10.0)
            out.append(_side(band, s))
    return _c(out, spec)


PARTS = {
    "body.structure.arch-liners": {"build": arch_liners},
    "body.structure.tunnel": {"build": tunnel},
    "body.structure.floor-l": {"build": floor_half(1)},
    "body.structure.floor-r": {"build": floor_half(-1)},
    "body.structure.floor-bung": {"build": floor_bung},
    "body.structure.toe-board-l": {"build": toe_board(1)},
    "body.structure.toe-board-r": {"build": toe_board(-1)},
    "body.structure.bulkhead": {"build": bulkhead},
    "body.structure.column-toe-mount": {"build": column_toe_mount},
    "body.structure.clutch-hose-support": {"build": clutch_hose_support},
    "body.structure.scuttle-inner": {"build": scuttle_inner},
    "body.structure.wiper-motor-bracket": {"build": wiper_motor_bracket},
    "body.structure.column-top-bracket": {"build": column_top_bracket},
    "body.structure.front-leg-l": {"build": front_leg(1)},
    "body.structure.front-leg-r": {"build": front_leg(-1)},
    "body.structure.inner-wing-l": {"build": inner_wing(1)},
    "body.structure.inner-wing-r": {"build": inner_wing(-1)},
    "body.structure.front-apron": {"build": front_apron},
    "body.structure.lock-platform": {"build": lock_platform},
    "body.structure.inner-sill-l": {"build": inner_sill(1)},
    "body.structure.inner-sill-r": {"build": inner_sill(-1)},
    "body.structure.castle-l": {"build": castle(1)},
    "body.structure.castle-r": {"build": castle(-1)},
    "body.structure.jack-socket-l": {"build": jack_socket(1)},
    "body.structure.jack-socket-r": {"build": jack_socket(-1)},
    "body.structure.hinge-pillar-l": {"build": hinge_pillar(1)},
    "body.structure.hinge-pillar-r": {"build": hinge_pillar(-1)},
    "body.structure.shut-pillar-l": {"build": shut_pillar(1)},
    "body.structure.shut-pillar-r": {"build": shut_pillar(-1)},
    "body.structure.heelboard": {"build": heelboard},
    "body.structure.tonneau-floor": {"build": tonneau_floor},
    "body.structure.battery-cover-l": {"build": battery_cover(1)},
    "body.structure.battery-cover-r": {"build": battery_cover(-1)},
    "body.structure.rear-bulkhead": {"build": rear_bulkhead},
    "body.structure.rear-wheelhouse-l": {"build": rear_wheelhouse(1)},
    "body.structure.rear-wheelhouse-r": {"build": rear_wheelhouse(-1)},
    "body.structure.boot-floor": {"build": boot_floor},
    "body.structure.tank-tabs": {"build": tank_tabs},
    "body.structure.rear-rail-l": {"build": rear_rail(1)},
    "body.structure.rear-rail-r": {"build": rear_rail(-1)},
    "body.structure.rear-hose-bracket": {"build": rear_hose_bracket},
    "body.structure.handbrake-abutment": {"build": handbrake_abutment},
    "body.structure.cable-grommet": {"build": cable_grommet},
    "body.structure.harness-grommets": {"build": harness_grommets},
    "body.structure.harness-clips": {"build": harness_clips},
}
