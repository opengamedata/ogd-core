# import libraries
from typing import Any, List, Optional
from datetime import timedelta
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class TotalDiveTime(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return ["dive_start", "dive_exit"]

    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "dive_start":
            self._dive_start_time = event.Timestamp
        elif event.EventName == "dive_exit":
            if self._dive_start_time is not None:
                self._time += (event.Timestamp - self._dive_start_time).total_seconds()
                self._dive_start_time = None

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
