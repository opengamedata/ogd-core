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
    
    def __init__(self, params: ExtractorParameters, region_map: dict):
        super().__init__(params=params, region_map=region_map)
        self._session_id = None
        self._current_region = None
        self._region_start_time = None
        self._time_in_region = {}  # Dictionary to store total time spent in each region


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            self._current_region = None  # Reset current region for a new session
            self._region_start_time = None

        # Check if the event provides information about the player's region
        region_data = event.EventData.get("region_name")
        if region_data is not None and region_data in self._region_map:
            if self._current_region != region_data:
                # Transition to a new region, update the current region and start time
                self._current_region = region_data
                self._region_start_time = event.Timestamp
            else:
                # Player is still in the same region, update the time spent
                if self._region_start_time is not None:
                    self._time_in_region[self._current_region] = self._time_in_region.get(self._current_region, 0) + (
                            event.Timestamp - self._region_start_time).total_seconds()

    
    def _extractFromFeatureData(self, feature:FeatureData):
        return
        
    def _getFeatureValues(self) -> List[Any]:
        # Return a list of total time spent in each region
        return [timedelta(seconds=self._time_in_region.get(region, 0)) for region in self._region_map.values()]

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