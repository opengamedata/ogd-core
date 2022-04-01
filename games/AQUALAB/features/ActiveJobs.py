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

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        job_name = event.event_data["job_name"]["string_value"]

        if (self._current_user_code is not None) and (self._current_user_code != user_code):
            # if we found a new user, then previous user must have left off on whatever their active job was.
            # so, add the user to the list for that job
            self._active_jobs[self._last_started_id].append(self._current_user_code)
        self._current_user_code = user_code # in either case, set latest user as "current"
        self._last_started_id = job_name # In either case, set latest job name as "current".

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val = self._active_jobs

        if self._last_started_id is not None:
            ret_val[self._last_started_id].append(self._current_user_code) # whatever last event was, assume player left off there.

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Union[str,None]:
        return "1"
