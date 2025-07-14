import logging
from collections import OrderedDict
from typing import Dict, List, Optional

from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.games.LAKELAND.models.KMeansModel import KMeansModel
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.common.models.Event import Event
from ogd.common.models.FeatureData import FeatureData
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.models.enums.IterationMode import IterationMode
from ogd.common.utils.Logger import Logger

class ModelRegistry(GeneratorRegistry):
    def __init__(self, mode: ExtractionMode):
        super().__init__(mode=mode)
        self._models: OrderedDict[str, KMeansModel] = OrderedDict()
        self._feature_registry: Dict[str, List[GeneratorRegistry.Listener]] = {}

    def _register(self, model: Generator, iter_mode: IterationMode):
        if isinstance(model, KMeansModel):
            _listener = GeneratorRegistry.Listener(name=model.Name, mode=iter_mode)
            _feature_deps = model.FeatureFilter(mode=self._mode)
            self._models[model.Name] = model

            for _feature_dep in _feature_deps:
                if _feature_dep not in self._feature_registry:
                    self._feature_registry[_feature_dep] = []
                self._feature_registry[_feature_dep].append(_listener)
        else:
            raise TypeError("ModelRegistry was given a Generator which was not a KMeansModel!")

    def _loadFromSchema(self, schema: GameSchema, loader: GeneratorLoader, overrides: Optional[List[str]] = None):
        model_name = "KMeansModel"
        try:
            model_params = GeneratorParameters(name=model_name, mode=self._mode, description="Hardcoded KMeansModel", count_index=0)
            kmeans_model = KMeansModel(params=model_params)
            if self._mode in kmeans_model.AvailableModes():
                self._register(model=kmeans_model, iter_mode=IterationMode.AGGREGATE)
                Logger.Log(f"Loaded and registered hardcoded KMeansModel: {model_name}", logging.INFO)
        except Exception as e:
            Logger.Log(f"Failed to create hardcoded KMeansModel: {e}", logging.ERROR)

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        Logger.Log(f"Updating models with feature data: {feature.Name}", logging.DEBUG)
        listeners = self._feature_registry.get(feature.Name, [])
        # print("\n\n\n\n\nFeature listeners:", listeners)
        for listener in listeners:
            # print("\n\n\n\n\nProcessing listener:", listener)
            Logger.Log(f"Routing {feature.Name} to {listener.name}", logging.DEBUG)
            if listener.name in self._models:
                # print(feature)
                self._models[listener.name]._updateFromFeatureData(feature)
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