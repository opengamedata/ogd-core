# import standard libraries
from enum import IntEnum

class ExportMode(IntEnum):
    SESSION = 1
    PLAYER = 2
    POPULATION = 3
    EVENTS = 4
    DETECTORS = 5

    def __str__(self):
        return self.name
