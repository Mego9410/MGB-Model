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

Next: P5, the gearbox and overdrive, with the bellhousing built on the datums in
`mgb/gearbox_layout.py`. The exhaust: the early cars have a one-piece welded system (Ch 3 Sec 46) that hangs
from the body, so it goes in with the floor and the gearbox mountings, along with the fuel
pump, tank and the rigid pipe from the pump to the feed union. The engine mountings (Fig 1.29) go in with the
front crossmember, and the 18ACR alternator with the electrical system. The working standard is in
`CLAUDE.md`.
