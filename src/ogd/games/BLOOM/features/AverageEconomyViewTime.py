# import libraries
from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class AverageEconomyViewTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._econ_time  = None
        self._econ_count = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["EconomyViewTime", "EconomyViewCount"]

    def _updateFromEvent(self, event: Event) -> None:
        pass

    def _updateFromFeatureData(self, feature: FeatureData):
        if feature.ExportMode == self.ExtractionMode:
            match feature.Name:
                case "EconomyViewTime":
                    idx = feature.FeatureNames.index("EconomyViewTime-Seconds")
                    self._econ_time = feature.FeatureValues[idx]
                case "EconomyViewCount":
                    self._econ_count = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        if self._econ_time is not None and self._econ_count is not None and self._econ_count > 0:
            avg = self._econ_time / self._econ_count
        else:
            avg = None
        return [ avg ]