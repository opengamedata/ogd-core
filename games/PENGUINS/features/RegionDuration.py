# import libraries
import json
from typing import Any, Dict, List
from datetime import timedelta
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger
# import libraries
import logging
from games.PENGUINS.features.PerRegionFeature import PerRegionFeature
    
class RegionDuration(PerRegionFeature):
    
    def __init__(self, params:ExtractorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params,region_map = region_map)
        self._session_id = None
        self._region_start_time = None
        self._prev_timestamp = None
        self._time = 0
        self._name = None
        self._region_name = None
        self._region_dict = dict()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._region_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._region_start_time).total_seconds()
                self._region_start_time = event.Timestamp

        self._prev_timestamp = event.Timestamp
        if event.EventName == "region_enter":
            self._region_start_time = event.Timestamp
            self._region_name = event.event_data.get("region")
            if not self._region_name in self._region_dict.keys():
                self._region_start_time[self._region_name] = timedelta(0)
        elif event.EventName == "region_exit":
            if self._region_start_time is not None:
                self._time += (event.Timestamp - self._region_start_time).total_seconds()
                self._region_dict[self._region_name]+=timedelta(seconds=self._time)
                self._region_start_time = None

        self._prev_timestamp = event.Timestamp

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._region_dict]


