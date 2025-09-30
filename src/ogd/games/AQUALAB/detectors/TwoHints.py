# import standard libraries
from datetime import datetime, timedelta
from time import time
from typing import Callable, Final, List, Optional, Union
# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.typing import Map


class TwoHints(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    DEFAULT_THRESOLD : Final[int] = 5

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], time_threshold:Optional[int]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        # 1. Get custom params
        self._threshold : timedelta
        if time_threshold is not None:
            self._threshold = timedelta(seconds=time_threshold)
        else:
            self._threshold = timedelta(seconds=TwoHints.DEFAULT_THRESOLD)

        # 2. Create state variables
        self._found = False
        self._sess_id            : Optional[str]       = None
        self._job_name           : str                 = "Unknown"
        self._first_hint         : Optional[str]       = None
        self._second_hint        : Optional[str]       = None
        self._first_hint_time    : Optional[datetime]  = None
        self._time_between_hints : Optional[timedelta] = None

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["ask_for_help"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        # 1. If first event we ever saw, just keep track of the session ID.
        if self._sess_id is None:
            self._sess_id = event.SessionID
        # 2. Otherwise, if found new session ID, switch to it and reset.
        elif self._sess_id != event.SessionID:
            self._sess_id = event.SessionID
            self._first_hint_time = None
        # 3. If we don't have a previous hint marked, mark this as the first hint.
        if not self._first_hint_time:
            self._first_hint_time = event.Timestamp
            self._first_hint = event.EventData.get("node_id", "HINT node_id NOT FOUND")
        # 4. If we did have previous hint, mark this as the second hint and record relevant state variables.
        else:
            self._second_hint = event.EventData.get("node_id", "HINT node_id NOT FOUND")
            self._time_between_hints = event.Timestamp - self._first_hint_time
            self._job_name = event.GameState.get('job_name', event.EventData.get('job_name', "JOB NAME NOT FOUND"))
        return

    def _trigger_condition(self) -> bool:
        if self._second_hint is not None and self._time_between_hints is not None:
            return self._time_between_hints.total_seconds() <= self._threshold.total_seconds()
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # 1. Create Event
        _detector_event_data = {
            "time": self._time_between_hints,
            "threshold": self._threshold.total_seconds(),
            "job_name": self._job_name,
            "last_hint_node": self._first_hint,
            "this_hint_node": self._second_hint
        }
        ret_val: DetectorEvent = self.GenerateEvent(event_name="TwoHints", event_data=_detector_event_data)
        # 2. Cleanup
        self._first_hint = None
        self._second_hint = None
        self._first_hint_time = None
        self._time_between_hints = None
        self._job_name = "Unknown"
        return ret_val
