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
from extractors.features.SessionFeature import SessionFeature

region_map = {'Mirror':0, 'HillUp':0, 'Entrance':0, 'SnowballBowling':0, 'HillDown':0, 'Bridge':5, 'Chimes':0, 'MatingDPath':0, 'MatingD':0, 'ProtectNestPath':0, 'ProtectNest':0}

class RegionWaddleCount(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._failure_count : int = 0
        self._region_started = False
        self._cnt_dict = region_map.copy()
        self._curr_region = None
        self._region_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["enter_region","player_waddle"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "enter_region":
            self._region_list.append(event.event_data.get("region_name"))
        elif event.EventName == "player_waddle" and len(self._region_list)>0:
            self._curr_region = self._region_list[-1]
            # Logger.Log(f"region lst is {self._region_list}")
            self._cnt_dict[self._curr_region] += 1
        return
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._cnt_dict]

    