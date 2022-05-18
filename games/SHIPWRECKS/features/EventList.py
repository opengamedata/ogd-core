# import libraries
import json
from typing import Any, List
# import locals
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class EventList(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._event_list = []
        self._mission_id = None

        # Map of event names to primary detail parameter and its type
        self._details_map = {
            "scene_load":               ("scene", "string_value"),
            "checkpoint":               ("status", "string_value"),
            "new_evidence":             ("evidence_id", "string_value"),
            "sonar_percentage_update":  ("percentage", "int_value"),
            "dive_moveto_location":     ("next_node_id", "string_value"),
            "dive_photo_click":         ("accurate", "string_value"),
            "view_dialog":              ("dialog_id", "string_value")
        }

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
            "index": event.event_sequence_index,
            "event_primary_detail": None
        }

        if event.event_name in self._details_map:
            param_name = self._details_map[event.event_name][0]
            param_type = self._details_map[event.event_name][1]

            next_event["event_primary_detail"] = event.event_data[param_name][param_type]

        self._event_list.append(next_event)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [json.dumps(self._event_list)]
