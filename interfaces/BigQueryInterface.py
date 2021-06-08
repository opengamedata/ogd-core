import logging
import math
from datetime import datetime
from google.cloud import bigquery
from typing import Any, Dict, List, Tuple, Union

from interfaces.DataInterface import DataInterface
from utils import Logger

class BigQueryInterface(DataInterface):

    def __init__(self, game_id: str):
        super().__init__(game_id=game_id)
        self._open()
        self._test()

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

    def _test(self):
        query = """
            SELECT event_name, param.value.int_value AS id
            FROM `aqualab-57f88.analytics_271167280.events_20210607`,
            UNNEST(event_params) AS param
            WHERE param.key = "ga_session_id"
            AND param.value.int_value IN (1623093427, 1623073002, 1623092659)
        """
        #[1623009463, 1623024789] 06
        #[1623093427, 1623073002, 1623092659, 1623069624] 07

        results = self._client.query(query)

        for row in results:
            print(row)
        
        ids = []
        [ids.append(int(row['id'])) for row in results if int(row['id']) not in ids]
        print(ids)

        return results

    def _eventsFromIDs(self, id_list: List[int], versions: Union[List[int], None] = None) -> List[Tuple]:
        if self._client != None:
            id_string = ','.join([f"'{x}'" for x in id_list])
            session_filter = f"param.value.int_value IN ({id_string})"
            query = """
                SELECT event_name, param.value.int_value AS id
                FROM `aqualab-57f88.analytics_271167280.events_20210607`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                AND param.value.int_value IN (1623093427, 1623073002, 1623092659)
            """
            data = self._client.query(query)
            return data if data != None else []
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, BigQuery connection is not open.", logging.WARN)

    def _allIDs(self) -> List[int]:
        if self._client != None:
            query = """
                SELECT event_name, param.value.int_value AS id
                FROM `aqualab-57f88.analytics_271167280.events_20210606`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
            """
            data = self._client.query(query)
            ids = []
            [ids.append(int(row['id'])) for row in data if int(data['id']) not in ids]
            return ids if ids != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, BigQuery connection is not open.", logging.WARN)
            return []

    def _fullDateRange(self) -> Dict[str, datetime]:
        if self._client != None:
            data = SELECT(columns=["MIN(event_timestamp)", "MAX(event_timestamp)"])
            return {"min":result[0][0], "max":result[0][1]}
        else:
            Logger.Log(f"Could not get full date range, BigQuery connection is not open.", logging.WARN)
            return {"min":datetime.now(), "max":datetime.now()}

    def _IDsFromDates(self, min: datetime, max: datetime, versions: Union[List[int], None] = None) -> List[int]:
        pass

    def _datesFromIDs(self, id_list: List[int], versions: Union[List[int], None] = None) -> Dict[str, datetime]:
        pass

BigQueryInterface("test")
