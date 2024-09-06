# import standard libraries
import abc
import logging
from typing import Any, Dict, List
# import local files
from ogd.core.schemas.games.ExtractorSchema import ExtractorSchema
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class SubfeatureSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._return_type : str
        self._description : str    

        if not isinstance(all_elements, dict):
            self._elements = {}
            Logger.Log(f"For {name} subfeature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "return_type" in all_elements.keys():
            self._return_type = SubfeatureSchema._parseReturnType(all_elements['return_type'])
        else:
            self._return_type = "Unknown"
            Logger.Log(f"{name} subfeature config does not have an 'return_type' element; defaulting to return_type='{self._return_type}", logging.WARN)
        if "description" in all_elements.keys():
            self._description = SubfeatureSchema._parseDescription(all_elements['description'])
        else:
            self._description = "No description"
            Logger.Log(f"{name} subfeature config does not have an 'description' element; defaulting to description='{self._description}'", logging.WARN)
        
        _leftovers = { key : val for key,val in all_elements.items() if key not in {"return_type", "description"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Description(self) -> str:
        return self._description

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ReturnType}*, {self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += f'   (other items: {self.NonStandardElements}'
        return ret_val

    @staticmethod
    def _parseReturnType(return_type):
        ret_val : str
        if isinstance(return_type, str):
            ret_val = return_type
        else:
            ret_val = str(return_type)
            Logger.Log(f"Subfeature return_type was not a string, defaulting to str(return_type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Extractor description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

class FeatureSchema(ExtractorSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._subfeatures : Dict[str, SubfeatureSchema]
        self._return_type : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "return_type" in all_elements.keys():
            self._return_type = FeatureSchema._parseReturnType(all_elements['return_type'], feature_name=name)
        else:
            self._return_type = ""
            Logger.Log(f"{name} Feature config does not have an 'return_type' element; defaulting to return_type='{self._return_type}'", logging.WARN)
        if "subfeatures" in all_elements.keys():
            self._subfeatures = FeatureSchema._parseSubfeatures(all_elements['subfeatures'])
        else:
            self._subfeatures = {}

        _elements = { key : val for key,val in all_elements.items() if key not in {"return_type", "subfeatures"} }
        super().__init__(name=name, all_elements=_elements)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Subfeatures(self) -> Dict[str, SubfeatureSchema]:
        return self._subfeatures

    @staticmethod
    def _parseReturnType(return_type, feature_name:str=""):
        ret_val : str
        if isinstance(return_type, str):
            ret_val = return_type
        else:
            ret_val = str(return_type)
            Logger.Log(f"Feature {feature_name} return_type was not a string, defaulting to str(return_type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSubfeatures(subfeatures) -> Dict[str, SubfeatureSchema]:
        ret_val : Dict[str, SubfeatureSchema]
        if isinstance(subfeatures, dict):
            ret_val = {name:SubfeatureSchema(name=name, all_elements=elems) for name,elems in subfeatures.items()}
        else:
            ret_val = {}
            Logger.Log(f"Extractor subfeatures was unexpected type {type(subfeatures)}, defaulting to empty list.", logging.WARN)
        return ret_val
