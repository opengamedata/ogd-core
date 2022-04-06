## import standard libraries
import json
import logging
from typing import Any, List, Tuple, Union
## import local files
from detectors.DetectorRegistry import DetectorRegistry
from schemas.Event import Event
from schemas.TableSchema import TableSchema
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
    def __init__(self):
        # define instance vars
        self._lines        : List[str]    = []
        self._columns      : List[str]    = Event.ColumnNames()
        self._registry : DetectorRegistry = DetectorRegistry()

    def ReceiveEventTrigger(self, event:Event):
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
        Logger.Log(f"Clearing {len(self._lines)} entries from EventProcessor.", logging.DEBUG)
        self._lines = []