"""Road wheels (P9): 4 1/2J x 14 centre-lock wire wheels, 5.60-14 crossply tyres, two-eared knock-on spinners.

Wheel frame (WF): origin on the wheel axis at the start of the hub's inner cone (front: front_suspension_layout
EXT_COLLAR_Y[0]; rear: rear_axle_layout EXT_COLLAR_Y[0]), local +y outboard along the axis, x forward, z up. The
same wheel sits on all four hubs: the front hubs' cone, splines and thread stations were set to match the rear hub
extensions (P7). Right-hand wheels are the same part turned half round the vertical axis.

What is fixed: rim 4 1/2J x 14 and tyre 5.60 x 14 tubed crossply on early cars (Haynes Ch 11 specifications, printed
p203; tyre pressures 18-19 front, 18-22 rear lbf/in2); 60-spoke centre-lock wheels, painted aluminium on early
cars, chrome from October 1965 (MGOC Spares "MGB OE steel & wire wheels"); 42 mm series splines and 12 tpi spinner
threads to GHN3-30850, left-hand threads on the car's right-hand side (MGOC). Rim contour: the J flange (17.5 mm)
and 14 in bead seat diameter are the standard (ETRTO/TRA) figures for a J rim.

Derived (D): the hub shell's flanges, the spoke lacing (inner flange to the rim's outer row, outer flange to the
inner row, alternately leading and trailing, tangential), the drop centre, the tyre's section shape (5.60 in
section, 92 % profile as car_layout) and tread pattern (zig-zag ribs in the manner of the period Dunlop crossply),
the spinner's size.
"""
from __future__ import annotations

from mgb import car_layout as CL, front_suspension_layout as FS, rear_axle_layout as A

IN = 25.4

# ---- placing: wheel frame origin per corner (y of the hub's inner cone start, |y|) ------------------------------------
FRONT_SEAT_Y = FS.EXT_COLLAR_Y[0]
REAR_SEAT_Y = A.EXT_COLLAR_Y[0]
CENTRE_PLANE = FS.WHEEL_PLANE_Y - FS.EXT_COLLAR_Y[0]   # 10.5: wheel centre plane, local y

# ---- rim (4 1/2J x 14) -------------------------------------------------------------------------------------------------
RIM_W = 4.5 * IN                          # between the flanges' inner faces
BEAD_R = 14.0 * IN / 2                    # bead seat radius
FLANGE_H = 17.5                           # J flange height
RIM_T = 2.6
WELL_R = BEAD_R - 19.0                    # drop centre floor
WELL_W = 46.0
NIPPLE_R = WELL_R - RIM_T                 # where the spoke nipples seat, inside the well
VALVE_ANGLE = 3.0                         # valve hole between two spokes (deg from up, toward the front)

# ---- hub shell and spokes ------------------------------------------------------------------------------------------------
SHELL_Y = (2.5, A.EXT_THREAD_Y[0] - A.EXT_COLLAR_Y[0] - 1.0)   # shell from the inner cone to the outer cone
INNER_CONE_R = A.EXT_CONE_R               # (33.0 at local y 5, 27.5 at y 25) - as the hubs' cones
SPLINE = A.EXT_SPLINE                     # 36 x 42 mm series
SPLINE_Y = (A.EXT_SPLINE_Y[0] - A.EXT_COLLAR_Y[0], A.EXT_SPLINE_Y[1] - A.EXT_COLLAR_Y[0])
INNER_FLANGE = (30.0, 56.0)               # (local y, radius) of the inboard spoke flange, outboard of the hub's studs
OUTER_FLANGE = (78.0, 46.0)
SPOKES = 60
SPOKE_D = 0.128 * IN                      # 10 SWG
RIM_ROWS = (CENTRE_PLANE + 9.0, CENTRE_PLANE - 9.0)   # outer row (inner flange spokes), inner row (outer flange spokes)
LACE_ANGLE = 30.0                         # tangential offset of a spoke's hub end from its rim hole (deg)

# ---- tyre (5.60-14 crossply) ---------------------------------------------------------------------------------------------
TYRE_R = CL.TYRE_D / 2                    # 308.7 overall radius (unladen)
SECTION_W = 5.60 * IN
TREAD_W = 104.0
TREAD_DEPTH = 7.0
TREAD_PITCHES = 72
TREAD_RIBS = 5

# ---- spinner (two-eared knock-on) -----------------------------------------------------------------------------------------
SPINNER_Y = (SHELL_Y[1] - 4.0, A.EXT_END_Y - A.EXT_COLLAR_Y[0] + 3.0)   # boss from the shell's outer cone past the thread
SPINNER_SPAN = 7.0 * IN                   # ear tip to ear tip
SPINNER_BOSS_R = 33.0
