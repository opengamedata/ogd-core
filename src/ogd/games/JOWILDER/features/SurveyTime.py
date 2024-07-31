# import libraries
from datetime import datetime, timedelta
import json
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

# BUG: quizstart and quizend don't match. Using "wellsdidit" save code to inspect it.

class SurveyTime(PerCountFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params=GeneratorParameters):
        super().__init__(params=params)
        self._start_time : Optional[datetime] = None
        self._duration : Optional[timedelta] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        # NOTE: [0,2,3,4,5] to [0,1,2,3,4]
        quiz_index = event.EventData.get("quiz_number")
        if quiz_index is not None:
            if quiz_index >= 2:
                return quiz_index - 1 == self.CountIndex
            else:
                return quiz_index == self.CountIndex
        else:
            raise KeyError(f"SurveyTime got an event of type {event.EventName} with no quiz_number! EventData keys are: {event.EventData.keys()}")

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.23", "CUSTOM.24"] 
        # ["CUSTOM.23", "CUSTOM.24"] = [quizstart, quizend]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        if self.CountIndex == 0:
            return
        # TODO: Fix the bugs that quizstart and quizend doesn't match
        raise(NotImplementedError("Haven't implemented the function due to bugs"))
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._duration]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return super().MinVersion()

    @staticmethod
    def MaxVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return super().MaxVersion()
