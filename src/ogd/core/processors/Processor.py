## import standard libraries
import abc
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Type, Optional
# import locals
from ogd.core.models.FeatureData import FeatureData
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.models.Event import Event
from ogd.core.utils.utils import ExportRow, Logger

## @class Processor
class Processor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _processEvent(self, event:Event) -> None:
        pass

    @abc.abstractmethod
    def _getLines(self) -> List[ExportRow]:
        pass

    @abc.abstractmethod
    def _clearLines(self) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, game_schema: GameSchema):
        self._game_schema : GameSchema = game_schema

    def __str__(self):
        return f"Processor object for {self._game_schema.GameName} data"

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessEvent(self, event:Event) -> None:
        # TODO: add error handling code, if applicable.
        self._processEvent(event=event)
    
    @property
    def Lines(self) -> List[ExportRow]:
        ret_val : List[ExportRow] = []

        # TODO: Should do list of events instead, and put it on outerface to do this part.
        # When retrieving lines, ensure all lines have values in appropriate format for output to file/web response/whatever.
        _dumps_default = lambda x : x.isoformat() if isinstance(x, datetime) else str(x)
        ret_val = [[json.dumps(_col, default=_dumps_default) for _col in _line] for _line in self._getLines()]

        return ret_val

    def ClearLines(self):
        self._clearLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
