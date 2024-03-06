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


class ActivityCompleted(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._activ_lst = []
        self._object_id = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [ "activity_end"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        self._object_id = event.event_data.get("activity_name")
        self._activ_lst.append(self._object_id)
        #if self._object_id not in self._activ_dict.keys():
            #self._activ_dict[self._object_id]=0
        #else:
            #self._activ_dict[self._object_id]+=1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._activ_lst]


