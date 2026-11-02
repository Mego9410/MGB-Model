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
| P5b Overdrive (Laycock type D), speedometer drive, rear mounting | Ch 6 | |
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
- Overdrive (P5b) bolts to the datums in `mgb/gearbox_layout.py`: the adaptor's rear face `OD_FACE_X`
  (gasket 37H1901 already fitted by P5a), eight 1/4 in UNF studs on `OD_STUD_R` at `OD_STUD_ANGLES`
  (index `OD_STUD_LONG` is the long one; P5b supplies the nuts and washers), the register `OD_SPIGOT_R`,
  the oil way `OD_OIL_PORT` at the bottom of the face. The mainshaft tail is built to `MS_CAM_D` (1/2 in
  Woodruff keyway and circlip groove for the pump cam: cam, key and circlip are P5b), `MS_SPLINE_D` /
  `MS_SPLINE` (clutch and planet carrier) and `MS_PILOT_D` / `MS_PILOT_R` (needle bearing in the output
  shaft); the shaft ends at `MS_END_X`. Keep the overdrive under `REMOTE_BOTTOM_UP` below the remote
  housing, and give it two bosses for the remote support bracket screws at `REMOTE_BRACKET_D`,
  `REMOTE_BRACKET_UP`, `REMOTE_BRACKET_HOLES`. The speedometer drive is in the overdrive rear casing on
  these cars (Fig 6.13 items 78, 88, 89), so it comes with P5b.
- Gearbox rear mounting ("mounting to gearbox case 15-20 lbf ft", Ch 6 specs) and the rear crossmember:
  with P5b and the chassis (P9).
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

