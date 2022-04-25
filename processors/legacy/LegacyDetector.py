# import standard libraries
from datetime import datetime
from typing import Any, List, Union
# import local files
from detectors.Detector import Detector
from schemas.Event import EventSource
from schemas.Event import Event

class LegacyDetector(Detector):
    """Dummy version of a detector, so that LegacyLoader can return something that's not None.
    """

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        return

    def _trigger_condition(self) -> bool:
        return False

    def _trigger_event(self) -> Union[Event, None]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = Event(session_id="Not Implemented", app_id="Not Implemented", timestamp=datetime.now(),
                                event_name="CustomDetector", event_data={}, event_source=EventSource.GENERATED)
        return ret_val

    # *** PUBLIC BUILT-INS and FORMATTERS ***

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0, trigger_callback=lambda x : None)
