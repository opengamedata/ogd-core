# import libraries
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.extractors.builtin.BuiltinExtractor import BuiltinExtractor
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class StopwatchTimer(BuiltinExtractor):
    """Built-in feature to count time between occurrences of 'start' and 'stop' events.

    It takes the following parameters:
    * start_event   : The event marking when to start the virtual 'stopwatch'
    * end_event     : The event marking when to stop the virtual 'stopwatch
    * ignore_events : An optional list of events that should be ignored from time counting.
        For example, main-menu events when a player is trying to resume a game after time away.
    * reset_events  : An optional list of events that will be *both* ignored *and* treated as additional end_events.
        For example, a "session_start" event that marks a point where the player resumes the game, but outside a mode that they may have been in when they quit.
    """
    _start_event   = "NO EVENT"
    _end_event     = "NO EVENT"
    _ignore_events = []
    _reset_events  = []

    def __init__(self, params: GeneratorParameters, schema_args:Dict[str,Any]):
        super().__init__(params=params, schema_args=schema_args)
        self.previous_time : Optional[datetime] = None
        self.total_time    : timedelta          = timedelta(0)
        self.counting      : bool               = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _createDerivedGenerator(cls, params:GeneratorParameters, schema_args:Dict[str,Any]) -> Type[BuiltinExtractor]:
        class_params = {
            "_start_event"   : schema_args.get("start_event",   cls._start_event),
            "_end_event"     : schema_args.get("end_event",     cls._end_event),
            "_ignore_events" : schema_args.get("ignore_events", cls._ignore_events),
            "_reset_events"  : schema_args.get("reset_events",  cls._reset_events),
        }
        return type(params._name, (StopwatchTimer,), class_params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    def Subfeatures(self) -> List[str]:
        return ["Seconds"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventSource == EventSource.GAME:
            # Ignore anything in the ignore and reset lists.
            if event.EventName in self._reset_events:
                self.previous_time = None
                self.counting = False
            elif event.EventName in self._ignore_events:
                self.previous_time = None
            # when we're counting, count the stuff
            if self.counting and self.previous_time is not None:
                event_duration = event.Timestamp - self.previous_time
                self.total_time += event_duration
            self.previous_time = event.Timestamp
        # After counting, check if we should start/stop the timer.
        if event.EventName == self._start_event:
            self.counting = True
        elif event.EventName == self._end_event:
            self.counting = False

    def _updateFromFeature(self, feature: Feature):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [
            self.total_time,
            self.total_time.total_seconds()
        ]

    # *** Optionally override public functions ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
