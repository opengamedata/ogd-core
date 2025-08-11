# import libraries
import logging
from datetime import datetime
from typing import List
# import locals
from ogd.core.processors.Processor import Processor
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.models.Event import Event
from ogd.common.models.EventSet import EventSet
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.utils.typing import ExportRow
from ogd.common.utils.Logger import Logger

class EventProcessor(Processor):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema:GameStoreConfig, filters:DatasetFilterCollection=DatasetFilterCollection()):
        super().__init__(game_schema=game_schema)
        self._events : EventSet = EventSet(events=[], filters=filters)

    @property
    def Events(self) -> EventSet:
        return self._events

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _processEvent(self, event:Event):
        self._events.Events.append(event)

    def _getLines(self) -> List[ExportRow]:
        ret_val : List[ExportRow]

        start   = datetime.now()
        ret_val = [_event.ColumnValues for _event in self._events.Events]
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Event lines: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)

        return ret_val

    def _clearLines(self) -> None:
        self._events = EventSet(events=[], filters=DatasetFilterCollection())

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
