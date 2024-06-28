# import libraries
import json
from collections import defaultdict
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class ActiveJobs(Feature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._current_session_id = None
        self._last_started_id = None
        self._active_jobs = defaultdict(list)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["checkpoint"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        session_id = event.SessionID
        mission_name = event.EventData["mission_id"]

        if (self._current_session_id is not None) and (self._current_session_id != session_id) and (self._current_session_id not in self._active_jobs[self._last_started_id]):
            # if we found a new user, then previous user must have left off on whatever their active job was.
            # so, add the user to the list for that job
            self._active_jobs[self._last_started_id].append(self._current_session_id)
        self._current_session_id = session_id # in either case, set latest user as "current"
        self._last_started_id = mission_name # In either case, set latest job name as "current".

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val = self._active_jobs

        if (self._last_started_id is not None) and (self._current_session_id not in self._active_jobs[self._last_started_id]):
            ret_val[self._last_started_id].append(self._current_session_id) # whatever last event was, assume player left off there.

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
