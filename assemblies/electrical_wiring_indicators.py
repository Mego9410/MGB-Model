"""Wiring: Indicators and stop lamps. Flasher unit, column switch, indicator warning arrows, front and rear flashers, stop lamp switch and stop lamps. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-indicators"
NAME = "Wiring: Indicators and stop lamps"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
