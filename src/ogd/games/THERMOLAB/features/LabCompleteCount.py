from typing import Any, Final, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
class LabCompleteCount(SessionFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._completed_labs = set()  # Initialize an empty set to store unique lab numbers

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["complete_lab"]  # Filter events where lab completion is recorded

    def _updateFromEvent(self, event: Event) -> None:
        lab = event.EventData.get("lab_name")
        if event is not None and event.EventData.get("percent_complete", 0) >= 100:
            self.complete_labs[lab] += 1

    def _getFeatureValues(self) -> List[Any]:
        # Return the count of unique labs completed (length of the set)
        return [len(self._completed_labs)]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromFeature(self, feature:Feature):
        return
