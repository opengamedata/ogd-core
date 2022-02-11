# Global imports
import logging
from collections import Counter
from typing import Any, List, Union
# Local imports
import utils
from extractors.Feature import Feature
from schemas.Event import Event

class TopJobDestinations(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._current_user_code = None
        self._last_completed_id = None
        self._job_pairs = []

    def GetEventTypes(self) -> List[str]:
        return ["accept_job", "complete_job"]

    def GetFeatureValues(self) -> List[Any]:
        return Counter(self._job_pairs).most_common(5)

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.event_data["job_id"]):
            user_code = event.event_data["user_code"]["string_value"]
            job_id = event.event_data["job_id"]["int_value"]

            if event.event_name == "complete_job" and job_id == self._count_index:
                self._current_user_code = user_code
                self._last_completed_id = event.event_data["job_id"]["int_value"]
            elif event.event_name == "accept_job" and self._current_user_code == user_code:
                self._job_pairs.append((self._last_completed_id, job_id))
                self._last_completed_id = None

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['int_value'] is not None:
            if job_data['int_value'] == self._count_index:
                ret_val = True
        elif job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            utils.Logger.toStdOut(f"Got invalid job_id data in TopJobDestinations", logging.WARNING)
        return ret_val
