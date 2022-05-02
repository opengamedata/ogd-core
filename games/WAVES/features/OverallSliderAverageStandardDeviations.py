# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class OverallSliderAverageStandardDeviations(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._std_devs = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._std_devs.append(event.event_data["stdev_val"])

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._std_devs) > 0:
            return [sum(self._std_devs) / len(self._std_devs)]
        else:
            return [None]

    # *** Optionally override public functions. ***


