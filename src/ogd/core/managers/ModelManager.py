import logging
from datetime import datetime
from typing import List, Type, Optional

from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.ModelProcessor import ModelProcessor
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
# from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.models.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.utils.Logger import Logger

class ModelManager:
    def __init__(self, generator_cfg:GeneratorCollectionConfig, LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]):
        self._models: Optional[ModelProcessor] = None
        if LoaderClass is not None:
            self._models = ModelProcessor(LoaderClass=LoaderClass, generator_cfg=generator_cfg, feature_overrides=feature_overrides)
            self._models.InitializeModels()
        else:
            Logger.Log("ModelManager did not set up a ModelProcessor, no LoaderClass was given!", logging.WARN)

    def ProcessFeature(self, features: List[Feature]):
        # REFINED: A single, clean public method to process a list of features.
        if not self._models:
            return
        start = datetime.now()
        Logger.Log(f"ModelManager processing {len(features)} features...", logging.INFO)
        for feature in features:
            self._models.ProcessFeatures(feature)
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