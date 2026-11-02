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
| P6 Propeller shaft | Ch 7 | |
| P7 Rear axle | Ch 8 | |
| P8 Brakes | Ch 9 | |
| P9 Suspension, steering, wheels and tyres; engine mountings | Ch 11 | |
| P10 Electrical: battery, 18ACR alternator, starter, coil, lamps, wipers, instruments, loom | Ch 10 | |
| P11 Body shell, panels, trim, fittings; exhaust; fuel tank, pump and pipe | Ch 12, Ch 3 | |

## Carried over

- Exhaust system (Ch 3 Sec 46, one-piece welded on early cars): with the body/floor.
- Fuel pump, tank and the rigid pipe to `fuel.pipes.feed-union`: with the body.
- Engine mountings (Fig 1.29): with the front crossmember (P9).
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
  there. The engine stay rod, its bracket, buffers, distance tube, bush and pin (Fig 1.29 items 20-32;
  MGOC 1G9384 3-synchro pin) go with P9: the bracket bolts to the two holes in the crossmember's dip,
  under the overdrive valves (Ch 6 Sec 14 para 1), the rod's front end to the gearbox.
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

