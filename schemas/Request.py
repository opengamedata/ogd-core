# include libraries
import abc
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Union
# include local files
from interfaces.DataInterface import DataInterface


## @class ExporterFiles
#  Completely dumb struct that just enforces the names of the three kinds of file we can output.
#  @param events Bool stating whether to output a events file or not.
#  @param raw  Bool stating whether to output a raw file or not.
#  @param sessions Bool stating whether to output a processed session feature file or not.
class ExporterTypes:
    def __init__(self, events:bool = True, sessions:bool = True, players:bool = True, population:bool = True):
        self.events = events
        self.sessions = sessions
        self.players = players
        self.population = population

class IDMode(Enum):
    SESSION = 1
    PLAYER = 2

class ExporterLocations:
    def __init__(self, files:bool = True, dict:bool = False):
        self.files = files
        self.dict  = dict

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
    def FromIDs(source:DataInterface, ids:List[str], id_mode:IDMode, versions:Union[List[int],None]=None):
        date_range = source.DatesFromIDs(ids, versions=versions)
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=ids, versions=versions)

    def GetDateRange(self) -> Dict[str,Union[datetime,None]]:
        return {'min':self._date_min, 'max':self._date_max}

    def GetIDs(self) -> Union[List[str],None]:
        return self._ids

class ResultStatus(Enum):
    NONE = 1
    SUCCESS = 2
    FAILURE = 3

class RequestResult:
    def __init__(self, msg:str, status:ResultStatus=ResultStatus.NONE,
                 events:Union[List[Any], None] = None, sessions:Union[List[Any], None] = None,
                 players:Union[List[Any], None] = None, population:Union[List[Any], None] = None,):
        self._message    = msg
        self._status     = status
        self._events     = events
        self._sessions   = sessions
        self._players    = players
        self._population = population

    def Status(self) -> ResultStatus:
        return self._status

    def Message(self) -> str:
        return self._message
    
    def Events(self) -> Union[List[Any], None]:
        return self._events
    
    def Sessions(self) -> Union[List[Any], None]:
        return self._sessions
    
    def Players(self) -> Union[List[Any], None]:
        return self._players
    
    def Population(self) -> Union[List[Any], None]:
        return self._population

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
                feature_overrides:Union[List[str], None]=None):
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id        : str                    = str(interface._game_id)
        self._interface      : DataInterface          = interface
        self._range          : ExporterRange          = range
        self._exports        : ExporterTypes          = exporter_types
        self._locs           : ExporterLocations      = exporter_locs
        self._feat_overrides : Union[List[str], None] = feature_overrides

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        _fmt = "%Y-%m-%d"
        _range = self._range.GetDateRange()
        _min = _range['min'].strftime(_fmt) if _range['min'] is not None else "None"
        _max = _range['max'].strftime(_fmt) if _range['max'] is not None else "None"
        return f"{self._game_id}: {_min}-{_max}"

    def GetGameID(self):
        return self._game_id

    def GetInterface(self) -> DataInterface:
        return self._interface

    def GetRange(self) -> ExporterRange:
        return self._range

    def ExportEvents(self) -> bool:
        return self._exports.events
    def ExportSessions(self) -> bool:
        return self._exports.sessions
    def ExportPlayers(self) -> bool:
        return self._exports.players
    def ExportPopulation(self) -> bool:
        return self._exports.population

    def ToFile(self) -> bool:
        return self._locs.files
    def ToDict(self) -> bool:
        return self._locs.dict

    ## Method to retrieve the list of IDs for all sessions covered by the request.
    #  Note, this will use the 
    def RetrieveSessionIDs(self) -> Union[List[str],None]:
        return self._range.GetIDs()