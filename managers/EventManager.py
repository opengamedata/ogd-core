## import standard libraries
import json
import logging
from datetime import datetime
from typing import Any, Callable, List, Type, Optional
## import local files
from detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from processors.EventProcessor import EventProcessor
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from utils import Logger

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    def __init__(self, LoaderClass:Type[ExtractorLoader], game_schema: GameSchema,
                 trigger_callback:Callable[[Event], None], feature_overrides:Optional[List[str]]=None):
        """Constructor for EventManager.
        Just creates empty list of lines and generates list of column names.
        """
        # define instance vars
        self._lines       : List[str]        = []
        self._columns     : List[str]        = Event.ColumnNames()
        self._processor   : EventProcessor   = EventProcessor(LoaderClass=LoaderClass,           game_schema=game_schema,
                                                              trigger_callback=trigger_callback, feature_overrides=feature_overrides)

    def ProcessEvent(self, event:Event, separator:str = "\t") -> None:
        col_values = event.ColumnValues()
        for i,col in enumerate(col_values):
            # TODO: double-check if the remote_addr is there to be dropped/ignored.
            # if row_columns[i] != "remote_addr":
            if type(col) == str:
                col_values[i] = f"\"{col}\""
            elif type(col) == dict:
                col_values[i] = json.dumps(col)
        # event.EventData = json.dumps(event.EventData)
        self._lines.append(separator.join([str(item) for item in col_values]) + "\n") # changed , to \t
        self._processor.ProcessEvent(event=event)

    def GetColumnNames(self) -> List[str]:
        return self._columns

    def GetLines(self, slice_num:int, slice_count:int) -> List[str]:
        start   : datetime = datetime.now()
        ret_val : List[str] = self._lines
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Event lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing {len(self._lines)} entries from EventManager.", logging.DEBUG, depth=2)
        self._lines = []
