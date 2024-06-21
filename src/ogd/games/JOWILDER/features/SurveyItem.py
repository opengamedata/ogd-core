# import libraries
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Final, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event
from ogd.core.utils.Logger import Logger

# BUG: Question0 and quiz 0 don't have start time
# NOTE: Assumptions are: Every quiz should have a quizstart.

QUIZ_INDEXES : Final[Dict[int, Dict[int, int]]] = {
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
    
    
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        # NOTE: The time we record it the first time that players answered the given question minus the last time answering the last question or the time starting the quiz
        self._last_timestamp : Optional[datetime] = None
        self._quiz_start_timestamp : Optional[datetime] = None
        self._time : Optional[timedelta] = None
        self._response_index : Optional[int] = None
        self._index : Optional[int] = None
        self._text : str = ""
        self._num_answers : int = 0
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        # BUG: It's so weird that question NO.0, 4, 8... use quizstart time but others use last question's time. see JowilderExtractor.py line 492
        # TODO: In the old code, when the quiz starts, self._last_timestamp is assigned a value, and when the quiz ends, the member is assigned to None. But logically, I don't think the latter one is needed, since after a quiz ends and before another starts, we shouldn't have any other quizquestion events or access this feature extractor. So I ignored this part.
        quiz_index = event.event_data["quiz_number"]
        if event.EventName == "CUSTOM.23":
            return self.CountIndex in QUIZ_INDEXES[quiz_index].values()
        question_index = event.event_data["question_index"]
        self._index = QUIZ_INDEXES[quiz_index][question_index]
        return self._index == self.CountIndex or self._index == self.CountIndex - 1

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["CUSTOM.22", "CUSTOM.23"] 
        # ["CUSTOM.22", "CUSTOM.23"] = ["quizquestion", "quizstart"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        # TODO: Add explict code and comments to skip quiz 0 also for survey_time
        if self.CountIndex == 0:
            return 
        if event.EventName == "CUSTOM.23":
            self._quiz_start_timestamp = event.Timestamp
            return
        if self._index == self.CountIndex - 1: 
            self._last_timestamp = event.Timestamp
            return
        
        if self._time in [0, None]:
            _question_index = event.EventData.get("question_index")
            if _question_index == 0:
                if self._quiz_start_timestamp is not None:
                    self._time = event.Timestamp - self._quiz_start_timestamp
                else:
                    raise ValueError(f"SurveyItem got a question answer when there was no quiz start time.")
            else:
                if self._last_timestamp is not None:
                    self._time = event.Timestamp - self._last_timestamp
                else:
                    self._time = None
                    Logger.Log("SurveyItem got a question answer when there was no last timestamp.", logging.DEBUG)
                    # raise ValueError(f"SurveyItem got a question answer when there was no last timestamp.")
        self._response_index = event.EventData["response_index"]
        self._text = event.EventData["response"]
        self._num_answers += 1
            
        
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        # By now, ResponseChanges will return -1 if there is no answer for this question.
        return [self._response_index, self._text, self._time, self._num_answers - 1]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Text", "Time", "ResponseChanges"]
