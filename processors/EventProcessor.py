# import libraries
import json
from datetime import datetime
from typing import List, Type, Optional
# import locals
from processors.Processor import Processor
from schemas.Event import Event
from schemas.games.GameSchema import GameSchema
from utils.utils import ExportRow

class EventProcessor(Processor):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema:GameSchema):
        super().__init__(game_schema=game_schema)
        self._events : List[Event] = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _processEvent(self, event:Event):
        self._events.append(event)

    def _getLines(self) -> List[ExportRow]:
        return [_event.ColumnValues() for _event in self._events]

    def _clearLines(self) -> None:
        self._events = []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
