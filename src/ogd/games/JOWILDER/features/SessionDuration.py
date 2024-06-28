# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

# BUG: There may be multiple endgame events with only one startgame event

class SessionDuration(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._start_time : Optional[datetime] = None
        self._duration : timedelta = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "CUSTOM.1" and not self._start_time:
            self._start_time = event.Timestamp
            return
        elif event.EventName == "CUSTOM.2" and self._start_time:
            self._duration = event.Timestamp - self._start_time
            return


    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._duration]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] 
