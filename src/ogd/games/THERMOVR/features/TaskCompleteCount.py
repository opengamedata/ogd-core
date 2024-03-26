from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class TaskCompleteCount(SessionFeature):

    def __init__(self, params:GeneratorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._task_complete_count = 0

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["game_state"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.UserID == self._player_id:
            current_task = event.GameState.get('current_task', None)
            if current_task and current_task.get('is_complete', False):
                self._task_complete_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._task_complete_count]
