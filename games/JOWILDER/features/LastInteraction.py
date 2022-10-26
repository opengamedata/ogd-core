# import libraries
import json
from typing import Any, List, Optional
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class LastInteraction(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    NO_SENSE = 'tunic.historicalsociety.closet.intro'

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._interaction : Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"] 

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        _interaction = event.EventData.get("text_fqid")
        if _interaction is not None and _interaction != LastInteraction.NO_SENSE:
            self._interaction = _interaction

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._interaction]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    