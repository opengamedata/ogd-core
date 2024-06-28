# import standard libraries
from enum import IntEnum

class IDMode(IntEnum):
    SESSION = 1
    USER = 2
    GAME = 3

    def __str__(self):
        return self.name
