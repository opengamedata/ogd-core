# import libraries
import json
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.PerCountFeature import PerCountFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from datetime import datetime, timedelta

QUIZ_INDEXES = {
    0: {0: 0, 1: 1},
    2: {0: 2, 1: 3, 2: 4, 3: 5},
    3: {0: 6, 1: 7, 2: 8, 3: 9},
    4: {0: 10, 1: 11, 2: 12, 3: 13},
    5: {0: 14, 1: 15, 2: 16, 3: 17}
}

class SurveyItem(PerCountFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    
    
    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)
        # NOTE: The time we record it the first time that players answered the given question minus the last time answering the last question or the time starting the quiz
        self._last_timestamp : datetime = None
        self._time : Optional[timedelta] = None
        self._response_index : Optional[int] = None
        self._index : Optional[int] = None
        self._text : str = ""
        self._num_answers : int = 0
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        # BUG: It's so weird that question NO.0, 4, 8... use quizstart time but others use last question's time. see JowilderExtractor.py line 492
        # TODO: In the old code, when the quiz starts, self._last_timestamp is assigned a value, and when the quiz ends, the member is assigned to None. But logically, I don't think the latter one is needed, since after a quiz ends and before another starts, we shouldn't have any other quizquestion events or access this feature extractor. So I ignored this part.
        if event.EventName == "CUSTOM.23":
            return self.CountIndex%4 == 0
        quiz_index = event.event_data["quiz_number"]
        question_index = event.event_data["question_index"]
        self._index = QUIZ_INDEXES[quiz_index][question_index]
        return self._index == self.CountIndex or self._index == self.CountIndex - 1

    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["CUSTOM.22", "CUSTOM.23"] 
        # ["CUSTOM.22", "CUSTOM.23"] = ["quizquestion", "quizstart"]

    def _getFeatureDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if event.EventName == "CUSTOM.23" or self._index == self.CountIndex - 1:
            self._last_timestamp = event.Timestamp
            return
        if self._time in [0, None]:
            self._time = event.Timestamp - self._last_timestamp
        self._response_index = event.EventData["response_index"]
        self._text = event.EventData["response"]
        self._num_answers += 1
            
        
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._response_index, self._text, self._time, self._num_answers]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Text", "Time", "AnswerTimeCounts"]
