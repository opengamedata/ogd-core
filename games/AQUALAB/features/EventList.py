# import libraries
import json
from typing import Any, List, Optional

from docutils import DataError
# import locals
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class EventList(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._event_list = []

        # Map of event names to primary detail parameter and its type
        self._details_map = {
            "accept_job":                   ("job_name", "string_value"),
            "switch_job":                   ("job_name", "string_value"),
            "receive_fact":                 ("fact_id", "string_value"),
            "receive_entity":               ("entity_id", "string_value"),
            "complete_job":                 ("job_name", "string_value"),
            "complete_task":                ("task_id", "string_value"),
            "scene_changed":                ("scene_name", "string_value"),
            "room_changed":                 ("room_name", "string_value"),
            "begin_dive":                   ("site_id", "string_value"),
            "ask_for_help":                 ("node_id", "string_value"),
            "script_fired":                 ("node_id", "string_value"),
            "bestiary_select_species":      ("species_id", "string_value"),
            "bestiary_select_environment":  ("environment_id", "string_value"),
            "bestiary_select_model":        ("model_id", "string_value"),
            "begin_model":                  ("job_name", "string_value"),
            "model_phase_changed":          ("phase", "string_value"),
            "model_ecosystem_selected":     ("ecosystem", "string_value"),
            "model_concept_started":        ("ecosystem", "string_value"),
            "model_concept_updated":        ("status", "string_value"),
            "model_concept_exported":       ("ecosystem", "string_value"),
            "begin_simulation":             ("job_name", "string_value"),
            "model_sync_error":             ("sync", "int_value"),
            "simulation_sync_achieved":     ("job_name", "string_value"),
            "model_predict_completed":      ("ecosystem", "string_value"),
            "model_intervene_update":       ("difference_value", "int_value"),
            "model_intervene_error":        ("ecosystem", "string_value"),
            "model_intervene_completed":    ("ecosystem", "string_value"),
            "end_model":                    ("phase", "string_value"),
            "purchase_upgrade":             ("item_name", "string_value"),
            "insufficient_funds":           ("item_name", "string_value"),
            "add_environment":              ("environment", "string_value"),
            "remove_environment":           ("environment", "string_value"),
            "add_critter":                  ("critter", "string_value"),
            "remove_critter":               ("critter", "string_value"),
            "begin_experiment":             ("tank_type", "string_value"),
            "end_experiment":               ("tank_type", "string_value"),
            "begin_argument":               ("job_name", "string_value"),
            "fact_submitted":               ("fact_id", "string_value"),
            "fact_rejected":                ("fact_id", "string_value"),
            "leave_argument":               ("job_name", "string_value"),
            "complete_argument":            ("job_name", "string_value")
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["all_events"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.user_id:
            next_event = {
                "name": event.event_name,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "timestamp": event.timestamp.isoformat(),
                "job_name": event.event_data["job_name"]["string_value"],
                "index": event.event_sequence_index,
                "event_primary_detail": None
            }

            if event.event_name == "scene_changed":
                next_event['scene_name'] = event.event_data['scene_name']['string_value']

            if event.event_name in self._details_map:
                param_name = self._details_map[event.event_name][0]
                param_type = self._details_map[event.event_name][1]

                try:
                    next_event["event_primary_detail"] = event.event_data[param_name][param_type]
                except KeyError as err:
                    raise KeyError(f"Event of type {event.event_name} did not have parameter {param_name}, valid parameters are {event.event_data.keys()}")

            self._event_list.append(next_event)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [json.dumps(self._event_list)]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"
