import abc
import traceback
import typing
import pandas as pd
## import local files
import utils
from GameTable import GameTable
from schemas.Schema import Schema

class DataManager(abc.ABC):
    def __init__(self, game_id):
        self._game_id = game_id

    ## Abstract method to retrieve the data for a given set of ids.
    #  the request.
    @abc.abstractmethod
    def RetrieveSliceData(self, id_list) -> typing.List[typing.Tuple]:
        pass

class SQLDataManager(DataManager):
    def __init__(self, game_id: str, game_schema: Schema, settings):
        DataManager.__init__(self, game_id=game_id)
        self._game_schema = game_schema
        self._settings = settings
        self._tunnel, self._db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
        self._db_cursor = self._db.cursor()

    def RetrieveSliceData(self, id_list) -> typing.List[typing.Tuple]:
        # grab data for the given session range. Sort by event time, so
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            ver_filter = f" AND app_version in ({','.join([str(x) for x in self._game_schema.schema()['config']['SUPPORTED_VERS']])}) "
        else:
            ver_filter = ''
        id_string = ','.join([f"'{x}'" for x in id_list])
        # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
        filt = f"app_id='{self._game_id}' AND session_id  IN ({id_string}){ver_filter}"
        query = utils.SQL._prepareSelect(db_name=self._settings["db_config"]["DB_NAME_DATA"],
                                         table=self._settings["db_config"]["TABLE"], columns=None, filter=filt, limit=-1,
                                         sort_columns=["session_id", "session_n"], sort_direction="ASC",
                                         grouping=None, distinct=False)
        # self._select_queries.append(select_query) # this doesn't appear to be used???
        return utils.SQL.SELECTfromQuery(cursor=self._db_cursor, query=query, fetch_results=True)

    def __del__(self):
        utils.SQL.disconnectMySQLViaSSH(tunnel=self._tunnel, db=self._db)

class CSVDataManager(DataManager):
    # TODO: Take a path, rather than an existing dataframe.
    def __init__(self, game_id: str, data_frame: pd.DataFrame):
        DataManager.__init__(self, game_id=game_id)
        self._data = data_frame

    def RetrieveSliceData(self, id_list) -> typing.List[typing.Tuple]:
        return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))