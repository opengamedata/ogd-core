# include libraries
import abc
import enum
import typing
from datetime import datetime
from typing import List, Union
# include local files
import utils
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

    def GetDateRange(self) -> typing.Dict:
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
        self._interface  = interface
        self._range = range
        self._exporter_files = exporter_files

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        fmt = "%Y%m%d"
        rng = self._range.GetDateRange()
        return f"{self._game_id}: {self._range.GetDateRange()['min'].strftime(fmt)}-{self._range.GetDateRange()['max'].strftime(fmt)}"

    ## Method to retrieve the list of IDs for all sessions covered by
    #  the request.
    def retrieveSessionIDs(self, cursor, db_settings) -> typing.List:
        # We grab the ids for all sessions that have 0th move in the proper date range.
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            ver_filter = f" AND app_version in ({','.join([str(x) for x in self._game_schema.schema()['config']['SUPPORTED_VERS']])}) "
        start = self.start_date.isoformat()
        end = self.end_date.isoformat()
        supported_vers = Schema(schema_name=f"{self.game_id}.json")['config']['SUPPORTED_VERS']
        ver_filter = f" AND `app_version` in ({','.join([str(x) for x in supported_vers])}) " if supported_vers else ''
        filt = f"`app_id`=\"{self.game_id}\" AND `session_n`='0' AND (`server_time` BETWEEN '{start}' AND '{end}'){ver_filter}"
        session_ids_raw = SQL.SELECT(cursor=cursor, db_name=db_settings["DB_NAME_DATA"], table=db_settings["TABLE"],
                                columns=["`session_id`"], filter=filt,
                                sort_columns=["`session_id`"], sort_direction="ASC", distinct=True)
        return [sess[0] for sess in session_ids_raw]

## Class representing a request that includes a range of dates to be retrieved
#  for the given game.
class DateRangeRequest(Request):
    def __init__(self, game_id: str = None, start_date: date = None, end_date: date = None,
                 exporter_files: ExporterFiles = ExporterFiles()):
        Request.__init__(self, game_id=game_id, exporter_files=exporter_files)
        self.start_date = start_date
        self.end_date = end_date

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        fmt = "%Y%m%d"
        return f"{self.game_id}: {self.start_date.strftime(fmt)}-{self.end_date.strftime(fmt)}"

    ## Method to retrieve the list of IDs for all sessions covered by
    #  the request.
    def retrieveSessionIDs(self, db_cursor, db_settings) -> typing.List:
        # We grab the ids for all sessions that have 0th move in the proper date range.
        start = self.start_date.isoformat()
        end = self.end_date.isoformat()
        supported_vers = Schema(schema_name=f"{self.game_id}.json")['config']['SUPPORTED_VERS']
        ver_filter = f" AND `app_version` in ({','.join([str(x) for x in supported_vers])}) " if supported_vers else ''
        filt = f"`app_id`=\"{self.game_id}\" AND `session_n`='0' AND (`server_time` BETWEEN '{start}' AND '{end}'){ver_filter}"
        session_ids_raw = SQL.SELECT(cursor=db_cursor, db_name=db_settings["DB_NAME_DATA"], table=db_settings["TABLE"],
                                columns=["`session_id`"], filter=filt,
                                sort_columns=["`session_id`"], sort_direction="ASC", distinct=True)
        return [sess[0] for sess in session_ids_raw]

## Class representing a request for a specific list of session IDs.
class IDListRequest(Request):
    def __init__(self, game_id: str = None, session_ids = [], exporter_files: ExporterFiles = ExporterFiles()):
        Request.__init__(self, game_id=game_id, exporter_files=exporter_files)
        self._session_ids = session_ids

    def __str__(self):
        return f"{self.game_id}: {self._session_ids[0]}-{self._session_ids[-1]}"

    ## Method to retrieve the list of IDs for all sessions covered by
    #  the request. Should just be the original request list.
    def retrieveSessionIDs(self, db_cursor, db_settings) -> typing.List:
        return self._session_ids

class FileRequest(Request):
    def __init__(self, file_path, game_id: str = None, exporter_files: ExporterFiles = ExporterFiles()):
        Request.__init__(self, game_id=game_id, exporter_files=exporter_files)
        self.file_path = file_path

    def __str__(self):
        return f"{self.game_id}: {str(self.file_path)}"

    # TODO: actually get the sessionIDs, so this request behaves properly.
    def retrieveSessionIDs(self, db_cursor, db_settings) -> typing.List:
        return []