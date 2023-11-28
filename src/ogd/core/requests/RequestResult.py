# import standard libraries
from datetime import timedelta
from enum import IntEnum
from typing import Any, Dict, List, Union
# import locals
from ogd.core.utils.utils import ExportRow

class ResultStatus(IntEnum):
    NONE = 1
    SUCCESS = 2
    FAILURE = 3

class ExportResult:
    def __init__(self, columns:List[str] = [], values:List[ExportRow] = []):
        self._columns = columns
        self._values  = values

    @property
    def Columns(self) -> List[str]:
        return self._columns
    @Columns.setter
    def Columns(self, new_columns:List[str]):
        self._columns = new_columns

    @property
    def Values(self) -> List[ExportRow]:
        return self._values

    def ToDict(self) -> Dict[str, Union[List[str], List[ExportRow]]]:
        return {
            "cols":self._columns,
            "vals":self._values
        }

    def AppendRow(self, new_values:ExportRow):
        self._values.append(new_values)
    
    def ConcatRows(self, new_values:List[ExportRow]):
        self._values += new_values

class RequestResult:
    def __init__(self, msg:str="", status:ResultStatus=ResultStatus.NONE,
                 sess_ct : int = 0, duration:timedelta=timedelta()):
        self._message    = msg
        self._status     = status
        self._sess_ct    = sess_ct
        self._duration   = duration

    @property
    def Status(self) -> ResultStatus:
        return self._status

    @property
    def Message(self) -> str:
        return self._message

    @property
    def SessionCount(self):
        return self._sess_ct
    @SessionCount.setter
    def SessionCount(self, new_ct:int):
        self._sess_ct = new_ct

    @property
    def Duration(self) -> timedelta:
        return self._duration
    @Duration.setter
    def Duration(self, new_duration):
        self._duration = new_duration

    def RequestSucceeded(self, msg:str):
        self._status = ResultStatus.SUCCESS
        self._message = msg

    def RequestErrored(self, msg:str):
        self._status = ResultStatus.FAILURE
        self._message = msg
