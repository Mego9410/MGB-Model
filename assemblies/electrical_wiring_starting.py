"""Wiring: Starting, ignition and supplies. Battery and starter cables, the ignition switch feeds, the coil and distributor leads, the fused supply joints and the fuel pump leads. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-starting"
NAME = "Wiring: Starting, ignition and supplies"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
