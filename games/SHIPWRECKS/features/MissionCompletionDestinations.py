import json
from collections import defaultdict
from typing import Any, List, Union

import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class MissionCompletionDestinations(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._current_user_code = None
        self._last_completed_id = None
        self._complete_pairs = defaultdict(dict)

    def GetEventDependencies(self) -> List[str]:
        return ["mission_start", "mission_complete"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        ret_val = {}

        for src in self._complete_pairs.keys():
            dests = sorted(
                self._complete_pairs[src].items(),
                key=lambda item: len(item[1]), # sort by length of list of ids.
                reverse=True # sort largest to smallest
            )
            ret_val[src] = {
                item[0]:item[1] for item in dests[0:5]
            }

            utils.Logger.Log(f"For MissionCompletionDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        mission_id = event.event_data["mission_id"]["int_value"]

        # in either case, handle event.
        if event.event_name == "mission_complete":
            self._last_completed_id = mission_id # here, we take what we last completed, and append where we switched to.
        elif event.event_name == "accept_job":
            if user_code == self._current_user_code and self._last_completed_id is not None:
                if not mission_id in self._complete_pairs[self._last_completed_id].keys():
                    self._complete_pairs[self._last_completed_id][mission_id] = 0

                self._complete_pairs[self._last_completed_id][mission_id] += 1
                self._last_completed_id = None

        # finally, once we process the event, we know we're looking at data for this event's user.
        self._current_user_code = user_code

    def _extractFromFeatureData(self, feature: FeatureData):
        return
