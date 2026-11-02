"""Clutch hydraulics, early RHD car: master cylinder on the pedal box, metal pipe to the hose
bracket, hose to the slave cylinder on the bellhousing (Haynes Ch 5 Secs 3, 5, 6; Fig 5.3).

Explode stages follow Haynes:
  Sec 6 para 1   hose off the slave cylinder; the two bolts and spring washers out;
                 the cylinder pulled off the pushrod, which stays on the fork      orders 1-3
  Sec 6 para 2   boot off and the internals shaken out (clips, boot, piston, cup,
                 cup filler, spring); bleed screw and its cap                      orders 4-5
  Sec 5 paras 1-3 cap and seal off to drain; the pipe union (banjo bolt, washers,
                 banjo and pipe) undone at the master cylinder                     orders 6-7
  Sec 5 para 4   the two bolts, nuts and washers (and stiffener) out; cylinder off  orders 8-9
  Sec 5 para 5   boot, circlip, pushrod, piston and cups, washer, retainer, spring  orders 10-11
"""
from pathlib import Path

from build123d import Location, Plane, Rot

from mgb import gearbox_layout as G, spec as S
from parts.clutch import hydraulics as H

ID = "clutch.hydraulics"
NAME = "Clutch master cylinder, pipe, hose and slave cylinder"
PARENT = "clutch"
HAYNES = {"figures": [{"figure": "5.3"}], "section": 5}

ROOT = Path(__file__).resolve().parent.parent
SP = {s.id: s for s in S.load_file(ROOT / "specs" / "clutch" / "hydraulics.yaml")}
UP, DOWN, FWD, BACK, RIGHT = [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, -1, 0]
GROUPS = {"slave": {"axis": FWD, "order": 3, "distance_mm": 90},
          "pipe": {"axis": RIGHT, "order": 7, "distance_mm": 70},
          "master": {"axis": FWD, "order": 9, "distance_mm": 130}}


def ex(axis, order, d):
    return {"axis": list(axis), "order": order, "distance_mm": d}


def nom(part, key):
    return SP["clutch.hydraulics." + part].nom(key)


I, _n = [], {}


def add(part, loc, **o):
    pid = "clutch.hydraulics." + part
    _n[pid] = _n.get(pid, 0) + 1
    I.append((f"{pid}#{_n[pid]}", pid, loc, o))


O = Location((0, 0, 0))
MC = H.mc_frame()
SL = H.slave_frame()
MAS, SLV, PIPE = ["master"], ["slave"], ["pipe"]

# ---- slave cylinder -------------------------------------------------------------------------
add("hose", O, explode=ex(UP, 1, 60))
add("copper-washer", O, explode=ex(UP, 1, 35))
swt = nom("slave-spring-washer", "thickness")
for k, s in enumerate((1, -1)):
    zb = -H.SL_FLANGE_T - swt
    add("slave-spring-washer", SL * Location((s * G.SLAVE_BOLT_DZ, 0, zb)), explode=ex(BACK, 2, 35), label=k == 0)
    add("slave-bolt", SL * Location((s * G.SLAVE_BOLT_DZ, 0, zb)), explode=ex(BACK, 2, 70), label=k == 0)
add("slave-body", SL, groups=SLV)
add("bleed-screw", SL, groups=SLV, explode=ex(UP, 5, 45))
add("bleed-cap", SL, groups=SLV, explode=ex(UP, 4.5, 70))
add("boot-clip-large", SL, groups=SLV, explode=ex(BACK, 4, 25))
add("boot-clip-small", SL, groups=SLV, explode=ex(BACK, 4, 30))
add("slave-boot", SL, groups=SLV, explode=ex(BACK, 4.2, 45))
add("slave-piston", SL, groups=SLV, explode=ex(BACK, 4.4, 80))
add("slave-cup", SL, groups=SLV, explode=ex(BACK, 4.6, 70))
add("slave-cup-filler", SL, groups=SLV, explode=ex(BACK, 4.8, 60))
add("slave-spring", SL, groups=SLV, explode=ex(BACK, 5, 50))
add("slave-pushrod", SL)                       # stays on the fork (Sec 6 para 1)
add("slave-clevis-pin", SL, explode=ex(UP, 1, 40))

# ---- master cylinder --------------------------------------------------------------------------
add("mc-cap", MC, groups=MAS, explode=ex(UP, 6, 60))
add("mc-seal", MC, groups=MAS, explode=ex(UP, 6, 40))
add("banjo-bolt", MC, explode=ex(FWD, 6.5, 60))
add("sealing-washer-outer", MC, explode=ex(FWD, 6.5, 40))
add("banjo", MC, groups=PIPE)
add("sealing-washer-inner", MC, groups=PIPE)
add("metal-pipe", O, groups=PIPE)
pts = H.pipe_points()
for k, f in enumerate((0.3, 0.7)):
    a, b = pts[2], pts[3]
    p = tuple(a[i] + f * (b[i] - a[i]) for i in range(3))
    t = tuple(b[i] - a[i] for i in range(3))
    add("pipe-clip", Plane(origin=p, z_dir=t, x_dir=(0, 0, 1)).location, groups=PIPE, label=k == 0)
add("hose-locknut", O, explode=ex(UP, 1.5, 30))
add("hose-lockwasher", O, explode=ex(UP, 1.5, 20))

add("mc-body", MC, groups=MAS)
wt, st = nom("mc-washer", "thickness"), nom("mc-stiffener", "thickness")
BOX_WALL = 2.0                                   # pedal box sheet behind the flange (P11)
for s, bolt in ((1, "mc-bolt-long"), (-1, "mc-bolt")):
    x = s * H.MC_BOLT_X
    z = -BOX_WALL
    if s > 0:
        add("mc-stiffener", MC * Location((x, 0, z - st)), explode=ex(BACK, 8, 40))
        z -= st
    add("mc-washer", MC * Location((x, 0, z - wt)), explode=ex(BACK, 8, 60), label=s > 0)
    add("mc-nut", MC * Location((x, 0, z - wt)) * Rot(180, 0, 0), explode=ex(BACK, 8, 85), label=s > 0)
    add(bolt, MC * Location((x, 0, H.MC_FLANGE_T)) * Rot(180, 0, 0), explode=ex(FWD, 8, 60))
add("mc-boot", MC, groups=MAS, explode=ex(BACK, 10, 40))
add("mc-circlip", MC, groups=MAS, explode=ex(BACK, 10.2, 60))
add("mc-pushrod", MC, groups=MAS, explode=ex(BACK, 10.4, 90))
add("mc-secondary-cup", MC, groups=MAS, explode=ex(BACK, 10.6, 120))
add("mc-piston", MC, groups=MAS, explode=ex(BACK, 10.6, 120))
add("mc-piston-washer", MC, groups=MAS, explode=ex(BACK, 10.8, 105))
add("mc-main-cup", MC, groups=MAS, explode=ex(BACK, 10.8, 95))
add("mc-spring-retainer", MC, groups=MAS, explode=ex(BACK, 11, 85))
add("mc-spring", MC, groups=MAS, explode=ex(BACK, 11, 80))
INSTANCES = I
