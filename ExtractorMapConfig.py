# import standard libraries
import logging
from typing import Dict, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.generators.AggregateConfig import AggregateConfig
from ogd.common.configs.generators.IteratedConfig import IteratedConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import conversions, Map

class ExtractorMapConfig(Config):
    """
    Dumb struct to contain the specification and config of a set of features for a game.

    TODO : Rename to DetectorMapConfig
    """

    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_LEGACY_EXTORS = {}
    _DEFAULT_ITERATED_EXTORS = {}
    _DEFAULT_AGGREGATE_EXTORS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, legacy_mode:Optional[bool],        legacy_perlevel_extractors:Optional[Dict[str, IteratedConfig]],
                 iterated_extractors:Optional[Dict[str, IteratedConfig]], aggregate_extractors:Optional[Dict[str, AggregateConfig]],
                 other_elements:Optional[Map]=None):
        """Constructor for the `ExtractorMapConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "iterated" : {
                "ExtractorName1": {
                    "enabled": true,
                    "type": "ExtractorClass",
                    "count": "level_range",
                    "prefix": "lvl",
                    "description": "Info about the per-count extractor; the per-count is generally optional.",
                    "return_type": "str"
                },
                "ExtractorName2": {
                    ...
                },
                ...
            },
            "aggregate" : {
                "ExtractorName1": {
                    "enabled": true,
                    "type": "ExtractorClass",
                    "description": "Info about the aggregate (session-level) extractor.",
                    "return_type": "str"
                },
                "ExtractorName2": {
                    ...
                },
                ...
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param legacy_mode: _description_
        :type legacy_mode: Optional[bool]
        :param legacy_perlevel_feats: _description_
        :type legacy_perlevel_feats: Optional[Dict[str, IteratedConfig]]
        :param percount_feats: _description_
        :type percount_feats: Optional[Dict[str, IteratedConfig]]
        :param aggregate_feats: _description_
        :type aggregate_feats: Optional[Dict[str, AggregateConfig]]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._legacy_mode           : bool                       = legacy_mode           or self._parseLegacyMode(unparsed_elements=unparsed_elements)
        self._legacy_extractors     : Dict[str, IteratedConfig]  = legacy_perlevel_extractors or self._parsePerLevelExtractors(unparsed_elements=unparsed_elements)
        self._iterated_extractors   : Dict[str, IteratedConfig]  = iterated_extractors        or self._parseIteratedExtractors(unparsed_elements=unparsed_elements)
        self._aggregate_feats       : Dict[str, AggregateConfig] = aggregate_extractors       or self._parseAggregateExtractors(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def LegacyMode(self) -> bool:
        return self._legacy_mode

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str, IteratedConfig]:
        return self._legacy_extractors

    @property
    def IteratedExtractors(self) -> Dict[str, IteratedConfig]:
        return self._iterated_extractors
    @property
    def PerCountFeatures(self) -> Dict[str, IteratedConfig]:
        """Legacy alias for IteratedExtractors

        :return: _description_
        :rtype: Dict[str, IteratedConfig]
        """
        return self.IteratedExtractors

    @property
    def AggregateExtractors(self) -> Dict[str, AggregateConfig]:
        return self._aggregate_feats

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_feats.values()] + [feature.AsMarkdown for feature in self._iterated_extractors.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        return "  \n\n".join(feature_summary + feature_list)

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "ExtractorMapConfig":
        """Function to generate a DetectorMapConfig from a JSON-formatted dictionary.

        Expected structure is:
        {
            "legacy" : {
                "enabled" : false,
                "return_type" : "Not really sure if this is used or not, in any case, legacy element is optional and not expected to occur in general."
            }
            "perlevel" : {
                "example" : {
                    "type":"ExampleDetectorClass",
                    "enabled":true,
                    "description":"Info about the per-level detector; the perlevel is a legacy sub-dict and should not be included."
                }
            },
            "iterated" : {
                "example" : {
                    "type":"ExampleDetectorClass",
                    "enabled":true,
                    "description":"Info about the per-count detector; the per-count is generally optional."
                }
            },
            "aggregate" : {
                "example" : {
                    "type":"ExampleDetectorClass",
                    "enabled":true,
                    "description":"Info about the aggregate (session-level) detector."
                }
            },
        }

        :param name: The name of the detector map configuration.
        :type name: str
        :param unparsed_elements: Elements of the source dictionary that have not yet been parsed, and will be used to construct the config.
        :type unparsed_elements: Map
        :return: A DetectorMapConfig based on the given collection of elements.
        :rtype: DetectorMapConfig
        """
        return ExtractorMapConfig(name=name, legacy_mode=None, legacy_perlevel_extractors=None,
                                iterated_extractors=None, aggregate_extractors=None,
                                other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "ExtractorMapConfig":
        return ExtractorMapConfig(
            name="DefaultExtractorMapConfig",
            legacy_mode=cls._DEFAULT_LEGACY_MODE,
            legacy_perlevel_extractors=cls._DEFAULT_LEGACY_EXTORS,
            iterated_extractors=cls._DEFAULT_ITERATED_EXTORS,
            aggregate_extractors=cls._DEFAULT_AGGREGATE_EXTORS,
            other_elements={}
        )

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
    def _parseLegacyMode(unparsed_elements:Map) -> bool:
        """_summary_

        TODO : Get the 'legacy' dict with the conversions function, to take advantage of debug prints.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: bool
        """
        ret_val : bool = False

        legacy_element = unparsed_elements.get("legacy", None)
        if legacy_element:
            if isinstance(legacy_element, dict):
                ret_val = ExtractorMapConfig.ParseElement(
                    unparsed_elements=legacy_element,
                    valid_keys=["enabled"],
                    to_type=bool,
                    default_value=ExtractorMapConfig._DEFAULT_LEGACY_MODE,
                )
            else:
                ret_val = conversions.ConvertToType(value=legacy_element, to_type=bool, name="legacy_element")
                Logger.Log(f"LegacyMode element was not a dict, defaulting to bool(legacy_element) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerLevelExtractors(unparsed_elements:Map) -> Dict[str, IteratedConfig]:
        ret_val : Dict[str, IteratedConfig]

        perlevels = ExtractorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["perlevel", "per_level"],
            to_type=dict,
            default_value=ExtractorMapConfig._DEFAULT_LEGACY_EXTORS
        )
        if isinstance(perlevels, dict):
            ret_val = { key : IteratedConfig.FromDict(name=key, unparsed_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log("Per-level features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseIteratedExtractors(unparsed_elements:Map) -> Dict[str, IteratedConfig]:
        ret_val : Dict[str, IteratedConfig]

        percounts = ExtractorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["iterated", "per_count", "percount"],
            to_type=dict,
            default_value=ExtractorMapConfig._DEFAULT_ITERATED_EXTORS
        )
        if isinstance(percounts, dict):
            ret_val = { key : IteratedConfig.FromDict(name=key, unparsed_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateExtractors(unparsed_elements:Map) -> Dict[str, AggregateConfig]:
        ret_val : Dict[str, AggregateConfig]

        aggregates = ExtractorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["aggregate"],
            to_type=dict,
            default_value=ExtractorMapConfig._DEFAULT_AGGREGATE_EXTORS
        )
        if isinstance(aggregates, dict):
            ret_val = {key : AggregateConfig.FromDict(name=key, unparsed_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Aggregate features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
