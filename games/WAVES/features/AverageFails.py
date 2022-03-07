from schemas import Event
from typing import Any, List, Union
# local imports
from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageFails(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._levels_encountered : set = set()
        self._fail_count         : int = 0

    def GetEventDependencies(self) -> List[str]:
        return ["FAIL.0"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        if len(self._levels_encountered) > 0:
            return [self._fail_count / len(self._levels_encountered)]
        else:
            return [None]

    def _extractFromEvent(self, event:Event) -> None:
        self._levels_encountered.add(event.event_data['level']) # set-add level to list, at end we will have set of all levels seen.
        self._fail_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


