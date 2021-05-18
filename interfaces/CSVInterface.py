import abc
import typing
import pandas as pd
## import local files
from interfaces.DataInterface import DataInterface
from GameTable import GameTable
from schemas.Schema import Schema

class CSVInterface(DataInterface):
    # TODO: Take a path, rather than an existing dataframe.
    def __init__(self, game_id: str, data_frame: pd.DataFrame):
        super().__init__(self, game_id=game_id)
        self._data = data_frame

    def RetrieveSliceData(self, id_list) -> typing.List[typing.Tuple]:
        return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))