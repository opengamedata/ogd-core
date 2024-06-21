# import libraries
from typing import Any, Final, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class UsedContinue(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    START_SIGN : Final[str] = "tunic.historicalsociety.closet.gramps.intro_0_cs_0"

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._continue : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["FirstInteraction", "UsedSaveCode"] 

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        if feature.FeatureType == "UsedSaveCode":
            self._save_code = feature.FeatureValues[0]
        elif feature.FeatureType == "FirstInteraction":
            self._first_inc = feature.FeatureValues[0]
        return

    def _getFeatureValues(self) -> List[Any]:
        if not self._save_code and self._first_inc != UsedContinue.START_SIGN:
            self._continue = 1
        return [self._continue]
