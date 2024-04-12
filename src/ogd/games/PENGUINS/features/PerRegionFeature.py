# import libraries
import logging
import json 
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.schemas.Event import Event



class PerRegionFeature(PerCountFeature):
    def __init__(self, params:GeneratorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params)
        self._region_map = region_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        # region_data = event.EventData["region_name"]
        target_region = self._region_map[self.CountIndex]
        current_position = {
            'x': event.GameState['posX'],
            'y': event.GameState['posY'],
            'z': event.GameState['posZ']
        }

        if (current_position['x'] > target_region['minX'] and 
            current_position['x'] < target_region['maxX'] and
            current_position['y'] > target_region['minY'] and
            current_position['y'] < target_region['maxY'] and
            current_position['z'] > target_region['minZ'] and
            current_position['z'] < target_region['maxZ']):
            ret_val = True
        # else:
        #     self.WarningMessage(f"Got invalid region_name data in {type(self).__name__}")
        return ret_val

        #if region_data is not None:
            #if region_data in self.region_map and self.region_map[region_data] == self.CountIndex:
                #ret_val = True
        #else:
            #self.WarningMessage(f"Got invalid region_name data in {type(self).__name__}")
        #return ret_val

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
