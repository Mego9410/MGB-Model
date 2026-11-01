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

P0 (foundations) complete: pipeline, checks, fastener library, viewer shell,
inlet valve end to end. Next: P1, the full cylinder head (Haynes Fig 1.6 and 1.9).
