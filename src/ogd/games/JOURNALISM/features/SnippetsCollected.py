import logging
from datetime import datetime
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class SnippetsCollected(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._snippet_ids   : List[str] = []
        self._snippet_quals : List[str] = []
        self._snippet_types : List[str] = []


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["snippet_received"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "snippet_received":
            self._snippet_ids.append(event.EventData.get("snippet_id", "SNIPPET ID NOT FOUND"))
            self._snippet_quals.append(event.EventData.get("snippet_quality", "SNIPPET QUALITY NOT FOUND"))
            self._snippet_types.append(event.EventData.get("snippet_type", "SNIPPET TYPE NOT FOUND"))

    def _updateFromFeatureData(self, feature: FeatureData):
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
