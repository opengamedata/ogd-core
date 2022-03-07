from typing import Any, List

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionDiveSitesCount(Feature):
    
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._count = 0
        self._visited_sites = []

    def GetEventDependencies(self) -> List[str]:
        return ["begin_dive"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._count]

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data["site_id"]['string_value'] not in self._visited_sites:
            self._count += 1
            self._visited_sites.append(event.event_data["site_id"]['string_value'])

    def _extractFromFeatureData(self, feature: FeatureData):
        return
