# import libraries
import inspect
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.extractors.features.PerCountFeature import PerCountFeature
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature

class RegionJobCount(PerCountFeature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        regions = ['arctic', 'coral', 'bayou', 'kelp', 'other']
        self.count = 0
        self.region = regions[self.CountIndex]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_job"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event:Event):
        if event.app_version == 'Aqualab' or event.app_version == 'None':
            if event.EventData.get('job_name', {}).get('string_value').startswith(self.region):
                return True
            else:
                return False
        else:
            if event.EventData.get('job_name', {}).startswith(self.region):
                return True
            else:
                return False
# 'aqualab' and 'GameState"
    def _extractFromEvent(self, event:Event) -> None:
        self.count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
