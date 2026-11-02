"""Wiring: Lighting. Headlamps (through the foot dip switch), side, tail, number plate, panel and map lamps. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-lighting"
NAME = "Wiring: Lighting"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
