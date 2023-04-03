import logging
import pandas as pd
from datetime import datetime
from pandas.io.parsers import TextFileReader
from pathlib import Path
from typing import Any, Dict, IO, List, Tuple, Optional
## import local files
from interfaces.DataInterface import DataInterface
from schemas.IDMode import IDMode
from schemas.TableSchema import TableSchema
from utils import Logger

class CSVInterface(DataInterface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_id:str, filepath:Path, delim:str = ',', file_schema_name:str = "OGD_EVENT_FILE"):
        # set up data from params
        self._file_schema_name = file_schema_name
        self._filepath  : Path = filepath
        self._delimiter : str = delim
        super().__init__(game_id=game_id, config={})
        # set up data from file
        self._data      : pd.DataFrame = pd.DataFrame()
        self.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self) -> bool:
        try:
            self._data = pd.read_csv(filepath_or_buffer=self._filepath, delimiter=self._delimiter, parse_dates=['timestamp'])
            self._is_open = True
            return True
        except FileNotFoundError as err:
            Logger.Log(f"Could not find file {self._filepath}.", logging.ERROR)
            return False

    def _close(self) -> bool:
        self._is_open = False
        self._data = pd.DataFrame() # make new dataframe, let old data get garbage collected I assume.
        return True

    def _loadTableSchema(self, game_id:str) -> TableSchema:
        # TODO: make the .meta file of an export include the name of the most current table schema for Event files, then read that in here as default.
        return TableSchema(schema_name=self._file_schema_name)

    def _allIDs(self) -> List[str]:
        return self._data['session_id'].unique().tolist()

    def _fullDateRange(self) -> Dict[str,datetime]:
        min_time = pd.to_datetime(self._data['timestamp'].min())
        max_time = pd.to_datetime(self._data['timestamp'].max())
        return {'min':min_time, 'max':max_time}

    def _rowsFromIDs(self, id_list: List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> List[Tuple]:
        if self.IsOpen() and not self._data.empty:
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
            mask = (server_times >= pd.to_datetime(min)) & (server_times <= pd.to_datetime(max))
            if versions is not None and versions is not []:
                mask = mask & (self._data['app_version'].isin(versions))
            data_masked = self._data.loc[mask]
            return data_masked['session_id'].unique().tolist()
        else:
            return []

    def _datesFromIDs(self, id_list:List[int], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Dict[str, datetime]:
        if id_mode == IDMode.SESSION:
            min_date = self._data[self._data['session_id'].isin(id_list)]['timestamp'].min()
            max_date = self._data[self._data['session_id'].isin(id_list)]['timestamp'].max()
        elif id_mode == IDMode.USER:
            min_date = self._data[self._data['user_id'].isin(id_list)]['timestamp'].min()
            max_date = self._data[self._data['user_id'].isin(id_list)]['timestamp'].max()
        else:
            min_date = self._data[self._data['session_id'].isin(id_list)]['timestamp'].min()
            max_date = self._data[self._data['session_id'].isin(id_list)]['timestamp'].max()
        return {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
