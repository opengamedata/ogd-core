# global imports
import json
from collections import defaultdict
from typing import Any, List
# local imports
import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TopJobCompletionDestinations(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._current_session_id = None
        self._last_completed_id = None
        self._mission_complete_pairs = defaultdict(dict)

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["checkpoint"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        session_id = event.session_id
        checkpoint = event.event_data["status"]["string_value"]
        mission_name = event.event_data["mission_id"]["string_value"]

        # in either case, handle event.
        if checkpoint == "Case Closed":
            self._last_completed_id = mission_name # here, we take what we last completed, and append where we switched to.
        elif checkpoint == "Begin Mission":
            if session_id == self._current_session_id and self._last_completed_id is not None:
                if not mission_name in self._mission_complete_pairs[self._last_completed_id].keys():
                    self._mission_complete_pairs[self._last_completed_id][mission_name] = []

                self._mission_complete_pairs[self._last_completed_id][mission_name].append(session_id)
                self._last_completed_id = None

        # finally, once we process the event, we know we're looking at data for this event's user.
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
            utils.Logger.Log(f"For TopJobCompletionDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
