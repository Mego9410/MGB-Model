"""Twin SU HS4 carburettors and air cleaners (Haynes Ch 3, Figs 3.1, 3.10-3.12).

Explode stages follow Haynes: Sec 3 air cleaners off (bolts, cases, elements,
baseplates, gaskets, adaptors); Sec 18 linkage and springs, flange nuts, the pair of
instruments off together, distance pieces, gaskets and heat shield; then each
instrument dismantled - damper, suction chamber, spring and piston, float chamber
lid and float, float chamber, jet and its nuts.
"""

from pathlib import Path

from build123d import Location, Rot

from mgb import carb_layout as K, spec as S

ID = "fuel.carbs"
NAME = "Twin SU HS4 carburettors and air cleaners"
PARENT = "fuel"
HAYNES = {"figures": [{"figure": "3.10"}, {"figure": "3.11"}, {"figure": "3.1"}], "section": 18}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "fuel" / "carburettors.yaml")}
OUT, UP, DOWN = [0, 1, 0], [0, 0, 1], [0, 0, -1]
GROUPS = {f"cleaner-{k}": {"axis": OUT, "order": 2, "distance_mm": 160} for k in ("front", "rear")}
GROUPS.update({f"carb-{k}": {"axis": OUT, "order": 6, "distance_mm": 140} for k in ("front", "rear")})


def ex(axis, order, d):
    return {"axis": axis, "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "fuel.carbs." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


def nom(part, key):
    return SP["fuel.carbs." + part].nom(key)


O = Location((0, 0, 0))
z = K.AXIS_Z
add("heat-shield", O, explode=ex(OUT, 8, 40))
add("coupling-shaft", O, explode=ex(UP, 4, 90))
add("jet-rod", O, explode=ex(DOWN, 4, 90))
for x, name in zip(K.CARB_X, ("front", "rear")):
    s = K.side(x)
    first = name == "front"
    C = [f"carb-{name}"]
    # stack-up: gasket, shield, gasket, distance piece, gasket
    y = K.MANIFOLD_FACE_Y
    add("flange-gasket", Location((x, y, z)), explode=ex(OUT, 8.5, 20), label=first)
    y += K.GASKET + K.SHIELD_T
    add("flange-gasket", Location((x, y, z)), explode=ex(OUT, 7.5, 50), label=False)
    y += K.GASKET
    add("distance-piece", Location((x, y, z)), explode=ex(OUT, 7, 80), label=first)
    y += K.DISTANCE_T
    add("flange-gasket", Location((x, y, z)), explode=ex(OUT, 6.5, 100), label=False)
    for dx in (-K.STUD_DX, K.STUD_DX):
        add("stud", Location((x + dx, K.MANIFOLD_FACE_Y - 12, z)) * Rot(-90, 0, 0), label=first and dx < 0)
        wt = nom("washer", "thickness")
        add("washer", Location((x + dx, K.BODY_Y + 9, z)) * Rot(-90, 0, 0), explode=ex(OUT, 5, 60), label=first and dx < 0)
        add("nut", Location((x + dx, K.BODY_Y + 9 + wt, z)) * Rot(-90, 0, 0), explode=ex(OUT, 5, 90), label=first and dx < 0)
    # the instrument
    add(f"body-{name}", O, groups=C)
    add(f"throttle-disc-{name}", O, groups=C, explode=ex(DOWN, 12, 30))
    add("throttle-spindle", Location((x, K.SPINDLE_Y, z)), groups=C, explode=ex([-s, 0, 0], 12, 80), label=first)
    add("throttle-lever", Location((x - s * 46, K.SPINDLE_Y, z)), groups=C, explode=ex([-s, 0, 0], 11, 60), label=first)
    add("return-spring", Location((x - s * 46, K.SPINDLE_Y, z - 88)), explode=ex(DOWN, 3, 60), label=first)
    add("suction-chamber", Location((x, K.PISTON_Y, K.CHAMBER_BASE_Z)), groups=C, explode=ex(UP, 9, 120), label=first)
    add("damper", Location((x, K.PISTON_Y, K.CHAMBER_BASE_Z + nom("suction-chamber", "height"))), groups=C,
        explode=ex(UP, 8, 220), label=first)
    add("piston-spring", Location((x, K.PISTON_Y, z + 34)), groups=C, explode=ex(UP, 9.5, 190), label=first)
    add("piston", Location((x, K.PISTON_Y, z - 6)), groups=C, explode=ex(UP, 10, 150), label=first)
    add(f"float-lid-{name}", O, groups=C, explode=ex(UP, 9, 70))
    add("float", Location((x + s * K.FLOAT_DX, K.PISTON_Y, z - 50 - nom("float-chamber-front", "height") / 2 + 6)),
        groups=C, explode=ex(UP, 9.5, 110), label=first)
    add(f"float-chamber-{name}", O, groups=C, explode=ex([s, 0, 0], 10, 70))
    d = nom("float-chamber-front", "diameter")
    add("float-bolt", Location((x + s * (K.FLOAT_DX - d / 2 + 3), K.PISTON_Y, z - 50)) * Rot(0, -90 * s, 0), groups=C,
        explode=ex([s, 0, 0], 9.8, 120), label=first)
    add(f"jet-{name}", O, groups=C, explode=ex(DOWN, 11, 90))
    add("jet-locking-nut", Location((x, K.PISTON_Y, z - 65)), groups=C, explode=ex(DOWN, 10.5, 50), label=first)
    add("jet-adjusting-nut", Location((x, K.PISTON_Y, z - 74)), groups=C, explode=ex(DOWN, 10.6, 70), label=first)
    # air cleaner (Fig 3.1)
    A = [f"cleaner-{name}"]
    yi = K.INTAKE_Y
    add("cleaner-adaptor", Location((x, yi, z)), explode=ex(OUT, 3, 40), label=first)
    add("cleaner-gasket", Location((x, yi + 4, z)), groups=A, explode=ex(OUT, 2.9, 10), label=first)
    add("cleaner-baseplate", Location((x, yi + 4.8, z)), groups=A, explode=ex(OUT, 2.8, 20), label=first)
    add("cleaner-element", Location((x, yi + 6.4, z)), groups=A, explode=ex(OUT, 2.6, 60), label=first)
    add(f"cleaner-case-{name}", Location((x, yi + 4.8, z)), groups=A, explode=ex(OUT, 2.4, 110))
    for dx in (-K.CLEANER_BOLT_DX, K.CLEANER_BOLT_DX):
        add("cleaner-bolt", Location((x + dx, yi + 4.8 + nom("cleaner-case-front", "depth"), z)) * Rot(90, 0, 0),
            groups=A, explode=ex(OUT, 1, 120), label=first and dx < 0)
INSTANCES = I

