# import libraries
import json
from typing import Any, Dict, List
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
    
    def __init__(self, params:ExtractorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params,region_map = region_map)
        self._region_start_time = None
        self._time = timedelta(0)
        self._target_region = self._region_map[self.CountIndex].get("name")

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["region_enter","region_exit"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "region_enter":
            self._region_start_time = event.Timestamp
        elif event.EventName == "region_exit":
            if self._region_start_time is not None:
                self._time += (event.Timestamp - self._region_start_time)
                self._region_start_time = None

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time.total_seconds()]

    def _validateEventCountIndex(self, event:Event):
        _event_region = event.EventData.get("region", "NO REGION FOUND")
        if _event_region == self._target_region:
            return True
        else:
            return False

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Extractor

        Base function to give a list of which ExtractionModes an extractor will handle.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.SESSION]
