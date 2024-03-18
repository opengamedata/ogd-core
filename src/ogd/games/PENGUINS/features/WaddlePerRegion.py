# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.extractors.features.Feature import Feature
from ogd.games.PENGUINS.features.PerRegionFeature import PerRegionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.extractors.features.SessionFeature import SessionFeature

class WaddlePerRegion(PerRegionFeature):

    def __init__(self, params:ExtractorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params, region_map = region_map)
        self._waddle_count : int = 0
        # self._region_started = False
        # self._cnt_dict = region_map
        # self._curr_region = None
        # self._region_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["player_waddle"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._waddle_count += 1
        # if event.EventName == "player_waddle" and len(self._region_list)>0:
        #     self._curr_region = self._region_list[-1]
            # Logger.Log(f"region lst is {self._region_list}")
            # self._cnt_dict[self._curr_region] += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._waddle_count]

    