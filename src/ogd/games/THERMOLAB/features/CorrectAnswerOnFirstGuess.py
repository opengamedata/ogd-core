from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

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

        if event.EventName == "click_submit_answer":
            quiz_task = event.EventData.get("quiz_task")
            if quiz_task:
                # Convert nested keys to snake_case
                quiz_task = self._convert_keys_to_snake_case(quiz_task)

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

        # Convert nested keys to snake_case
        quiz_task = self._convert_keys_to_snake_case(quiz_task)

        lab_name = quiz_task.get("lab_name", "")
        section_number = quiz_task.get("section_number", "")
        task_number = quiz_task.get("task_number", "")
        prompt = quiz_task.get("prompts", [""])[0]

        quiz_id = f"{lab_name}.{section_number}.{task_number}_{prompt}"

        return quiz_id == self._quiz_list[self.CountIndex]

    def _updateFromEvent(self, event: Event) -> None:
        quiz_task = event.EventData.get("quiz_task", {})
        if not quiz_task:
            return

        # Convert nested keys to snake_case
        quiz_task = self._convert_keys_to_snake_case(quiz_task)

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

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        quiz_id = self._quiz_list[self.CountIndex]
        return [self.quiz_results.get(quiz_id, None)]

    def _convert_keys_to_snake_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        
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
