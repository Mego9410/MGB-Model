"""Cylinder head layout, computed once from the casting spec.

Frame: X along the engine (front, No 1 cylinder, is +X), Y to the left of the car
(+Y is the manifold and pushrod side), Z up. Origin at the head joint face, on the
bore centre line, midway between the end valves.

Fig 1.5 is drawn from above with the front on the right; its upper edge is the
manifold side and its lower edge carries the four spark plug wells.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SCALE_NOTE = "Fig 1.5 at 0.451 mm per 300-dpi pixel"


@dataclass
class Valve:
    name: str          # e.g. "in-1" (inlet, cylinder 1)
    kind: str          # "inlet" | "exhaust"
    cyl: int
    x: float
    y: float


@dataclass
class HeadLayout:
    pitch: float
    vpitch: float
    valve_y: float
    pushrod_y: float
    shaft_y: float
    short_stud_y: float
    top_z: float
    chamber_depth: float
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    cyl_x: list[float] = field(default_factory=list)
    valves: list[Valve] = field(default_factory=list)
    head_studs: list[tuple[int, float, float, str]] = field(default_factory=list)  # (Fig 1.5 number, x, y, kind)
    cover_studs: list[tuple[float, float]] = field(default_factory=list)
    plugs: list[tuple[float, float, float]] = field(default_factory=list)  # chamber end point
    inlet_ports: list[tuple[float, float, list[str]]] = field(default_factory=list)   # (x, z, valves)
    exhaust_ports: list[tuple[float, float, list[str]]] = field(default_factory=list)
    manifold_studs: list[tuple[float, float, str]] = field(default_factory=list)  # (x, z, "centre"|"end")
    thermostat: tuple[float, float] = (0.0, 0.0)


def layout(casting) -> HeadLayout:
    p = casting.nom("cylinder_pitch")
    vp = casting.nom("valve_pitch_in_cylinder")
    vy = casting.nom("valve_row_offset")
    py = vy + casting.nom("pushrod_row_offset")
    L, W = casting.nom("length"), casting.nom("width")
    arm_ratio = 1.4                                  # Haynes p22
    shaft_y = py - (py - vy) / (1 + arm_ratio)       # pushrod arm : valve arm = 1 : 1.4
    cyl_x = [1.5 * p, 0.5 * p, -0.5 * p, -1.5 * p]   # cylinders 1..4, front first
    lay = HeadLayout(
        pitch=p, vpitch=vp, valve_y=vy, pushrod_y=py, shaft_y=shaft_y,
        short_stud_y=shaft_y - 12.8, top_z=casting.nom("height"),
        chamber_depth=casting.nom("chamber_depth"),
        x_min=-228.0, x_max=-228.0 + L, y_max=py + 30.0, y_min=py + 30.0 - W, cyl_x=cyl_x)
    # valve order front to rear: E I | I E | E I | I E
    for c, xc in enumerate(cyl_x, start=1):
        front_kind = "exhaust" if c in (1, 3) else "inlet"
        rear_kind = "inlet" if c in (1, 3) else "exhaust"
        for kind, x in ((front_kind, xc + vp / 2), (rear_kind, xc - vp / 2)):
            lay.valves.append(Valve(f"{kind[:2]}-{c}", kind, c, x, vy))
    # head studs, numbered as Fig 1.5
    for n, x in zip((7, 3, 2, 6), (cyl_x[3], cyl_x[2], cyl_x[1], cyl_x[0])):
        lay.head_studs.append((n, x, py, "pedestal"))
    lay.head_studs.append((11, -206.5, shaft_y - 12.8, "external"))
    lay.head_studs.append((10, 209.0, shaft_y - 12.8, "external"))
    for n, x in zip((8, 4, 1, 5, 9), (-183.0, -p, 0.0, p, 183.0)):
        lay.head_studs.append((n, x, -36.8, "external"))
    lay.cover_studs = [(-p, 20.0), (p, 20.0)]
    lay.plugs = [(x, -20.0, 5.0) for x in cyl_x]
    v = {vv.name: vv for vv in lay.valves}
    lay.inlet_ports = [(p, 38.0, ["in-1", "in-2"]), (-p, 38.0, ["in-3", "in-4"])]
    lay.exhaust_ports = [(v["ex-1"].x, 32.0, ["ex-1"]), (0.0, 32.0, ["ex-2", "ex-3"]),
                         (v["ex-4"].x, 32.0, ["ex-4"])]
    lay.manifold_studs = [(sx * p / 2, z, "centre") for sx in (1, -1) for z in (12.0, 58.0)]
    lay.manifold_studs += [(200.0, 34.0, "end"), (-200.0, 34.0, "end")]
    lay.thermostat = (lay.x_max - 30.0, -18.0)
    return lay
