# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from datetime import datetime, timedelta
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.SessionFeature import SessionFeature

class EggRecoverTime(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._stolen_timestamp : Optional[datetime] = None
        self._time = 0
        self._skua_id = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["egg_lost", "egg_recovered"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "egg_lost":
            self._skua_id = event.event_data.get("object_id")
            self._stolen_timestamp = event.Timestamp
            # Logger.Log(f"lost time is {self._argument_start_time}")
        elif event.EventName == "egg_recovered":
            if self._stolen_timestamp is not None:
                self._time += (event.Timestamp - self._stolen_timestamp).total_seconds()
                self._stolen_timestamp = None
            else: 
                Logger.Log("Got an 'egg_recovered' with no preceding 'egg_lost' event!", logging.WARN)
    
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    