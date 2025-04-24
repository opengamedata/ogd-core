# import libraries
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.extractors.builtin.BuiltinExtractor import BuiltinExtractor
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class StopwatchTimer(BuiltinExtractor):
    _start_event = "NO EVENT"
    _end_event   = "NO EVENT"
    _reset_event = "NO EVENT"

    def __init__(self, params: GeneratorParameters, schema_args:Dict[str,Any]):
        super().__init__(params=params, schema_args=schema_args)
        self.previous_time : Optional[datetime] = None
        self.total_time    : timedelta          = timedelta(0)
        self.counting      : bool               = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _createDerivedGenerator(cls, params:GeneratorParameters, schema_args:Dict[str,Any]) -> Type[BuiltinExtractor]:
        class_params = {
            "_start_event" : schema_args.get("start_event", cls._start_event),
            "_end_event"   : schema_args.get("end_event",   cls._end_event),
            "_reset_event" : schema_args.get("reset_event", cls._reset_event)
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
            if event.EventName == self._reset_event:
                self.previous_time = None
            if self.counting and self.previous_time is not None:
                event_duration = event.Timestamp - self.previous_time
                self.total_time += event_duration
            self.previous_time = event.Timestamp
        # if player paused game, we want to start counting paused time
        if event.EventName == self._start_event:
            self.counting = True
        elif event.EventName == self._end_event:
            self.counting = False

    def _updateFromFeatureData(self, feature: FeatureData):
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
