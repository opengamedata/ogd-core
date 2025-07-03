# import standard libraries
from typing import Callable, Dict, List

# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class TaskCompleteOutsideJob(Detector):
    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], metadata:Dict):
        super().__init__(params=params, trigger_callback=trigger_callback)
        _job_task_map = {elem.get("id") : elem.get("tasks") for elem in metadata.get("jobs", [])}
        self._facts_registry = {}
        self._bestiary_registry = {}
        for job, tasks in _job_task_map:
            for task in tasks:
                for step in task.get("steps", []):
                    match step.get("stepType"):
                        case "AcquireBestiaryEntry":
                            _bestiary_id = step.get("id", "NOT FOUND")
                            if not _bestiary_id in self._bestiary_registry:
                                self._bestiary_registry[_bestiary_id] = []
                            self._bestiary_registry[_bestiary_id].append(job)
                        case "AcquireFact":
                            _fact_id = step.get("id", "NOT FOUND")
                            if not _fact_id in self._facts_registry:
                                self._facts_registry[_fact_id] = []
                            self._facts_registry[_fact_id].append(job)

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["receive_fact"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        self._current_job = event.GameState.get('job_name', event.EventData.get('job_name', None))
        if isinstance(self._current_job, dict):
            self._current_job = self._current_job['string_value']
        if self._current_job is None:
            raise KeyError("Could not find key 'job_name' in GameState or EventData!")
        if self._current_job == "no-active-job":
            self._found_jobless_fact = True
            self._fact_id = event.EventData['fact_id']
        return

    def _trigger_condition(self) -> bool:
        if self._found_jobless_fact:
            self._found_jobless_fact = False
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : DetectorEvent = self.GenerateEvent(app_id="AQUALAB",
                                                     event_name="CollectFactNoJob", event_data={"fact_id":self._fact_id},
                                                     game_state={"job_name":self._current_job})
        return ret_val
