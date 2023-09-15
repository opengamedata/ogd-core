# import libraries
import json
from typing import Any, List, Optional
from datetime import timedelta
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger
# import libraries
import logging
from games.PENGUINS.features.PerRegionFeature import PerRegionFeature
    
class RegionDuration(PerRegionFeature):
    
    def __init__(self, params:ExtractorParameters, region_map:dict):
        super().__init__(params=params, region_map = region_map)
        self._session_id = None
        # self._region_start_time = None
        self._prev_timestamp = None
        self._time = 0
        self._name = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID

            if self._region_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._region_start_time).total_seconds()
                self._region_start_time = event.Timestamp
        
        if event.EventData.get("region_name") == self.CountIndex:
            self._region_start_time = event.Timestamp 
        self._prev_timestamp = event.Timestamp
        
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event, region_map:dict):
        ret_val : bool = False
        region_data = event.EventData.get("region_name")
        # Logger.Log("______________________________")
        
        if region_data is not None:
            if region_map[region_data] == self.CountIndex:

                ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val
