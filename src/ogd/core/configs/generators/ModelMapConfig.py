# import standard libraries
import logging
from typing import Dict, Optional, Self
# import local files
from ogd.common.configs.Config import Config
from ogd.core.configs.generators.ModelConfig import ModelConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map


class ModelMapConfig(Config):
    _DEFAULT_MODELS = {}

    def __init__(self, name:str, models:Optional[Dict[str, ModelConfig]]=None, other_elements:Optional[Map]=None):
        self._models = models or self._parseModels(unparsed_elements= other_elements or {})
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Models(self) -> Dict[str, ModelConfig]:
        return self._models
    
    @staticmethod
    def _parseModels(unparsed_elements:Map) -> Dict[str, ModelConfig]:
        model_dict = ModelMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["models"], to_type=dict,
            default_value=ModelMapConfig._DEFAULT_MODELS, remove_target=True)
        if isinstance(model_dict, dict):
            return {key : ModelConfig.FromDict(name=key , unparsed_elements=val) for key ,val in model_dict.items()}
        return {}

    def AsMarkdown(self) -> str:
        pass

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None):
        pass

    @classmethod
    def Default(cls):
        pass