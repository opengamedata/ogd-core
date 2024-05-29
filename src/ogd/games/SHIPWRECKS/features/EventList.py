# import libraries
import json
from typing import Any, List
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class EventList(Feature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
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
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "checkpoint" and event.EventData["status"] == "Begin Mission":
            self._mission_id = event.EventData["mission_id"]

        next_event = {
            "name": event.EventName,
            "user_id": event.UserID,
            "session_id": event.SessionID,
            "timestamp": event.Timestamp.isoformat(),
            "job_name": self._mission_id,
            "index": event.EventSequenceIndex,
            "event_primary_detail": None
        }

        if event.EventName in self._details_map:
            param_name = self._details_map[event.EventName][0]

            next_event["event_primary_detail"] = event.EventData[param_name]

        self._event_list.append(next_event)

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [json.dumps(self._event_list)]
