# import libraries
from typing import Any, Callable, Dict, List, Type
# import locals
from detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorRegistry import ExtractorRegistry
from features.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from processors.Processor import Processor
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

class EventProcessor(Processor):
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _prepareRegistry(self) -> ExtractorRegistry:
        return DetectorRegistry()

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    def _getFeatureValues(self, export_types:ExporterTypes) -> Dict[str,List[Any]]:
        return {}

    def _getFeatureData(self, order:int) -> Dict[str,List[FeatureData]]:
        return {}

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    def _processEvent(self, event:Event):
        pass

    def _processFeatureData(self, feature:FeatureData):
        pass

    def _prepareLoader(self) -> ExtractorLoader:
        return self._LoaderClass(player_id="events", session_id="events",
                                 game_schema=self._game_schema, feature_overrides=self._overrides)

    # *** PUBLIC BUILT-INS ***

    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema, trigger_callback:Callable[[Event], None]):
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=None)
        self._registry = DetectorRegistry()
        self._loader.LoadToDetectorRegistry(registry=self._registry, trigger_callback=trigger_callback)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***