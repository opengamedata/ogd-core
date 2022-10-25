# import libraries
from datetime import datetime
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class JobLocationChanges(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._by_task       : Dict[str, int] = {}
        self._total_count   : int = 0
        self._current_count : int = 0
        self._last_time     : Optional[datetime] = None
        self._last_type     : str = "NO_CHANGE"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["scene_change", "room_change", "complete_task"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "scene_change":
            if self._validateSceneChange(event=event):
                self._current_count += 1
                self._total_count += 1
                self._last_type = event.EventName
                self._last_time = event.Timestamp
        elif event.EventName == "room_change":
            if self._validateRoomChange(event=event):
                self._current_count += 1
                self._total_count += 1
                self._last_type = event.EventName
                self._last_time = event.Timestamp
        elif event.EventName == "complete_task":
            task_id = event.EventData.get("task_id", {}).get("string_value", "UNKNOWN_TASK")
            self._by_task[task_id] = self._current_count
            self._current_count = 0

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._total_count, self._by_task]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["ByTask"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    # *** Private Methods ***

    def _validateSceneChange(self, event:Event):
        if self._last_type == "scene_change":
            return True # if last thing was a scene change, this must be a new change.
        elif self._last_type == "room_change":
            if self._last_time is not None and abs((self._last_time - event.Timestamp).total_seconds()) < 0.01:
                return False # if last thing was a room change, and occurred at effectively the same time, then this is a doubling-up of the two, don't count it.
            else:
                return True # if we haven't encountered a previous time, or the two were separated by some meaningful time, this is a new change.
        else:
            return True # if we didn't encounter a valid previous type of change, then this is a new change

    def _validateRoomChange(self, event:Event):
        if self._last_type == "room_change":
            return True # if last thing was a room change, this must be a new change.
        elif self._last_type == "scene_change":
            if self._last_time is not None and abs((self._last_time - event.Timestamp).total_seconds()) < 0.01:
                return False # if last thing was a scene change, and occurred at effectively the same time, then this is a doubling-up of the two, don't count it.
            else:
                return True # if we haven't encountered a previous time, or the two were separated by some meaningful time, this is a new change.
        else:
            return True # if we didn't encounter a valid previous type of change, then this is a new change
