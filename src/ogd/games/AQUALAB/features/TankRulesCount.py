# import libraries
from datetime import timedelta
from typing import Any, Final, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

TANK_TYPE : Final[List[str]] = [
    "Observation",
    "Stress",
    "Measurement"]

class TankRulesCount(PerCountFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._count = 0
        self._found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["end_experiment", "scene_changed", "begin_experiment", "receive_fact"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
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

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        return True
