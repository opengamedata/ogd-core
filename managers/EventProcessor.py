## import standard libraries
import json
import logging
import typing
from typing import List, Tuple, Union
## import local files
import utils
from schemas.TableSchema import TableSchema
from schemas.Schema import Schema

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
    def __init__(self, game_table: TableSchema, game_schema: Schema,
                  events_csv_file: typing.IO[str]):
        # define instance vars
        self._lines             : List[str]      = []
        self._game_table        : TableSchema    = game_table
        self._events_file       : typing.IO[str] = events_csv_file
        self._db_columns        : List[str]      = game_schema.db_columns()

    ## Function to handle processing one row of data.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessRow(self, row_with_complex_parsed: Tuple):
        line : List[typing.Any] = [None] * len(self._db_columns)
        for i,col in enumerate(row_with_complex_parsed):
            # only set a value if this was not the remote address (IP) column.
            if i != self._game_table.remote_addr_index:
                if type(col) == str:
                    line[i] = f"\"{col}\""
                elif type(col) == dict:
                    line[i] = json.dumps(col)
                else:
                    line[i] = col
        self._lines.append("\t".join([str(item) for item in line]) + "\n") # changed , to \t

    ## Function to empty the list of lines stored by the EventProcessor.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing {len(self._lines)} entries from EventProcessor.", logging.DEBUG)
        self._lines = []

    ## Function to write out the header for a events csv file.
    def WriteEventsCSVHeader(self):
        self._events_file.write("\t".join(self._db_columns) + "\n")# changed , to \t

    ## Function to write out all lines of event data that have been parsed so far.
    def WriteEventsCSVLines(self):
        for line in self._lines:
            self._events_file.write(line)