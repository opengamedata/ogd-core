# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class PercentOffsetGoodMoves(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        Feature.__init__(self, params=params)
        self._offset_count = 0
        self._good_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventData['slider'].upper() == 'OFFSET':
            self._offset_count += 1
            if event.EventName == "CUSTOM.1":
                if event.EventData['end_closeness'] > event.EventData['begin_closeness']:
                    self._good_count += 1
            elif event.EventName == "CUSTOM.2":
                start_dist = event.EventData['correct_val'] - event.EventData['begin_val']
                end_dist = event.EventData['correct_val'] - event.EventData['end_val']
                if abs(end_dist) < abs(start_dist):
                    self._good_count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._good_count / self._offset_count if self._offset_count != 0 else None]

    # *** Optionally override public functions. ***
