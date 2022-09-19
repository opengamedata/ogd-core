# import libraries
import json
import logging
from collections import defaultdict
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.features.Feature import Feature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class TopJobSwitchDestinations(Feature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params)
        self._current_user_code = None
        self._last_started_id = None
        self._job_switch_pairs = defaultdict(dict)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["accept_job", "switch_job"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.EventData['job_name']):
            user_code = event.UserID
            job_name = event.EventData["job_name"]["string_value"]

            if event.EventName == "accept_job":
                self._last_started_id = job_name
            elif event.EventName == "switch_job":
                if user_code == self._current_user_code and self._last_started_id is not None and self._last_started_id != job_name and job_name != "no-active-job":
                    if not job_name in self._job_switch_pairs[self._last_started_id].keys():
                        self._job_switch_pairs[self._last_started_id][job_name] = []

                    self._job_switch_pairs[self._last_started_id][job_name].append(user_code) # here, we take what we switched to, and append where we switched from

                self._last_started_id = job_name

            # once we process the event, we know we're looking at data for this event's user next time.
            self._current_user_code = user_code

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
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
            # Logger.Log(f"For TopJobSwitchDestinations, sorted dests as: {json.dumps(dests)}")

        return [json.dumps(ret_val)]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] and job_data['string_value'] in self._job_map:
            ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobsAttempted", logging.WARNING)
        return ret_val
