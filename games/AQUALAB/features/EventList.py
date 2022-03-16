# Global imports
from collections import Counter, defaultdict
from typing import Any, List, Union
# Local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class EventList(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._event_list = []

    def GetEventDependencies(self) -> List[str]:
        return ["scene_changed", "accept_job", "switch_job", "complete_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        # Count the top five accepted job ids for each completed job id
        return [self._event_list]

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        if "user_id" not in event.event_data.keys():
            return
        next_event = {
            "name":event.event_name,
            "user_id":event.event_data["user_code"]["string_value"],
            "session_id":event.session_id,
            "timestamp":event.timestamp,
            "job_id":event.event_data["job_id"]["int_value"]
        }
        if event.event_name == "scene_changed":
            next_event['scene_name'] = event.event_data['scene_name']['string_value']
        self._event_list.append(next_event)

    def _extractFromFeatureData(self, feature: FeatureData):
        return
