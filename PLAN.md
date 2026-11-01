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
| P4 Clutch | Ch 5 | |
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

## Questions for Oliver (asked at the end of the overnight run)

- Distributor cap orientation: which way do the plug leads leave the cap on your car?
- Fuel hose run between the float chambers: where does it go on your car?
