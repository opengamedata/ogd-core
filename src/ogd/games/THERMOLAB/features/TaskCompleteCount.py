from typing import Any, List, Set
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
import json

class TaskCompleteCount(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self.completed_tasks: Set[str] = set()
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["target_state_achieved", "click_submit_answer"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "target_state_achieved":
            target_state = event.EventData.get("target_state")
            if target_state:
                self.completed_tasks.add(str(target_state))
        elif event.EventName == "click_submit_answer":
            quiz_task = event.EventData.get("quiz_task", [])
            if isinstance(quiz_task, str):
                quiz_task = json.loads(quiz_task)
            
            # Convert nested keys to snake_case
            quiz_task = self._convert_keys_to_snake_case(quiz_task)
            
            if quiz_task and quiz_task.get("is_complete"):
                _id = f"{quiz_task.get('lab_name')}_{quiz_task.get('section_number')}_{quiz_task.get('task_number')}"
                self.completed_tasks.add(_id)

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [len(self.completed_tasks)]

    def _convert_keys_to_snake_case(self, data: dict[str, Any]) -> dict[str, Any]:
        
        #Convert all keys in a dictionary from PascalCase to snake_case.
        
        return {self._to_snake_case(key): value for key, value in data.items()}

    def _to_snake_case(self, name: str) -> str:
        
        #Convert a PascalCase string to snake_case.
    
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
