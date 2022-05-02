# import libraries
from typing import Any, List, Union
from datetime import timedelta
# import locals
from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class TotalDiveTime(SessionFeature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["dive_start", "dive_exit"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "dive_start":
            self._dive_start_time = event.timestamp
        elif event.event_name == "dive_exit":
            if self._dive_start_time is not None:
                self._time += (event.timestamp - self._dive_start_time).total_seconds()
                self._dive_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
