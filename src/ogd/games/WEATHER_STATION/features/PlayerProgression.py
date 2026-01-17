# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from .utils import _getIndexNameFromEvent

class PlayerProgression(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes (puzzle_id -> node info)
        self.links = {} # nested dict (src_puzzle_id -> dest_puzzle_id -> count & type) of links
        self.prev_puzzle_started = None
        self.prev_puzzle_started = None
        self.prev_puzzle_started_time = None
        self.session_id = None

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["start_puzzle", "complete_puzzle"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        session_id = event.SessionID
        if session_id != self.session_id:
            self.session_id = session_id
            # self.prev_puzzle_started = None
            self.prev_puzzle_started = None
            self.prev_puzzle_started_time = None

        puzzle_id = _getIndexNameFromEvent(event)
        if puzzle_id is None:
            return

        if event.EventName == "start_puzzle":            
            if puzzle_id not in self.nodes:
                self.nodes[puzzle_id] = {"node_count": 0, "time_spent": 0, "completed_count": 0}
            self.nodes[puzzle_id]["node_count"] += 1

            # create a link showing progression
            if self.prev_puzzle_started and puzzle_id != self.prev_puzzle_started:
                if self.prev_puzzle_started not in self.links:
                    self.links[self.prev_puzzle_started] = {}
                if puzzle_id not in self.links[self.prev_puzzle_started]:
                    self.links[self.prev_puzzle_started][puzzle_id] = {
                        "link_count": 0,
                    }
                self.links[self.prev_puzzle_started][puzzle_id]["link_count"] += 1

            self.prev_puzzle_started = puzzle_id
            self.prev_puzzle_started_time = event.Timestamp

        # Track transitions between puzzles - only on complete_puzzle events
        if event.EventName == "complete_puzzle":
            # Track puzzle as a node when completed
            if puzzle_id not in self.nodes:
                self.nodes[puzzle_id] = {
                    "node_count": 1,
                    "time_spent": 0,
                    "completed_count": 0,
                }
            self.nodes[puzzle_id]["completed_count"] += 1

            if self.prev_puzzle_started_time is not None and self.prev_puzzle_started == puzzle_id:
                self.nodes[puzzle_id]["time_spent"] += (event.Timestamp - self.prev_puzzle_started_time).total_seconds()
                self.prev_puzzle_started = None
                self.prev_puzzle_started_time = None

            # # When a puzzle is completed, if there was a previous completed puzzle,
            # # create a link showing progression
            # if self.prev_puzzle_started and puzzle_id != self.prev_puzzle_started:
            #     if self.prev_puzzle_started not in self.links:
            #         self.links[self.prev_puzzle_started] = {}
            #     if puzzle_id not in self.links[self.prev_puzzle_started]:
            #         self.links[self.prev_puzzle_started][puzzle_id] = {
            #             "link_count": 0,
            #         }
            #     self.links[self.prev_puzzle_started][puzzle_id]["link_count"] += 1

            # Update previous puzzle to the completed one
            self.prev_puzzle_started = puzzle_id

    def _updateFromFeatureData(self, feature: FeatureData):
        return 

    def _getFeatureValues(self) -> List[Any]:
        nodes = []
        for node_id, node in self.nodes.items():
            avg_time = node["time_spent"] / node["node_count"] if node["node_count"] > 0 else 0
            nodes.append({
                "id": node_id,
                "node_name": node_id,
                "node_count": node["node_count"],
                "percentage_completed": 0 if node["node_count"] == 0 else node["completed_count"] / node["node_count"] * 100,
                "average_time_spent": avg_time,
                "node_tooltip": f"Completed {node['completed_count']} out of {node['node_count']} puzzles\nAverage time spent: {avg_time:.2f} seconds",
            })
        links = [
            {
                "source": src_puzzle_id,
                "target": dest_puzzle_id,
                "link_count": link["link_count"],
            }
            for src_puzzle_id, dest_puzzle_links in self.links.items()
            for dest_puzzle_id, link in dest_puzzle_links.items()
        ]

        ret = {
            "nodes": nodes,
            "links": links,
            "encodings": {
                "nodeColor": "percentage_completed",
                "nodeSize": "average_time_spent",
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
