## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# import local files
from interfaces.Interface import Interface
from schemas.IDMode import IDMode
from utils import Logger

class DataInterface(Interface):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _allIDs(self) -> List[str]:
        pass

    @abc.abstractmethod
    def _fullDateRange(self) -> Dict[str,datetime]:
        pass

    @abc.abstractmethod
    def _rowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None) -> List[Tuple]:
        pass

    @abc.abstractmethod
    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]] = None) -> List[str]:
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None) -> Dict[str,datetime]:
        pass

    # *** BUILT-INS ***

    def __init__(self, game_id):
        super().__init__()
        self._game_id : str  = game_id

    def __del__(self):
        self.Close()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def AllIDs(self) -> Optional[List[str]]:
        ret_val = None
        if self.IsOpen():
            ret_val = self._allIDs()
        else:
            Logger.Log("Can't retrieve list of all session IDs, the source interface is not open!", logging.WARNING, depth=3)
        return ret_val

    def FullDateRange(self) -> Union[Dict[str,datetime], Dict[str,None]]:
        ret_val = {'min':None, 'max':None}
        if self.IsOpen():
            ret_val = self._fullDateRange()
        else:
            Logger.Log(f"Could not get full date range, the source interface is not open!", logging.WARNING, depth=3)
        return ret_val

    def RowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Optional[List[Tuple]]:
        ret_val = None
        if self.IsOpen():
            Logger.Log(f"Retrieving rows from IDs with {id_mode} ID mode.", logging.DEBUG, depth=3)
            ret_val = self._rowsFromIDs(id_list=id_list, id_mode=id_mode, versions=versions)
        else:
            Logger.Log(f"Could not retrieve rows for {len(id_list)} session IDs, the source interface is not open!", logging.WARNING, depth=3)
        return ret_val

    def IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]]=None) -> Optional[List[str]]:
        ret_val = None
        if not self.IsOpen():
            str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
            Logger.Log(f"Could not retrieve IDs for {str_min}-{str_max}, the source interface is not open!", logging.WARNING, depth=3)
        else:
            ret_val = self._IDsFromDates(min=min, max=max, versions=versions)
        return ret_val

    def DatesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Union[Dict[str,datetime], Dict[str,None]]:
        ret_val = {'min':None, 'max':None}
        if not self.IsOpen():
            Logger.Log(f"Could not retrieve date range {len(id_list)} session IDs, the source interface is not open!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Retrieving date range from IDs with {id_mode} ID mode.", logging.DEBUG, depth=3)
            ret_val = self._datesFromIDs(id_list=id_list, id_mode=id_mode, versions=versions)
        return ret_val

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
