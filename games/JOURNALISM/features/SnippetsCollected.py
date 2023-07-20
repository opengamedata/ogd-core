import logging
from datetime import datetime
from schemas import Event
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class SnippetsCollected(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._snippet_ids : List[str] = []


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["snippet_received"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event: Event):
        return self.CountIndex == 1

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "snippet_received":
            self._snippet_ids.append(event.EventData["snippet_id"])

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._snippet_ids]

    # *** Optionally override public functions. ***
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]
