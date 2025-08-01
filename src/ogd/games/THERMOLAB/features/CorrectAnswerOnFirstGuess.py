from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


"""

NEED EDIT AS CURRENTLY USING HARD-CODED QUIZ LIST

"""

class CorrectAnswerOnFirstGuess(PerCountFeature):

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.quiz_results: Dict[str, Optional[bool]] = {}
        self.quiz_prompts: Dict[str, str] = {}
        self._quiz_list: List[str] = self._initialize_quiz_list()

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_submit_answer"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _initialize_quiz_list(self) -> List[str]:

        # Example of hard-coded quiz list
        return [
            "1.3.4",  # Lab 1, Section 3, Task 4
            "1.4.2",  # Lab 1, Section 4, Task 2
            "2.1.1",  # Lab 2, Section 1, Task 1
            
        ]

    def _validateEventCountIndex(self, event: Event) -> bool:

        quiz_task = event.EventData.get("quiz_task", {})
        if not quiz_task:
            return False

        lab_name = quiz_task.get("lab_name", "")
        section_number = quiz_task.get("section_number", "")
        task_number = quiz_task.get("task_number", "")

        quiz_id = f"{lab_name}.{section_number}.{task_number}"
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
        quiz_id = f"{lab_name}.{section_number}.{task_number}"


        if quiz_id not in self.quiz_results:
            is_correct = event.EventData.get("is_correct_answer", None)
            self.quiz_results[quiz_id] = is_correct

            prompt = quiz_task.get("prompts", [""])[0] 
            self.quiz_prompts[quiz_id] = prompt

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        """
        Return the correctness of the first guess for the current quiz (indexed by CountIndex).
        """
        quiz_id = self._quiz_list[self.CountIndex]
        return [self.quiz_results.get(quiz_id, None)]
