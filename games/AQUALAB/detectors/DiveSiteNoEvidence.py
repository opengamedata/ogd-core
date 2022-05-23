# import standard libraries
from datetime import datetime, timedelta
from typing import Any, Callable, List, Optional
# import local files
from detectors.Detector import Detector
from detectors.DetectorEvent import DetectorEvent
from schemas.Event import Event

class DiveSiteNoEvidence(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    # *** Implement abstract functions ***

    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["all_events"]

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if event.EventName == "scene_changed":
            # as soon as scene changes, reset state.
            self._has_triggered = False
            self._time_since_evidence = 0
            scene : str = event.EventData['scene_name']['string_value']
            if scene.startswith("RS-"):
                self._in_dive = True
                # if we just started a dive, use now as starting point for counting time without evidence.
                self._last_evidence_time = event.Timestamp
            else:
                # if we changed to a different scene, reset state.
                self._in_dive = False
                self._last_evidence_time = None
        elif event.EventName == "receive_entity":
            self._last_evidence_time = event.Timestamp

        if self._in_dive and self._last_evidence_time is not None and not self._has_triggered:
            self._time_since_evidence = (event.Timestamp - self._last_evidence_time).total_seconds()
        return
    
    def _trigger_condition(self) -> bool:
        """_summary_
        """
        if self._in_dive and self._time_since_evidence > self._threshold and not self._has_triggered:
            self._has_triggered = True
            return True
        else:
            return False

    def _trigger_event(self) -> Optional[Event]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = DetectorEvent(session_id="Not Implemented", app_id="Not Implemented", timestamp=datetime.now(),
                                        event_name="CustomDetector", event_data={})
        # >>> use state variables to generate the detector's event. <<<
        # >>> definitely don't return all these "Not Implemented" things, unless you really find that useful... <<<
        #
        # e.g. for an (admittedly redundant) Event stating a click of any kind was detected:
        # ret_val : Event = Event(session_id="Unknown", app_id="CustomGame", timestamp=datetime.now(),
        #                         event_name="ClickDetected", event_data={})
        # note the code above doesn't provide much useful information to the Event;
        # we may want to use additional state variables to capture the session_id, app_id, timestamp, etc. from the click Event in _extractFromEvent(...)
        # further note the event_data can contain any extra data you desire; its contents are entirely up to you.
        return ret_val

    # *** BUILT-INS ***

    def __init__(self, name:str, description:str, trigger_callback:Callable[[Event], None], threshold:float):
        super().__init__(name=name, description=description, count_index=0, trigger_callback=trigger_callback)
        self._threshold : float = threshold
        self._in_dive : bool    = False
        self._last_evidence_time  : Optional[datetime] = None
        self._time_since_evidence : float = 0
        self._has_triggered : bool = False

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
