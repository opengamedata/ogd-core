
## import standard libraries
import logging
import math
import re
import typing
## import local libraries
from models.SequenceModel import SequenceModel

## @class LogisticModel
class NthEventModel(SequenceModel):
    def __init__(self, n: int, levels: typing.List[int] = []):
        super().__init__(levels)
        self._n = n

    def _eval(self, rows: typing.List[typing.Dict[str, typing.Any]]) -> typing.Any:
        return rows[self._n]