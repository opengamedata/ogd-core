# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from features.Feature import Feature
from schemas.Event import Event

class RangeSlope(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***
