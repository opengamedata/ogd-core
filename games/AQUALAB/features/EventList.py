# import libraries
import json
from typing import Any, List, Union
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class EventList(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._event_list = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["scene_changed", "accept_job", "switch_job", "complete_job", "ask_for_help", "begin_dive", "begin_model", "end_model", "begin_argument"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.user_id:
            next_event = {
                "name":event.event_name,
                "user_id":event.user_id,
                "session_id":event.session_id,
                "timestamp":event.timestamp.isoformat(),
                "job_name":event.event_data["job_name"]["string_value"]
            }
            if event.event_name == "scene_changed":
                next_event['scene_name'] = event.event_data['scene_name']['string_value']
            self._event_list.append(next_event)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [json.dumps(self._event_list)]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Union[str,None]:
        return "1"
