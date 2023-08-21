# import libraries
import logging
from typing import Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
region_map = {'Mirror':0, 'HillUp':1, 'Entrance':2, 'SnowballBowling':3, 'HillDown':4, 'Bridge':5, 'Chimes':6, 'MatingDPath':7, 'MatingD':8, 'ProtectNestPath':9, 'ProtectNest':10}
class PerRegionFeature(PerCountFeature):
    def __init__(self, params:ExtractorParameters, region_map:dict):
        super().__init__(params=params,)
        self.region_map = region_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        region_data = event.EventData["region_name"]
        if region_data is not None:
            if region_data in self.region_map and self.region_map[region_data] == self.CountIndex:
                ret_val = True
        else:
            Logger.Log(f"Got invalid region_name data in {type(self).__name__}", logging.WARNING)

        return ret_val

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
