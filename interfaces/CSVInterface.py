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
        super().__init__(game_id=game_id)
        self._data = data_frame

    def Open(self, force_reopen:bool = False) -> bool:
        if force_reopen or not self.IsOpen():
            self._data = pd.read_csv(filepath_or_buffer=self._file, delimiter=self._delimiter, parse_dates=['server_time', 'client_time'])
            self._is_open = True
        return True

    @abc.abstractmethod
    def Close(self) -> bool:
        pass

    @abc.abstractmethod
    def _retrieveFromIDs(self, id_list: typing.List[int]) -> typing.List:
        return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))

    @abc.abstractmethod
    def _IDsFromDates(self, min, max):
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:typing.List[int]):
        pass