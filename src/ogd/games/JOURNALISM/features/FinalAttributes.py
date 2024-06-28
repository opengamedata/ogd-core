# import libraries
import json
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class FinalAttributes(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerCountFeature.__init__(self, params=params)
        self._ATTRIBUTE_ENUM : List[str] = ["endurance", "resourceful", "tech","social","trust","research"]
        self._last_attribs : Dict[str, Optional[int]] = dict(zip(self._ATTRIBUTE_ENUM, [None]*len(self._ATTRIBUTE_ENUM)))


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        #self._story_alignment = event.EventData["story_alignment"]
        _default = str([None]*len(self._ATTRIBUTE_ENUM))
        _stats = json.loads(event.GameState.get("current_stats", _default))
        self._last_attribs = dict(zip(self._ATTRIBUTE_ENUM, _stats))

    def _extractFromFeatureData(self, feature:FeatureData):
        #add logic to make sure that MODE is session, not player so we don't get duplicates
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._last_attribs]

    # *** Optionally override public functions. ***
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
