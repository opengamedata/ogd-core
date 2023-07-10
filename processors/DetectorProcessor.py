# import libraries
from typing import Any, Callable, Dict, List, Type, Optional
# import locals
from extractors.registries.DetectorRegistry import DetectorRegistry
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from processors.ExtractorProcessor import ExtractorProcessor
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.games.GameSchema import GameSchema
from utils import ExportRow

class DetectorProcessor(ExtractorProcessor):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema: GameSchema, LoaderClass: Type[ExtractorLoader], trigger_callback:Callable[[Event], None],
                 feature_overrides:Optional[List[str]]=None):
        # TODO: Consider having multiple registries for per-player or per-session kinds of things.
        super().__init__(game_schema=game_schema, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry = DetectorRegistry(mode=self._mode, trigger_callback=trigger_callback)
        self._registry.LoadFromSchema(schema=game_schema, loader=self._loader, overrides=feature_overrides)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.DETECTOR

    @property
    def _playerID(self) -> str:
        return "detectors"

    @property
    def _sessionID(self) -> str:
        return "detectors"

    def _getExtractorNames(self, order:int) -> Dict[str,List[FeatureData]]:
        raise NotImplementedError("Function stub! Haven't written name getter for detector processor.")

    def _processEvent(self, event:Event):
        if self._registry is not None:
            self._registry.ExtractFromEvent(event)

    def _getLines(self) -> List[ExportRow]:
        return []

    def _clearLines(self):
        if self._registry is not None:
            self._registry.LoadFromSchema(schema=self._game_schema, loader=self._loader, overrides=self._overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***