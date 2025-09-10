# import standard libraries
import logging
from typing import Dict, Optional, Self
# 3rd-party Imports
from deprecated import deprecated
# import local files
from ogd.common.configs.Config import Config
from ogd.core.configs.generators.DetectorConfig import DetectorConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DetectorMapConfig(Config):
    _DEFAULT_ITERATED_DETECTORS  = {}
    _DEFAULT_AGGREGATE_DETECTORS = {}

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """
    def __init__(self, name:str,
                 percount_detectors:Optional[Dict[str, DetectorConfig]],
                 aggregate_detectors:Optional[Dict[str, DetectorConfig]],
                 other_elements:Optional[Map]=None):
        """Constructor for the `DetectorMapConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "iterated" : {
                "DetectorName1": {
                    "type": "DetectorClass",
                    "enabled": true,
                    "description": "Info about the iterated detector; the iterated is generally optional.",
                },
                "DetectorName2": {
                    ...
                },
                ...
            },
            "aggregate" : {
                "DetectorName1": {
                    "type": "DetectorClass",
                    "enabled": true,
                    "description": "Info about the aggregate (session-level) detector.",
                },
                "DetectorName2": {
                    ...
                },
                ...
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param percount_detectors: _description_
        :type percount_detectors: Dict[str, DetectorConfig]
        :param aggregate_detectors: _description_
        :type aggregate_detectors: Dict[str, DetectorConfig]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        self._iterated_detectors  : Dict[str, DetectorConfig] = percount_detectors  if percount_detectors  is not None else self._parseIteratedDetectors(unparsed_elements=other_elements or {}, schema_name=name)
        self._aggregate_detectors : Dict[str, DetectorConfig] = aggregate_detectors if aggregate_detectors is not None else self._parseAggregateDetectors(unparsed_elements=other_elements or {}, schema_name=name)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def IteratedDetectors(self) -> Dict[str, DetectorConfig]:
        """A dictionary for all the detector configurations that are iterated by game units

        :return: _description_
        :rtype: Dict[str, DetectorConfig]
        """
        return self._iterated_detectors
    @property
    @deprecated("Use the IteratedDetectors property instead")
    def PerCountDetectors(self) -> Dict[str, DetectorConfig]:
        """A dictionary for all the detector configurations that are iterated by game units

        :return: _description_
        :rtype: Dict[str, DetectorConfig]
        """
        return self.IteratedDetectors

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorConfig]:
        return self._aggregate_detectors

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        detector_summary = ["## Detected Events",
                           "The new events generated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        detector_list = [detector.AsMarkdown for detector in self.AggregateDetectors.values()] + [detector.AsMarkdown for detector in self.IteratedDetectors.values()]
        detector_list = detector_list if len(detector_list) > 0 else ["None"]
        return "  \n\n".join(detector_summary + detector_list)

    @property
    def AsDict(self) -> Dict[str, Dict[str, DetectorConfig]]:
        ret_val = {
            "iterated" : self.IteratedDetectors,
            "aggregate" : self.AggregateDetectors
        }
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DetectorMapConfig":
        """Function to generate a DetectorMapConfig from a JSON-formatted dictionary.

        Expected structure is:
        {
            "iterated" : {
                "DetectorName1": {
                    "type": "DetectorClass",
                    "enabled": true,
                    "description": "Info about the iterated detector; the iterated is generally optional.",
                },
                "DetectorName2": {
                    ...
                },
                ...
            },
            "aggregate" : {
                "DetectorName1": {
                    "type": "DetectorClass",
                    "enabled": true,
                    "description": "Info about the aggregate (session-level) detector.",
                },
                "DetectorName2": {
                    ...
                },
                ...
            }
        }

        :param name: The name associated with the feature, typically just "detectors"
        :type name: str
        :param unparsed_elements: The dictionary containing the contents for the `DetectorMapConfig`
        :type unparsed_elements: Map
        :param key_overrides: (_Ignored_) A dictionary of overrides for keys to look for, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :return: An DetectorMapConfig with data from the given `unparsed_elements`
        :rtype: DetectorMapConfig
        """
        return DetectorMapConfig(name=name,
                                 percount_detectors=None, aggregate_detectors=None,
                                 other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "DetectorMapConfig":
        return DetectorMapConfig(
            name="DefaultDetectorMapConfig",
            percount_detectors=cls._DEFAULT_ITERATED_DETECTORS,
            aggregate_detectors=cls._DEFAULT_AGGREGATE_DETECTORS,
            other_elements={}
        )

    # TODO : Bring back AsMarkdownRow for markdown table approach to representing game schemas.
    # @property
    # def AsMarkdownRow(self) -> str:
    #     ret_val : str = f"| {self.Name} | {self.ElementType} | {self.Description} |"
    #     if self.Details is not None:
    #         detail_markdowns = [f"**{name}** : {desc}" for name,desc in self.Details.items()]
    #         ret_val += ', '.join(detail_markdowns)
    #     ret_val += " |"
    #     return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseIteratedDetectors(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]

        percounts = DetectorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["iterated", "per_count", "percount"],
            to_type=dict,
            default_value=DetectorMapConfig._DEFAULT_ITERATED_DETECTORS,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(percounts, dict):
            ret_val = { key : DetectorConfig.FromDict(name=key, unparsed_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Iterated detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateDetectors(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]

        aggregates = DetectorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["aggregate"],
            to_type=dict,
            default_value=DetectorMapConfig._DEFAULT_AGGREGATE_DETECTORS,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(aggregates, dict):
            ret_val = {key : DetectorConfig.FromDict(name=key, unparsed_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Aggregate detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
