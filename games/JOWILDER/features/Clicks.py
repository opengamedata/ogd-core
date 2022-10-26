# import libraries
import logging
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from utils import Logger

class Clicks(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._click_count : int = 0
        self._avg_time : float = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [f"CUSTOM.{i}" for i in range(3, 12)]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"] 

    def _extractFromEvent(self, event:Event) -> None:
        self._click_count += 1
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        try: 
            self._avg_time = feature.FeatureValues[0].total_seconds()/self._click_count
        except ZeroDivisionError:
            Logger.Log(f"Clicks extractor tried to divide by 0 clicks, in mode {self.ExtractionMode}", logging.WARN)
        self._avg_time = round(self._avg_time, 3)
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._click_count, self._avg_time]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["AverageTimeBetween"] 