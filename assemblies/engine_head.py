"""Cylinder head assembly, Haynes Fig 1.6.

P0 holds a single inlet valve so the pipeline can be proven end to end.
P1 adds every Fig 1.6 legend item, placed by mating frames.
"""
from build123d import Location

ID = "engine.head"
NAME = "Cylinder head"
PARENT = "engine"
HAYNES = {"figures": [{"figure": "1.6"}, {"figure": "1.9"}], "section": 12}

# (instance id, part id, location). Removal order lives on each part's spec.
INSTANCES = [
    ("engine.head.valve-inlet#1", "engine.head.valve-inlet", Location((0, 0, 0))),
]
