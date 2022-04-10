## import standard libraries
import json
import logging
from typing import Any, List, Tuple, Union
## import local files
from utils import Logger
from schemas.Event import Event
from schemas.TableSchema import TableSchema

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventManager:
    def __init__(self):
        """Constructor for EventManager.
        Just creates empty list of lines and generates list of column names.
        """
        # define instance vars
        self._lines        : List[str]      = []
        self._columns      : List[str]      = Event.ColumnNames()

    def ProcessEvent(self, event:Event, separator:str = "\t") -> None:
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

    def GetLines(self) -> List[str]:
        return self._lines

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing {len(self._lines)} entries from EventProcessor.", logging.DEBUG)
        self._lines = []