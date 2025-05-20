from typing import Any, List
from datetime import timedelta
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class TotalPlayTime(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self.total_time = timedelta(0)
        self.session_start_time = None
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["session_start", "headset_on", "headset_off"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "session_start":
            self.session_start_time = event.Timestamp
        elif event.EventName == "headset_on":
            self.session_start_time = event.Timestamp
        elif event.EventName == "headset_off" and self.session_start_time:
            self.total_time += event.Timestamp - self.session_start_time
            self.session_start_time = None

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.total_time.total_seconds()]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromFeatureData(self, feature: FeatureData):
        return