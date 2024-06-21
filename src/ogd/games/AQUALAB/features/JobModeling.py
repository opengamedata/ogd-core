# import libraries
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class JobModeling(PerJobFeature):
    def __init__(self, params:GeneratorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._session_id = None
        self._modeling_start_count : int = 0
        self._modeling_start_time = None
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

            if self._modeling_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._modeling_start_time).total_seconds()
                self._modeling_start_time = event.Timestamp

        if event.EventName == "begin_model":
            self._modeling_start_count += 1
            self._modeling_start_time = event.Timestamp
        elif event.EventName in ["room_changed", "end_model"]:
            if self._modeling_start_time is not None:
                self._time += (event.Timestamp - self._modeling_start_time).total_seconds()
                self._modeling_start_time = None

        self._prev_timestamp = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._modeling_start_count, timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["Time"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
