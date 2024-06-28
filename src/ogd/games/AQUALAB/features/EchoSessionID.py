# import libraries
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class EchoSessionID(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionID"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
        self._session_id = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        return [f"The sess ID is: {self._session_id}"]

    # *** Optionally override public functions. ***
