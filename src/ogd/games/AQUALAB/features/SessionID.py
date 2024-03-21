from typing import Any, List

from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.generators.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SessionID(SessionFeature):
    """_summary_

    :param SessionFeature: _description_
    :type SessionFeature: _type_
    """
    def __init__(self, params:ExtractorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._session_id]

    # *** Optionally override public functions. ***
