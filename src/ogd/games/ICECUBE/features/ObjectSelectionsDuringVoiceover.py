# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
# count of object_selected 
# between script_audio_started and script_audio_complete
# return the # of object_selected during audio playing
class ObjectSelectionsDuringVoiceover (SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._select_count = 0
        self._audio_started = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["script_audio_started","script_audio_complete","object_selected"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "script_audio_complete" or event.EventName == "scene_changed":
            self._audio_started = False
            return
        if not self._audio_started:
            if event.EventName == "script_audio_started":
                self._audio_started = True
            return
        if event.EventName == "object_selected":
            self._select_count += 1
        return


    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._select_count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"