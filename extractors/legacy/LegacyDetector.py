# import standard libraries
from datetime import datetime
from typing import Any, List, Union
# import local files
from detectors.Detector import Detector
from schemas.Event import Event

class LegacyDetector(Detector):
    """Dummy version of a detector, so that LegacyLoader can return something that's not None.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)

    # *** Implement abstract functions ***
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

    def _trigger(self) -> Union[Event, None]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = Event(session_id="Not Implemented", app_id="Not Implemented", timestamp=datetime.now(),
                                event_name="CustomDetector", event_data={})
        return ret_val
