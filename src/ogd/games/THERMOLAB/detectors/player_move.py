# import standard libraries
from datetime import datetime
from typing import Any, Callable, List, Optional

# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class SliderMoveDetector(Detector):

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._start_val: Optional[float] = None
        self._end_val: Optional[float] = None
        self._slider_grabbed: bool = False

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["slider_grab", "slider_release"]

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "slider_grab":
            self._start_val = event.EventData.get("slider_value", None)
            self._slider_grabbed = True
        elif event.EventName == "slider_release" and self._slider_grabbed:
            self._end_val = event.EventData.get("slider_value", None)
            self._slider_grabbed = False

    def _trigger_condition(self) -> bool:
        # Ensure both start and end values are captured
        if self._start_val is not None and self._end_val is not None:
            return True
        return False

    def _trigger_event(self) -> Optional[DetectorEvent]:
        if self._trigger_condition():
            direction = "up" if self._end_val > self._start_val else "down"
            event_data = {
                "start_val": self._start_val,
                "end_val": self._end_val,
                "direction": direction
            }
            # Create the event and reset state
            ret_val: DetectorEvent = self.GenerateEvent(
                event_name="SliderMoveDetected", event_data=event_data
            )
            # Reset start and end values for the next detection
            self._start_val = None
            self._end_val = None
            return ret_val
        return None
