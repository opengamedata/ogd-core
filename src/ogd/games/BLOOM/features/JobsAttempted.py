# import libraries
from typing import Any, List, Optional, Dict
from statistics import mean, stdev
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class JobsAttempted(Extractor):
    
    COUNTY_INDEX_MAP = {
        "Hillside": 0,
        "Forest": 1, 
        "Prairie": 2,
        "Wetland": 3,
        "Urban": 4
    }

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        county_list = ["Hillside","Forest", "Prairie", "Wetland", "Urban"]
        
        if self.CountIndex is not None:
            self.county_index = self.CountIndex
            self.county_name = county_list[self.CountIndex]
        else:
            raise ValueError("JobsAttempted was not given a count index!")
            
        self.num_starts = 1
        self.num_completes = 0
        self.unlock_times = [] 
        self.player_won = False
        
        self.county_unlock_time = None
        self.next_county_unlock_time = None

        self.session_new_game = False
        self.session_resumed = False
        self.session_started = False

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_new_game", "click_resume_game", "game_start", "county_unlocked", "win_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:

        if event.EventName == "click_new_game":
            self.session_new_game = True
            self.session_resumed = False
            self.session_started = False

        elif event.EventName == "click_resume_game":
            self.session_resumed = True

        elif event.EventName == "game_start":
            if self.session_new_game and not self.session_resumed:
                if self.county_index == 0:
                    self.num_starts += 1
            self.session_started = True  

        elif event.EventName == "county_unlocked":
            county_name = event.EventData.get("county_name")
            if county_name == self.county_name:
                self.num_starts += 1
                self.county_unlock_time = event.Timestamp
            elif self._is_next_county(county_name):
                self.num_completes += 1
                self.next_county_unlock_time = event.Timestamp
                if self.county_unlock_time:
                    time_diff = self.next_county_unlock_time - self.county_unlock_time
                    self.unlock_times.append(time_diff.total_seconds())

        elif event.EventName == "win_game":
            if self.county_index == 4 or self.county_name == "Urban":
                self.player_won = True


        # if event.EventName == "county_unlocked":
        #     county_name = event.EventData.get("county_name")
            
        #     if county_name == self.county_name:
        #         # print(county_name, self.county_name, self.county_index)
        #         self.num_starts += 1
        #         self.county_unlock_time = event.Timestamp
                
        #     elif self._is_next_county(county_name):
        #         self.num_completes += 1
        #         self.next_county_unlock_time = event.Timestamp
        #         if self.county_unlock_time:
        #             time_diff = self.next_county_unlock_time - self.county_unlock_time
        #             self.unlock_times.append(time_diff.total_seconds())
        # elif event.EventName == "win_game":
        #     self.player_won = True


    def _updateFromFeature(self, feature: Feature):
        pass

    def _getFeatureValues(self) -> List[Any]:
        if self.player_won:
            self.num_completes = self.num_completes + 1
            
        percent_complete = (self.num_completes / self.num_starts * 100) if self.num_starts > 0 else 0
        
        avg_time = mean(self.unlock_times) if self.unlock_times else 0
        std_time = stdev(self.unlock_times) if len(self.unlock_times) > 1 else 0
        
        difficulties = {
            "experimentation": 0,
            "modeling": 0, 
            "argumentation": 0,
            "topicComplexity": 0
        }
        
        return [self.county_index, self.county_name, self.num_starts, self.num_completes, percent_complete, avg_time, std_time, difficulties]

    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-per-attempt",  "std-dev-per-attempt", "job-difficulties"]

    def _is_next_county(self, county_name: str) -> bool:
        if county_name not in self.COUNTY_INDEX_MAP:
            return False
        next_index = self.county_index + 1
        return self.COUNTY_INDEX_MAP[county_name] == next_index

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"