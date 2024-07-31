# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class PersistentSessionID(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        SessionFeature.__init__(self, params=params)
        self._persistent_id : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["BEGIN.0"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if self._persistent_id is None:
            self._persistent_id = event.UserData['persistent_session_id']

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._persistent_id]

    # *** Optionally override public functions. ***


