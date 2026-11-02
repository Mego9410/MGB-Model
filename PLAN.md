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
| P4 Clutch | Ch 5 | done |
| P5a Gearbox (three-synchro, overdrive type), remote control | Ch 6 | done |
| P5b Overdrive (Laycock type D), speedometer drive, rear mounting | Ch 6, Ch 1 | done |
| P6 Propeller shaft | Ch 7 | done |
| P7 Rear axle | Ch 8 | done |
| P8 Brakes | Ch 9 | done |
| P9 Suspension, steering, wheels and tyres; engine mountings | Ch 11 | |
| P10 Electrical: battery, 18ACR alternator, starter, coil, lamps, wipers, instruments, loom | Ch 10 | done |
| P11 Body shell, panels, trim, fittings; exhaust; fuel tank, pump and pipe | Ch 12, Ch 3 | |

## Carried over

- Front brakes (P8) for P9, `mgb/front_suspension_layout.py` (left-hand front hub frame FH: origin on the wheel
  axis at the car centre line, car axes, |y| outward; static camber and king pin inclination are P9's to add by
  turning this frame): the disc's centre plate seats on the inboard face of the hub flange at |y| `DISC_FACE_Y` 588,
  flange `HUB_FLANGE_Y` 588-598, `HUB_FLANGE_R` 62, four 3/8 UNF bolts (heads in the disc's hat, spring washers and
  nuts on the flange's outer face) on a 100 mm circle at 45 deg (`DISC_BOLT_*`); the hub must pass through the
  disc's 82 mm centre hole (`DISC_BORE_R` 41) inside the hat (`HAT_R` 60). The caliper hangs straight behind the
  axle (`CALIPER_ANGLE` 270): its two lugs face the swivel axle's caliper flange at |y| `CALIPER_MOUNT_FACE_Y` 512,
  the flange `SWIVEL_CALIPER_FLANGE_T` 12 thick (|y| 500-512) with two 7/16 UNF clearance holes at
  `CALIPER_BOLTS` (64 mm behind the axis, 40 mm above and below it), bolt heads and the tab washer on its inboard
  face. The stone guard's centre (|y| `SHIELD_FACE_Y` 532) sits on three pads on the swivel axle with tapped 5/16
  UNF holes at `SHIELD_SCREWS` (58 mm radius, 0/100/200 deg from up toward the front). The front hose bracket is
  at `HOSE_BRACKET` (x 80, |y| 470, z -132.5, on the wing valance, P11): P9 to check the hose at full lock and
  bump, and the front pipes' run along the chassis legs (`brake_layout.CHASSIS_LEG_Y`, `LEG_PIPE_Z`) and up to the
  bracket against the crossmember, springs and dampers. The rear brakes cover P7's backplate face, drum face and
  studs as P7 left them.
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
- Rear springs, dampers and straps (P9): spring seats welded under the tubes, flat face at z `SEAT_FACE_Z`
  (48 mm below the axle centre), centred at |y| `SPRING_Y` 420, 100 mm fore and aft, 11 mm hole for the
  locating plate's peg (Fig 11.4 items 18-19); U-bolt legs (`UBOLT_LEGS`) 45 mm fore and aft of the tube, 30 mm
  either side of the spring; the bump rubber pedestal saddles the tube top (`PEDESTAL_SEAT`); the damper link
  goes to bracket 20 under the spring (Fig 11.4), not to the axle; rebound strap eyes on the spindles at
  (x -22, |y| 500, z -88) (`REBOUND_EYE`), 3/8 UNF, the spindle nut already fitted outboard at |y| 509 with room
  for the strap, plain and spring washers. Spring centre line, seat height and bracket positions are derived:
  P9 should check them against the body's spring hangers.
- Wheels (P9): the wire wheel's inner cone seats on the hub extension collar (|y| 615-640, 66 to 55 mm across),
  42 mm series splines |y| 640-712, spinner thread |y| 714-744, 12 tpi, right-hand thread on the left hub and
  left-hand on the right (`SPINNER_HAND`); wheel centre plane at the track (|y| 625.5).
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

- Exhaust system (Ch 3 Sec 46, one-piece welded on early cars): with the body/floor.
- Fuel pump, tank and the rigid pipe to `fuel.pipes.feed-union`: with the body.
- Engine mountings (Fig 1.29): with the front crossmember (P9).
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
  there. The engine stay rod, its bracket, buffers, distance tube, bush and pin (Fig 1.29 items 20-32;
  MGOC 1G9384 3-synchro pin) go with P9: the bracket bolts to the two holes in the crossmember's dip,
  under the overdrive valves (Ch 6 Sec 14 para 1), the rod's front end to the gearbox.
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
  |y| `BATTERY_BOX_Y`, floor underside `TONNEAU_FLOOR_Z`, 186 x 236 x 226 mm inside, 22 mm flange with
  four bolt holes; P11 adds the floor, the access panel with quick-release screws (photo 2.1), the
  earth bolt and the cable grommet through the box's front wall.
- Fuel tank sender (Fig 10.26 item 35) and its lead: with the tank (P11).
- Known P10 approximations: unit positions in the engine bay, the facia layout and every harness
  route are derived (no photographs of a 1963 engine bay or facia could be opened from the build
  machine); the 18ACR, M418G, DR3A and the instruments are modelled from the Haynes figures and
  common pattern sizes, not measured; lens optics, dial figures and individual wires are not drawn;
  the thermal transmitter sits on the head's right face, which has no boss for it in P1 yet.

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

## Questions for Oliver (asked at the end of the overnight run)

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
