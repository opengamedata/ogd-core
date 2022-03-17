import json
from collections import defaultdict
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
        self._active_jobs = defaultdict(list)

    def GetEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        ret_val = self._active_jobs

        if self._last_started_id is not None:
            ret_val[self._last_started_id].append(self._current_user_code) # whatever last event was, assume player left off there.

        return [json.dumps(ret_val)]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        job_name = event.event_data["job_name"]["string_value"]

        if self._current_user_code is None:
            self._current_user_code = user_code
        elif self._current_user_code != user_code:
            # if we found a new user, then previous user must have left off on whatever their active job id was.
            self._active_jobs[job_name].append(self._current_user_code)
            # and don't forget to make new user active.
            self._current_user_code = user_code

        self._last_started_id = job_name # for either kind of event, that's the last job we started.

    def _extractFromFeatureData(self, feature: FeatureData):
        return
