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
