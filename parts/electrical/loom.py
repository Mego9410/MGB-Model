"""Wiring loom coverings (P10b): braided sleeving over the main runs of the harness, each run sized to
the bundle of wires it covers (mgb.wiring_layout), and the bulkhead grommet. The wires are the parts of
the electrical.wiring-* assemblies; hide the sleeving to see them."""
import importlib.util
from pathlib import Path

from build123d import Compound, Location, Part, Plane

from mgb import body_layout as BL, wiring_layout as WL
from mgb.elec_shapes import label, rev

_sp = importlib.util.spec_from_file_location("_wiring", Path(__file__).with_name("wiring.py"))
_w = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_w)

GROUP = {"engine-bay": ("gr.bay", "bay."), "overdrive": ("od.", "relay.n", "iso.n", "odsol.n"),
         "facia": ("gr.cab", "fa.", "wiper.n", "dip.n", "col.n"), "rear": ("re.",)}
TRIM = 9.0                                          # sleeving stops short of each node: the tape ends


def _group(a, b):
    if a == "gr.bay" and b == "gr.cab":
        return "facia"
    for g in ("overdrive", "facia", "rear", "engine-bay"):
        if any(a.startswith(p) or b.startswith(p) for p in GROUP[g]) and g != "engine-bay":
            return g
    return "engine-bay"


def _trimmed(pts, d):
    """The path with d cut off each end."""
    import math
    out = list(pts)
    for _ in range(2):
        rem = d
        while len(out) > 2 and math.dist(out[0], out[1]) <= rem:
            rem -= math.dist(out[0], out[1])
            out.pop(0)
        L = math.dist(out[0], out[1])
        if L > rem:
            out[0] = WL._add(out[0], WL._unit(WL._sub(out[1], out[0])), rem)
        out = out[::-1]
    return out


def sleeving(group):
    def build(spec) -> Part:
        t = spec.nom("wall")
        lay = WL.layout()
        solids = []
        for (a, b), e in lay["edges"].items():
            if not e["sleeved"] or _group(a, b) != group:
                continue
            r = e["radius"] + 0.35
            pts = WL.smooth(_trimmed(e["points"], TRIM), 2.0 * r)
            if len(pts) < 2 or sum(__import__("math").dist(p, q) for p, q in zip(pts, pts[1:])) < 6.0:
                continue
            outer = _w.tube(pts, r + t, 12)
            try:
                s = outer - _w.tube(_extend(pts, 1.0), r, 12)
                if not s.is_valid:
                    s = outer
            except Exception:  # noqa: BLE001 - keep the solid sleeve if the kernel refuses
                s = outer
            solids.append(s)
        return label(Compound(children=solids), spec)
    return build


def _extend(pts, d):
    a = WL._add(pts[0], WL._unit(WL._sub(pts[0], pts[1])), d)
    b = WL._add(pts[-1], WL._unit(WL._sub(pts[-1], pts[-2])), d)
    return [a] + list(pts) + [b]


def grommet(spec) -> Part:
    """Rubber grommet: a flanged ring each side of the bulkhead (1 mm panel) round the harness."""
    e = WL.layout()["edges"][("gr.bay", "gr.cab")]
    ri = e["radius"] + 0.4
    ro = spec.nom("flange_diameter") / 2
    x0 = BL.HARNESS_GROMMET[0]
    prof = [(ri, -9.0), (ri + 2.0, -9.0), (ro, -3.0), (ro, -0.5), (ri + 5.0, -0.5), (ri + 5.0, 0.5), (ro, 0.5), (ro, 3.0),
            (ri + 2.0, 9.0), (ri, 9.0)]
    g = Plane(origin=(x0, BL.HARNESS_GROMMET[1], BL.HARNESS_GROMMET[2]), z_dir=(1, 0, 0)).location * rev(prof)
    return label(g, spec)


PARTS = {f"electrical.loom.{g}": {"build": sleeving(g)} for g in GROUP}
PARTS["electrical.loom.bulkhead-grommet"] = {"build": grommet}
