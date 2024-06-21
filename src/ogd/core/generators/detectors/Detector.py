## import standard libraries
import abc
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
# import locals
from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.utils.typing import Map

## @class Model
#  Abstract base class for session-level Wave Detectors.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on Detectors from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Detector(Generator):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or Detector since last calculation

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _trigger_condition(self) -> bool:
        pass

    @abc.abstractmethod
    def _trigger_event(self) -> DetectorEvent:
        pass

    # *** BUILT-INS & PROPERTIES *8jr47t*

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params)
        self._callback        = trigger_callback
        self._saw_first_event : bool            = False
        # Set up variables for default values of DetectorEvent elements
        self._triggering_event: Event

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """Base function for getting any features a second-order feature depends upon.
        By default, no dependencies.
        Any feature intented to be second-order should override this function.

        :return: _description_
        :rtype: List[str]
        """
        return []

    # *** PUBLIC STATICS ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Detector.

        Overridden from Extractor's version of the function, only makes Detector mode supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.DETECTOR]

    # *** PUBLIC METHODS ***

    def UpdateFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            self._updateFromEvent(event=event)
            if self._trigger_condition():
                self._triggering_event = event
                _new_event = self._trigger_event()
                self._callback(_new_event)

    def GenerateEvent(self, event_name:str,              event_data:Map,
                      session_id:Optional[str]=None,     app_id:Optional[str]=None,
                      timestamp:Optional[datetime]=None, time_offset:Optional[timedelta]=None,
                      app_version:Optional[str]=None,    log_version:Optional[str]=None,
                      user_id:Optional[str] = None,      user_data:Optional[Map] = None,
                      game_state:Optional[Map]=None,     event_sequence_index:Optional[int]=None):
        return DetectorEvent(
            session_id = session_id   or self._triggering_event.SessionID,
            app_id     = app_id       or self._triggering_event.AppID,
            event_name = event_name,  # no default, must be provided
            event_data = event_data,  # no default, must be provided
            timestamp  = timestamp    or self._triggering_event.Timestamp,
            time_offset= time_offset  or self._triggering_event.TimeOffset,
            app_version= app_version  or self._triggering_event.AppVersion,
            log_version= log_version  or self._triggering_event.LogVersion,
            user_id    = user_id      or self._triggering_event.UserID,
            user_data  = user_data    or self._triggering_event.UserData,
            game_state = game_state   or self._triggering_event.GameState,
            event_sequence_index = event_sequence_index or self._triggering_event.EventSequenceIndex
        )

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
