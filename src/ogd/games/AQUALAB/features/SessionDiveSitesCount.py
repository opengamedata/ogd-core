# import libraries
from typing import Any, List
# import locals
from ogd.core.generators.Generator import ExtractorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SessionDiveSitesCount(Feature):
    
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._count = 0
        self._visited_sites = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_dive"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData["site_id"] not in self._visited_sites:
            self._count += 1
            self._visited_sites.append(event.EventData["site_id"])

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
