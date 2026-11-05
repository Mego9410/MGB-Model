"""Export built parts and assemblies: STEP (exact) and compressed GLB (viewer)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from build123d import Compound, Location, Part, export_gltf, export_step

ROOT = Path(__file__).resolve().parent.parent
GLTFPACK = ROOT / "node_modules" / ".bin" / "gltfpack"

# Tessellation for the two detail levels (mm, radians)
LOD = {
    "detail": {"linear": 0.03, "angular": 0.3},
    "car": {"linear": 0.2, "angular": 0.5},
    "body": {"linear": 0.25, "angular": 0.12, "exact_normals": True},   # large thin panels (P11b): smooth curves,
                                                                        # coarser chords on the flats, the surface's own normals
}


def step(part: Part, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    export_step(part, str(path))


def node_name(inst_id: str) -> str:
    """glTF node name for an instance. three.js strips '.', ':', '/', '[' and ']'
    from node names, so ids are written with only letters, digits, '-' and '_'."""
    return inst_id.replace(".", "--").replace("#", "__")


def _surface_normals(face, approx):
    """Exact surface normals at the face's mesh nodes (from their UV parameters), turned to agree with the mesh's
    own normals: smooth shading on large, gently curved panels with long triangles (P11b body skins)."""
    import numpy as np
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.TopLoc import TopLoc_Location
    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face.wrapped, loc)
    if tri is None or not tri.HasUVNodes() or tri.NbNodes() != len(approx):
        return approx
    surf = BRepAdaptor_Surface(face.wrapped)
    props = BRepLProp_SLProps(surf, 1, 1e-6)
    trsf = loc.Transformation()
    out = approx.copy()
    for i in range(tri.NbNodes()):
        uv = tri.UVNode(i + 1)
        props.SetParameters(uv.X(), uv.Y())
        if not props.IsNormalDefined():
            continue
        d = props.Normal().Transformed(trsf)
        v = np.array([d.X(), d.Y(), d.Z()])
        if v @ approx[i] < 0:
            v = -v
        out[i] = v
    return out


def _mesh_part(part: Part, linear: float, angular: float, exact_normals: bool = False):
    """Tessellate face by face so normals stay sharp at edges and smooth within a face.

    Returns float32 positions (metres), float32 normals and uint32 indices.
    """
    import numpy as np
    pos, nrm, idx = [], [], []
    base = 0
    skipped = 0
    for face in part.faces():
        try:
            verts, tris = face.tessellate(linear, angular)
        except AttributeError:          # a degenerate face the mesher cannot triangulate
            skipped += 1
            continue
        if not tris:
            continue
        v = np.array([(p.X, p.Y, p.Z) for p in verts], dtype=np.float64) / 1000.0
        t = np.array(tris, dtype=np.int64)
        # area-weighted vertex normals within this face only
        fn = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
        n = np.zeros_like(v)
        for k in range(3):
            np.add.at(n, t[:, k], fn)
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        n = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
        if exact_normals and len(v) > 12:
            n = _surface_normals(face, n)
        pos.append(v)
        nrm.append(n)
        idx.append(t + base)
        base += len(v)
    if not pos:
        return None
    return (np.concatenate(pos).astype("float32"), np.concatenate(nrm).astype("float32"),
            np.concatenate(idx).astype("uint32").ravel())


def _matrix(loc: Location):
    """Column-major 4x4 glTF matrix for a build123d Location, translation in metres."""
    t = loc.wrapped.Transformation()
    m = [[t.Value(r, c) for c in range(1, 5)] for r in range(1, 4)]
    return [m[0][0], m[1][0], m[2][0], 0, m[0][1], m[1][1], m[2][1], 0,
            m[0][2], m[1][2], m[2][2], 0, m[0][3] / 1000, m[1][3] / 1000, m[2][3] / 1000, 1]


def glb(instances: list[tuple[str, Part, Location]], path: Path, lod: str) -> int:
    """Write one GLB: each distinct solid meshed once, one node per instance.

    Node names are instance ids made safe for three.js (see node_name). The root
    node turns the CAD Z-up frame into glTF Y-up. Returns the compressed size.
    """
    import json
    import struct

    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    q = LOD[lod]
    meshes, mesh_of = [], {}
    buf = bytearray()
    views, accs = [], []

    def add_view(arr, target):
        nonlocal buf
        while len(buf) % 4:
            buf += b"\0"
        off = len(buf)
        buf += arr.tobytes()
        views.append({"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes, "target": target})
        return len(views) - 1

    nodes = [{"name": node_name(path.stem), "rotation": [-0.70710678, 0, 0, 0.70710678], "children": []}]
    for inst_id, part, loc in instances:
        key = id(part)
        if key not in mesh_of:
            m = _mesh_part(part, q["linear"], q["angular"], q.get("exact_normals", False))
            if m is None:
                continue
            p, n, ix = m
            pv, nv, iv = add_view(p, 34962), add_view(n, 34962), add_view(ix, 34963)
            accs.append({"bufferView": pv, "componentType": 5126, "count": len(p), "type": "VEC3",
                         "min": p.min(0).tolist(), "max": p.max(0).tolist()})
            accs.append({"bufferView": nv, "componentType": 5126, "count": len(n), "type": "VEC3"})
            accs.append({"bufferView": iv, "componentType": 5125, "count": len(ix), "type": "SCALAR"})
            a = len(accs)
            meshes.append({"name": node_name(part.label or inst_id),
                           "primitives": [{"attributes": {"POSITION": a - 3, "NORMAL": a - 2}, "indices": a - 1}]})
            mesh_of[key] = len(meshes) - 1
        nodes.append({"name": node_name(inst_id), "mesh": mesh_of[key], "matrix": _matrix(loc)})
        nodes[0]["children"].append(len(nodes) - 1)
    while len(buf) % 4:
        buf += b"\0"
    doc = {"asset": {"version": "2.0", "generator": "mgb-model"}, "scene": 0,
           "scenes": [{"nodes": [0]}], "nodes": nodes, "meshes": meshes, "accessors": accs,
           "bufferViews": views, "buffers": [{"byteLength": len(buf)}]}
    js = json.dumps(doc, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    raw = path.with_suffix(".raw.glb")
    total = 12 + 8 + len(js) + 8 + len(buf)
    raw.write_bytes(struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                    + struct.pack("<II", len(buf), 0x004E4942) + bytes(buf))
    # meshopt compression; keep node names and hierarchy; 16-bit positions (~0.01 mm on a 0.5 m part)
    subprocess.run([str(GLTFPACK), "-i", str(raw), "-o", str(path), "-cc", "-kn", "-km", "-vp", "16"],
                   check=True, stdout=subprocess.DEVNULL)
    raw.unlink()
    return path.stat().st_size


def glb_to_embedded_gltf(src: Path, dst: Path) -> int:
    """Rewrite a GLB as glTF JSON with its binary buffer embedded as base64.

    Claude artifacts serve .json but not .glb; three.js loads either the same way.
    """
    import base64
    import json
    import struct
    b = src.read_bytes()
    jlen = struct.unpack("<I", b[12:16])[0]
    doc = json.loads(b[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack("<I", b[off:off + 4])[0]
    binchunk = b[off + 8:off + 8 + blen]
    doc["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(binchunk).decode()
    for buf in doc["buffers"][1:]:
        buf.setdefault("uri", "data:application/octet-stream;base64,")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(doc, separators=(",", ":")))
    return dst.stat().st_size
