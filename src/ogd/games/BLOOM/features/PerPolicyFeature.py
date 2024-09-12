from typing import List, Any, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class PerPolicyFeature(PerCountFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if self._validateEventCountIndex(event):
            self._incrementCount()

    def _updateFromFeatureData(self, feature: Any):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self._getCount()]

    def _validateEventCountIndex(self, event: Event) -> bool:
        # Get the policy from the event data and check if it matches the count index
        policy = event.EventData.get('policy')
        return policy == self.CountIndex

    def _incrementCount(self) -> None:
        self._count += 1

    def _getCount(self) -> int:
        return getattr(self, '_count', 0)

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
