"""Wiring loom coverings (P10b): braided sleeving over the harness runs and the bulkhead grommet. The
wires inside are the electrical.wiring-* assemblies (one per circuit); hide this assembly, or a sleeve,
to see them. Haynes Fig 10.26."""
from mgb.wiring_assembly import instances

ID = "electrical.loom"
NAME = "Wiring loom: sleeving and grommet"
PARENT = "electrical"
HAYNES = {"figures": [{"figure": "10.26"}], "section": 1}
GROUPS = {}
INSTANCES = instances(ID)
