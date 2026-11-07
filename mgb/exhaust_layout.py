"""Exhaust system (P11a): the early one-piece welded system, 18G engine, three-synchro overdrive gearbox, chrome
bumper roadster. Car frame (mgb.car_layout). Every route below is a list of pipe centre-line points; the parts
sweep tube along them and the mountings sit on them.

What Haynes fixes (Ch 3 Sec 46, printed p92; Ch 1 Sec 6 para 14 and photos 6.14(a), (b), printed p27; Ch 8 Sec 3
para 6, printed p142): on earlier types a one-piece welded assembly is fitted; it comes off by removing the nuts at
the manifold (note the sealing rings, photo 46.2), loosening the rear mounting pipe bolt and removing the front
support bolt; refit with every fixing loose until the manifold fixings are tight, then tighten from front to
rear. The pipe is held at the manifold by a clamp and at the gearbox by a clip (Ch 1), and under the car at "the
manifold clamp, and at the two brackets under the car" (Ch 8).

Supplier and club data (S): twin downpipes from the two manifold outlets (cylinders 1 and 4 by a Y in the
casting, the siamesed 2/3 port by the centre pipe) join ahead of a centre silencer of flattened oval section;
an interpipe runs back to a cylindrical rear silencer and the tail pipe, which leaves the car on the left; the
tail pipe originally cut at 45 degrees; 3-synchro gearbox cars have their own gearbox bracket; cars to 1970 a
pinch clamp rear mounting (MGOC Spares "MGB exhaust systems"); system pipe 1 7/8 in (MGOC Spares GEX9008 U
clamp 1 7/8 in); downpipe seals two per car (Rimmer Bros GEX130FKEARLY fitting kit, "downpipe seals, gearbox
strap ... rear mounting"); the system passes under the gearbox crossmember (Moss Motors 459-075 instructions:
"the tail end of the head pipe may touch the transmission cross member") and under the rear axle (same: the
mounting holes "lower the system enough to clear the rear axle").

Derived (D): every station. The downpipes drop from the manifold outlets beside the bellhousing, behind the
engine rear plate, and join behind the bellhousing; the single pipe passes under the crossmember; the centre
silencer lies under the left-hand floor beside the tunnel, clear of the floor by 8 mm and of the road by the
published 4.2 in minimum clearance; the interpipe runs back between the tunnel and P10's left-hand battery
carrier, under the axle's left neck and under the left-hand handbrake rod (P8) behind it, to the rear silencer
beside the tank (between it and the left road spring); the tail pipe ends at the bumper line. The gearbox clip
hangs on a bracket under the two lowest rear side-cover bolts (3-synchro gearboxes have the side cover on the
left, where the pipe runs); the rear mounting hangs from the boot floor.

Frames: the downpipes, the front pipe, the gearbox clip and the centre silencer are placed from the engine and
gearbox (engine frame: the silencer follows the gearbox crossmember); the interpipe's run under the cockpit and boot,
the rear silencer, the tail pipe and the rear mounting are placed from the body (body stations, car_layout.bx). If the
engine moves back in the body (P12, Oliver's scan), the interpipe's crossing from beside the tunnel to IP_Y ahead of
the left-hand battery carrier has to be re-fitted: the silencer's rear end then lies within 90 mm of the carrier.
"""
from __future__ import annotations

import math

from mgb import car_layout as CL, chassis_layout as CH, gearbox_layout as G, rear_axle_layout as A
from mgb import underbody_layout as U

IN = 25.4
DOWN_OD, DOWN_T = 1.5 * IN, 1.6                 # downpipes (D: 16 swg, sized to the outlets)
PIPE_OD, PIPE_T = 1.875 * IN, 1.6               # system pipe 1 7/8 in (S: MGOC GEX9008)

# ---- manifold outlets (the exhaust manifold casting is built to these) ---------------------------------------
OUTLET_FACE_Z = -132.0                          # underside of the manifold's outlet flange (P2 kept)
OUTLET_Y = 158.0
OUTLETS = {"front": (12.0, OUTLET_Y), "rear": (-32.0, OUTLET_Y)}   # (x, y): 1/4 by the Y, 2/3 by the centre pipe
OUTLET_BORE = 34.0                               # bore of each outlet
SEAT_D, SEAT_DEPTH = 44.0, 6.0                    # counterbore the sealing ring seats in
STUD_DY = 30.0                                    # two studs per outlet either side of it, across the car
STUDS = [(x, OUTLET_Y + s * STUD_DY) for x, _ in OUTLETS.values() for s in (-1, 1)]
STUD = "5/16"
FLANGE_T = 5.0                                   # downpipe flange plate (D)
RING_H = 8.0                                     # sealing ring height; it stands RING_H - SEAT_DEPTH below the face
FLANGE_TOP_Z = OUTLET_FACE_Z - (RING_H - SEAT_DEPTH)   # downpipe flange top face (the ring holds it off the casting)

# ---- routes (centre lines) -------------------------------------------------------------------------------------
RUN_Z = -412.0                                   # downpipes alongside and behind the bellhousing
Y_X = -440.0                                     # the two downpipes join here
XM_Z = -433.0                                    # under the gearbox crossmember (its flanges at about -395 here)
DOWN_ROUTES = {
    "front": [(12.0, OUTLET_Y, FLANGE_TOP_Z + 4.0), (12.0, OUTLET_Y, -205.0), (-60.0, 188.0, -330.0),
              (-170.0, 188.0, RUN_Z), (Y_X + 40.0, 188.0, RUN_Z)],
    "rear": [(-32.0, OUTLET_Y, FLANGE_TOP_Z + 4.0), (-32.0, OUTLET_Y, -195.0), (-95.0, 147.0, -320.0),
             (-190.0, 147.0, RUN_Z), (Y_X + 40.0, 146.0, RUN_Z)],
}
Y_CENTRE = (Y_X, 167.0, RUN_Z)                    # the Y: two downpipe sockets in, the system pipe out

CS_X = (-905.0, -1362.2)                          # centre silencer case, front and rear ends (18 in)
CS_W, CS_H = 8.0 * IN, 80.0                       # flattened oval section (D)
CS_Y = U.TUNNEL_Y + CS_W / 2 + 12.0               # beside the tunnel
CS_Z = U.FLOOR_Z - 8.0 - CS_H / 2                 # 8 mm under the floor
FRONT_ROUTE = [(Y_X - 20.0, 160.0, RUN_Z), (-560.0, 160.0, RUN_Z), (CH.REAR_XMEMBER_X, 150.0, XM_Z),
               (-850.0, CS_Y, CS_Z), (CS_X[0] + 2.0, CS_Y, CS_Z)]

IP_Y = 110.0                                      # interpipe between the tunnel and the left battery carrier
IP_Z = -425.0
UNDER_AXLE = (A.AX + 20.0, 132.0, -405.0)         # under the left neck
UNDER_ROD = (A.AX - 95.0, 214.0, -442.0)          # under the left handbrake rod (P8 comp_tip to the lever)
RS_X = (CL.bx(-2385.0), CL.bx(-2766.0))                       # rear silencer case (15 in)
RS_D = 4.5 * IN
RS_Y = 304.0                                      # between the tank (y <= 210) and the left spring (inner edge 398)
RS_Z = -362.0
INTER_ROUTE = [(CS_X[1] - 2.0, CS_Y, CS_Z), (CL.bx(-1410.0), CS_Y, CS_Z), (CL.bx(-1560.0), IP_Y, IP_Z), (CL.bx(-2040.0), IP_Y, IP_Z),
               UNDER_AXLE, UNDER_ROD, (CL.bx(-2330.0), RS_Y - 20.0, -385.0), (RS_X[0] + 2.0, RS_Y, RS_Z)]
# Tail pipe (QA fix round 1, Oliver's photo 25 scaled on the plate and kf062, kf165, kf166): straight out on the left
# 365 above the road (centre), the pipe's top tight to the rear valance's lower edge where it passes through a notch in
# it, a square-cut end standing out about 50 mm behind the valance under the bumper; it rises from the rear silencer's
# level just behind the rear mounting.
# QA fix round 2 (kf058, kf062, kf165): the rise is short and steep, tucked behind the valance's turned-under lower edge,
# so only the straight run shows from behind; the end stands out under the bumper blade (about 20 mm inside the
# overriders' rear faces).
TAIL_END_X = CL.REAR_X + 20.0
TAIL_Z = CL.GROUND_Z + 365.0
TAIL_Y = 352.0                                      # out to |y| 352 (photos 11, 14)
TAIL_RISE_X = (CL.bx(-2845.0), CL.bx(-2885.0))     # the rise from the silencer's level to TAIL_Z
TAIL_ROUTE = [(RS_X[1] + 2.0, RS_Y, RS_Z), (TAIL_RISE_X[0], RS_Y, RS_Z), (TAIL_RISE_X[1], TAIL_Y, TAIL_Z),
              (TAIL_END_X, TAIL_Y, TAIL_Z)]
TAIL_CUT_DEG = 0.0                                 # square cut on Oliver's car (kf165, kf166); MGOC: originally 45 degrees

# ---- gearbox clip (front support) ---------------------------------------------------------------------------------
BRACKET_T = 4.0                                    # flat bar bracket under the two side cover bolts
SIDE_COVER_BOLTS = (8, 9)                          # indices into parts.gearbox.casing SC_BOLTS (lowest, rearmost two)
CLIP_X = -523.0                                    # strap round the system pipe, between the two bolts
STRAP_W, STRAP_T = 22.0, 2.5

# ---- rear mounting (pinch clamp on a rubber block from a bracket under the boot floor) --------------------------
# on the level run between the silencer and the rise (QA fix round 1: with the tail pipe up at the valance there is no
# room for the block over it further back)
REAR_MOUNT_X = CL.bx(-2803.0)                  # clear of the silencer's outlet spigot (to -2790)
REAR_CLAMP = (REAR_MOUNT_X, RS_Y, RS_Z)            # pinch clamp round the tail pipe
REAR_RUBBER_Z = (RS_Z + 52.0, RS_Z + 82.0)         # bonded rubber block, bottom and top plate faces
REAR_BRACKET_Z = (REAR_RUBBER_Z[1], U.BOOT_FLOOR_Z)   # bracket from the block up to the boot floor


def seg_point(route, x):
    """Point on a route's polyline at a given x (between the first and last points)."""
    for a, b in zip(route, route[1:]):
        if min(a[0], b[0]) <= x <= max(a[0], b[0]) and a[0] != b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            return tuple(a[i] + t * (b[i] - a[i]) for i in range(3))
    raise ValueError(x)


def rod_left(af_y):
    """P8's left-hand handbrake rod at |y| (axle frame): (x, z) in the car frame, for the clearance check."""
    from mgb import brake_layout as B
    t0 = B.comp_tip("inner")
    t1 = (-50.0, 549.0, -100.0)
    t = (af_y - t0[1]) / (t1[1] - t0[1])
    return (A.AX + t0[0] + t * (t1[0] - t0[0]), A.AZ + t0[2] + t * (t1[2] - t0[2]))


CLIP_PIPE = seg_point(FRONT_ROUTE, CLIP_X)          # system pipe centre at the gearbox clip
