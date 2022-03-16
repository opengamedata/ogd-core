from collections import Counter, defaultdict
from typing import Any, List, Union

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TopJobSwitchDestinations(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_started_id = None
        self._job_switch_pairs = defaultdict(list)
        self._top_destinations = defaultdict(list)

    def GetEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        # Count the top five accepted job ids for each completed job id
        for key in self._job_switch_pairs.keys():
            self._top_destinations[str(key)] = Counter(self._job_switch_pairs[key]).most_common(5)

        return [dict(self._top_destinations)]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        job_name = event.event_data["job_name"]["string_value"]
        job_id = self._job_map[job_name]

        if event.event_name == "accept_job":
            self._last_started_id = job_id
        elif event.event_name == "switch_job":
            if user_code == self._current_user_code and self._last_started_id is not None:
                self._job_switch_pairs[job_id].append(self._last_started_id) # here, we take what we switched to, and append where we switched from
            self._last_started_id = job_id
        # once we process the event, we know we're looking at data for this event's user next time.
        self._current_user_code = user_code

    def _extractFromFeatureData(self, feature: FeatureData):
        return
