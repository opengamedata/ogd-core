import logging
import json
from datetime import datetime
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class SnippetsSubmitted(PerLevelFeature):
    has_printed = False
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._snippet_ids : List[str] = []


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["story_click"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "story_click":
            snippet_list = json.loads( event.EventData["snippet_list"] )
            for snippet in snippet_list:
                # if not SnippetsSubmitted.has_printed:
                #     print(f"snippet: {snippet} of type {type(snippet)}")
                #     SnippetsSubmitted.has_printed = True
                self._snippet_ids.append(snippet.get("SnippetId", "NOT FOUND"))

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._snippet_ids]

    # *** Optionally override public functions. ***
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION, ExtractionMode.PLAYER]

