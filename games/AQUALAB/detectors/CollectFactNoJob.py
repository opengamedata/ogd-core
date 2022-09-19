# import standard libraries
from datetime import datetime
from typing import Callable, List

# import local files
from extractors.detectors.Detector import Detector
from extractors.detectors.DetectorEvent import DetectorEvent
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class CollectFactNoJob(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._found_jobless_fact = False
        self._sess_id = "Unknown"
        self._player_id = "Unknown"
        self._time = datetime.now()
        self._fact_id = None
        self._app_version = "Unknown"
        self._log_version = "Unknown"

    # *** Implement abstract functions ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["receive_fact"]

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if event.EventData['job_name'] == "no-active-job":
            self._sess_id = event.SessionID
            self._player_id = event.UserID
            self._time = event.Timestamp
            self._found_jobless_fact = True
            self._fact_id = event.EventData['fact_id']
            self._app_version = event.AppVersion
            self._log_version = event.LogVersion
            self._sequence_index = event.EventSequenceIndex
        return

    def _trigger_condition(self) -> bool:
        if self._found_jobless_fact:
            self._found_jobless_fact = False
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : DetectorEvent = DetectorEvent(session_id=self._sess_id, app_id="AQUALAB", timestamp=self._time,
                                                event_name="CollectFactNoJob", event_data={"fact_id":self._fact_id},
                                                app_version=self._app_version, log_version=self._log_version,
                                                user_id=self._player_id, event_sequence_index=self._sequence_index)
        return ret_val
