"""Wiring harness (P10b): every wire must follow the viewer's wire contract and land on real terminals."""
import re
from pathlib import Path

from mgb import electrical_layout as E, spec as S, wiring_layout as WL

ROOT = Path(__file__).resolve().parent.parent
LUCAS = {"B", "U", "N", "G", "LG", "P", "R", "W", "Y", "S", "K", "O"}
SPECS = S.load_all(ROOT / "specs")
WIRES = [sp for sp in SPECS.values() if sp.data.get("wire")]


def _split(code):
    def take(s):
        return ("LG", s[2:]) if s.startswith("LG") else (s[:1], s[1:])
    m, rest = take(code)
    return m, (take(rest)[0] if rest else None)


def test_every_wire_end_is_a_real_part():
    for sp in WIRES:
        for end in ("from", "to"):
            e = sp.data["wire"][end]
            assert e.get("label"), (sp.id, end)
            if e.get("part"):
                assert e["part"] in SPECS, (sp.id, end, e["part"])
        for p in sp.data["wire"].get("via_parts", []):
            assert p in SPECS, (sp.id, p)


def test_finish_matches_the_lucas_code():
    for sp in WIRES:
        code = sp.data["wire"]["code"]
        if not code:                       # heavy cables and the earth strap carry no code on the diagram
            continue
        m, t = _split(code)
        assert m in LUCAS and (t is None or t in LUCAS), (sp.id, code)
        assert sp.data["finish"] == f"wire_{m}" + (f"_{t}" if t else ""), (sp.id, code, sp.data["finish"])
        assert re.fullmatch(r"\d+/0\.30", sp.data["wire"]["size"]), (sp.id, sp.data["wire"]["size"])


def test_routes_land_on_the_terminals_named_on_the_card():
    T = E.terminals()
    for sp in WL.wire_specs():
        r = sp.data["route"]
        for end in ("from", "to"):
            t = T[r[end]]
            assert t["part"] == sp.data["wire"][end]["part"], (sp.id, end)
            WL.term_node(r[end])


def test_every_wire_has_a_harness_path_and_starts_at_its_terminal():
    lay = WL.layout()
    T = E.terminals()
    for sp in WL.wire_specs():
        w = lay["wires"][sp.id]
        for end in ("from", "to"):
            t = T[sp.data["route"][end]]
            e = w["ends"][end]
            assert sum((a - b) ** 2 for a, b in zip(e["p"], t["p"])) ** 0.5 < 12.0, (sp.id, end)


def test_the_two_fuses_feed_what_haynes_says():
    # Sec 33 para 1: fuse 1-2 (A1 in, A2 out) for the horns; fuse 3-4 (A3 in, A4 out) for the ignition circuits
    outs = {sp.data["route"]["from"]: sp.data["wire"]["code"] for sp in WL.wire_specs()}
    assert outs["fuse.A2"] == "P"
    assert outs["fuse.A4"] == "G"
