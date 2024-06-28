# import libraries
import json
from typing import Any, Final, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class FirstInteraction(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    NO_SENSE : Final[str] = 'tunic.historicalsociety.closet.intro'

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._interaction : Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"] 

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        _interaction = event.EventData.get("text_fqid")
        if _interaction is not None and _interaction != FirstInteraction.NO_SENSE and self._interaction is None:
            self._interaction = event.EventData.get("text_fqid")

        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._interaction]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
