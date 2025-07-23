"""Detector Config Module
"""
# import standard libraries
from typing import Dict, Optional, Self, Set
# import local files
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.generators.GeneratorConfig import GeneratorConfig
from ogd.common.utils.typing import Map

class DetectorConfig(GeneratorConfig):
    """Schema for tracking the configuration of a detector."""
    def __init__(self, name:str,
                 # params for class
                 # params for parent
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `DetectorConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "type": "DetectorClass",
            "enabled": true,
            "description": "Description of the detected event",
        },
        ```

        :param name: _description_
        :type name: str
        :param enabled: _description_, defaults to None
        :type enabled: Optional[Set[ExtractionMode]], optional
        :param type_name: _description_, defaults to None
        :type type_name: Optional[str], optional
        :param description: _description_, defaults to None
        :type description: Optional[str], optional
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        super().__init__(name=name, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *Detector* {' (disabled)' if not ExtractionMode.DETECTOR in self.Enabled else ''}  \n{self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DetectorConfig":
        """Function to parse an AggregateConfig from a dictionary.

        Expected format:

        ```
        {
            "type": "DetectorClass",
            "enabled": true,
            "description": "Description of the detected event",
        },
        ```

        :param name: The name associated with the detector, typically but not always equal to the `"type"` value.
        :type name: str
        :param unparsed_elements: The dictionary containing the contents for the `DetectorConfig`
        :type unparsed_elements: Map
        :param key_overrides: (_Ignored_) A dictionary of overrides for keys to look for, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :return: A `DetectorConfig` with data from the given `unparsed_elements`
        :rtype: DetectorConfig
        """
        return DetectorConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "DetectorConfig":
        return DetectorConfig(name="DefaultDetectorConfig", other_elements={})
