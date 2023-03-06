# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from games.PENGUINS.features.PerRegionFeature import PerRegionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from extractors.features.PerCountFeature import PerCountFeature

region_map = {'Mirror':0, 'HillUp':1, 'Entrance':2, 'SnowballBowling':3, 'HillDown':4, 'Bridge':5, 'Chimes':6, 'MatingDPath':7, 'MatingD':8, 'ProtectNestPath':9, 'ProtectNest':10}

class RegionEnterCount(PerCountFeature):

    def __init__(self, params:ExtractorParameters):
        self._region_map = region_map
        super().__init__(params=params)
        self._current_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["enter_region"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._current_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._current_count]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        ret_val : bool = False

        region_data = event.EventData.get("region_name")
        if region_data is not None:
            if region_data in region_map and region_map[region_data] == self.CountIndex:
                ret_val = True
        else:
            Logger.Log(f"Got invalid region data in {type(self).__name__}", logging.WARNING)

        return ret_val