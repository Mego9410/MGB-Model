"""Geometry of the body shell's outer surface (P11b), shared by every outer panel and the frames that follow it.

The outer surface is one B-spline face fitted through ray samples of the implicit body in mgb.body_shell_layout (the
rays fan out from a spine along the car that turns down round the nose and the tail, so the face wraps the whole
body without a crease). A panel is the part of this face inside a signed-distance region along its shut lines
(negative inside): the region is contoured on a grid of the face's parameters, the contours become trimming wires in
the face's parameter plane, and the trimmed face is thickened inward. (Lofted solids and
solid booleans on the free-form surface failed or took minutes in OpenCascade, so no thin-wall boolean is used.)

Results are cached on disk (`.cache/body/`, keyed on the layout files and CACHE_VERSION); bump CACHE_VERSION when the
trimming code here changes, or delete the folder.
"""
from __future__ import annotations

import functools
import hashlib
import math
from pathlib import Path

from build123d import Compound, Edge, Face, Solid, Vector, Wire, export_brep, import_brep, thicken
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

from mgb import body_shell_layout as S

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "body"
_SOURCES = ["mgb/body_shell_layout.py", "mgb/body_layout.py", "mgb/underbody_layout.py", "mgb/car_layout.py"]
CACHE_VERSION = "6"                        # bump when the trimming code here changes (the layout files are hashed)


@functools.lru_cache(maxsize=None)
def _source_hash(extra=()):
    h = hashlib.sha1(CACHE_VERSION.encode())
    for f in list(_SOURCES) + list(extra):
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()[:16]


def disk_cached(name, fn, extra_sources=()):
    """Build fn() once and keep its BREP in .cache/body/ until the body sources change."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}-{_source_hash(tuple(extra_sources))}.brep"
    if path.exists():
        try:
            shp = import_brep(str(path))
            if shp is not None and shp.is_valid:
                return shp
        except Exception:  # noqa: BLE001 - a damaged cache file is rebuilt
            pass
    shp = fn()
    export_brep(shp, str(path))
    return shp


# ---- the outer surface -------------------------------------------------------------------------------------------
def _outer_face():
    """One B-spline face through the ray samples of the implicit body (mgb.body_shell_layout.sample_grid)."""
    return fit_ls(S.sample_grid(), N_POLES)


N_POLES = (150, 110)                         # control net along the car and round the section


def fit_ls(P, n_poles, lam=0.02, deg=3):
    """Least-squares tensor-product cubic B-spline through a grid of points P (rows, cols, 3), parametrised by the
    grid index, with a light second-difference smoothing on the control net (so it cannot oscillate)."""
    import numpy as np
    from scipy.interpolate import BSpline
    from OCP.Geom import Geom_BSplineSurface
    from OCP.collections import Array1_double as TColStd_Array1OfReal, Array1_int as TColStd_Array1OfInteger
    from OCP.collections import Array2_gp_Pnt as TColgp_Array2OfPnt
    from OCP.gp import gp_Pnt
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    m, n, _ = P.shape
    na, nb = n_poles

    def basis(count, npol):
        inner = np.linspace(0.0, 1.0, npol - deg + 1)
        t = np.r_[[0.0] * deg, inner, [1.0] * deg]
        x = np.linspace(0.0, 1.0, count)
        B = BSpline.design_matrix(x, t, deg).toarray()
        D = np.diff(np.eye(npol), 2, axis=0)
        return B, D, inner

    Bu, Du, ku = basis(m, na)
    Bv, Dv, kv = basis(n, nb)
    Au = np.linalg.solve(Bu.T @ Bu + lam * Du.T @ Du, Bu.T)        # (na, m)
    Av = np.linalg.solve(Bv.T @ Bv + lam * Dv.T @ Dv, Bv.T)        # (nb, n)
    C = np.einsum("am,mnk,bn->abk", Au, P, Av)
    poles = TColgp_Array2OfPnt(1, na, 1, nb)
    for i in range(na):
        for j in range(nb):
            poles.SetValue(i + 1, j + 1, gp_Pnt(*map(float, C[i, j])))

    def knots(inner):
        k = TColStd_Array1OfReal(1, len(inner))
        mu = TColStd_Array1OfInteger(1, len(inner))
        for i, v in enumerate(inner):
            k.SetValue(i + 1, float(v))
            mu.SetValue(i + 1, deg + 1 if i in (0, len(inner) - 1) else 1)
        return k, mu
    uk, um = knots(ku)
    vk, vm = knots(kv)
    srf = Geom_BSplineSurface(poles, uk, vk, um, vm, deg, deg)
    return Face(BRepBuilderAPI_MakeFace(srf, 1e-7).Face())


def _fit(rows, tol):
    """B-spline surface through a grid of points; the fit is checked against the grid's bounds (a tight tolerance
    can make the approximation oscillate) and loosened until it stays inside them."""
    import numpy as np
    from OCP.BRep import BRep_Tool
    A = np.array(rows)
    lo, hi = A.reshape(-1, 3).min(0) - 8.0, A.reshape(-1, 3).max(0) + 8.0
    for t in (tol, tol * 2, tol * 4, tol * 8):
        f = Face.make_surface_from_array_of_points(rows, tol=t, min_deg=3, max_deg=3)
        srf = BRep_Tool.Surface_s(f.wrapped)
        u0, u1, v0, v1 = srf.Bounds()
        ok = True
        for a in np.linspace(0.0, 1.0, 161):
            for b in np.linspace(0.0, 1.0, 81):
                p = srf.Value(u0 + (u1 - u0) * a, v0 + (v1 - v0) * b)
                if not (lo[0] < p.X() < hi[0] and lo[1] < p.Y() < hi[1] and lo[2] < p.Z() < hi[2]):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return f
    raise ValueError("surface fit oscillates")


SURFACES = {"outer": (_outer_face, 2200, 900)}


@functools.lru_cache(maxsize=None)
def surface_face(name):
    return disk_cached(f"surface-{name}", SURFACES[name][0]).faces()[0]


@functools.lru_cache(maxsize=None)
def _surf(name):
    from OCP.BRep import BRep_Tool
    return BRep_Tool.Surface_s(surface_face(name).wrapped)


@functools.lru_cache(maxsize=None)
def uv_grid(name):
    """Points of a surface face on a grid of its parameters: (U, V, XYZ)."""
    import numpy as np
    nu, nv = SURFACES[name][1:]
    path = CACHE / f"uvgrid-{name}-{nu}x{nv}-{_source_hash()}.npy"
    U = np.linspace(0.0, 1.0, nu)
    V = np.linspace(0.0, 1.0, nv)
    if path.exists():
        return U, V, np.load(path)
    srf = _surf(name)
    u0, u1, v0, v1 = srf.Bounds()
    P = np.zeros((nu, nv, 3))
    for a, u in enumerate(U):
        uu = u0 + (u1 - u0) * u
        for b, v in enumerate(V):
            p = srf.Value(uu, v0 + (v1 - v0) * v)
            P[a, b] = (p.X(), p.Y(), p.Z())
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, P)
    return U, V, P


def _region_on(name, X, Y, Z):
    """Where the outer face is skin: above the skin's lower edge (the implicit body continues under it)."""
    return S.z_of(S.z_b_xy(X, Y)) - Z


def _march(F):
    """Closed zero contours of the field F (negative inside) as lists of (row, col) points; F's border must be
    positive."""
    import numpy as np
    neg = F < 0
    segs = {}
    R, C = F.shape

    def interp(a, b, pa, pb):
        fa, fb = F[pa], F[pb]
        t = fa / (fa - fb)
        return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
    # edges keyed by grid edge id: ('h', r, c) between (r,c)-(r,c+1); ('v', r, c) between (r,c)-(r+1,c)
    cells = np.argwhere(neg[:-1, :-1] ^ neg[1:, :-1] | neg[:-1, :-1] ^ neg[:-1, 1:] | neg[1:, 1:] ^ neg[1:, :-1])
    adj = {}
    pts = {}

    def link(e1, e2):
        adj.setdefault(e1, []).append(e2)
        adj.setdefault(e2, []).append(e1)
    for r, c in cells:
        r, c = int(r), int(c)
        corners = [(r, c), (r, c + 1), (r + 1, c + 1), (r + 1, c)]
        edges = [("h", r, c), ("v", r, c + 1), ("h", r + 1, c), ("v", r, c)]
        ins = [neg[p] for p in corners]
        cross = []
        for k in range(4):
            if ins[k] != ins[(k + 1) % 4]:
                e = edges[k]
                if e not in pts:
                    pts[e] = interp(corners[k], corners[(k + 1) % 4], corners[k], corners[(k + 1) % 4])
                cross.append(e)
        if len(cross) == 2:
            link(cross[0], cross[1])
        elif len(cross) == 4:
            centre = F[r:r + 2, c:c + 2].mean()
            if (centre < 0) == ins[0]:
                link(cross[0], cross[1]); link(cross[2], cross[3])
            else:
                link(cross[0], cross[3]); link(cross[1], cross[2])
    loops, seen = [], set()
    for e0 in adj:
        if e0 in seen:
            continue
        loop, prev, cur = [], None, e0
        while True:
            seen.add(cur)
            loop.append(pts[cur])
            nxt = [e for e in adj[cur] if e != prev]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            if cur == e0:
                break
        if len(loop) > 8:
            loops.append(loop)
    return loops


def _area(loop):
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(loop, loop[1:] + loop[:1]))


def _resample_loop(loop, n):
    """n points evenly spaced round a closed loop."""
    import math as m
    pts = loop + [loop[0]]
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + m.dist(a, b))
    out, j = [], 0
    for k in range(n):
        s_ = d[-1] * k / n
        while j < len(d) - 2 and d[j + 1] < s_:
            j += 1
        t = (s_ - d[j]) / max(d[j + 1] - d[j], 1e-12)
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _wire_on_surface(loop_uv, srf, spacing=2.0):
    """Closed wire on the surface along a loop given in grid cells (row, col) mapped to (u, v): straight segments in
    the surface's parameter plane, `spacing` grid cells long."""
    import math as m
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
    from OCP.Geom2d import Geom2d_Line, Geom2d_TrimmedCurve
    from OCP.gp import gp_Dir2d, gp_Pnt2d
    cells, (u0, u1, v0, v1), (nu, nv) = loop_uv
    per = sum(m.dist(a, b) for a, b in zip(cells, cells[1:] + cells[:1]))
    n = max(int(per / spacing), 8)
    pts = _resample_loop(cells, n)
    uv = [(u0 + (u1 - u0) * min(max(r / (nu - 1), 1e-6), 1 - 1e-6),
           v0 + (v1 - v0) * min(max(c / (nv - 1), 1e-6), 1 - 1e-6)) for r, c in pts]
    mw = BRepBuilderAPI_MakeWire()
    for a, b in zip(uv, uv[1:] + uv[:1]):
        L = m.dist(a, b)
        if L < 1e-12:
            continue
        seg = Geom2d_TrimmedCurve(Geom2d_Line(gp_Pnt2d(*a), gp_Dir2d(b[0] - a[0], b[1] - a[1])), 0.0, L)
        mw.Add(BRepBuilderAPI_MakeEdge(seg, srf).Edge())
    return mw.Wire()


def _dedupe2(pts, tol=1e-7):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > tol:
            out.append(p)
    while len(out) > 3 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= tol:
        out.pop()
    return out


def trimmed_faces(sdf):
    """Faces of the outer surfaces where sdf(X, Y, Z) < 0 (numpy arrays of car coordinates, mm): one face per outer
    contour, with the inner contours as holes."""
    import numpy as np
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.BRepLib import BRepLib
    from OCP.ShapeFix import ShapeFix_Face
    faces = []
    for name in SURFACES:
        U, V, P = uv_grid(name)
        X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
        bb = sdf(X, Y, Z)
        if not (bb < 0).any():
            continue
        Fd = sd_and(bb, _region_on(name, X, Y, Z))
        if not (Fd < 0).any():
            continue
        nu, nv = Fd.shape
        Fd[0, :] = np.maximum(Fd[0, :], 1e-3)
        Fd[-1, :] = np.maximum(Fd[-1, :], 1e-3)
        Fd[:, 0] = np.maximum(Fd[:, 0], 1e-3)
        Fd[:, -1] = np.maximum(Fd[:, -1], 1e-3)
        loops = _march(Fd)
        srf = _surf(name)
        bounds = srf.Bounds()
        loops = [lp for lp in loops if abs(_area(lp)) > 1.0]
        depth = [sum(1 for other in loops if other is not lp and _inside(lp[0], other)) for lp in loops]
        ccw = lambda lp: lp if _area(lp) > 0 else lp[::-1]                       # noqa: E731
        outers = [ccw(lp) for lp, d in zip(loops, depth) if d % 2 == 0 and abs(_area(lp)) > 4.0]
        holes = [ccw(lp)[::-1] for lp, d in zip(loops, depth) if d % 2 == 1]
        for ol in outers:
            mk = BRepBuilderAPI_MakeFace(srf, _wire_on_surface((ol, bounds, (nu, nv)), srf))
            for il in holes:
                if _inside(il[0], ol) and not any(_inside(il[0], o2) and _inside(o2[0], ol) for o2 in outers if o2 is not ol):
                    mk.Add(_wire_on_surface((il, bounds, (nu, nv)), srf))
            f = mk.Face()
            BRepLib.BuildCurves3d_s(f)
            fx = ShapeFix_Face(f)
            fx.Perform()
            face = Face(fx.Face())
            if face.is_valid and face.area > 50.0:
                faces.append(face)
    return faces


def _inside(p, poly):
    x, y = p
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def _inward(face):
    c = face.center()
    n = face.normal_at(c)
    inner = Vector(min(max(c.X, -2700.0), 650.0), 0.0, S.z_of(560.0))
    return 1.0 if n.dot(inner - c) > 0 else -1.0


def skin_sdf(sdf, t=S.T, shift=None):
    """Thin panel skin where sdf < 0, thickened inward by t (a Compound of thin solids). `shift` (x, y, z) moves the
    trimmed faces before thickening: an inner panel parallel to the skin (a bonnet or boot lid frame, a door's inner
    panel)."""
    from build123d import Location
    out = []
    for f in trimmed_faces(sdf):
        direction = _inward(f)
        if shift:
            f = f.moved(Location(shift))
        try:
            th = thicken(f, direction * t)
        except Exception:  # noqa: BLE001 - skip a patch the offset kernel refuses
            th = None
        if th is None or not th.is_valid:
            continue
        out.append(th)
    return Compound(out)


# ---- signed distance helpers (negative inside; numpy arrays) -----------------------------------------------------------
def sd_poly(a, b, poly):
    """Signed distance from points (a, b) to a closed polygon [(a, b)] (negative inside)."""
    import numpy as np
    d = np.full(a.shape, np.inf)
    inside = np.zeros(a.shape, bool)
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        L2 = ex * ex + ey * ey or 1e-12
        t = np.clip(((a - x1) * ex + (b - y1) * ey) / L2, 0.0, 1.0)
        dx, dy = a - (x1 + t * ex), b - (y1 + t * ey)
        d = np.minimum(d, np.hypot(dx, dy))
        cond = ((y1 > b) != (y2 > b)) & (a < (x2 - x1) * (b - y1) / ((y2 - y1) if y2 != y1 else 1e-12) + x1)
        inside ^= cond
    return np.where(inside, -d, d)


def sd_and(*fs):
    import numpy as np
    out = fs[0]
    for f in fs[1:]:
        out = np.maximum(out, f)
    return out


def sd_or(*fs):
    import numpy as np
    out = fs[0]
    for f in fs[1:]:
        out = np.minimum(out, f)
    return out


def sd_not(f):
    return -f


# ---- region prisms (car frame) ------------------------------------------------------------------------------------


def fillet_poly(pts, radii, n=6):
    """Closed polygon with each vertex i rounded to radii[i] (0 keeps it sharp)."""
    out = []
    m = len(pts)
    for i in range(m):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % m]
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        u1 = ((a[0] - b[0]), (a[1] - b[1]))
        u2 = ((c[0] - b[0]), (c[1] - b[1]))
        l1, l2 = math.hypot(*u1), math.hypot(*u2)
        if r <= 0 or l1 < 1e-6 or l2 < 1e-6:
            out.append(b)
            continue
        u1, u2 = (u1[0] / l1, u1[1] / l1), (u2[0] / l2, u2[1] / l2)
        cosang = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
        half = math.acos(cosang) / 2
        if half < 1e-3 or abs(half - math.pi / 2) < 1e-3:
            out.append(b)
            continue
        d = min(r / math.tan(half), 0.45 * l1, 0.45 * l2)
        rr = d * math.tan(half)
        t1 = (b[0] + u1[0] * d, b[1] + u1[1] * d)
        t2 = (b[0] + u2[0] * d, b[1] + u2[1] * d)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        lb = math.hypot(*bis)
        cen = (b[0] + bis[0] / lb * rr / math.sin(half), b[1] + bis[1] / lb * rr / math.sin(half))
        a1 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        a2 = math.atan2(t2[1] - cen[1], t2[0] - cen[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            t = a1 + da * k / n
            out.append((cen[0] + rr * math.cos(t), cen[1] + rr * math.sin(t)))
    return out


def bonnet_outline(grow=0.0):
    """Bonnet in plan (both sides), grown by `grow` (negative shrinks)."""
    xr = S.BONNET_REAR_X - grow
    xf = S.BONNET_FRONT_X + grow
    ws = [(x, w + grow) for x, w in S.BONNET_W]
    wf = S._interp(ws, xf)
    left = [(xr, S._interp(ws, S.BONNET_REAR_X))] + [(x, w) for x, w in sorted(ws) if xr + 10 < x < xf - 40] + \
           [(xf - 0.00012 * wf ** 2, wf)]
    front = [(xf - 0.00012 * y * y, y) for y in (wf * k / 4 for k in (3, 2, 1, 0, -1, -2, -3))]
    pts = left + front + [(x, -y) for x, y in reversed(left)]
    rf, rr = S.BONNET_CORNER_R
    radii = [rr] + [0] * (len(left) - 2) + [rf] + [0] * len(front) + [rf] + [0] * (len(left) - 2) + [rr]
    return fillet_poly(pts, radii)


def cockpit_outline(grow=0.0):
    xf, xr = S.COCKPIT_FRONT_X + grow, S.COCKPIT_REAR_X - grow
    ws = [(x, w + grow) for x, w in S.COCKPIT_W]
    left = [(xf, ws[0][1])] + [(x, w) for x, w in ws[1:-1]] + [(xr, ws[-1][1])]
    pts = left + [(x, -y) for x, y in reversed(left)]
    rf, rr = S.COCKPIT_CORNER_R
    radii = [rf] + [0] * (len(left) - 2) + [rr, rr] + [0] * (len(left) - 2) + [rf]
    return fillet_poly(pts, radii)


def boot_outline(grow=0.0):
    xf = S.BOOT_FRONT_X + grow
    ws = [(x, w + grow) for x, w in S.BOOT_W]
    left = [(xf, ws[0][1])] + [(x, w) for x, w in ws[1:]] + [(-3200.0, ws[-1][1])]
    pts = left + [(x, -y) for x, y in reversed(left)]
    r = S.BOOT_CORNER_R
    radii = [r] + [0] * (len(left) - 1) + [0] * (len(left) - 1) + [r]
    return fillet_poly(pts, radii)


def door_outline_xz(grow=0.0):
    """Door in side view as (x, height above the road), grown by `grow`: the front shut line straight up to h 690 and
    curving rearward to the pointed top front corner on the waist, the lower corners rounded (S.DOOR_LOWER_R)."""
    xr = S.DOOR_REAR_X - grow
    hb = S.DOOR_BOTTOM_H - grow
    curve = [(S.door_front_x(h) + grow, h) for h in
             (861.0, 852.0, 842.0, 830.0, 818.0, 806.0, 794.0, 782.0, 770.0, 758.0, 746.0, 734.0, 722.0, 710.0, 698.0)]
    pts = [(S.DOOR_FRONT_X + grow, hb), (xr, hb), (xr + S.DOOR_REAR_LEAN, 1100.0), (S.DOOR_TOP_FRONT_X + grow, 1100.0)]
    pts += curve + [(S.DOOR_FRONT_X + grow, S.DOOR_FRONT_CURVE[0][0])]
    r = S.DOOR_LOWER_R + min(grow, 0.0)
    return fillet_poly(pts, [r, r] + [0] * (len(pts) - 2), 10)
