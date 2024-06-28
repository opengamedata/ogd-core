from typing import Any, Dict, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class LeftHandMovesCount(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self._left_hand_move_count = 0
        self._last_hand_action = None
        super().__init__(params=params)

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["grab_tool_slider", "release_tool_slider", "click_new_game", "click_reset_sim", 
                "grab_tablet", "release_tablet", "grab_workstation_handle", "release_workstation_handle",
                "click_rotate_graph_cw", "click_rotate_graph_ccw", "grab_graph_ball", "release_graph_ball",
                "click_tool_toggle", "click_tool_increase", "click_tool_decrease",
                "click_view_settings", "click_toggle_setting", 
                "click_sandbox_mode", "click_lab_mode", "click_lab_scroll_up", "click_lab_scroll_down"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        hand = event.EventData.get("hand")
        if hand == "LEFT":
            action = event.EventName.split("_")[0]  # Extract action (grab, release, click, etc.)
            if action in ["grab", "click"] or (action == "release" and self._last_hand_action != "grab"):
                self._left_hand_move_count += 1
            self._last_hand_action = action

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._left_hand_move_count]
