# import standard libraries
from enum import IntEnum

class ExtractionMode(IntEnum):
    """Simple enum to represent the different levels of granularity at which extractions can be carried out:
    Session, Player, Population, or Detector.
    """
    SESSION = 1
    PLAYER = 2
    POPULATION = 3
    DETECTOR = 4

    def __str__(self):
        return self.name
