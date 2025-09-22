from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class SessionHelpCount(Extractor):
    """_summary_

    :param Extractor: _description_
    :type Extractor: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["ask_for_help"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._count += 1

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
