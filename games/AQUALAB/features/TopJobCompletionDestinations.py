# Global imports
from collections import Counter, defaultdict
from typing import Any, List, Union
# Local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event
import utils

class TopJobCompletionDestinations(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_completed_id = None
        self._job_complete_pairs = defaultdict(dict)

    def GetEventDependencies(self) -> List[str]:
        return ["accept_job", "complete_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        ret_val = {}
        for src in self._job_complete_pairs.keys():
            dests = sorted(
                self._job_complete_pairs[src].items(),
                key=lambda item: len(item[1]), # sort by length of list of ids.
                reverse=True # sort largest to smallest
            )
            ret_val[src] = {
                item[0]:item[1] for item in dests[0:5]
            }
            utils.Logger.Log(f"For TopJobDestinations, sorted dests as: {dests}")
        return [ret_val]

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.event_data["user_code"]["string_value"]
        job_id = event.event_data["job_id"]["int_value"]

        # in either case, handle event.
        if event.event_name == "complete_job":
            self._last_completed_id = event.event_data["job_id"]["int_value"] # here, we take what we last completed, and append where we switched to.
        elif event.event_name == "accept_job":
            if user_code == self._current_user_code and self._last_completed_id is not None:
                if not job_id in self._job_complete_pairs[self._last_completed_id].keys():
                    self._job_complete_pairs[self._last_completed_id][job_id] = []
                self._job_complete_pairs[self._last_completed_id][job_id].append(user_code)
                self._last_completed_id = None
        # finally, once we process the event, we know we're looking at data for this event's user.
        self._current_user_code = user_code

    def _extractFromFeatureData(self, feature: FeatureData):
        return
