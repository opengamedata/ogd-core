from typing import Any, List, Set
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.extractors.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class TaskCompleteCount(SessionFeature):

    def __init__(self, params: ExtractorParameters, player_id: str):
        self.completed_tasks: Set[str] = set()
        super().__init__(params=params)

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["target_state_achieved", "click_submit_answer"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.EventName == "target_state_achieved":
            target_state = event.EventData.get("target_state")
            if target_state:
                self.completed_tasks.add(str(target_state))
        elif event.EventName == "click_submit_answer":
            quiz_task = event.EventData.get("quiz_task")
            if quiz_task and quiz_task.get("is_complete"):
                _id = f"{quiz_task.get('lab_name')}_{quiz_task.get('section_number')}_{quiz_task.get('task_number')}"
                self.completed_tasks.add(_id)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [len(self.completed_tasks)]
