# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class PlayerProgression(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes
        self.links = {} # nested dict (src_hub_id -> dest_hub_id -> count & type) of links
        self.prev_node = {}
        self.current_session_id = None
        self.prev_event_timestamp = timedelta(0)
        self.hybernation_time = timedelta(0)
        self.game_start_timestamp = timedelta(0)

        
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.UserID is None or event.UserID == "":
            return
        
        # measure time gap between sessions
        session_id = event.SessionID
        if event.EventName == "click_play_game":
            self.game_start_timestamp = event.Timestamp

        if self.current_session_id is None:
            self.current_session_id = session_id
        
        if session_id != self.current_session_id:
            self.hybernation_time += event.Timestamp - self.prev_event_timestamp
            self.prev_event_timestamp = event.Timestamp
            self.current_session_id = session_id

        # update starting node (Hillside) based on click_play_game event
        # if event.EventName == "click_play_game":
        #     self.nodes["Hillside"] = {
        #         "node_count": 1,
        #         "percentage_completed": 0,
        #         "time_spent": timedelta(0),
        #     }
        #     self.prev_node = {"id": "Hillside", "timestamp": event.Timestamp}


        # update ending node (Urban) based on win_game event
        if event.EventName == "win_game":     
            self.nodes["Urban"] = {     
                "node_count": 1,
                "percentage_completed": 1,
                "time_spent": event.Timestamp - self.prev_node["timestamp"] - self.hybernation_time,
            }
            self.hybernation_time = timedelta(0)
            
        # update intermediate nodes and links for county_unlocked event
        if event.EventName == "county_unlocked":
            cur_node = {"id": event.EventData.get("county_name"), "timestamp": event.Timestamp}

            # update nodes
            if cur_node["id"] not in self.nodes:
                self.nodes[cur_node["id"]] = {
                    "node_count": 1,
                    "percentage_completed": 0,
                    "time_spent": timedelta(0),
                }
            
            if self.prev_node and event.EventName == "county_unlocked":
                self.nodes[self.prev_node["id"]]["percentage_completed"] = 1
                self.nodes[self.prev_node["id"]]["time_spent"] = event.Timestamp - self.prev_node["timestamp"] - self.hybernation_time
                self.hybernation_time = timedelta(0)
                
            # update links
            if self.prev_node and cur_node["id"] != self.prev_node["id"]:
                if self.prev_node["id"] not in self.links:
                    self.links[self.prev_node["id"]] = {}
                if cur_node["id"] not in self.links[self.prev_node["id"]]:
                    self.links[self.prev_node["id"]][cur_node["id"]] = {
                        "link_count": 1,
                    }

            self.prev_node = cur_node
        self.prev_event_timestamp = event.Timestamp
 
    def _updateFromFeatureData(self, feature: FeatureData):
        return 

    def _getFeatureValues(self) -> List[Any]:
        return [{"nodes": self.nodes, "links": self.links}]

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]