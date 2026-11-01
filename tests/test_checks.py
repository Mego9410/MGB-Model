"""The checks must catch what they claim to. Run: python -m pytest tests -q"""
import shutil
from pathlib import Path

import yaml

from mgb import spec as S
from mgb.vendor import check_vendor_urls

ROOT = Path(__file__).resolve().parent.parent


def _spec(tmp_path, specs):
    p = tmp_path / "t.yaml"
    p.write_text(yaml.safe_dump({"id": "t", "name": "T", "haynes": {}, "quantity": 1, "specs": specs}))
    return S.load(p)


def test_crankpin_misprint_is_caught(tmp_path):
    # Haynes p20 prints 1.8579 to 1.8764 in beside 47.648 to 47.661 mm
    sp = _spec(tmp_path, {"crankpin": {"in": [1.8579, 1.8764], "mm": [47.648, 47.661],
                                       "source": {"label": "H", "page": 20}}})
    assert [f.level for f in S.check_units(sp)] == ["error"]


def test_inlet_head_misprint_is_caught_unless_acknowledged(tmp_path):
    raw = {"in": [1.562, 1.567], "mm": [38.67, 38.80], "source": {"label": "H", "page": 22}}
    assert [f.level for f in S.check_units(_spec(tmp_path, {"h": raw}))] == ["error"]
    fixed = {"in": [1.562, 1.567], "mm": [39.67, 39.80], "printed_mm": [38.67, 38.80],
             "erratum": True, "source": {"label": "H", "page": 22}}
    assert [f.level for f in S.check_units(_spec(tmp_path, {"h": fixed}))] == ["warning"]


def test_good_pair_passes(tmp_path):
    sp = _spec(tmp_path, {"stem": {"in": [0.3422, 0.3427], "mm": [8.69, 8.71],
                                   "source": {"label": "H", "page": 22}}})
    assert S.check_units(sp) == []


def test_unsourced_figure_fails(tmp_path):
    sp = _spec(tmp_path, {"x": {"mm": 3.0}})
    assert any(f.level == "error" for f in S.check_provenance(sp))


def test_haynes_figure_needs_page(tmp_path):
    sp = _spec(tmp_path, {"x": {"mm": 3.0, "source": {"label": "H"}}})
    assert any("page" in f.message for f in S.check_provenance(sp))


def test_bad_cdn_path_fails(tmp_path):
    (tmp_path / "viewer").mkdir()
    (tmp_path / "viewer" / "index.html").write_text(
        '"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"')
    (tmp_path / "node_modules").symlink_to(ROOT / "node_modules")
    assert any(f.level == "error" for f in check_vendor_urls(tmp_path))


def test_real_viewer_urls_pass():
    assert not [f for f in check_vendor_urls(ROOT) if f.level == "error"]
