"""Engine layout below the head, in the same frame as mgb.head_layout.

Frame: X forward (No 1 cylinder front), Y to the car's left (manifold, pushrod
and camshaft side), Z up. z = 0 is the head joint face; the block deck sits one
compressed gasket thickness lower.

The crank centre is fixed by published figures:
  half stroke 1.75 in (Haynes p20) + rod centres 6.5 in (Haynes p21)
  + piston compression height 42.06 mm (FIA homologation 3016)
so a piston at TDC sits flush with the deck.
"""
from __future__ import annotations

from dataclasses import dataclass, field

STROKE = 88.9            # Haynes p20
ROD_CENTRES = 165.1      # Haynes p21
COMPRESSION_HEIGHT = 42.06  # FIA homologation 3016: gudgeon centre to crown, 42.01/42.11 mm
GASKET = 1.6             # derived head gasket thickness


@dataclass
class EngineLayout:
    deck_z: float
    crank_z: float
    throw: float
    cyl_x: list[float]
    pin_angle: dict[int, float]            # cylinder -> crank angle (deg), 0 = throw straight up
    main_x: list[float]                    # front, centre, rear main journals
    cam_y: float
    cam_z: float
    cam_journal_x: list[float]
    tappet_xy: list[tuple[float, float]] = field(default_factory=list)
    block_x: tuple[float, float] = (-226.0, 226.0)
    sump_z: float = 0.0
    chest_y: float = 108.0                 # face of the tappet chest panel (left side)
    chest_z: float = 0.0                   # centre height of the two tappet chest openings
    drive_x: float = -89.0                 # skew gear: distributor and oil pump drives (between Nos 3 and 4 lobes)


def layout(head_layout) -> EngineLayout:
    deck = -GASKET
    crank_z = deck - (STROKE / 2 + ROD_CENTRES + COMPRESSION_HEIGHT)
    # firing order 1-3-4-2: throws of 1 and 4 together, 2 and 3 opposite; shown at No 1 TDC
    lay = EngineLayout(
        deck_z=deck, crank_z=crank_z, throw=STROKE / 2, cyl_x=list(head_layout.cyl_x),
        pin_angle={1: 0.0, 2: 180.0, 3: 180.0, 4: 0.0},
        main_x=[205.0, 0.0, -205.0],
        cam_y=head_layout.pushrod_y, cam_z=-150.0,
        cam_journal_x=[200.0, 0.0, -200.0],
        sump_z=crank_z - 50.0,
    )
    lay.chest_z = lay.cam_z + 72.0
    lay.tappet_xy = [(v.x, head_layout.pushrod_y) for v in head_layout.valves]
    return lay


def piston_z(lay: EngineLayout, cyl: int) -> float:
    """Gudgeon pin centre height for a cylinder at the shown crank angle."""
    import math
    a = math.radians(lay.pin_angle[cyl])
    pin_z = lay.crank_z + lay.throw * math.cos(a)
    return pin_z + ROD_CENTRES   # throws are vertical at 0 and 180 deg, so rods are vertical
