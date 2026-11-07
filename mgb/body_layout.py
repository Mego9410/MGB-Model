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
BODY_WIDEST_H = 690.0                                  # the body's widest line above the road (the shell's H_M; D: profile
                                                       # photo 29 and Oliver's photo 09), no longer tied to the strip
# Chrome side strip line, (x, height above the road) along the car (QA fix 1, sides-glass 11 / rear 20: Oliver's
# keyframes kf048, kf016, kf015, kf046 on the SfM cameras and his scan; 679 at x 400, 711 at -600, 713-718 on the
# doors, 718-724 on the rear wings). The mgexp survey's 14.25 in above the hub would be 663.
SIDE_STRIP_H = [(560.0, 676.0), (400.0, 679.0), (100.0, 694.0), (-300.0, 705.0), (-600.0, 711.0), (-900.0, 714.0),
                (-1300.0, 716.0), (-1620.0, 717.0), (-2000.0, 719.0), (-2400.0, 721.0), (-2800.0, 723.0)]
SIDE_STRIP_Z = above_ground(716.0)                    # the strip on the doors

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
# QA fix round 1 (front finding 20): Oliver's scan in front elevation puts the lamp at y 490-623, h 436-495 (centre
# |y| 555, h 465), its face turned about 30 deg outboard with the wing corner (keyframes kf210-213). The wing there
# turns only about 19 deg (mgb.body_shell_layout nose_x(555, 465) = 693.7), so the lamp's base stands 14 mm off the skin
# along its axis, its outboard end on the wing and its inboard end on the deep chrome body (kf212 shows it standing
# proud inboard). Before: |y| 569, h 461, facing ahead.
SIDELAMP_X = FRONT_X - 125.0
SIDELAMP_Y = 560.0
SIDELAMP_Z = above_ground(465.0)
SIDELAMP_TURN = 30.0                                   # deg about z, the face turned outboard
# Horns: two on the front cross panel behind the grille, either side of the radiator (D).
HORN_POS = [(CL.bx(600.0), s * 300.0, -205.0) for s in (1, -1)]   # (x, y, z) of the horn bracket bolt on the panel face
HORN_PANEL_X = CL.bx(590.0)                                  # rear face of the panel the brackets bolt to

# ---- engine bay: inner wing valances and bulkhead (D) ---------------------------------------------
INNER_WING_Y = 430.0                                   # |y| of the engine-bay face of each inner wing valance
INNER_WING_X = (CL.BULKHEAD_X, CL.bx(330.0))
BULKHEAD_X = CL.BULKHEAD_X                             # engine side face (car_layout)
# items on the right-hand valance (Lucas RB340 and the 4FJ fuse block beside it: MGOC Spares)
CONTROL_BOX = (CL.bx(-175.0), -INNER_WING_Y, 40.0)            # (x, y, z) of the base's centre on the valance face
FUSE_BOX = (CL.bx(-300.0), -INNER_WING_Y, 40.0)
SOLENOID = (CL.bx(-60.0), -INNER_WING_Y, -70.0)               # starter solenoid, ahead of and below the control box
FLASHER = (CL.bx(-365.0), -INNER_WING_Y, 10.0)
OD_RELAY = (CL.bx(-240.0), INNER_WING_Y, 30.0)                # overdrive relay on the left-hand valance
OD_VACUUM_SWITCH = (BULKHEAD_X, 300.0, 60.0)           # on the left of the bulkhead (MGOC: P5b note)
HARNESS_GROMMET = (BULKHEAD_X, -330.0, 190.0)          # main harness through the bulkhead, right side, high (above P8's
                                                       # pedal box, raised in QA fix round 1, steering)
CABLE_GROMMET = (BULKHEAD_X - 40.0, -355.0, -330.0)    # battery cable up through the toe board beside the footwell

# ---- scuttle, windscreen and facia (D) ---------------------------------------------------------------
# Scuttle top at the windscreen base 915 mm above the road; facia rear face 375 mm behind the
# bulkhead, ahead of the gear lever knob (gearbox_layout.KNOB x -889, 114 mm behind it; 271 mm with the engine moved
# back to Oliver's scan, P12); driver on the right. Fore-aft positions here are body stations (car_layout.bx).
WINDSCREEN_BASE_X = CL.bx(-605.0)                          # QA fix 1: the glass's lower edge at the centre (Oliver's scan
WINDSCREEN_BASE_Z = above_ground(921.0)                     # and keyframes; body_shell_layout.SCREEN_BASE has the whole line)
SCUTTLE_TILT_DEG = 14.0                                # scuttle top falls toward the front at this angle
FACIA_X = CL.bx(-775.0)                                      # rear (cockpit) face of the facia panel
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
# QA fix round 1 (front fittings): the scuttle fittings' plan positions measured on Oliver's car (keyframes kf076,
# kf088, kf092 triangulated, 0-19 mm residuals, agreeing with his registered scan's plan to ~10 mm). They stand on the
# scuttle skin, so their heights come from the outer surface (mgb.body_shell_layout.top_h, resolved lazily below because
# that module imports this one) and they follow it when the scuttle is reshaped; they do not hang off the bonnet's rear
# edge or the screen base. P10 had the spindles 22 mm ahead of the screen base at |y| 240 (138 mm too far back, 50 mm
# too close together); the car's triangulated spindle tops are at h 913, the vent at h 908.
WIPER_SPINDLE_XY = [(CL.bx(-545.0), y) for y in (290.0, -290.0)]   # left, right: spindle centres on the scuttle
WASHER_JET_XY = [(CL.bx(-535.0), y) for y in (355.0, -355.0)]      # chrome jets just outboard of the spindles (one
                                                       # triangulated at y +355; the other mirrored, kf195, kf199, kf202)
# Vent: tips y -191/+192 (383 long), triangulated centre x -470..-480 and about 60 fore-aft from the scan plan; but the
# photos (kf195-199) show it standing clear behind the bonnet's rear edge (x -453 from the same triangulation, the
# corners -433/-474) by about a rim's width or two, so the centre is taken 12 mm further back and the depth 56 (the
# cells about square, kf199): front edge x -464, 11 mm behind the bonnet edge.
SCUTTLE_VENT_X = CL.bx(-492.0)
SCUTTLE_VENT_LEN, SCUTTLE_VENT_DEPTH = 383.0, 56.0
WIPER_MOTOR = (CL.bx(-560.0), 470.0, 150.0)                   # motor bracket bolts to the scuttle side, left
WIPER_PARK_SIDE = -1                                   # arms park toward the right (-y), along the screen base


def skin_point(x, y):
    """(z, unit outward normal) of the outer skin's top at plan point (x, y) (mgb.body_shell_layout)."""
    from mgb import body_shell_layout as S
    h = S.top_h(x, y)
    dhx = (S.top_h(x + 10.0, y) - S.top_h(x - 10.0, y)) / 20.0
    dhy = (S.top_h(x, abs(y) + 10.0) - S.top_h(x, abs(y) - 10.0)) / 20.0 * (1.0 if y >= 0 else -1.0)
    n = (-float(dhx), -float(dhy), 1.0)
    L = math.sqrt(sum(c * c for c in n))
    return float(S.z_of(h)), tuple(c / L for c in n)


_LAZY = {}


def __getattr__(name):
    """WIPER_SPINDLES, WIPER_AXIS and WASHER_JETS: positions on the skin, worked out on first use."""
    if name not in ("WIPER_SPINDLES", "WIPER_AXIS", "WASHER_JETS"):
        raise AttributeError(name)
    if not _LAZY:
        sp = [(x, y, skin_point(x, y)[0]) for x, y in WIPER_SPINDLE_XY]
        nx, _, nz = skin_point(*WIPER_SPINDLE_XY[0])[1]
        L = math.hypot(nx, nz)
        _LAZY["WIPER_SPINDLES"] = sp                   # left, right: (x, y, z of the spindle's seat on the skin)
        _LAZY["WIPER_AXIS"] = (nx / L, 0.0, nz / L)    # square to the scuttle in side view (both sides alike)
        _LAZY["WASHER_JETS"] = [(x, y, skin_point(x, y)[0]) for x, y in WASHER_JET_XY]
    return _LAZY[name]

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
    "headlamp-right": ((CL.bx(560.0), -INNER_WING_Y - 30.0, 95.0), (0.0, 1.0, 0.0)),
    "headlamp-left": ((CL.bx(560.0), INNER_WING_Y + 30.0, 95.0), (0.0, -1.0, 0.0)),
    "relay": ((CL.bx(-195.0), INNER_WING_Y, 0.0), (0.0, -1.0, 0.0)),
    "facia": ((FACIA_X + FACIA_T, -225.0, IP_Z - 95.0), (1.0, 0.0, 0.0)),
    "scuttle": ((CL.bx(-640.0), INNER_WING_Y + 10.0, 120.0), (0.0, -1.0, 0.0)),
    "boot": ((CL.bx(-2470.0), -HALF_W + 190.0, -150.0), (0.0, 1.0, 0.0)),
}

# ---- rear lamps (D) ------------------------------------------------------------------------------------
# On the rear wing ends' raked plinths (profile photo 29: the plinth raked about 31 deg from vertical, its top corner
# X -2774 h 803 and foot X -2930 h 570; Oliver's photos 18, 24: centres |y| 645). P11b moved the lamp back onto the
# plinth and tilted it (P10 had it upright at REAR_X + 75, 640 high).
REAR_LAMP_X = REAR_X + 203.5                           # lens face centre on the plinth (moved 12.7 forward up the 33 deg plinth
                                                       # with the 18 mm rise below: QA fix round 1)
REAR_LAMP_Y = 620.0                                    # QA fix round 1 (rear 19): Oliver's photo 25 scaled on the plate, 617-624 off the centre line (was 634)
REAR_LAMP_Z = above_ground(713.0)                      # QA fix round 1: the chrome runs 595 to 836 on the car (Oliver's photo 25 scaled on
# the plate, his scan), 18 mm higher than the 695 first set from photos 14, 18 (548 to 798 above Oliver's road; his car sits 18-24 mm
# lower at the back than the model (scan: rear rims 20 mm higher in the body), so on the body 22 mm higher (Oliver's scan:
# lamp top 819 against the body, the plinth's top corner 830)
REAR_LAMP_RAKE = 33.0                                  # deg: the lamp's top leans forward with the plinth
OVERRIDER_Y = 333.0                                    # rear overrider centre lines (QA: photos 14, 25 scaled on the plate)
# Number plate lamps (QA fix round 1): the chrome "ear" on the inboard face of each rear overrider near its top, centred
# 551 above the road (Oliver's photo 25 scaled on the plate; keyframes kf165, kf168, kf171, kf173), not at the overrider's
# foot. (x, |y|, z) of the lamp base on the overrider's inner face (parts.body.brightwork rear overrider).
NUMBER_LAMP = (REAR_X + 62.0, OVERRIDER_Y - 24.0, above_ground(551.0))

# ---- battery carriers (D) ------------------------------------------------------------------------------
# Two boxes hang under the tonneau floor behind the seats, either side of the tunnel, ahead
# of the rear axle and inboard of the rear springs (rear_axle_layout SPRING_Y 420).
BATTERY_BOX_X = CL.bx(-1800.0)                               # box centre (x): behind the shelf's front riser (underbody_layout
                                                       # SHELF_FRONT_X, QA fix round 1, cockpit)
BATTERY_BOX_Y = 268.0                                  # |y| of each box centre
TONNEAU_FLOOR_Z = -28.0                                # floor (box flange) under side: the shelf behind the seats, its carpet
                                                       # about 568 above the road (Oliver's body scan, sections y -300 to 300:
                                                       # 560-580; QA fix round 1, cockpit; was -140)
BATTERY_BOX_INNER = (186.0, 236.0, 226.0)              # x, y, depth inside the box (takes a Lucas SG9E 6 V)
BATTERY_BOX_FLANGE = 22.0                              # flange round the top, bolted up to the floor
BATTERY_SIDE = -1                                      # Oliver's single 12 V battery: right-hand box (question in PLAN)
