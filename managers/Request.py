# include libraries
import abc
import enum
from datetime import datetime
from typing import Dict, List, Union
# include local files
import utils
from interfaces.DataInterface import DataInterface
from schemas.GameSchema import GameSchema


## @class ExporterFiles
#  Completely dumb struct that just enforces the names of the three kinds of file we can output.
#  @param events Bool stating whether to output a events file or not.
#  @param raw  Bool stating whether to output a raw file or not.
#  @param sessions Bool stating whether to output a processed session feature file or not.
class ExporterTypes:
    def __init__(self, events:bool = True, sessions:bool = True, population:bool = True):
        self.events = events
        self.sessions = sessions
        self.population = population

class ExporterLocations:
    def __init__(self, files:bool = True, dict:bool = False):
        self.files = files
        self.dict  = dict

class ExporterRange:
    def __init__(self, date_min:Union[datetime,None], date_max:Union[datetime,None], ids:Union[List[str],None], versions:Union[List[int],None]=None):
        self._date_min : Union[datetime,None] = date_min
        self._date_max : Union[datetime,None] = date_max
        self._ids      : Union[List[str],None] = ids
        self._versions : Union[List[int],None] = versions

    @staticmethod
    def FromDateRange(date_min:datetime, date_max:datetime, source:DataInterface, versions:Union[List[int],None]=None):
        ids = source.IDsFromDates(date_min, date_max, versions=versions)
        return ExporterRange(date_min=date_min, date_max=date_max, ids=ids, versions=versions)

    @staticmethod
    def FromIDs(ids:List[str], source:DataInterface, versions:Union[List[int],None]=None):
        date_range = source.DatesFromIDs(ids, versions=versions)
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=ids, versions=versions)

    def GetDateRange(self) -> Dict[str,Union[datetime,None]]:
        return {'min':self._date_min, 'max':self._date_max}

    def GetIDs(self) -> Union[List[str],None]:
        return self._ids

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
                exporter_types:ExporterTypes = ExporterTypes(), exporter_locs:ExporterLocations = ExporterLocations()):
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id   : str               = interface._game_id
        self._interface : DataInterface     = interface
        self._range     : ExporterRange     = range
        self._exports   : ExporterTypes     = exporter_types
        self._locs      : ExporterLocations = exporter_locs

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        _fmt = "%Y-%m-%d"
        _range = self._range.GetDateRange()
        _min = _range['min'].strftime(_fmt) if _range['min'] is not None else "None"
        _max = _range['max'].strftime(_fmt) if _range['max'] is not None else "None"
        return f"{self._interface._game_id}: {_min}-{_max}"

    def GetGameID(self):
        return str(self._game_id)

    ## Method to retrieve the list of IDs for all sessions covered by the request.
    #  Note, this will use the 
    def RetrieveSessionIDs(self) -> Union[List[str],None]:
        return self._range.GetIDs()