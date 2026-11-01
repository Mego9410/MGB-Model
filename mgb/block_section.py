"""Cross-section of the cylinder block casting (y, z), shared by the casting and the
block assembly so fittings sit on its faces. Engine frame as mgb.engine_layout.

Derived (D) from Haynes Fig 1.8, Haynes photos 58.4 and 61.1(a), and owners' photos
of bare 18G blocks: a straight water-jacket wall on the right with a ledge where the
crankcase steps out, the tappet chest standing proud on the left, and crankcase walls
that widen slightly down to a pocketed sump flange.
"""
from mgb import engine_layout as E

YR, YL = -62.0, 98.0                # upper wall faces: right (plugs, distributor), left (tappet chest side)
LEDGE_Z = -118.0                    # right-hand ledge, carries the main oil gallery
YR_LOW, YW = -84.0, 112.0           # right crankcase wall just below the ledge; half width at the sump flange
LEFT_KNEE_Z = -175.0                # left wall turns outward below the camshaft
FLANGE_HW = 120.0                   # sump flange half width
CHEST_Z0, CHEST_Z1 = -14.0, -128.0  # tappet chest panel top and bottom
OPEN_L, OPEN_H = 144.0, 62.0        # each tappet chest opening
# left-side features below the camshaft shelf (Fig 1.8 order: "1800" panel and fuel pump
# flange just under the shelf, the oil pump drive pillar, then plug 7 and the relief valve)
FUEL_PUMP_Z = -240.0
LETTER_Z = (-234.0, -204.0)
PLUG7_Z, RELIEF_Z = -232.0, -264.0

def _sump_z():
    from pathlib import Path

    from mgb import spec as S
    from mgb.head_layout import layout as head_layout
    root = Path(__file__).resolve().parent.parent
    return E.layout(head_layout(S.load(root / "specs" / "engine" / "head" / "casting.yaml"))).sump_z


SUMP_Z = _sump_z()


def section(deck, sz, d=0.0):
    """Outline of the block section, grown outward by d."""
    return [(YR - d, deck), (YR - d, LEDGE_Z), (YR_LOW - d, LEDGE_Z - 14), (-YW - d, sz + 10), (-YW - d, sz),
            (YW + d, sz), (YW + d, sz + 10), (YL + d, LEFT_KNEE_Z), (YL + d, deck)]


def wall_y(z, side):
    """Outer wall position at height z, on the left (+1) or right (-1)."""
    sz = SUMP_Z
    if side > 0:
        if z >= LEFT_KNEE_Z:
            return YL
        return YL + (YW - YL) * (LEFT_KNEE_Z - z) / (LEFT_KNEE_Z - sz - 10)
    if z >= LEDGE_Z:
        return YR
    top = LEDGE_Z - 14
    return YR_LOW + (-YW - YR_LOW) * (top - z) / (top - sz - 10)
