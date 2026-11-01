"""Export built parts and assemblies: STEP (exact) and compressed GLB (viewer)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from build123d import Compound, Location, Part, export_gltf, export_step

ROOT = Path(__file__).resolve().parent.parent
GLTFPACK = ROOT / "node_modules" / ".bin" / "gltfpack"

# Tessellation for the two detail levels (mm, radians)
LOD = {
    "detail": {"linear": 0.01, "angular": 0.08},
    "car": {"linear": 0.15, "angular": 0.35},
}


def step(part: Part, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    export_step(part, str(path))


def node_name(inst_id: str) -> str:
    """glTF node name for an instance. three.js strips '.', ':', '/', '[' and ']'
    from node names, so ids are written with only letters, digits, '-' and '_'."""
    return inst_id.replace(".", "--").replace("#", "__")


def glb(instances: list[tuple[str, Part, Location]], path: Path, lod: str) -> int:
    """Write one GLB holding every instance as a node named by its instance id.

    Returns the compressed file size in bytes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    children = []
    for inst_id, part, loc in instances:
        placed = part.moved(loc)
        placed.label = node_name(inst_id)
        children.append(placed)
    comp = Compound(children=children)
    comp.label = path.stem
    raw = path.with_suffix(".raw.glb")
    q = LOD[lod]
    export_gltf(comp, str(raw), binary=True,
                linear_deflection=q["linear"], angular_deflection=q["angular"])
    # meshopt compression, keep node names (part ids) and node hierarchy
    subprocess.run([str(GLTFPACK), "-i", str(raw), "-o", str(path),
                    "-cc", "-kn", "-km", "-noq"], check=True,
                   stdout=subprocess.DEVNULL)
    raw.unlink()
    return path.stat().st_size
