"""Wiring: Instruments. Ignition warning lamp feed, voltage stabiliser and the fuel gauge to the tank unit. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-instruments"
NAME = "Wiring: Instruments"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
