# import libraries
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class GameVersion(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._version : Optional[int] = None
        self._log_version: Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1"]

    def _getFeatureDependencies(self) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        self._version = event.AppVersion
        self._log_version = event.LogVersion
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._version, self._log_version]

    def Subfeatures(self) -> List[str]:
        return ["Log"]

