from datetime import datetime
from google.cloud import bigquery
from typing import Any, Dict, List, Tuple, Union

from interfaces.DataInterface import DataInterface

class BigQueryInterface(DataInterface):

    def __init__(self, game_id: str):
        super().__init__(game_id=game_id)
        self._open()
        self._eventsFromIDs(None)

    def _open(self, force_reopen: bool = False) -> bool:
        if not self._is_open:
            self._client = bigquery.Client()
            self._is_open = True

        return True

    def _close(self) -> bool:
        self._client.close()
        self._is_open = False

        return True

    def _eventsFromIDs(self, id_list: List[int], versions: Union[List[int], None] = None) -> List[Tuple]:
        query = """
            SELECT *
            FROM `aqualab-57f88.analytics_271167280.events_`
            LIMIT 2
        """
        
        test_query = """
            SELECT corpus AS title, COUNT(word) AS unique_words
            FROM `bigquery-public-data.samples.shakespeare`
            GROUP BY title
            ORDER BY unique_words
            DESC LIMIT 10
        """
        results = self._client.query(query)

        for row in results:
            #title = row['title']
            #unique_words = row['unique_words']
            #print(f'{title:<20} | {unique_words}')
            print(row)

        return (None, results)

    def _allIDs(self) -> List[int]:
        pass

    def _fullDateRange(self) -> Dict[str, datetime]:
        pass

    def _IDsFromDates(self, min: datetime, max: datetime, versions: Union[List[int], None] = None) -> List[int]:
        pass

    def _datesFromIDs(self, id_list: List[int], versions: Union[List[int], None] = None) -> Dict[str, datetime]:
        pass

BigQueryInterface("test")
