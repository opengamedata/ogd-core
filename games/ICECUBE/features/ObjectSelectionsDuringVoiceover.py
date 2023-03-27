# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
# count of object_selected 
# between script_audio_started and script_audio_complete
# return the # of object_selected during audio playing
class ObjectSelectionsDuringVoiceover (SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._select_count = 0
        self._audio_started = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["script_audio_started","script_audio_complete","object_selected"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
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


    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._select_count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"