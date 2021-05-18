## import standard libraries
import abc
import typing
## import locals
import utils

class DataInterface(abc.ABC):
    def __init__(self, game_id):
        self._game_id : str  = game_id
        self._is_open : bool = False

    def __del__(self):
        if self.IsOpen():
            self.Close()

    def RetrieveFromIDs(self, id_list: typing.List[int]) -> typing.List:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve data, the source interface is not open!")
            return []
        else:
            return self._retrieveFromIDs(id_list)

    def IDsFromDates(self, min, max):
        if not self._is_open:
            utils.Logger.Log("Can't retrieve IDs, the source interface is not open!")
        else:
            return self._IDsFromDates(min=min, max=max)

    def DatesFromIDs(self, id_list:typing.List[int]):
        if not self._is_open:
            utils.Logger.Log("Can't retrieve dates, the source interface is not open!")
        else:
            return self._datesFromIDs(id_list=id_list)
    
    def IsOpen(self) -> bool:
        return True if self._is_open else False

    @abc.abstractmethod
    def Open(self) -> bool:
        pass

    @abc.abstractmethod
    def Close(self) -> bool:
        pass

    @abc.abstractmethod
    def _retrieveFromIDs(self, id_list: typing.List[int]) -> typing.List:
        pass

    @abc.abstractmethod
    def _IDsFromDates(self, min, max):
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:typing.List[int]):
        pass