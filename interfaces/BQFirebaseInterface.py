import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
# import locals
from interfaces.BigQueryInterface import BigQueryInterface
from schemas.IDMode import IDMode
from schemas.configs.GameSourceSchema import GameSourceSchema
from utils.Logger import Logger

AQUALAB_MIN_VERSION = 6.2

class BQFirebaseInterface(BigQueryInterface):
    """Subclass of the general BigQueryInterface, with re-implemented queries to handle old Firebase unnest bullshit.
    """

    # *** BUILT-INS ***

    def __init__(self, game_id:str, config:GameSourceSchema, fail_fast:bool):
        super().__init__(game_id=game_id, config=config, fail_fast=fail_fast)
        self.Open()

    # *** RE-IMPLEMENT ABSTRACT FUNCTIONS ***

    def _allIDs(self) -> List[str]:
        query = f"""
            SELECT DISTINCT param.value.int_value AS session_id
            FROM `{self.DBPath()}`,
            UNNEST(event_params) AS param
            WHERE param.key = "ga_session_id"
        """
        Logger.Log(f"BQ-Firebase: Running query for all ids:\n{query}", logging.DEBUG, depth=3)
        data = self._client.query(query)
        ids = [str(row['session_id']) for row in data]
        return ids if ids != None else []

    def _fullDateRange(self) -> Dict[str, datetime]:
        query = f"""
            WITH datetable AS
            (
                SELECT event_date, event_timestamp,
                FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
                FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
                FROM `{self.DBPath()}`
            )
            SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
            FROM datetable
        """
        Logger.Log(f"BQ-Firebase: Running query for full date range:\n{query}", logging.DEBUG, depth=3)
        data = list(self._client.query(query))
        return {'min':data[0][0], 'max':data[0][1]}

    def _rowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None, exclude_rows:Optional[List[str]]=None) -> List[Tuple]:
        # 2) Set up clauses to select based on Session ID or Player ID.
        events = None
        if self._client != None:
            query = self._generateRowFromIDQuery(id_list=id_list, id_mode=id_mode, exclude_rows=exclude_rows)
            Logger.Log(f"BQ-Firebase: Running query for rows from IDs:\n{query}", logging.DEBUG, depth=3)
            data = self._client.query(query)
            events = []
            for row in data:
                items = tuple(row.items())
                event = []
                for item in items:
                    if item[0] == "event_params":
                        _params = {param['key']:param['value'] for param in item[1]}
                        event.append(json.dumps(_params, sort_keys=True))
                    elif item[0] in {"device", "geo"}:
                        event.append(json.dumps(item[1], sort_keys=True))
                    else:
                        event.append(item[1])
                events.append(tuple(event))
        return events if events != None else []

    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]] = None) -> List[str]:
        ret_val = []
        str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
        query = f"""
            SELECT DISTINCT param.value.int_value AS session_id
            FROM `{self.DBPath(min_date=min.date(), max_date=max.date())}`,
            UNNEST(event_params) AS param
            WHERE param.key = "ga_session_id"
            AND _TABLE_SUFFIX BETWEEN '{str_min}' AND '{str_max}'
        """
        Logger.Log(f"BQ-Firebase: Running query for ids from dates:\n{query}", logging.DEBUG, depth=3)
        data = self._client.query(query)
        ids = [str(row['session_id']) for row in data]
        if ids is not None:
            ret_val = ids
        return ret_val

    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None) -> Dict[str, datetime]:
        if id_mode==IDMode.SESSION:
            id_string = ','.join([f"{x}" for x in id_list])
            where_clause = f"""
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
        elif id_mode==IDMode.USER:
            id_string = ','.join([f"'{x}'" for x in id_list])
            where_clause = f"""
                WHERE param.key = "user_code"
                AND param.value.string_value IN ({id_string})
            """
        else:
            Logger.Log(f"Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
            id_string = ','.join([f"{x}" for x in id_list])
            where_clause = f"""
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
        query = f"""
            WITH datetable AS
            (
                SELECT event_date, event_timestamp, event_params,
                FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
                FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
                FROM `{self.DBPath()}`
            )
            SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
            FROM datetable,
            UNNEST(event_params) AS param
            {where_clause}
        """
        Logger.Log(f"BQ-Firebase: Running query for dates from IDs:\n{query}", logging.DEBUG, depth=3)
        data = list(self._client.query(query))
        ret_val : Dict[str, datetime] = {}
        if len(data) == 1:
            dates = data[0]
            if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
                ret_val = {'min':datetime.strptime(dates[0], "%m-%d-%Y %H:%M:%S"), 'max':datetime.strptime(dates[1], "%m-%d-%Y %H:%M:%S")}
            else:
                Logger.Log(f"BQFirebaseInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
                ret_val = {'min':datetime.now(), 'max':datetime.now()}
        else:
            Logger.Log(f"BQ-Firebase: Query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
            ret_val = {'min':datetime.now(), 'max':datetime.now()}
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _generateRowFromIDQuery(self, id_list:List[str], id_mode:IDMode, exclude_rows:Optional[List[str]]=None) -> str:
        session_clause : str = ""
        player_clause  : str = ""
        if id_mode == IDMode.SESSION:
            id_string = ','.join([f"{x}" for x in id_list])
            session_clause = f"param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
            player_clause  = f"(param_user.key   = 'user_code'     OR  param_user.key = 'undefined')"
        elif id_mode == IDMode.USER:
            id_string = ','.join([f"'{x}'" for x in id_list])
            session_clause = f"param_session.key = 'ga_session_id'"
            player_clause  = f"(param_user.key   = 'user_code' OR param_user.key = 'undefined') AND param_user.value.string_value IN ({id_string})"
        else:
            Logger.Log(f"BQ-Firebase: Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
            id_string = ','.join([f"{x}" for x in id_list])
            session_clause = f"param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
            player_clause  = f"(param_user.key   = 'user_code' OR param_user.key = 'undefined')"
        # 3) Set up WHERE clause based on whether we need Aqualab min version or not.
        if self._game_id == "AQUALAB":
            where_clause = \
            f"""WHERE param_app_version.key = 'app_version'
                AND   param_log_version.key = 'log_version'
                AND   {session_clause}
                AND   {player_clause}"""
        else:
            where_clause = \
            f"""WHERE param_app_version.key = 'app_version'
                AND   param_log_version.key = 'log_version'
                AND   {session_clause}
                AND   {player_clause}"""
        # 4) Set up actual query
        query = ""
        if self._game_id == "SHIPWRECKS":
            query = f"""
                SELECT event_name, event_params, device, geo, platform,
                concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                param_session.value.int_value as session_id,
                FROM `{self.DBPath()}`
                CROSS JOIN UNNEST(event_params) AS param_session
                WHERE param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})
                ORDER BY `session_id`, `timestamp` ASC;
            """
        else:
            # TODO Order by user_id, and by timestamp within that.
            # Note that this could prove to be wonky when we have more games without user ids,
            # will need to really rethink this when we start using new system.
            # Still, not a huge deal because most of these will be rewritten at that time anyway.
            query = f"""
                SELECT event_name, event_params, device, geo, platform,
                concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                param_app_version.value.string_value as app_version,
                param_log_version.value.int_value as log_version,
                param_session.value.int_value as session_id,
                param_user.value.string_value as fd_user_id
                FROM `{self.DBPath()}`
                CROSS JOIN UNNEST(event_params) AS param_app_version
                CROSS JOIN UNNEST(event_params) AS param_log_version
                CROSS JOIN UNNEST(event_params) AS param_session
                CROSS JOIN UNNEST(event_params) AS param_user
                {where_clause}
                ORDER BY `fd_user_id`, `timestamp` ASC;
            """
        return query
