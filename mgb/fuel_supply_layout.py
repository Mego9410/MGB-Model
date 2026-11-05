"""Fuel supply (P11a): the early strap-mounted tank under the boot floor, the SU type HP electric pump on the
heelboard and the pipe forward to the engine bay feed union (fuel.pipes.feed-union, P3). Car frame
(mgb.car_layout).

What Haynes fixes (Ch 3, printed p66-72): a fuel tank at the rear, an electric pump and the lines to the
carburettors (Sec 1); early models the SU HP pump, minimum delivery 7 Imp gal per hour (specifications p66);
the pump "is positioned under the right side of the car; on the heelboard adjacent to the front of the RH
leaf spring", held with its bracket by two bolts and spring washers, inlet and outlet pipes on nuts or clips,
a vent pipe, the earth and supply wires (Sec 5); the HP body, sandwich plate and coil housing on six screws
with the two cast lugs of the coil housing at the bottom (Sec 7 para 20); the early tourer tank on two straps
whose nuts are at the rear of the tank, the gauge wires on its right side, the drain plug underneath, the fuel
pipe union, the filler neck hose with two clips, the extension (filler tube) and its seal (Sec 12); the early
gauge unit on six screws (Sec 16); the parts (Fig 3.9, printed p71, items 1-12 and 25-33).

Supplier and club data (S): the original tank fitted to early 1965, "a wedge-shaped unit with a flat top and
curved bottom", on two straps with rear hangers and clevis pins (MGOC Spares "MGB fuel tanks, fillers and sender
units": ARH176, straps AHH6253, packing AHH5115, clevis pin CLZ427, bolt 1/4 UNF x 2 1/4, sender BHA4292 with a
six-screw cork gasket, filler hose clips 2 in); the pump on the axle side of the right-hand heelboard, on a
bracket with a rubber block; the underfloor pipe clipped under the right-hand floor with the battery cable and
the rear brake pipe, entering the engine bay "by the heater" (MGOC Spares, "Keeping on top of the MGB fuel
system", parts 2 and 3); direct pipe connections on cars to 1964, braided hoses at the rear (MGOC Spares "MGB
fuel lines - rear & main").

Derived (D): all sizes and stations below. Tank 18 x 22.6 in in plan, deeper at the rear, sized to the 10 Imp
gal of the early cars, between the right-hand road spring and the rear silencer; the pump between the
heelboard and P10's right-hand battery carrier, inboard of the spring's front eye; the tank-to-pump pipe across
the tank's front face, over the axle under the arch and forward between the tunnel and the battery carrier; the
main pipe down the heelboard, forward under the floor beside P8's rear brake pipe, up the toe board, up and
across the bulkhead's engine-side face above the bellhousing and forward along the left of the engine to the
feed union under the carburettors.

Frames: fore-aft numbers are body stations (car_layout.bx), except the last run from the bulkhead to P3's feed union
under the carburettors, which follows the engine (engine frame). If the engine moves back in the body (P12, Oliver's
scan), that run's first two points (behind the head) have to be re-fitted ahead of the moved bulkhead.
"""
from __future__ import annotations

from mgb import car_layout as CL, underbody_layout as U

IN = 25.4
PIPE_OD = 5.0 / 16.0 * IN                      # 5/16 in steel pipe (D: matches the 5/16 in hoses of P3)
PIPE_WALL = 0.7

# ---- tank (Fig 3.9 item 1, earlier type) -----------------------------------------------------------------------
TANK_X = (CL.bx(-2322.0), CL.bx(-2779.2))                   # front and rear faces (18 in)
TANK_Y = (-365.0, 210.0)                       # right-hand and left-hand end faces
TANK_TOP_Z = U.BOOT_FLOOR_Z - 3.0              # held up under the boot floor by the straps
DEPTH_FRONT, DEPTH_REAR = 142.0, 200.0         # the wedge: deeper at the rear (D)
SEAM_W = 9.0                                   # rolled seam flange round each end plate
SENDER = (CL.bx(-2560.0), -262.0)                    # (x, z) of the gauge unit on the right-hand end face
SENDER_PCD, SENDER_BORE = 66.0, 46.0
OUTLET = (CL.bx(-2385.0), -318.0)                    # (x, z) of the outlet stub on the right-hand end face
DRAIN = (CL.bx(-2610.0), -310.0)                     # (x, y) of the drain plug boss under the tank
FILLER = (CL.bx(-2470.0), -205.0)                    # (x, y) of the filler stub on the top
FILLER_OD = 2.0 * IN                           # 2 in hose clips (S: MGOC GHC1622)
FILLER_STUB_H = 34.0                           # up through the boot floor
STRAP_Y = (-232.0, 78.0)                       # the two straps
STRAP_W, STRAP_T = 1.0 * IN, 1.6
PACK_T = 3.0                                   # rubber packing strip under each strap
STRAP_PIN_FRONT = (TANK_X[0] + 14.0, TANK_TOP_Z - 14.0)     # (x, z) front pin through the body tab (P11)
HANGER_PIN = (TANK_X[1] - 26.0, U.BOOT_FLOOR_Z - 12.0)    # (x, z) rear hanger clevis pin through the body tab (P11)
HANGER_FOOT_Z = TANK_TOP_Z - 46.0                         # strap end tab under the hanger's foot
STRAP_BOLT_X = TANK_X[1] - 26.0
FILLER_TUBE_TOP_Z = CL.GROUND_Z + 610.0     # QA: Oliver's photos 14, 18 (26 mm under the plate's top), + 22 on the body (scan)                     # filler tube elbow's horizontal leg
FILLER_CAP_Y = -382.0                          # P11b: the cap is on the rear panel right of the plate (QA: photos 14, 18)
FILLER_CAP_X = U.REAR_PANEL_X - 5.0                 # (Oliver's photos 11, 18, 21: a chrome locking cap), the tube's face there                         # cap end of the filler tube (P11: filler housing in the body)

# ---- pump (SU HP, Fig 3.2) -------------------------------------------------------------------------------------
PUMP_Y0 = -172.0                               # body end face (inboard); the pump axis runs out along -y
PUMP_X = U.HEELBOARD_X - 47.0                  # axis x
PUMP_Z = -335.0                                # axis z
# stations along the axis (s outward from the body end face)
BODY_S = (0.0, 40.0)
SANDWICH_S = (40.5, 48.5)
COIL_S = (49.0, 125.0)
COVER_S = (125.0, 165.0)
PORT_S = 17.0                                  # inlet and outlet ports' station
LUG_S = (62.0, 108.0)                          # the two cast lugs under the coil housing
BRACKET_T = 2.5


def pump_pt(s, dx=0.0, dz=0.0):
    """Car point at station s along the pump axis, offset dx forward and dz up."""
    return (PUMP_X + dx, PUMP_Y0 - s, PUMP_Z + dz)


INLET_TIP = pump_pt(PORT_S, dx=-68.0)          # inlet union's end, facing the rear (toward the tank pipe)
OUTLET_TIP = pump_pt(PORT_S, dz=74.0)          # outlet connection's end, facing up

# ---- pipes ---------------------------------------------------------------------------------------------------
TANK_STUB_END = (CL.bx(-2337.0), TANK_Y[0] - 14.0, OUTLET[1])     # outlet stub, turned forward on the tank
TANK_HOSE = [TANK_STUB_END, (CL.bx(-2316.0), TANK_Y[0] - 14.0, OUTLET[1]), (CL.bx(-2307.0), -330.0, OUTLET[1])]
PIPE_IN_Y = -136.0                              # between the tunnel and the right-hand battery carrier
TP_ROUTE = CL.bxt([(-2307.0, -330.0, OUTLET[1]), (-2307.0, PIPE_IN_Y, OUTLET[1]), (-2307.0, PIPE_IN_Y, U.ARCH_Z - 9.0),
            (-1990.0, PIPE_IN_Y, U.ARCH_Z - 9.0), (-1890.0, PIPE_IN_Y, U.TONNEAU_Z - 12.0),
            (-1592.0, PIPE_IN_Y, U.TONNEAU_Z - 12.0), (-1592.0, INLET_TIP[1], INLET_TIP[2])]) + [
            (INLET_TIP[0] - 2.0, INLET_TIP[1], INLET_TIP[2])]
MAIN_START = (U.HEELBOARD_X - 8.0, -352.0, -262.0)        # union on the heelboard outboard of the pump's end cover
HOSE_Z = OUTLET_TIP[2] + 26.0                    # the pump hose's run over the pump to the heelboard
PUMP_HOSE = [(OUTLET_TIP[0], OUTLET_TIP[1], OUTLET_TIP[2] + 3.5), (OUTLET_TIP[0], OUTLET_TIP[1], HOSE_Z),
             (MAIN_START[0] - 8.0, MAIN_START[1] + 40.0, HOSE_Z), (MAIN_START[0], MAIN_START[1], MAIN_START[2] + 8.0)]
FLOOR_Y = -370.0                                 # under the floor outboard of P10's battery cable (y -300 to -355)
                                                 # and P8's rear brake pipe (y -270)
FLOOR_PIPE_Z = U.FLOOR_Z - 10.0
UP_Y = -385.0                                    # up the bulkhead outboard of the pedal box flange (y -346) and P8's pipes
CROSS_Z = 70.0                                   # across the bulkhead above the pedal box, by the heater (MGOC)
BULK_X = CL.BULKHEAD_X + 9.0
FEED_END_X = -70.0                               # P3's feed union nut on the hose end (parts/fuel/pipes FEED_END)
FEED_Y, FEED_Z = 204.0, -82.0
TOE_UP_X = CL.bx(-425.0)                               # top of the run up the toe board
MAIN_ROUTE = [MAIN_START, (MAIN_START[0], MAIN_START[1], -330.0), (MAIN_START[0], FLOOR_Y, -365.0),
              (MAIN_START[0], FLOOR_Y, FLOOR_PIPE_Z), (CL.bx(-520.0), FLOOR_Y, FLOOR_PIPE_Z),
              (CL.bx(-470.0), FLOOR_Y, U.toe_z(CL.bx(-470.0)) - 10.0), (TOE_UP_X, FLOOR_Y, U.toe_z(TOE_UP_X) - 10.0),
              (BULK_X, UP_Y, U.toe_z(TOE_UP_X) - 4.0), (BULK_X, UP_Y, CROSS_Z), (BULK_X, 150.0, CROSS_Z),
              # engine frame from here: forward from the bulkhead along the left of the engine to the feed union
              (-300.0, 196.0, 30.0), (-245.0, FEED_Y, -60.0), (-200.0, FEED_Y, FEED_Z), (FEED_END_X - 18.0, FEED_Y, FEED_Z)]
# P-clips: (route name, point, unit normal of the body face the clip screws to)
CLIPS = {
    "main": [((CL.bx(-1250.0), FLOOR_Y, FLOOR_PIPE_Z), (0, 0, 1)), ((CL.bx(-950.0), FLOOR_Y, FLOOR_PIPE_Z), (0, 0, 1)),
             ((CL.bx(-650.0), FLOOR_Y, FLOOR_PIPE_Z), (0, 0, 1)), ((BULK_X, UP_Y, -100.0), (-1, 0, 0)),
             ((BULK_X, -60.0, CROSS_Z), (-1, 0, 0))],
    "tank": [((CL.bx(-2150.0), PIPE_IN_Y, U.ARCH_Z - 9.0), (0, 0, 1)), ((CL.bx(-1860.0), PIPE_IN_Y, U.TONNEAU_Z - 12.0), (0, 0, 1))],
}
