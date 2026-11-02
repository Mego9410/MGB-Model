"""Generate registry.json: everything the viewer needs to know about each part."""
from __future__ import annotations

from .export import node_name
from .spec import MM_PER_IN, Spec

SOURCE_TEXT = {
    "H": "Haynes", "F": "Factory manual", "S": "Supplier", "M": "Measured", "D": "Derived",
}

# Top-level systems in Haynes chapter order (filled in as phases land)
SYSTEMS = [
    ("engine", "Engine", 1), ("cooling", "Cooling", 2), ("fuel", "Fuel and exhaust", 3),
    ("ignition", "Ignition", 4), ("clutch", "Clutch", 5), ("gearbox", "Gearbox and overdrive", 6),
    ("propshaft", "Propeller shaft", 7), ("axle", "Rear axle", 8), ("brakes", "Brakes", 9),
    ("electrical", "Electrical", 10), ("chassis", "Suspension and steering", 11), ("wheels", "Wheels and tyres", 11),
    ("body", "Body and fittings", 12),
]


def _fmt(v: float, dp: int) -> str:
    s = f"{v:.{dp}f}"
    return s


def _range(lo, hi, dp, unit):
    if lo is None:
        return "Not published"
    if abs(lo - hi) < 1e-12:
        return f"{_fmt(lo, dp)} {unit}".strip()
    return f"{_fmt(lo, dp)} to {_fmt(hi, dp)} {unit}".strip()


def _dp(values) -> int:
    """Decimal places as printed in the source, at least 2."""
    best = 2
    for v in values:
        s = repr(float(v)).rstrip("0").split(".")
        if len(s) == 2:
            best = max(best, len(s[1]))
    return min(best, 5)


def _label(key: str) -> str:
    return key.replace("_", " ").capitalize()


def spec_rows(sp: Spec) -> list[dict]:
    rows = []
    for key, d in sp.dims.items():
        raw = d.raw
        src = raw.get("source", {})
        if "lbf_ft" in raw:
            tq = raw["lbf_ft"] if isinstance(raw["lbf_ft"], list) else [raw["lbf_ft"]] * 2
            nm = raw.get("nm")
            nm = nm if isinstance(nm, list) else [nm, nm] if nm else None
            text = _range(tq[0], tq[-1], 0, "lbf ft") + (f" ({_range(nm[0], nm[-1], 0, 'Nm')})" if nm else "")
        elif "deg" in raw:
            text = _range(d.lo_mm, d.hi_mm, 1, "").rstrip() + "°"
        elif "in" in raw:
            inch = raw["in"] if isinstance(raw["in"], list) else [raw["in"], raw["in"]]
            mm = raw.get("mm")
            if mm is not None and not raw.get("erratum"):
                # show the metric figure as the source printed it
                mm = mm if isinstance(mm, list) else [mm, mm]
                mm_text = _range(mm[0], mm[-1], _dp(mm), "mm")
            else:
                mm_text = _range(d.lo_mm, d.hi_mm, 2 if d.hi_mm > 1 else 3, "mm")
            text = _range(inch[0], inch[-1], _dp(inch), "in") + " (" + mm_text + ")"
        elif "count" in raw:
            text = _range(d.lo_mm, d.hi_mm, 0, "")
        else:
            text = _range(d.lo_mm, d.hi_mm, 1, "mm")
            if d.lo_mm is not None and src.get("label") != "D":
                text += f" ({d.lo_mm / MM_PER_IN:.3f} in)"
        ref = ""
        if src.get("label") == "H":
            ref = f"p{src['page']}"
        elif src.get("label") in ("F", "S"):
            ref = src.get("ref", "")
        elif src.get("label") == "D":
            ref = src.get("method", "")
        elif src.get("label") == "M":
            ref = src.get("by", "")
        rows.append({
            "key": key, "label": _label(key), "value": text,
            "source": src.get("label"), "sourceName": SOURCE_TEXT.get(src.get("label"), "?"),
            "ref": ref, "note": src.get("note", ""), "erratum": bool(raw.get("erratum")),
            "printed_mm": (raw["printed_mm"] if isinstance(raw.get("printed_mm"), list)
                           else [raw["printed_mm"]] if raw.get("printed_mm") is not None else None),
        })
    return rows


def build_registry(specs: dict[str, Spec], assemblies, sizes: dict[str, int]) -> dict:
    nodes = {"car": {"id": "car", "kind": "car", "name": "1963 MGB roadster", "parent": None,
                     "children": []}}
    for sid, name, ch in SYSTEMS:
        nodes[sid] = {"id": sid, "kind": "system", "name": name, "parent": "car",
                      "haynes": {"chapter": ch}, "children": []}
        nodes["car"]["children"].append(sid)
    instances = {}
    for a in assemblies:
        nodes[a.ID] = {"id": a.ID, "kind": "assembly", "name": a.NAME, "parent": a.PARENT,
                       "haynes": a.HAYNES, "children": [], "file": f"models/{a.ID}.json",
                       "bytes": sizes.get(a.ID)}
        nodes[a.PARENT]["children"].append(a.ID)
        groups = getattr(a, "GROUPS", {})
        for inst in a.INSTANCES:
            inst_id, part_id = inst[0], inst[1]
            opts = inst[3] if len(inst) > 3 else {}
            own = opts.get("explode", specs[part_id].data.get("explode"))
            stages = [dict(groups[g], group=g) for g in opts.get("groups", [])]
            if own:
                stages.append(own)
            instances[inst_id] = {"part": part_id, "assembly": a.ID, "node": node_name(inst_id),
                                  "stages": stages, "label": opts.get("label", True),
                                  "fitted": opts.get("fitted_note")}
            if part_id not in nodes[a.ID]["children"]:
                nodes[a.ID]["children"].append(part_id)
    for pid, sp in specs.items():
        d = sp.data
        derived = sum(1 for r in sp.dims.values() if r.source.get("label") == "D")
        nodes[pid] = {
            "id": pid, "kind": "part", "name": d["name"], "parent": d.get("assembly"),
            "haynes": d.get("haynes"), "quantity": d.get("quantity"),
            "partNumbers": [{"number": p["number"], "by": p.get("by", "")}
                            for p in d.get("part_numbers", [])],
            "material": d.get("material"), "finish": d.get("finish"), "notes": d.get("notes", "").strip(),
            "variant": d.get("variant", {}), "explode": d.get("explode"),
            "specs": spec_rows(sp), "derivedShare": round(derived / max(1, len(sp.dims)), 2),
        }
        if d.get("wire"):
            # a wire: Lucas colour code, circuit and the two terminals it joins (shown on the card, traced in the viewer)
            nodes[pid]["wire"] = d["wire"]
    # prune empty systems from the tree so the viewer shows only what exists
    return {"schema": 1, "nodes": nodes, "instances": instances}
