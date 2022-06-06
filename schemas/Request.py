# import standard libraries
import abc
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
# import local files
from interfaces.DataInterface import DataInterface
from schemas.IDMode import IDMode
from utils import Logger

class ExporterRange:
    """
    Simple class to define a range of data for export.
    """
    def __init__(self, date_min:Optional[datetime], date_max:Optional[datetime], ids:Optional[List[str]], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None):
        self._date_min : Optional[datetime] = date_min
        self._date_max : Optional[datetime] = date_max
        self._ids      : Optional[List[str]] = ids
        self._id_mode  : IDMode                = id_mode
        self._versions : Optional[List[int]] = versions

    @staticmethod
    def FromDateRange(source:DataInterface, date_min:datetime, date_max:datetime, versions:Optional[List[int]]=None):
        ids = source.IDsFromDates(date_min, date_max, versions=versions)
        return ExporterRange(date_min=date_min, date_max=date_max, ids=ids, id_mode=IDMode.SESSION, versions=versions)

    @staticmethod
    def FromIDs(source:DataInterface, ids:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None):
        date_range = source.DatesFromIDs(id_list=ids, id_mode=id_mode, versions=versions)
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=ids, id_mode=id_mode, versions=versions)

    @property
    def DateRange(self) -> Dict[str,Optional[datetime]]:
        return {'min':self._date_min, 'max':self._date_max}

    @property
    def IDs(self) -> Optional[List[str]]:
        return self._ids

    @property
    def IDMode(self):
        return self._id_mode

class ExporterTypes:
    """Completely dumb struct that just enforces the names of the four kinds of file we can output.
    """
    def __init__(self, events:bool = True, sessions:bool = True, players:bool = True, population:bool = True):
        self.events = events
        self.sessions = sessions
        self.players = players
        self.population = population

class ExporterLocations:
    def __init__(self, files:bool = True, dict:bool = False):
        self.files = files
        self.dict  = dict

class ResultStatus(Enum):
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

## @class Request
#  Dumb struct to hold data related to requests for data export.
#  This way, we've at least got a list of what is available in a request.
#  Acts as a base class for more specific types of request.
class Request(abc.ABC):
    ## Constructor for the request base class.
    #  Just stores whatever data is given. No checking done to ensure we have all
    #  necessary data, this can be checked wherever Requests are actually used.
    #  @param game_id An identifier for the game from which we want to extract data.
    #                 Should correspond to the app_id in the database.
    #  @param start_date   The starting date for our range of data to process.
    #  @param end_date     The ending date for our range of data to process.
    def __init__(self, interface:DataInterface, range:ExporterRange,
                exporter_types:ExporterTypes = ExporterTypes(), exporter_locs:ExporterLocations = ExporterLocations(),
                feature_overrides:Optional[List[str]]=None):
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id        : str                    = str(interface._game_id)
        self._interface      : DataInterface          = interface
        self._range          : ExporterRange          = range
        self._exports        : ExporterTypes          = exporter_types
        self._locs           : ExporterLocations      = exporter_locs
        self._feat_overrides : Optional[List[str]] = feature_overrides

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        _fmt = "%Y-%m-%d"
        _min = "Unkown"
        _max = "Unkown"
        try:
            _range = self.Range.DateRange
            _min = _range['min'].strftime(_fmt) if _range['min'] is not None else "None"
            _max = _range['max'].strftime(_fmt) if _range['max'] is not None else "None"
        except Exception as err:
            Logger.Log(f"Got an error when trying to stringify a Request: {type(err)} {str(err)}")
        finally:
            return f"{self._game_id}: {_min}<->{_max}"

    @property
    def GameID(self):
        return self._game_id

    @property
    def Interface(self) -> DataInterface:
        return self._interface

    @property
    def Range(self) -> ExporterRange:
        return self._range

    @property
    def ExportEvents(self) -> bool:
        return self._exports.events
    @property
    def ExportSessions(self) -> bool:
        return self._exports.sessions
    @property
    def ExportPlayers(self) -> bool:
        return self._exports.players
    @property
    def ExportPopulation(self) -> bool:
        return self._exports.population

    @property
    def ToFile(self) -> bool:
        return self._locs.files
    @property
    def ToDict(self) -> bool:
        return self._locs.dict

    ## Method to retrieve the list of IDs for all sessions covered by the request.
    #  Note, this will use the 
    def RetrieveIDs(self) -> Optional[List[str]]:
        return self.Range.IDs