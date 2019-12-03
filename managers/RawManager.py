## import standard libraries
import json
import logging
import typing
## import local files
import utils
import GameTable
from schemas.Schema import Schema

## @class RawManager
#  Class to manage data for a raw csv file.
class RawManager:
    ## Constructor for the RawManager class.
    #  Stores some of the passed data, and generates some other members.
    #  In particular, generates a list of all columns after splitting out JSON
    #  data, and a mapping from column names back to indices of columns in the
    #  raw csv.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param proc_csv_file The output file, to which we'll write the raw game data.
    def __init__(self, game_table: GameTable, game_schema: Schema,
                 raw_csv_file: typing.IO.writable):
        # define instance vars
        self._lines             : typing.List[typing.List] = []
        self._game_table        : GameTable           = game_table
        self._raw_file          : typing.IO.writable  = raw_csv_file
        self._db_columns        : typing.List[str]    = game_schema.db_columns()
        self._JSON_columns      : typing.List[str]
        self._all_columns       : typing.List[str]
        self._columns_to_indices: typing.Dict
        # set instance vars
        self._JSON_columns = RawManager._generateJSONColumns(game_schema)
        self._all_columns = game_table.column_names[:game_table.complex_data_index] \
                          + self._JSON_columns \
                          + game_table.column_names[game_table.complex_data_index+1:]
        # Not the nicest thing ever, but this function creates a dictionary that maps column names
        # to indices, so we can store each line for raw csv as a list with guaranteed consistent order.
        self._columns_to_indices = {name:index for index,name in enumerate(self._all_columns)}

    ## Function to handle processing one row of data.
    #  Data is handled in three cases: data that goes before event_data_custom,
    #  data that goes after, and event_data_custom itself.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessRow(self, row_with_complex_parsed: typing.Tuple):
        line = [None] * len(self._all_columns)
        for i,col in enumerate(row_with_complex_parsed):
            # So, I'm only using columns_to_indices for the JSON stuff,
            # since the other stuff comes in tuples, which have a consistent order.
            # A little inconsistent, but... whatever.
            # I don't know of a good way to get column names with the other row data.
            if i < self._game_table.complex_data_index:
                line[i] = f"\"{col}\"" if type(col) == str else col
            elif i > self._game_table.complex_data_index:
                index = i + len(self._JSON_columns) - 1
                line[index] = f"\"{col}\"" if type(col) == str else col
            else: # must be at complex_data_index, so process all its columns.
                complex_data_parsed = row_with_complex_parsed[self._game_table.complex_data_index]
                for key in complex_data_parsed.keys():
                    try:
                        index = self._columns_to_indices[key]
                    except KeyError as e:
                        utils.Logger.err_logger(f'{e}: Key error because {key} of {row_with_complex_parsed} is not in the SCHEMA',logging.WARNING)
                        continue
                    item = complex_data_parsed[key]
                    line[index] = f"\"{str(item)}\"" if (type(item) == type({}) or type(item) == str) else item

        self._lines.append(",".join([str(item) for item in line]) + "\n")

    ## Function to empty the list of lines stored by the RawManager.
    #  This is helpful if we're processing a lot of data and want to avoid
    #  Eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing {len(self._lines)} entries from RawManager.", logging.DEBUG)
        self._lines = []

    ## Function to write out the header for a raw csv file.
    def WriteRawCSVHeader(self):
        self._raw_file.write(",".join(self._all_columns) + "\n")

    ## Function to write out all lines of raw data that have been parsed so far.
    def WriteRawCSVLines(self):
        for line in self._lines:
            self._raw_file.write(line)

    ## Private helper function to construct a list of all possible JSON columns
    #  for the given game.
    #  @param game_schema A dictionary that defines how the game data is structured.
    #                     This includes a list of all possible events, and the
    #                     names of their member variables.
    # @return A list of all distinct column names from the game's event types.
    @staticmethod
    def _generateJSONColumns(game_schema: Schema):
        JSON_columns = []
        for event_type in game_schema.event_types():
            JSON_columns.extend([col for col in game_schema.events()[event_type].keys() if col not in JSON_columns])
        return JSON_columns