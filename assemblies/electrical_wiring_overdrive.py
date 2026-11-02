"""Wiring: Overdrive. Facia switch, relay, throttle (vacuum) switch, gearbox switch and solenoid (Haynes Fig 6.19). Haynes Fig 6.19. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-overdrive"
NAME = "Wiring: Overdrive"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "6.19"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
