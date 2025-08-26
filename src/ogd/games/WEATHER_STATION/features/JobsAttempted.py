# import libraries
from typing import Any, List, Optional, Dict
from statistics import mean, stdev
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from .utils import _getIndexNameFromEvent

# lv1-jobs-attempted
class JobsAttempted(PerCountFeature):
    
    PUZZLE_INDEX_MAP = {
        "lv0-battery": 0,
        "lv0-thermometer": 1,
        "lv0-data_logger": 2,
        "lv0-turbine": 3,
        "lv0-solar": 4,

        "lv1-battery": 5,
        "lv1-thermometer": 6, 
        "lv1-data_logger": 7,
        "lv1-turbine": 8,
        "lv1-solar": 9,

        "lv2-battery": 10,
        "lv2-thermometer": 11,
        "lv2-data_logger": 12,
        "lv2-turbine": 13,
        "lv2-solar": 14,
        
        "lv3-battery": 15,
        "lv3-thermometer": 16,
        "lv3-data_logger": 17,
        "lv3-turbine": 18,
        "lv3-solar": 19,
        
        "lv4-battery": 20,
        "lv4-thermometer": 21,
        "lv4-data_logger": 22,
        "lv4-turbine": 23,
        "lv4-solar": 24,

        "lv5-battery": 25,
        "lv5-thermometer": 26,
        "lv5-data_logger": 27,
        "lv5-turbine": 28,
        "lv5-solar": 29,
    }

    @classmethod
    def _get_puzzle_list(cls) -> List[str]:
        """Generate PUZZLE_LIST from PUZZLE_INDEX_MAP to ensure consistency."""
        return [puzzle for puzzle, _ in sorted(cls.PUZZLE_INDEX_MAP.items(), key=lambda x: x[1])]

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        if self.CountIndex is not None:
            self.puzzle_index = self.CountIndex
            self.puzzle_name = self._get_puzzle_list()[self.CountIndex]
        else:
            raise ValueError("JobsAttempted was not given a count index!")
            
        self.num_starts = 0
        self.num_completes = 0
        self.cur_start_time = None
        self.durations = [] # in seconds

        # self.cur_session = None

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["start_puzzle", "complete_puzzle"]

    
    def _validateEventCountIndex(self, event: Event):
        index_name = _getIndexNameFromEvent(event)
        if index_name is not None and index_name in self.PUZZLE_INDEX_MAP:
            return self.CountIndex == self.PUZZLE_INDEX_MAP[index_name]
        return False


    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        
        index_name = _getIndexNameFromEvent(event)

        # PerCountFeature.WarningMessage(index_name)

        # if index_name is not None and index_name in self.PUZZLE_INDEX_MAP:
        if event.EventName == "start_puzzle":
                self.puzzle_name = index_name
                self.puzzle_index = self.PUZZLE_INDEX_MAP[index_name]
                self.num_starts = self.num_starts + 1
                self.cur_start_time = event.GameState.get("seconds_from_launch", None)
            
        if event.EventName == "complete_puzzle":
                self.num_completes = self.num_completes + 1
                if self.cur_start_time is not None:
                    end_time = event.GameState.get("seconds_from_launch", None)
                    if end_time is not None:
                        self.durations.append(end_time - self.cur_start_time)

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        percent_complete = (self.num_completes / self.num_starts * 100) if self.num_starts > 0 else 0
        
        avg_time = mean(self.durations) if self.durations else 0
        std_time = stdev(self.durations) if len(self.durations) > 1 else 0
        
        difficulties = {
            "experimentation": 0,
            "modeling": 0, 
            "argumentation": 0,
            "topicComplexity": 0
        }
        
        return [self.puzzle_index, self.puzzle_name, self.num_starts, self.num_completes, percent_complete, avg_time, std_time, difficulties]

    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-per-attempt",  "std-dev-per-attempt", "job-difficulties"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION]