# import libraries
import json
from collections import defaultdict
from typing import Any, List
# import locals
from utils import Logger
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class TopJobSwitchDestinations(Feature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._current_session_id = None
        self._last_started_id = None
        self._mission_switch_pairs = defaultdict(dict)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["checkpoint"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        session_id = event.SessionID
        checkpoint = event.EventData["status"]["string_value"]
        mission_name = event.EventData["mission_id"]["string_value"]

        if checkpoint == "Begin Mission":
            if not self._last_started_id:
                self._last_started_id = mission_name
            elif session_id == self._current_session_id:
                # Started a new mission before completing the previous one
                if not mission_name in self._mission_switch_pairs[self._last_started_id].keys():
                    self._mission_switch_pairs[self._last_started_id][mission_name] = []

                self._mission_switch_pairs[self._last_started_id][mission_name].append(session_id) # here, we take what we switched to, and append where we switched from
        elif checkpoint == "Case Closed" and self._last_started_id:
            self._last_started_id = None

        # once we process the event, we know we're looking at data for this event's user next time.
        self._current_session_id = session_id

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val = {}

        for src in self._mission_switch_pairs.keys():
            dests = sorted(
                self._mission_switch_pairs[src].items(),
                key=lambda item: len(item[1]), # sort by length of list of ids.
                reverse=True # sort largest to smallest
            )
            ret_val[src] = {
                item[0]:item[1] for item in dests[0:5]
            }
            Logger.Log(f"For TopJobSwitchDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
