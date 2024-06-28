# import standard libraries
import math
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode

class RegionEnter(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], region_map:List[Dict[str, Any]]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._region_map = region_map
        self._last_timestamp = datetime.now()
        self._old_region : str = "NoRegion"
        self._new_region : str = "NoRegion"

    # *** Implement abstract functions ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["player_waddle"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        old_position : Dict[str, float]
        new_position : Dict[str, float]

        int_version = int(event.LogVersion) # Penguins just uses an int for the log_version
        match int_version:
            case int_version if int_version <= 9:
                old_position = {
                    'x': event.GameState.get('old_posX', -math.inf),
                    'y': event.GameState.get('old_posY', -math.inf),
                    'z': event.GameState.get('old_posZ', -math.inf)
                }
                new_position = {
                    'x': event.GameState.get('posX', -math.inf),
                    'y': event.GameState.get('posY', -math.inf),
                    'z': event.GameState.get('posZ', -math.inf)
                }
            # New format, up to latest version as of last change to file:
            case int_version if int_version <= 11:
                _pos_old = event.GameState.get("pos_old", [-math.inf, -math.inf, -math.inf])
                _pos_new = event.GameState.get("pos_new", [-math.inf, -math.inf, -math.inf])
                old_position = {
                    'x': _pos_old[0],
                    'y': _pos_old[1],
                    'z': _pos_old[2],
                }
                new_position = {
                    'x': _pos_new[0],
                    'y': _pos_new[1],
                    'z': _pos_new[2],
                }
            # Default to current format as of last change to file:
            case _:
                _pos_old = event.GameState.get("pos_old", [-math.inf, -math.inf, -math.inf])
                _pos_new = event.GameState.get("pos_new", [-math.inf, -math.inf, -math.inf])
                old_position = {
                    'x': _pos_old[0],
                    'y': _pos_old[1],
                    'z': _pos_old[2],
                }
                new_position = {
                    'x': _pos_new[0],
                    'y': _pos_new[1],
                    'z': _pos_new[2],
                }

        # Need to set to "NoRegion" as the default.
        self._old_region = "NoRegion"
        self._new_region = "NoRegion"

        for region in self._region_map:
            if (old_position['x'] > region['minX'] and 
                old_position['x'] < region['maxX'] and
                old_position['y'] > region['minY'] and
                old_position['y'] < region['maxY'] and
                old_position['z'] > region['minZ'] and
                old_position['z'] < region['maxZ']):
                self._old_region = region['name']
            if (new_position['x'] > region['minX'] and 
                new_position['x'] < region['maxX'] and
                new_position['y'] > region['minY'] and
                new_position['y'] < region['maxY'] and
                new_position['z'] > region['minZ'] and
                new_position['z'] < region['maxZ']):
                self._new_region = region['name']
        self._last_timestamp = event.Timestamp
    
    def _trigger_condition(self) -> bool:
        """_summary_
        """
        if (self._old_region != self._new_region) and (self._new_region != "NoRegion"):
            return True
        else:
            return False

    def _trigger_event(self) -> Optional[Event]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = self.GenerateEvent(app_id="PENGUINS", timestamp=self._last_timestamp,
                                             event_name="region_enter", event_data={"region":self._new_region})
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
