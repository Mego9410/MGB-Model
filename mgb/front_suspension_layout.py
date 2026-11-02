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


# =================================================================================================
# P9 additions: front suspension, front hub, steering arm and wheel datums (car frame unless stated).
# =================================================================================================
# What Haynes fixes (Ch 11, printed p202-205, 210): independent coil spring and wishbones, the upper arm
# formed by the double arms of the lever damper; damper arm centres 8 in (203.2 mm) front; coil spring free
# height 9.9 in (18G); camber 1 deg positive, castor 7 deg, king pin inclination 8 deg (static unloaded);
# wheel bearing end float 0.002-0.004 in; the stack on the swivel pin (Fig 11.2 items 46-61) and the hub
# (items 67-77). The wheel axis stays level (P8 contract): the published 1 deg of camber is recorded on the
# swivel axle's spec but not drawn, so the disc, caliper and hub keep P8's frame.
#
# Derived (D), not published: every station below. Proportions from Fig 11.1 (front view, scaled on the
# disc faces at |y| DISC_FACE_Y): the damper shaft about 305 mm from the centre line, the top trunnion's
# fulcrum and the swivel pin's lower eye just inboard of the disc, the lower wishbone dropping a little
# toward its outer end, the spring outboard of the damper.
CAMBER_DEG = 1.0                                  # H p202, not applied (wheel axis level, see above)
CASTOR_DEG = 7.0                                  # H p202: king pin top rearward
KPI_DEG = 8.0                                     # H p202: king pin top inboard
KP_Y0 = 490.0                                     # |y| where the king pin axis crosses wheel-centre height
_tc, _tk = math.tan(math.radians(CASTOR_DEG)), math.tan(math.radians(KPI_DEG))
_n = math.sqrt(_tc * _tc + _tk * _tk + 1.0)
KP_DIR = (-_tc / _n, -_tk / _n, 1.0 / _n)          # unit vector up the king pin, left-hand corner, car axes


def kp(h):
    """Point on the left-hand king pin axis at height h above the wheel centre (car frame)."""
    return (FX - h * _tc, KP_Y0 - h * _tk, FZ + h)


def kp_frame(h=0.0, side=1):
    """Location with origin on the king pin axis at height h, local z up the pin, local x as near car x as
    the pin allows; for side -1 the right-hand pin (a proper frame: parts placed in it are round about the pin)."""
    from build123d import Plane, Vector
    o = kp(h)
    o = (o[0], side * o[1], o[2])
    zd = Vector(KP_DIR[0], side * KP_DIR[1], KP_DIR[2])
    xd = Vector(1, 0, 0) - zd * zd.X
    loc = Location(Plane(origin=o, x_dir=xd.normalized(), z_dir=zd))
    return loc


# swivel pin stack, heights h along the axis above the wheel centre crossing (Fig 11.2 order, bottom up)
LOWER_EYE_H = -135.0                              # centre of the swivel pin's lower eye (pivot bolt 30, along x)
EYE_HALF = 32.0                                   # eye boss half length (distance tube 25 inside)
PIN_D = 20.0                                      # swivel pin bearing diameter (D)
PIN_BASE_TOP_H = -112.0                           # top of the pin's base boss (cork ring 53 on it)
CORK_T = 3.0
DUST_LOWER_H = (PIN_BASE_TOP_H + CORK_T, -76.0)   # lower dust excluder tube 54
DUST_UPPER_H = (-86.0, -64.0)                     # upper dust excluder tube 56, over the lower one
SWIVEL_H = (-62.0, 62.0)                          # swivel axle boss, bushes 50/51 at its ends
BUSH_L = 30.0
THRUST_T = 1.6                                    # steel thrust washer 57
FLOAT_T = 0.0545 * IN                             # bronze floating thrust washer 58, 0.052-0.057 in (H p205)
TRUNNION_H0 = SWIVEL_H[1] + THRUST_T + FLOAT_T    # trunnion (59) underside
TOP_FULCRUM_H = 110.0                             # fulcrum pin 11 centre height
TRUNNION_EYE_OUT = 24.0                           # fulcrum eye outboard of the pin
TRUNNION_TOP_H = TRUNNION_H0 + 56.0
PIN_TOP_H = TRUNNION_TOP_H + 16.0                 # threaded end above the nut 60
PIN_THREAD = "1/2"                                # swivel pin top thread (D)

TOP_FULCRUM = (kp(TOP_FULCRUM_H)[0], kp(TOP_FULCRUM_H)[1] + TRUNNION_EYE_OUT, kp(TOP_FULCRUM_H)[2])
LOWER_PIVOT = kp(LOWER_EYE_H)                     # pivot bolt 30 axis (along x) passes here

# lever damper (Fig 11.2 item 8): shaft along x, its two arms reach the fulcrum pin (H: arm centres 8 in)
DAMPER_ARM = 8.0 * IN
DAMPER_SHAFT_Y = 305.0
DAMPER_SHAFT = (TOP_FULCRUM[0], DAMPER_SHAFT_Y,
                TOP_FULCRUM[2] + math.sqrt(DAMPER_ARM ** 2 - (TOP_FULCRUM[1] - DAMPER_SHAFT_Y) ** 2))
DAMPER_BASE_Z = DAMPER_SHAFT[2] - 38.0            # body's mounting face on the crossmember tower top
DAMPER_ARM_X = 36.0                               # each arm's centre plane fore and aft of the shaft's x
DAMPER_BOLTS = [(DAMPER_SHAFT[0] + dx, DAMPER_SHAFT_Y - 40.0 + dy, DAMPER_BASE_Z) for dx in (-44.0, 44.0) for dy in (-30.0, 30.0)]

# lower wishbone (items 20, 33): inner pivot along x under the crossmember, outer on the pivot bolt
WISHBONE_INNER = (FX, 200.0, LOWER_PIVOT[2] + 17.5)
WISHBONE_ARM_X = 72.0                             # arm web centres fore and aft at the inner pivot
WISHBONE_OUT_X = 42.0                             # and at the outer (either side of the swivel pin eye)
PAN_Y = 405.0                                     # spring axis |y| (D: Fig 11.1, outboard of the damper)


def wishbone_z(y):
    """Height of the wishbone arm centre line at |y| (straight from inner pivot to outer pivot)."""
    y0, z0 = WISHBONE_INNER[1], WISHBONE_INNER[2]
    y1, z1 = LOWER_PIVOT[1], LOWER_PIVOT[2]
    return z0 + (z1 - z0) * (y - y0) / (y1 - y0)


def arm_x(fore, y):
    """x of the front (fore +1) or rear (-1) wishbone arm's web centre at |y|."""
    x0 = WISHBONE_INNER[0] + fore * WISHBONE_ARM_X
    x1 = LOWER_PIVOT[0] + fore * WISHBONE_OUT_X
    return x0 + (x1 - x0) * (y - WISHBONE_INNER[1]) / (LOWER_PIVOT[1] - WISHBONE_INNER[1])


SPRING_X = (arm_x(1, PAN_Y) + arm_x(-1, PAN_Y)) / 2      # spring axis x: centred between the arms
PAN_SEAT_Z = wishbone_z(PAN_Y) - 22.0             # spring bottom on the pan's dished seat
SPRING_TOP_Z = -237.5                             # spigot flange underside, under the shelf (XM_SHELF_Z - XM_T - 2.5)
SPRING_INSTALLED = SPRING_TOP_Z - PAN_SEAT_Z      # static laden length (D)

# front crossmember (item 1): a pressed box beam, centre section dipped under the sump; towers each end
XM_X = (FX - 66.0, FX + 70.0)                     # rear and front faces of the beam
XM_T = 3.0
XM_TOWER_TOP = DAMPER_BASE_Z                      # damper platform
XM_TOWER_Y = (215.0, 350.0)                       # platform extent |y|
XM_SHELF_Z = -232.0                               # outer shelf: chassis leg seat, spring seat underneath
XM_SHELF_Y = (368.0, 458.0)
XM_DIP_TOP = -428.0                               # centre top, just under the sump (sump floor -421.2, D)
XM_DIP_Y = 128.0                                  # dip half width before the sides rise
XM_LOW_Z = CL.GROUND_Z + 4.2 * IN                 # underside of the dip: the published 4.2 in ground clearance
XM_BOTTOM_Z = WISHBONE_INNER[2] + 21.0            # beam underside at the wishbone pivots
XM_EAR_X = 96.0                                   # body mounting ears fore and aft of FX on the shelf
BODY_BOLT_Y = 432.0                               # crossmember to body support bolts (item 2), two each side
BODY_BOLT_X = (FX - 80.0, FX + 84.0)
BODY_FACE_Z = XM_SHELF_Z + 6.0                    # upper rubber pad (3) on the shelf: chassis leg underside (P11)
BODY_PAD_T = 6.0                                  # upper and lower rubber pads (3, 4)
BODY_BOLTS = {s: [(x, s * BODY_BOLT_Y, BODY_FACE_Z) for x in BODY_BOLT_X] for s in (1, -1)}
                                                  # P11: front chassis leg underside faces; the bolts pass up through
SPRING_TOP_SEAT_Z = XM_SHELF_Z - XM_T             # shelf underside
WISHBONE_PIVOT_BOLTS = [WISHBONE_INNER[0] - 24.0, WISHBONE_INNER[0] + 24.0]   # x of bolts 34, up into the beam
REBOUND_BUFFER = (DAMPER_SHAFT[0] + DAMPER_ARM_X, 382.0, -205.0)   # buffer 40 on a ledge on the tower wall, under the
                                                  # damper's front arm (stops it on rebound)
SPIGOT_SCREWS = [(SPRING_X - 44.0, 380.0), (SPRING_X + 44.0, 380.0)]
ENGINE_MOUNT_Y = 166.0                            # crossmember's engine mounting brackets, |y| of the pad centre
ENGINE_MOUNT_ANGLE = 40.0                         # pad face tilt from horizontal, facing up and inboard
ENGINE_MOUNT_PAD = (XM_X[1] - 15.0, ENGINE_MOUNT_Y, -295.0)   # pad face centre (x, |y|, z)
BODY_LEG_TOP_Z = BODY_FACE_Z + 50.0               # P11: top of the chassis leg where nuts 7 sit (D)
RACK_AXIS = (XM_X[1] + 62.0, -362.0)              # (x, z) of the rack housing axis (Fig 11.6), ahead of the beam
RACK_CLAMP_Y = 196.0                              # |y| of the two rack clamps on the crossmember bosses
RACK_SHIM_T = 0.020 * IN                          # one shim each side (H p212: shims 0.020 in)
RACK_BOSS_TOP = RACK_AXIS[1] - 22.0 - RACK_SHIM_T - 3.0   # boss tops (rack bracket feet 3 mm thick under the housing pads)
RACK_BOLT_DX = 30.0                               # clamp bolts fore and aft of the rack axis, vertical into the bosses

# front hub, wire wheels (item 67): stations |y| outward, hub frame
STUB_ROOT_Y = SHIELD_FACE_Y                       # swivel axle pads / stub axle shoulder
COLLAR_Y = (SHIELD_FACE_Y + SHIELD_T, 546.0)      # oil seal collar 68
SEAL_Y = (546.0, 555.0)                           # oil seal 69 in the hub's inner end
# wire wheel splined extension of the hub: stations matched to the rear (rear_axle_layout) so the same wheel
# sits on both: inner cone start 10.5 mm inboard of the wheel centre plane
EXT_COLLAR_Y = (WHEEL_PLANE_Y - 10.5, WHEEL_PLANE_Y + 14.5)
EXT_CONE_R = (33.0, 27.5)
EXT_SPLINE_Y = (EXT_COLLAR_Y[1], EXT_COLLAR_Y[1] + 72.0)
EXT_SPLINE = (36, 42.0, 39.4)
EXT_THREAD_Y = (EXT_SPLINE_Y[1] + 2.0, EXT_SPLINE_Y[1] + 32.0)
EXT_THREAD_D = 39.0
EXT_TPI = 12                                      # to GHN3-30850 (MGOC BTB346/BTB347)
HUB_BORE_R = 17.0                                 # bore in the splined end round the nut (split pin through it)
IN_BRG = (31.75, 62.0, 17.5)                      # inner taper roller bearing 70 (bore, OD, width; D)
IN_BRG_Y = (556.0, 556.0 + IN_BRG[2])
OUT_BRG = (19.05, 45.24, 15.49)                   # outer bearing 73 (D: LM11949/LM11910 size)
OUT_BRG_Y = (EXT_COLLAR_Y[0] + 1.0, EXT_COLLAR_Y[0] + 1.0 + OUT_BRG[2])   # under the inner cone
SPACER_Y = (IN_BRG_Y[1], OUT_BRG_Y[0] - 0.076)    # spacer 71, then one 0.003 in shim 72
WASHER_Y = (OUT_BRG_Y[1], OUT_BRG_Y[1] + 3.2)     # retaining washer 74
NUT_Y = (WASHER_Y[1], WASHER_Y[1] + 14.0)         # castellated nut 75
STUB_THREAD = "3/4"
STUB_END_Y = NUT_Y[1] + 5.0
HUB_IN_Y = SEAL_Y[0] - 0.5                        # hub's inner end
HUB_BARREL_R = 39.5                               # inside the disc's centre hole (DISC_BORE_R)
SPINNER_HAND = {1: "right", -1: "left"}           # as the rear (MGOC: right-hand side of the car, LH thread)

# steering lever (item 62) on the swivel axle, tie-rod end ball pin (Fig 11.6 item 30)
ARM_BALL = (FX + 130.0, 506.0, FZ - 76.0)         # ball pin centre at the lever's eye (|y|)
ARM_PAD_H = -38.0                                 # lever's bolting pad on the swivel axle, height on the pin
ARM_BOLT_X = (FX + 28.0, FX + 52.0)               # two bolts 63 (D)


def side_pt(side, p):
    """Left-hand point (x, |y|, z) on one side."""
    return (p[0], side * p[1], p[2])
