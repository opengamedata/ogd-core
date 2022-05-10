# import libraries
import json
from typing import Any, List, Union
# import locals
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class EventList(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        print("SETUP")
        self._event_list = []
        self._mission_id = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["all_events"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "checkpoint" and event.event_data["status"]["string_value"] == "Begin Mission":
            self._mission_id = event.event_data["mission_id"]["string_value"]

        next_event = {
            "name": event.event_name,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "timestamp": event.timestamp.isoformat(),
            "job_name": self._mission_id,
            "index": event.event_sequence_index
        }
        self._event_list.append(next_event)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [json.dumps(self._event_list)]
