# Global imports
from collections import Counter, defaultdict
from typing import Any, List, Union
# Local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class ActiveJobs(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_started_id = None
        self._active_jobs = { val : 0 for val in job_map.values() }

    def GetEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        # Count the top five accepted job ids for each completed job id
        ret_val = dict(self._active_jobs)
        ret_val[self._last_started_id] += 1 # whatever last event was, assume player left off there.
        return [ret_val]

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.event_data["user_code"]["string_value"]
        job_id = event.event_data["job_id"]["int_value"]

        if self._current_user_code is None:
            self._current_user_code = user_code
        elif self._current_user_code != user_code:
            # if we found a new user, then previous user must have left off on whatever their active job id was.
            self._active_jobs[job_id] += 1
            # and don't forget to make new user active.
            self._current_user_code = user_code
        self._last_started_id = job_id # for either kind of event, that's the last job we started.

    def _extractFromFeatureData(self, feature: FeatureData):
        return
