# import libraries
import json
from collections import defaultdict
from typing import Any, List
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class TopJobSwitchDestinations(Feature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._current_session_id = None
        self._last_started_id = None
        self._mission_switch_pairs = defaultdict(dict)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["checkpoint"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        session_id = event.SessionID
        checkpoint = event.EventData["status"]
        mission_name = event.EventData["mission_id"]

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

    def _updateFromFeatureData(self, feature:FeatureData):
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
