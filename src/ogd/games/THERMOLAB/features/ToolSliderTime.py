from typing import Any, Dict, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class ToolSliderTime(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self._slider_start_time = {}
        self._slider_times = {}
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["grab_tool_slider", "release_tool_slider"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "grab_tool_slider":
            tool_name = event.EventData["tool_name"]
            self._slider_start_time[tool_name] = event.Timestamp
        elif event.EventName == "release_tool_slider":
            tool_name = event.EventData["tool_name"]
            if tool_name in self._slider_start_time:
                start_time = self._slider_start_time[tool_name]
                end_time = event.Timestamp
                slider_time = end_time - start_time
                if tool_name in self._slider_times:
                    self._slider_times[tool_name].append(slider_time)
                else:
                    self._slider_times[tool_name] = [slider_time]

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._slider_times]
