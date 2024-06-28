# import standard libraries
from datetime import datetime
from typing import Callable, List
# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode

class EchoRoomChange(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

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
        return ["room_changed"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        self._found = True
        return

    def _trigger_condition(self) -> bool:
        if self._found:
            self._found = False
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : DetectorEvent = self.GenerateEvent(event_name="EchoRoomChange", event_data={})
        return ret_val
