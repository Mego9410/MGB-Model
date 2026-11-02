"""Lucas 18ACR alternator on the dynamo mountings: pivot bolts through the water pump ear and
the rear bracket, adjusting link on its stud (Haynes Ch 10 Sec 15, 20, 21; Ch 2 Figs 2.1, 2.6).

Explode stages follow Haynes: Sec 15 para 2 the terminal block off, the adjuster link bolt
out, the mounting bolts slackened and the alternator lowered (belt off: cooling), then the
bolts out and the alternator away; Sec 21 para 1 the end cover off, the through-bolts out and
the brackets apart; Fig 2.6 the pulley nut, pulley and fan; then the link, stud and bracket.
"""
from pathlib import Path

from build123d import Location, Rot

from mgb import electrical_layout as E, spec as S

ID = "electrical.charging"
NAME = "Alternator, Lucas 18ACR, and mountings"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.3"}, {"figure": "2.6"}, {"figure": "2.1"}], "section": 20}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "electrical" / "charging.yaml")}
OUT = [0, -0.6, -0.8]
FWD, BACK = [1, 0, 0], [-1, 0, 0]
GROUPS = {"alternator": {"axis": OUT, "order": 4, "distance_mm": 160}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def nom(part, key):
    return SP["electrical.charging." + part].nom(key)


I, _n = [], {}


def add(part, loc, **o):
    pid = "electrical.charging." + part
    _n[pid] = _n.get(pid, 0) + 1
    o.setdefault("label", _n[pid] == 1)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


ay, az = E.ALT_AXIS
ALT = Location((E.BELT_X, ay, az)) * Rot(0, 90, 0)
ALTG = ["alternator"]
O = Location((0, 0, 0))
XF = Rot(0, 90, 0)            # part +z -> car +x
XB = Rot(0, -90, 0)           # part +z -> car -x
YL = Rot(-90, 0, 0)           # part +z -> car +y

# the alternator
add("terminal-plug", ALT, explode=ex(BACK, 1, 90))
add("end-cover", ALT, groups=ALTG, explode=ex(BACK, 5, 70))
for k, a in enumerate((75.0, 195.0, 315.0)):
    add("through-bolt", ALT * Rot(0, 0, a), groups=ALTG, explode=ex(BACK, 6, 120))
add("slip-ring-bracket", ALT, groups=ALTG, explode=ex(BACK, 7, 90))
add("stator", ALT, groups=ALTG, explode=ex(BACK, 7.2, 45))
add("rotor", ALT, groups=ALTG)
add("drive-end-bracket", ALT, groups=ALTG, explode=ex(FWD, 7.5, 40))
add("shaft-nut", ALT, groups=ALTG, explode=ex(FWD, 8, 110))
add("pulley", ALT, groups=ALTG, explode=ex(FWD, 8.2, 80))
add("fan", ALT, groups=ALTG, explode=ex(FWD, 8.4, 55))

# front pivot: bolt 34 from behind the water pump ear, spring washer 35 and nut 36 in front of the lug
py, pz = E.PIVOT
sw = nom("spring-washer", "thickness")
front_lug = E.BELT_X + E.FRONT_LUG_Z[1]
add("pivot-bolt", Location((E.PUMP_EAR_X[0], py, pz)) * XF, explode=ex(BACK, 3, 70))
add("spring-washer", Location((front_lug, py, pz)) * XF, explode=ex(FWD, 3, 40))
add("nut", Location((front_lug + sw, py, pz)) * XF, explode=ex(FWD, 3, 60))
# rear pivot: bolt 31 through the bracket ear and the slip ring end lug, 32 and 33 in front
rear_lug = E.BELT_X + E.REAR_LUG_Z[1]
add("pivot-bolt", Location((E.REAR_EAR_X[0], py, pz)) * XF, explode=ex(BACK, 3, 90))
add("spring-washer", Location((rear_lug, py, pz)) * XF, explode=ex(FWD, 3, 30))
add("nut", Location((rear_lug + sw, py, pz)) * XF, explode=ex(FWD, 3, 45))
# link screw 29 and spring washer 30 into the adjusting lug
ly, lz = E.LINK_LUG
add("spring-washer", Location((E.LINK_X[1], ly, lz)) * XF, explode=ex(FWD, 2, 40))
add("link-screw", Location((E.LINK_X[1] + sw, ly, lz)) * XB, explode=ex(FWD, 2, 70))
# link on its stud: washer 26, spring washer 27, nut 28
sy, sz = E.LINK_STUD
pw = SP["electrical.charging.plain-washer"]
pw_t = 0.065 * 25.4
add("plain-washer", Location((E.LINK_X[1], sy, sz)) * XF, explode=ex(FWD, 9, 40))
add("spring-washer", Location((E.LINK_X[1] + pw_t, sy, sz)) * XF, explode=ex(FWD, 9, 55))
add("nut", Location((E.LINK_X[1] + pw_t + sw, sy, sz)) * XF, explode=ex(FWD, 9, 70))
add("link", O, explode=ex(FWD, 10, 50))
add("link-stud", O, explode=ex(FWD, 11, 90))
# rear bracket on the block boss: screw 16 and spring washer 15
bx, bz = E.REAR_BRACKET_BOSS
bt = nom("rear-bracket", "thickness")
add("spring-washer", Location((bx, E.BOSS_FACE_Y - bt - sw, bz)) * YL, explode=ex([0, -1, 0], 12, 40))
add("bracket-screw", Location((bx, E.BOSS_FACE_Y - bt - sw, bz)) * YL, explode=ex([0, -1, 0], 12, 70))
add("rear-bracket", O, explode=ex([0, -1, 0], 13, 60))
INSTANCES = I
