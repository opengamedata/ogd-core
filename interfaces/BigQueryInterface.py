import logging
from datetime import datetime
from google.cloud import bigquery
from typing import Dict, List

from config import settings
from interfaces.DataInterface import DataInterface
from utils import Logger

class BigQueryInterface(DataInterface):

    def __init__(self, game_id: str):
        super().__init__(game_id=game_id)
        self._settings = settings
        self.Open()

    def _open(self, force_reopen: bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            self._client = bigquery.Client()
            if self._client != None:
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

    def _eventsFromIDs(self, id_list: List[int]) -> List[bigquery.Row]:
        if self._client != None:
            db_name = self._settings["db_config"]["DB_NAME_DATA"]
            table_name = self._settings["db_config"]["TABLE"]
            id_string = ','.join([f"'{x}'" for x in id_list])
            query = f"""
                SELECT event_name, event_date, param.value.int_value AS session_id, event_params
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN ({id_string})
            """
            data = list(self._client.query(query))
            return data if data != None else []
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, BigQuery connection is not open.", logging.WARN)

    def _allIDs(self) -> List[int]:
        if self._client != None:
            db_name = self._settings["db_config"]["DB_NAME_DATA"]
            table_name = self._settings["db_config"]["TABLE"]
            query = f"""
                SELECT DISTINCT param.value.int_value AS session_id
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
            """
            data = self._client.query(query)
            ids = []
            [ids.append(int(row['session_id'])) for row in data]
            return ids if ids != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, BigQuery connection is not open.", logging.WARN)
            return []

    def _fullDateRange(self) -> Dict[str, datetime]:
        if self._client != None:
            db_name = self._settings["db_config"]["DB_NAME_DATA"]
            table_name = self._settings["db_config"]["TABLE"]
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

    def _IDsFromDates(self, min: datetime, max: datetime) -> List[int]:
        if self._client != None:
            db_name = self._settings["db_config"]["DB_NAME_DATA"]
            table_name = self._settings["db_config"]["TABLE"]
            min, max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
            query = f"""
                SELECT DISTINCT param.value.int_value AS session_id
                FROM `{db_name}.{table_name}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND _TABLE_SUFFIX BETWEEN '{min}' AND '{max}'
            """
            data = self._client.query(query)
            ids = []
            [ids.append(int(row['session_id'])) for row in data]
            return ids if ids != None else []
        else:
            Logger.Log(f"Could not get session list for {min}-{max} range, BigQuery connection is not open.", logging.WARN)
            return []

    def _datesFromIDs(self, id_list: List[int]) -> Dict[str, datetime]:
        if self._client != None:
            db_name = self._settings["db_config"]["DB_NAME_DATA"]
            table_name = self._settings["db_config"]["TABLE"]
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
