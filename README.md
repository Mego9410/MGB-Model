# MGB-Model

A part-by-part digital model of a 1963 MGB roadster (RHD, 18G engine, overdrive,
Lucas 18ACR alternator, negative earth, wire wheels), built to the dimensions
published in the Haynes MGB workshop manual.

Every part is a parametric CAD script driven by a spec file. The build measures
each solid against its spec and fails if a published dimension is out of range.

## Layout

| Path | What it holds |
| --- | --- |
| `specs/` | One YAML file per part: Haynes reference, dimensions, and a source label on every figure |
| `parts/` | One build123d script per part, built from its spec, with probes that measure the result |
| `assemblies/` | Which parts go in each assembly and where |
| `mgb/` | Spec loading and checks, probes, fastener library, export, registry |
| `viewer/` | The web viewer (single page, three.js) |
| `tests/` | Check tests (`pytest`) and the viewer smoke test (Playwright) |
| `build/` | Generated, not committed: STEP files, GLB, the viewer bundle |
| `site/` | Generated and committed: the static site Vercel serves. Rebuild with `python build.py` before pushing |

## Source labels

| Label | Source |
| --- | --- |
| H | Haynes MGB owners workshop manual, with page |
| F | Factory BMC manual or parts catalogue |
| S | Supplier data or a published standard, with reference |
| M | Measured on the car |
| D | Derived, with the method stated |

Where Haynes prints an inch figure and a metric figure that disagree, the inch
figure governs and the spec records the misprint (`printed_mm`, `erratum: true`).

## Build

```bash
pip install -r requirements-dev.txt
npm install
python build.py            # build, check, export to build/
python build.py --check    # checks only
python -m pytest tests -q
node tests/smoke.mjs       # viewer smoke test (needs playwright)
```

## Deploy

Vercel serves `site/` as a static site (see `vercel.json`); it runs no Python and no build.
The CAD build needs OpenCascade, so it runs locally and its output is committed.

## Status

- P0 (foundations) complete: pipeline, checks, fastener library, viewer shell.
- P1 (cylinder head) signed off: every Haynes Fig 1.6 legend item plus the
  Fig 1.9 valve gear, laid out from Fig 1.5 and exploded in the Haynes removal order.
- P2a (block and crank train) built: Fig 1.8 block with its full exterior form,
  crankshaft, main and big-end bearings, pistons and rods, camshaft, tappets,
  pushrods, tappet covers, front plate (Fig 1.8 outline) and the rear end plate
  with its early-type oil seal retaining plate (Sec 22/53).

- P2b built: timing gear and cover (Fig 1.25, 1.11), lubrication (Fig 1.16, 1.1,
  1.20: sump, pump, strainer, early filter, oil pipe, relief valve, dipstick), flywheel
  and 120-tooth ring gear, inlet and exhaust manifolds. The camshaft height now comes
  from the 52-pitch timing chain on 20/40-tooth wheels.

- P2c built: water pump, three-blade fan, pulley, fan belt, radiator with cap and drain
  tap, top and bottom hoses (Haynes Ch 2, Figs 2.4 and 2.6).

- P3 (in progress): twin SU HS4 carburettors and air cleaners (Haynes Ch 3, Figs 3.1,
  3.10-3.12); Lucas 25D4 distributor with its housing and driveshaft, side-entry cap, HT
  leads and plug caps (Ch 4 Fig 4.3; Ch 1 Sec 16 and 63); the rocker cover breather pipe to
  the front air cleaner and the float chamber fuel hoses (Ch 3 Sec 3 and 18).

- P4 (clutch) built: Borg & Beck 8 in diaphragm spring clutch, early type with the release
  plate and graphite bearing (Haynes Ch 5, Figs 5.1 and 5.2): cover with its drive straps and
  fulcrum rivets, diaphragm, release plate, pressure plate, driven plate (hub, centre, six
  damper springs, facings) and fixings; the release bearing, withdrawal lever and its pivot
  on the bellhousing datums of `mgb/gearbox_layout.py`; the master cylinder on the pedal box,
  RHD pipe, hose and slave cylinder with every Fig 5.3 item; and the clutch pedal.

- P5a (gearbox) built: early three-synchro gearbox for an overdrive car (Haynes Ch 6, Figs 6.3, 6.4
  and 6.6): the casing with its integral bellhousing on the engine rear plate, front cover with the
  clutch lever pivot lugs, side cover, plugs and fixings; first motion shaft, mainshaft (overdrive
  type tail) with helical second, third and constant mesh gears, straight-cut first gear, both
  synchronisers and baulk rings, bushes, the third gear locking washer and peg; laygear on loose
  needle rollers; reverse idler; selector rods, forks, detent block, selectors, interlock plate and
  front selector lever; the overdrive adaptor ("gearbox extension") with the overdrive studs; and the
  remote control housing with the selector shaft, gear lever, knob, plungers, detents, isolation
  switch, dipstick and support bracket. Tooth counts give the published ratios.

- P5b (overdrive and rear mounting) built: Laycock de Normanville type D overdrive (Haynes Ch 6, Figs
  6.10-6.18): main casing with its sump, filter cover, plugs, operating cylinders, valve bosses and
  lever chamber, the brake ring and the rear casing with the remote bracket bosses; the clutch bolts,
  springs, retainer plate, thrust bearing and housing, the cone clutch, sun wheel, planet carrier with
  three timed helical planets (0.802), the uni-directional roller clutch, the annulus and output shaft on
  its two bearings with the speedometer worm, spacer and shim, the rear seal and the coupling flange,
  washer, castellated nut and split pin; the pump cam, pump, non-return, relief and operating valves,
  filter, the operating pistons and bridge pieces, solenoid, operating lever and cover; the speedometer
  drive (pinion, housing, seal, locking screw), the angle drive and the cable end; and the gearbox rear
  mounting (Ch 1 Fig 1.29): two rubber mountings on the overdrive and the removable crossmember. Shared
  datums: `mgb/overdrive_layout.py` (overdrive stations, P6 flange datums), `mgb/chassis_layout.py`
  (crossmember and its body bolts for P9/P11).

- P6 (propeller shaft) built: Hardy Spicer tubular shaft, overdrive length, greasable joints (Haynes Ch 7, Figs
  7.1, 7.4, 7.5): two flange yokes, two spiders with their lubricators, eight needle bearing cups, circlips,
  cork gaskets and retainers, the sleeve yoke with its lubricator, dust cap, steel and cork washers, the shaft
  (splined stub, swaged cone, tube, welded rear yoke) with balance weights, and the eight flange bolts, spring
  washers and self-locking nuts. It runs from the overdrive flange to the axle pinion flange at the supplier
  length 31 1/8 in, inside the Haynes travel, 4.3 deg down toward the rear (`mgb/propshaft_layout.py`).

- P7 (rear axle) built: early three-quarter floating banjo axle, 3.909 (43/11), wire wheels (Haynes Ch 8, Fig
  8.1): the welded banjo case with its seam, ring and carrier studs, forged ends (backplate flanges, seal
  tracks, bearing journals, handed nut threads with keyways), spring seats, rebound strap brackets and spindles,
  breather, filler/level and drain plugs; the carrier with its saddles, caps, studs, nuts and washers and gasket;
  the hypoid pinion on two taper roller bearings with spacer, shim, thrust washer, seal, dust cover, flange,
  spring washer and nut; the differential (cage, 43-tooth crown wheel, bolts and tab washers, side gears,
  pinions on their shaft and peg, thrust washers, ball bearings, packing washers); axleshafts and the wire wheel
  hubs (hub, studs, double row bearing, seal, O-ring, locking washer, RH and LH bearing nuts, the RH and LH
  12 tpi hub extensions with handed spinner threads, Welch plugs, screws). Datums for brakes (P8) and springs,
  dampers, straps and wheels (P9) are in `mgb/rear_axle_layout.py`.

- P8 (brakes) built: Lockheed single-line system, early RHD car (Haynes Ch 9, Figs 9.1, 9.6-9.11, 9.16). Front:
  10.75 in hat discs with their bolts, two-piston calipers (mounting and rim halves with bridge bolts and the fluid
  transfer seal, 54 mm pistons, fluid seals, dust seals and retainers, pads with anti-squeal shims, retaining clip
  and split pins, bleed screw, plug), caliper bolts and tab washer, stone guards, flexible hoses with their brackets,
  locking plates, nuts and washers, on the hub datums in `mgb/front_suspension_layout.py` (hub and swivel axle P9).
  Rear: 10 x 1.75 in drums on P7's hub extension flanges with the four nyloc nuts; pressed backplates with shoe
  platforms and ribs, the wheel cylinder (0.800 in) with pistons, seals, boots, E-clip, bleed screw and the
  handbrake lever and boot; leading and trailing shoes with bonded linings, pull-off springs, steady pins, springs
  and cups; the square-headed adjuster with its tappets and wedge. Master cylinder: GMC150 square-tank cylinder
  (3/4 in) with every Fig 9.11 item on the pedal box beside the clutch cylinder; the pedal box with its cover and
  fixings; the brake pedal and the common pivot bolt, spacers and washers. Pipes: master cylinder to the four-way
  connection with its hydraulic stop lamp switch, pipes to both front hoses and back under the floor to the rear
  hose, the three-way connection on P7's tab and the two axle pipes. Handbrake (early layout, Fig 9.10): lever,
  ratchet, pawl and rod, operating lever, trunnion, brass adjusting nut and spring, the cable, the scissor
  compensator on P7's pin, rods, clevis pins and clips. Datums: `mgb/brake_layout.py`.

Next: P9 (suspension, steering, wheels, engine mountings) on `mgb/front_suspension_layout.py` and the axle datums;
P10 electrical; P11 the body. The exhaust: the early cars have a one-piece welded system (Ch 3 Sec 46) that hangs
from the body, so it goes in with the floor and the gearbox mountings, along with the fuel
pump, tank and the rigid pipe from the pump to the feed union. The working standard is in `CLAUDE.md`.
