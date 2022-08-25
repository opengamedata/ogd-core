# import libraries
from lib2to3.pgen2.token import OP
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class GameScript(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._name : Optional[str] = None
        self._version : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1"]

    def _getFeatureDependencies(self) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        if Event.CompareVersions(event.LogVersion, "7") >= 0:
            self._name = event.EventData.get("script_type")
            self._version = event.EventData.get("script_version")

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._name, self._version]
    
    def Subfeatures(self) -> List[str]:
        return ["Version"]

    def BaseFeatureSuffix(self) -> str:
        return "Name"

