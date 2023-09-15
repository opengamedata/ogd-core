# import standard libraries
from enum import IntEnum

class IterationMode(IntEnum):
    AGGREGATE = 1
    PERCOUNT = 2

    def __str__(self):
        return self.name
