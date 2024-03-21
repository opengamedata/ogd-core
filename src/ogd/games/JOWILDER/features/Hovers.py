# import libraries
from typing import Any, List, Optional
from ogd.core.generators.Extractor import ExtractorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.schemas.Event import Event

class Hovers(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._hover_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [f"CUSTOM.{i}" for i in range(12, 21)]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        self._hover_count += 1
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._hover_count]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] 
