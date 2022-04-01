# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from features.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class OffsetGoodMoveCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['slider'].upper() == 'OFFSET':
            if event.event_name == "CUSTOM.1":
                if event.event_data['end_closeness'] > event.event_data['begin_closeness']:
                    self._count += 1
            elif event.event_name == "CUSTOM.2":
                start_dist = event.event_data['correct_val'] - event.event_data['begin_val']
                end_dist = event.event_data['correct_val'] - event.event_data['end_val']
                if abs(end_dist) < abs(start_dist):
                    self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
