# import standard libraries
from datetime import datetime, timedelta
from time import time
from typing import Callable, List, Optional, Union
# import local files
from extractors.detectors.Detector import Detector
from extractors.detectors.DetectorEvent import DetectorEvent
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode


class HintAndLeave(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    DEFAULT_THRESOLD = 5


    def __init__(self, params:ExtractorParameters, trigger_callback:Callable[[Event], None], time_threshold:Optional[int]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._found = False
        self._sess_id = "Unknown"
        self._player_id = "Unknown"
        self._app_version = "Unknown"
        self._log_version = "Unknown"

        self._scene = "Unknown"
        self._job_name = "Unknown"
        self._hint = "Unknown"
        self._last_hint_time:Optional[datetime] = None
        self._time_spent: Optional[Union[timedelta, float]] = None
        self._detector_event_data: Optional[dict] = None
        if time_threshold is not None:
            self._threshold: Union[timedelta, float] = timedelta(seconds=time_threshold)
        else:
            self._threshold: Union[timedelta, float] = timedelta(
                seconds=HintAndLeave.DEFAULT_THRESOLD)

    # *** Implement abstract functions ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["ask_for_help", "scene_changed", "room_changed"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if self._sess_id == "Unknown":
            self._sess_id = event.SessionID
        elif self._sess_id != event.SessionID:
            self._sess_id = event.SessionID
            self._last_hint_time = None

        if event.EventName == "ask_for_help":
            self._last_hint_time = event.Timestamp
            self._job_name = event.EventData.get("job_name")
            self._hint = event.EventData.get("node_id")
            return

        if not self._last_hint_time:
            return
        self._time_spent = event.Timestamp - self._last_hint_time
        self._last_hint_time = None

        if self._time_spent <= self._threshold:
            self._found = True
            self._time_spent = self._time_spent / timedelta(seconds=1)
            self._sess_id = event.SessionID
            self._player_id = event.UserID
            self._time = event.Timestamp
            self._app_version = event.AppVersion
            self._log_version = event.LogVersion
            self._sequence_index = event.EventSequenceIndex
            if event.EventName == "scene_changed":
                self._scene = event.EventData.get("scene_name")
                self._detector_event_data = {"time": self._time_spent, "level": self._threshold / timedelta(
                    seconds=1), "scene": self._scene, "job_name": self._job_name, "hint_node": self._hint}
            else:
                self._room = event.EventData.get("room_name")
                self._detector_event_data = {"time": self._time_spent, "level": self._threshold / timedelta(
                    seconds=1), "room": self._room, "job_name": self._job_name, "hint_node": self._hint}
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
        ret_val: DetectorEvent = DetectorEvent(session_id=self._sess_id, app_id="AQUALAB", timestamp=self._time,
                                               event_name="HintAndLeave", event_data=self._detector_event_data,
                                               app_version=self._app_version, log_version=self._log_version,
                                               user_id=self._player_id, event_sequence_index=self._sequence_index)
        return ret_val
