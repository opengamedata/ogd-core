import abc
import pandas as pd
from datetime import datetime
from typing import Any, Dict, IO, List, Tuple, Union
## import local files
from interfaces.DataInterface import DataInterface
from schemas.Schema import Schema

class CSVInterface(DataInterface):
    def __init__(self, game_id:str, filepath_or_buffer:Union[str, IO[bytes]], delim:str = ','):
        # set up data from params
        super().__init__(game_id=game_id)
        self._file      : Union[str, IO[bytes]] = filepath_or_buffer
        self._delimiter : str = delim
        # set up data from file
        self._data      : pd.DataFrame = pd.DataFrame()

    def Open(self, force_reopen:bool = False) -> bool:
        if force_reopen or not self.IsOpen():
            self._data = pd.read_csv(filepath_or_buffer=self._file, delimiter=self._delimiter, parse_dates=['server_time', 'client_time'])
            self._is_open = True
        return True

    def Close(self) -> bool:
        self._is_open = False
        return True

    def _retrieveFromIDs(self, id_list: List[int]) -> List[Tuple]:
        if self.IsOpen() and self._data != None:
            return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
        else:
            return []

    def _IDsFromDates(self, min:datetime, max:datetime) -> List[int]:
        if not self._data.empty:
            return list(self._data.loc[self._data['server_time'] > min and self._data['server_time'] < max, ['session_id']])
        else:
            return []

    def _datesFromIDs(self, id_list:List[int]) -> Dict[str, datetime]:
        min_date = self._data.loc[self._data['session_id'] in id_list, ['server_time']].min
        max_date = self._data.loc[self._data['session_id'] in id_list, ['server_time']].max
        return {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}