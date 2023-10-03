import logging
from datetime import datetime
from schemas import Event
from typing import Any, List, Optional
# import locals
from utils.Logger import Logger
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class SnippetsCollected(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._snippet_ids   : List[str] = []
        self._snippet_quals : List[str] = []
        self._snippet_types : List[str] = []


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["snippet_received"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "snippet_received":
            self._snippet_ids.append(event.EventData.get("snippet_id", "SNIPPET ID NOT FOUND"))
            self._snippet_quals.append(event.EventData.get("snippet_quality", "SNIPPET QUALITY NOT FOUND"))
            self._snippet_types.append(event.EventData.get("snippet_type", "SNIPPET TYPE NOT FOUND"))

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._snippet_ids, self._snippet_quals, self._snippet_types]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["Qualities", "Types"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]
