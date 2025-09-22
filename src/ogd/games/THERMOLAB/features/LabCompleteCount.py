from collections import Counter
from typing import Any, List, Set
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
class LabCompleteCount(SessionFeature):
    def __init__(self):
        self.complete_labs = Counter()

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["complete_lab"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        lab = event.EventData.get("lab_name")
        if event is not None and event.EventData.get("percent_complete", 0) >= 100:
            self.complete_labs[lab] += 1

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [len(self.complete_labs)]
