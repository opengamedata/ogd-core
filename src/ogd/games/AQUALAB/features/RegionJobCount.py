# import libraries
import inspect
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.Extractor import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature

class RegionJobCount(PerCountFeature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        regions = ['arctic', 'coral', 'bayou', 'kelp', 'other']
        self.count = 0
        self.region = regions[self.CountIndex]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
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
    def _updateFromEvent(self, event:Event) -> None:
        self.count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
