# import libraries
import json
from typing import Any, Dict, List
from datetime import timedelta
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.utils.Logger import Logger
# import libraries
import logging
from ogd.games.PENGUINS.features.bases.PerRegionFeature import PerRegionFeature
    
class RegionDuration(PerRegionFeature):
    
    def __init__(self, params:GeneratorParameters, region_map:List[Dict[str, Any]]):
        super().__init__(params=params,region_map = region_map)
        self._region_start_time = None
        self._time = timedelta(0)
        self._target_region = self._region_map[self.CountIndex].get("name")

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["region_enter","region_exit"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "region_enter":
            self._region_start_time = event.Timestamp
        elif event.EventName == "region_exit":
            if self._region_start_time is not None:
                self._time += (event.Timestamp - self._region_start_time)
                self._region_start_time = None

    def _updateFromFeatureData(self, feature:FeatureData):
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
