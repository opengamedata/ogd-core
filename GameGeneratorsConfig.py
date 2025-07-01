# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.games.DetectorMapConfig import DetectorMapConfig
from ogd.common.configs.games.FeatureMapConfig import FeatureMapConfig
from ogd.common.configs.games.AggregateConfig import AggregateConfig
from ogd.common.configs.games.DetectorConfig import DetectorConfig
from ogd.common.configs.games.DetectorMapConfig import DetectorMapConfig
from ogd.common.configs.games.PerCountConfig import PerCountConfig
from ogd.common.configs.games.FeatureConfig import FeatureConfig
from ogd.common.models.enums.IterationMode import IterationMode
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class GameSchema
class GameGeneratorsConfig(Config):
    """A fairly simple class that reads a JSON config with information on the features we want to extract
    for a given game.
    The class includes several functions for easy access to the various parts of
    this schema data.

    TODO : Use DetectorMapConfig and FeatureMapConfig instead of just dicts... I think. Depending how these all work together.
    TODO : make parser functions for config and versions, so we can do ElementFromDict for them as well.
    TODO : In general, there's a metric fuckload of parsing functions and other things missing from standard way of doing this, class as a whole needs work.
    """
    _DEFAULT_DETECTOR_MAP = {'perlevel':{}, 'per_count':{}, 'aggregate':{}}
    _DEFAULT_AGGREGATES = {}
    _DEFAULT_PERCOUNTS = {}
    _DEFAULT_LEGACY_PERCOUNTS = {}
    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_FEATURE_MAP = FeatureMapConfig(name="DefaultFeatureMap", legacy_mode=_DEFAULT_LEGACY_MODE, legacy_perlevel_feats=_DEFAULT_LEGACY_PERCOUNTS,
                                            percount_feats=_DEFAULT_PERCOUNTS, aggregate_feats=_DEFAULT_AGGREGATES, other_elements={})
    _DEFAULT_CONFIG = {}
    _DEFAULT_MIN_LEVEL = None
    _DEFAULT_MAX_LEVEL = None
    _DEFAULT_OTHER_RANGES = {}
    _DEFAULT_VERSIONS = None
    _DEFAULT_GAME_FOLDER = Path("./") / "ogd" / "games"
    @property
    def _DEFAULT_LEGACY_CONFIG(self) -> AggregateConfig:
        return AggregateConfig.FromDict("legacy", {"type":"legacy", "return_type":None, "description":"", "enabled":True})

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:str, 
                 detector_map:DetectorMapConfig,
                 extractor_map:FeatureMapConfig,
                 config:Map, min_level:Optional[int], max_level:Optional[int], other_ranges:Dict[str, range],
                 other_elements:Optional[Map]=None):
        """Constructor for the GameSchema class.
        Given a path and filename, it loads the data from a JSON schema,
        storing the full schema into a private variable, and compiling a list of
        all features to be extracted.

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: str
        :param detector_map: _description_
        :type detector_map: DetectorMapConfig
        :param extractor_map: _description_
        :type extractor_map: FeatureMapConfig
        :param config: _description_
        :type config: Map
        :param min_level: _description_
        :type min_level: Optional[int]
        :param max_level: _description_
        :type max_level: Optional[int]
        :param other_ranges: _description_
        :type other_ranges: Dict[str, range]
        :param other_elements: _description_
        :type other_elements: Dict[str, Any]
        :return: The new instance of GameSchema
        :rtype: GameSchema
        """
        unparsed_elements = other_elements or {}

    # 1. define instance vars
        self._game_id                : str               = game_id
        self._detector_map           : DetectorMapConfig = detector_map
        self._extractor_map          : FeatureMapConfig  = extractor_map
        self._config                 : Map               = config
        self._level_range            : Optional[range]   = range(min_level, max_level+1) if min_level is not None and max_level is not None else None
        # self._min_level              : Optional[int]   = min_level
        # self._max_level              : Optional[int]   = max_level
        self._other_ranges           : Dict[str, range]  = other_ranges

        super().__init__(name=self._game_id, other_elements=other_elements)

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
        for _category in self.Detectors.values():
            ret_val += [detector.Name for detector in _category.values()]
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
    def Extractors(self) -> FeatureMapConfig:
        """Property for the dictionary of categorized features to extract.
        """
        return self._extractor_map
    @property
    def Features(self) -> FeatureMapConfig:
        """Alias for Extractors property

        :return: _description_
        :rtype: FeatureMapConfig
        """
        return self.Extractors

    @property
    def FeatureNames(self) -> List[str]:
        """Property for the compiled list of all feature names.
        """
        ret_val : List[str] = []
        for _category in self.Features.values():
            ret_val += [feature.Name for feature in _category.values()]
        return ret_val

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str,PerCountConfig]:
        """Property for the dictionary of legacy per-level features
        """
        return self.Extractors.LegacyPerLevelFeatures

    @property
    def PerCountFeatures(self) -> Dict[str,PerCountConfig]:
        """Property for the dictionary of per-custom-count features.
        """
        return self.Extractors.PerCountFeatures

    @property
    def AggregateFeatures(self) -> Dict[str,AggregateConfig]:
        """Property for the dictionary of aggregate features.
        """
        return self.Extractors.AggregateFeatures

    @property
    def LevelRange(self) -> range:
        """Property for the range of levels defined in the schema if any.
        """
        ret_val = range(0)
        if self._min_level is not None and self._max_level is not None:
            # for i in range(self._min_level, self._max_level+1):
            ret_val = range(self._min_level, self._max_level+1)
        else:
            Logger.Log(f"Could not generate per-level features, min_level={self._min_level} and max_level={self._max_level}", logging.ERROR)
        return ret_val

    @property
    def OtherRanges(self) -> Dict[str, range]:
        return self._other_ranges

    @property
    def Config(self) -> Dict[str, Any]:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        event_summary = ["## Logged Events",
                         "The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game."
                        ]
        enum_list     = ["### Enums",
                         "\n".join(
                             ["| **Name** | **Values** |",
                             "| ---      | ---        |"]
                         + [f"| {name} | {val_list} |" for name,val_list in self.EnumDefs.items()]
                        )]
        game_state_list = ["### Game State",
                           "\n".join(
                               ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                               "| ---      | ---      | ---             | ---         |"]
                           + [elem.AsMarkdownRow for elem in self.GameState.values()]
                          )]
        user_data_list = ["### User Data",
                          "\n".join(
                              ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                              "| ---      | ---      | ---             | ---         |"]
                          + [elem.AsMarkdownRow for elem in self.UserData.values()]
                         )]
        # Set up list of events
        event_list = [event.AsMarkdownTable for event in self.Events] if len(self.Events) > 0 else ["None"]
        # Set up list of detectors
        detector_summary = ["## Detected Events",
                            "The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run."
                           ]
        detector_list = []
        for detect_kind in ["perlevel", "per_count", "aggregate"]:
            if detect_kind in self._detector_map:
                detector_list += [detector.AsMarkdown for detector in self.Detectors[detect_kind].values()]
        detector_list = detector_list if len(detector_list) > 0 else ["None"]
        # Set up list of features
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_feats.values()] + [feature.AsMarkdown for feature in self._percount_feats.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        # Include other elements
        other_summary = ["## Other Elements",
                         "Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_element_list = [ f"{key} : {self._other_elements[key]}" for key in self._other_elements.keys()]
        other_range_summary = ["### Other Ranges",
                         "Extra ranges specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_range_list = [ f"{key} : {self.OtherRanges[key]}" for key in self.OtherRanges ]

        ret_val = "  \n\n".join(event_summary
                              + enum_list + game_state_list + user_data_list + event_list
                              + detector_summary + detector_list
                              + feature_summary + feature_list
                              + other_summary + other_element_list
                              + other_range_summary + other_range_list)

        return ret_val

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "GameSchema":
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
        :rtype: GameSchema
        """
    # 1. define local vars
        _game_id                : str                                  = name
        _enum_defs              : Dict[str, List[str]]
        _game_state             : Dict[str, Any]
        _user_data              : Dict[str, Any]
        _event_list             : List[EventSchema]
        _detector_map           : Dict[str, Dict[str, DetectorConfig]]
        _aggregate_feats        : Dict[str, AggregateConfig] = {}
        _percount_feats         : Dict[str, PerCountConfig]  = {}
        _legacy_perlevel_feats  : Dict[str, PerCountConfig]  = {}
        _legacy_mode            : bool
        _config                 : Dict[str, Any]
        _min_level              : Optional[int]
        _max_level              : Optional[int]
        _other_ranges           : Dict[str, range]
        _supported_vers         : Optional[List[int]]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements   = {}
            Logger.Log(f"For {_game_id} GameSchema, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)

    # 2. set instance vars, starting with event data

        _enum_defs = cls._parseEnumDefs(unparsed_elements=unparsed_elements)
        _game_state = cls._parseGameState(unparsed_elements=unparsed_elements)
        _user_data = cls._parseUserData(unparsed_elements=unparsed_elements)

        _event_list = cls._parseEventList(unparsed_elements=unparsed_elements)

    # 3. Get detector information
        # TODO : investigate weird Dict[str, Dict[str, DetectorConfig]] type inference
        _detector_map = cls._parseDetectorMap(unparsed_elements=unparsed_elements).AsDict

    # 4. Get feature information
        _feat_map = cls._parseFeatureMap(unparsed_elements=unparsed_elements)
        _aggregate_feats.update(_feat_map.AggregateFeatures)
        _percount_feats.update(_feat_map.PerCountFeatures)
        _legacy_perlevel_feats.update(_feat_map.LegacyPerLevelFeatures)
        _legacy_mode = _feat_map.LegacyMode

    # 5. Get config, if any
        if "config" in unparsed_elements.keys():
            _config = unparsed_elements['config']
        else:
            Logger.Log(f"{_game_id} game schema does not define any config items.", logging.INFO)
        if "SUPPORTED_VERS" in _config:
            _supported_vers = _config['SUPPORTED_VERS']
        else:
            _supported_vers = None
            Logger.Log(f"{_game_id} game schema does not define supported versions, defaulting to support all versions.", logging.INFO)

    # 6. Get level range and other ranges, if any
        _min_level, _max_level = cls._parseLevelRange(unparsed_elements=unparsed_elements)

        _other_ranges = {key : range(val.get('min', 0), val.get('max', 1)) for key,val in unparsed_elements.items() if key.endswith("_range")}

    # 7. Collect any other, unexpected elements
        _used = {'enums', 'game_state', 'user_data', 'events', 'detectors', 'features', 'level_range', 'config'}.union(_other_ranges.keys())
        _leftovers = { key:val for key,val in unparsed_elements.items() if key not in _used }
        return GameSchema(name=name, game_id=_game_id, enum_defs=_enum_defs,
                          game_state=_game_state, user_data=_user_data,
                          event_list=_event_list, detector_map=_detector_map,
                          aggregate_feats=_aggregate_feats, percount_feats=_percount_feats,
                          legacy_perlevel_feats=_legacy_perlevel_feats, use_legacy_mode=_legacy_mode,
                          config=_config, min_level=_min_level, max_level=_max_level,
                          other_ranges=_other_ranges, supported_vers=_supported_vers,
                          other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "GameSchema":
        return GameSchema(
            name="DefaultGameSchema",
            game_id="DEFAULT_GAME",
            enum_defs=cls._DEFAULT_ENUMS,
            game_state=cls._DEFAULT_GAME_STATE,
            user_data=cls._DEFAULT_USER_DATA,
            event_list=cls._DEFAULT_EVENT_LIST,
            detector_map=cls._DEFAULT_DETECTOR_MAP,
            aggregate_feats=cls._DEFAULT_AGGREGATES,
            percount_feats=cls._DEFAULT_PERCOUNTS,
            legacy_perlevel_feats=cls._DEFAULT_LEGACY_PERCOUNTS,
            use_legacy_mode=cls._DEFAULT_LEGACY_MODE,
            config=cls._DEFAULT_CONFIG,
            min_level=cls._DEFAULT_MIN_LEVEL,
            max_level=cls._DEFAULT_MAX_LEVEL,
            other_ranges=cls._DEFAULT_OTHER_RANGES,
            supported_vers=cls._DEFAULT_VERSIONS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, game_id:str, schema_path:Optional[Path] = None, search_templates:bool=True) -> "GameSchema":
        """Function to get a GameSchema from a file

        :param game_id: _description_
        :type game_id: str
        :param schema_path: _description_, defaults to None
        :type schema_path: Optional[Path], optional
        :param search_templates: _description_, defaults to True
        :type search_templates: bool, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: GameSchema
        """
        ret_val : Schema
        # Give schema_path a default, don't think we can use game_id to construct it directly in the function header (so do it here if None)
        schema_path = schema_path or cls._DEFAULT_GAME_FOLDER / game_id / "schemas"
        ret_val = cls._fromFile(schema_name=game_id, schema_path=schema_path, search_templates=search_templates)
        if isinstance(ret_val, GameSchema):
            return ret_val
        else:
            raise ValueError("The result of the class _fromFile function was not a GameSchema!")

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
        if isinstance(count, str):
            if count.lower() == "level_range":
                count_range = self.LevelRange
            elif count in self.OtherRanges.keys():
                count_range = self.OtherRanges.get(count, range(0))
            else:
                other_range : Dict[str, int] = self.NonStandardElements.get(count, {'min':0, 'max':-1})
                count_range = range(other_range['min'], other_range['max']+1)
        else:
            count_range = range(0,int(count))
        return count_range

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
        if self._legacy_mode:
            return False
        ret_val : bool

        _detector_schema : Optional[DetectorConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _detector_schema = self.Detectors['aggregate'].get(detector_name)
            case IterationMode.PERCOUNT:
                _detector_schema = self.Detectors['per_count'].get(detector_name, self.Detectors['perlevel'].get(detector_name))
            case _:
                raise ValueError(f"In GameSchema, DetectorEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _detector_schema is not None:
            ret_val = extract_mode in _detector_schema.Enabled
        else:
            Logger.Log(f"Could not find detector {detector_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def FeatureEnabled(self, feature_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        if self._legacy_mode:
            return feature_name == "legacy"
        ret_val : bool

        _feature_schema : Optional[FeatureConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _feature_schema = self.AggregateFeatures.get(feature_name)
            case IterationMode.PERCOUNT:
                _feature_schema = self.PerCountFeatures.get(feature_name)
            case _:
                raise ValueError(f"In GameSchema, FeatureEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _feature_schema is not None:
            ret_val = extract_mode in _feature_schema.Enabled
        else:
            Logger.Log(f"Could not find feature {feature_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def EnabledDetectors(self, iter_modes:Set[IterationMode], extract_modes:Set[ExtractionMode]=set()) -> Dict[str, DetectorConfig]:
        if self._legacy_mode:
            return {}
        ret_val : Dict[str, DetectorConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateDetectors.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountDetectors.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    def EnabledFeatures(self, iter_modes:Set[IterationMode]={IterationMode.AGGREGATE, IterationMode.PERCOUNT}, extract_modes:Set[ExtractionMode]=set()) -> Dict[str, FeatureConfig]:
        if self._legacy_mode:
            return {"legacy" : self._DEFAULT_LEGACY_CONFIG} if IterationMode.AGGREGATE in iter_modes else {}
        ret_val : Dict[str, FeatureConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateFeatures.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountFeatures.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEnumDefs(unparsed_elements:Map) -> Dict[str, List[str]]:
        """_summary_

        TODO : Fully parse this, rather than just getting dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Dict[str, List[str]]
        """
        ret_val : Dict[str, List[str]]

        enums_list = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["enums"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_ENUMS,
            remove_target=True
        )
        if isinstance(enums_list, dict):
            ret_val = enums_list
        else:
            ret_val = GameSchema._DEFAULT_ENUMS
            Logger.Log(f"enums_list was unexpected type {type(enums_list)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameState(unparsed_elements:Map) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]

        game_state = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_GAME_STATE,
            remove_target=True
        )
        ret_val = {
            name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
            for name,elems in game_state.items()
        }

        return ret_val

    @staticmethod
    def _parseUserData(unparsed_elements:Map) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]

        user_data = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_USER_DATA,
            remove_target=True
        )
        ret_val = {
            name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
            for name,elems in user_data.items()
        }

        return ret_val

    @staticmethod
    def _parseEventList(unparsed_elements:Map) -> List[EventSchema]:
        ret_val : List[EventSchema]

        events_list = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_EVENT_LIST,
            remove_target=True
        )
        ret_val = [
            EventSchema.FromDict(name=key, unparsed_elements=val) for key,val in events_list.items()
        ]

        return ret_val

    @staticmethod
    def _parseDetectorMap(unparsed_elements:Map) -> DetectorMapConfig:
        ret_val : DetectorMapConfig

        detector_map = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["detectors"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_DETECTOR_MAP,
            remove_target=True
        )
        ret_val = DetectorMapConfig.FromDict(name="DetectorMap", unparsed_elements=detector_map)

        return ret_val

    @staticmethod
    def _parseFeatureMap(unparsed_elements:Map) -> FeatureMapConfig:
        ret_val : FeatureMapConfig

        feature_map = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["features"],
            to_type=dict,
            default_value=GameSchema._DEFAULT_FEATURE_MAP,
            remove_target=True
        )
        ret_val = FeatureMapConfig.FromDict(name="FeatureMap", unparsed_elements=feature_map)
        return ret_val

    @staticmethod
    def _parseLevelRange(unparsed_elements:Map) -> Tuple[Optional[int], Optional[int]]:
        ret_val : Tuple[Optional[int], Optional[int]]

        level_range = GameSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["level_range"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )

        if isinstance(level_range, dict):
            ret_val = (level_range.get("min", None), level_range.get("max", None))
        elif level_range == None:
            ret_val = (GameSchema._DEFAULT_MIN_LEVEL, GameSchema._DEFAULT_MAX_LEVEL)
        else:
            ret_val = (GameSchema._DEFAULT_MIN_LEVEL, GameSchema._DEFAULT_MAX_LEVEL)
            Logger.Log(f"level_range was unexpected type {type(level_range)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
