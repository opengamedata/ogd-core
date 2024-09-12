from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
COUNTY_LIST = ["Hillside", "Forest", "Prairie", "Wetland", "Urban"]

class CountyUnlockTime(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.time_started: Optional[float] = None
        self.total_time: float = 0.0
        self._start_counting: bool = False

    # Implement abstract functions
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["county_unlocked", "tick"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        event_type = event.EventName

        if event_type == "county_unlocked":
            county = event.EventData.get("county_name")
            if county and self._getCountyIndex(county) == self.CountIndex:
                self._start_counting = True
                self.time_started = event.Timestamp

        elif event_type == "tick" and self._start_counting:
            if self.time_started is not None:
                elapsed_time = event.Timestamp - self.time_started
                self.total_time += elapsed_time
                self.time_started = event.Timestamp  # reset start time

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.total_time]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    def _getCountyIndex(self, county_name: str) -> int:
        try:
            return COUNTY_LIST.index(county_name)
        except ValueError:
            return -1
