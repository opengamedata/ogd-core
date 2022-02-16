# Global imports
from collections import Counter, defaultdict
from typing import Any, List, Union
# Local imports
from extractors.Feature import Feature
from schemas.Event import Event

class TopJobDestinations(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_completed_id = None
        self._job_pairs = defaultdict(list)
        self._top_destinations = {}

        # Populate dict with an empty list for each possible job id
        for job_id in job_map.values():
            self._top_destinations[job_id] = []

    def GetEventTypes(self) -> List[str]:
        return ["accept_job", "complete_job"]

    def GetFeatureValues(self) -> List[Any]:
        # Count the top five accepted job ids for each completed job id
        for key in self._job_pairs.keys():
            self._top_destinations[key] = Counter(self._job_pairs[key]).most_common(5)

        return [self._top_destinations]

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.event_data["user_code"]["string_value"]
        job_id = event.event_data["job_id"]["int_value"]

        if event.event_name == "complete_job":
            self._current_user_code = user_code
            self._last_completed_id = event.event_data["job_id"]["int_value"]
        elif event.event_name == "accept_job" and user_code == self._current_user_code:
            self._job_pairs[self._last_completed_id].append(job_id)
            self._last_completed_id = None
