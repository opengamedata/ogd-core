# import libraries
from datetime import timedelta
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event, EventSource
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from extractors.features.PerCountFeature import PerCountFeature

class TotalCoralTime(Feature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self.prev_time = timedelta(0)
        self.total_time = timedelta(0)
        self.idle_time = timedelta(0)
        self.on = False
        self.coral = 'coral'
### use count index like in region count, then run normal logic after that

    def Subfeatures(self) -> List[str]:
        return ["Seconds", "Active", "Active-Seconds", "Idle", "Idle-Seconds"]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_argument", "room_changed", "leave_argument", "complete_argument"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.app_version == 'Aqualab' or event.app_version == 'None':
            if event.EventSource == EventSource.GAME:
                if self.on:
                    self.total_time += (event.Timestamp - self.prev_time)
                    if (event.Timestamp - self.prev_time) > timedelta(minutes=1):
                        self.idle_time += (event.Timestamp - self.prev_time)
                    if not event.EventData.get('job_name', {}).get('string_value').startswith(self.coral):
                        self.on = False
                else:
                    if event.EventData.get('job_name', {}).get('string_value').startswith(self.coral):
                        self.on = True
                self.prev_time = event.Timestamp
        else:
            if event.EventSource == EventSource.GAME:
                if self.on:
                    self.total_time += (event.Timestamp - self.prev_time)
                    if (event.Timestamp - self.prev_time) > timedelta(minutes=1):
                        self.idle_time += (event.Timestamp - self.prev_time)
                    if not event.EventData.get('job_name', {}).get('string_value').startswith(self.coral):
                        self.on = False
                else:
                    if event.EventData.get('job_name', {}).get('string_value').startswith(self.coral):
                        self.on = True
                self.prev_time = event.Timestamp

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self.total_time is not None:
            return [self.total_time, self.total_time.total_seconds(), (self.total_time - self.idle_time), (self.total_time - self.idle_time).total_seconds(), self.idle_time, self.idle_time.total_seconds()]
        else:
            return ["No events"]

    # *** Optionally override public functions. ***
