# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional
# import local files
from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from utils import Logger

class Timespan(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters, schema_args:dict):
        self._start_event = schema_args['start_event']
        self._end_event = schema_args['end_event']
        super().__init__(params=params)
        self._start_time : Optional[datetime] = None
        self._end_time   : Optional[datetime] = None
        self._span = timedelta()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [self._start_event, self._end_event]

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
        if event.EventName == self._start_event:
            if self._start_time is None:
                self._start_time = event.Timestamp
            else:
                Logger.Log(f"{self.Name} received a second {self._start_event} (start-of-span) event! This occurred {event.Timestamp - self._start_time} after the initial {self._start_event} event.", logging.WARN)
        if event.EventName == self._end_event:
            if self._start_time is not None:
                if self._end_time is not None:
                    Logger.Log(f"{self.Name} received a second {self._end_event} (end-of-span) event! This occurred {event.Timestamp - self._end_time} after the initial {self._end_event} event. Using the later event's timestamp for span.", logging.WARN)
                self._end_time = event.Timestamp
            else:
                Logger.Log(f"{self.Name} received a {self._end_event} event (end-of-span event) when no {self._start_event} event (start-of-span event) had occurred!", logging.WARN)
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : List[float]
        if self._start_time is not None and self._end_time is not None:
            ret_val = [(self._end_time - self._start_time).total_seconds()]
        else:
            ret_val = [0]
        return ret_val

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return None

    @staticmethod
    def MaxVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return None
