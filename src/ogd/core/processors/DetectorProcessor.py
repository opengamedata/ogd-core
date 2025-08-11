# import libraries
from typing import Any, Callable, Dict, List, Type, Optional
# import locals
from ogd.core.registries.DetectorRegistry import DetectorRegistry
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.GeneratorProcessor import GeneratorProcessor
from ogd.common.models.Event import Event
from ogd.common.models.Feature import Feature
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.utils.typing import ExportRow

class DetectorProcessor(GeneratorProcessor):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema:GameStoreConfig, LoaderClass: Type[GeneratorLoader], trigger_callback:Callable[[Event], None],
                 feature_overrides:Optional[List[str]]=None):
        # TODO: Consider having multiple registries for per-player or per-session kinds of things.
        super().__init__(generator_cfg=game_schema, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry = DetectorRegistry(mode=self._mode, trigger_callback=trigger_callback)
        self._registry.LoadGenerators(generator_cfg=game_schema, loader=self._loader, overrides=feature_overrides)

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

    def _getGeneratorNames(self, order:int) -> Dict[str,List[Feature]]:
        raise NotImplementedError("Function stub! Haven't written name getter for detector processor.")

    def _processEvent(self, event:Event):
        if self._registry is not None:
            self._registry.UpdateFromEvent(event)

    def _getLines(self) -> List[ExportRow]:
        return []

    def _clearLines(self):
        if self._registry is not None:
            self._registry.LoadGenerators(generator_cfg=self._generator_cfg, loader=self._loader, overrides=self._overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
