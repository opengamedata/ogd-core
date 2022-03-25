import json
from collections import defaultdict
from typing import Any, List, Union

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class ActiveJobs(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._current_session_id = None
        self._last_started_id = None
        self._active_jobs = defaultdict(list)

    def GetEventDependencies(self) -> List[str]:
        return ["checkpoint"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        ret_val = self._active_jobs

        if self._last_started_id is not None:
            ret_val[self._last_started_id].append(self._current_session_id) # whatever last event was, assume player left off there.

        return [json.dumps(ret_val)]

    def _extractFromEvent(self, event:Event) -> None:
        session_id = event.session_id
        mission_name = event.event_data["mission_id"]["string_value"]

        if (self._current_session_id is not None) and (self._current_session_id != session_id):
            # if we found a new user, then previous user must have left off on whatever their active job was.
            # so, add the user to the list for that job
            self._active_jobs[self._last_started_id].append(self._current_session_id)
        self._current_session_id = session_id # in either case, set latest user as "current"
        self._last_started_id = mission_name # In either case, set latest job name as "current".

    def _extractFromFeatureData(self, feature: FeatureData):
        return
