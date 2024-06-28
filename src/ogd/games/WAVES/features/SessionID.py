# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class SessionID(SessionFeature):
    def __init__(self, params:GeneratorParameters, sessionID:str):
        SessionFeature.__init__(self, params=params)
        self._sessionID = sessionID

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._sessionID]

    # *** Optionally override public functions. ***

