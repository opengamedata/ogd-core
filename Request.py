# include libraries
import abc
import enum
import typing
from datetime import datetime
from typing import Dict, List, Union
# include local files
import utils
from schemas.TableSchema import TableSchema
from interfaces.DataInterface import DataInterface
from interfaces.MySQLInterface import SQL
from schemas.Schema import Schema


## @class ExporterFiles
#  Completely dumb struct that just enforces the names of the three kinds of file we can output.
#  @param events Bool stating whether to output a events file or not.
#  @param raw  Bool stating whether to output a raw file or not.
#  @param sessions Bool stating whether to output a processed session feature file or not.
class ExporterFiles:
    def __init__(self, events:bool = True, raw:bool = True, sessions:bool = True):
        self.events = events
        self.raw = False
        self.sessions = sessions

class ExporterRange:
    def __init__(self, date_min:Union[datetime,None], date_max:Union[datetime,None], ids:Union[List[int],None]):
        self._date_min : Union[datetime,None] = date_min
        self._date_max : Union[datetime,None] = date_max
        self._ids      : Union[List[int],None] = ids

    @staticmethod
    def FromDateRange(date_min:datetime, date_max:datetime, source:DataInterface):
        ids = source.IDsFromDates(date_min, date_max)
        return ExporterRange(date_min=date_min, date_max=date_max, ids=ids)

    @staticmethod
    def FromIDs(ids:List[int], source:DataInterface):
        date_range = source.DatesFromIDs(ids)
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=ids)

    def GetDateRange(self) -> Dict:
        return {'min':self._date_min, 'max':self._date_max}

    def GetIDs(self) -> Union[List[int],None]:
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
    def __init__(self, interface:DataInterface, range:ExporterRange, exporter_files:ExporterFiles = ExporterFiles()):
        self._interface : DataInterface = interface
        self._range     : ExporterRange = range
        self._files     : ExporterFiles = exporter_files

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        fmt = "%Y%m%d"
        rng = self._range.GetDateRange()
        return f"{self._interface._game_id}: {rng['min'].strftime(fmt)}-{rng['max'].strftime(fmt)}"

    ## Method to retrieve the list of IDs for all sessions covered by
    #  the request.
    def retrieveSessionIDs(self, cursor, db_settings) -> Union[List[int],None]:
        supported_vers = Schema(schema_name=f"{self.game_id}.json")['config']['SUPPORTED_VERS']
        dates = self._range.GetDateRange()
        return self._interface.IDsFromDates(dates['min'], dates['max'], versions=supported_vers)