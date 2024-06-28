# import libraries
from typing import Any, Dict, Final, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class GameScript(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    TYPE : Final[Dict[int, str]] = {0: 'Dry', 1: 'No Humor', 2: 'No Snark', 3: 'Normal'}

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._name : Optional[str] = None
        self._version : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        if Event.CompareVersions(event.LogVersion, "7") >= 0:
            _type = event.EventData.get("script_type")
            self._version = event.EventData.get("script_version")
            if _type is not None:
                self._name = GameScript.TYPE.get(_type)
            else:
                raise ValueError(f"")

        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._name, self._version]
    
    def Subfeatures(self) -> List[str]:
        return ["Version"]

    def BaseFeatureSuffix(self) -> str:
        return "Name"

