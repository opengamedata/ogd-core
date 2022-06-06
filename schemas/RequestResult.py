# import standard libraries
from datetime import timedelta
from enum import IntEnum
from typing import Any, Dict, List

class ResultStatus(IntEnum):
    NONE = 1
    SUCCESS = 2
    FAILURE = 3

class ExportResult:
    def __init__(self, columns:List[str] = [], values:List[Any] = []):
        self._columns = columns
        self._values  = values

    @property
    def Columns(self) -> List[str]:
        return self._columns
    @Columns.setter
    def Columns(self, new_columns:List[str]):
        self._columns = new_columns

    @property
    def Values(self) -> List[Any]:
        return self._values

    def ToDict(self) -> Dict[str, List[Any]]:
        return {
            "cols":self._columns,
            "vals":self._values
        }

    def AppendValues(self, new_values:List[Any]):
        self._values += new_values


class RequestResult:
    def __init__(self, msg:str="", status:ResultStatus=ResultStatus.NONE,
                 events:ExportResult  = ExportResult(), sessions:ExportResult   = ExportResult(),
                 players:ExportResult = ExportResult(), population:ExportResult = ExportResult(),
                 duration:timedelta=timedelta()):
        self._message    = msg
        self._status     = status
        self._events     = events
        self._sessions   = sessions
        self._players    = players
        self._population = population
        self._duration   = duration

    @property
    def Status(self) -> ResultStatus:
        return self._status

    @property
    def Message(self) -> str:
        return self._message
    
    @property
    def Events(self) -> ExportResult:
        return self._events
    
    @property
    def Sessions(self) -> ExportResult:
        return self._sessions
    
    @property
    def Players(self) -> ExportResult:
        return self._players
    
    @property
    def Population(self) -> ExportResult:
        return self._population

    @property
    def ValuesDict(self) -> Dict[str, Dict[str, List[Any]]]:
        return {
            "population" : self.Population.ToDict(),
            "players"    : self.Players.ToDict(),
            "sessions"   : self.Sessions.ToDict(),
            "events"     : self.Events.ToDict()
        }

    @property
    def Duration(self) -> timedelta:
        return self._duration
    @Duration.setter
    def Duration(self, new_duration):
        self._duration = new_duration

    def RequestSucceeded(self, msg:str, val:Any):
        self._status = ResultStatus.SUCCESS
        self._msg = msg
        self._val = val

    def RequestErrored(self, msg:str):
        self._status = ResultStatus.FAILURE
        self._msg = msg
