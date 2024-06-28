# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AverageFails(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        SessionFeature.__init__(self, params=params)
        self._levels_encountered : set = set()
        self._fail_count         : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["FAIL.0"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._levels_encountered.add(event.GameState['level']) # set-add level to list, at end we will have set of all levels seen.
        self._fail_count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._levels_encountered) > 0:
            return [self._fail_count / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***
