# import libraries
import json
from typing import Any, List, Optional
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils import Logger

# import libraries
import logging

region_map = {'Mirror':0, 'HillUp':1, 'Entrance':2, 'SnowballBowling':3, 'HillDown':4, 'Bridge':5, 'Chimes':6, 'MatingDPath':7, 'MatingD':8, 'ProtectNestPath':9, 'ProtectNest':10}

class WaddlePerRegion(PerCountFeature):
    
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._failure_count = 0
        self._name = None
        self._found = False
        self._count = 0
        self._task_idx = 0
        self._idx = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["exit_region","enter_region","player_waddle"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        # Logger.Log(f"event data is {event.EventData}")
        if event.EventName == "player_waddle":
        #     self._name = event.event_data.get("region_name")
            self._count+=1
        
        
        

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        ret_val : bool = False

        region_data = event.EventData.get("region_name")
        
        if region_data is not None:
            
            if region_map[region_data] == self.CountIndex:
                
                ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val
      