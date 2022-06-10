# import libraries
from typing import Any, Callable, Dict, List, Type, Optional
# import locals
from extractors.detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorRegistry import ExtractorRegistry
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from processors.Processor import Processor
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from ogd_requests.Request import ExporterTypes

class EventProcessor(Processor):

    # *** BUILT-INS ***

    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema, trigger_callback:Callable[[Event], None],
                 feature_overrides:Optional[List[str]]=None):
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        self._registry = DetectorRegistry()
        self._loader.LoadToDetectorRegistry(registry=self._registry, trigger_callback=trigger_callback)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _prepareLoader(self) -> ExtractorLoader:
        return self._LoaderClass(player_id="events", session_id="events",
                                 game_schema=self._game_schema, feature_overrides=self._overrides)

    def _getExtractorNames(self, order:int) -> Dict[str,List[FeatureData]]:
        raise NotImplementedError("Function stub! Haven't written name getter for event processor.")

    def _processEvent(self, event:Event):
        if self._registry is not None:
            self._registry.ExtractFromEvent(event)

    def _processFeatureData(self, feature:FeatureData):
        if self._registry is not None:
            self._registry.ExtractFromFeatureData(feature=feature)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
