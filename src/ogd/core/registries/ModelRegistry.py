# ## import standard libraries
# import logging
# from collections import OrderedDict
# from typing import Any, Dict, List, Optional, Set

# ## import local files
# from ogd.core.generators.Generator import Generator, GeneratorParameters
# from ogd.core.generators.GeneratorLoader import GeneratorLoader
# from ogd.games.LAKELAND.models.KMeansModel import KMeansModel
# from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
# from ogd.common.models.Event import Event
# from ogd.common.models.FeatureData import FeatureData
# from ogd.common.models.enums.ExtractionMode import ExtractionMode
# from ogd.common.schemas.games.GameSchema import GameSchema
# from ogd.common.models.enums.IterationMode import IterationMode
# from ogd.common.utils.Logger import Logger


# class ModelRegistry(GeneratorRegistry):
#     def __init__(self, mode: ExtractionMode):

#         super().__init__(mode=mode)
#         self._models: OrderedDict[str, KMeansModel] = OrderedDict()
#         self._feature_registry: Dict[str, List[GeneratorRegistry.Listener]] = {}


#     def __str__(self) -> str:
#         ret_val: List[str] = [str(model) for model in self._models.values()]
#         return '\n'.join(ret_val)


#     def to_string(self, num_lines: Optional[int] = None) -> str:
#         ret_val: List[str] = [str(model) for model in self._models.values()]
        
#         if num_lines is None:
#             return '\n'.join(ret_val)
#         else:
#             return '\n'.join(ret_val[:num_lines])


#     def _register(self, extractor: Generator, iter_mode: IterationMode):
#         print("\n\n\nInside _register of ModelRegistry with extractor:", extractor)
#         if isinstance(extractor, KMeansModel):
#             _listener = GeneratorRegistry.Listener(name=extractor.Name, mode=iter_mode)
#             _feature_deps = extractor.FeatureFilter(mode=self._mode)
#             _event_deps = extractor.EventFilter(mode=self._mode)

#             self._models[extractor.Name] = extractor

#             print("The _feature_deps inside ModelRegistry._register:", _feature_deps)
#             for _feature_dep in _feature_deps:
#                 if _feature_dep not in self._feature_registry.keys():
#                     self._feature_registry[_feature_dep] = []
#                 self._feature_registry[_feature_dep].append(_listener)


#             if "all_events" in _event_deps:
#                 self._event_registry["all_events"].append(_listener)
#             else:
#                 for event in _event_deps:
#                     if event not in self._event_registry.keys():
#                         self._event_registry[event] = []
#                     self._event_registry[event].append(_listener)
#             return self._feature_registry, self._event_registry
#         else:
#             raise TypeError("ModelRegistry was given a Generator which was not a KMeansModel!")

#     def _getGeneratorNames(self) -> List[str]:
#         ret_val: List[str] = [model.Name for model in self._models.values()]
#         return ret_val


#     def _loadFromSchema(self, schema: GameSchema, loader: GeneratorLoader, overrides: Optional[List[str]] = None):
#         model_name = "KMeansModel"
#         try:
#             model_params = GeneratorParameters(
#                 name=model_name,
#                 mode=self._mode,
#                 description="Hardcoded KMeansModel for Lakeland",
#                 count_index=0
#             )
            
#             kmeans_model = KMeansModel(params=model_params)

            

#             if kmeans_model is not None and self._mode in kmeans_model.AvailableModes():
#                 x,y = self._register(extractor=kmeans_model, iter_mode=IterationMode.AGGREGATE)
#                 print(x,y)
#                 kmeans_model._updateFromFeatureData(x)
#                 kmeans_model._train()
#                 Logger.Log(f"Loaded hardcoded KMeansModel: {model_name}", logging.INFO)
#             else:
#                 Logger.Log(f"KMeansModel does not support mode {self._mode.name}", logging.WARNING)
                
#         except Exception as e:
#             Logger.Log(f"Failed to create hardcoded KMeansModel: {e}", logging.ERROR)


#     def _updateFromEvent(self, event: Event) -> None:
#         """Perform model updates from events.

#         Sends events to all registered models that are listening for the specific event.

#         :param event: The event to process
#         :type event: Event
#         """
#         listener: GeneratorRegistry.Listener = GeneratorRegistry.Listener("EMPTY", IterationMode.AGGREGATE)
        
#         try:
#             for listener in self._event_registry.get(event.EventName, []):
#                 if listener.name in self._models.keys():
#                     self._models[listener.name].UpdateFromEvent(event)

#             for listener in self._event_registry["all_events"]:
#                 if listener.name in self._models.keys():
#                     self._models[listener.name].UpdateFromEvent(event)
                    
#         except KeyError as err:
#             Logger.Log(f"{listener.name} found event {event} missing expected key: {err}", logging.ERROR)


#     def _updateFromFeatureData(self, feature: FeatureData) -> None:
#         print("\n\n\nInside _updateFromFeatureData of ModelRegistry")
#         listeners = self._feature_registry.get(feature.FeatureType, [])
#         print('\n\n\n\n\nhihih')
#         print(listeners)
#         for listener in listeners:
#             if listener.name in self._models.keys():
#                 _model = self._models[listener.name]
#                 if feature.ExportMode in _model.FeatureDependencyModes():
#                     self._models[listener.name].UpdateFromFeatureData(feature)
#                 Logger.Log(f"[ModelRegistry] Routing {feature.Name} to {listener.name}", logging.DEBUG)


#     def render(self):
#         for model in self._models.values():
#             try:
#                 model._render()
#             except Exception as e:
#                 Logger.Log(f"Failed to render model {model.Name}: {e}", logging.ERROR)


#     def modelInfo(self):
#         for model in self._models.values():
#             try:
#                 model._modelInfo()
#             except Exception as e:
#                 Logger.Log(f"Failed to generate model info for {model.Name}: {e}", logging.ERROR)




# File: src/ogd/core/registries/ModelRegistry.py

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
                # self._updateFromFeatureData(FeatureData)
                self.TrainModels()
        except Exception as e:
            Logger.Log(f"Failed to create hardcoded KMeansModel: {e}", logging.ERROR)

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        Logger.Log(f"Updating models with feature data: {feature.Name}", logging.DEBUG)
        listeners = self._feature_registry.get(feature.Name, [])
        for listener in listeners:
            if listener.name in self._models:
                self._models[listener.name]._updateFromFeatureData(feature)
        
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