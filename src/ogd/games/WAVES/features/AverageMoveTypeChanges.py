# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AverageMoveTypeChanges(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        SessionFeature.__init__(self, params=params)
        self._levels_encountered : set = set()
        self._last_move = {}
        self._change_count = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        _level = event.GameState['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if not _level in self._change_count.keys():
            self._change_count[_level] = 0
            self._last_move[_level] = None
        if self._last_move[_level] != event.EventName:
            self._change_count[_level] += 1
        self._last_move[_level] = event.EventName

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        _counts = [count for count in self._change_count.values()]
        if len(self._levels_encountered) > 0:
            return [sum(_counts) / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***


