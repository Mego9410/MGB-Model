# Working standard for this repo

The owner wants production-grade models, not reference blocks. Work to this level
without being asked:

- **Research every part before modelling it.** Use the Haynes figure and every Haynes
  photo that shows the part (render the PDF pages and zoom in), plus outside reference
  photos of the real part. When a browser is available, look at photos of bare parts
  from several sides. Note what you used in the part's spec `notes`.
- **Model the real form.** Castings get their bosses, ribs, pads, flanges, ledges,
  lettering and fillets; pressings get their outline, dimples, beads and raised panels;
  holes go where the mating fixings go. A plain box or plate is never finished work.
- **Compare before calling it done.** Render the part from the same angles as the
  figure and photos (`tests/shots.mjs` with `VIEWS` and `window.mgbCamera`), look at
  them side by side, and fix the differences. Repeat until it matches.
- **Fixings sit on real faces.** Use shared section/layout modules (`mgb/block_section.py`,
  `mgb/engine_layout.py`, `mgb/head_layout.py`) so placements follow the geometry.
- Keep the source labels honest: published figures are H/F/S with a page or reference;
  shapes taken from figures or photos are D with the method stated.
- Never commit env files.

# How the repo works (read before adding a phase)

- **Frames.** One frame for the whole car: X forward, Y to the car's left (near side,
  manifold side), Z up, origin on the engine centreline at the head joint face. Engine
  datums: `mgb/engine_layout.py` (crank_z -253.21, sump joint -303.21, block x +/-226,
  front plate face x 230, rear plate at -226). Car datums (wheels, ground, axles,
  overhangs): `mgb/car_layout.py`. Never hard-code a position another module owns;
  import it, and put new shared datums in a `mgb/<system>_layout.py`.
- **Specs.** `specs/<system>/<file>.yaml`: `defaults` (system, assembly, haynes,
  variant, finish) and `parts` (id, name, haynes {section, figures [{figure, legend}]},
  quantity, finish, notes, specs). Every spec dimension has a source: H needs `page`
  (printed page), F/S need `ref`, M needs `by`, D needs `method`. Inch figures govern;
  a Haynes metric misprint is kept as `printed_mm` with `erratum: true`. Published
  dimensions that cannot be probed get `display_only: true`; otherwise give the part a
  probe in `PARTS` so the build measures it.
- **Parts.** `parts/<system>/<name>.py` exports `PARTS = {id: {"build": fn(spec), "probes": {...}}}`.
  Build functions return a valid build123d solid with `label = spec.id`. Helpers:
  `mgb/shapes.py` (revolved, tube, washer, coil_spring, ...), `mgb/fasteners.py`
  (hex_bolt(size, length_in), hex_nut, plain_washer).
- **Assemblies.** `assemblies/<system>_<name>.py` exports ID ("system.name"), NAME,
  PARENT (a system id from `mgb/registry.py` SYSTEMS), HAYNES, GROUPS and INSTANCES:
  a list of `(inst_id, part_id, Location, opts)`; opts `groups` (names in GROUPS that
  explode together), `explode` ({axis, order, distance_mm}; stages run in order, follow
  the Haynes removal order), `label` (False on repeats). Copy `assemblies/fuel_carbs.py`.
- **Viewer.** `viewer/index.html`: add any new finish to `FINISH` and the assembly's
  whole-system offset to `SYSTEM_EXPLODE` (CAD axes) so it separates in the car view.
- **Build and check.** `python build.py` (0 errors required), `python -m pytest tests -q`.
  Review renders: `SELECT=<node id> VIEWS='[{"name":"a","explode":0,"camera":{"dir":[x,y,z],"part":"<part id>","zoom":1}}]' node tests/shots.mjs <assembly id>`
  writes PNGs to `build/review/`. The viewer is Y-up, so a camera `dir` is [CAD x, CAD z, -CAD y]:
  +z in `dir` looks from the car's right (off side). Use SELECT=car to see an assembly in
  place. Swiftshader is slow: never run two builds, or a build and the smoke test, at once.
- **Haynes.** `/home/claude/haynes/haynes.pdf`; printed page = PDF page - 4. Chapter
  starts (PDF): Ch5 110, Ch6 115, Ch7 142, Ch8 146, Ch9 150, Ch10 165, Ch11 206, Ch12 219.
  Render with `pdftoppm -r 110 -f N -l N -png`, crop and zoom with Python PIL, and read
  the text with `pdftotext -layout`.
- **Geometry gotchas.** Extrude a YZ-plane sketch with `dir=(1,0,0)`. Avoid tangent
  booleans (they make invalid solids); offset by a fraction of a millimetre. Give
  `FilletPolyline` a radius fallback. Hollow sweeps can fail; fall back to a solid sweep.
  Check `part.is_valid` on every new part before a full build.
- **Processes.** Kill a stale process by PID, never `pkill -f` with a pattern that can
  match your own shell.
