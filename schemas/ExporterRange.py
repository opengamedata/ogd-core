# import standard libraries
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
# import local files
from interfaces.DataInterface import DataInterface

class IDMode(Enum):
    SESSION = 1
    PLAYER = 2

class ExporterRange:
    def __init__(self, date_min:Union[datetime,None], date_max:Union[datetime,None], ids:Union[List[str],None], id_mode:IDMode=IDMode.SESSION, versions:Union[List[int],None]=None):
        self._date_min : Union[datetime,None] = date_min
        self._date_max : Union[datetime,None] = date_max
        self._ids      : Union[List[str],None] = ids
        self._id_mode  : IDMode                = id_mode
        self._versions : Union[List[int],None] = versions

    @staticmethod
    def FromDateRange(source:DataInterface, date_min:datetime, date_max:datetime, versions:Union[List[int],None]=None):
        ids = source.IDsFromDates(date_min, date_max, versions=versions)
        return ExporterRange(date_min=date_min, date_max=date_max, ids=ids, versions=versions)

    @staticmethod
    def FromIDs(source:DataInterface, ids:List[str], id_mode:IDMode=IDMode.SESSION, versions:Union[List[int],None]=None):
        date_range = source.DatesFromIDs(id_list=ids, id_mode=id_mode, versions=versions)
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=ids, versions=versions)

    def GetDateRange(self) -> Dict[str,Union[datetime,None]]:
        return {'min':self._date_min, 'max':self._date_max}

    def GetIDs(self) -> Union[List[str],None]:
        return self._ids
