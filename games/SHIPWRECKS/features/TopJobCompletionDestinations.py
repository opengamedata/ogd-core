# import libraries
import json
from collections import defaultdict
from typing import Any, List
# import locals
from utils import Logger
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TopJobCompletionDestinations(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._current_session_id = None
        self._current_mission_id = None
        self._last_completed_id = None
        self._mission_complete_pairs = defaultdict(dict)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["checkpoint"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        session_id = event.session_id
        checkpoint = event.event_data["status"]["string_value"]
        mission_id = event.event_data["mission_id"]["string_value"]

        if checkpoint == "Case Closed" and session_id == self._current_session_id and mission_id != self._last_completed_id:
            if not self._last_completed_id:
                self._last_completed_id = mission_id
            else:
                if mission_id not in self._mission_complete_pairs[self._last_completed_id].keys():
                    self._mission_complete_pairs[self._last_completed_id][mission_id] = []

                self._mission_complete_pairs[self._last_completed_id][mission_id].append(session_id)
                self._last_completed_id = mission_id

        self._current_session_id = session_id

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val = {}

        for src in self._mission_complete_pairs.keys():
            dests = sorted(
                self._mission_complete_pairs[src].items(),
                key=lambda item: len(item[1]), # sort by length of list of ids.
                reverse=True # sort largest to smallest
            )
            ret_val[src] = {
                item[0]:item[1] for item in dests[0:5]
            }
            Logger.Log(f"For TopJobCompletionDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
