import abc
import pandas as pd
from typing import Any, Dict, IO, List, Tuple, Union
## import local files
from interfaces.DataInterface import DataInterface
from GameTable import GameTable
from schemas.Schema import Schema

class CSVInterface(DataInterface):
    def __init__(self, game_id:str, filepath_or_buffer:Union[str, IO[bytes]], delim:str = ','):
        # set up data from params
        super().__init__(game_id=game_id)
        self._file      : Union[str, IO[bytes]] = filepath_or_buffer
        self._delimiter : str = delim
        # set up data from file
        self._data      : Union[pd.DataFrame, None] = None

    def Open(self, force_reopen:bool = False) -> bool:
        if force_reopen or not self.IsOpen():
            self._data = pd.read_csv(filepath_or_buffer=self._file, delimiter=self._delimiter, parse_dates=['server_time', 'client_time'])
            self._is_open = True
        return True

    def Close(self) -> bool:
        self._is_open = False
        return True

    @abc.abstractmethod
    def _retrieveFromIDs(self, id_list: List[int]) -> List:
        if self.IsOpen():
            return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
        else:
            return []

    @abc.abstractmethod
    def _IDsFromDates(self, min, max):
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:typing.List[int]):
        pass