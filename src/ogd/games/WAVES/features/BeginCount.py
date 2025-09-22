# import libraries
from ogd.common.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class BeginCount(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._num_begins = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["BEGIN.0"]
        # return ["BEGIN"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._num_begins += 1

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._num_begins]

    # *** Optionally override public functions. ***
