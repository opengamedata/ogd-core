import json
from collections import defaultdict
from typing import Any, List, Union

import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TopJobSwitchDestinations(Feature):

    def __init__(self, name:str, description:str, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_started_id = None
        self._job_switch_pairs = defaultdict(dict)

    def GetEventDependencies(self) -> List[str]:
        return ["switch_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        ret_val = {}

        for src in self._job_switch_pairs.keys():
            dests = sorted(
                self._job_switch_pairs[src].items(),
                key=lambda item: len(item[1]), # sort by length of list of ids.
                reverse=True # sort largest to smallest
            )
            ret_val[src] = {
                item[0]:item[1] for item in dests[0:5]
            }
            utils.Logger.Log(f"For TopJobSwitchDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        job_name = event.event_data["job_name"]["string_value"]
        prev_job_name = event.event_data["prev_job_name"]["string_value"]
        
        if user_code == self._current_user_code and job_name != prev_job_name and prev_job_name != "no-active-job":
            if not job_name in self._job_switch_pairs[prev_job_name]:
                self._job_switch_pairs[prev_job_name][job_name] = []

            self._job_switch_pairs[prev_job_name][job_name].append(user_code)

        self._current_user_code = user_code

    def _extractFromFeatureData(self, feature: FeatureData):
        return
