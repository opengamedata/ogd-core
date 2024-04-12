# import libraries
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class JobDiveTime(PerJobFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._session_id = None
        self._dive_start_time = None
        self._prev_timestamp = None
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._dive_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._dive_start_time).total_seconds()
                self._dive_start_time = event.Timestamp

        if event.EventName == "begin_dive":
            self._dive_start_time = event.Timestamp
        elif event.EventName == "scene_changed":
            if self._dive_start_time is not None:
                self._time += (event.Timestamp - self._dive_start_time).total_seconds()
                self._dive_start_time = None

        self._prev_timestamp = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
