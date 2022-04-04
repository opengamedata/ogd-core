# import standard libraries
from datetime import datetime
from typing import Any, List, Union

from chardet import detect
# import local files
from detectors.Detector import Detector
from schemas.Event import Event

class CollectFactNoJob(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._sess_id = "Unknown"
        self._time = datetime.now()

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["receive_fact"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if event.event_data['job_name'] == "no-active-job":
            self._sess_id = event.session_id
            self._time = event.timestamp
            self.Trigger()
        return

    def _trigger(self) -> Union[Event, None]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = Event(session_id=self._sess_id, app_id="AQUALAB", timestamp=self._time,
                                event_name="CollectFactNoJob", event_data={})
        return ret_val
