# import standard libraries
from datetime import datetime
from typing import Callable, List
# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class EchoRoomChange(Detector):
    """Simple working example of a detector for Aqualab.

    Not intended for "real" usage.
    Instead, use as a simple example for reviewing how to write event detectors.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params, trigger_callback=trigger_callback)

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["room_changed"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        self._found = True
        return

    def _trigger_condition(self) -> bool:
        return self._found

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # 1. Create Event
        ret_val : DetectorEvent = self.GenerateEvent(event_name="EchoRoomChange", event_data={})
        # 2. Cleanup
        self._found = False
        return ret_val
