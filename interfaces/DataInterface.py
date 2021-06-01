## import standard libraries
import abc
import typing
from datetime import datetime
from typing import Dict, List, Tuple, Union
## import locals
import utils

class DataInterface(abc.ABC):
    def __init__(self, game_id):
        self._game_id : str  = game_id
        self._is_open : bool = False

    def __del__(self):
        self.Close()

    def Open(self, force_reopen:bool = False) -> bool:
        if force_reopen or not self._is_open:
            return self._open()
        else:
            return True
    
    def IsOpen(self) -> bool:
        return True if self._is_open else False

    def Close(self) -> bool:
        if self._is_open:
            return self._close()
        else:
            return True

    def AllIDs(self) -> Union[List[int],None]:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve data, the source interface is not open!")
            return None
        else:
            return self._allIDs()

    def FullDateRange(self) -> Dict[str,Union[datetime,None]]:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve data, the source interface is not open!")
            return {'min':None, 'max':None}
        else:
            return self._fullDateRange()

    def EventsFromIDs(self, id_list: List[int], versions: Union[List[int],None]=None) -> Union[List, None]:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve data, the source interface is not open!")
            return None
        else:
            return self._eventsFromIDs(id_list, versions=versions)

    def IDsFromDates(self, min:datetime, max:datetime, versions: Union[List[int],None]=None) -> Union[List[int], None]:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve IDs, the source interface is not open!")
            return None
        else:
            return self._IDsFromDates(min=min, max=max, versions=versions)

    def DatesFromIDs(self, id_list:List[int], versions: Union[List[int],None]=None) -> Dict[str,Union[datetime,None]]:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve dates, the source interface is not open!")
            return {'min':None, 'max':None}
        else:
            return self._datesFromIDs(id_list=id_list, versions=versions)

    @abc.abstractmethod
    def _open(self) -> bool:
        pass

    @abc.abstractmethod
    def _close(self) -> bool:
        pass

    @abc.abstractmethod
    def _allIDs(self) -> List[int]:
        pass

    @abc.abstractmethod
    def _fullDateRange(self) -> Dict[str,datetime]:
        pass

    @abc.abstractmethod
    def _eventsFromIDs(self, id_list: List[int], versions: Union[List[int],None]=None) -> List[Tuple]:
        pass

    @abc.abstractmethod
    def _IDsFromDates(self, min:datetime, max:datetime, versions: Union[List[int],None]=None) -> List[int]:
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:List[int], versions: Union[List[int],None]=None) -> Dict[str,datetime]:
        pass