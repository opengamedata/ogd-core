import json
import logging
import os
from datetime import datetime
from google.cloud import bigquery
from typing import Dict, List, Tuple, Union
# import locals
from coding.Code import Code
from coding.Coder import Coder
from config.config import settings as default_settings
from interfaces.CodingInterface import CodingInterface
from schemas.IDMode import IDMode
from utils import Logger

# TODO: see about merging this back into BigQueryInterface for a unified interface.

class BigQueryCodingInterface(CodingInterface):

    # *** PUBLIC BUILT-INS ***

    def __init__(self, game_id: str, settings):
        super().__init__(game_id=game_id)
        self._settings = settings
        self.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, force_reopen: bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            if "GITHUB_ACTIONS" in os.environ:
                self._client = bigquery.Client()
            else:
                credential_path : str
                if "GAME_SOURCE_MAP" in self._settings:
                    credential_path = self._settings["GAME_SOURCE_MAP"][self._game_id]["credential"]
                else:
                    credential_path = default_settings["GAME_SOURCE_MAP"][self._game_id]["credential"]
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
                self._client = bigquery.Client()
            if self._client != None:
                self._is_open = True
                Logger.Log("Connected to BigQuery database.", logging.DEBUG)
                return True
            else:
                Logger.Log("Could not connect to BigQuery Database.", logging.WARN)
                return False
        else:
            return True

    def _close(self) -> bool:
        self._client.close()
        self._is_open = False
        Logger.Log("Closed connection to BigQuery.", logging.DEBUG)
        return True

    def _allCoders(self) -> Union[List[Coder], None]:
        db_name    : str
        table_name : str
        if "BIGQUERY_CONFIG" in self._settings:
            db_name = self._settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = self._settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        else:
            db_name = default_settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = default_settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        query = f"""
            SELECT DISTINCT param.value.int_value AS session_id
            FROM `{db_name}.{table_name}`,
            UNNEST(event_params) AS param
            WHERE param.key = "ga_session_id"
        """
        data = self._client.query(query)
        ids = [str(row['session_id']) for row in data]
        return ids if ids != None else []


    def _rowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Union[List[int],None] = None) -> List[Tuple]:
        db_name    : str
        table_name : str
        # 1) Get db and table names
        if "BIGQUERY_CONFIG" in self._settings:
            db_name = self._settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = self._settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        else:
            db_name = default_settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = default_settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        # 2) Set up clauses to select based on Session ID or Player ID.
        session_clause : str = ""
        player_clause  : str = ""
        if id_mode == IDMode.SESSION:
            id_string = ','.join([f"{x}" for x in id_list])
            session_clause = f"AND   param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
            player_clause  = f"AND   param_user.key    = 'user_code'"
        elif id_mode == IDMode.PLAYER:
            id_string = ','.join([f"'{x}'" for x in id_list])
            session_clause = f"AND   param_session.key = 'ga_session_id'"
            player_clause  = f"AND   param_user.key    = 'user_code' AND param_user.value.string_value IN ({id_string})"
        else:
            Logger.Log(f"Invalid ID mode given (val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
            id_string = ','.join([f"{x}" for x in id_list])
            session_clause = f"AND   param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
            player_clause  = f"AND   param_user.key    = 'user_code'"
        # 3) Set up WHERE clause based on whether we need Aqualab min version or not.
        if self._game_id == "AQUALAB":
            where_clause = f"""
                WHERE param_app_version.key = 'app_version' AND param_app_version.value.double_value >= {AQUALAB_MIN_VERSION}
                AND   param_log_version.key = 'log_version'
                {session_clause}
                {player_clause}
            """
        else:
            where_clause = f"""
                WHERE param_app_version.key = 'app_version'
                AND   param_log_version.key = 'log_version'
                {session_clause}
                {player_clause}
            """
        # 4) Set up actual query
        query = ""
        if self._game_id == "SHIPWRECKS":
            query = f"""
                SELECT event_name, event_params, device, geo, platform,
                concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                param_session.value.int_value as session_id,
                FROM `{db_name}.{table_name}`
                CROSS JOIN UNNEST(event_params) AS param_session
                WHERE param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})
                ORDER BY `session_id`, `timestamp` ASC
            """
        else:
            query = f"""
                SELECT event_name, event_params, device, geo, platform,
                concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                param_app_version.value.double_value as app_version,
                param_log_version.value.int_value as log_version,
                param_session.value.int_value as session_id,
                param_user.value.string_value as fd_user_id
                FROM `{db_name}.{table_name}`
                CROSS JOIN UNNEST(event_params) AS param_app_version
                CROSS JOIN UNNEST(event_params) AS param_log_version
                CROSS JOIN UNNEST(event_params) AS param_session
                CROSS JOIN UNNEST(event_params) AS param_user
                {where_clause}
                ORDER BY `session_id`, `timestamp` ASC
            """
        data = self._client.query(query)
        events = []
        for row in data:
            items = tuple(row.items())
            event = []
            for item in items:
                if item[0] == "event_params":
                    _params = {param['key']:param['value'] for param in item[1]}
                    event.append(json.dumps(_params, sort_keys=True))
                elif item[0] in ["device", "geo"]:
                    event.append(json.dumps(item[1], sort_keys=True))
                else:
                    event.append(item[1])
            events.append(tuple(event))
        return events if events != None else []

    def _IDsFromDates(self, min:datetime, max:datetime, versions:Union[List[int],None] = None) -> List[str]:
        ret_val = []
        str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
        db_name    : str
        table_name : str
        if "BIGQUERY_CONFIG" in self._settings:
            db_name = self._settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = self._settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        else:
            db_name = default_settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = default_settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        query = f"""
            SELECT DISTINCT param.value.int_value AS session_id
            FROM `{db_name}.{table_name}`,
            UNNEST(event_params) AS param
            WHERE param.key = "ga_session_id"
            AND _TABLE_SUFFIX BETWEEN '{str_min}' AND '{str_max}'
        """
        data = self._client.query(query)
        ids = [str(row['session_id']) for row in data]
        if ids is not None:
            ret_val = ids
        return ret_val

    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Union[List[int],None] = None) -> Dict[str, datetime]:
        db_name    : str
        table_name : str
        if "BIGQUERY_CONFIG" in self._settings:
            db_name = self._settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = self._settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        else:
            db_name = default_settings["BIGQUERY_CONFIG"][self._game_id]["DB_NAME"]
            table_name = default_settings["BIGQUERY_CONFIG"]["TABLE_NAME"]
        if id_mode==IDMode.SESSION:
            id_string = ','.join([f"{x}" for x in id_list])
            where_clause = f"""
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
        elif id_mode==IDMode.PLAYER:
            id_string = ','.join([f"'{x}'" for x in id_list])
            where_clause = f"""
                WHERE param.key = "user_code"
                AND param.value.string_value IN ({id_string})
            """
        else:
            Logger.Log(f"Invalid ID mode given (val={id_mode}), defaulting to session mode.", logging.WARNING, depth=3)
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
                FROM `{db_name}.{table_name}`
            )
            SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
            FROM datetable,
            UNNEST(event_params) AS param
            {where_clause}
        """
        data = list(self._client.query(query))
        return {'min':datetime.strptime(data[0][0], "%m-%d-%Y %H:%M:%S"), 'max':datetime.strptime(data[0][1], "%m-%d-%Y %H:%M:%S")}

    # *** PUBLIC METHODS ***
    def IsOpen(self) -> bool:
        """Overridden version of IsOpen function, checks that BigQueryInterface client has been initialized.

        :return: True if the interface is open, else False
        :rtype: bool
        """
        return True if (super().IsOpen() and self._client is not None) else False
