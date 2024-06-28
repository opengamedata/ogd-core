# import libraries
import json
from datetime import datetime
from typing import List, Type, Optional
# import locals
from ogd.core.processors.Processor import Processor
from ogd.core.models.Event import Event
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.utils import ExportRow

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
