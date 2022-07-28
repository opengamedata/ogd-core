## import standard libraries
import abc
from typing import Callable, List, Optional
# import locals
from extractors.Extractor import Extractor, ExtractorParameters
from extractors.detectors.DetectorEvent import DetectorEvent
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode

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

    # *** BUILT-INS *8jr47t*

    def __init__(self, params:ExtractorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params)
        self._callback    = trigger_callback

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getFeatureDependencies(self) -> List[str]:
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