import json
import logging
import os
from datetime import datetime
from google.cloud import bigquery
from typing import Dict, List, Tuple, Union

from config.config import settings
from interfaces.DataInterface import DataInterface
from utils import Logger

class BigQueryInterface(DataInterface):

    def __init__(self, game_id: str, settings):
        super().__init__(game_id=game_id)
        self._settings = settings
        self.Open()

    def _open(self, force_reopen: bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            credential_path = settings["game_source_map"][self._game_id]["credential"]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
            self._client = bigquery.Client()
            if self._client != None:
                self._is_open = True
                Logger.Log("Connected to BigQuery database.", logging.DEBUG)
                return True
            else:
                Logger.Log("Could not connect to BigQuery Databse.", logging.WARN)
                return False
        else:
            return True

    def _close(self) -> bool:
        self._client.close()
        self._is_open = False
        Logger.toStdOut("Closed connection to BigQuery.", logging.DEBUG)
        return True

    def _rowsFromIDs(self, id_list: List[int], versions: Union[List[int],None]=None) -> List[Tuple]:
        if self._client != None:
            db_name = self._settings["bq_config"]["DB_NAME"]
            table_name = self._settings["bq_config"]["TABLE_NAME"]
            id_string = ','.join([f"{x}" for x in id_list])
            query = f"""
                SELECT event_name, event_params, user_id, device, geo, platform, param.value.int_value AS session_id,
                concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%E*S', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
            data = self._client.query(query)
            events = []
            for row in data:
                items = tuple(row.items())
                event = []
                for item in items:
                    if item[0] in ["event_params", "device", "geo"]:
                        event.append(json.dumps(item[1]))
                    else:
                        event.append(item[1])
                events.append(tuple(event))
            return events if events != None else []
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, BigQuery connection is not open.", logging.WARN)
            return []

    def _allIDs(self) -> List[int]:
        if self._client != None:
            db_name = self._settings["bq_config"]["DB_NAME"]
            table_name = self._settings["bq_config"]["TABLE_NAME"]
            query = f"""
                SELECT DISTINCT param.value.int_value AS session_id
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
            """
            data = self._client.query(query)
            ids = [row['session_id'] for row in data]
            return ids if ids != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, BigQuery connection is not open.", logging.WARN)
            return []

    def _fullDateRange(self) -> Dict[str, datetime]:
        if self._client != None:
            db_name = self._settings["bq_config"]["DB_NAME"]
            table_name = self._settings["bq_config"]["TABLE_NAME"]
            query = f"""
                WITH datetable AS
                (
                    SELECT event_date, event_timestamp,
                    FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
                    FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
                    FROM `{db_name}.{table_name}`
                )
                SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
                FROM datetable
            """
            data = list(self._client.query(query))
            return {'min':data[0][0], 'max':data[0][1]}
        else:
            Logger.Log(f"Could not get full date range, BigQuery connection is not open.", logging.WARN)
            return {"min":datetime.now(), "max":datetime.now()}

    def _IDsFromDates(self, min: datetime, max: datetime, versions: Union[List[int],None]=None) -> List[int]:
        str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
        if self._client != None:
            db_name = self._settings["bq_config"]["DB_NAME"]
            table_name = self._settings["bq_config"]["TABLE_NAME"]
            query = f"""
                SELECT DISTINCT param.value.int_value AS session_id
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND _TABLE_SUFFIX BETWEEN '{str_min}' AND '{str_max}'
            """
            data = self._client.query(query)
            ids = [row['session_id'] for row in data]
            return ids if ids != None else []
        else:
            Logger.Log(f"Could not get session list for {str_min}-{str_max} range, BigQuery connection is not open.", logging.WARN)
            return []

    def _datesFromIDs(self, id_list: List[int], versions: Union[List[int],None]=None) -> Dict[str, datetime]:
        if self._client != None:
            db_name = self._settings["bq_config"]["DB_NAME"]
            table_name = self._settings["bq_config"]["TABLE_NAME"]
            id_string = ','.join([f"'{x}'" for x in id_list])
            query = f"""
                WITH datetable AS
                (
                    SELECT event_date, event_timestamp, event_params
                    FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
                    FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
                    FROM `{db_name}.{table_name}`
                )
                SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
                FROM datetable,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
            data = list(self._client.query(query))
            return {'min':data[0][0], 'max':data[0][1]}
        else:
            Logger.Log(f"Could not get date range for {len(id_list)} sessions, BigQuery connection is not open.", logging.WARN)
            return {'min':datetime.now(), 'max':datetime.now()}
