# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class FirstMoveType(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._first_move = None

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # "events": ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"],

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._first_move = event.event_data['slider'][0]

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._first_move]

    # *** Optionally override public functions. ***
