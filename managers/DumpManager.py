## import standard libraries
import json
import logging
import typing
## import local files
import utils
import GameTable
from schemas.Schema import Schema

## @class DumpManager
#  Class to manage data for a csv dump file.
class DumpManager:
    ## Constructor for the DumpManager class.
    #  Stores some of the passed data, and generates some other members.
    #  In particular, generates a mapping from column names back to indices of columns in the
    #  dump csv.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param dump_csv_file The output file, to which we'll write the dumped game data.
    def __init__(self, game_table: GameTable, game_schema: Schema,
                 dump_csv_file: typing.IO.writable):
        # define instance vars
        self._lines             : typing.List[typing.List] = []
        self._game_table        : GameTable           = game_table
        self._dump_file         : typing.IO.writable  = dump_csv_file
        self._db_columns        : typing.List[str]    = game_schema.db_columns()

    ## Function to handle processing one row of data.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessRow(self, row_with_complex_parsed: typing.Tuple):
        line = [None] * len(self._db_columns)
        for i,col in enumerate(row_with_complex_parsed):
            # only set a value if this was not the remote address (IP) column.
            if i != self._game_table.remote_addr_index:
                line[i] = f"\"{col}\"" if type(col) == str else col
        self._lines.append("\t".join([str(item) for item in line]) + "\n") # changed , to \t

    ## Function to empty the list of lines stored by the DumpManager.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing {len(self._lines)} entries from DumpManager.", logging.DEBUG)
        self._lines = []

    ## Function to write out the header for a dump csv file.
    def WriteDumpCSVHeader(self):
        self._dump_file.write("\t".join(self._db_columns) + "\n")# changed , to \t

    ## Function to write out all lines of dumped data that have been parsed so far.
    def WriteDumpCSVLines(self):
        for line in self._lines:
            self._dump_file.write(line)