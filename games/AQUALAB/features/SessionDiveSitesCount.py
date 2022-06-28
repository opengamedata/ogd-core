# import libraries
from typing import Any, List
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class SessionDiveSitesCount(Feature):
    
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._count = 0
        self._visited_sites = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_dive"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData["site_id"]['string_value'] not in self._visited_sites:
            self._count += 1
            self._visited_sites.append(event.EventData["site_id"]['string_value'])

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
