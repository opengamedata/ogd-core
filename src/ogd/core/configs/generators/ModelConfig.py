# import standard libraries
import logging
from typing import Dict, Optional, Set, List, Any
# import local files
from ogd.core.configs.generators.GeneratorConfig import GeneratorConfig
from ogd.core.configs.generators.SubfeatureConfig import SubfeatureConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map


class ModelConfig(GeneratorConfig):

    _DEFAULT_OUTPUT_TYPE = "str"
    _DEFAULT_X_VARIABLES = []
    _DEFAULT_PARAMS = {}

    def __init__(self, name:str,
                 enabled:Optional[set]=None,
                 type_name:Optional[str]=None,
                 description:Optional[str]=None,
                 x_variables:Optional[List[str]]=None,
                 y_variable:Optional[str]=None,
                 output_type:Optional[str]=None,
                 params:Optional[Dict[str, Any]]=None,
                 train_mode:Optional[str]=None,
                 apply_mode:Optional[str]=None,
                 other_elements:Optional[Map]=None):
        
        unparsed_elements : Map = other_elements or {}

        self._x_variables = x_variables or self._parseXVariables(unparsed_elements)
        self._y_variable = y_variable or self._parseYVariable(unparsed_elements)
        self._output_type = output_type or self._parseOutputType(unparsed_elements)
        self._params = params or self._parseParams(unparsed_elements)
        self._train_mode = train_mode or self._parseTrainMode(unparsed_elements)
        self._apply_mode = apply_mode or self._parseApplyMode(unparsed_elements)

        super().__init__(name=name, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def XVariables(self):
        return self._x_variables

    @property
    def YVariable(self):
        return self._y_variable

    @property
    def OutputType(self):
        return self._output_type

    @property
    def Params(self):
        return self._params

    @property
    def TrainMode(self):
        return self._train_mode

    @property
    def ApplyMode(self):
        return self._apply_mode

    @staticmethod
    def _parseXVariables(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["x_variables"], to_type=list,
            default_value=ModelConfig._DEFAULT_X_VARIABLES, remove_target=True)
    
    @staticmethod
    def _parseYVariable(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["y_variable"], to_type=str,
            default_value=None, remove_target=True)
    
    @staticmethod
    def _parseOutputType(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["output_type"], to_type=str,
            default_value=ModelConfig._DEFAULT_OUTPUT_TYPE, remove_target=True)
    
    @staticmethod
    def _parseParams(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["params"], to_type=dict,
            default_value=ModelConfig._DEFAULT_PARAMS, remove_target=True)
    
    @staticmethod
    def _parseTrainMode(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["train_mode"], to_type=str,
            default_value=None, remove_target=True)
    
    @staticmethod
    def _parseApplyMode(unparsed_elements):
        return ModelConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["apply_mode"], to_type=str,
            default_value=None, remove_target=True)

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides=None, default_override=None) -> "ModelConfig":
        return ModelConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "ModelConfig":
        return ModelConfig(name="DefaultModelConfig", other_elements={})
    