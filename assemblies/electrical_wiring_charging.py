"""Wiring: Charging (18ACR alternator). Wiring, wire by wire: the 18ACR conversion's charging leads, the charging junction and the warning lamp connector. Haynes Fig 10.26. Each wire is its own part: select one to see its
colour code, size, circuit and both terminals; isolate this assembly to trace the circuit."""
from mgb.wiring_assembly import instances

ID = "electrical.wiring-charging"
NAME = "Wiring: Charging (18ACR alternator)"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
