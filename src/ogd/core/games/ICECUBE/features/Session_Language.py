from typing import Any, List

from typing import Any, Dict, List, Optional
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.extractors.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class Session_Language(SessionFeature):
    """_summary_

    :param SessionFeature: _description_
    :type SessionFeature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        self._session_language = None
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ['language_selected']

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._session_language = event.EventData.get("language")

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._session_language]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"