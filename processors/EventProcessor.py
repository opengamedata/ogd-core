# import libraries
from typing import Any, Callable, Dict, List, Type, Optional
# import locals
from extractors.registries.DetectorRegistry import DetectorRegistry
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from processors.Processor import Processor
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema

class EventProcessor(Processor):

    # *** BUILT-INS ***

    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema, trigger_callback:Callable[[Event], None],
                 feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema, feature_overrides=feature_overrides)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.DETECTOR

    def _getExtractorNames(self, order:int) -> Dict[str,List[FeatureData]]:
        raise NotImplementedError("Function stub! Haven't written name getter for event processor.")

    def _processEvent(self, event:Event):
        if self._registry is not None:
            self._registry.ExtractFromEvent(event)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
