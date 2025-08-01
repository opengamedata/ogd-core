from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class PhosphorusViewUnlocked(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.unlock_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["view_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        _view = event.EventData.get("view_type")
        if _view == "PHOSPHORUS_VIEW":
            self.unlock_count += 1

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.unlock_count > 0, max(self.unlock_count - 1, 0)]

    def Subfeatures(self) -> List[str]:
        return ["Repeats"]