"""Front hub, swivel axle and disc brake datums (P8 brakes; P9 builds the hub, swivel axle and wheel on them).

Car frame as mgb.car_layout (X forward, Y to the car's left, Z up). The front hub frame (FH) of each wheel
has its origin on the wheel axis (car_layout FRONT_AXLE_X, WHEEL_Z) at the car centre line, axes as the car
frame; distances along the axle are |y| outward. Parts are drawn for the left-hand (near side) wheel; the
right-hand wheel's parts are the left-hand ones mirrored (handed parts: caliper, dust cover) or placed by
`place()` below (parts that are round about their own axis). The wheel axis is taken as level and square
to the car (static camber and king pin inclination are P9's to add; they turn this frame, not the stack).

What Haynes fixes (Ch 9, printed p146, 150-151): disc 10.75 in (273 mm), 0.34-0.35 in thick new; the disc
bolts to the hub with four bolts, washers and nuts (Sec 11 para 4; Fig 9.7 items 1-4: the bolt heads on the
disc side, the nuts on the hub flange); the two-piston caliper (mounting half and rim half) held by two
bolts under a tab washer, 40-45 lbf ft; the dust cover (stone guard) on bolts and spring washers, 17-19
lbf ft. Figs 9.2 and 9.3 draw the front calipers behind the wheel centre.

Supplier data (S): pistons 54 mm (bpnorthwest 8G8642 / 17H7989); disc-to-hub bolts with 3/8 UNF nuts and
spring washers, dust cover screws 5/16 UNF x 1/2 in (MGOC Spares "front brakes").

Derived (D), not published: every station and radius below. The disc's hat stands outboard (Fig 9.7: the
disc's centre face, with its four holes, is the outermost part of the disc and seats against the back of
the hub flange), so the friction ring lies 66 mm inboard of the wheel centre plane, inside the wire wheel's
inner rim; the caliper sits horizontally behind the axle (Figs 9.2, 9.3) with its two bolts parallel to the
axle, screwed into the mounting half from behind the swivel axle's caliper flange (heads and tab washer
inboard); the dust cover is held to the swivel axle by three screws round the stub axle.
"""
from __future__ import annotations

import math

from build123d import Location, Rot

from mgb import car_layout as CL

IN = 25.4
FX, FZ = CL.FRONT_AXLE_X, CL.WHEEL_Z
WHEEL_PLANE_Y = CL.TRACK_FRONT / 2                # 622.3: wheel centre plane

# ---- disc (H p146 diameter and thickness; stations D) -----------------------------------------------------
DISC_R = 10.75 * IN / 2                           # 136.525
DISC_T = 0.345 * IN                               # middle of 0.34-0.35 in
DISC_MID_Y = 556.0                                # friction ring mid plane
DISC_FACES_Y = (DISC_MID_Y - DISC_T / 2, DISC_MID_Y + DISC_T / 2)
RING_IN_R = 84.0                                  # inner edge of the swept ring
HAT_R = (60.0, 66.0)                              # hat wall, inside and outside
DISC_FACE_Y = 588.0                               # outboard face of the disc's centre plate = hub flange's inboard face (P9)
DISC_PLATE_T = 6.0
DISC_BORE_R = 41.0                                # centre hole round the stub axle and hub (P9 must fit inside)
DISC_BOLT_PCD = 100.0
DISC_BOLT_ANGLES = [45.0 + 90.0 * k for k in range(4)]    # in the x-z plane, from up toward the front
DISC_BOLT = "3/8"
HUB_FLANGE_Y = (DISC_FACE_Y, DISC_FACE_Y + 10.0)  # P9: hub flange the disc bolts through (nuts on its outer face)
HUB_FLANGE_R = 62.0

# ---- caliper (CF: caliper centre on the axle's horizontal, behind it) -----------------------------------
CALIPER_ANGLE = 270.0                             # from up toward the front: 270 = straight behind the axle
PISTON_D = 54.0                                   # S: bpnorthwest 8G8642
PISTON_R_AT = 106.0                               # piston axes, radius from the wheel axis
PISTON_L = 30.0
PAD_LINING_T = 9.5
PAD_BACK_T = 3.2
SHIM_T = 0.5
PAD_FACE = DISC_T / 2                             # pad lining face on the disc
BORE_MOUTH = PAD_FACE + PAD_LINING_T + PAD_BACK_T + SHIM_T + 0.8   # |dy| of each half's inner face from the mid plane
BORE_DEPTH = 33.0
HALF_DEPTH = 40.0                                 # each half: inner face to outer face
CALIPER_W = 2 * (BORE_MOUTH + HALF_DEPTH)         # overall across the halves
BODY_U = (76.0, 140.0)                            # radial extent of the cylinder bodies
BRIDGE_U = (140.0, 160.0)                         # bridge over the disc edge
BODY_V = 52.0                                     # half the body's width (tangential)
PAD_W, PAD_H = 76.0, 50.0                         # pad: tangential length, radial height (D, GBP202 shape)
BRIDGE_BOLT_V = 44.0                              # bridge bolts either side of the pad aperture
BRIDGE_BOLT_U = 151.0
BRIDGE_BOLT = "7/16"
PIN_V = 14.0                                      # pad retaining pins, either side of the centre, through both halves
PIN_U = 147.0
LUG_U = (56.0, 77.0)                              # mounting lugs below the body (toward the axis)
LUG_V = 40.0                                      # bolts 80 mm apart
CALIPER_MOUNT_FACE_Y = 512.0                      # lug faces = outboard face of the swivel axle's caliper flange (P9)
SWIVEL_CALIPER_FLANGE_T = 12.0                    # P9: flange the bolts pass through, heads inboard
CALIPER_BOLT = "7/16"
INLET = (120.0, -26.0)                            # (u, v) of the hose union on the mounting half's inboard face
BLEED_Y = DISC_MID_Y - BORE_MOUTH - 14.0          # bleed screw on top of the mounting half
PLUG_Y = DISC_MID_Y + BORE_MOUTH + 14.0           # blanking plug on top of the rim half

# ---- dust cover (stone guard) --------------------------------------------------------------------------
SHIELD_FACE_Y = 532.0                             # inboard face of its centre, on the swivel axle's pads (P9)
SHIELD_T = 1.2
SHIELD_SCREW_R = 58.0
SHIELD_SCREW_ANGLES = [0.0, 100.0, 200.0]         # from up toward the front
SHIELD_GAP = (CALIPER_ANGLE - 46.0, CALIPER_ANGLE + 46.0)   # open sector round the caliper

# ---- flexible hose bracket on the body (P11 builds the wing valance it is welded to) ---------------------
HOSE_BRACKET = (FX - 70.0, 470.0, FZ + 150.0)     # (x, |y|, z) car frame: hose end through it, axis vertical


def uv(u, v):
    """(x, z) of a caliper point at radius u from the wheel axis (straight back, CALIPER_ANGLE 270) and v
    across it (up)."""
    return -u, v


def ang(r, a):
    """(x, z) of a point at radius r, angle a from up toward the front."""
    return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))


def origin(side):
    return (FX, 0.0, FZ)


def place(side, p=(0.0, 0.0, 0.0), rot=None):
    """Location of a part drawn in the left-hand front hub frame at local point p (|y| outward), for one side.
    Parts round about an axis along y keep their axis outward on the right (turned half round z). Parts
    that are handed are mirrored instead (see parts.brakes.front.mirror_y)."""
    rot = rot if rot is not None else Rot(0, 0, 0)
    if side > 0:
        return Location((FX, 0.0, FZ)) * Location(p) * rot
    return Location((FX, 0.0, FZ)) * Rot(0, 0, 180) * Location((-p[0], p[1], p[2])) * rot


def car(side, p):
    """Left-hand front hub frame point -> car frame on one side."""
    return (FX + p[0], side * p[1], FZ + p[2])


# ---- datums for P9 (car frame) ---------------------------------------------------------------------------
HUB_FLANGE_INNER = {s: s * DISC_FACE_Y for s in (1, -1)}
CALIPER_BOLTS = {s: [car(s, (uv(LUG_U[0] + 8.0, v)[0], CALIPER_MOUNT_FACE_Y, uv(LUG_U[0] + 8.0, v)[1])) for v in (-LUG_V, LUG_V)]
                 for s in (1, -1)}
SHIELD_SCREWS = {s: [car(s, (ang(SHIELD_SCREW_R, a)[0], SHIELD_FACE_Y, ang(SHIELD_SCREW_R, a)[1])) for a in SHIELD_SCREW_ANGLES]
                 for s in (1, -1)}

# ---- notes added at the end of P8 (the datums above are fixed for P9) ------------------------------------
# PIN_U is not used: the pad retaining pins sit just over the pad clip at parts/brakes/front.py PIN_U (137.5 mm).
PAD_PIN_U = PISTON_R_AT + PAD_H / 2 + 4.0 + 0.8 + 1.7    # caliper pad pins, radius from the wheel axis
