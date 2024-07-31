# import libraries
import json
import logging
import math 
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event



class PerRegionFeature(PerCountFeature):
    def __init__(self, params:GeneratorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params)
        self._region_map = region_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False
        current_position : Dict[str, float]

        int_version = int(event.LogVersion)
        match int_version:
            # Old format
            case int_version if int_version <= 9:
                current_position = {
                    'x': event.GameState.get('posX', -math.inf),
                    'y': event.GameState.get('posY', -math.inf),
                    'z': event.GameState.get('posZ', -math.inf)
                }
            # New format, up to latest version as of last change to file:
            case int_version if int_version <= 11:
                _pos = event.GameState.get("pos", [-math.inf, -math.inf, -math.inf])
                if isinstance(_pos, str):
                    try:
                        _pos = json.loads(_pos)
                    except json.JSONDecodeError as err:
                        fix_dumb_fucking_data_error = _pos[:-2] + "]"
                        _pos = json.loads(fix_dumb_fucking_data_error)
                current_position = {
                    'x': _pos[0],
                    'y': _pos[1],
                    'z': _pos[2]
                }
            # Default to current format as of last change to file:
            case _:
                _pos = event.GameState.get("pos", [-math.inf, -math.inf, -math.inf])
                if isinstance(_pos, str):
                    try:
                        _pos = json.loads(_pos)
                    except json.JSONDecodeError as err:
                        fix_dumb_fucking_data_error = _pos[:-2] + "]"
                        _pos = json.loads(fix_dumb_fucking_data_error)
                current_position = {
                    'x': _pos[0],
                    'y': _pos[1],
                    'z': _pos[2]
                }


        # region_data = event.EventData["region_name"]
        target_region = self._region_map[self.CountIndex]

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
