import typing
import GameTable
from schemas.Schema import Schema

## Class to manage data for a raw csv file.
class RawManager:
    def __init__(self: RawManager, db_columns: typing.List[str], game_table: GameTable, game_schema: Schema, complex_data_index: int):
        ## define instance vars
        self._lines:              typing.List[typing.List]
        self._db_columns:         typing.List[str]
        self._JSON_columns:       typing.List[str]
        self._all_columns:       typing.List[str]
        self._columns_to_indices: typing.Dict
        ## set instance vars
        self._lines = []
        self._db_columns = db_columns
        self._JSON_columns = RawManager._generateJSONColumns(game_schema)
        self._all_columns = game_table.column_names[:game_table.complex_data_index] + list(self._JSON_columns) + game_table.column_names[game_table.complex_data_index:]
        ## Not the nicest thing ever, but this function creates a dictionary that maps column names
        ## to indices, so we can store each line for raw csv as a list with guaranteed consistent order.
        self._columns_to_indices = {name:index for index,name in enumerate(self._JSON_columns)}

    @staticmethod
    def _generateJSONColumns(game_schema: Schema):
        JSON_column_set = {}
        for event_type in game_schema.event_types():
            JSON_column_set |= game_schema.events()[event_type].keys()
        return JSON_column_set
        