# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageMoveTypeChanges(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._levels_encountered : set = set()
        self._last_move = {}
        self._change_count = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        _level = event.EventData['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if not _level in self._change_count.keys():
            self._change_count[_level] = 0
            self._last_move[_level] = None
        if self._last_move[_level] != event.EventName:
            self._change_count[_level] += 1
        self._last_move[_level] = event.EventName

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        _counts = [count for count in self._change_count.values()]
        if len(self._levels_encountered) > 0:
            return [sum(_counts) / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***


