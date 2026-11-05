"""Underbody datums the exhaust and the fuel supply (P11a) hang from, for the body shell phase (P11b) to build
its floor, heelboard, tonneau floor, axle arch, boot floor and rear panel round. Car frame (mgb.car_layout:
X forward, Y to the car's left, Z up, origin on the engine centreline at the head joint face).

None of these is published; every value is derived (D) from datums the earlier phases set, so the parts
that hang from the body already agree with each other:

- FLOOR_Z, the underside of the cockpit floor beside the tunnel: between the gearbox crossmember's body face
  (mgb.chassis_layout BODY_FACE_Z, -381.2) and P8's brake pipe run under the floor (mgb.brake_layout
  FLOOR_PIPE z -394, a 3/16 in pipe in clips).
- TOE_FOOT, the foot of the toe board: P8's rear brake pipe runs down it from the four-way connection on the
  bulkhead (x -396, z -215) to the floor about 90 mm further back (parts/brakes/lines.py rear_pipe_points).
- TUNNEL_Y, the tunnel's side walls: P8's handbrake spigot passes through the right-hand wall at |y| 122
  (mgb.brake_layout TUNNEL_SIDE_Y).
- HEELBOARD_X, the heelboard's rear (axle side) face: behind the handbrake lever's pivot (x -1420, inside the
  cockpit) and ahead of the battery carriers P10 hangs under the tonneau floor (mgb.body_layout on P10, box
  front wall about x -1606), leaving room between them for the fuel pump, which Haynes puts "on the
  heelboard adjacent to the front of the RH leaf spring" (Ch 3 Sec 5 para 1, printed p67). The heelboard runs
  from FLOOR_Z up to TONNEAU_Z.
- TONNEAU_Z, the underside of the tonneau floor behind the seats: P10's battery box flanges
  (mgb.body_layout TONNEAU_FLOOR_Z).
- ARCH_Z, the underside of the body over the axle: the rear springs' bump stops strike the body at the axle
  pedestal top + bump rubber + 52 mm static gap (P9 rear_suspension_layout BUMP_STRIKE: axle centre + tube
  radius + 26 + 44 + 52); the axle arch and the pipes clipped under it are kept at that height, x ARCH_X.
- BOOT_FLOOR_Z, the boot floor's underside over the tank: 50 mm below the arch, so the tank's filler neck
  passes up through it into the boot (Fig 3.9 item 12, rubber seal tank to boot floor).
- REAR_PANEL: the lower edge of the rear valance under the bumper, where the tail pipe leaves the car.

Fore-aft numbers here and in the notes above are body stations (mgb.car_layout bx: the front wheel axis at 150).
"""
from __future__ import annotations

from mgb import body_layout as BL, car_layout as CL, rear_axle_layout as A

FLOOR_Z = -386.0                         # cockpit floor underside beside the tunnel (D)
TOE_FOOT = (CL.bx(-485.0), FLOOR_Z)            # (x, z) where the toe board meets the floor (D)
TOE_TOP = (CL.BULKHEAD_X, -215.0)        # (x, z) where the toe board meets the bulkhead's engine-side face (D)
TUNNEL_Y = 122.0                         # |y| of the tunnel side walls, cabin face (D, P8)
HEELBOARD_X = CL.bx(-1450.0)                  # rear (axle side) face of the heelboard (D)
TONNEAU_Z = BL.TONNEAU_FLOOR_Z           # tonneau floor underside (D, P10)
ARCH_Z = CL.WHEEL_Z + A.TUBE_R + 26.0 + 44.0 + 52.0   # body underside over the axle (D, P9 bump strike) = -122.5
ARCH_X = (CL.REAR_AXLE_X + 180.0, CL.REAR_AXLE_X - 150.0)   # front and rear ends of the arch's flat roof (D)
BOOT_FLOOR_Z = ARCH_Z - 50.0             # boot floor underside over the tank (D)
REAR_PANEL_X = CL.REAR_X + 105.0         # rear panel face behind the number plate (D: P11b, profile photo 29)
REAR_PANEL_LOW_Z = CL.GROUND_Z + 300.0   # lower edge of the rear valance (D)
SILL_Y = 600.0                           # |y| of the inner sill faces (D, outside every P11a part)


def toe_z(x):
    """Toe board underside height at x between the floor and the bulkhead."""
    (x0, z0), (x1, z1) = TOE_FOOT, TOE_TOP
    if x <= x0:
        return z0
    if x >= x1:
        return z1
    return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
