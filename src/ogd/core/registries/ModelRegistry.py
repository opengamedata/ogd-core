import logging
from collections import OrderedDict
from typing import Dict, List, Optional

from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.games.LAKELAND.models.KMeansModel import KMeansModel
from ogd.games.BLOOM.models.LogisticRegressionModel import LogisticRegressionModel
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig

from ogd.core.generators.models.PopulationModel import PopulationModel

from ogd.common.models.Event import Event
from ogd.common.models.Feature import Feature
from ogd.common.models.enums.ExtractionMode import ExtractionMode
# from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.models.enums.IterationMode import IterationMode
from ogd.common.utils.Logger import Logger

class ModelRegistry(GeneratorRegistry):
    def __init__(self, mode: ExtractionMode):
        super().__init__(mode=mode)
        self._models: OrderedDict[str, KMeansModel] = OrderedDict()
        self._feature_registry: Dict[str, List[GeneratorRegistry.Listener]] = {}


    def _register(self, model: PopulationModel, iter_mode: IterationMode):
        if not isinstance(model, PopulationModel):
            raise TypeError("ModelRegistry can only register PopulationModel subclasses!")

        listener = GeneratorRegistry.Listener(name=model.Name, mode=iter_mode)

        for feat in model.FeatureFilter(mode=self._mode):
            self._feature_registry.setdefault(feat, []).append(listener)
        self._models[model.Name] = model

    
    # def _loadGenerators(self, generator_cfg: GeneratorCollectionConfig, loader: GeneratorLoader, overrides: Optional[List[str]] = None):
    #     model_name = "KMeansModel"
    #     try:
    #         model_params = GeneratorParameters(name=model_name, mode=self._mode, description="Hardcoded KMeansModel", count_index=0)
    #         kmeans_model = KMeansModel(params=model_params)
    #         if self._mode in kmeans_model.AvailableModes():
    #             self._register(model=kmeans_model, iter_mode=IterationMode.AGGREGATE)
    #             Logger.Log(f"Loaded and registered hardcoded KMeansModel: {model_name}", logging.INFO)
    #     except Exception as e:
    #         Logger.Log(f"Failed to create hardcoded KMeansModel: {e}", logging.ERROR)

        # try:
        #     lr_params = GeneratorParameters(name="LogisticRegressionModel", mode=self._mode, 
        #                                     description="Hard-coded LogisticRegressionModel", count_index=0)
        #     logreg = LogisticRegressionModel(params=lr_params)
        #     if self._mode in logreg.AvailableModes():
        #         self._register(model=logreg, iter_mode=IterationMode.AGGREGATE)
        #         Logger.Log("Loaded LogisticRegressionModel", logging.INFO)
        # except Exception as e:
        #     Logger.Log(f"Failed to create LogisticRegressionModel: {e}", logging.ERROR)


    def _loadGenerators(self, generator_cfg: GeneratorCollectionConfig, loader: GeneratorLoader, overrides: Optional[List[str]] = None):
        print("inside loadgenerator of model registry")
        model_pairs = loader.loadConfiguredModels(generator_cfg, self._mode)
        print("model pairs loaded:", model_pairs)
        for model_name, model in model_pairs:
            self._register(model=model, iter_mode=IterationMode.AGGREGATE) 


    def _updateFromFeature(self, feature: Feature) -> None:
        Logger.Log(f"Updating models with feature data: {feature.Name}", logging.DEBUG)
        listeners = self._feature_registry.get(feature.Name, [])
        # print("\n\n\n\n\nFeature listeners:", listeners)
        for listener in listeners:
            # print("\n\n\n\n\nProcessing listener:", listener)
            Logger.Log(f"Routing {feature.Name} to {listener.name}", logging.DEBUG)
            if listener.name in self._models:
                # print(feature)
                self._models[listener.name]._updateFromFeature(feature)
        # self._models[listener.name].Train()
        
    def TrainModels(self):
        Logger.Log(f"Beginning training for {len(self._models)} models...", logging.INFO)
        for model in self._models.values():
            try:
                model.Train()
            except Exception as e:
                Logger.Log(f"Failed to train model {model.Name}: {e}", logging.ERROR)

    def render(self):
        for model in self._models.values():
            model.Render()

    def modelInfo(self):
        for model in self._models.values():
            model.ModelInfo()

    def _getGeneratorNames(self) -> List[str]:
        return list(self._models.keys())

    def _updateFromEvent(self, event: Event) -> None:
        pass 