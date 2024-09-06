# import standard libraries
from enum import IntEnum

class IterationMode(IntEnum):
    """Simple enum to represent the different kinds of extractor iteration:
    Aggregate (no iteration) or Per-Count (iterated by count)
    """
    AGGREGATE = 1
    PERCOUNT = 2

    def __str__(self):
        return self.name
