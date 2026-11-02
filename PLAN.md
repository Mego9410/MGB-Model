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
| P8 Brakes | Ch 9 | |
| P9 Suspension, steering, wheels and tyres; engine mountings | Ch 11 | done |
| P10 Electrical: battery, 18ACR alternator, starter, coil, lamps, wipers, instruments, loom | Ch 10 | |
| P11 Body shell, panels, trim, fittings; exhaust; fuel tank, pump and pipe | Ch 12, Ch 3 | |

## Carried over

- Brakes (P8) on the rear axle (`mgb/rear_axle_layout.py`, axle frame AF at `car_layout.REAR_AXLE_X`,
  `WHEEL_Z`): each backplate seats on the case flange's outer face at |y| `BACKPLATE_FACE_Y` 562 mm, four
  3/8 in holes on a 108 mm pitch circle at 45 deg (`BACKPLATE_BOLT_*`); the drum's face seats on the hub
  extension flange at |y| `DRUM_FACE_Y` 615 over four 1/2 in UNF studs on a 4 1/2 in pitch circle at 45 deg
  (`STUD_*`); its centre hole must clear the extension collar (72 mm across); the four drum nuts (MGOC lists a
  1/2 UNF nyloc, GHF225) come with the drum (Ch 8 Sec 4 para 5). Shoes and wheel cylinder between |y| 562 and
  615, drum 10 in (P8 to confirm). Brake pipe three-way union bolts to the tab on top of the left-hand neck
  (`PIPE_BRACKET`, x 10, y 150, face z 52 in AF); the handbrake balance lever pivots on the pin on the rear of
  the bowl (`BALANCE_PIVOT`, y 60, z -78, pointing rearward, split pin hole); both positions derived.
- Body mountings for the suspension and steering (P11), all car frame, per side (P9 datums):
  - Front crossmember: two support bolts each side up through the front chassis legs
    (`front_suspension_layout.BODY_BOLTS`, |y| 432, x FX-80 and FX+84, leg underside `BODY_FACE_Z` z -226 on the upper
    rubber pads, leg top `BODY_LEG_TOP_Z` -176 where the nuts and washers sit). The damper arms sweep over the legs
    between |y| 305 and 499 at z -110 to -173 (more on rebound): the inner wing valances need openings there. The
    column runs through a tube in the RHD crossmember's right tower (`steering_layout.CROSSMEMBER_TUBE_R`).
  - Steering column top: the clamp (Fig 11.6 item 59) on a body bracket under the facia at
    `steering_layout.COLUMN_TOP_CLAMP` (x -780, y -311, z 21) with packing washers; the bottom bracket, blanking plate
    and draught excluder on the toe board at `COLUMN_TOE_PLATE` (x -440, y -280, z -92): the toe board needs a hole for
    the 1 1/2 in tube there. The column passes the pedal box area beside the brake and clutch pedals (P8 to check).
  - Rear springs: front hanger plates either side of the eye on the eyebolt axis `rear_suspension_layout.FRONT_HANGER`
    (|y| 420, x -1589.9, z -299.3, bolt along y); the rear shackle's upper pin through a body bracket at
    `SHACKLE_BRACKET` (x -2785, z -208); dampers bolted by two bolts along y to the side member's inner face at
    `DAMPER_MOUNT` (|y| 436); rebound strap bolts at `REBOUND_BOLT` (x -2246.4, |y| 500, z -132.8); bump rubber strike
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
  were added to the block's left wall, P2).
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
- 18ACR alternator and the Lucas HA12 coil: P10.
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
  there. The stay rod went in with P9 (`gearbox.stay-rod`).
- Speedometer cable (P10/P11): P5b built only the end: the angle drive (MGOC 120694) on the speedometer
  housing on the right of the overdrive rear casing, output turned forward and down at 45 deg, its
  knurled nut and a 70 mm stub. The run to the speedometer is P10/P11 (Ch 1 Sec 6 para 30).
- Overdrive wiring (P10): the solenoid lead leaves the back of the solenoid (right side, car x about
  -895); the isolation switch is on the remote housing (P5a); the relay, the vacuum switch (left bulkhead,
  MGOC) and the dash switch with the loom (Ch 6 Sec 16, Fig 6.19).
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
- Starter motor (P10): its pinion runs in the pocket on the right of the bellhousing behind the rear
  plate's starter aperture.
- Bulkhead and tunnel (P11): the bellhousing's back wall is at the bulkhead line (`car_layout.BULKHEAD_X`),
  so the tunnel starts there and must clear the casing (104 mm left and 84 mm right of the mainshaft,
  92 mm above it), the adaptor and the remote housing.
- Known P5a approximations: the 2nd gear thrust washer (Fig 6.3 item 97) is drawn ahead of the 1st/2nd
  synchroniser but sits behind it in the model; the selector mechanism layout (rods side by side high on
  the left, the selector lever shaft above them in the remote housing) is derived; gear teeth are
  phased to mesh in neutral (first gear and the idler's 13 teeth are out of mesh).
- Pedal box, its cover over the master cylinders, the common pedal pivot bolt, the brake
  pedal and the bulkhead (P8/P11): the clutch master cylinder flange face is at
  `clutch_layout.PEDAL_BOX_FACE_X`; `car_layout.BULKHEAD_X` is derived.
- Hose bracket on the right-hand chassis leg (`clutch_layout.HOSE_BRACKET`) and the two pipe
  clip screws: with the body (P11).

## Questions for Oliver (asked at the end of the overnight run)

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

