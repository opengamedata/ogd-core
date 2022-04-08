## import standard libraries
import json
import logging
from typing import Any, List, Type, Union
## import local files
from detectors.DetectorRegistry import DetectorRegistry
from features.FeatureLoader import FeatureLoader
from games.LAKELAND.LakelandLoader import LakelandLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from utils import Logger

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    ## Constructor for the EventProcessor class.
    #  Stores some of the passed data, and generates some other members.
    #  In particular, generates a mapping from column names back to indices of columns in the
    #  events csv.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param events_csv_file The output file, to which we'll write the event game data.
    def __init__(self, LoaderClass:Type[FeatureLoader], game_schema: GameSchema,
                 feature_overrides:Union[List[str],None]=None):
        # define instance vars
        self._lines       : List[str]        = []
        self._columns     : List[str]        = Event.ColumnNames()
        self._registry    : DetectorRegistry = DetectorRegistry()

        self._game_schema : GameSchema            = game_schema
        self._overrides   : Union[List[str],None] = feature_overrides
        self._LoaderClass : Type[FeatureLoader]   = LoaderClass
        self._loader      : FeatureLoader         = self._prepareLoader()
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
            if type(col) == str:
                col_values[i] = f"\"{col}\""
            elif type(col) == dict:
                col_values[i] = json.dumps(col)
        # event.event_data = json.dumps(event.event_data)
        self._lines.append(separator.join([str(item) for item in col_values]) + "\n") # changed , to \t
        # Logger.Log(f"Got event: {str(event)}")

    def GetColumnNames(self) -> List[str]:
        return self._columns

    def GetLines(self) -> List[str]:
        return self._lines

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing {len(self._lines)} entries from EventManager.", logging.DEBUG)
        self._lines = []

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id="EventManager", session_id="EventManager", game_schema=self._game_schema, feature_overrides=self._overrides, output_file=None)
        else:
            ret_val = self._LoaderClass(player_id="EventManager", session_id="EventManager", game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val
