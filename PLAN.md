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
| P5 Gearbox and overdrive, rear mounting | Ch 6 | |
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
- Gearbox bellhousing (P5): build it on `mgb/gearbox_layout.py` - front face on the rear plate's
  bellhousing holes, the two lever pivot lugs above and below the lever boss, the wall opening
  at `LEVER_PORT` under the dust cover, and the slave cylinder pad (rear face at `SLAVE_PAD_X`,
  34 mm bore, two 5/16 UNF tapped holes 30 mm above and below the axis). The first motion shaft passes through
  the release plate, the bearing and the driven plate hub (23 splines).
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
