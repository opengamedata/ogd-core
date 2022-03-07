from schemas import Event
from typing import Any, List, Union
# local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class PercentOffsetGoodMoves(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._offset_count = 0
        self._good_count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._good_count / self._offset_count if self._offset_count != 0 else None]

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['slider'].upper() == 'OFFSET':
            self._offset_count += 1
            if event.event_name == "CUSTOM.1":
                if event.event_data['end_closeness'] > event.event_data['begin_closeness']:
                    self._good_count += 1
            elif event.event_name == "CUSTOM.2":
                start_dist = event.event_data['correct_val'] - event.event_data['begin_val']
                end_dist = event.event_data['correct_val'] - event.event_data['end_val']
                if abs(end_dist) < abs(start_dist):
                    self._good_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
