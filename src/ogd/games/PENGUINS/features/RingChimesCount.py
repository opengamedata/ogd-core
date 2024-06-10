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

chime_dict = {'chime 1':0, 'chime 2':0, 'chime 3':0, 'chime 4':0, 'chime 5':0, 'chime 6':0, 'unknown chime':0}
class RingChimesCount(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._current_count : int = 0
        self._object_id = None
        self._chime_dict = chime_dict.copy()
        self._obj_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["ring_chime"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # self._current_count += 1
        self._object_id = event.event_data.get("note_played", "unknown chime")
        self._chime_dict[self._object_id] += 1
        
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._chime_dict]

    