"""Brakes (P8): datums for the rear drum brakes on the banjo axle, the brake master cylinder and pedal in the
pedal box, the handbrake, and the car-level brake pipe routes (P11 attaches clips and grommets to these).

Frames:
- Rear brakes are drawn in the axle frame AF of mgb.rear_axle_layout (origin on the axle centre, car axes)
  for the left-hand (near side) wheel; distances along the axle are |y| outward. Parts symmetric fore and
  aft are turned half round z for the right-hand wheel (as P7 does); handed parts (backplate, handbrake
  lever and its boot) are built mirrored.
- Front brakes: mgb.front_suspension_layout.
- Pedal box, master cylinders, handbrake lever and pipes: car frame.

What Haynes fixes (Ch 9, printed p146-160): drum internal diameter 10 in; the rear brake parts and their order
(Fig 9.9: backplate on four bolts, nuts and spring washers; two shoes with a pull-off spring at the cylinder
end and one at the adjuster end; a steady pin, spring and washer per shoe; the square-headed adjuster with two
tappets and a wedge, held by two nuts and spring washers behind the backplate (Sec 3 para 3, Sec 13 para 5);
the wheel cylinder with piston, seal and boot, held by a retaining clip, with its bleed screw; the handbrake
lever through the backplate with its boot; the drum, held on wire-wheel cars by the four nuts (Sec 13 para 3));
the single master cylinder and supply tank (Fig 9.11) beside the clutch master cylinder under a cover held by
four screws (Sec 17 para 1, photo 1.1), the longer bolt in the top hole (Sec 17 para 5); the hydraulic
layout (Fig 9.1: pipe from the master cylinder to a four-way connection carrying the stop lamp switch,
pipes to the front hoses, one to the rear hose and the three-way connection on the axle, clips on the axle);
the early handbrake (Fig 9.10, Sec 4 and 16: lever and ratchet on the floor, the operating lever under the floor
with the cable's trunnion, brass adjusting nut and spring, the cable from a front abutment back to the
compensating levers on the axle, and rods with clevis pins out to the levers on the backplates).

Supplier data (S): MGOC Spares "MGB rear brakes" (drums 10 x 1.75 in; wheel cylinder 0.800 in bore to 1967;
bleed screw 1/4 UNF; cylinder E-clip; backplate bolts 3/8 UNF x 2 with Philidas nuts; drum nuts 1/2 UNF nyloc;
adjuster nuts 1/4 UNF with spring washers), Moss Motors 180-757 / 180-754 (brake master cylinder 3/4 in bore,
square metal tank to 1967).

Derived (D): every station below unless noted. The backplate is drawn as the usual Lockheed pressing: a flat
centre on the axle flange, a raised annular face the shoes rest on (their webs on six pressed platforms), and a
rim turned back to the drum mouth. Wheel cylinder at the bottom and adjuster at the top (Haynes photo 13.3, Fig
9.9); handbrake lever out through the backplate behind the cylinder, the rods running behind the axle under
the road springs to the compensating levers on P7's pin (`rear_axle_layout.BALANCE_PIVOT`).
"""
from __future__ import annotations

import math

from mgb import car_layout as CL, clutch_layout as K, rear_axle_layout as A

IN = 25.4

# =================================================================================================
# rear drum brake (AF, left-hand wheel, |y| outward)
# =================================================================================================
BP_FACE_Y = A.BACKPLATE_FACE_Y                      # 562: backplate's inboard face on the case flange
BP_T = 2.4
# inboard surface of the pressing, (r, y), centre outward
BP_PROFILE = [(30.0, BP_FACE_Y), (80.0, BP_FACE_Y), (91.0, 581.0), (111.0, 581.0), (116.0, 563.0), (122.5, 563.0),
              (124.0, 564.5)]
PLATEAU_Y = 581.0 + BP_T                            # outboard face of the raised annulus (shoe side)
PLATFORM_H = 1.6                                    # pressed shoe platforms on it
PLATFORM_ANGLES = [40.0, 90.0, 140.0]               # front shoe; the rear shoe's are mirrored (from up toward front)
DRUM_ID = 10.0 * IN                                 # H p146
DRUM_R = DRUM_ID / 2
DRUM_MOUTH_Y = 567.0
DRUM_PLATE_Y = (A.DRUM_FACE_Y, A.DRUM_FACE_Y + 6.0)  # drum's plate on the hub extension flange, 615-621
DRUM_OUT_R = 134.0
LINING_W = 1.75 * IN                                # S: MGOC 10 x 1.75 in
LINING_T = 4.8
LINING_Y = (DRUM_PLATE_Y[0] - 2.5 - LINING_W, DRUM_PLATE_Y[0] - 2.5)
LINING_R = (DRUM_R - 0.3 - LINING_T, DRUM_R - 0.3)  # 0.3 mm running clearance
TABLE_T = 2.5
TABLE_R = (LINING_R[0] - TABLE_T, LINING_R[0])
WEB_T = 4.5
WEB_Y = (PLATEAU_Y + PLATFORM_H, PLATEAU_Y + PLATFORM_H + WEB_T)
WEB_MID_Y = sum(WEB_Y) / 2
WEB_IN_R = 92.0                                     # inner edge of the web at mid-shoe
SHOE_TIPS = (16.0, 164.0)                           # web tips, angles from up toward the front (front shoe)
LINING_ARC = (24.0, 156.0)

# wheel cylinder at the bottom, axis fore and aft
WC_Z = -100.0
WC_AXIS_Y = 594.0
WC_BORE = 0.800 * IN                                # S: MGOC GWC1103
WC_BODY_R = 13.5
WC_HALF_L = 30.0
WC_NECK = (22.0, 14.0)                              # neck through the backplate (x, z)
WC_NECK_END_Y = 552.0
WC_CLIP_Y = 581.0 - 1.6                             # E-clip on the neck behind the raised face
WC_INLET_Z = WC_Z                             # inlet on the neck's end face, pointing inboard
WC_BLEED_Y = 558.0                                  # bleed screw on top of the neck, behind the backplate
PISTON_L = 14.0

# handbrake lever (inside the drum beside the cylinder, out through the backplate behind it)
HB_LEVER_PIVOT = (-24.0, WC_Z)                      # (x, z) pin in the cylinder's rear lug, axis along z
HB_LEVER_Y = 603.0
HB_LEVER_PATH = [(-12.0, HB_LEVER_Y), (-24.0, HB_LEVER_Y), (-36.0, HB_LEVER_Y), (-50.0, 586.0), (-50.0, 545.0)]  # (x, y)
HB_LEVER_END = (-50.0, 549.0, WC_Z)                 # clevis hole, pin along z (x, |y|, z)
HB_SLOT = (-50.0, WC_Z)                             # slot in the backplate (x, z)

# adjuster at the top
ADJ_Z = 101.0
ADJ_BODY = (36.0, 20.0, 15.0)                       # length along x, height along z, depth outboard from the plateau
ADJ_STUD_X = 13.0
ADJ_WEDGE_HEAD_Y = (560.0, 572.0)                   # square head behind the backplate

STEADY_R = 104.0                                    # steady pins at the middle of each shoe
SPRING_TOP = (40.0, 79.0)                           # (x, z) web holes for the adjuster end pull-off spring
SPRING_BOT = (40.0, -79.0)                          # cylinder end
SPRING_Y = WEB_Y[1] + 3.0

# =================================================================================================
# master cylinder, pedal and pedal box (car frame, RHD: brake outboard of the clutch)
# =================================================================================================
# The pedal box (D: Haynes photo 1.1 and Fig 9.16 item 11; Sec 17 para 1, Sec 19 paras 6-7) is a pressed steel
# box on the engine side of the bulkhead: a rear section the pedals hang in (open underneath, the common pivot
# bolt through its side walls), an internal mounting wall the two master cylinders bolt to (clutch_layout
# PEDAL_BOX_FACE_X), and a front section round the cylinders with a floor, closed by the protecting cover on four
# screws. The box is bolted to the bulkhead through a flange round its rear edge (six bolts).
MC_Y, MC_Z = K.MC_Y - 75.0, K.MC_Z                 # brake master cylinder axis (75 mm outboard of the clutch's)
PAD_Y = -418.0                                      # brake pad (clutch_layout PAD_Y: Oliver's kf151, kf152)
PEDAL_PIVOT = (K.PEDAL_PIVOT[0], MC_Y, K.PEDAL_PIVOT[2])
PEDAL_CLEVIS = (K.PEDAL_CLEVIS[0], MC_Y, K.PEDAL_CLEVIS[2])
PEDAL_PAD = (K.PEDAL_PAD[0], PAD_Y, K.PEDAL_PAD[2])
BOX_REAR_X = CL.BULKHEAD_X                          # rear flange on the bulkhead's engine-side face
BOX_WALL_X = K.PEDAL_BOX_FACE_X                     # mounting wall: its front face carries the cylinder flanges
BOX_FRONT_X = K.PEDAL_BOX_FACE_X + 172.0            # front wall, clear of the clutch cylinder's banjo bolt
BOX_Y = (MC_Y - 38.0, K.MC_Y + 31.0)                # outer faces of the side walls (-370, -226; the outer one 4 mm in
                                                    # from P8's margin, clear of the valance's control box)
BOX_Z = (-114.0 + K.PEDAL_BOX_RAISE, 16.0 + K.PEDAL_BOX_RAISE)   # underside of the floor (front section), top rim
BOX_T = 1.6
BOX_FRONT_T = 2.0                                   # mounting wall (clutch_hydraulics BOX_WALL)
BOX_FLANGE = 18.0                                   # rear flange and top rim widths
COVER_TOP_Z = 58.0 + K.PEDAL_BOX_RAISE                                  # top of the protecting cover, over the brake cylinder's cap
PIVOT_BOLT_Y = (BOX_Y[1], BOX_Y[0])                 # head on the inboard wall (Sec 24 para 3: head against the clutch pedal end)
SPRING_ANCHOR_X = K.PEDAL_PIVOT[0] - 26.0           # pull-off spring anchor tabs just ahead of the rear flange (as parts/clutch/pedal.py)
PEDAL_T = 8.0                                       # pedal plate thickness (as the clutch pedal)
# QA fix round 1, steering, had the brake arm joggle outboard round the column; with the box moved out (cockpit) the
# arm's line in the box (ARM_Y) is the cylinder's, 21 mm clear of the column's outer tube, and the arm steps outboard to
# the pad below the column as the clutch arm does (D: Haynes Fig 9.16 item 1, the RHD pedals are cranked pressings).
ARM_Y = MC_Y

# =================================================================================================
# handbrake (car frame, D): lever on the right of the tunnel between the seats, cable back to the axle
# =================================================================================================
# Fig 9.10 (early layout): the lever pivots at its rear end on a spigot through the tunnel's right wall, the grip
# forward, so pulling it up swings the operating lever's lower end (inside the tunnel, under the floor line)
# forward; the cable's inner passes through the trunnion there with the brass adjusting nut on its front side
# (Sec 4 para 2), the cable spring behind it, and the outer runs from the front abutment A back to the axle.
HB_PIVOT = (CL.bx(-1420.0), -129.0, -300.0)                # lever pivot (handle mid-plane), axis along y
TUNNEL_SIDE_Y = -122.0                              # tunnel's right wall, cabin face (P11): the spigot passes through it
HB_PLATE_T = 2.5                                    # ratchet plate on the tunnel wall
OP_LEVER_Y = -106.0                                 # operating lever inside the tunnel (mid-plane)
OP_LEVER_LEN = 92.0                                 # pivot to the trunnion, straight down
HB_GRIP = (CL.bx(-1110.0), -129.0, -215.0)                 # front end of the handle, off position
HB_HANDLE_T = 6.0
CABLE_ABUTMENT = (CL.bx(-1490.0), OP_LEVER_Y, HB_PIVOT[2] - OP_LEVER_LEN)   # A: front abutment behind the trunnion (P11 bracket)
CABLE_FLOOR = (-150.0, -405.0)                      # (y, z) cable outer under the floor beside the tunnel
CABLE_CLIP_Y = -330.0                               # clip 29 on top of the right-hand axle tube (AF |y|)

# compensating levers on the axle pin (AF): levers hang from the pin, rods from their tips
COMP_LEVER_X = {"inner": (-110.0, -105.0), "outer": (-121.0, -116.0)}   # lever 14 (to the left rod), 15 (to the right rod)
COMP_DROP = 50.0                                    # pin to the rod pins
COMP_SPLAY = 16.0                                   # rod pins either side of the pin
CABLE_X = -113.0                                    # cable centre line between the levers
CABLE_Z = A.BALANCE_PIVOT[1] - 25.0


def comp_tip(which):
    """(x, y, z) in AF of a compensating lever's rod pin."""
    y0, z0 = A.BALANCE_PIVOT
    x = sum(COMP_LEVER_X[which]) / 2
    return (x, y0 + (COMP_SPLAY if which == "inner" else -COMP_SPLAY), z0 - COMP_DROP)


def car_af(p):
    return A.car(p)


# =================================================================================================
# brake pipe routes (car frame, D). P11: clips on these runs, grommets where they pass panels.
# =================================================================================================
# Fig 9.1: the master cylinder feeds a four-way connection carrying the hydraulic stop lamp switch; pipes from it to
# the two front hoses and one to the rear hose, which feeds the three-way connection on the axle. Positions derived:
# the four-way on the bulkhead below the pedal box between the pedals' bulkhead crossing and the clutch hose; the
# front pipes up the bulkhead face over the bellhousing and along the chassis legs; the rear pipe down the toe board
# and back under the floor beside the tunnel, rising over the axle to the rear hose bracket on the body.
FOUR_WAY = (CL.BULKHEAD_X + 4.0, -262.0, -215.0)    # bulkhead face point under the connection's bolt (bolt along x)
FOUR_WAY_SPACER = 10.0                               # Fig 9.1 item 6 between the bulkhead and the block
FOUR_WAY_BLOCK = (26.0, 44.0, 26.0)                  # x, y, z
HEAT_CROSS_Z = -66.0                                 # front pipes cross the bulkhead above the bellhousing (r 163)
CHASSIS_LEG_Y = 300.0                                # front pipes forward along the chassis legs
LEG_PIPE_Z = -215.0
FLOOR_PIPE = (-270.0, -394.0)                        # (y, z) rear pipe under the floor beside the tunnel
REAR_HOSE_BRACKET = car_af((150.0, A.PIPE_BRACKET[1], 200.0))   # on the body ahead of and above the union (P11): the hose
                                                     # hangs from it and curves back to the union, slack for axle travel
UNION_Y = A.PIPE_BRACKET[1]
AXLE_PIPE_R = 45.0                                   # axle pipes along the rear-upper side of the tubes (P9: U-bolts outside)
AXLE_PIPE_ANGLE = -45.0                              # from up toward the front: -45 = up and to the rear
UNION_BODY = (-16.0, 4.0, 52.0, 72.0)                # AF x0, x1, z0, z1 of the three-way connection's body on P7's tab
UNION_PORT_X = -6.0                                  # its ports' x (hose on top, pipes either side)
UNION_EAR_X = A.PIPE_BRACKET[0]                      # mounting ear's bolt over the tab's tapped hole
