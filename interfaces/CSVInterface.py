import logging
from utils import Logger
import pandas as pd
from datetime import datetime
from typing import Any, Dict, IO, List, Tuple, Union
from pandas.io.parsers import TextFileReader
## import local files
from interfaces.DataInterface import DataInterface
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

class CSVInterface(DataInterface):
    def __init__(self, game_id:str, filepath_or_buffer:Union[str, IO[bytes]], delim:str = ','):
        # set up data from params
        super().__init__(game_id=game_id)
        self._file      : Union[str, IO[bytes]] = filepath_or_buffer
        self._delimiter : str = delim
        # set up data from file
        self._data      : pd.DataFrame = pd.DataFrame()

    def _open(self) -> bool:
        try:
            self._data = pd.read_csv(filepath_or_buffer=self._file, delimiter=self._delimiter, parse_dates=['server_time', 'client_time'])
            self._is_open = True
            return True
        except FileNotFoundError as err:
            Logger.Log(f"Could not find file {self._file}.", logging.ERROR)
            return False

    def _close(self) -> bool:
        self._is_open = False
        return True

    def _allIDs(self) -> List[str]:
        return self._data['session_id'].unique().tolist()

    def _fullDateRange(self) -> Dict[str,datetime]:
        min_time = pd.to_datetime(self._data['server_time'].min())
        max_time = pd.to_datetime(self._data['server_time'].max())
        return {'min':min_time, 'max':max_time}

    def _rowsFromIDs(self, id_list: List[str], versions: Union[List[int],None]=None) -> List[Tuple]:
        if self.IsOpen() and self._data != None:
            return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
        else:
            return []

    def _IDsFromDates(self, min:datetime, max:datetime, versions: Union[List[int],None]=None) -> List[str]:
        if not self._data.empty:
            server_times = pd.to_datetime(self._data['server_time'])
            if versions is not None and versions is not []:
                mask = self._data.loc[(server_times >= min) & (server_times <= max) & (self._data['app_version'].isin(versions))]
            else:
                mask = self._data.loc[(server_times >= min) & (server_times <= max)]
            return mask['session_id'].unique().tolist()
        else:
            return []

    def _datesFromIDs(self, id_list:List[int], versions: Union[List[int],None]=None) -> Dict[str, datetime]:
        min_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].min()
        max_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].max()
        return {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}
