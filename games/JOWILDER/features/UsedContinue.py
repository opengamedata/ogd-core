# import libraries
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class UsedContinue(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    START_SIGN = "tunic.historicalsociety.closet.gramps.intro_0_cs_0"

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._continue : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["FirstInteraction", "UsedSaveCode"] 

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.FeatureType == "UsedSaveCode":
            self._save_code = feature.FeatureValues[0]
        elif feature.FeatureType == "FirstInteraction":
            self._first_inc = feature.FeatureValues[0]
        
        return

    def _getFeatureValues(self) -> List[Any]:
        if not self._save_code and self._first_inc != UsedContinue.START_SIGN:
            self._continue = 1
        return [self._continue]


