## import standard libraries
import abc
from typing import Any, Callable, Dict, List, Optional
# import locals
from ogd.core.extractors.Extractor import Extractor, ExtractorParameters
from ogd.core.extractors.detectors.DetectorEvent import DetectorEvent
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

## @class Model
#  Abstract base class for session-level Wave Detectors.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on Detectors from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Detector(Extractor):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or Detector since last calculation

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _trigger_condition(self) -> bool:
        pass

    @abc.abstractmethod
    def _trigger_event(self) -> DetectorEvent:
        pass

    # *** BUILT-INS & PROPERTIES *8jr47t*

    def __init__(self, params:ExtractorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params)
        self._callback        = trigger_callback
        self._saw_first_event : bool          = False
        # Set up variables for default values of DetectorEvent elements
        self._session_id      : str           = "UNKNOWN"
        self._app_id          : str           = "UNKNOWN"
        self._app_version     : Optional[str] = None
        self._log_version     : Optional[str] = None
        self._user_id         : Optional[str] = None
        self._user_data       : Optional[Map] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        """Base function for getting any features a second-order feature depends upon.
        By default, no dependencies.
        Any feature intented to be second-order should override this function.

        :return: _description_
        :rtype: List[str]
        """
        return []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ExtractFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            if not self._saw_first_event:
                self._firstEvent(event=event)
                self._saw_first_event = True
            self._extractFromEvent(event=event)
            if self._trigger_condition():
                _event = self._trigger_event()
                # TODO: add some logic to fill in empty values of Event with reasonable defaults, where applicable.
                self._callback(_event)

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Detector.

        Overridden from Extractor's version of the function, only makes Detector mode supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.DETECTOR]

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _firstEvent(self, event:Event):
        self._session_id = event.SessionID
        self._app_id = event.AppID
        self._app_version = event.AppVersion
        self._log_version = event.LogVersion
        self._user_id = event.UserID
        self._user_data = event.UserData