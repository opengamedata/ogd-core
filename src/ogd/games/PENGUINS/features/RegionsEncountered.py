# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.extractors.features.Feature import Feature
from ogd.core.extractors.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class RegionsEncountered(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        #self._scene_name = None
        self._cnt_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["region_enter"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._object_id = event.event_data.get("region")
        self._cnt_list.append(self._object_id)

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._cnt_list]

    # *** Optionally override public functions. ***