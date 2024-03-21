import logging
import json
from datetime import datetime
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.features.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SnippetsSubmitted(PerLevelFeature):
    has_printed = False
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._snippet_ids : List[str] = []


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["story_click"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "story_click":
            snippet_list = json.loads( event.EventData["snippet_list"] )
            for snippet in snippet_list:
                if not SnippetsSubmitted.has_printed:
                    print(f"snippet: {snippet} of type {type(snippet)}")
                    SnippetsSubmitted.has_printed = True
                self._snippet_ids.append(snippet.get("SnippetId", "NOT FOUND"))

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._snippet_ids]

    # *** Optionally override public functions. ***
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION, ExtractionMode.PLAYER]

