# import libraries
from typing import Any, List, Optional, Union
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class GameVersion(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._version    : Union[str,int,None] = None
        self._log_version: Union[str,int,None] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        self._version = event.AppVersion
        self._log_version = event.LogVersion
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._version, self._log_version]

    def Subfeatures(self) -> List[str]:
        return ["Log"]

