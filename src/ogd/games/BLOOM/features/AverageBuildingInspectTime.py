# import libraries
from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class AverageBuildingInspectTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._inspect_time  = None
        self._inspect_count = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["ManualBuildingInspectTime", "ManualBuildingInspectCount"]

    def _updateFromEvent(self, event: Event) -> None:
        pass

    def _updateFromFeatureData(self, feature: FeatureData):
        if feature.ExportMode == self.ExtractionMode:
            match feature.Name:
                case "ManualBuildingInspectTime":
                    idx = feature.FeatureNames.index("ManualBuildingInspectTime-Seconds")
                    self._inspect_time = feature.FeatureValues[idx]
                case "ManualBuildingInspectCount":
                    self._inspect_count = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        if self._inspect_time is not None and self._inspect_count is not None and self._inspect_count > 0:
            avg = self._inspect_time / self._inspect_count
        else:
            avg = None
        return [ avg ]