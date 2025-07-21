# ## import standard libraries
# import itertools
# import logging
# from datetime import datetime
# from typing import Dict, List, Type, Optional, Set, Tuple, Union
# ## import local files
# from ogd.core.generators.GeneratorLoader import GeneratorLoader
# from ogd.core.generators.models.Model import Model
# from ogd.core.processors.ModelProcessor import ModelProcessor
# from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
# from ogd.common.schemas.games.GameSchema import GameSchema
# from ogd.common.models.FeatureData import FeatureData
# from ogd.common.models.Event import Event
# from ogd.common.utils.Logger import Logger
# from ogd.common.utils.typing import ExportRow

# class ModelManager:
#     def __init__(self, game_schema:GameSchema, LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]):
#         self._game_schema    : GameSchema                 = game_schema
#         self._LoaderClass    : Optional[Type[GeneratorLoader]] = LoaderClass
#         self._overrides      : Optional[List[str]]        = feature_overrides
#         # local tracking of whether we're up-to-date on getting feature values.
#         self._up_to_date     : bool                       = True
#         self._latest_values: Dict[str, List[ExportRow]] = {}
#         self._models : ModelProcessor
#         if self._LoaderClass is not None:
#             self._models = ModelProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
#                                                 feature_overrides=feature_overrides)
#         else:
#             Logger.Log(f"ModelManager did not set up any Processors, no LoaderClass was given!", logging.WARN, depth=3)

#     # TODO: make this function take list of events, and do the loop over events as low in the hierarchy as possible, which technically should be faster.
#     def ProcessEvent(self, event:Event) -> None:
#         # 1. process at population level.
#         # NOTE: removed the skipping of unrequested modes because second-order features may need feats at levels not requested for final export.
#         if self._models is not None:
#             self._models.ProcessEvent(event=event)
#             self._up_to_date = False

#     def ProcessFeatureData(self, feature:FeatureData) -> None:
#         print("\n\n\nInside ProcessFeatureData of ModelManager")
#         start = datetime.now()
#         Logger.Log(f"Processing Feature Data for Modeling...", logging.INFO, depth=3)
#         if self._models is not None:
#             self._models._processFeature(feature)
#             Logger.Log(f"Time for modeling to process Feature Data: {datetime.now() - start}", logging.INFO, depth=3)
#         else:
#             Logger.Log(f"Skipped model processing of FeatureData, no model Processors available!", logging.INFO, depth=3)


#     def UpdateFromFeatureData(self, features: List[FeatureData]) -> None:
#         print("\n\n\nInside UpdateFromFeatureData of ModelManager")
#         if self._models is None:
#             Logger.Log("No ModelProcessor initialized, cannot update from feature data.", logging.WARN, depth=3)
#             return
#         for feature in features:
#             self._models.ProcessFeatureData(feature)
#         self._up_to_date = False

#     def GetModelNames(self) -> List[str]:
#         return self._models.GeneratorNames if self._models is not None else []
    

#     def GetModels(self, as_str:bool = False) -> Dict[str, List[ExportRow]]:
#         start = datetime.now()
#         self._try_update(as_str=as_str)
#         Logger.Log(f"Time to retrieve all models: {datetime.now() - start}", logging.INFO, depth=2)
#         return self._latest_values
    
#     def TrainModels(self) -> None:
#         if self._models:
#             self._models.trainModels()

#     def ModelOutputs(self):
#         return self._models.modelOutput()

#     def ClearPopulationLines(self) -> None:
#         if self._population is not None:
#             self._population.ClearLines()

#     def _flatHierarchy(self) -> List[ExtractorProcessor]:
#         ret_val : List[ExtractorProcessor] = []
#         if self._population is not None:
#             ret_val = [self._population]
#         if self._players is not None:
#             ret_val += self._players.values()
#         if self._sessions is not None:
#             for sess_list in self._sessions.values():
#                 ret_val += sess_list.values()
#         return ret_val

#     def _try_update(self, as_str:bool = False):
#         if not self._up_to_date:
#             self._latest_values = {
#             "models": self._models._getLines()
#         }
#             self._up_to_date = True



# File: src/ogd/core/managers/ModelManager.py

import logging
from datetime import datetime
from typing import List, Type, Optional

from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.ModelProcessor import ModelProcessor
from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.models.FeatureData import FeatureData
from ogd.common.models.Event import Event
from ogd.common.utils.Logger import Logger

class ModelManager:
    def __init__(self, game_schema:GameSchema, LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]):
        self._models: Optional[ModelProcessor] = None
        if LoaderClass is not None:
            self._models = ModelProcessor(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
            # REFINED: Initialize the models as soon as the manager is created.
            self._models.InitializeModels()
        else:
            Logger.Log("ModelManager did not set up a ModelProcessor, no LoaderClass was given!", logging.WARN)

    def ProcessFeatureData(self, features: List[FeatureData]):
        # REFINED: A single, clean public method to process a list of features.
        if not self._models:
            return
        start = datetime.now()
        Logger.Log(f"ModelManager processing {len(features)} features...", logging.INFO)
        for feature in features:
            self._models.ProcessFeature(feature)
        Logger.Log(f"Time for ModelManager to process features: {datetime.now() - start}", logging.INFO)

    def TrainModels(self) -> None:
        """
        Ensures the public TrainModels (capital T) method on the processor is called.
        """
        if self._models:
            Logger.Log("ModelManager initiating model training...", logging.INFO)
            # This MUST call the processor's TrainModels method.
            self._models.TrainModels()

    def RenderModels(self):
        # REFINED: A new, explicit method for rendering.
        if self._models and self._models._registry:
            self._models._registry.render()

    def GetModelInfo(self):
        # REFINED: A new, explicit method for getting summary info.
        if self._models and self._models._registry:
            self._models._registry.modelInfo()
            
    # Other required methods
    def ProcessEvent(self, event:Event) -> None:
        pass # Models don't currently process raw events.

    def apply_model_to_players(self, player_feature_lists):
        model_outputs = {}
        # print("player feature list", player_feature_lists)
        if self._models:
            for player_id, features in player_feature_lists.items():
                for model in self._models._registry._models.values():
                    print(model)
                    try:
                        # print(f"Applying model {model.Name} to player {player_id} with features: {features}")
                        result = model._apply(features)
                        model_outputs[player_id] = result
                    except Exception as e:
                        model_outputs[player_id] = None
                        # print(f"Failed to apply model {model.Name} to player {player_id}: {e}")
        return model_outputs