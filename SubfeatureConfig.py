# import standard libraries
from typing import Dict, Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.typing import Map

class SubfeatureConfig(Schema):
    _DEFAULT_RETURN_TYPE = "str"
    _DEFAULT_DESCRIPTION = "Default Subfeature schema object. Does not correspond to any actual data."

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 return_type:Optional[str], description:Optional[str],
                 # params for parent
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}
        
        self._return_type : str = return_type or self._parseReturnType(unparsed_elements=unparsed_elements)
        self._description : str = description or self._parseDescription(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Description(self) -> str:
        return self._description

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ReturnType}*, {self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += f'   (other items: {self.NonStandardElements}'
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "SubfeatureConfig":
        """_summary_

        Example SubfeatureConfig dictionary format:

        ```json
        "Seconds": {
            "description": "The number of seconds of active time.",
            "return_type": "int"
        }
        ```

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: SubfeatureConfig
        """
        return SubfeatureConfig(name=name, return_type=None, description=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "SubfeatureConfig":
        return SubfeatureConfig(
            name="DefaultSubFeatureConfig",
            return_type=cls._DEFAULT_RETURN_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(unparsed_elements:Map) -> str:
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["return_type"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_RETURN_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
