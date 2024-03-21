# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class AverageMoveTypeChanges(SessionFeature):
    def __init__(self, params:ExtractorParameters):
        SessionFeature.__init__(self, params=params)
        self._levels_encountered : set = set()
        self._last_move = {}
        self._change_count = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        _level = event.GameState['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if not _level in self._change_count.keys():
            self._change_count[_level] = 0
            self._last_move[_level] = None
        if self._last_move[_level] != event.EventName:
            self._change_count[_level] += 1
        self._last_move[_level] = event.EventName

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        _counts = [count for count in self._change_count.values()]
        if len(self._levels_encountered) > 0:
            return [sum(_counts) / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***


