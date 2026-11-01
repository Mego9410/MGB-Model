"""Build every part and assembly, check them, and write the viewer bundle.

    python build.py            # full build into build/
    python build.py --check    # specs and probes only, no export

Exit code is non-zero if any check reports an error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mgb import export, probes, spec as S  # noqa: E402
from mgb.registry import build_registry  # noqa: E402
from mgb.vendor import check_vendor_urls  # noqa: E402

OUT = ROOT / "build"
SITE = ROOT / "site"   # committed static site, served by Vercel as-is


def _load_module(path: Path):
    m = importlib.util.spec_from_file_location(path.stem + "_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(m)
    m.loader.exec_module(mod)
    return mod


def build_parts(findings):
    parts, specs = {}, {}
    for script in sorted((ROOT / "parts").rglob("*.py")):
        mod = _load_module(script)
        sp = S.load(ROOT / "specs" / mod.SPEC)
        specs[sp.id] = sp
        findings += S.check_units(sp) + S.check_provenance(sp)
        part = mod.build(sp)
        if not part.is_valid:
            findings.append(S.Finding("error", sp.id, "geometry", "solid is not valid"))
        for key, fn in getattr(mod, "PROBES", {}).items():
            d = sp[key]
            val = fn(part)
            if not probes.within(val, d.lo_mm, d.hi_mm):
                findings.append(S.Finding("error", sp.id, key,
                                          f"built {val:.4f}, spec {d.lo_mm:.4f}-{d.hi_mm:.4f}"))
        unprobed = [k for k, d in sp.dims.items()
                    if k not in getattr(mod, "PROBES", {}) and not d.raw.get("display_only")
                    and d.source.get("label") in ("H", "F", "S")]
        for k in unprobed:
            findings.append(S.Finding("warning", sp.id, k, "published figure has no probe"))
        parts[sp.id] = part
        print(f"  part  {sp.id:<40} ok, {len(getattr(mod, 'PROBES', {}))} probes")
    return parts, specs


SKELETON = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '</head>\n<body>\n')


def write_site():
    """Copy the viewer bundle to site/ as a standalone static site.

    The artifact host wraps the page in a doctype skeleton; a plain static host
    does not, so site/index.html gets one here.
    """
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(OUT / "viewer", SITE)
    lines = (ROOT / "viewer" / "index.html").read_text().splitlines()
    head = [ln for ln in lines if ln.startswith(("<title", "<meta", "<link"))]
    body = [ln for ln in lines if ln not in head]
    html = SKELETON.replace("</head>", "\n".join(head) + "\n</head>") + "\n".join(body)
    (SITE / "index.html").write_text(html + "\n</body>\n</html>\n")
    print(f"  site  {SITE.relative_to(ROOT)}/ written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    findings: list[S.Finding] = []
    print("Building parts")
    parts, specs = build_parts(findings)
    assemblies = [_load_module(p) for p in sorted((ROOT / "assemblies").glob("*.py"))]

    for a in assemblies:
        for inst_id, part_id, _ in a.INSTANCES:
            if part_id not in parts:
                findings.append(S.Finding("error", a.ID, inst_id, f"unknown part {part_id}"))

    findings += check_vendor_urls(ROOT)

    sizes = {}
    if not args.check:
        if OUT.exists():
            shutil.rmtree(OUT)
        print("Exporting")
        for pid, part in parts.items():
            export.step(part, OUT / "step" / f"{pid}.step")
        for a in assemblies:
            inst = [(i, parts[p], loc) for i, p, loc in a.INSTANCES]
            glb_path = OUT / "glb" / f"{a.ID}.glb"
            export.glb(inst, glb_path, "detail")
            sizes[a.ID] = export.glb_to_embedded_gltf(glb_path, OUT / "viewer" / "models" / f"{a.ID}.json")
            print(f"  glb   {a.ID:<40} {sizes[a.ID] / 1024:.0f} KB")
        reg = build_registry(specs, assemblies, sizes)
        reg["built"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        (OUT / "viewer" / "registry.json").write_text(json.dumps(reg, indent=1))
        shutil.copy(ROOT / "viewer" / "index.html", OUT / "viewer" / "index.html")
        write_site()

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warning"]
    print(f"\n{len(errors)} errors, {len(warns)} warnings")
    for f in errors + warns:
        print(" ", f)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
