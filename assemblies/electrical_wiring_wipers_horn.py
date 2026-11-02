"""Wiring: Wipers, horns and heater. Wiper motor and switch, the horns and horn push lead, and the heater blower switch. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-wipers-horn"
NAME = "Wiring: Wipers, horns and heater"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
