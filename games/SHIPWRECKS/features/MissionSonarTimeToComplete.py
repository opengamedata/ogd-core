# import libraries
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class MissionSonarTimeToComplete(Feature):
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._sonar_start_time = None
        self._time = timedelta(0)

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["sonar_start", "sonar_exit"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "sonar_start":
            self._sonar_start_time = event.Timestamp
        elif event.EventName == "sonar_complete":
            if self._sonar_start_time is not None:
                self._time += (event.Timestamp - self._sonar_start_time).total_seconds() # TODO : maybe see if we should add timedeltas and convert to float at end?
                self._sonar_start_time = None

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***