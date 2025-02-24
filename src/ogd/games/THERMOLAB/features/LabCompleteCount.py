from typing import Any, Final, List
from enum import Enum
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class LabCompleteCount(SessionFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.complete_count = 0

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["complete_section"]

    def _updateFromEvent(self, event: Event) -> None:
        # Get the 'section' data from the event
        event_data = event.EventData.get("section", None)
        if event_data:
            is_complete = event_data.get("IsComplete", False)
            if is_complete:
                self.complete_count += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self.complete_count]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromFeatureData(self, feature: FeatureData):
        return
