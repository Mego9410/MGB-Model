"""Gear selectors: rods, forks, detent block, selectors, interlock plate and front selector
lever (Haynes Ch 6 Fig 6.3 items 2, 49-75, 82, 119-121; Sec 4 paras 6, 8-9; Sec 7 paras 9-17).

Built in the gearbox frame (mgb.gearbox_layout GF). Explode stages (shared numbering):
  Sec 4 para 6   interlock plate lifted out; front selector lever bolt out; the lever
                 falls free as the extension (adaptor) comes off                 orders 5-9
  Sec 4 para 8   locking wire cut, selector bolts out, selectors off              orders 12-14
  Sec 4 para 9   block screws out, block off, balls and springs out; fork bolts
                 and locknuts out; rods out reverse, 3rd/4th, 1st/2nd; forks out  orders 15-22
"""
from build123d import Location, Rot

from mgb import gearbox_layout as G
from parts.gearbox import selectors as SE
from parts.gearbox.casing import BLOCK, BLOCK_T, BLOCK_SCREWS

ID = "gearbox.selectors"
NAME = "Selector rods, forks and interlock"
PARENT = "gearbox"
HAYNES = {"figures": [{"figure": "6.3"}], "section": 4}

BACK, FWD, UP, DOWN, LEFT, RIGHT = [-1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0]
GROUPS = {"lever": {"axis": BACK, "order": 9, "distance_mm": 60},
          "block": {"axis": BACK, "order": 16, "distance_mm": 110}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


I, _n = [], {}


def add(part, loc, **o):
    pid = "gearbox.selectors." + part
    _n[pid] = _n.get(pid, 0) + 1
    if _n[pid] > 1:
        o.setdefault("label", False)
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


GF = G.GF
KEYS = {"first-second": "12", "third-fourth": "34", "reverse": "rev"}
ROD_ORDER = {"reverse": 19, "third-fourth": 20, "first-second": 21}

# interlock plate and the front selector lever (on the remote control shaft)
add("interlock-plate", GF, explode=ex(UP, 5, 90))
add("pinch-washer", GF * Location((SE.SU + 6.0, SE.SL - 18.0, sum(SE.LEVER_HUB) / 2)) * Rot(0, 90, 0), groups=["lever"],
    explode=ex(UP, 6, 40))
add("pinch-bolt", GF * Location((SE.SU + 7.6, SE.SL - 18.0, sum(SE.LEVER_HUB) / 2)) * Rot(0, -90, 0), groups=["lever"],
    explode=ex(UP, 6, 70))
add("front-lever", GF, groups=["lever"], explode=ex(DOWN, 9.5, 40))

# selectors on the rod ends, their bolts and the wire
add("locking-wire", GF, explode=ex(DOWN, 12, 40))
zs = sum(G.SEL_D) / 2
for key, k in KEYS.items():
    y = G.ROD_LEFT[key]
    add("selector-screw", GF * Location((G.ROD_UP - 11.0, y, zs)) * Rot(0, 90, 0), explode=ex(DOWN, 13, 50))
    add(f"selector-{k}", GF, explode=ex(BACK, 14, 60))

# detent block, balls and springs
u0, u1, l0, l1 = BLOCK
for u, l in BLOCK_SCREWS:
    add("block-washer", GF * Location((u, l, G.CASE_LEN + BLOCK_T - 6.0)), explode=ex(BACK, 15, 40))
    add("block-screw", GF * Location((u, l, G.CASE_LEN + BLOCK_T - 6.0 + 1.6)) * Rot(180, 0, 0), explode=ex(BACK, 15, 70))
add("detent-block", GF, groups=["block"])
for key in KEYS:
    y = G.ROD_LEFT[key]
    ub = G.ROD_UP + SE.RR + 1.2
    add("detent-ball", GF * Location((ub, y, SE.DETENT_D)), groups=["block"], explode=ex(UP, 17, 40))
    add("detent-spring", GF * Location((ub + 3.2, y, SE.DETENT_D)) * Rot(0, 90, 0), groups=["block"], explode=ex(UP, 17, 70))

# forks on the rods
for key, k in KEYS.items():
    y = G.ROD_LEFT[key]
    zb = SE.BOSS_D[key]
    du, dl = SE.BOLT_DIR[key]
    out = [0.0, dl, du]                                   # car frame: along the bolt, away from the rod
    pad = SE.PAD_OFF[key] + 4.0                           # pad face off the rod axis
    add("fork-washer", GF * SE.bolt_frame(key, pad + 0.6), explode=ex(out, 18, 40))
    add("fork-locknut", GF * SE.bolt_frame(key, pad + 0.6 + 5.6), explode=ex(out, 18, 55))
    add("fork-bolt", GF * SE.bolt_frame(key, pad + 0.6 + 5.6), explode=ex(out, 18, 80))
    add(f"rod-{k}", GF, explode=ex(BACK, ROD_ORDER[key], 320))
    add(f"fork-{k}", GF, explode=ex(LEFT if key != "reverse" else LEFT, 22, 150))
add("distance-piece", GF, explode=ex(BACK, 20, 320))
INSTANCES = I
