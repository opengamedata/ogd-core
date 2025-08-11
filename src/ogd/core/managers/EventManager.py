## import standard libraries
import logging
from typing import Callable, List, Type, Optional
## import local files
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.DetectorProcessor import DetectorProcessor
from ogd.core.processors.EventProcessor import EventProcessor
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.EventSet import EventSet
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    def __init__(self, game_schema:GameStoreConfig, trigger_callback:Callable[[Event], None],
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

    def ProcessEvent(self, event:Event) -> None:
        self._all_events.ProcessEvent(event=event)
        if event.EventSource == EventSource.GAME:
            self._raw_events.ProcessEvent(event=event)
        if self._detector_processor is not None:
            self._detector_processor.ProcessEvent(event=event)

    @property
    def ColumnNames(self) -> List[str]:
        return self._columns

    @property
    def GameEvents(self) -> EventSet:
        return self._raw_events.Events
    @property
    def GameLines(self) -> List[ExportRow]:
        return self._raw_events.Lines

    @property
    def AllEvents(self) -> EventSet:
        return self._all_events.Events
    @property
    def AllLines(self) -> List[ExportRow]:
        return self._all_events.Lines

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing {len(self._raw_events.Lines)} raw event and {len(self._all_events.Lines)} processed event entries from EventManager.", logging.DEBUG, depth=2)
        self._raw_events.ClearLines()
        self._all_events.ClearLines()
