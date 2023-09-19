# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from games.PENGUINS.features.PerRegionFeature import PerRegionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature

gaze_dict = {'BigRock00': 0, 'Bridge': 0, 'Bridge2': 0, 'BigRock01': 0, 'River3': 0, 'Inland2':0, 'Sea4': 0, 'River2': 0, 'Inland1': 0, 'Sea5': 0, 'Sea3': 0, 'River5': 0, 'River4': 0, 'Inland5': 0, 'Inland4': 0, 'Inland3': 0, 'River1': 0, 'Sea2': 0, 'Sea1': 0 }
class GazeCount(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._current_count : int = 0
        self._object_id = None
        self._gaze_dict = gaze_dict.copy()
        self._obj_list = list()
        
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["gaze_object_end"]
    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []
    def _extractFromEvent(self, event:Event) -> None:
        # self._current_count += 1
        self._object_id = event.event_data.get("object_id")
        self._gaze_dict[self._object_id]+=1
        
    def _extractFromFeatureData(self, feature:FeatureData):
        return
    def _getFeatureValues(self) -> List[Any]:
        return [self._gaze_dict]

    