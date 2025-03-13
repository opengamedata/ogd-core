from typing import Any, Dict, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class AnswerAttemptsCount(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self.quiz_attempts: Dict[str, int] = {}
        self.correct_answers: Dict[str, bool] = {}
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_select_answer", "click_submit_answer"]

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "click_select_answer":
            quiz_task = event.EventData.get("quiz_task")
            if quiz_task:
                task_id = f"{quiz_task.get('lab_name')}_{quiz_task.get('section_number')}_{quiz_task.get('task_number')}"
                self.quiz_attempts[task_id] = self.quiz_attempts.get(task_id, 0) + 1
        elif event.EventName == "click_submit_answer":
            quiz_task = event.EventData.get("quiz_task")
            if quiz_task and quiz_task.get("is_complete"):
                task_id = f"{quiz_task.get('lab_name')}_{quiz_task.get('section_number')}_{quiz_task.get('task_number')}"
                self.correct_answers[task_id] = True

    def _getFeatureValues(self) -> List[Any]:
        return [{"attempts": self.quiz_attempts, "correct_answers": self.correct_answers}]
