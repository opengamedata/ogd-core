# import standard libraries
from enum import IntEnum

class IDMode(IntEnum):
    SESSION = 1
    PLAYER = 2

    def __str__(self):
        if self.value == 1:
            return "Session"
        elif self.value == 2:
            return "Player"
        else:
            raise ValueError("Invalid IDMode value!")
