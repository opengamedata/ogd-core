# import libraries
from typing import Any, List, Optional
from ogd.core.generators.Extractor import ExtractorParameters
# import local files
from ogd.core.generators.features.SessionFeature import SessionFeature
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.schemas.Event import Event

class UsedSaveCode(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._save_code : Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData.get("save_code") != 0:
            self._save_code = str(event.EventData.get("save_code"))

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._save_code]

