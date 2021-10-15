## import standard libraries
import json
import logging
from typing import Any, List, Tuple, Union
## import local files
import utils
from managers.FileManager import FileManager
from schemas.Event import Event
from schemas.TableSchema import TableSchema

## @class EventProcessor
#  Class to manage data for a csv events file.
class EventProcessor:
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
        self._lines        : List[str]      = []
        self._columns      : List[str]      = Event.ColumnNames()

    ## Function to handle processing one row of data.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessRow(self, row_with_complex_parsed: Tuple, schema:TableSchema):
        row_columns = schema.ColumnNames()
        line : List[Any] = [None] * len(row_columns)
        for i,col in enumerate(row_with_complex_parsed):
            # only set a value if this was not the remote address (IP) column.
            if row_columns[i] != "remote_addr":
                if type(col) == str:
                    line[i] = f"\"{col}\""
                elif type(col) == dict:
                    line[i] = json.dumps(col)
                else:
                    line[i] = col
        # print(f"From EventProcessor, about to add event to lines: {[str(item) for item in line]}")
        self._lines.append("\t".join([str(item) for item in line]) + "\n") # changed , to \t

    def ProcessEvent(self, event:Event, separator:str = "\t"):
        self._lines.append(separator.join([str(item) for item in event.ColumnValues()]) + "\n") # changed , to \t
        # utils.Logger.toStdOut(f"Got event: {str(event)}")

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing {len(self._lines)} entries from EventProcessor.", logging.DEBUG)
        self._lines = []

    ## Function to write out the header for a events csv file.
    def WriteEventsCSVHeader(self, file_mgr:FileManager, separator:str = "\t"):
        file_mgr.GetEventsFile().write(separator.join(self._columns) + "\n")

    ## Function to write out all lines of event data that have been parsed so far.
    def WriteEventsCSVLines(self, file_mgr:FileManager):
        file_mgr.GetEventsFile().writelines(self._lines)