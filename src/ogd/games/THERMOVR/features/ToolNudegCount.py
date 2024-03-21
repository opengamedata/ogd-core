from typing import Any, List
from enum import Enum
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.generators.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class Thermotool(Enum):
    INSULATION = "insulation"
    LOWER_STOP = "lower_stop"
    UPPER_STOP = "upper_stop"
    INCREASE_WEIGHT = "increase_weight"
    DECREASE_WEIGHT = "decrease_weight"
    HEAT = "heat"
    COOLING = "cooling"
    CHAMBER_TEMPERATURE = "chamber_temperature"
    CHAMBER_PRESSURE = "chamber_pressure"

class ToolNudgeCount(SessionFeature):

    def __init__(self, params:ExtractorParameters, player_id:str):
        self._player_id = player_id
        self._tool_nudge_count = {tool: 0 for tool in Thermotool}
        super().__init__(params=params)

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["click_tool_increase", "click_tool_decrease"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
            if event.EventType == "click_tool_increase" or event.EventType == "click_tool_decrease":
                tool_name = event.EventData.get('tool_name', None)
                if tool_name:
                    tool = Thermotool(tool_name)
                    self._tool_nudge_count[tool] += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return list(self._tool_nudge_count.values())
