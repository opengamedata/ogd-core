# import libraries
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class MissionSonarTimeToComplete(Extractor):
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._sonar_start_time = None
        self._time = timedelta(0)

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["sonar_start", "sonar_exit"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "sonar_start":
            self._sonar_start_time = event.Timestamp
        elif event.EventName == "sonar_complete":
            if self._sonar_start_time is not None:
                self._time += (event.Timestamp - self._sonar_start_time).total_seconds() # TODO : maybe see if we should add timedeltas and convert to float at end?
                self._sonar_start_time = None

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***