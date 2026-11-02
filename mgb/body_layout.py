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
SIDE_STRIP_Z = WHEEL_Z + 14.25 * IN                   # wing chrome strip height (mgexp survey, 1963 roadster)

# ---- front lamps (D) -------------------------------------------------------------------------------
# Headlamps in the wing nacelles: centres 200 mm in from the widest point of the body, the
# rim's front face 95 mm behind the front of the bumper, centre 690 mm above the road (just
# above the chrome strip line, as the side view shows the strip running back from the lower
# half of the nacelle).
HEADLAMP_RIM_X = FRONT_X - 95.0
HEADLAMP_Y = HALF_W - 200.0
HEADLAMP_Z = above_ground(690.0)
HEADLAMP_BOWL_DEPTH = 118.0                            # the nacelle must take the bowl behind the rim
# Side and flasher lamps below the headlamps, on the wing front above the bumper (photo 35.1).
SIDELAMP_X = FRONT_X - 70.0
SIDELAMP_Y = HEADLAMP_Y + 6.0
SIDELAMP_Z = above_ground(545.0)
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
# (name, y, z) on the facia rear face. Speedometer outboard of the tachometer for RHD (mirror of
# the LHD layout); fuel gauge inboard, oil pressure / water temperature gauge outboard (Fig 10.9
# draws two large dials flanked by two small ones over the column cut-out).
INSTRUMENTS = {
    "tachometer": (DRIVER_Y + 64.0, IP_Z),
    "speedometer": (DRIVER_Y - 64.0, IP_Z),
    "fuel-gauge": (DRIVER_Y + 186.0, IP_Z - 22.0),
    "dual-gauge": (DRIVER_Y - 186.0, IP_Z - 22.0),
}
WARNING_LAMPS = {                                      # small lenses between and above the dials
    "ignition": (DRIVER_Y, IP_Z + 34.0),
    "main-beam": (DRIVER_Y - 18.0, IP_Z + 58.0),
    "indicator": (DRIVER_Y + 18.0, IP_Z + 58.0),
}
# centre switch panel (Fig 10.9 items 1, 4, 5, 6/7, 8, 13; early cars)
SWITCHES = {
    "lighting": (-92.0, IP_Z - 10.0),
    "wiper": (-40.0, IP_Z - 10.0),
    "heater": (12.0, IP_Z - 10.0),
    "panel-lamp": (64.0, IP_Z - 10.0),
    "map-lamp": (116.0, IP_Z - 10.0),
    "ignition": (-40.0, IP_Z - 72.0),
    "overdrive": (DRIVER_Y - 250.0, IP_Z - 40.0),        # toggle on the facia to the right of the binnacle (Fig 10.9 item 2)
}
# Wipers: two wheelboxes under the scuttle, spindles through it just ahead of the screen base,
# axis square to the scuttle top; the DR3A motor under the passenger (left) side of the facia
# (Haynes Ch 10 Sec 54 para 1).
WIPER_SPINDLES = [(WINDSCREEN_BASE_X + 22.0, y, WINDSCREEN_BASE_Z - 4.0) for y in (240.0, -240.0)]   # left, right
WIPER_AXIS = (math.sin(math.radians(SCUTTLE_TILT_DEG)), 0.0, math.cos(math.radians(SCUTTLE_TILT_DEG)))
WIPER_MOTOR = (-560.0, 470.0, 150.0)                   # motor bracket bolts to the scuttle side, left
WIPER_PARK_SIDE = -1                                   # arms park toward the right (-y), along the screen base

# ---- rear lamps (D) ------------------------------------------------------------------------------------
REAR_LAMP_X = REAR_X + 75.0                            # lens face, on the rear wing end above the bumper
REAR_LAMP_Y = HALF_W - 115.0
REAR_LAMP_Z = above_ground(640.0)
OVERRIDER_Y = 262.0                                    # rear overrider centre lines (number plate lamps on their inner faces)
NUMBER_LAMP = (REAR_X + 38.0, OVERRIDER_Y - 26.0, above_ground(430.0))   # lamp base on the overrider's inner face

# ---- battery carriers (D) ------------------------------------------------------------------------------
# Two boxes hang under the tonneau floor behind the seats, either side of the tunnel, ahead
# of the rear axle and inboard of the rear springs (rear_axle_layout SPRING_Y 420).
BATTERY_BOX_X = -1700.0                                # box centre (x)
BATTERY_BOX_Y = 268.0                                  # |y| of each box centre
TONNEAU_FLOOR_Z = -228.0                               # floor (box flange) under side
BATTERY_BOX_INNER = (186.0, 236.0, 226.0)              # x, y, depth inside the box (takes a Lucas SG9E 6 V)
BATTERY_BOX_FLANGE = 22.0                              # flange round the top, bolted up to the floor
BATTERY_SIDE = -1                                      # Oliver's single 12 V battery: right-hand box (question in PLAN)
