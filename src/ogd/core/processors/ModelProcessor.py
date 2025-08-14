import logging
from typing import List, Type, Optional

from ogd.common.models.Feature import Feature
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.registries.ModelRegistry import ModelRegistry
from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class ModelProcessor(ExtractorProcessor):
    def __init__(self, LoaderClass:Type[GeneratorLoader], game_schema: GameSchema, feature_overrides:Optional[List[str]]=None):
        self._player_id    : str = "population"
        self._session_id   : str = "population"
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)

    def InitializeModels(self):
        self._registry = self._createRegistry()
        self._registry._loadFromSchema(schema=self._game_schema, loader=self._loader, overrides=self._overrides)
            
    def ProcessFeature(self, feature: Feature):
        # self._registry = self._createRegistry()
        if self._registry:
            self._registry._updateFromFeature(feature)

    def TrainModels(self):
        # self._registry = self._createRegistry()
        if self._registry:
            self._registry.TrainModels()

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.POPULATION

    def _createRegistry(self) -> ModelRegistry:
        return ModelRegistry(mode=ExtractionMode.PLAYER)
    
    def _getGeneratorNames(self) -> List[str]:
        return self._registry._getGeneratorNames() if self._registry else []
    @property
    def _playerID(self) -> str: return self._player_id
    @property
    def _sessionID(self) -> str: return self._session_id
    def _processEvent(self, event: Event): pass
    def _getLines(self) -> List[ExportRow]: return []
    def _getFeature(self, order:int) -> List[Feature]: return []
    def _clearLines(self) -> None: self._registry = self._createRegistry()
