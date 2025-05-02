# import standard libraries
import math
from datetime import timedelta
from enum import IntEnum
from typing import Callable, List

# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger

class AlertFollowedByInspect(Detector):
    class Inspection(IntEnum):
        """An enum for the various ways a player could respond to an alert they viewed by inspecting an appropriate building.

        """
        EXCESS_RUNOFF = 1
        SELLING_LOSS = 2

        def __str__(self):
            return self.name

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], inspect_time_threshold:timedelta):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._inspect_threshold = inspect_time_threshold
        self._found_alert = False
        self._alert_type = "ALERT TYPE NOT FOUND!"
        self._last_alert_time = None
        self._last_alert_location = "ALERT TILE INDEX NOT FOUND!"
        self._triggered = None

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["click_local_alert", "click_inspect_building"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        time_since_alert = (event.Timestamp - self._last_alert_time) if self._last_alert_time is not None else timedelta(days=self._inspect_threshold.days + 1)
        within_threshold = time_since_alert < self._inspect_threshold
        match event.EventName:
            case "click_local_alert":
                self._found_alert = True
                self._alert_type = event.EventData.get("alert_type", "ALERT TYPE NOT FOUND!")
                self._last_alert_time = event.Timestamp
                self._last_alert_location = event.EventData.get("tile_index", "ALERT TILE INDEX NOT FOUND!")
            case "click_inspect_building":
                inspect_location = event.EventData.get("tile_index", "INSPECT TILE INDEX NOT FOUND!")
                if self._found_alert and within_threshold and inspect_location == self._last_alert_location:
                    match self._alert_type.upper():
                        case "EXCESSRUNOFF":
                            self._triggered = AlertFollowedByInspect.Inspection.EXCESS_RUNOFF
                        case "SELLINGLOSS":
                            self._triggered = AlertFollowedByInspect.Inspection.SELLING_LOSS
                        case _:
                            pass
            case _:
                pass

    def _trigger_condition(self) -> bool:
        if self._triggered:
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # For now, include the triggering event's EventData, for better debugging.
        ret_val : DetectorEvent = self.GenerateEvent(
            app_id="BLOOM", event_name="alert_followed_by_inspect",
            event_data=self._triggering_event.EventData | {"alert_inspection":str(self._triggered)}
        )
        self._triggered = None
        return ret_val
