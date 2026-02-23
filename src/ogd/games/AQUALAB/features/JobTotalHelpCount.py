# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class JobTotalHelpCount(PerJobFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._by_task       : Dict[str, int] = {}
        self._current_count : int = 0
        self._total_count   : int = 0
        self._player_count  : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["JobHelpCount"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.ExportMode == ExtractionMode.PLAYER and feature.CountIndex == self.CountIndex:
            player_ct    = feature.FeatureValues[0]
            player_tasks = feature.FeatureValues[1]

            self._player_count += 1 if player_ct > 0 else 0
            self._total_count += player_ct
            for key in player_tasks.keys():
                if key in self._by_task:
                    self._by_task[key] += player_tasks[key]
                else:
                    self._by_task[key] = player_tasks[key]

    def _getFeatureValues(self) -> List[Any]:
        return [self._total_count, self._by_task, self._player_count]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from Extractor's version of the function, only makes the Feature-related modes supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION]

    def Subfeatures(self) -> List[str]:
        return ["ByTask", "Players"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
