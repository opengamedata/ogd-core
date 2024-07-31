# import libraries
from datetime import timedelta
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event, EventSource
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class TotalExperimentationTime(Feature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self.prev_time = timedelta(0)
        self.total_time = timedelta(0)
        self.idle_time = timedelta(0)
        self.on = False

    def Subfeatures(self) -> List[str]: 
        return ["Seconds", "Active", "Active-Seconds", "Idle", "Idle-Seconds"]
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_experiment", "room_changed", "end_experiment"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventSource == EventSource.GAME:
            if self.on:
                self.total_time += (event.Timestamp - self.prev_time)
                if (event.Timestamp - self.prev_time) > timedelta(minutes=1):
                    self.idle_time += (event.Timestamp - self.prev_time)
                if event.EventName == 'end_experiment':
                    self.on = False
            else:
                if event.EventName == "begin_experiment":
                    self.on = True
            self.prev_time = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self.total_time is not None:
            return [self.total_time, self.total_time.total_seconds(), (self.total_time - self.idle_time), (self.total_time - self.idle_time).total_seconds(), self.idle_time, self.idle_time.total_seconds()]
        else:
            return ["No events"]
    # *** Optionally override public functions. ***
