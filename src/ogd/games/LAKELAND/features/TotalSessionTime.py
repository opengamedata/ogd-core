import json
from typing import Any, List
from datetime import timedelta
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class TotalSessionTime(Extractor):
    def __init__(self, params: GeneratorParameters, threshold: float):
        super().__init__(params=params)
        self.threshold = threshold 
        self.total_time = timedelta(0)
        self.idle_time = timedelta(0)
        self.active_time = timedelta(0)
        self.previous_timestamp = None

    def Subfeatures(self) -> List[str]:
        return ["TotalSeconds", "IdleTime", "IdleSeconds", "ActiveTime", "ActiveSeconds"]

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        # Request all events
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:

        current_timestamp = event.timestamp
        if self.previous_timestamp is not None:
            delta = current_timestamp - self.previous_timestamp
            self.total_time += delta
            if delta.total_seconds() > self.threshold:
                self.idle_time += delta
            else:
                self.active_time += delta
        self.previous_timestamp = current_timestamp


    def _updateFromFeature(self, feature: Feature):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [
            str(self.total_time), 
            self.total_time.total_seconds(),  
            str(self.idle_time), 
            self.idle_time.total_seconds(),  
            str(self.active_time), 
            self.active_time.total_seconds()  
        ]

