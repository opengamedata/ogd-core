# import libraries
import logging
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event
from ogd.core.utils.Logger import Logger

class Clicks(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._click_count : int = 0
        self._avg_time : float = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return [f"CUSTOM.{i}" for i in range(3, 12)]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"] 

    def _updateFromEvent(self, event:Event) -> None:
        self._click_count += 1
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        if self._click_count > 0:
            self._avg_time = feature.FeatureValues[0].total_seconds()/self._click_count
        else:
            Logger.Log(f"Clicks extractor received 0 click events, in mode {self.ExtractionMode.name}", logging.DEBUG)
            self._avg_time = 0
        self._avg_time = round(self._avg_time, 3)
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._click_count, self._avg_time]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["AverageTimeBetween"] 
