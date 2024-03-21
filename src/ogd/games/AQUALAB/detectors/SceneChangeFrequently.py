# import standard libraries
from datetime import datetime, timedelta
from time import time
from typing import Callable, List, Optional, Union
# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode


class SceneChangeFrequently(Detector):
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
        self._scene_from = "Unknown"
        self._scene_stopby = "Unknown"
        self._scene_at = "Unknown"
        self._app_version = "Unknown"
        self._log_version = "Unknown"
        self._job_name = "Unknown"
        self._last_change_time:Optional[datetime] = None
        self._time_spent: Optional[Union[timedelta, float]] = None
        if time_threshold is not None:
            self._threshold: Union[timedelta, float] = timedelta(seconds=time_threshold)
        else:
            self._threshold: Union[timedelta, float] = timedelta(
                seconds=SceneChangeFrequently.DEFAULT_THRESOLD)

    # *** Implement abstract functions ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["scene_changed"] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if self._sess_id == "Unknown":
            self._sess_id = event.SessionID
        elif self._sess_id != event.SessionID:
            self._sess_id = event.SessionID
            self._last_change_time = None
            self._scene_from = None
            self._scene_stopby = None
            self._scene_at = None
        if not self._last_change_time:
            self._last_change_time = event.Timestamp
            self._scene_stopby = event.EventData.get("scene_name")
            return

        self._time_spent = event.Timestamp - self._last_change_time
        self._last_change_time = event.Timestamp
        self._scene_from = self._scene_stopby
        self._scene_stopby = self._scene_at
        self._scene_at = event.EventData.get("scene_name")
        if self._time_spent <= self._threshold:
            self._found = True
            self._time_spent = self._time_spent / timedelta(seconds=1)
            self._sess_id = event.SessionID
            self._player_id = event.UserID
            self._time = event.Timestamp
            self._app_version = event.AppVersion
            self._log_version = event.LogVersion
            self._sequence_index = event.EventSequenceIndex
            self._job_name = event.GameState.get('job_name', event.EventData.get('job_name', "JOB NAME NOT FOUND"))
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
        ret_val: DetectorEvent = DetectorEvent(session_id=self._sess_id, app_id="AQUALAB", timestamp=self._time, event_name="SceneChangeFrequently", event_data={"time": self._time_spent, "level": self._threshold / timedelta(
            seconds=1), "scene_stopby": self._scene_stopby, "job_name": self._job_name, "scene_from": self._scene_from, "scene_to": self._scene_at}, app_version=self._app_version, log_version=self._log_version, user_id=self._player_id, event_sequence_index=self._sequence_index)
        return ret_val
