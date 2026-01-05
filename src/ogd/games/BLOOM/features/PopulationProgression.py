# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta
import logging

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger
import json

class PopulationProgression(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes
        self.links = {} # nested dict (src_hub_id -> dest_hub_id -> count & type) of links
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["PlayerProgression"]

    def _updateFromEvent(self, event: Event) -> None:
        return 
 
    def _updateFromFeatureData(self, feature: FeatureData):
        data = feature.FeatureValues[0]
        for key, node in data["nodes"].items():
            if key is None:
                continue
            if key not in self.nodes:
                self.nodes[key] = {
                    "node_count": 0,
                    "percentage_completed": 0,
                    "time_spent": timedelta(0),
                }
            self.nodes[key]["node_count"] += node["node_count"]
            self.nodes[key]["percentage_completed"] += node["percentage_completed"]
            # Normalize time_spent to timedelta if it's an int
            time_spent = node["time_spent"]
            if isinstance(time_spent, int):
                time_spent = timedelta(seconds=time_spent)
            self.nodes[key]["time_spent"] += time_spent
        for source, targets in data["links"].items():
            if source is None:
                continue
            if source not in self.links:
                self.links[source] = {}
            for target, link_data in targets.items():
                if target is None:
                    continue
                if target not in self.links[source]:
                    self.links[source][target] = {
                        "link_count": 0,
                    }
                self.links[source][target]["link_count"] += link_data["link_count"]
         

    def _getFeatureValues(self) -> List[Any]:
        for _, node in self.nodes.items():
            node["percentage_completed"] = node["percentage_completed"] / node["node_count"] *100
            node["time_spent"] = node["time_spent"] / node["node_count"]

        nodes = [{
            "id": node_id,
            "node_name": node_id,
            "node_count": node["node_count"],
            "percentage_completed": node["percentage_completed"],
            "time_spent": node["time_spent"].total_seconds(),
            "node_tooltip": f"{node['node_count']} players visited {node_id}, {node['percentage_completed']:.2f}% completed, {node['time_spent'].total_seconds():.2f} seconds spent on average"
            } for node_id, node in self.nodes.items()]
        links = [{
            "source": src_node_id, 
            "target": dest_node_id, 
            "link_count": link["link_count"]
            } for src_node_id, dest_node_links in self.links.items() for dest_node_id, link in dest_node_links.items()]

        ret = {
            "nodes": nodes,
            "links": links,
            "encodings": {
                "nodeColor": "percentage_completed",
                "nodeSize": "time_spent",
                "nodeLabel": "node_name",
		        "nodeTooltip": "node_tooltip",
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