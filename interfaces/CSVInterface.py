import logging
import pandas as pd
from datetime import datetime
from pandas.io.parsers import TextFileReader
from pathlib import Path
from typing import Any, Dict, IO, List, Tuple, Optional
## import local files
from interfaces.DataInterface import DataInterface
from schemas.IDMode import IDMode
from utils import Logger

class CSVInterface(DataInterface):

    # *** PUBLIC BUILT-INS ***

    def __init__(self, game_id:str, filepath:Path, delim:str = ','):
        # set up data from params
        super().__init__(game_id=game_id)
        self._filepath  : Path = filepath
        self._delimiter : str = delim
        # set up data from file
        self._data      : pd.DataFrame = pd.DataFrame()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self) -> bool:
        try:
            self._data = pd.read_csv(filepath=self._filepath, delimiter=self._delimiter, parse_dates=['timestamp'])
            self._is_open = True
            return True
        except FileNotFoundError as err:
            Logger.Log(f"Could not find file {self._filepath}.", logging.ERROR)
            return False

    def _close(self) -> bool:
        self._is_open = False
        self._data = pd.DataFrame() # make new dataframe, let old data get garbage collected I assume.
        return True

    def _allIDs(self) -> List[str]:
        return self._data['session_id'].unique().tolist()

    def _fullDateRange(self) -> Dict[str,datetime]:
        min_time = pd.to_datetime(self._data['server_time'].min())
        max_time = pd.to_datetime(self._data['server_time'].max())
        return {'min':min_time, 'max':max_time}

    def _rowsFromIDs(self, id_list: List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> List[Tuple]:
        if self.IsOpen() and self._data != None:
            if id_mode == IDMode.SESSION:
                return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
            elif id_mode == IDMode.USER:
                return list(self._data.loc[self._data['user_id'].isin(id_list)].itertuples(index=False, name=None))
            else:
                return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
        else:
            return []

    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]]=None) -> List[str]:
        if not self._data.empty:
            server_times = pd.to_datetime(self._data['server_time'])
            mask = (server_times >= min) & (server_times <= max)
            if versions is not None and versions is not []:
                mask = mask & (self._data['app_version'].isin(versions))
            data_masked = self._data.loc[mask]
            return data_masked['session_id'].unique().tolist()
        else:
            return []

    def _datesFromIDs(self, id_list:List[int], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Dict[str, datetime]:
        if id_mode == IDMode.SESSION:
            min_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].min()
            max_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].max()
        elif id_mode == IDMode.USER:
            min_date = self._data[self._data['user_id'].isin(id_list)]['server_time'].min()
            max_date = self._data[self._data['user_id'].isin(id_list)]['server_time'].max()
        else:
            min_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].min()
            max_date = self._data[self._data['session_id'].isin(id_list)]['server_time'].max()
        return {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}
