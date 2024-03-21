# import libraries
from lib2to3.pgen2.token import OP
from typing import Any, List, Optional
from ogd.core.generators.Generator import ExtractorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.schemas.Event import Event

class GameScript(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    TYPE = {0: 'Dry', 1: 'No Humor', 2: 'No Snark', 3: 'Normal'}

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._name : Optional[str] = None
        self._version : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        if Event.CompareVersions(event.LogVersion, "7") >= 0:
            _type = event.EventData.get("script_type")
            self._version = event.EventData.get("script_version")
            if _type is not None:
                self._name = GameScript.TYPE.get(_type)
            else:
                raise ValueError(f"")

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._name, self._version]
    
    def Subfeatures(self) -> List[str]:
        return ["Version"]

    def BaseFeatureSuffix(self) -> str:
        return "Name"

