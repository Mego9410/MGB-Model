"""Chassis datums set by the gearbox rear mounting (P5b) for the body/chassis phases (P9, P11).

Car frame as mgb.car_layout: X forward, Y left, Z up, origin on the engine centreline at the head
joint face.

What Haynes fixes: on early cars the gearbox rests on a removable rear crossmember through the
rear mountings; the crossmember bolts to the body and the stay rod is detached from the gearbox
(Ch 1 Sec 6 paras 33-35, photo 6.33); the crossmember assembly with an engine (gearbox) mounting
each side, the mounting's plain washer, spring washer and nut under the crossmember, and the two
screws and spring washers holding each mounting to the gearbox (Fig 1.29 items 17-19, 33-38,
printed p52); mounting to gearbox case 15 to 20 lbf ft (Ch 6 specs, printed p112); the steady rod
bracket on the crossmember lies under the overdrive valves (Ch 6 Sec 14 para 1).

Derived (D): where the crossmember sits. The two mountings bolt to pads low on the sides of the
overdrive main casing (mgb.overdrive_layout MOUNT_*), so the crossmember runs across the car
under them, behind the overdrive's three underside plugs. Its ends bolt up to the floor beside
the transmission tunnel; that floor height (BODY_FACE_Z) is not published and is set 202 mm
above the road (the 4.2 in minimum ground clearance is to the lowest point, the crossmember
centre, here about 190 mm). P9/P11 build the floor, the tunnel, captive nuts and brackets to
these datums, and the gearbox stay rod (Fig 1.29 items 20-32) with them.
"""
from __future__ import annotations

from mgb import car_layout as CL, gearbox_layout as G, overdrive_layout as O

# ---- in the gearbox frame (up, left, e) for building the parts ------------------------------------
MOUNT_E = sum(O.MOUNT_E) / 2                          # crossmember centre station
XM_WIDTH = 44.0                                       # fore-aft width of the top web
XM_T = 3.0                                            # pressing thickness
XM_FLANGE = 22.0                                      # depth of the front and rear flanges
BODY_UP = -128.0                                      # crossmember end top faces on the floor underside
PAD_UP = -109.0                                       # mounting pads (top face) under the mountings
CENTRE_UP = -136.0                                    # dip under the overdrive sump (drain plug clear)
END_LEFT = (200.0, 252.0)                             # end pads, each side
BOLT_LEFT = 228.0                                     # two bolts per end, either side of the centre
BOLT_DE = 10.0
MOUNT_STUD_LEFT = 107.0                               # mounting stud through the pad, each side
# top surface of the crossmember, (|left|, up), from the centre outward
PROFILE = [(0.0, CENTRE_UP), (66.0, CENTRE_UP), (84.0, PAD_UP), (130.0, PAD_UP), (150.0, BODY_UP),
           (END_LEFT[1], BODY_UP)]

# ---- car frame datums for P9/P11 ---------------------------------------------------------------
REAR_XMEMBER_X = O.x_of(MOUNT_E)                      # crossmember centre line (car x)
BODY_FACE_Z = G.AXIS_Z + BODY_UP                       # floor underside the crossmember ends bolt up to
REAR_XMEMBER_BOLTS = [(O.x_of(MOUNT_E + s * BOLT_DE), side * BOLT_LEFT, BODY_FACE_Z)
                      for side in (1, -1) for s in (-1, 1)]       # 3/8 in UNF, screwed up into the body
REAR_XMEMBER_BOLT = "3/8"
REAR_MOUNT_STUDS = [(REAR_XMEMBER_X, side * MOUNT_STUD_LEFT, G.AXIS_Z + PAD_UP) for side in (1, -1)]
LOWEST_Z = G.AXIS_Z + CENTRE_UP - XM_FLANGE            # bottom of the crossmember flanges at the centre
CLEARANCE = LOWEST_Z - CL.GROUND_Z

# ---- gearbox stay (steady) rod, Fig 1.29 items 20-32 (P9) ----------------------------------------------------------
# Derived (D): the rod lies fore and aft on the left of the overdrive sump (its plugs leave no room under it), from
# a pin under the gearbox casing's left-hand side to the bracket (20) screwed to the crossmember dip's two holes
# (P5b), its threaded rear end through the bracket's upright between two rubber buffers (24) with their plates
# (25) on a distance tube (26). The pin (30) hangs from a wedge flange screwed to the casing (the casing has no
# drawn pad there: see PLAN).
STAY_Y = 80.0                                          # rod axis, car y (left of the overdrive sump)
STAY_Z = -372.0                                        # rod axis height
STAY_PIN = (-600.0, STAY_Y, STAY_Z)                    # front eye on the pin (pin vertical)
STAY_PIN_TOP_Z = -339.3                                # casing underside at the pin (sloping side, D)
STAY_BRACKET_SCREWS = [(O.x_of(MOUNT_E + 12.0), s * 16.0, G.AXIS_Z + CENTRE_UP) for s in (1, -1)]   # P5b's holes
STAY_WEB_X = -735.0                                    # bracket upright, ahead of the crossmember (the rod passes along x)
