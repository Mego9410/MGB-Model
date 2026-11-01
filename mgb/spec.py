"""Part spec files: loading, unit-pair checks and provenance checks.

A spec file is YAML. Every dimension carries a source label:
  H  Haynes (page required)       F  factory manual / parts catalogue
  S  supplier data (ref required) M  measured
  D  derived (method required)

A dimension may give inches (`in`), millimetres (`mm`) or both, each as a
single value or a [low, high] range. When Haynes prints a metric figure that
disagrees with its inch figure, record what was printed under `printed_mm`
and set `erratum: true`; the inch figure then governs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

MM_PER_IN = 25.4
NM_PER_LBF_FT = 1.35582
UNIT_TOL_MM = 0.01          # max disagreement between an inch figure and its metric twin
LABELS = {"H", "F", "S", "M", "D"}


@dataclass
class Finding:
    level: str      # "error" | "warning"
    part: str
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.part} :: {self.key} :: {self.message}"


def _rng(v):
    """Normalise a value or [lo, hi] to a (lo, hi) tuple of floats, or None."""
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return float(v[0]), float(v[-1])
    return float(v), float(v)


@dataclass
class Dim:
    key: str
    lo_mm: float | None
    hi_mm: float | None
    unit: str               # "mm" or "deg" or "" for counts
    raw: dict = field(default_factory=dict)

    @property
    def nominal(self) -> float:
        return (self.lo_mm + self.hi_mm) / 2

    @property
    def source(self) -> dict:
        return self.raw.get("source", {})


@dataclass
class Spec:
    path: Path
    data: dict
    dims: dict[str, Dim]

    @property
    def id(self) -> str:
        return self.data["id"]

    def __getitem__(self, key: str) -> Dim:
        return self.dims[key]

    def nom(self, key: str) -> float:
        """Nominal value in mm (or degrees) for building geometry."""
        return self.dims[key].nominal


def _to_dim(key: str, raw: dict) -> Dim:
    inch = _rng(raw.get("in"))
    mm = _rng(raw.get("mm"))
    deg = _rng(raw.get("deg"))
    if deg is not None:
        return Dim(key, deg[0], deg[1], "deg", raw)
    tq = _rng(raw.get("lbf_ft"))
    if tq is not None:
        return Dim(key, tq[0], tq[1], "lbf ft", raw)
    if inch is not None:  # inch governs when present
        return Dim(key, inch[0] * MM_PER_IN, inch[1] * MM_PER_IN, "mm", raw)
    if mm is not None:
        return Dim(key, mm[0], mm[1], "mm", raw)
    count = _rng(raw.get("count"))
    if count is not None:
        return Dim(key, count[0], count[1], "", raw)
    return Dim(key, None, None, "mm", raw)


def _make(path: Path, data: dict) -> Spec:
    dims = {k: _to_dim(k, v) for k, v in (data.get("specs") or {}).items()}
    return Spec(Path(path), data, dims)


def load_file(path: Path) -> list[Spec]:
    """A spec file holds one part, or several under `parts:` with shared `defaults:`."""
    data = yaml.safe_load(Path(path).read_text())
    if "parts" not in data:
        return [_make(path, data)]
    base = data.get("defaults", {})
    out = []
    for item in data["parts"]:
        merged = {**base, **item}
        if "haynes" in base and "haynes" in item:
            merged["haynes"] = {**base["haynes"], **item["haynes"]}
        out.append(_make(path, merged))
    return out


def load(path: Path) -> Spec:
    return load_file(path)[0]


def load_all(root: Path) -> dict[str, Spec]:
    out = {}
    for p in sorted(Path(root).rglob("*.yaml")):
        for sp in load_file(p):
            if sp.id in out:
                raise ValueError(f"duplicate part id {sp.id} in {p} and {out[sp.id].path}")
            out[sp.id] = sp
    return out


# ---------------------------------------------------------------- checks

def check_units(spec: Spec) -> list[Finding]:
    """Every inch figure must match its metric twin to UNIT_TOL_MM."""
    out = []
    for key, raw in (spec.data.get("specs") or {}).items():
        tq, nm = _rng(raw.get("lbf_ft")), _rng(raw.get("nm"))
        if tq and nm and max(abs(tq[0] * NM_PER_LBF_FT - nm[0]), abs(tq[1] * NM_PER_LBF_FT - nm[1])) > 1.0:
            out.append(Finding("error", spec.id, key, f"{tq} lbf ft is not {nm} Nm"))
        inch, mm = _rng(raw.get("in")), _rng(raw.get("mm"))
        printed = _rng(raw.get("printed_mm"))
        if inch is None:
            continue
        conv = (inch[0] * MM_PER_IN, inch[1] * MM_PER_IN)
        for label, pair in (("mm", mm), ("printed_mm", printed)):
            if pair is None:
                continue
            worst = max(abs(conv[0] - pair[0]), abs(conv[1] - pair[1]))
            # allow half a unit of the last decimal place the source printed
            vals = raw.get(label) if isinstance(raw.get(label), list) else [raw.get(label)]
            dp = max(len(repr(float(v)).split(".")[1].rstrip("0") or "") for v in vals)
            if worst > UNIT_TOL_MM + 0.5 * 10 ** -dp:
                msg = (f"{inch[0]}-{inch[1]} in = {conv[0]:.3f}-{conv[1]:.3f} mm, "
                       f"but {label} says {pair[0]}-{pair[1]} mm")
                if label == "printed_mm" and raw.get("erratum"):
                    out.append(Finding("warning", spec.id, key, "known Haynes misprint: " + msg))
                else:
                    out.append(Finding("error", spec.id, key, msg))
    return out


def check_provenance(spec: Spec) -> list[Finding]:
    """Every figure needs a label and the reference that label requires."""
    out = []
    need = {"H": "page", "F": "ref", "S": "ref", "M": "by", "D": "method"}
    for key, raw in (spec.data.get("specs") or {}).items():
        src = raw.get("source") or {}
        lab = src.get("label")
        if lab not in LABELS:
            out.append(Finding("error", spec.id, key, f"missing or unknown source label {lab!r}"))
            continue
        if not src.get(need[lab]):
            out.append(Finding("error", spec.id, key, f"source {lab} needs '{need[lab]}'"))
        if lab == "D":
            out.append(Finding("warning", spec.id, key, "derived figure: " + src.get("method", "")))
    for f in ("id", "name", "haynes", "quantity"):
        if f not in spec.data:
            out.append(Finding("error", spec.id if "id" in spec.data else str(spec.path), f, "missing field"))
    return out
