# import libraries
from datetime import datetime, timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.Extractor import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AverageSessionTime(Feature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._play_time: timedelta = timedelta(0)
        self._session_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _updateFromEvent(self, event:Event) -> None:
        pass

    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.ExportMode == ExtractionMode.SESSION:
            try:
                self._play_time += feature.FeatureValues[0]
                self._session_count += 1
            except TypeError as err:
                self.WarningMessage(f"TotalPlayTime for player {feature.PlayerID} got non-timedelta value of {feature.FeatureValues[0]}")

    def _getFeatureValues(self) -> List[Any]:
        return [self._play_time / self._session_count]

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]
