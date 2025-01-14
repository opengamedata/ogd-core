from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode


class CorrectAnswerOnFirstGuess(PerCountFeature):

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.quiz_results: Dict[str, Optional[bool]] = {}
        self.quiz_prompts: Dict[str, str] = {}
        self._quiz_list: List[str] = []  # We'll initialize this dynamically

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_submit_answer"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _initialize_quiz_list(self, event: Event) -> List[str]:
        quizzes = set()

        for e in event:
            if e.EventType == "click_submit_answer":
                quiz_task = e.EventData.get("quiz_task")
                if quiz_task:
                    lab_name = quiz_task.get("lab_name", "")
                    section_number = quiz_task.get("section_number", "")
                    task_number = quiz_task.get("task_number", "")
                    prompt = quiz_task.get("prompts", [])

  
                    quiz_id = f"{lab_name}.{section_number}.{task_number}"
                    if prompt:
                        quiz_id += f"_{prompt[0]}" 
                    quizzes.add(quiz_id)

        return list(quizzes)

    def _validateEventCountIndex(self, event: Event) -> bool:
        quiz_task = event.EventData.get("quiz_task", {})
        if not quiz_task:
            return False

        lab_name = quiz_task.get("lab_name", "")
        section_number = quiz_task.get("section_number", "")
        task_number = quiz_task.get("task_number", "")
        prompt = quiz_task.get("prompts", [""])[0]

        quiz_id = f"{lab_name}.{section_number}.{task_number}_{prompt}"

        return quiz_id == self._quiz_list[self.CountIndex]

    def _updateFromEvent(self, event: Event) -> None:
        """
        Update feature values based on the event data.
        """
        quiz_task = event.EventData.get("quiz_task", {})
        if not quiz_task:
            return

        lab_name = quiz_task.get("lab_name", "")
        section_number = quiz_task.get("section_number", "")
        task_number = quiz_task.get("task_number", "")
        prompt = quiz_task.get("prompts", [""])[0]

        quiz_id = f"{lab_name}.{section_number}.{task_number}_{prompt}"

        # Add the quiz ID dynamically if it's a new one
        if quiz_id not in self.quiz_results:
            is_correct = event.EventData.get("is_correct_answer", None)
            self.quiz_results[quiz_id] = is_correct


            self.quiz_prompts[quiz_id] = prompt

    def _getFeatureValues(self) -> List[Any]:
        quiz_id = self._quiz_list[self.CountIndex]
        return [self.quiz_results.get(quiz_id, None)]
