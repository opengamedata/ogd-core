from typing import Any, List, Union

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class ActiveJobs(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_started_id = None
        self._active_jobs = { val : [] for val in job_map.values() }

    def GetEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        # Count the top five accepted job ids for each completed job id
        ret_val = dict(self._active_jobs)
        if self._last_started_id is not None:
            if not self._last_started_id in ret_val:
                ret_val[self._last_started_id] = []
            ret_val[self._last_started_id].append(self._current_user_code) # whatever last event was, assume player left off there.
        return [ret_val]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        job_name = event.event_data["job_name"]["string_value"]
        job_id = self._job_map[job_name]

        if self._current_user_code is None:
            self._current_user_code = user_code
        elif self._current_user_code != user_code:
            # if we found a new user, then previous user must have left off on whatever their active job id was.
            self._active_jobs[job_id].append(self._current_user_code)
            # and don't forget to make new user active.
            self._current_user_code = user_code
        self._last_started_id = job_id # for either kind of event, that's the last job we started.

    def _extractFromFeatureData(self, feature: FeatureData):
        return
