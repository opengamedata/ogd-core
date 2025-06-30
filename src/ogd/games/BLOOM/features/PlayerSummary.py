import logging
from datetime import timedelta
from multiprocessing.sharedctypes import Value
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from time import sleep
from typing import Optional, Dict, Any, List


class PlayerSummary(SessionFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._summary = {}
        self.player_won = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["CountyUnlockCount", "ActiveTime", "NumberOfSessionsPerPlayer", "GameCompletionStatus"]

    def _updateFromEvent(self, event: Event) -> None:
        pass
       
    def _updateFromFeatureData(self, feature: FeatureData):
        # print(f"Processing feature: {feature}")
        player_id = feature.PlayerID

        if feature.ExportMode == ExtractionMode.PLAYER:
            if player_id not in self._summary:
                self._summary[player_id] = {
                    "active_time": 0,
                    "counties_unlocked": 0,
                    "sessions": set(),
                    "num_sessions": 0
                }

            if feature.FeatureType == "CountyUnlockCount":
                # print(f"Processing CountyUnlockCount for player {player_id}: {feature.FeatureValues[0]}")
                # print(feature)
                self._summary[player_id]["counties_unlocked"] = feature.FeatureValues[0]

            elif feature.FeatureType == "ActiveTime":
                # print(f"Processing ActiveTime for player {player_id}: {feature.FeatureValues[1]}")
                if isinstance(feature.FeatureValues[0], timedelta):
                    self._summary[player_id]["active_time"] += feature.FeatureValues[0].total_seconds()
                elif isinstance(feature.FeatureValues[0], str) and feature.FeatureValues[0] == "No events":
                    pass
                else:
                    raise ValueError(f"PlayerSummary got {feature.Name} feature with value {feature.FeatureValues[0]} of non-timedelta type {type(feature.FeatureValues[0])} in the {feature.FeatureNames[0]} column!")
            elif feature.FeatureType == "GameCompletionStatus":
                if feature.FeatureValues[0] == 'WIN':
                    self._summary[player_id]["counties_unlocked"] += 1
                    # print(f"Updated summary for player {player_id}: {self._summary[player_id]}")
        elif feature.ExportMode == ExtractionMode.SESSION:
            if feature.FeatureType == "NumberOfSessionsPerPlayer":
                # print(f"Processing Session for player {player_id}: {feature.FeatureValues[0]}")
                self._summary[player_id]["sessions"].add(feature.SessionID)
                self._summary[player_id]["num_sessions"] = len(self._summary[player_id]["sessions"])

       

    def _getFeatureValues(self) -> List[Any]:
        return [self._summary]
    

    def Subfeatures(self) -> List[str]:
        return []

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
