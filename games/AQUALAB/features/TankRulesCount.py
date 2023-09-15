# import libraries
from datetime import timedelta
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

TANK_TYPE = [
    "Observation",
    "Stress",
    "Measurement"]

class TankRulesCount(PerCountFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._count = 0
        self._found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["end_experiment", "scene_changed", "begin_experiment", "receive_fact"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "end_experiment" or event.EventName == "scene_changed":
            self._found = False
            return
        if not self._found:
            if event.EventName == "begin_experiment" and event.EventData.get("tank_type") == TANK_TYPE[self.CountIndex]:
                self._found = True
            return
        if event.EventName == "receive_fact":
            self._count += 1
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        return True
