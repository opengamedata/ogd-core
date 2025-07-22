# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.generators.DetectorMapConfig import DetectorMapConfig
from ogd.common.configs.generators.ExtractorMapConfig import ExtractorMapConfig
from ogd.common.configs.generators.AggregateConfig import AggregateConfig
from ogd.common.configs.generators.DetectorConfig import DetectorConfig
from ogd.common.configs.generators.IteratedConfig import IteratedConfig
from ogd.common.configs.generators.ExtractorConfig import ExtractorConfig
from ogd.common.models.enums.IterationMode import IterationMode
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class GeneratorCollectionConfig
class GeneratorCollectionConfig(Config):
    """A fairly simple class that reads a JSON config with information on the features we want to extract
    for a given game.
    The class includes several functions for easy access to the various parts of
    this schema data.
    """
    _DEFAULT_DET_AGGREGATES = {}
    _DEFAULT_DET_PERCOUNTS = {}
    _DEFAULT_DETECTOR_MAP = DetectorMapConfig(name="DefaultDetectorMap", percount_detectors=_DEFAULT_DET_PERCOUNTS, aggregate_detectors=_DEFAULT_DET_AGGREGATES, other_elements={})
    _DEFAULT_FEAT_AGGREGATES = {}
    _DEFAULT_FEAT_PERCOUNTS = {}
    _DEFAULT_LEGACY_PERCOUNTS = {}
    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_FEATURE_MAP = ExtractorMapConfig(name="DefaultFeatureMap", legacy_mode=_DEFAULT_LEGACY_MODE, legacy_perlevel_feats=_DEFAULT_LEGACY_PERCOUNTS,
                                            percount_feats=_DEFAULT_FEAT_PERCOUNTS, aggregate_feats=_DEFAULT_FEAT_AGGREGATES, other_elements={})
    _DEFAULT_LEVEL_RANGE = None
    _DEFAULT_OTHER_RANGES = {}
    _DEFAULT_GAME_FOLDER = Path("./") / "ogd" / "games"
    @property
    def _DEFAULT_LEGACY_CONFIG(self) -> AggregateConfig:
        return AggregateConfig.FromDict("legacy", {"type":"legacy", "return_type":None, "description":"", "enabled":True})

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:str,
                 detector_map:Optional[DetectorMapConfig], extractor_map:Optional[ExtractorMapConfig],
                 subunit_range:Optional[range], other_ranges:Dict[str, range],
                 other_elements:Optional[Map]=None):
        """Constructor for the GeneratorCollectionConfig class.
        
        If optional params are not given, data is searched for in `other_elements`.

        `level_range` is explicitly searched for; any other elements with a suffix of `_range` are placed into the `OtherRanges` property.

        Expected format:

        ```
        {
            "level_range": {
                "min": 0,
                "max": 25
            },
            "questionnaire_range": {
                "min": 0,
                "max": 10
            },
            "detectors" : {
                "per_count" : {
                    "DetectorName1": {
                        ...
                    },
                    ...
                },
                "aggregate" : {
                    "DetectorName1": {
                        ...
                    },
                    ...
                }
            },
            "extractors" : {
                "per_count" : {
                    "ExtractorName1": {
                        ...
                    },
                    ...
                },
                "aggregate" : {
                    "ExtractorName1": {
                        ...
                    },
                    ...
                }
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: str
        :param detector_map: _description_
        :type detector_map: DetectorMapConfig
        :param extractor_map: _description_
        :type extractor_map: ExtractorMapConfig
        :param subunit_range: _description_
        :type subunit_range: Optional[range]
        :param other_ranges: _description_
        :type other_ranges: Dict[str, range]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

    # 1. define instance vars
        self._game_id            : str               = game_id or name
        self._detector_map       : DetectorMapConfig = detector_map  or self._parseDetectorMap(unparsed_elements=unparsed_elements)
        self._extractor_map      : ExtractorMapConfig  = extractor_map or self._parseFeatureMap(unparsed_elements=unparsed_elements)
        self._subunit_range      : Optional[range]   = subunit_range
        self._other_ranges       : Dict[str, range]  = other_ranges

        super().__init__(name=name, other_elements=unparsed_elements)

    # def __getitem__(self, key) -> Any:
    #     return _schema[key] if _schema is not None else None

    @property
    def GameName(self) -> str:
        """Property for the name of the game configured by this schema
        """
        return self._game_id

    @property
    def Detectors(self) -> DetectorMapConfig:
        """Property for the dictionary of categorized detectors to extract.
        """
        return self._detector_map

    @property
    def DetectorNames(self) -> List[str]:
        """Property for the compiled list of all detector names.
        """
        ret_val : List[str] = []

        ret_val = [detector.Name for detector in self.Detectors.AggregateDetectors.values()] \
                + [detector.Name for detector in self.Detectors.PerCountDetectors.values()]

        return ret_val

    @property
    def PerCountDetectors(self) -> Dict[str, DetectorConfig]:
        """Property for the dictionary of per-custom-count detectors.
        """
        return self.Detectors.PerCountDetectors

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorConfig]:
        """Property for the dictionary of aggregate detectors.
        """
        return self.Detectors.AggregateDetectors

    @property
    def Extractors(self) -> ExtractorMapConfig:
        """Property for the dictionary of categorized features to extract.
        """
        return self._extractor_map
    @property
    def Features(self) -> ExtractorMapConfig:
        """Alias for Extractors property

        :return: _description_
        :rtype: ExtractorMapConfig
        """
        return self.Extractors

    @property
    def FeatureNames(self) -> List[str]:
        """Property for the compiled list of all feature names.
        """
        ret_val : List[str] = []
        ret_val = [extractor.Name for extractor in self.Extractors.AggregateFeatures.values()] \
                + [extractor.Name for extractor in self.Extractors.PerCountFeatures.values()] \
                + [extractor.Name for extractor in self.Extractors.LegacyPerLevelFeatures.values()]
        return ret_val

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str,IteratedConfig]:
        """Property for the dictionary of legacy per-level features
        """
        return self.Extractors.LegacyPerLevelFeatures

    @property
    def PerCountFeatures(self) -> Dict[str,IteratedConfig]:
        """Property for the dictionary of per-custom-count features.
        """
        return self.Extractors.PerCountFeatures

    @property
    def AggregateFeatures(self) -> Dict[str,AggregateConfig]:
        """Property for the dictionary of aggregate features.
        """
        return self.Extractors.AggregateFeatures

    @property
    def SubunitRange(self) -> Optional[range]:
        """Property for the range of levels or other game sub-units that are the primary per-count property for the given game.
        """
        ret_val = None
        if self._subunit_range:
            ret_val = self._subunit_range
        else:
            Logger.Log("Could not get game sub-unit (or per-level) feature range, there was no range configured!", logging.ERROR)
        return ret_val
    @property
    def LevelRange(self) -> Optional[range]:
        """Alias for the primary game sub-unit range.
        """
        return self.SubunitRange

    @property
    def OtherRanges(self) -> Dict[str, range]:
        return self._other_ranges

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        # Set up list of detectors
        detector_summary = ["## Detected Events",
                            "The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run."
                           ]
        detector_list = [detector.AsMarkdown for detector in self.Detectors.AggregateDetectors.values()] \
                      + [detector.AsMarkdown for detector in self.Detectors.PerCountDetectors.values()]
        detector_list = detector_list if len(detector_list) > 0 else ["None"]
        # Set up list of features
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self.Features.AggregateFeatures.values()] \
                     + [feature.AsMarkdown for feature in self.Features.PerCountFeatures.values()] \

        feature_list = feature_list + [feature.AsMarkdown for feature in self.Features.LegacyPerLevelFeatures.values()] if self.Features.LegacyMode else feature_list
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        # Include other elements
        other_summary = [
            "## Other Elements",
            "Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors."
        ]
        other_element_list = [ f"{key} : {self._other_elements[key]}" for key in self._other_elements.keys()]
        level_range_summary = [
            "### Sub-unit/Level Range",
            "The range for the primary sub-unit (e.g. level) of gameplay."
        ] if self.SubunitRange else []
        level_range_list = [ str(self.SubunitRange) ] if self.SubunitRange else []
        other_range_summary = [
            "### Other Ranges",
            "Extra ranges specified in the game's schema, which may be referenced by event/feature processors."
        ]
        other_range_list = [ f"{key} : {self.OtherRanges[key]}" for key in self.OtherRanges ]

        ret_val = "  \n\n".join(detector_summary + detector_list
                              + feature_summary + feature_list
                              + other_summary + other_element_list
                              + level_range_summary + level_range_list
                              + other_range_summary + other_range_list)

        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "GeneratorCollectionConfig":
        """_summary_

        TODO : Need to have parse functions for all the variables, currently only have about half of them.
        In particular, we have all features theoretically under one parsed 'map' below, which is weird,
        since we clearly have vars for each kind of feature separately here.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :raises ValueError: _description_
        :raises ValueError: _description_
        :return: _description_
        :rtype: GeneratorCollectionConfig
        """
    # 1. define local vars
        _game_id      : str              = name
        _level_range  : Optional[range]  = cls._parseLevelRange(unparsed_elements=unparsed_elements)
        _other_ranges : Dict[str, range] = cls._parseOtherRanges(unparsed_elements=unparsed_elements)

        return GeneratorCollectionConfig(name=name, game_id=_game_id,
                          detector_map=None, extractor_map=None,
                          subunit_range=_level_range, other_ranges=_other_ranges,
                          other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "GeneratorCollectionConfig":
        return GeneratorCollectionConfig(
            name="DefaultGeneratorCollectionConfig",
            game_id="DEFAULT_GAME",
            detector_map=cls._DEFAULT_DETECTOR_MAP,
            extractor_map=cls._DEFAULT_FEATURE_MAP,
            subunit_range=cls._DEFAULT_LEVEL_RANGE,
            other_ranges=cls._DEFAULT_OTHER_RANGES,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Optional[Path] = None, search_templates:bool=True) -> "GeneratorCollectionConfig":
        """Function to get a GeneratorCollectionConfig from a file

        :param game_id: _description_
        :type game_id: str
        :param schema_path: _description_, defaults to None
        :type schema_path: Optional[Path], optional
        :param search_templates: _description_, defaults to True
        :type search_templates: bool, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: GeneratorCollectionConfig
        """
        ret_val : Config

        game_id = schema_name.split('.')[0] # the 'schema name' is meant to match the game ID. We do want to strip off any file types, so only take string up to first '.'
        schema_path = schema_path or cls._DEFAULT_GAME_FOLDER / game_id / "schemas"
        ret_val = cls._fromFile(schema_name=game_id, schema_path=schema_path, search_templates=search_templates)
        if isinstance(ret_val, GeneratorCollectionConfig):
            return ret_val
        else:
            raise ValueError("The result of the class _fromFile function was not a GeneratorCollectionConfig!")

    # *** PUBLIC METHODS ***

    def GetCountRange(self, count:Any) -> range:
        """Function to get a predefined range for per-count features, or to generate a range up to given count.
        Typically, this would be used to retrieve the `level_range` for the game.
        However, any other ranges defined in the game's schema can be retrieved here, or a custom range object generated (using `int(count)`).

        :param count: The name of a range defined in the game schema, or an object that can be int-ified to define a custom range.
        :type count: Any
        :return: The range object with name given by `count`, or a new range from 0 to (but not including) `int(count)`
        :rtype: range
        """
        ret_val :range

        if isinstance(count, str):
            if count.lower() == "level_range" and self.LevelRange:
                ret_val = self.LevelRange
            elif count in self.OtherRanges.keys():
                ret_val = self.OtherRanges.get(count, range(0))
            else:
                other_range : Dict[str, int] = self.NonStandardElements.get(count, {'min':0, 'max':-1})
                ret_val = range(other_range['min'], other_range['max']+1)
        else:
            ret_val = range(0,int(count))

        return ret_val

    def DetectorEnabled(self, detector_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        """Function to check if detector with given base name and iteration mode (aggregate or percount) is enabled for given extract mode.

        :param detector_name: The base name of the detector class to check
        :type detector_name: str
        :param iter_mode: The "iteration" mode of the detector class (aggregate or per-count)
        :type iter_mode: IterationMode
        :param extract_mode: The extraction mode of the detector (which... should always be detector?)
        :type extract_mode: ExtractionMode
        :raises ValueError: Error indicating an unrecognized iteration mode was given.
        :return: True if the given detector is enabled in the schema, otherwise False
        :rtype: bool
        """
        ret_val : bool

        _detector_schema : Optional[DetectorConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _detector_schema = self.Detectors.AggregateDetectors.get(detector_name)
            case IterationMode.PERCOUNT:
                _detector_schema = self.Detectors.PerCountDetectors.get(detector_name)
            case _:
                raise ValueError(f"In GeneratorCollectionConfig, DetectorEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _detector_schema is not None:
            ret_val = extract_mode in _detector_schema.Enabled
        else:
            Logger.Log(f"Could not find detector {detector_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def FeatureEnabled(self, feature_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        if self.Extractors.LegacyMode:
            return feature_name == "legacy"
        ret_val : bool

        _feature_schema : Optional[ExtractorConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _feature_schema = self.AggregateFeatures.get(feature_name)
            case IterationMode.PERCOUNT:
                _feature_schema = self.PerCountFeatures.get(feature_name)
            case _:
                raise ValueError(f"In GeneratorCollectionConfig, FeatureEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _feature_schema is not None:
            ret_val = extract_mode in _feature_schema.Enabled
        else:
            Logger.Log(f"Could not find feature {feature_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def EnabledDetectors(self, iter_modes:Set[IterationMode], extract_modes:Set[ExtractionMode]=set()) -> Dict[str, DetectorConfig]:
        if self.Extractors.LegacyMode:
            return {}
        ret_val : Dict[str, DetectorConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateDetectors.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountDetectors.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    def EnabledFeatures(self, iter_modes:Set[IterationMode]={IterationMode.AGGREGATE, IterationMode.PERCOUNT}, extract_modes:Set[ExtractionMode]=set()) -> Dict[str, ExtractorConfig]:
        if self.Extractors.LegacyMode:
            return {"legacy" : self._DEFAULT_LEGACY_CONFIG} if IterationMode.AGGREGATE in iter_modes else {}
        ret_val : Dict[str, ExtractorConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateFeatures.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountFeatures.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDetectorMap(unparsed_elements:Map) -> DetectorMapConfig:
        ret_val : DetectorMapConfig

        detector_map = GeneratorCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["detectors"],
            to_type=dict,
            default_value=GeneratorCollectionConfig._DEFAULT_DETECTOR_MAP,
            remove_target=True
        )
        ret_val = DetectorMapConfig.FromDict(name="DetectorMap", unparsed_elements=detector_map)

        return ret_val

    @staticmethod
    def _parseFeatureMap(unparsed_elements:Map) -> ExtractorMapConfig:
        ret_val : ExtractorMapConfig

        feature_map = GeneratorCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["features"],
            to_type=dict,
            default_value=GeneratorCollectionConfig._DEFAULT_FEATURE_MAP,
            remove_target=True
        )
        ret_val = ExtractorMapConfig.FromDict(name="FeatureMap", unparsed_elements=feature_map)
        return ret_val

    @staticmethod
    def _parseLevelRange(unparsed_elements:Map) -> Optional[range]:
        ret_val : Optional[range] = GeneratorCollectionConfig._DEFAULT_LEVEL_RANGE

        level_range = GeneratorCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["level_range"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )

        if isinstance(level_range, dict):
            _min = level_range.get("min", 0)
            _max = level_range.get("max", None)
            if _max:
                ret_val = range(_min, _max)
            else:
                Logger.Log(f"level_range had no max element defined, defaulting to {ret_val}.", logging.WARN)
        elif level_range == None:
            pass
        else:
            Logger.Log(f"level_range was unexpected type {type(level_range)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseOtherRanges(unparsed_elements:Map) -> Dict[str, range]:
        return {key : range(val.get('min', 0), val.get('max', 1)) for key,val in unparsed_elements.items() if key.endswith("_range")}

    # *** PRIVATE METHODS ***
