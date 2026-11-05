"""Body datums set by the electrical phase (P10) for the body phase (P11), car frame
(mgb.car_layout: X forward, Y to the car's left, Z up, origin on the engine centreline at the
head joint face). P11 builds the wings, valances, bulkhead, scuttle, facia, tonneau floor and
rear panel round these points so the lamps, wipers, instruments and battery carriers fit.

Published (S):
- Overall length, width and height, wheelbase, tracks: mgb.car_layout.
- Wing chrome strip to front hub centre 14.25 in, 1963 roadster (mgexp.com "MGB ride height
  survey", article/height.html); used as the side reference line.
- Twin 6 V batteries in boxes under the tonneau floor behind the seats, reached through a
  cover panel (MGOC Spares, MGB batteries and cables page; Haynes Ch 10 Sec 2 para 1 and photo
  2.1: "lift the rear carpet, release the quick release screws in the access panel"); Moss
  Motors lists the 6 V battery box 456-271, two per car, 1962-74.
- Headlamp light units are 7 in (Lucas F700 class; Haynes Fig 10.8 items 2, 4, 5).

Derived (D), each by the method in its comment. None of these positions is published; the
side views of the MGB roadster and the photographs in Haynes Ch 10 (35.1, 36.1, 37.1) and
Ch 12 set the proportions. P11 should check them against the car.
"""
from __future__ import annotations

import math

from mgb import car_layout as CL

IN = 25.4
LENGTH, WIDTH, FRONT_X, REAR_X = CL.LENGTH, CL.WIDTH, CL.FRONT_X, CL.REAR_X
GROUND_Z, WHEEL_Z = CL.GROUND_Z, CL.WHEEL_Z
HALF_W = WIDTH / 2


def above_ground(h):
    return GROUND_Z + h


# ---- side reference (S) ------------------------------------------------------------------------
SIDE_STRIP_Z = above_ground(690.0)                    # wing chrome strip height (D: profile photo 29 and Oliver's photo
                                                       # 09; the mgexp survey's 14.25 in above the hub would be 663)

# ---- front lamps (D) -------------------------------------------------------------------------------
# Headlamps in the wing nacelles (P11b moved these from P10's first estimates to Oliver's car): rim face 186 mm
# behind the overriders' front (profile photo 29 scaled on the wheelbase: the rim's front at X 641-645, just above the front
# tyre's leading edge), centres 585 mm either side (Oliver's photos 15 and 27 scaled on the 198 mm rim), centre 632
# mm above the road (photos 09, 15, 29: the rim's top just under the wing crown, 731 high). P10 had the rim 95 mm behind the bumper, |y| 561, 690 high.
HEADLAMP_RIM_X = FRONT_X - 186.0
HEADLAMP_Y = 585.0
HEADLAMP_Z = above_ground(632.0)
HEADLAMP_BOWL_DEPTH = 118.0                            # the nacelle must take the bowl behind the rim
# Side and flasher lamps (Oliver's photos 10, 15, 20): rectangular units with chrome surrounds below each headlamp,
# just above the bumper beside the grille surround; centres |y| 569, 461 mm above the road, the face on the wing front
# (P10 had a lozenge lamp at FRONT_X - 70, 545 high).
SIDELAMP_X = FRONT_X - 136.0
SIDELAMP_Y = 569.0
SIDELAMP_Z = above_ground(461.0)                       # Oliver's photos 15, 20 (QA): 28 mm above the bumper blade
# Horns: two on the front cross panel behind the grille, either side of the radiator (D).
HORN_POS = [(600.0, s * 300.0, -205.0) for s in (1, -1)]   # (x, y, z) of the horn bracket bolt on the panel face
HORN_PANEL_X = 590.0                                   # rear face of the panel the brackets bolt to

# ---- engine bay: inner wing valances and bulkhead (D) ---------------------------------------------
INNER_WING_Y = 430.0                                   # |y| of the engine-bay face of each inner wing valance
INNER_WING_X = (CL.BULKHEAD_X, 330.0)
BULKHEAD_X = CL.BULKHEAD_X                             # engine side face (car_layout)
# items on the right-hand valance (Lucas RB340 and the 4FJ fuse block beside it: MGOC Spares)
CONTROL_BOX = (-175.0, -INNER_WING_Y, 40.0)            # (x, y, z) of the base's centre on the valance face
FUSE_BOX = (-300.0, -INNER_WING_Y, 40.0)
SOLENOID = (-60.0, -INNER_WING_Y, -70.0)               # starter solenoid, ahead of and below the control box
FLASHER = (-365.0, -INNER_WING_Y, 10.0)
OD_RELAY = (-240.0, INNER_WING_Y, 30.0)                # overdrive relay on the left-hand valance
OD_VACUUM_SWITCH = (BULKHEAD_X, 300.0, 60.0)           # on the left of the bulkhead (MGOC: P5b note)
HARNESS_GROMMET = (BULKHEAD_X, -330.0, 120.0)          # main harness through the bulkhead, right side, high
CABLE_GROMMET = (BULKHEAD_X - 40.0, -355.0, -330.0)    # battery cable up through the toe board beside the footwell

# ---- scuttle, windscreen and facia (D) ---------------------------------------------------------------
# Scuttle top at the windscreen base 915 mm above the road; facia rear face 375 mm behind the
# bulkhead, ahead of the gear lever knob (gearbox_layout.KNOB x -889); driver on the right.
WINDSCREEN_BASE_X = -700.0
WINDSCREEN_BASE_Z = above_ground(915.0)
SCUTTLE_TILT_DEG = 14.0                                # scuttle top falls toward the front at this angle
FACIA_X = -775.0                                       # rear (cockpit) face of the facia panel
FACIA_T = 1.2
DRIVER_Y = -350.0                                      # steering column / driver centre line (RHD)
IP_Z = above_ground(830.0)                             # centre height of the large instruments
# (name, y, z) on the facia rear face, as on Oliver's car (photos 01, 04, 17, 22; P11b moved them from P10's
# Fig 10.9 layout): the speedometer on the left and the tachometer on the right in the binnacle over the column,
# the fuel gauge further right, the dual oil/water gauge on the centre panel right of the plaque.
INSTRUMENTS = {
    "speedometer": (DRIVER_Y + 112.0, IP_Z),
    "tachometer": (DRIVER_Y - 78.0, IP_Z),
    "fuel-gauge": (DRIVER_Y - 196.0, IP_Z - 14.0),
    "dual-gauge": (DRIVER_Y + 266.0, IP_Z - 10.0),
}
# Warning lamps (P10b): on the early cars they are inside the instruments (Haynes Fig 10.26, printed
# p190: the ignition warning lamp 44 in the tachometer 95, the main beam warning lamp 10 in the
# speedometer 45, and a green arrow (27) for each side, left in the tachometer, right in the
# speedometer). (name, instrument, y, z) of each lens on its dial, lit from a bulb holder in the case.
WARNING_LAMPS = {
    "ignition": ("tachometer", INSTRUMENTS["tachometer"][0], IP_Z - 22.0),
    "main-beam": ("speedometer", INSTRUMENTS["speedometer"][0], IP_Z - 22.0),
    "indicator-left": ("tachometer", INSTRUMENTS["tachometer"][0] + 20.0, IP_Z - 12.0),
    "indicator-right": ("speedometer", INSTRUMENTS["speedometer"][0] - 20.0, IP_Z - 12.0),
}
# centre switch panel (Fig 10.9 items 1, 4, 5, 6/7, 8, 13; early cars), as on Oliver's car (photos 16, 22): three
# toggles in a row under the plaque and the ignition (P11b moved them); the choke knob beside them (fuel.choke).
SWITCHES = {
    "lighting": (120.0, IP_Z - 50.0),
    "wiper": (88.0, IP_Z - 50.0),
    "heater": (56.0, IP_Z - 50.0),
    "ignition": (8.0, IP_Z - 50.0),
    "panel-lamp": (DRIVER_Y + 17.0, IP_Z + 8.0),          # pull knob in the binnacle between the speedometer and the
                                                         # tachometer (photo 22); the knob right of the ignition is the
                                                         # choke (its "C", photo 16: mgb.throttle_layout CHOKE_KNOB)
    "map-lamp": (-84.0, IP_Z + 36.0),                    # small knob above the dual gauge
    "overdrive": (DRIVER_Y - 262.0, IP_Z - 10.0),        # toggle outboard of the fuel gauge
}
# centre panel fittings (Oliver's photos 16, 22): the plaque above the switches, the two heater knobs left of it
PLAQUE_Y, PLAQUE_Z = 62.0, IP_Z + 22.0
HEATER_KNOB_Y, HEATER_KNOB_Z = 196.0, (IP_Z + 26.0, IP_Z - 44.0)
# Wipers: two wheelboxes under the scuttle, spindles through it just ahead of the screen base,
# axis square to the scuttle top; the DR3A motor under the passenger (left) side of the facia
# (Haynes Ch 10 Sec 54 para 1).
WIPER_SPINDLES = [(WINDSCREEN_BASE_X + 22.0, y, WINDSCREEN_BASE_Z - 4.0) for y in (240.0, -240.0)]   # left, right
WIPER_AXIS = (math.sin(math.radians(SCUTTLE_TILT_DEG)), 0.0, math.cos(math.radians(SCUTTLE_TILT_DEG)))
WIPER_MOTOR = (-560.0, 470.0, 150.0)                   # motor bracket bolts to the scuttle side, left
WIPER_PARK_SIDE = -1                                   # arms park toward the right (-y), along the screen base

# ---- wiring harness fittings (P10b, D) ------------------------------------------------------------------
# Headlamp dip switch (Fig 10.26 item 7): on the toe board, mgb.wiring_layout DIP_SWITCH (from mgb.underbody_layout).
# Direction indicator switch (item 26): on P9's steering column, mgb.wiring_layout COLUMN_SWITCH.
# Instrument voltage stabiliser (item 64) on the facia rear face beside the fuel gauge.
STABILISER = (FACIA_X + FACIA_T, -118.0, IP_Z - 100.0)    # below the fuel gauge and switches, clear of their cases
# Heater blower motor lead (items 32/33): the heater (P11) sits on the engine side of the bulkhead; the
# harness ends at its snap connector there.
HEATER_CONNECTOR = (BULKHEAD_X + 30.0, -40.0, 190.0)
# Map lamp (items 101/102, early cars): on the facia top rail, centre (P11 trim); its lead ends at a snap
# connector behind the facia.
MAP_LAMP_CONNECTOR = (FACIA_X + 60.0, 30.0, IP_Z + 70.0)
# Earth points: a self-tapping screw into the body with the eyelets under its head; (point on the panel
# face, outward normal of the face).
EARTH_POINTS = {
    "headlamp-right": ((560.0, -INNER_WING_Y - 30.0, 95.0), (0.0, 1.0, 0.0)),
    "headlamp-left": ((560.0, INNER_WING_Y + 30.0, 95.0), (0.0, -1.0, 0.0)),
    "relay": ((-195.0, INNER_WING_Y, 0.0), (0.0, -1.0, 0.0)),
    "facia": ((FACIA_X + FACIA_T, -225.0, IP_Z - 95.0), (1.0, 0.0, 0.0)),
    "scuttle": ((-640.0, INNER_WING_Y + 10.0, 120.0), (0.0, -1.0, 0.0)),
    "boot": ((-2470.0, -HALF_W + 190.0, -150.0), (0.0, 1.0, 0.0)),
}

# ---- rear lamps (D) ------------------------------------------------------------------------------------
# On the rear wing ends' raked plinths (profile photo 29: the plinth raked about 31 deg from vertical, its top corner
# X -2774 h 803 and foot X -2930 h 570; Oliver's photos 18, 24: centres |y| 645). P11b moved the lamp back onto the
# plinth and tilted it (P10 had it upright at REAR_X + 75, 640 high).
REAR_LAMP_X = REAR_X + 191.0                           # lens face centre on the plinth
REAR_LAMP_Y = HALF_W - 127.0                           # Oliver's photos 14, 18 (QA, scaled on the plate): centre 634 off the centre line
REAR_LAMP_Z = above_ground(695.0)                      # photos 14, 18: 548 to 798 above Oliver's road; his car sits 18-24 mm
# lower at the back than the model (scan: rear rims 20 mm higher in the body), so on the body 22 mm higher (Oliver's scan:
# lamp top 819 against the body, the plinth's top corner 830)
REAR_LAMP_RAKE = 33.0                                  # deg: the lamp's top leans forward with the plinth
OVERRIDER_Y = 333.0                                    # rear overrider centre lines (QA: photos 14, 25 scaled on the plate)
NUMBER_LAMP = (REAR_X + 2.0, OVERRIDER_Y - 26.0, above_ground(452.0))   # lamp base on the overrider's inner face, moved back with the overriders (Oliver's scan)

# ---- battery carriers (D) ------------------------------------------------------------------------------
# Two boxes hang under the tonneau floor behind the seats, either side of the tunnel, ahead
# of the rear axle and inboard of the rear springs (rear_axle_layout SPRING_Y 420).
BATTERY_BOX_X = -1700.0                                # box centre (x)
BATTERY_BOX_Y = 268.0                                  # |y| of each box centre
TONNEAU_FLOOR_Z = -140.0                               # floor (box flange) under side: the boxes' bottoms clear P8's rear brake
                                                       # pipe (z -394) and handbrake cable (z -387) that run under them
BATTERY_BOX_INNER = (186.0, 236.0, 226.0)              # x, y, depth inside the box (takes a Lucas SG9E 6 V)
BATTERY_BOX_FLANGE = 22.0                              # flange round the top, bolted up to the floor
BATTERY_SIDE = -1                                      # Oliver's single 12 V battery: right-hand box (question in PLAN)
