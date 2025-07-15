# # import standard libraries
# import logging
# import traceback
# from typing import List, Dict, Type, Optional, Set
# # import local files
# from ogd.common.models.FeatureData import FeatureData
# from ogd.core.generators.GeneratorLoader import GeneratorLoader
# from ogd.core.registries.ModelRegistry import ModelRegistry
# from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
# from ogd.common.models.Event import Event
# from ogd.common.models.enums.ExportMode import ExportMode
# from ogd.common.models.enums.ExtractionMode import ExtractionMode
# from ogd.common.schemas.games.GameSchema import GameSchema
# from ogd.common.utils.Logger import Logger
# from ogd.common.utils.typing import ExportRow

# ## @class SessionProcessor
# #  Class to extract and manage features for a processed csv file.
# class ModelProcessor(ExtractorProcessor):

#     # *** BUILT-INS & PROPERTIES ***

#     ## Constructor for the SessionProcessor class.
#     def __init__(self, LoaderClass:Type[GeneratorLoader], game_schema: GameSchema,
#                  feature_overrides:Optional[List[str]]=None):
#         self._session_id   : Optional[str] = None  # type: Optional[str]
#         self._player_id    : Optional[str] = None  # type: Optional[str]
#         # NOTE: need session and player IDs set before we do initialization in parent.
#         super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)

#     def __str__(self):
#         return f"SessionProcessor({self._player_id}, {self._session_id})"

#     def __repr__(self):
#         return str(self)

#     # *** IMPLEMENT ABSTRACT FUNCTIONS ***

#     @property
#     def _mode(self) -> ExtractionMode:
#         return ExtractionMode.SESSION

#     @property
#     def _playerID(self) -> str:
#         return self._player_id

#     @property
#     def _sessionID(self) -> str:
#         return self._session_id

#     def _getGeneratorNames(self) -> List[str]:
#         return ["PlayerID", "SessionID"] + self._registry.GetGeneratorNames()

#     ## Function to handle processing of a single row of data.
#     def _processEvent(self, event: Event):
#         self._registry.UpdateFromEvent(event)

#     def _getLines(self) -> List[ExportRow]:
#         ret_val : ExportRow
#         # if as_str:
#         #     ret_val = [self._playerID, self._sessionID] + self._registry.GetFeatureStringValues()
#         # else:
#         ret_val = [self._playerID, self._sessionID] + self._registry.GetFeatureValues()
#         return [ret_val]

#     def _getFeatureData(self, order:int) -> List[FeatureData]:
#         return self._registry.GetFeatureData(order=order, player_id=self._player_id, sess_id=self._session_id)
    
#     def trainModels(self):
#         self._registry = self._clearLines()
#         try:
#             self._registry._loadFromSchema(schema=self._game_schema, loader=self._loader, overrides=self._overrides)
#         except Exception as e:
#             Logger.Log(f"Training failed : {e}", logging.ERROR)


#     def _processFeature(self, feature: FeatureData): 
#         print("\n\n\nInside _processFeature of ModelProcessor")  
#         self._registry = self._clearLines()
#         self._registry._updateFromFeatureData(feature)

#     # def modelOutput(self):
#     #     self.modelInfo()
        

#     def _clearLines(self) -> None:
#         Logger.Log(f"Clearing features from SessionProcessor for player {self._player_id}, session {self._session_id}.", logging.DEBUG, depth=2)
#         self._registry = ModelRegistry(mode=self._mode)
#         return self._registry

#     # *** PUBLIC STATICS ***

#     # *** PUBLIC METHODS ***

#     # *** PRIVATE STATICS ***

#     # *** PRIVATE METHODS ***



# File: src/ogd/core/processors/ModelProcessor.py

import logging
from typing import List, Type, Optional

from ogd.common.models.FeatureData import FeatureData
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
            
    def ProcessFeature(self, feature: FeatureData):
        # self._registry = self._createRegistry()
        if self._registry:
            self._registry._updateFromFeatureData(feature)

    def TrainModels(self):
        # self._registry = self._createRegistry()
        if self._registry:
            self._registry.TrainModels()

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.POPULATION

    def _createRegistry(self) -> ModelRegistry:
        return ModelRegistry(mode=self._mode)
    
    def _getGeneratorNames(self) -> List[str]:
        return self._registry._getGeneratorNames() if self._registry else []
    @property
    def _playerID(self) -> str: return self._player_id
    @property
    def _sessionID(self) -> str: return self._session_id
    def _processEvent(self, event: Event): pass
    def _getLines(self) -> List[ExportRow]: return []
    def _getFeatureData(self, order:int) -> List[FeatureData]: return []
    def _clearLines(self) -> None: self._registry = self._createRegistry()
