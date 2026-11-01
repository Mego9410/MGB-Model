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

Next: P2c (cooling: radiator, water pump, fan, hoses). The engine mountings (Fig 1.29)
go in with the front crossmember, since they bolt to it. The working standard is in
`CLAUDE.md`.
