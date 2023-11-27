# import standard libraries
from enum import IntEnum

class ExtractionMode(IntEnum):
    SESSION = 1
    PLAYER = 2
    POPULATION = 3
    DETECTOR = 4

    def __str__(self):
        return self.name
