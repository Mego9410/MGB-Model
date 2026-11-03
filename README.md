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

- P3b (throttle and choke controls) built, early RHD car (Haynes Ch 3 Figs 3.10 and 3.13, photo 17.1(b), Secs 21 and
  45; factory parts list plates 108-G2 and 108-G4): `fuel.throttle` - the pendant accelerator pedal (AHC135) on its
  welded bracket with the distance tube, pivot bolt, washer and nyloc nut, the rubber pad, the RHD pedal stop on the toe
  board with its stop screw and locknut, the cable guide and gasket on the bulkhead, the cable (outer with ferrules,
  inner with its nipple and split pin at the pedal) P-clipped to the pedal box cover and run behind the head to an
  abutment bracket on the heat shield, the swivel pin, washers and anti-rattle washer on the throttle shaft lever, the
  interconnecting shaft in its two folded clamps, both throttle levers with their nuts, tab washers and adjusting
  screws, and the three return springs to the heat shield's lip; `fuel.choke` - the round "C" knob on the centre panel
  (Oliver's photo 16), the control's bezel and bush with its nut behind the facia, the cable through its bulkhead
  grommet to the abutment on the bracket, the trunnion, the cable lever and the interconnecting rod with its two
  lever-and-pin clamps, and each instrument's jet lever and link on its pivot bolt, tube, washers and spring, screwed to
  the jet head. Datums: `mgb/throttle_layout.py`.

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

- P10 (electrical) built: Lucas 18ACR alternator (Oliver's conversion) on the dynamo mountings - drive end
  and slip ring end brackets, stator, rotor, fan, 2 3/4 in pulley, end cover, terminal plug, pivot bolts
  through the water pump ear and the rear bracket, adjusting link and stud (Haynes Ch 10 Fig 10.3, Ch 2
  Figs 2.1, 2.6); Lucas M418G inertia starter (Fig 10.4: drive end bracket, yoke, cover band, commutator
  end bracket, armature, 9-tooth pinion, drive and main spring, terminal post) on two bolts into the
  bellhousing, the remote solenoid, starter cable and earth strap; Lucas HA12 coil on its bracket with
  the king lead and low tension lead; the RB340 control box, 4FJ fuse block, flasher, overdrive relay
  and vacuum switch, two horns; both battery carriers, a single 12 V battery (conversion), clamp,
  J-bolts and cables; 7 in headlamps (bowl, light unit, rim, beam setting screws, dust excluder), side
  and flasher lamps, rear lamps and number plate lamps; the DR3A wiper motor, rack casings, wheelboxes,
  spindles, arms and blades (Fig 10.17); speedometer, tachometer, dual and fuel gauges, warning lamps
  and switches (Fig 10.9), the speedometer cable from the overdrive, the oil gauge pipe and the
  temperature capillary; and the wiring loom as sleeved bundles with branches. Body datums for P11
  are in `mgb/body_layout.py`; engine-bay electrical datums in `mgb/electrical_layout.py`.

- P10b (wiring harness) built, wire by wire: every cable of the harness from Haynes Fig 10.26 (wiring diagram up to
  1967) and Fig 6.19 (overdrive), each its own part in its Lucas colour (main colour and tracer), size, circuit and
  the two terminals it joins (the viewer's wire card links to both, and every component lists its wires). Wires run
  side by side in bundles along the harness routes (engine bay, facia, rear harness, overdrive leads), break out to
  their units and end in Lucar, bullet or ring terminals on the real terminal positions; the soldered joints, snap
  connectors, earth points, bulkhead grommet and braided sleeving are parts too. Grouped by circuit
  (`electrical.wiring-charging`, `-starting`, `-lighting`, `-indicators`, `-instruments`, `-wipers-horn`,
  `-overdrive`, `-earths`) so one circuit can be isolated and traced. Adapted for the 18ACR alternator (control box
  bypassed) and the negative-earth single 12 V battery. Terminals: `mgb/electrical_layout.py terminals()`; routes,
  joints and bundles: `mgb/wiring_layout.py`.

- P11a (exhaust and fuel supply) built: the early one-piece welded exhaust (Haynes Ch 3 Sec 46, photos 6.14 and
  46.2): twin downpipes with their flanges and sealing rings on the manifold's two outlets (the manifold now has
  two), the Y-piece, the flattened oval centre silencer, the interpipe under the axle and the left handbrake rod,
  the cylindrical rear silencer and the 45 degree tail pipe; the studs, washers and brass nuts; the 3-synchro
  gearbox bracket and strap with the front support bolt; the rear pinch clamp mounting with its rubber block and
  body bracket. The early strap-mounted 10 gallon tank (Fig 3.9): the tank with its seams, X pressing, filler stub,
  gauge ring, outlet and drain boss; drain plug and washer; straps, packing strips, rear hangers, clevis pins,
  washers, split pins, strap bolts, washers and nyloc nuts; filler seal, hose, clips, filler tube and lift-off cap;
  the early gauge unit, its gasket and six screws. The SU HP pump (Fig 3.2): body, gaskets, sandwich plate, coil
  housing with its two lugs, end cover with terminal and vent valve, sealing band, outlet and inlet connections,
  filter plug, six body screws, on a bracket and rubber mountings on the heelboard ahead of the right spring
  (Sec 5). The pipes: braided hoses at the tank and the pump, the tank-to-pump pipe over the axle, the main pipe
  under the right-hand floor and up and across the bulkhead to P3's feed union, with union nuts and P-clips. Body
  datums for P11b: `mgb/underbody_layout.py`.

- P9 (suspension, steering, wheels and tyres; engine mountings) built (Haynes Ch 11 Figs 11.1-11.8; Ch 1 Fig 1.29):
  the front crossmember with its rubber body mountings, spring towers, engine and rack brackets (and the RHD column
  tube); lever-arm dampers whose arms are the upper wishbones, top trunnions and fulcrum pins, swivel pins with their dust
  excluders, cork rings, bushes and thrust washers, LH and RH swivel axles with the stub axles, P8's caliper flange and
  dust cover pads; pressed lower wishbone arms on their pivots and bushes, coil springs and pans, steering levers; the
  wire wheel front hubs (12 tpi, handed) with their taper bearings, spacer, shim, seal, collar, nut and grease retainer;
  the rear leaf springs (five leaves and a bottom plate, clips, centre bolt), locating plates and pads, U-bolts, bump
  rubber pedestals, damper brackets, eyebolts and bushes, shackles, rear lever dampers and links, rebound straps; the
  rack and pinion (RHD) with its brackets and shims, tie-rods, ball housings, gaiters and outer ball joints, the column
  with its universal joint, bearings, clamp and toe board fittings, the 16 1/2 in banjo steering wheel and horn push;
  four 60-spoke 4 1/2J x 14 wire wheels with 5.60-14 crossply tyres, valves and handed two-eared spinners; the front
  engine mountings (brackets, rubbers, packing plates) and the gearbox stay rod. Datums: `mgb/front_suspension_layout.py`
  (with P8's hub and brake datums), `mgb/rear_suspension_layout.py`, `mgb/steering_layout.py`, `mgb/wheel_layout.py`,
  `mgb/engine_mount_layout.py`, `mgb/chassis_layout.py` (stay rod); body mounting datums for P11 are listed in PLAN.md.

- P11b (body) built to Oliver's car (his 28 photos and a near-orthographic side view of a sister car, scaled on the
  wheelbase; Haynes Ch 12, Figs 12.1, 12.7, 12.12, 12.13, 12.15, 12.19 for the construction): the welded shell's
  structure (floor, tunnel, toe boards, bulkhead with the pedal box aperture and grommets, scuttle inner and facia
  rail, front legs on P9's crossmember mountings, inner wings and wheel houses, front apron and radiator duct, lock
  platform, three-member sills with jacking sockets, hinge and shut pillars, heelboard with the fuel pump's captive
  nuts, tonneau floor over P10's battery carriers with the access covers, rear bulkhead, rear wheel houses, boot floor
  with P11a's tank tabs and exhaust bracket nuts, rear rails with P9's spring hangers, shackle brackets, damper
  doublers, strap brackets and bump strike plates, P10b's wiring grommets and clips); the outer panels (bolt-on front
  wings with the hooded headlamp nacelles, grille panel, front valance, the bonnet with its swage between the proud
  wing crowns, scuttle, doors with frames, hinges, wind-up glass, quarter-lights, pull handles, locks, the driver's
  mirror, outer sills, rear wings ending in the raked lamp plinths, rear deck, boot lid, rear panel with the filler
  cap); the windscreen; chrome bumpers with rubber-faced overriders, the slatted grille with its plain shield badge,
  the scuttle intake, side strips, plain badges and blank plates; the interior (black crinkle facia round P10's
  instruments and switches with the plaque, heater knobs, binnacle, crash roll and glovebox; the console with its
  speaker grille; black seats with red piping; carpets, door cards, cappings); the hood erected; the spare wire wheel
  on the boot carpet. The outer skin is one B-spline face fitted to an implicit body (`mgb/body_shell_layout.py`,
  `mgb/body_shell.py`, cached in `.cache/body/`).