# import libraries
from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class AveragePhosphorusViewTime(Extractor):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._phos_time  = None
        self._phos_count = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["PhosphorusViewTime", "PhosphorusViewCount"]

    def _updateFromEvent(self, event: Event) -> None:
        pass

    def _updateFromFeature(self, feature: Feature):
        if feature.ExportMode == self.ExtractionMode:
            match feature.Name:
                case "PhosphorusViewTime":
                    idx = feature.FeatureNames.index("PhosphorusViewTime-Seconds")
                    self._phos_time = feature.FeatureValues[idx]
                case "PhosphorusViewCount":
                    self._phos_count = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        if self._phos_time is not None and self._phos_count is not None and self._phos_count > 0:
            avg = self._phos_time / self._phos_count
        else:
            avg = None
        return [ avg ]