## import standard libraries
import json
import logging
from datetime import datetime
from typing import Any, Callable, List, Type, Optional, Set
## import local files
from ogd.core.registries.DetectorRegistry import DetectorRegistry
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.DetectorProcessor import DetectorProcessor
from ogd.core.processors.EventProcessor import EventProcessor
from ogd.core.models.Event import Event, EventSource
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils import utils
from ogd.core.utils.Logger import Logger
from ogd.core.utils.utils import ExportRow

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    def __init__(self, game_schema: GameSchema, trigger_callback:Callable[[Event], None],
                 LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]=None):
        """Constructor for EventManager.
        Just creates empty list of lines and generates list of column names.
        """
        # define instance vars
        self._columns     : List[str]      = Event.ColumnNames()
        self._raw_events  : EventProcessor = EventProcessor(game_schema=game_schema)
        self._all_events  : EventProcessor = EventProcessor(game_schema=game_schema)
        self._detector_processor : Optional[DetectorProcessor] = None
        if LoaderClass is not None:
            self._detector_processor = DetectorProcessor(game_schema=game_schema,           LoaderClass=LoaderClass,
                                                         trigger_callback=trigger_callback, feature_overrides=feature_overrides)

    def ProcessEvent(self, event:Event, separator:str = "\t") -> None:
        # event.EventData = json.dumps(event.EventData)
        # TODO: double-check if the remote_addr is there to be dropped/ignored.
        self._all_events.ProcessEvent(event=event)
        if event.EventSource == EventSource.GAME:
            self._raw_events.ProcessEvent(event=event)
        if self._detector_processor is not None:
            self._detector_processor.ProcessEvent(event=event)

    def GetColumnNames(self) -> List[str]:
        return self._columns

    def GetRawLines(self, slice_num:int, slice_count:int) -> List[ExportRow]:
        start   : datetime = datetime.now()
        ret_val : List[Any] = self._raw_events.Lines
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve raw Event lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetAllLines(self, slice_num:int, slice_count:int) -> List[ExportRow]:
        start   : datetime = datetime.now()
        ret_val : List[Any] = self._all_events.Lines
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve all Event lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing {len(self._raw_events.Lines)} raw event and {len(self._all_events.Lines)} processed event entries from EventManager.", logging.DEBUG, depth=2)
        self._raw_events.ClearLines()
        self._all_events.ClearLines()
