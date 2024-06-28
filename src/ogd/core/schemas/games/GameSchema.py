# import standard libraries
import logging
from importlib.resources import files
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Set, Tuple, Union
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.schemas.games.AggregateSchema import AggregateSchema
from ogd.core.schemas.games.DetectorSchema import DetectorSchema
from ogd.core.schemas.games.DetectorMapSchema import DetectorMapSchema
from ogd.core.schemas.games.DataElementSchema import DataElementSchema
from ogd.core.schemas.games.EventSchema import EventSchema
from ogd.core.schemas.games.PerCountSchema import PerCountSchema
from ogd.core.schemas.games.FeatureSchema import FeatureSchema
from ogd.core.schemas.games.FeatureMapSchema import FeatureMapSchema
from ogd.core.models.enums.IterationMode import IterationMode
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.utils import utils
from ogd.core.utils.utils import loadJSONFile
from ogd.core.utils.Logger import Logger

## @class GameSchema
#  A fairly simple class that reads a JSON schema with information on how a given
#  game's data is structured in the database, and the features we want to extract
#  for that game.
#  The class includes several functions for easy access to the various parts of
#  this schema data.
class GameSchema(Schema):
    # *** BUILT-INS & PROPERTIES ***

    # TODO: need to get game_state from schema file.

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        """Constructor for the GameSchema class.
        Given a path and filename, it loads the data from a JSON schema,
        storing the full schema into a private variable, and compiling a list of
        all features to be extracted.

        :param schema_name: The name of the JSON schema file (if .json is not the file extension, .json will be appended)
        :type schema_name: str
        :param schema_path: schema_path Path to the folder containing the JSON schema file; if None is given, defaults to ./ogd/games/{game_id}/schemas/
        :type schema_path: str, optional
        """
    # 1. define instance vars
        self._game_id                : str                                  = name
        self._enum_defs              : Dict[str, List[str]]                 = {}
        self._game_state             : Dict[str, Any]                       = {}
        self._user_data              : Dict[str, Any]                       = {}
        self._event_list             : List[EventSchema]                    = []
        self._detector_map           : Dict[str, Dict[str, DetectorSchema]] = {'perlevel':{}, 'per_count':{}, 'aggregate':{}}
        self._aggregate_feats        : Dict[str, AggregateSchema]           = {}
        self._percount_feats         : Dict[str, PerCountSchema]            = {}
        self._legacy_perlevel_feats  : Dict[str, PerCountSchema]            = {}
        self._legacy_mode            : bool                                 = False
        self._config                 : Dict[str, Any]                       = {}
        self._min_level              : Optional[int]                        = None
        self._max_level              : Optional[int]                        = None
        self._other_ranges           : Dict[str, range]
        self._supported_vers         : Optional[List[int]]

        if not isinstance(all_elements, dict):
            all_elements   = {}
            Logger.Log(f"For {self._game_id} GameSchema, all_elements was not a dict, defaulting to empty dict", logging.WARN)

    # 2. set instance vars, starting with event data

        if "enums" in all_elements.keys():
            self._enum_defs = GameSchema._parseEnumDefs(enums_list=all_elements['enums'])
        else:
            Logger.Log(f"{self._game_id} game schema does not specify any custom enums", logging.INFO)

        if "game_state" in all_elements.keys():
            self._game_state = GameSchema._parseGameState(game_state=all_elements['game_state'])
        else:
            Logger.Log(f"{self._game_id} game schema does not specify the structure of the game state colum, defaulting to empty dictn", logging.INFO)

        if "user_data" in all_elements.keys():
            self._user_data = GameSchema._parseUserData(user_data=all_elements['user_data'])
        else:
            Logger.Log(f"{self._game_id} game schema does not specify the structure of the user data colum, defaulting to empty dictn", logging.INFO)
        if "events" in all_elements.keys():
            self._event_list = GameSchema._parseEventList(events_list=all_elements['events'])
        else:
            Logger.Log(f"{self._game_id} game schema does not document any events.", logging.INFO)

    # 3. Get detector information
        if "detectors" in all_elements.keys():
            # TODO : Just have DetectorMapSchema directly
            _detector_map = GameSchema._parseDetectorMap(detector_map=all_elements['detectors'])
            self._detector_map = _detector_map.AsDict
        else:
            Logger.Log(f"{self._game_id} game schema does not define any detectors.", logging.INFO)

    # 4. Get feature information
        if "features" in all_elements.keys():
            # TODO : Just have the FeatureMapSchema directly, not 4 different things.
            _feat_map = GameSchema._parseFeatureMap(feature_map=all_elements['features'])
            self._aggregate_feats.update(_feat_map.AggregateFeatures)
            self._percount_feats.update(_feat_map.PerCountFeatures)
            self._legacy_perlevel_feats.update(_feat_map.LegacyPerLevelFeatures)
            self._legacy_mode = _feat_map.LegacyMode
        else:
            Logger.Log(f"{self._game_id} game schema does not define any features.", logging.INFO)

    # 5. Get config, if any
        if "config" in all_elements.keys():
            self._config = all_elements['config']
        else:
            Logger.Log(f"{self._game_id} game schema does not define any config items.", logging.INFO)
        if "SUPPORTED_VERS" in self._config:
            self._supported_vers = self._config['SUPPORTED_VERS']
        else:
            self._supported_vers = None
            Logger.Log(f"{self._game_id} game schema does not define supported versions, defaulting to support all versions.", logging.INFO)

    # 6. Get level range and other ranges, if any
        if "level_range" in all_elements.keys():
            self._min_level, self._max_level = GameSchema._parseLevelRange(all_elements['level_range'])
        else:
            Logger.Log(f"{self._game_id} game schema does not define a level range.", logging.INFO)

        self._other_ranges = {key : range(val.get('min', 0), val.get('max', 1)) for key,val in all_elements.items() if key.endswith("_range")}

    # 7. Collect any other, unexpected elements
        _leftovers = { key:val for key,val in all_elements.items() if key not in {'enums', 'game_state', 'user_data', 'events', 'detectors', 'features', 'level_range', 'config'}.union(self._other_ranges.keys()) }
        super().__init__(name=self._game_id, other_elements=_leftovers)

    # *** BUILT-INS & PROPERTIES ***

    # def __getitem__(self, key) -> Any:
    #     return _schema[key] if _schema is not None else None

    @property
    def GameName(self) -> str:
        """Property for the name of the game configured by this schema
        """
        return self._game_id

    @property
    def EnumDefs(self) -> Dict[str, List[str]]:
        """Property for the dict of all enums defined for sub-elements in the given game's schema.
        """
        return self._enum_defs

    @property
    def GameState(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the GameState column for the given game.
        """
        return self._game_state

    @property
    def UserData(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the UserData column for the given game.
        """
        return self._user_data

    @property
    def Events(self) -> List[EventSchema]:
        """Property for the list of events the game logs.
        """
        return self._event_list

    @property
    def EventTypes(self) -> List[str]:
        """Property for the names of all event types for the game.
        """
        return [event.Name for event in self.Events]

    @property
    def Detectors(self) -> Dict[str, Dict[str, DetectorSchema]]:
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
    def PerCountDetectors(self) -> Dict[str, DetectorSchema]:
        """Property for the dictionary of per-custom-count detectors.
        """
        return self.Detectors.get("per_count", {})

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorSchema]:
        """Property for the dictionary of aggregate detectors.
        """
        return self.Detectors.get("aggregate", {})

    @property
    def Features(self) -> Dict[str, Union[Dict[str, AggregateSchema], Dict[str, PerCountSchema]]]:
        """Property for the dictionary of categorized features to extract.
        """
        return { 'aggregate' : self._aggregate_feats, 'per_count' : self._percount_feats, 'perlevel' : self._legacy_perlevel_feats }

    @property
    def FeatureNames(self) -> List[str]:
        """Property for the compiled list of all feature names.
        """
        ret_val : List[str] = []
        for _category in self.Features.values():
            ret_val += [feature.Name for feature in _category.values()]
        return ret_val

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str,PerCountSchema]:
        """Property for the dictionary of legacy per-level features
        """
        return self._legacy_perlevel_feats

    @property
    def PerCountFeatures(self) -> Dict[str,PerCountSchema]:
        """Property for the dictionary of per-custom-count features.
        """
        return self._percount_feats

    @property
    def AggregateFeatures(self) -> Dict[str,AggregateSchema]:
        """Property for the dictionary of aggregate features.
        """
        return self._aggregate_feats

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


    # *** PUBLIC STATICS ***
    @staticmethod
    def FromFile(game_id:str, schema_path:Optional[Path] = None):
        # Give schema_path a default, don't think we can use game_id to construct it directly in the function header (so do it here if None)
        schema_path = schema_path or Path("./") / "ogd" / "games" / game_id / "schemas"
        all_elements = GameSchema._loadSchemaFile(game_name=game_id, schema_path=schema_path)
        return GameSchema(name=game_id, all_elements=all_elements or {})

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

        _detector_schema : Optional[DetectorSchema]
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

        _feature_schema : Optional[FeatureSchema]
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

    def EnabledDetectors(self, iter_modes:Set[IterationMode], extract_modes:Set[ExtractionMode]=set()) -> Dict[str, DetectorSchema]:
        if self._legacy_mode:
            return {}
        ret_val : Dict[str, DetectorSchema] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateDetectors.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountDetectors.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    def EnabledFeatures(self, iter_modes:Set[IterationMode]={IterationMode.AGGREGATE, IterationMode.PERCOUNT}, extract_modes:Set[ExtractionMode]=set()) -> Dict[str, FeatureSchema]:
        if self._legacy_mode:
            return {"legacy" : AggregateSchema("legacy", {"type":"legacy", "return_type":None, "description":"", "enabled":True})} if IterationMode.AGGREGATE in iter_modes else {}
        ret_val : Dict[str, FeatureSchema] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateFeatures.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountFeatures.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    # *** PRIVATE STATICS ***

    @staticmethod
    def _loadSchemaFile(game_name:str, schema_path:Path) -> Optional[Dict[Any, Any]]:
        ret_val = None

        # 1. make sure the name and path are in the right form.
        schema_name = f"{game_name.upper()}.json"
        # 2. try to actually load the contents of the file.
        try:
            ret_val = utils.loadJSONFile(filename=schema_name, path=schema_path)
        except (ModuleNotFoundError, FileNotFoundError) as err:
            Logger.Log(f"Unable to load GameSchema for {game_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARN, depth=1)
            ret_val = GameSchema._schemaFromTemplate(schema_path=schema_path, schema_name=schema_name)
            if ret_val is not None:
                Logger.Log(f"Loaded schema for {game_name} from template.", logging.WARN, depth=1)
            else:
                Logger.Log(f"Failed to load schema for {game_name} from template.", logging.WARN, depth=1)
        else:
            if ret_val is None:
                Logger.Log(f"Could not load game schema at {schema_path / schema_name}, the file was empty!", logging.ERROR)
        return ret_val

    @staticmethod
    def _schemaFromTemplate(schema_path:Path, schema_name:str) -> Optional[Dict[Any, Any]]:
        ret_val = None

        template_name = schema_name + ".template"
        try:
            ret_val = loadJSONFile(filename=template_name, path=schema_path, autocorrect_extension=False)
        except FileNotFoundError as no_file:
            Logger.Log(       f"Could not load {schema_name} from template, the template does not exist at {schema_path}.", logging.WARN, depth=2)
            print(f"(via print) Could not create {schema_name} from template, the template does not exist at {schema_path}.")
        else:
            Logger.Log(f"Trying to copy {schema_name} from template, for future use...", logging.DEBUG, depth=2)
            template = schema_path / template_name
            try:
                copyfile(template, schema_path / schema_name)
            except Exception as cp_err:
                Logger.Log(       f"Could not copy {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}", logging.WARN, depth=2)
                print(f"(via print) Could not copy {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}")
            else:
                Logger.Log(       f"Successfully copied {schema_name} from template.", logging.DEBUG, depth=2)
        return ret_val


    @staticmethod
    def _parseEnumDefs(enums_list:Dict[str, Any]) -> Dict[str, List[str]]:
        ret_val : Dict[str, List[str]]
        if isinstance(enums_list, dict):
            ret_val = enums_list
        else:
            ret_val = {}
            Logger.Log(f"enums_list was unexpected type {type(enums_list)}, defaulting to empty Dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameState(game_state:Dict[str, Any]) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]
        if isinstance(game_state, dict):
            ret_val = {name:DataElementSchema(name=name, all_elements=elems) for name,elems in game_state.items()}
        else:
            ret_val = {}
            Logger.Log(f"game_state was unexpected type {type(game_state)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseUserData(user_data:Dict[str, Any]) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]
        if isinstance(user_data, dict):
            ret_val = {name:DataElementSchema(name=name, all_elements=elems) for name,elems in user_data.items()}
        else:
            ret_val = {}
            Logger.Log(f"user_data was unexpected type {type(user_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEventList(events_list:Dict[str, Any]) -> List[EventSchema]:
        ret_val : List[EventSchema]
        if isinstance(events_list, dict):
            ret_val = [EventSchema(name=key, all_elements=val) for key,val in events_list.items()]
        else:
            ret_val = []
            Logger.Log(f"events_list was unexpected type {type(events_list)}, defaulting to empty List.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDetectorMap(detector_map:Dict[str, Any]) -> DetectorMapSchema:
        ret_val : DetectorMapSchema
        if isinstance(detector_map, dict):
            ret_val = DetectorMapSchema(name=f"Detectors", all_elements=detector_map)
        else:
            ret_val = DetectorMapSchema(name="Empty Features", all_elements={})
            Logger.Log(f"detector_map was unexpected type {type(detector_map)}, defaulting to empty map.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFeatureMap(feature_map:Dict[str, Any]) -> FeatureMapSchema:
        ret_val : FeatureMapSchema
        if isinstance(feature_map, dict):
            ret_val = FeatureMapSchema(name=f"Features", all_elements=feature_map)
        else:
            ret_val = FeatureMapSchema(name="Empty Features", all_elements={})
            Logger.Log(f"feature_map was unexpected type {type(feature_map)}, defaulting to empty map.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseLevelRange(level_range:Dict[str, int]) -> Tuple[Optional[int], Optional[int]]:
        ret_val : Tuple[Optional[int], Optional[int]]
        if isinstance(level_range, dict):
            ret_val = (level_range.get("min", None), level_range.get("max", None))
        else:
            ret_val = (None, None)
            Logger.Log(f"level_range was unexpected type {type(level_range)}, defaulting to no specified range.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
