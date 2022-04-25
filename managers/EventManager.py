## import standard libraries
import json
import logging
from datetime import datetime
from typing import Any, List, Type, Union
## import local files
from detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from games.LAKELAND.LakelandLoader import LakelandLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from utils import Logger

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    def __init__(self, LoaderClass:Type[ExtractorLoader], game_schema: GameSchema,
                 feature_overrides:Union[List[str],None]=None):
        """Constructor for EventManager.
        Just creates empty list of lines and generates list of column names.
        """
        # define instance vars
        self._lines       : List[str]        = []
        self._columns     : List[str]        = Event.ColumnNames()
        self._registry    : DetectorRegistry = DetectorRegistry()
        self._game_schema : GameSchema            = game_schema
        self._overrides   : Union[List[str],None] = feature_overrides
        self._LoaderClass : Type[ExtractorLoader]   = LoaderClass
        self._loader      : ExtractorLoader         = self._prepareLoader()
        self._loader.LoadToDetectorRegistry(registry=self._registry, trigger_callback=self.ReceiveEventTrigger)
        self._debug_count : int                   = 0

    def ReceiveEventTrigger(self, event:Event) -> None:
        if self._debug_count < 20:
            Logger.Log("EventManager received an event trigger.", logging.DEBUG)
            self._debug_count += 1
        self.ProcessEvent(event=event, separator='\t')

    def ProcessEvent(self, event:Event, separator:str = "\t") -> None:
        self._registry.ExtractFromEvent(event=event)
        col_values = event.ColumnValues()
        for i,col in enumerate(col_values):
            # TODO: double-check if the remote_addr is there to be dropped/ignored.
            # if row_columns[i] != "remote_addr":
            if type(col) == str:
                col_values[i] = f"\"{col}\""
            elif type(col) == dict:
                col_values[i] = json.dumps(col)
        # event.event_data = json.dumps(event.event_data)
        self._lines.append(separator.join([str(item) for item in col_values]) + "\n") # changed , to \t

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
        Logger.Log(f"Clearing {len(self._lines)} entries from EventManager.", logging.DEBUG)
        self._lines = []

    def _prepareLoader(self) -> ExtractorLoader:
        ret_val : ExtractorLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id="EventManager", session_id="EventManager", game_schema=self._game_schema, feature_overrides=self._overrides, output_file=None)
        else:
            ret_val = self._LoaderClass(player_id="EventManager", session_id="EventManager", game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val
