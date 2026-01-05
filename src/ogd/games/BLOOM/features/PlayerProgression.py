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
        self.prev_event_timestamp = None

        
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        # return ["click_new_game", "click_resume_game", "county_unlocked", "win_game"]
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # if event.EventName == "click_resume_game" and self.prev_event_timestamp is not None:

        # if event.EventName == "click_play_game":
        #     self.prev_node = {}
        #     return

        if event.EventName == "win_game":     
            self.nodes["Urban"] = {     
                "node_count": 1,
                "percentage_completed": 1,
                "time_spent": event.Timestamp - self.prev_node["timestamp"],
            }
            
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
                self.nodes[self.prev_node["id"]]["time_spent"] = event.Timestamp - self.prev_node["timestamp"]
                

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