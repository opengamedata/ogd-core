# import standard libraries
from datetime import datetime, timedelta
from typing import Callable, List, Optional, Union
# import local files
from extractors.detectors.Detector import Detector
from extractors.detectors.DetectorEvent import DetectorEvent
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode

class Idle(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    DEFAULT_IDLE_LEVELS = [30, 60, 90]


    def __init__(self, params:ExtractorParameters, trigger_callback:Callable[[Event], None], idle_levels:Optional[List[int]]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._found = False
        self._sess_id = "Unknown"
        self._player_id = "Unknown"
        self._last_action_time = None
        self._app_version = "Unknown"
        self._log_version = "Unknown"
        self._idle_level = 0
        self._idle_time: Optional[Union[float, timedelta]] = None
        if idle_levels is not None:
            self._idle_threads = sorted(idle_levels)
        else:
            self._idle_threads = Idle.DEFAULT_IDLE_LEVELS

    # *** Implement abstract functions ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["all_events"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if "script" in event.EventName:
            return
        if not self._last_action_time:
            self._last_action_time = event.Timestamp
            return
        self._idle_time = event.Timestamp - self._last_action_time
        self._last_action_time = event.Timestamp
        if self._idle_time > timedelta(seconds = self._idle_threads[0]):
            self._found = True
            self._idle_time = self._idle_time / timedelta(seconds=1)
            for thread in self._idle_threads:
                if self._idle_time < thread:
                    break
                self._idle_level = thread
            self._sess_id = event.SessionID
            self._player_id = event.UserID
            self._time = event.Timestamp
            self._app_version = event.AppVersion
            self._log_version = event.LogVersion
            self._sequence_index = event.EventSequenceIndex
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
        ret_val : DetectorEvent = DetectorEvent(session_id=self._sess_id, app_id="AQUALAB", timestamp=self._time, event_name="Idle", event_data={"level" : self._idle_level, "time": self._idle_time}, app_version=self._app_version, log_version=self._log_version, user_id=self._player_id, event_sequence_index=self._sequence_index)
        return ret_val
