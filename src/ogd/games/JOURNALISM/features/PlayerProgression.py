# import libraries
from typing import Any, List, Optional, Dict
from statistics import mean, stdev
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

# lv1-jobs-attempted
class PlayerProgression(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes
        self.links = {} # nested dict (src_hub_id -> dest_hub_id -> count & type) of links
        self.prev_hub_id = None
        self.session_id = None

        
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["hub_choice_click"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        session_id = event.SessionID
        if session_id != self.session_id:
            self.session_id = session_id
            self.prev_hub_id = None

        

        hub_id = event.EventData.get("node_id")
        choice_id = event.EventData.get("next_node_id")

        # update nodes
        if hub_id not in self.nodes:
            self.nodes[hub_id] = {
                "node_type": "hub",
                "node_count": 0,
            }
        self.nodes[hub_id]["node_count"] += 1

        if choice_id not in self.nodes:
            self.nodes[choice_id] = {
                "node_type": "choice",
                "node_count": 0,
            }
        self.nodes[choice_id]["node_count"] += 1

        # update links
        if hub_id not in self.links:
            self.links[hub_id] = {}

        if choice_id not in self.links[hub_id]:
            self.links[hub_id][choice_id] = {
                "link_count": 0,
                "link_type": "choice",
            }
        self.links[hub_id][choice_id]["link_count"] += 1

        if self.prev_hub_id and hub_id != self.prev_hub_id:
            if self.prev_hub_id not in self.links:
                self.links[self.prev_hub_id] = {}
            if hub_id not in self.links[self.prev_hub_id]:
                self.links[self.prev_hub_id][hub_id] = {
                    "link_count": 0,
                    "link_type": "hub",
                }
            self.links[self.prev_hub_id][hub_id]["link_count"] += 1

        self.prev_hub_id = hub_id
 
    def _updateFromFeatureData(self, feature: FeatureData):
        return 

    def _getFeatureValues(self) -> List[Any]:
        nodes = [{"id": node_id, "node_name": node_id, "node_type": node["node_type"], "node_count": node["node_count"]} for node_id, node in self.nodes.items()]
        links = [{"source": src_hub_id, "target": dest_hub_id, "link_count": link["link_count"], "link_type": link["link_type"]} for src_hub_id, dest_hub_links in self.links.items() for dest_hub_id, link in dest_hub_links.items()]

        ret = {
            "nodes": nodes,
            "links": links,
            "encodings": {
                "nodeColor":"node_type",
                "nodeSize": "node_count",
                "nodeLabel": "node_name",
		        "nodeTooltip": None,
		        "linkWidth": "link_count",
            }
        }
        return [ret]

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION]