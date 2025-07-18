# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.generators.AggregateConfig import AggregateConfig
from ogd.common.configs.generators.PerCountConfig import PerCountConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import conversions, Map

class FeatureMapConfig(Config):
    """
    Dumb struct to contain the specification and config of a set of features for a game.

    TODO : Rename to DetectorMapConfig
    """

    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_LEGACY_FEATS = {}
    _DEFAULT_PERCOUNT_FEATS = {}
    _DEFAULT_AGGREGATE_FEATS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, legacy_mode: bool,        legacy_perlevel_feats:Dict[str, PerCountConfig],
                 percount_feats:Dict[str, PerCountConfig], aggregate_feats:Dict[str, AggregateConfig],
                 other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._legacy_mode           : bool                       = legacy_mode           or self._parseLegacyMode(unparsed_elements=unparsed_elements)
        self._legacy_perlevel_feats : Dict[str, PerCountConfig]  = legacy_perlevel_feats or self._parsePerLevelFeatures(unparsed_elements=unparsed_elements)
        self._percount_feats        : Dict[str, PerCountConfig]  = percount_feats        or self._parsePerCountFeatures(unparsed_elements=unparsed_elements)
        self._aggregate_feats       : Dict[str, AggregateConfig] = aggregate_feats       or self._parseAggregateFeatures(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def LegacyMode(self) -> bool:
        return self._legacy_mode

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str, PerCountConfig]:
        return self._legacy_perlevel_feats

    @property
    def PerCountFeatures(self) -> Dict[str, PerCountConfig]:
        return self._percount_feats

    @property
    def AggregateFeatures(self) -> Dict[str, AggregateConfig]:
        return self._aggregate_feats

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_feats.values()] + [feature.AsMarkdown for feature in self._percount_feats.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        return "  \n\n".join(feature_summary + feature_list)

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "FeatureMapConfig":
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
            "per_count" : {
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
        _legacy_mode           : bool                       = cls._parseLegacyMode(unparsed_elements=unparsed_elements)
        _legacy_perlevel_feats : Dict[str, PerCountConfig]  = cls._parsePerLevelFeatures(unparsed_elements=unparsed_elements)
        _percount_feats        : Dict[str, PerCountConfig]  = cls._parsePerCountFeatures(unparsed_elements=unparsed_elements)
        _aggregate_feats       : Dict[str, AggregateConfig] = cls._parseAggregateFeatures(unparsed_elements=unparsed_elements)

        _used = {"legacy", "perlevel", "per_count", "aggregate"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return FeatureMapConfig(name=name, legacy_mode=_legacy_mode, legacy_perlevel_feats=_legacy_perlevel_feats,
                                percount_feats=_percount_feats, aggregate_feats=_aggregate_feats,
                                other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "FeatureMapConfig":
        return FeatureMapConfig(
            name="DefaultFeatureMapConfig",
            legacy_mode=cls._DEFAULT_LEGACY_MODE,
            legacy_perlevel_feats=cls._DEFAULT_LEGACY_FEATS,
            percount_feats=cls._DEFAULT_PERCOUNT_FEATS,
            aggregate_feats=cls._DEFAULT_AGGREGATE_FEATS,
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
                ret_val = FeatureMapConfig.ParseElement(
                    unparsed_elements=legacy_element,
                    valid_keys=["enabled"],
                    to_type=bool,
                    default_value=FeatureMapConfig._DEFAULT_LEGACY_MODE,
                )
            else:
                ret_val = conversions.ConvertToType(value=legacy_element, to_type=bool, name="legacy_element")
                Logger.Log(f"LegacyMode element was not a dict, defaulting to bool(legacy_element) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerLevelFeatures(unparsed_elements:Map) -> Dict[str, PerCountConfig]:
        ret_val : Dict[str, PerCountConfig]

        perlevels = FeatureMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["perlevel", "per_level"],
            to_type=dict,
            default_value=FeatureMapConfig._DEFAULT_LEGACY_FEATS
        )
        if isinstance(perlevels, dict):
            ret_val = { key : PerCountConfig.FromDict(name=key, unparsed_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log("Per-level features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerCountFeatures(unparsed_elements:Map) -> Dict[str, PerCountConfig]:
        ret_val : Dict[str, PerCountConfig]

        percounts = FeatureMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["per_count", "percount"],
            to_type=dict,
            default_value=FeatureMapConfig._DEFAULT_PERCOUNT_FEATS
        )
        if isinstance(percounts, dict):
            ret_val = { key : PerCountConfig.FromDict(name=key, unparsed_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateFeatures(unparsed_elements:Map) -> Dict[str, AggregateConfig]:
        ret_val : Dict[str, AggregateConfig]

        aggregates = FeatureMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["aggregate"],
            to_type=dict,
            default_value=FeatureMapConfig._DEFAULT_AGGREGATE_FEATS
        )
        if isinstance(aggregates, dict):
            ret_val = {key : AggregateConfig.FromDict(name=key, unparsed_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Aggregate features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
