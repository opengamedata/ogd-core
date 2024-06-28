# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.SessionFeature import SessionFeature

# gaze_dict = { 'BigRock00': 0, 'Bridge': 0, 'Bridge2': 0, 'BigRock01': 0, 'River3': 0, 'Inland2': 0, 'Sea4': 0, 'River2': 0,'Inland1': 0, 'Sea5': 0, 'Sea3': 0, 'River5': 0, 'River4': 0, 'Inland5': 0, 'Inland4': 0, 'Inland3': 0,'River1': 0, 'Sea2': 0, 'Sea1': 0}
class GazeCount(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        # self._current_count : int = 0
        self._object_id = None
        self._gaze_dict = dict()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["gaze_object_end"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # self._current_count += 1
        
        self._object_id = event.event_data.get("object_id")
        if not self._object_id in self._gaze_dict.keys():
                self._gaze_dict[self._object_id] = 0
        
        self._gaze_dict[self._object_id]+=1
        
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._gaze_dict]
