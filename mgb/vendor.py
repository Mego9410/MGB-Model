"""Verify every external script URL the viewer loads.

The first viewer hung because a support script it loaded from a CDN did not
exist at that path. jsDelivr's /npm/ URLs serve npm packages file for file, so
each URL is checked against the same package version installed locally.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .spec import Finding

JSD = re.compile(r"https://cdn\.jsdelivr\.net/npm/(@?[^@/]+(?:/[^@/]+)?)@([\d.]+)/([^\"'\s]+)")


def check_vendor_urls(root: Path) -> list[Finding]:
    html = (root / "viewer" / "index.html").read_text()
    out = []
    urls = JSD.findall(html)
    if not urls:
        out.append(Finding("warning", "viewer", "vendor", "no jsDelivr URLs found"))
    for pkg, ver, path in urls:
        pdir = root / "node_modules" / pkg
        url = f"https://cdn.jsdelivr.net/npm/{pkg}@{ver}/{path}"
        if not (pdir / "package.json").exists():
            out.append(Finding("error", "viewer", url, f"package {pkg} not installed to verify"))
            continue
        have = json.loads((pdir / "package.json").read_text())["version"]
        if have != ver:
            out.append(Finding("error", "viewer", url, f"installed {pkg} is {have}, URL pins {ver}"))
        elif not (pdir / path).is_file():
            out.append(Finding("error", "viewer", url, "file does not exist in the package"))
        else:
            out += _check_relative_imports(pdir / path, url, set())
    for other in re.findall(r"<script[^>]+src=\"(https?://[^\"]+)\"", html):
        if "cdn.jsdelivr.net/npm/" not in other:
            out.append(Finding("error", "viewer", other, "external script not on jsDelivr npm; cannot verify"))
    return out


REL = re.compile(r"(?:from|import)\s*['\"](\.{1,2}/[^'\"]+)['\"]")


def _check_relative_imports(file: Path, url: str, seen: set) -> list[Finding]:
    """A module's own relative imports load from the same CDN path, so check them too."""
    out = []
    for rel in REL.findall(file.read_text(errors="ignore")):
        target = (file.parent / rel).resolve()
        if target in seen:
            continue
        seen.add(target)
        if not target.is_file():
            out.append(Finding("error", "viewer", url, f"imports {rel}, which does not exist"))
        else:
            out += _check_relative_imports(target, url, seen)
    return out
