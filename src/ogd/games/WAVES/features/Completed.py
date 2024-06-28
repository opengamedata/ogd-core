# import libraries
from os import truncate
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class Completed(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._num_completes = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["COMPLETE.0"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._num_completes += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._num_completes > 0, self._num_completes]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Count"]
