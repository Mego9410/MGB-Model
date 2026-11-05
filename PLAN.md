# Build plan and status

Phases follow the Haynes chapter order. After each phase: build, render and compare,
`pytest`, commit with attribution, push, republish the MGB Workshop artifact with every
model JSON, then run the smoke test.

Car-level placement: `mgb/car_layout.py` (engine frame = car frame; wheel centres,
ground, overhangs). Every assembly outside the engine is placed from it.

| Phase | Haynes | Status |
| --- | --- | --- |
| P1 Cylinder head | Ch 1 | done |
| P2 Block, crank, timing, lube, flywheel, manifolds, cooling | Ch 1-2 | done |
| P3 Carburettors, fuel hoses, breather, ignition | Ch 3-4 | done |
| P3b Accelerator pedal and cable, throttle interconnection, choke control and jet linkage | Ch 3 | done |
| P4 Clutch | Ch 5 | done |
| P5a Gearbox (three-synchro, overdrive type), remote control | Ch 6 | done |
| P5b Overdrive (Laycock type D), speedometer drive, rear mounting | Ch 6, Ch 1 | done |
| P6 Propeller shaft | Ch 7 | done |
| P7 Rear axle | Ch 8 | done |
| P8 Brakes | Ch 9 | done |
| P9 Suspension, steering, wheels and tyres; engine mountings | Ch 11 | done |
| P10 Electrical: battery, 18ACR alternator, starter, coil, lamps, wipers, instruments, loom | Ch 10 | done |
| P10b Wiring harness, wire by wire (every cable, its colour, terminals and route) | Ch 10, Ch 6 | done |
| P11a Exhaust system; fuel tank, pump and pipes | Ch 3 | done |
| P11b Body shell, panels, trim, fittings | Ch 12 | done |

## Carried over

- Front brake hose (P8/P9): P9 built the hub, swivel axle and its caliper flange and dust cover pads to P8's datums;
  the front hose bracket on the wing valance (`front_suspension_layout.HOSE_BRACKET`) is P11's, and the hose's run at
  full lock and bump is still to be checked once the valance exists.
- Rear axle fittings (P8) for P9: the axle pipes run along the rear-upper side of each tube (`brake_layout.AXLE_PIPE_R`
  45 mm, 45 deg up and to the rear) from |y| 230 to 470 and down the front of the tube to the wheel cylinder; the
  U-bolts must pass outside them. The handbrake rods run from the compensator behind the bowl (`brake_layout.comp_tip`)
  to the backplate levers (AF x -50, |y| 549, z -100), passing under the road springs about 106 mm below the axle
  centre at |y| 420: P9's spring, U-bolt plate and damper link must clear them. The cable goes over the right-hand
  tube at |y| 330 (clip, `CABLE_CLIP_Y`).
- Body (P11) attachments left by P8: the pedal box's rear flange on the bulkhead's engine-side face (six bolts,
  `parts/brakes/master.py box_bolts`, nuts behind a 1 mm panel), the toe board slots the two pedals pass through
  (the arms cross the bulkhead plane at about z -140, y -215 and -290), the four-way connection's bolt
  through the bulkhead (`brake_layout.FOUR_WAY`); clips along the brake pipe runs (`parts/brakes/lines.py`
  `front_pipe_points`, `rear_pipe_points`: bulkhead face, chassis legs, under the floor at y -270, z -394, up the
  heel board); the rear hose bracket on the body (`brake_layout.REAR_HOSE_BRACKET`); the handbrake: tunnel right wall
  at y -122 with the ratchet plate's three bolts and the spigot hole (`HB_PIVOT`), the cable's front abutment
  bracket A (`CABLE_ABUTMENT`) and the floor clip; seats and tunnel must clear the lever and its 4-5 notch travel.
- Known P8 approximations: no outside photographs of the parts could be opened from the build machine, so forms are
  from the Haynes figures and photos (1.1, 13.3, 13.4) with sizes derived; the brake pedal is the clutch pedal's
  form moved to the brake line; the brake cylinder's internals are the clutch cylinder's (same 3/4 in bore); the
  front pad pins sit just over the clip (front.py `PIN_U`, not the layout's `PIN_U`); the stop lamp switch is drawn
  as a generic Lucas hydraulic switch; every pipe, hose and cable route is derived; the compensator is a scissor pair
  on P7's pin with the cable across their tabs, its proportions derived from Fig 9.10.
  Interference check (brakes against each other, the axle and the clutch hydraulics and pedal): what remains is
  thread engagement (bolts in tapped holes, nuts on studs and bolts, tube nuts in ports, about 50-700 mm3 each),
  rubber against metal where boots and seals grip (under 150 mm3), the springs' hooks in their holes, and the
  handbrake cable's ferrule on the compensator tab (48 mm3). The wheel cylinder boot is trimmed flat on the
  backplate side because the cylinder axis sits only 10.6 mm off the raised face.
- Body mountings for the suspension and steering (P11), all car frame, per side (P9 datums):
  - Front crossmember: two support bolts each side up through the front chassis legs
    (`front_suspension_layout.BODY_BOLTS`, |y| 432, x FX-80 and FX+88, leg underside `BODY_FACE_Z` z -226 on the upper
    rubber pads, leg top `BODY_LEG_TOP_Z` -176 where the nuts and washers sit). The damper arms sweep over the legs
    between |y| 305 and 499 at z -113 to -175 (more on rebound): the inner wing valances need openings there. The
    column runs through a tube in the RHD crossmember's right tower (`steering_layout.CROSSMEMBER_TUBE_R`).
  - Steering column top: the clamp (Fig 11.6 item 59) on a body bracket under the facia at
    `steering_layout.COLUMN_TOP_CLAMP` (x -780, y -338, z -42), just ahead of P10's facia (`body_layout.FACIA_X`; the
    wheel is on `DRIVER_Y`), with packing washers; the bottom bracket, blanking plate
    and draught excluder on the toe board at `COLUMN_TOE_PLATE` (x -440, y -319, z -127): the toe board needs a hole for
    the 1 1/2 in tube there. The column passes under P8's pedal box and master cylinder pipe and outboard
    of the brake pedal (the wheel centre about 590 mm above the road, on P10's `DRIVER_Y`); P4's clutch pipe and hose
    bracket (`clutch_layout.HOSE_BRACKET`, set on a chassis leg at |y| 268) lie inboard of it, whereas the front
    chassis legs are at |y| 432 (P9's crossmember mountings): P11 should move that bracket onto the leg.
  - Rear springs: front hanger plates either side of the eye on the eyebolt axis `rear_suspension_layout.FRONT_HANGER`
    (|y| 420, x -1589.9, z -299.3, bolt along y); the rear shackle's upper pin through a body bracket at
    `SHACKLE_BRACKET` (x -2785, z -208); dampers bolted by two bolts along y to the side member's inner face at
    `DAMPER_MOUNT` (|y| 436, x -2056 and -1902, z -210); rebound strap bolts at `REBOUND_BOLT` (x -2246.4, |y| 500, z -132.8); bump rubber strike
    faces at `BUMP_STRIKE` (z -122.5 at the axle line, |y| 420).
  - Spare wire wheel and tyre in the boot (P11): the same parts as `wheels.road-wheels` (wheel, tyre, valve) without a
    spinner, on its clamp.
- Known P9 approximations: no outside photographs could be opened from the build machine (the proxy refuses the parts
  suppliers' image hosts), so every form is from the Haynes figures (11.1, 11.2, 11.4, 11.5, 11.6, 11.8, 1.29) and the
  suppliers' text; the stub axle is drawn level (the published 1 deg of camber is on its spec card but not applied, to
  keep P8's hub frame); the front crossmember's dip goes lower than in Fig 11.1 to pass under the sump's deep well, which
  sits over the front axle line in this model (car_layout FRONT_AXLE_X 150, see questions); the column passes through a
  tube in the RHD crossmember's right tower; the rack and pinion's internals are simplified (the yoke's pad and spring,
  rack bush and pinion bearing nut are not drawn); the inner tube is not drawn (only its valve); the rear spring's centre
  bolt locknut is not drawn; the gearbox stay rod lies to the left of the overdrive sump and its pin is screwed under
  the gearbox casing where P5a drew no pad; the front engine mounting brackets are new shapes (a pad and two tapped holes
  were added to the block's left wall, P2); the rear U-bolts' bend is lifted 12 mm above the axle centre so it passes
  over P8's axle pipe, which runs in a channel under the pedestal's thickened saddle (the legs keep their places, clear
  of the handbrake rods; the damper bracket's aft edge is trimmed to clear the right-hand rod).
- Tunnel and floor (P11) must clear the propeller shaft: from the overdrive flange (car x -1018.8, z -253.2) to
  the pinion flange (x -1807.3, z -307.9), 4.3 deg down toward the rear, 96 mm flanges, 58 mm tube; and the
  axle's movement on its springs (bump travel not yet set).
- Known P6/P7 approximations: propeller shaft joint size taken as the 27 x 74.6 mm GUJ115 joint (not
  confirmed for the MGB from a parts list with dimensions); tube, sleeve and yoke sizes scaled from Fig 7.4;
  the axle's forms from Fig 8.1 only (no outside photographs could be opened); hypoid offset (1 in), crown
  wheel size (190 mm pitch), side gear and pinion counts (16/10), bearing sizes for the differential and
  pinion, spring seat and rebound bracket positions all derived; spiral teeth are lofted trapezoids, phased
  for least overlap (about 22 mm3 crown wheel to pinion, 5.5 mm3 side gear to pinion in the interference
  check); fasteners show thread engagement as small overlaps with nuts (as P5).

- Underbody (P11a) for P11b, `mgb/underbody_layout.py` (all D, derived from P5b/P8/P9/P10 datums): cockpit floor
  underside `FLOOR_Z` -386 beside the tunnel; toe board from `TOE_FOOT` (x -485, z -386) up to the bulkhead at
  `TOE_TOP` (x -400, z -215); tunnel walls |y| `TUNNEL_Y` 122; heelboard rear face `HEELBOARD_X` -1450, from the
  floor up to the tonneau floor `TONNEAU_Z` (P10's `body_layout.TONNEAU_FLOOR_Z`, -140); body underside over the axle `ARCH_Z` -122.5 (P9's bump strike)
  between `ARCH_X` (x -1981 to -2311); boot floor underside `BOOT_FLOOR_Z` -172.5 over the tank; rear valance
  `REAR_PANEL_X` / `REAR_PANEL_LOW_Z`. P11b builds the panels to these and adds what hangs on them:
  - exhaust: the rear mounting bracket's two 1/4 UNF screws up into the boot floor (captive nuts) at x -2871 and
    -2899, y 338 (`parts/fuel/exhaust.py` rear_bracket); the system's clearances to the floor (centre silencer
    8 mm under `FLOOR_Z` beside the tunnel, y 132-336), to the tunnel and to the boot floor;
  - tank: the two strap front pins and the two rear hanger clevis pins through body tabs under the boot floor
    (`fuel_supply_layout.STRAP_PIN_FRONT`, `HANGER_PIN`, at y -232 and 78); the filler stub's hole and seal in the
    boot floor at (x -2470, y -205); the filler cap end of the filler tube at y -470, z -40 (body filler housing:
    see the question below);
  - pump: the bracket's two 5/16 UNF bolts into captive nuts in the heelboard (`parts/fuel/pump.py`
    BRACKET_BOLT_Y, BRACKET_BOLT_Z);
  - fuel pipes: seven P-clip screws (`fuel_supply_layout.CLIPS`: three under the floor at y -370, two on the
    bulkhead face, one under the axle arch, one under the tonneau floor), the hose union on the heelboard
    (`MAIN_START`), and the pipe's run across the bulkhead's engine-side face at z 70 above the pedal box "by the
    heater" (MGOC).
- P11a changes outside its own files: the exhaust manifold (P2, `parts/engine/manifolds/manifolds.py`) now has two
  outlets with four studs and sealing-ring counterbores for the twin downpipes; two gearbox side cover bolts
  (`assemblies/gearbox_casing.py`, the lowest rear pair) sit 4 mm further out on the exhaust bracket.
- Interference (P11a, scratchpad clash check against main with P8 and P10 and against wip/p9's chassis parts): no
  clashes with other phases' parts. What remains is inside P11a and intended: pipes welded into the silencer
  collars, the rubber filler hose over its retaining beads, studs and nuts in their threads. The pump sits between
  the heelboard and P10's right-hand battery carrier, clear of P10's battery cable; if
  P11b moves the heelboard (x -1450) or the carriers, the pump, its bracket and the pipe ends move with
  `HEELBOARD_X`.
- Known P11a approximations: no photographs of the bare parts could be opened from the build machine; forms are
  from Haynes Figs 3.2 and 3.9 and photos 6.14 and 46.2 with sizes derived. The early system is drawn with the two
  supports Haynes gives (gearbox clip, rear pinch clamp mounting); Rimmer Bros' early fitting kit also lists an
  intermediate mounting, not drawn. The manifold's two outlets are drawn one behind the other; the downpipe flanges
  each carry two studs across the car. The tank's plan size and depths are derived for 10 gallons between the
  right-hand spring and the rear silencer (P7's springs at |y| 420 leave little room). The pump is drawn with its
  axis across the car, inlet to the rear, outlet up; the fuel pipe runs and clip stations are derived. Welded joints
  (pipes into the silencer collars, the tail pipe into the rear silencer) and thread engagement show as overlaps
  in the interference check.
- Propeller shaft (P6) bolts to the overdrive coupling flange (`mgb/overdrive_layout.py`): rear face
  `FLANGE_FACE_X` (car x -1018.8) on the axis `FLANGE_AXIS` (y 0, z -253.21, the crank axis; gearbox taken
  as level), flange 96 mm across, four 5/16 in UNF bolts (Rimmer Bros AAA4039, 5/16 UNF x 1 1/8; MGOC nut
  BTB753) in 8.3 mm holes on a 3.125 in (79.4 mm) pitch circle at `FLANGE_HOLE_ANGLES` (45 deg from the
  top); the castellated nut and split pin stand `NUT_PROTRUSION` (6.2 mm) proud of the face inside a
  20 mm radius recess, so the propeller shaft flange needs a centre clearance. Flange diameter and pitch
  circle are derived (Fig 6.12 scale), not published.
- Gearbox rear mounting: P5b built the two rubber mountings, the crossmember and their fixings
  (`gearbox.mounting`). The body side is P9/P11, to `mgb/chassis_layout.py`: four 3/8 in UNF screws up into
  the floor at `REAR_XMEMBER_BOLTS` (car x -772.8 and -792.8, y +/-228, faces at `BODY_FACE_Z` z -381.2,
  202 mm above the road, derived), so the floor beside the tunnel needs captive nuts or tapped plates
  there. The stay rod went in with P9 (`gearbox.stay-rod`). Its bracket uses P5b's two tapped holes in the
  crossmember's bead (`chassis_layout.STAY_BRACKET_SCREWS`); the left-hand screw's head and washer overlap the
  overdrive's drain plug (P5a, car x -783, y 24) by a few millimetres. One of the two has to move (P5 follow-up).
- Tunnel (P11) must also clear the overdrive: casings 188-191 mm across, up to 96 mm above the axis
  under the remote housing; the solenoid and lever chamber cover on the right out to 141 mm right of the
  axis; the filter cover on the left at 65 mm; the sump plugs to 128 mm below the axis; the remote
  support bracket on top.
- Known P5b approximations: casing forms are from the Haynes figures only (no outside photographs could
  be opened from the build machine); tooth counts derived for 0.802 (Zs 25, Zp 38, Za 101); the
  speedometer worm and pinion are not phased (about 19 mm3 overlap in the interference check); thread
  engagement of nuts on studs shows as small overlaps; the clutch is drawn in direct drive.
- Gearbox tunnel cover with the gear lever grommet and retainer (Fig 6.3 items 161-166) and the rubber
  cover over the dipstick (Sec 2 para 1): with the body (P11). The gear lever comes up at
  `gearbox_layout.LEVER_BALL` / `KNOB`; the tunnel must clear the remote housing (top at about crank
  axis + 157 mm) and the bellhousing.
- Bulkhead and tunnel (P11): the bellhousing's back wall is at the bulkhead line (`car_layout.BULKHEAD_X`),
  so the tunnel starts there and must clear the casing (104 mm left and 84 mm right of the mainshaft,
  92 mm above it), the adaptor and the remote housing.
- Known P5a approximations: the 2nd gear thrust washer (Fig 6.3 item 97) is drawn ahead of the 1st/2nd
  synchroniser but sits behind it in the model; the selector mechanism layout (rods side by side high on
  the left, the selector lever shaft above them in the remote housing) is derived; gear teeth are
  phased to mesh in neutral (first gear and the idler's 13 teeth are out of mesh).
- Bulkhead (P11): the pedal box (P8) bolts to it at `car_layout.BULKHEAD_X` (derived).
- Hose bracket on the right-hand chassis leg (`clutch_layout.HOSE_BRACKET`) and the two pipe
  clip screws: with the body (P11).

## Carried over from P10 (electrical) for P11 (body)

All positions are in `mgb/body_layout.py` (car frame, labelled D unless stated); P11 builds the body
round them and should check them against the car:

- Headlamp nacelles: rim face `HEADLAMP_RIM_X` (95 mm behind the bumper front), centres |y| `HEADLAMP_Y`,
  height `HEADLAMP_Z` (690 mm above the road); the nacelle takes a 118 mm deep bowl behind a 198 mm rim;
  three fixing screws in the bowl flange at 30/150/270 deg. Side and flasher lamps on the wing front at
  `SIDELAMP_*` (two studs through the wing, 92 x 50 mm lozenge). Horns on the front panel at `HORN_POS`
  (foot on a ledge, 5/16 in bolt; panel face `HORN_PANEL_X`).
- Inner wing valances: engine-bay faces at |y| `INNER_WING_Y` 430 from the bulkhead to x 330; on the right
  the control box, fuse block, flasher and starter solenoid (`CONTROL_BOX`, `FUSE_BOX`, `FLASHER`,
  `SOLENOID`, 1/4 in screws), on the left the overdrive relay (`OD_RELAY`); the overdrive vacuum switch
  on the left of the bulkhead (`OD_VACUUM_SWITCH`). Bulkhead grommets: main harness `HARNESS_GROMMET`,
  battery cable through the toe board `CABLE_GROMMET`; the speedometer cable, oil gauge pipe and
  temperature capillary also pass the bulkhead/tunnel on the right (routes in parts/electrical).
- Scuttle and facia: windscreen base `WINDSCREEN_BASE_X/Z`, scuttle top falling forward at
  `SCUTTLE_TILT_DEG`; facia rear face `FACIA_X` (1.2 mm panel); holes for the instruments (80 mm
  speedometer and tachometer, 52 mm small gauges) at `INSTRUMENTS`, warning lamps (`WARNING_LAMPS`,
  10 mm holes), switches (`SWITCHES`: toggles 12.4 mm, pull switches 11 mm, ignition 20 mm); steering
  column / driver centre line `DRIVER_Y` (P9 steering column to match). Wiper wheelbox spindles through
  the scuttle at `WIPER_SPINDLES` along `WIPER_AXIS` (18 mm holes), the DR3A motor bracket on the left
  scuttle side at `WIPER_MOTOR` (three screws).
- Rear: rear lamp plinths on the rear wing ends at `REAR_LAMP_*` (three screws); number plate lamps on
  the inner faces of the rear overriders (`OVERRIDER_Y`, `NUMBER_LAMP`), two screws each.
- Battery carriers: two boxes hang under the tonneau floor behind the seats at `BATTERY_BOX_X`,
  |y| `BATTERY_BOX_Y`, floor underside `TONNEAU_FLOOR_Z` (z -140, 443 mm above the road; set high enough that
  the boxes' bottoms clear P8's rear brake pipe and handbrake cable, which run under them at z -394 and -387),
  186 x 236 x 226 mm inside, 22 mm flange with four bolt holes; P11 adds the floor, the access panel with quick-release screws (photo 2.1), the
  earth bolt and the cable grommet through the box's front wall.
- Fuel tank sender (Fig 10.26 item 35) and its lead: with the tank (P11).
- Known P10 approximations: unit positions in the engine bay, the facia layout and every harness
  route are derived (no photographs of a 1963 engine bay or facia could be opened from the build
  machine); the 18ACR, M418G, DR3A and the instruments are modelled from the Haynes figures and
  common pattern sizes, not measured; lens optics and dial figures are not drawn (individual wires: P10b);
  the thermal transmitter sits on the head's right face, which has no boss for it in P1 yet.

## P10b wiring harness: what was built and assumed

- Wire list from Haynes Fig 10.26 (wiring diagram, models up to 1967, printed p190, key p189; rendered at 300 dpi
  and read section by section) and Fig 6.19 (overdrive circuit, p131); fuse duties from Sec 33 para 1 (fuse 1-2:
  horns, unfused-ignition items; fuse 3-4: stop lamps, fuel gauge, flashers, wipers). Cable sizes and outside
  diameters: Auto Electric Supplies standard cable table and Autosparks PVC cable (S). Conversion practice: mgaguru
  "generator to alternator" (Barney Gaylord), Moss conversion instructions 130-068, MGOC Spares (RB340 GEU6605, 4FJ).
  The specs are `specs/electrical/wiring-*.yaml` (one per circuit); every wire has its `wire:` block for the viewer
  card and a `route:` (its two terminal keys). Terminals: `mgb/electrical_layout.py terminals()` (P10/P5/P8/P11a
  components) and `mgb/wiring_layout.py terminals()` (the parts P10b adds); harness graph, joints, bundle layout:
  `mgb/wiring_layout.py`. Each wire leaves its terminal along the terminal's direction, follows the shortest path
  through the harness graph in its own slot of the bundle (hexagonal rings round the path), and lands on the other
  terminal with its fitting (female Lucar and PVC sleeve, sleeved bullet on a pin, eye on a stud, or into a moulded
  plug, bulb holder or joint).
- 18ACR conversion as modelled (an assumption, see questions): the RB340 control box stays on the wing but is
  bypassed; its two B terminals' browns (from the solenoid, to fuse A1) and the two browns from the alternator's +
  blades meet in a four-way snap connector beside it; the warning lamp's brown/yellow (old WL lead) is joined in a
  bullet connector to the old dynamo D lead's brown/yellow, which now goes to the alternator's IND blade. The old
  brown/green field lead (F) is redundant and not drawn. The car is taken as converted to negative earth throughout:
  the battery's positive post to the solenoid, the negative to the body; the HA12 coil's leads swapped (ignition
  white on CB, the distributor's white/black on SW); the tachometer's pulse loop reversed.
- Warning lamps moved into the instruments (Fig 10.26: ignition 44 in the tachometer 95, main beam 10 and the
  indicator arrows 27 in the speedometer 45 and tachometer): P10's three separate facia warning lamps are gone; their
  lenses sit on the dials, lit from bulb holders in the cases.
- Parts P10b added: headlamp dip switch on the toe board, direction indicator switch clamped on P9's outer column tube below the wheel
  (`wiring_layout.COLUMN_SWITCH`), with the horn push lead up beside the column to P9's horn push, instrument voltage stabiliser (item 64; Haynes draws it on the early diagram,
  see questions), harness joints and snap connectors, earth points (`body_layout.EARTH_POINTS`), the bulkhead
  grommet, and the braided sleeving sized to each bundle. Changes to P10 parts: the fuse block's blades now leave its
  ends (photo 33.1), the flasher has three blades (B, L, P), the alternator plug's stub leads are gone (the harness
  leads enter it), the coil's low tension lead is now the harness wire, the instrument cases have the extra bulb
  holders and the tachometer's pulse lead pins, the battery and starter cables and the earth strap moved to the
  wiring assemblies.
- Interference check (P10b, every wire's centre line and surface sampled every 2.5 mm against every other system,
  each hit confirmed by surface distance; joints, earth points and switch gear by booleans): no wire passes through
  another part; wires touch only their own
  terminals and bundle mates; the column switch's cancelling cam touches the column's swaged top (3 mm3).
- Known P10b approximations: every harness route, joint position and the order of the wires in each bundle are
  derived; joints (soldered splices in the factory harness) are drawn where the circuit splits, so the real harness
  may split at other places; terminal numbers on the lighting switch (4, 7, 8) and ignition switch (1, 2, 3) are as
  read on the diagram (the drawing is small); the map lamp, heater blower motor and horn push are not built (their
  leads end at connectors or the column switch); reversing lamps, fog/spot lamps, radio and cigar lighter are not
  fitted (dashed or later items on the diagram); cables are drawn 8-sided.

## Carried over from P10b (wiring) for P11b (body) and P9 (steering)

- Grommets and holes: the main harness grommet in the bulkhead (`body_layout.HARNESS_GROMMET`, about 38 mm hole);
  the rear harness passes the heelboard at x `underbody_layout.HEELBOARD_X` (+30 mm, cabin face) beside the right
  sill and on over the right-hand wheel arch at about z -90 (`wiring_layout` nodes re.*): a grommet or clip there, and
  where the pump lead goes back through the heelboard to the pump (y about -430, z -345) and where the tank unit lead
  goes down through the boot floor to the gauge unit (x about -2530, y -420); the number plate lamp leads pass
  through the rear panel/overriders; the overdrive leads pass the bulkhead/tunnel at about (x -430, y 120, z -120);
  the dip switch's leads come up the toe board from (x -445, y -165).
- Clips: P-clips along the inner wing tops (z 118, |y| 405), across the front panel behind the grille (x 560, z -40),
  along behind the facia (x -655, z 277), down the right sill (y -591, z -350) and in the boot; the facia harness
  runs need a bracket or the facia's own clips.
- Earth points on the body (`body_layout.EARTH_POINTS`, No 10 self-tapping screws): headlamps (front panel behind
  each lamp), left valance by the overdrive relay, facia rear face, scuttle by the wiper motor, boot (right-hand
  side by the tank), heelboard by the fuel pump.
- Heater blower (`body_layout.HEATER_CONNECTOR`) and map lamp (`MAP_LAMP_CONNECTOR`): the harness ends at their
  connectors; the units are the body's.
- Steering (P9 built): the direction indicator switch is clamped on the outer tube 56 mm below its swaged top
  (`wiring_layout.COLUMN_SWITCH`); a column cowl, if wanted, should enclose it. The horn push lead runs outside the
  tube to the push; the real contact (slip ring or brush in the wheel boss) is not modelled.
- Fuel (P11a built): the pump lead ends on the SU pump's end cover terminal stud and its earth lead goes from the
  cover to an earth screw on the heelboard; the tank unit's two blades take the green/black lead and its earth.
## P11b body (done): what was built and what is left

- Assemblies: `body.structure` (floor halves, tunnel, toe boards, bulkhead, scuttle inner panel and facia rail, front
  legs, inner wings and wheel houses, front apron and radiator duct, lock platform, inner and outer sills, castle
  sections, jacking sockets, hinge and shut pillars, heelboard, tonneau floor and battery covers, rear bulkhead, rear
  wheel houses, boot floor, rear rails, tank tabs, the brackets for P4/P8/P9/P10/P11a, and P10b's wiring passes:
  grommets and P-clips), `body.front` (wings, grille panel, valance, bonnet skin and frame, hinges, stay, lock,
  scuttle), `body.doors` (skins, frames, hinges, wind-up glass, quarter-lights, pull handles, locks, strikers, the
  driver's door mirror), `body.rear` (rear wings, deck, boot lid skin and frame, hinges, handle, lock, rear panel, the
  spare wire wheel on the black boot carpet with its clamp, jack and mallet), `body.glass` (windscreen, pillars, rails,
  centre rod, mirror), `body.brightwork` (bumpers with rubber-faced overriders, spring bars and brackets, the slatted
  grille in its surround with the lower rail, centre bar and plain shield badge, the scuttle air intake, side strips,
  plain octagon boot badge, blank plates and plinths), `body.interior` (facia, centre panel, plaque, heater knobs,
  binnacle, crash roll, glovebox lid and strip, console with the speaker grille, seats with red piping, carpets, door
  cards, handles, winders, cappings, gear lever grommet and retainer, dipstick plug), `body.hood` (hood erected).
- The main reference is Oliver's own car (28 photos, scratchpad refs/oliver-car, not in the repo) and the
  near-orthographic side view of a sister car (photo 29), scaled on the 91 in wheelbase: the side elevation (overhangs,
  top line, waist, strip, door shut lines, sill, arches, screen rake and height, lamp rake) is traced from 29, the
  front, rear and plan proportions and every fitting from Oliver's photos (cameras fitted to wheel, lamp and screen
  points; comparisons in scratchpad p11b/cmp-*.png).
- How the outer skin is made: `mgb/body_shell_layout.py` defines the body as an implicit solid F(x, y, h) < 0 from
  height and width functions (C2 splines through the traced stations): the side with its tumblehome and tuck-under,
  the top with the cambered bonnet, the front wing crowns standing proud of it and the bonnet swage, the nose (grille
  surround and valance at the centre, the wing fronts round the headlamps, swept back in plan) and the tail (the rear
  panel and the valance under the bumper down to the sill line, the flat raked lamp plinths on the square wing ends
  with a crisp outer edge), joined by cubic smooth maxima so the nose and tail roll into the
  sides and top without creases. `mgb/body_shell.py` samples F along rays leaving a core ellipse in planes square to a
  spine that turns down round the nose and the tail (so the rays never cross and the crowns cannot shadow the bonnet),
  fits one least-squares bicubic B-spline face (150 x 110 poles, light smoothing; 0.1 mm mean, under 2 mm at the 99th
  percentile, from the samples on the skin) and trims each panel out of it with a signed-distance region along its
  shut lines, then thickens it 1 mm inward. Results are cached in `.cache/body/` (git-ignored) keyed on the layout
  files; bump `CACHE_VERSION` in body_shell.py when the trimming code changes.
- Datums: `mgb/body_shell_layout.py` (body shape tables, shut lines, arches, screen, hood) and the moves listed under
  "Changes P11b made to earlier phases" below.
- Interference: the front tyre at full lock (28 deg front in, 37 deg rear in, from the 32 ft turning circle) clears
  every body part at static height; this needed the front legs stepped inboard to |y| 338 ahead of and behind the
  crossmember and the inner wing's lower edge raised there (tests/test_body.py checks the legs). With 60 mm of bump at
  full lock the tyre still reaches the inner wings and the legs (P9 has not set a bump travel). The bonnet skin clears
  the radiator header tank (tests/test_body.py). A check of every body panel's surface points against every other
  system's solids (scratchpad q/clash_body.py, from the build's STEP files) found these real clashes, now fixed: the
  bonnet frame's side bands over the radiator's header tank (cut away there), the pedal arms through the bulkhead
  (slots added below the pedal box aperture), the headlamp bowls and side lamp studs through the wing skin (the
  openings followed P10's old lamp positions), the filler cap against the right rear overrider (cap moved to y -425),
  the instruments' and switches' bezels and nuts in the raised centre panel (larger holes), the dual gauge under the
  plaque (plaque narrowed), the map lamp switch under the crash roll, the seat squabs through the heelboard into the
  fuel pump (squabs moved forward), the battery cable through the seat cushion's base (cushions raised 12 mm). The
  rest are intended mountings (units and brackets on their panels, fasteners through holes, the tank's hangers on
  their tabs, the handbrake ratchet plate on the tunnel, the dampers on the rail doublers, lamps seated on the wing,
  the instruments' bezels on the facia face) and two small ones left: P9's front coil springs touch the front legs'
  undersides (a few mm at |y| 428) and the speedometer cable passes the scuttle inner panel without a hole. Not
  checked: the rear axle at full bump against the boot floor's hump, the propeller shaft at full bump against the
  tunnel (static clearance about 35 mm).
- Known P11b approximations: no body drawing with dimensions; the shape is traced from photographs (about +/-10 mm on
  the side elevation, more on the plan and sections, which come from oblique views). Arch lips are a dark return band
  (body.structure.arch-liners) rather than a rolled flange; door and boot drip
  rails, the boot lid and bonnet return flanges are not drawn; the door glass is flat, the hood a smooth cover without
  seams; seat pleats are grooves; small fixing holes under about 3 mm radius in the skins are not cut. Lettering on
  the badges, plaque and plates is not modelled; the grille's club badges (AA and the MG car club) are not drawn.
  The tonneau cover (photo 25) is not modelled (the hood is shown erected).
- Leftovers: heater unit (Fig 12.27) and its ducts; windscreen washer; sun visors; tonneau cover; door check straps;
  bonnet and boot seals.
- Window and screen closures (QA round 1, Oliver's photos 08, 09, 15, 23, 27): the quarter-light frame is toed in
  so its front edge closes on the windscreen pillar's rear (closures `QL_FRONT_X`, `QL_FRONT_Y`, `ql_y`), with a
  rubber seal (body.doors.quarter-light-seal-*) touching both; it swings clear of the pillar as the door opens (8 mm
  at 2 deg). The screen pillars, top and bottom rails are flat chrome channels round the glass's edge (the glass
  runs into them); the bottom rail has its seal to the scuttle. The door glass runs 8 mm up inside the hood's edge
  (GLASS_TOP_H 1100); the hood's lower edge follows the quarter-light top, the glass's top and raked rear edge, and
  then the body's top behind the door (the hood's rear quarters), and its back edge lies on the rear deck. The crash
  roll ends inside the pillars and the facia rail follows the scuttle's fall (both showed through the skin).
- Door glass (QA round 2, Oliver's photos 08, 09, 23): it runs the whole length of the door, from the quarter-light
  post's channel to the rear shut line (`GLASS_REAR_X` = DOOR_REAR_X + 14), its rear edge raked forward 36 mm and
  rounded 75 into the top, curved 5 mm in its height, in a rear run channel inside the door
  (body.doors.glass-channel-*); the hood's rear quarters come down to the body right behind it.
- Door, bonnet and boot mechanisms (assemblies body.door-mechanisms and body.closure-fittings, parts/body/mechanisms.py;
  Haynes Ch 12 Secs 6, 25-27, 29, 33, 35, 38, 39, 42, Figs 12.12, 12.13, 12.15, 12.17; Oliver's photos 08, 11, 13, 14,
  28): each door's window regulator (mounting plate, quadrant and pinion on the winder spindle, balance spring, lift
  and extension arms with their studs in the glass's lower channel, the extension's pivot plate, arm stop and
  buffer), the early lock with its operating link from the pull handle, the remote control from the inner handle,
  the lock housing and barrel in the handle's front boss, a check strap, the interior pull, the trim clips, the
  aperture seal and the striker's packing and tapping plate; the bonnet's lock plate and catch, control cable and
  pull knob, safety catch, and the prop stay stowed on the right inner wing (photos 13, 28); the boot lid's stay
  stowed in its clip on the lid, its guide, the boot lock with its operating lever and the striker loop, and the
  aperture seal. Hide body.doors.skin-* and body.interior.door-card-* to see the regulator and lock. The doors, bonnet
  and boot lid are modelled closed (the stays stowed).
- Measured QA (scratchpad p11b/qa/qa-table.md): cameras solved for Oliver's photos from the number plate (520 x 111),
  lamps, wheels and screen; the straight front and rear views (15, 14, 18, 25, telephoto) measure the front and rear
  directly in mm off the plate. Moves from it: side/flasher lamps 495 -> 461 above the road (`SIDELAMP_Z`); rear
  lamps |y| 661 -> 634, centre 678 -> 673 high, 292 x 84 mm with a pointed top, amber over the top 42 % and a chrome
  bar 69 % down; filler cap |y| 425 -> 382 and 560 -> 588 high (P11a `fuel_supply_layout`); rear overrider tops
  600 -> 572 and front 506 -> 519; rear bumper blade 430-495 -> 424-474 (the plate stays at 507-618); rear valance's
  lower edge 280 -> 300; grille opening 596/428 -> 589/423; tail pipe end REAR_X + 70 -> + 95 (P11a
  `exhaust_layout.TAIL_END_X`).
- Viewer note: the body hides the mechanicals; hide or isolate a system from the Parts tree.

- Scan QA (5 Nov 2026, Oliver's photogrammetry scans; not in the repo): registration in `mgb/scan_layout.py` (body scan
  by its own symmetry plane and trimmed ICP of the red paint onto our panels, checked on the four wire wheel rims: scale
  good to about 0.5 %, rims symmetric within 1 mm; engine scan on the rocker cover's corners and the inner wing flanges,
  about +/-25 mm). Oliver's instruction: the scans give the layout, scale and flow; reflections on the glossy panels made
  dents, blobs and holes, so only low-reflection regions that agree left and right are used, and parts are not moved to
  match the scan except for minor appearance adjustments. Round 0 (pending work of the first scan pass): rear deck and
  waist heights, door tops 862, rear width at the lamps, rear bumper height and bow, raked overriders, tail pipe end,
  arch lips, the black cockpit-rim roll, hood seams, smooth surface normals on the body panels, the polished finned
  rocker cover, chrome pancake air filters and the yellow fan (engine scan). The door glass's bow now starts tangent at
  the waist (a kink there broke its thickening).

- Scan QA round 1 (5 Nov 2026; transverse sections every 50 mm and plan widths from the registered scan, robust upper
  envelopes, both sides compared; scratchpad sw2/): Oliver's priority, the rear quarters. The rear wing crowns
  are the highest points; from each crown the surface drops inboard into a dip and the rear deck and boot lid stay at
  that level right across (8 mm camber; Oliver's correction: no bulge in the middle of the boot), falling gently from
  the cockpit's rear and rounding off at the back along the dips' curve (`DECK_H`, `DECK_Y`: 803 above the road at
  x -2400, 779 at -2600, 735 at -2800, 60-75 mm under the crowns; the scan's high lid centre is reflection lift); the
  plinths' top corners rise to 830 and the rear wings taper in plan
  to the plinths (752 at x -2400, 731 at -2600, 697 at -2800: `W_M`, `TAIL_PLAN`), so the lamps sit at the body's
  outer corners as in photos 14, 24. Oliver's car sits about 22 mm lower at the back than the model's standard ride
  height (scan: the rear rims 20 mm higher in the body, its road 24 mm higher), so the rear fittings measured above his
  road in the photo QA are 22 mm higher on the body: rear lamps (centre 695), bumper blade 438-503, overriders to 600,
  plate 529-640, filler cap, number plate lamps, reflectors, tail pipe; the lamps' amber now covers the top 36 %. The
  sills' lower edge is 22-26 mm lower under the doors (228 above the road, 75 mm under the front wheel centre in photo
  09; the scan is reflection noise there). The rear wheel arch opening is a flattened arch (half an ellipse 320 x 180 on a
  line 470 above the road, vertical below; `REAR_ARCH_E`), as the scan shows on both sides within 10 mm; it was a circle. The nose rolls over the grille in a fuller lip (25-45 mm further forward at
  h 600-650; `NOSE_C`, `TOP_C`, `NOSE_TOP_K`), the bonnet's front edge on it. The windscreen is taller and more
  upright (top rail 1180 at the centre, 1150 at the pillars, 33 deg; it was 1118 and 45 deg), the quarter-lights and
  door glasses 60 mm taller to meet it (scan: quarter-light top 1150). The screen's bottom seal is now its own black
  rubber part, a bead on the scuttle along the rail's foot. The door glasses hide with the hood in the viewer (hood
  down, they are wound down out of sight), which removes the clear panel that stood behind the seats.
  Treated as reflection noise and not followed: the blobs and holes along both doors and sills, the bonnet's holes,
  the left side's deeper deck valley ahead of x -2600 (the right side has none; the model takes the mean), the red
  points under the rear bumper, the lamp lenses in the wing sections.

- Engine bay structure (QA round 2, Oliver's second priority; his engine-bay scan re-registered on the outer wings
  and headlamps, sections every 25 mm): the inner wings are now the wheel arch domes the scan shows - from the chassis
  leg's top they slope out and up to about |y| 520 at 640 above the road, then rise nearly vertical to a bolting flange
  under the outer wing's top with the wing bolts' heads along it, a swage along the wall, two drain holes; closed down
  to the leg (`iw_section`, `iw_wall_y`). The bulkhead steps back at a shelf 625 above
  the road to an upper face 155 mm behind it under the scuttle's front edge (the heater's place), with the heater
  opening, a swage, the scuttle drains and grommet holes (body.structure.bulkhead-upper). A front pan between the legs'
  feet under the radiator with the radiator's side brackets bolted through its channels and the duct side panels out
  to the inner wings (body.structure.front-pan); slam panel stays from the lock platform to the inner wings
  (body.structure.slam-stays). P10's units, P10b's harness clips and P9's hose brackets hang on brackets standing off
  the sloping wall (body.structure.inner-wing-brackets); the fittings earlier phases put on the old flat bulkhead
  above the shelf's height (harness and instrument grommets, choke grommet, vacuum switch, the fuel pipe clip) on
  plates standing on the shelf (body.structure.bulkhead-brackets); the bonnet stay and release cable follow the new
  wall. The bigger differences (engine 160 mm further back on the car, electric fan, heater, washer bottle, unit
  positions) are listed under "Differences seen in Oliver's scans".
  Clash check after it (scratchpad q/clash_body.py against every other system): the new contacts are the intended
  mountings (P10's units, the grommets, the vacuum switch's screws, the choke grommet and the fuel pipe clip on their
  new brackets and plates, P10b's wires lying on the brackets where they lay on the old panel, P9's hose on its gusset).
  Fixed: the radiator's bottom tank through the front pan (an opening for its foot), the headlamp bowls' backs and the
  wiper motor through the inner wings and the upper bulkhead (clearances), the front arch liners showing inside the
  sloping inner wings (moved outboard), the rear lamps' lower ends sunk 4 mm into the steeper plinths (lamps 4 mm back).
  Left: P9's front dampers touching the closed domes (see the differences list), the filler tube at the rear panel's
  hole edge (36 points).

## P3b throttle and choke controls: what was built and assumed

- Assemblies: `fuel.throttle` (accelerator pedal, pad, welded pivot bracket, distance tube, pivot bolt, washer and nyloc
  nut; RHD pedal stop on the toe board with its stop screw, locknut, two pan screws and spring washers; cable guide and
  gasket on the bulkhead with two screws and nuts; the cable outer with crimped ferrules and the inner's exposed ends,
  the barrel nipple and split pin at the pedal; the P-clip, screw and nut on the pedal box cover; the abutment bracket
  on the heat shield with its two screws and nuts; the throttle shaft lever with its pinch bolt and nut, the swivel pin,
  two washers, anti-rattle washer and split pin; the interconnecting shaft, two folded clamps with their pinch bolts
  and nuts; both throttle levers with nuts, tab washers, adjusting screws and springs; three return springs) and
  `fuel.choke` (the "C" knob, the control's bezel and bush, nut and shakeproof washer behind the facia; the cable outer
  and the inner's end; the bulkhead grommet; the abutment, nut and spring washer on the bracket; the trunnion; the
  cable lever with its bolt, spring washer and nut; the interconnecting rod and its two lever-and-pin clamps with
  bolts, washers and nuts; each instrument's jet lever and link with its screw to the jet head, pivot bolt, tube, two
  washers and spring). Explode stages follow Haynes Sec 45 (cables) and Sec 21 (linkage). Datums:
  `mgb/throttle_layout.py`.
- References: Haynes Ch 3 Fig 3.10 (printed p73, items 35-72, rendered at 220 dpi and read item by item), Fig 3.13 (p76:
  the cable coming down to the shaft lever between the instruments, the shaft lever's stop over the choke
  interconnecting spindle, the clamps' pinch bolts), Fig 3.17 (p77), photo 17.1(b) (p72: the return springs hooked
  down to the heat shield's lip), photos 18.2 and 18.3(a) (p75: the inner coming steeply down to the swivel pin, the
  springs on the levers), Sec 21 (p76: 0.012 in fast idle feeler, the folded clamp), Sec 23 para 22 (p77: 1/16 in
  free movement of the choke wire), Sec 45 (p92: pedal pivot bolt, split pin at the pedal's end, the choke trunnion's
  screw); Ch 12 Sec 47 para 4 (p232: the choke cable nut behind the facia and the air cleaner bracket). The factory
  service parts list (plates 108-G2 and 108-G4, chassis 101-138400, barneymg.chicagolandmgclub.com) for the early part
  numbers: pedal AHC135 RHD, pad GPR105, distance tube AHH6504, pedal stop AHB7162 RHD, cable guide AHH5308, cable
  AHH6997 RHD, choke cable BHH526, choke control bracket AHH6731, outer cable abutment AHH6734. Rimmer Bros
  GRID019709 and MGOC Spares ("pedals", "accelerator choke cables", "carburettor linkages cables") for the fixings
  and the three AEC2075 return springs, the P-clip to the pedal box cover on single-line cars, the swivel pin ACC5062,
  the choke trunnion AUE34 and the round "C" choke knob of 1962-69 cars. Oliver's photo 16: the knob right of the
  ignition is lettered C (zoomed: scratchpad p3b/knob16.png), so it is the choke.
- Known P3b approximations (all positions D): no photographs of the early bare parts or of an early car's throttle
  cable run could be opened from the build machine, so every form is from the Haynes figures and photos and the
  listings' descriptions. Haynes covers the throttle pedal and cable only for cars from 41002 (Sec 45); the early
  arrangement is inferred from the parts list: a pendant pedal with the inner on its top arm, the outer from the
  bulkhead guide P-clipped to the pedal box cover, and (from Fig 3.13) coming down to the shaft lever between the
  instruments, where it is drawn seating on the same bracket as the choke abutment. The cable route behind the head
  is derived. Fig 3.10 draws the later HS4 linkage (cam levers, forked throttle levers); the model keeps its items 38-45,
  46/47, 59-72 and Fig 3.13's stop-on-the-rod fast idle, without the cam levers 53/54 and their springs 55/56. The jet
  levers pivot on a bolt into a boss cast on the body instead of on the float chamber bolt (item 26), which has no
  room in the P3 carburettor model. The pedal's return relies on the three carburettor springs (plate 108-G2 lists no
  pedal spring). The pedal and linkage are drawn at rest (closed throttle, choke home); the travel is not modelled, and
  the pedal stop's screw (HZS412, 1/4 UNF x 1 1/2 in by its code) is drawn near the toe board's foot, 5 mm short of the
  arm, because the drawn arm runs close to the toe board higher up. The choke knob's C is a white infill part.
- Interference (scratchpad p3b/tools/clash2.py: every new instance against each other and against every instance whose
  box meets it, built from source for fuel, the bulkhead, facia and pedal box cover, from the build's STEP files for the
  rest; the body skins checked by distance instead - the cables pass 61 mm or more under the bonnet): no clashes with
  the engine, heater-side fittings, wiring, brake and fuel pipes or the steering column. What remains is intended:
  screws and nuts in their threads (pivot bolts into the bodies' bosses, the link screws into the jet lugs, the spindle
  nuts, 9-70 mm3 each), the P-clip gripping the outer (47 mm3), and the pedal stop's fixing and stop screws passing the
  toe board's carpet into the toe board (under 200 mm3 each). Along the way the check found and fixed: the heat shield's
  lip through the jet heads and their feed tubes (the lip now has notches there), the cable P-clip and its screw in the
  pedal box cover's lower step (moved onto the top), the cable over that step, the pinch bolts' nuts in the clamps' hubs,
  the jet levers' bosses in the body bosses and washers, the lever-and-pin clamps against the barrels and intake flanges,
  the pedal stop in the carpet and against the arm.

## Changes P3b made to earlier phases

- `fuel.carbs` (P3): the crude coupling shaft, jet rod, throttle levers and return springs are gone (rebuilt in
  `fuel.throttle` and `fuel.choke`); the throttle spindle is 130 mm long (was 100) so its inboard end reaches the
  coupling; each body has a throttle stop lug off the engine flange and a boss under the barrel for the jet lever's
  pivot bolt; the heat shield has the three return spring holes in its lip and the bracket's two screw holes.
- `mgb/body_layout.py` (P10/P11b): the push-pull knob right of the ignition (P10's "panel-lamp") is the choke; the
  panel lamp pull switch moves to the pull knob in the binnacle between the speedometer and the tachometer (photo 22),
  `SWITCHES["panel-lamp"]` = (DRIVER_Y + 17, IP_Z + 8). P10b's wiring follows it (`mgb/wiring_layout.py`: the facia
  run's panel switch node now branches off the driver's node). This invalidates the body cache (`.cache/body/` is keyed
  on body_layout.py).
- `parts/body/interior.py` (P11b): the facia and the centre panel have the choke control's hole at
  `throttle_layout.CHOKE_KNOB`. `parts/body/structure.py` (P11b): the bulkhead has the cable guide's hole and screw holes
  and the choke grommet's hole.
- `parts/brakes/master.py` (P8): the pedal box cover has a hole for the cable P-clip's screw.
- `fuel.carbs` heat shield: notches in its lip round the jet heads (the lip ran through the jets' heads and feed tubes).
- `viewer/index.html`: SYSTEM_EXPLODE for `fuel.throttle` and `fuel.choke` (no new finishes).

## Changes P11b made to earlier phases

- `mgb/car_layout.py`: FRONT_OVERHANG 760 -> 681 mm (profile photo 29: the overriders 681 ahead of the front hub, the
  rear 899 behind the rear hub; the published length is kept), so FRONT_X 909.9 -> 831 and REAR_X -2981 -> -3060. P11a's
  tail pipe (exhaust_layout TAIL_END_X) follows REAR_X; P11a's REAR_PANEL_X is now REAR_X + 105 (the rear panel face,
  photo 29).
- `mgb/body_layout.py` (P10's datums for the body), moved to Oliver's car: headlamp rim face FRONT_X - 95 -> - 186
  (x 645), centres |y| 561 -> 585, height 690 -> 632 above the road; side/flasher lamps to x 691, |y| 569, 461 high,
  and rectangular (136 x 52, amber inboard, clear outboard, chrome surround; P10 drew a 92 x 50 lozenge), the right
  lamp turned over so the clear part is outboard on both sides; rear lamps onto the flat raked wing-end plinths (REAR_X +
  195, |y| 634, 673 high, raked 33 deg, `REAR_LAMP_RAKE`), 292 mm on the rake (250 mm high seen from behind) and 84
  wide in a chrome rim with a pointed top, amber over the top 42 % and red below (P10 had a 172 mm lamp with red on
  top);
  rear overriders |y| 262 -> 340; the side strip 663 -> 690 above the road; the instruments and switches to the
  facia layout of photos 01, 04, 16, 22 (speedometer left and tachometer right in the binnacle over the column, fuel
  gauge further right, the dual gauge on the centre panel right of the plaque; three toggles, ignition and push-pull
  knob in a row under the plaque; the overdrive toggle outboard); new `PLAQUE_*`, `HEATER_KNOB_*`. The P10 lamp and
  instrument parts and P10b's terminals follow the datums; P10b's harness nodes at the headlamps and side lamps
  (`wiring_layout` hl.*.n, side.*.n) moved with them. The headlamp light units are now drawn as a reflector
  (aluminium) behind the lens.
- P11a filler (`fuel_supply_layout` FILLER_CAP_X/Y, FILLER_TUBE_TOP_Z; `parts/fuel/tank.py`; `assemblies/fuel_tank.py`):
  the filler tube now runs back across the boot to a chrome locking cap on the rear panel right of the number plate
  (photos 11, 18, 21), 560 mm above the road, outboard of the right-hand overrider; P11a had it ending at the right of
  the boot. P11a's tail pipe now ends under the bumper blade (exhaust_layout TAIL_END_X = REAR_X + 70, profile photo
  29), about 55 mm behind the new rear valance, below its lower edge; the valance hides the tank and silencer from
  behind (photo 18).
- `viewer/index.html`: FINISH vinyl_black, carpet, hood_black, paint_body_red (#d8261c, the body), piping_red,
  underseal (the floor pan, tunnel, toe boards, legs, rails, castles), glass_screen (the windscreen, and the hood's rear window: a flat clear panel set into an opening
  cut in the cover); SYSTEM_EXPLODE for the body
  assemblies; the review hook `window.mgbCamera` also takes an exact camera ({pos, at, fov} in CAD mm) and a list of
  nodes to hide ({hide: [ids]}), so renders can be laid beside photographs. P10b `wiring_layout`: the facia run's nodes follow the moved instruments and switches,
  and `smooth()` keeps a corner where a route folds straight back (it divided by zero). `build.py` uses an assembly's `LOD` (new "body" tessellation in `mgb/export.py`). `.gitignore`: .cache/.
- P4's clutch hose bracket stays where P4 put it, carried by a new support on the bulkhead; P9's column bottom bracket
  sits on a body cup 40 mm behind the bulkhead.

## Changes P10 made to earlier phases

- `cooling_layout.ALTERNATOR_AXIS` moved to (y -198, z -106) and the alternator pulley pitch radius
  to 32 (2 3/4 in pulley) so the pulley clears the fan blades; the fan belt follows.
- Water pump body: an ear on the right of its flange for the front pivot bolt (Fig 2.6 item 34).
- Engine front plate: a notch in the right-hand wing round the alternator body and a hole for the
  adjusting link stud.
- Engine rear plate and gearbox bellhousing: holes for the starter's two bolts (tapped in the
  bellhousing lobe).
- Sump, sump gasket and block skirt: a recess round the starter yoke at the right rear (the sump's
  three right-hand rear flange bolts go; the block keeps a wall round the recess).

## Questions for Oliver

- Scans (5 Nov): which of the differences listed under "Differences seen in Oliver's scans" should be followed - above
  all the engine's fore-and-aft position (the scan puts it about 160 mm further back) and the electric fan, heater and
  washer bottle? Does the car sit low at the back (new springs due), and are the rear wheel arches' tops about 650 mm
  above the road with the car on its wheels?

- Bonnet release: which side of the facia is the pull knob on (modelled under the left end, the cable along the left
  inner wing, from the catch's lever in photo 13)? Is there a door check strap on your doors? (asked at the end of the overnight run)
- Throttle and choke (P3b): the model hangs the accelerator pedal from a bracket on the bulkhead outboard of the brake
  pedal, its cable through a guide in the bulkhead, up over the pedal box cover (P-clip), behind the cylinder head and
  forward between the rocker cover and the rear dashpot to a bracket on the heat shield between the carburettors, where
  it drops to a lever on the throttle interconnecting shaft. Photos of your engine bay looking down at the back of the
  engine and at the linkage between the carburettors (air cleaners off), and one of the pedal in the footwell, would
  fix the route, the bracket and the pedal's shape.
- Choke: the knob right of the ignition reads "C", so the model makes it the choke (P10 had it as the panel lamp
  switch) and moves the panel lamp switch to the small pull knob in the binnacle between the speedometer and the
  tachometer (photo 22). Is that knob the panel lamp switch? Which is the small knob above the oil/water gauge (the
  model keeps it as the map lamp switch), and the knob at the far left of the facia beside the glovebox (photo 04)?
- Choke cable: does it pass the bulkhead left of the heater (as modelled) and is it clipped to an air cleaner bolt
  (Haynes Ch 12 mentions an air cleaner bracket on early cars)? With your box-type air cleaners, where does it run?
- Jet linkage: the model gives each carburettor a jet lever on a pivot bolt under the body joined by a rod, with a
  lever on the rod for the choke cable, and the throttle shaft lever's stop resting on the rod for the fast idle
  (Haynes Fig 3.13). If your carburettors have the later cam-lever linkage (Fig 3.10 items 53-56), say so.

- Body (P11b): the shape is traced from your photos and from a side view of a sister car (photo 29). A tape measure on
  a few points would let it be checked: wheel arch tops above the road, the bonnet's front edge and the scuttle at the
  screen above the road, the front of the overriders to the front hub, the door's front and rear shut lines from the
  front hub, the headlamp centre height.
- Hood: is yours the early detachable hood (frame stowed in the boot) or a folding hood? The model shows it erected;
  photo 25 shows a tonneau, which is not modelled yet.
- Facia: which toggle is which (the model has lighting, wipers, heater blower from left to right)? (The knob right of
  the ignition is the choke - its "C" - see the P3b question above.)
- Radio: the console carries a speaker grille (photos 04, 22); is a radio fitted (where), or only the grille?
- Grille badges: the model leaves off the club badges on the grille (AA and the MG car club). Should they be drawn?
- Door mirror: only the driver's (right) quarter-light has a mirror in the photos. Is there one on the left too?


- Hood: is it the early detachable "build-up" hood with the frame stowed in the boot, or a later folding hood? Do you
  have a tonneau cover?
- Door top height: the model puts the door top (waist) 870 mm (34.3 in) above the road, under P10's screen base at
  915 mm (36 in) and the strip line at 663 mm (the published 14.25 in above the hub). No published waist height was
  found; a review note suggested 38-39 in, which would put the door top above the scuttle. What does yours measure?
- Body shape: the model puts the door's front and rear shut lines 922 and 1852 mm behind the front hub centre, the
  door top 870 mm above the road, the bonnet's front edge about 720 mm and the scuttle at the screen 915 mm. A tape
  measure on those (and the wheel arch tops) would let the shell be checked.
- Front wheels at full lock: the model's tyre at full lock (and the king pin 132 mm inboard of the wheel centre plane,
  P9) only clears the front chassis legs because they step inboard ahead of and behind the crossmember. How close
  does your tyre come to the legs and the inner wings at full lock?
- Starter solenoid: P10 put it on the right inner wing at x -60, z -70; at full lock with bump the right front tyre's
  rear shoulder passes within the inner wing's line there. Where is the solenoid on your car?

- Exhaust: is your car still on a one-piece system (early type) or a later three or five piece system, and how
  many hangers does it have (the model has the gearbox clip and the rear pinch clamp only, as Haynes describes)?
  Does the tail pipe leave on the left as modelled? A photo from underneath of the downpipes and the gearbox clip
  would fix the downpipe run and the clip's bracket (the model hangs it under two gearbox side cover bolts).
- Exhaust manifold: the model gives it two outlets one behind the other, each with a two-stud downpipe flange
  and a sealing ring. Are yours side by side across the car instead, and how many studs hold the downpipes?
- Fuel tank: is it still the early strap-mounted tank with the six-screw gauge unit? Where is your filler cap on
  the body (the model brings the filler tube's elbow out to the right, toward the right-hand rear wing)?
- Fuel pump: is it still an SU HP (or has it been changed for an AUF or a modern pump), and is it on the heelboard
  just ahead of the right-hand spring, behind the right-hand battery carrier? Which way do its unions point?
- Fuel pipe: does your pipe run under the right-hand floor with the battery cable and come up into the engine bay
  on the right, crossing the bulkhead by the heater to the carburettors (as modelled), or another way?

- Brakes: is the car still on the original single-line system with the square-tank master cylinder (Lockheed
  GMC150) and the hydraulic stop lamp switch on the four-way connection, or has it been converted (dual line,
  servo, round-tank cylinder)?
- Where is the four-way connection on your car, and how do the front pipes cross the bulkhead? The model puts it
  low on the bulkhead below the pedal box with the left-hand pipe crossing above the bellhousing.
- Handbrake: the model puts the lever on the right of the tunnel with its pivot at the rear and the grip forward
  (so the operating lever's lower end pulls the cable forward), the cable over the right-hand axle tube to the
  compensator on the back of the differential. Is that how yours is laid out? A photo of the lever and of the
  compensator on the axle would fix it.
- Rear hose: where is the rear hose bracket on your body (the model hangs it ahead of the axle, 200 mm above the
  axle centre)?

- Rear hub nuts: Haynes lists one RH and one LH thread nut but not which side; the model follows mgaguru and
  BritishCarForum (left-hand thread on the left hub, so forward rotation tightens it), while the MGOC page text
  pairs them the other way. Which way does your left rear hub nut undo?
- Wire wheel spinners: cars to chassis GHN3-30850 (about February 1964) have 12 tpi hub extensions, later ones
  8 tpi. What is your car's chassis number, and are the hubs and spinners 12 tpi?
- Propeller shaft: is yours still the greasable type with a nipple on each joint (as modelled), or sealed joints?
- Axle ratio: the model is the standard 3.909 (43/11); has the axle been changed (some overdrive cars were
  fitted with 4.1 or 4.22)?
- Rear axle fittings: where are the handbrake balance lever, the brake pipe three-way union and the rebound
  strap brackets on your axle? A photo of the axle from behind and from underneath would fix them.

- Front axle line against the engine: the model puts the front wheel axis 76 mm behind the block's front face, so the
  sump's deep well sits over it and the front crossmember has to dip under the sump (its underside is then at the
  published 4.2 in ground clearance). On the real car I believe the crossmember passes just ahead of the sump. A tape
  measure from the front hub centre to the front of the block (or the crankshaft pulley) would settle it.
- Front suspension: is your car's camber still about 1 deg positive at the static unloaded height? (The model draws the
  stub axle level.) Are the front dampers the original lever-arm type, and are the wishbone pivots on rubber bushes?
- Steering column: where exactly does your column pass the crossmember's right tower and the engine? A photo looking
  down into the engine bay on the right, and one from underneath at the rack, would fix the pinion and joint positions.
- Steering wheel: is it the original 16 1/2 in banjo wheel with the black rim and the MG horn push?
- Rear springs: how many leaves do yours have (five plus a bottom plate as Haynes, or a later six-leaf), and where is the
  front hanger relative to the axle (the model has the eyes 22.5 in ahead of and 24 in behind the centre bolt)?
- Rear dampers and straps: are the rebound (check) straps still fitted, and which way does the damper link run (the model
  has it inboard of the spring, ahead of the tube)?
- Wheels: are your wire wheels painted (silver) or chrome, 60-spoke 4 1/2J, with two-eared spinners? Which tyres are
  fitted now (the model is the original 5.60-14 crossply)?
- Gearbox stay rod: is it fitted, and where does its front pin attach to your gearbox?

- Distributor cap orientation: which way do the plug leads leave the cap on your car?
- Fuel hose run between the float chambers: where does it go on your car?
- Clutch: is your clutch still the early diaphragm cover with the release plate and the graphite
  (carbon) release bearing, or has it been changed to a later cover with a ball/roller bearing?
- Clutch release lever: where does the lever leave the bellhousing on your car, and which way
  does the slave cylinder point? The model has the lever out of the right-hand wall at crank
  height, the slave cylinder lying fore and aft ahead of it, pushing the lever end rearward.
- Clutch hydraulics: where is the bracket where the metal pipe meets the flexible hose, and how
  long is the hose? The model puts the bracket on the right-hand chassis leg just behind the
  bellhousing flange.
- Bulkhead position: the model puts the engine side of the bulkhead 550 mm behind the front
  wheel centres (170 mm behind the engine rear plate). A tape measure from the front hub
  centre to the bulkhead would fix it.
- Gearbox side cover: the model puts it (and the selector rods and the reverse idler behind it) on the
  left-hand side of the casing. Is that right on your gearbox?
- Overdrive gearbox remote control: Haynes draws the overdrive remote control tower merged with the
  adaptor (Fig 6.4). The model has a short adaptor on the casing with the overdrive behind it and a
  separate remote housing bolted on top, reaching back to the gear lever, on a bracket on the overdrive.
  A photo of your gearbox from the left and from above would settle the shapes.
- Gear lever: where does your lever come out of the tunnel and how high is the knob? The model puts the
  lever ball on the centreline about 970 mm behind the front wheel centres, cranked back, with the knob
  about 680 mm above the road.
- Gearbox paint: the model paints the casing, adaptor and remote housing in the engine colour. Is your
  gearbox painted the same, black, or bare?
- Laygear: early three-bearing laygear with loose needle rollers assumed (18G); has yours been rebuilt
  with the later four-bearing type?
- Overdrive isolation switch: does your car have the switch on the remote housing (Fig 6.4 item 44)?
- Overdrive layout: the model puts the solenoid, its lever chamber and the speedometer drive on the right
  of the overdrive and the filter cover on the left (Haynes Figs 6.17, 6.18, Sec 2). Is that how yours
  sits, and which way does the speedometer cable leave (is there an angle drive on it)?
- Overdrive casings: modelled as bare aluminium alloy with a cast iron brake ring. Is yours bare, or
  painted with the gearbox?
- Gearbox rear mounting: the model hangs the gearbox on two rubber mountings on pads low on the sides of
  the overdrive main casing, on a crossmember bolted up to the floor about 930 mm behind the front wheel
  centres. A photo from underneath of the crossmember, the mountings and the stay rod would fix the
  position and shapes.


- Charging: the model has the 18ACR on the dynamo's mountings (pivot bolts through the water pump
  ear and the rear bracket, link below to a stud on the engine front). Which conversion brackets
  does your car use, and is the RB340 control box still in place (as a junction) or removed?
- Battery: which box holds the 12 V battery (the model uses the right-hand one), what size is it,
  and is there a battery master switch? Is the car converted to negative earth throughout (the
  18ACR needs it)?
- Starter: is it still the M418G inertia starter with the separate solenoid on the inner wing, or a
  later pre-engaged or high-torque starter? Where is the solenoid on your car?
- Coil: where is your coil mounted (the model has it on a bracket on the right of the block above
  the starter, Haynes' early position)? Is it still an HA12, and is there a ballast resistor?
- Engine bay units: please photograph the right and left inner wings and the bulkhead so the
  control box, fuse block, flasher, overdrive relay and vacuum switch can be put where they are.
- Horns: where are they mounted on your car (the model puts two behind the grille)?
- Facia: which switches are toggles and which pull switches on your facia, and which side are the
  speedometer and tachometer (the model has the speedometer outboard, on the right)? Is the
  tachometer the impulse type (electrical lead) or cable driven?
- Wipers: which way do the arms park (the model parks them toward the driver's side)?
- Lamps: are the front side/flasher lamps and rear lamps still the original early type, and are
  reversing lamps or any extra lamps fitted?

- Wiring (P10b), the 18ACR conversion: how was yours done? The model bypasses the RB340 (left in place) with a
  four-way snap connector joining the browns and a bullet joining the warning lamp's brown/yellow to the alternator's
  IND lead. Is the control box still there, removed, or replaced by a dummy junction box? Which wires go to the
  alternator plug (two browns on the + blades and brown/yellow on IND assumed)?
- Wiring: has the whole car been converted to negative earth (coil leads swapped, tachometer loop reversed)? The model
  assumes so, as the 18ACR needs.
- Wiring: does your car have the instrument voltage stabiliser (Haynes Fig 10.26 item 64) behind the facia? Haynes
  draws it on the up-to-1967 diagram; some early cars may not have one.
- Wiring: are the indicator warning lamps the two green arrows in the tachometer and speedometer (as Haynes Fig
  10.26 draws them, and as modelled), and the ignition and main beam warning lamps in the instruments? P10 had put
  three separate lamps on the facia.
- Wiring: is the harness the original braided type, or a replacement (PVC taped)? Any extra circuits (reversing
  lamps, fog/spot lamps, radio, electric fan, electronic ignition, a battery master switch)?
- Wiring: where are your dip switch and the horn push lead (the model has the foot switch on the toe board left of
  the clutch pedal, and the horn push lead through the column switch)?

## Differences seen in Oliver's scans (5 Nov 2026), for Oliver to decide

The scans (his photogrammetry of the whole car and of the engine bay; registration in `mgb/scan_layout.py`) were used
for the body's shape and the engine bay's panels. These bigger differences were seen and are not implemented, as he
asked; each needs his word (or a tape measure) before parts move:
- Engine and gearbox fore and aft: registered on the outer wings and headlamps, the scan's engine (its rocker cover)
  sits about 160 mm further back in the body than the model's. This agrees with the open question about the front axle
  line (the model's sump well over the axle, its crossmember dipping under the sump). Moving the engine, gearbox, propeller
  shaft and everything hung on them is a large change across phases P1-P6, P9, P10.
  P12 (5 Nov) measured it and stopped on a conflict: see "Engine set-back: open conflict" below.
- Cooling: the radiator carries a black plastic shroud with an electric fan (scan, photos 13, 28); the model has the
  engine-driven three-blade fan (now yellow, the colour of the scan's fan hub/pulley). An electric fan and shroud are
  not modelled.
- Heater: the Smiths heater box and its round blower stand on the bulkhead shelf in the middle (scan, photo 13). The
  shelf and the heater's opening are now in the body (body.structure.bulkhead-upper); the heater is not modelled.
- Screen washer bottle on the left of the shelf by the bulkhead (scan: about x -400, |y| 450, 650-820 above the road;
  photo 13): not modelled.
- Units on the right inner wing: the control box, fuse block, flasher and starter solenoid sit on the inner wing
  itself, 70-90 mm further outboard than P10 put them (|y| 430); the overdrive relay likewise on the left. They now hang
  on brackets standing off the sloping wall (body.structure.inner-wing-brackets); moving them out would move P10b's
  wires. The harness P-clips along the inner wings are on stand-off tabs for the same reason.
- Bulkhead fittings above the shelf: the main harness grommet, the speedometer, oil gauge and capillary grommets, the
  choke cable grommet and the overdrive vacuum switch were placed by P10/P3b on a flat bulkhead; on the car they pass
  through the stepped bulkhead's upper face. They are on plates standing on the shelf (body.structure.bulkhead-brackets)
  until they are moved.
- Front inner wings: on the car the wheel arch dome is closed down to the chassis leg, and so is the model's now; but
  the model's tyre at full lock (its king pin 132 mm inboard of the wheel's centre plane, P9) sweeps into the dome's
  lower part ahead of and behind the wheel, where the old flat valance had openings. P9's lock geometry (or the stop)
  should be checked against the car. Likewise P9's front springs, lever-arm dampers and the top of the crossmember
  stand up to 470 above the road at |y| 300-500, inboard of the real dome (the scan shows the dome covering them:
  nothing of the suspension is seen from above in his bay), so in the model they show through the closed dome.
- Radiator: in the scan it sits lower and further forward, right behind the grille with the fan shroud on it; the
  model's (P2) stands taller (header tank 761 above the road) further back.
- Ride height: his car sits 20-24 mm lower at the back than the model's standard height (scan: the rear rims 20 mm
  higher in the body, its road 24 mm higher at the rear and 6 mm at the front): tired or lowered rear springs, or a
  different tyre size. The model keeps the standard height and the body's rear fittings follow the body.
- Tyres: 165/80R14 radials (photo 03; the scan's tyre is about 10 mm larger in radius than the model's 5.60-14).

## Engine set-back: open conflict (P12, 5 Nov 2026)

Oliver chose to move the engine, gearbox and everything on them back to match his engine-bay scan. Measured: a trimmed
ICP of the scan's polished rocker cover top onto our cover (engine scan as registered on the wings and headlamps) puts
his engine 156.6 mm further back in the body (y -4.7, z +13.6 mm, residual 1.6 mm); FRONT_AXLE_X would become 307.
The move was not applied because the propeller shaft cannot fit: the gearbox (overdrive) flange to pinion flange
distance falls from 788.5 to 631.5 mm, an installed shaft of 634 mm (24.97 in) against the Haynes overdrive shaft's
fully compressed 30 3/16 in (766.8 mm) and the MGOC/Rimmer AHH7487 31 1/8 in (every MGB shaft listed is 30-32 in). The
pinion flange (D, 354.1 mm ahead of the axle centre, fitted to the shaft) cannot come back far enough: at the carrier
nose (about 290) the shaft would still be 69 mm too long fully compressed. So one of these is wrong and needs checking
before the engine moves: the gearbox and overdrive length in the model (engine rear plate to the overdrive flange
793 mm, D from the Haynes figures), the banjo axle's nose and pinion flange station, or the engine scan's registration
(supported by the radiator and headlamps lining up with the whole-car scan). Other numbers for the move as asked: fan
to radiator core 185 mm (now 28); bulkhead 17 mm behind the engine rear plate
(now 174); gear lever knob 271 mm behind the facia (now 114); the front crossmember's engine mounting pads would have
to reach about 50 mm behind the beam's rear face to stay under the engine brackets.

Done in P12 so the move stays a small change once decided: the layout modules write body, chassis and running-gear
fore-aft positions as body stations through `car_layout.bx()` (front wheel axis at station 150; a no-op today, checked
by diffing every layout datum and the body surface). Still to do for the move: the part modules' own hard-coded
stations (parts/body, parts/chassis, parts/brakes, parts/fuel, wiring), the bridging runs (hoses, fuel pipe end,
exhaust interpipe crossing ahead of the left battery carrier, clutch hose, cables, harness), the crossmember's
engine mounting pads (they should stay with the engine), and the scan registrations (BODY_TRANS and ENGINE_TRANS x
+157 with it).

## From Oliver's photos of his car (2 Nov 2026), mechanical items left for later

The photos (scratchpad refs/oliver-car, 28 images) show differences from the mechanical model. Oliver asked for the
body only for now; these are to do later:
- Rocker cover: polished, finned cast-alloy cover with a raised octagon emblem (photos 07, 12, 13, 28), not the
  pressed steel cover in `engine.head`.
- Cooling: an electric radiator fan in a plastic shroud on the radiator (photos 13, 28), not the engine-driven fan.
- Tyres: 165/80 R14 radials (photo 03: 165/80R14 85T), not 5.60-14 crossplies.
- Steering wheel: black rim, three spokes of three chrome wires each, octagon horn push (photos 01, 04, 17).
- Engine bay: Smiths heater blower on the bulkhead, separate screen washer bottle on the left inner wing, black
  box-type air cleaners on the carbs (photos 13, 28).
- Earth polarity: a sticker on the front slam panel reads "...wired POSITIVE EARTH" (photo 13). The wiring model
  assumes negative earth for the 18ACR alternator - this needs Oliver's confirmation (question below).

Question for Oliver: the slam panel sticker says positive earth. Is the car still positive earth (and is it really
an 18ACR alternator, or a dynamo?), or was the sticker left on after a negative-earth conversion?
