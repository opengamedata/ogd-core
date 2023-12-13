# import standard libraries
import logging
from importlib.resources import files
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Set, Union
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.schemas.games.AggregateSchema import AggregateSchema
from ogd.core.schemas.games.DetectorSchema import DetectorSchema
from ogd.core.schemas.games.EventSchema import EventSchema
from ogd.core.schemas.games.FeatureSchema import FeatureSchema
from ogd.core.schemas.games.PerCountSchema import PerCountSchema
from ogd.core.schemas.IterationMode import IterationMode
from ogd.core.schemas.ExtractionMode import ExtractionMode
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

    def __init__(self, game_id:str, schema_path:Optional[Path] = None):
        """Constructor for the GameSchema class.
        Given a path and filename, it loads the data from a JSON schema,
        storing the full schema into a private variable, and compiling a list of
        all features to be extracted.

        :param schema_name: The name of the JSON schema file (if .json is not the file extension, .json will be appended)
        :type schema_name: str
        :param schema_path: schema_path Path to the folder containing the JSON schema file, defaults to None
        :type schema_path: str, optional
        """
        # define instance vars
        self._event_list             : List[EventSchema] = []
        self._detector_map           : Dict[str, Dict[str, DetectorSchema]] = {'perlevel':{}, 'per_count':{}, 'aggregate':{}}
        self._aggregate_feats        : Dict[str, AggregateSchema]           = {}
        self._percount_feats         : Dict[str, PerCountSchema]            = {}
        self._legacy_perlevel_feats  : Dict[str, PerCountSchema]            = {}
        self._legacy_mode            : bool                                 = False
        self._game_id                : str                                  = game_id
        self._config                 : Dict[str, Any]
        self._min_level              : Optional[int]
        self._max_level              : Optional[int]
        self._supported_vers         : Optional[List[int]]
        # set instance vars
        _schema = GameSchema._loadSchemaFile(game_name=self._game_id, schema_path=schema_path)
        if _schema is not None:
            # 1. Get events, if any
            if "events" in _schema.keys():
                self._event_list = [EventSchema(name=key, all_elements=val) for key,val in _schema['events'].items()]
            else:
                Logger.Log(f"{self._game_id} game schema does not document any events.", logging.INFO)
            # 2. Get detectors, if any
            if "detectors" in _schema.keys():
                if "perlevel" in _schema['detectors']:
                    _perlevels = _schema['detectors']['perlevel']
                    self._detector_map['per_count'] = {key : DetectorSchema(name=key, all_elements=val) for key,val in _perlevels.items()}
                if "per_count" in _schema['detectors']:
                    _percounts = _schema['detectors']['per_count']
                    self._detector_map['per_count'].update({key : DetectorSchema(name=key, all_elements=val) for key,val in _percounts.items()})
                if "aggregate" in _schema['detectors']:
                    _aggregates = _schema['detectors']['aggregate']
                    self._detector_map['aggregate'] = {key : DetectorSchema(name=key, all_elements=val) for key,val in _aggregates.items()}
            else:
                Logger.Log(f"{self._game_id} game schema does not define any detectors.", logging.INFO)
            # 3. Get features, if any
            if "features" in _schema.keys():
                if "legacy" in _schema['features'].keys():
                    self._legacy_mode = _schema['features']['legacy'].get('enabled', False)
                if "perlevel" in _schema['features']:
                    _perlevels = _schema['features']['perlevel']
                    self._legacy_perlevel_feats.update({key : PerCountSchema(name=key, all_elements=val) for key,val in _perlevels.items()})
                if "per_count" in _schema['features']:
                    _percounts = _schema['features']['per_count']
                    self._percount_feats.update({key : PerCountSchema(name=key, all_elements=val) for key,val in _percounts.items()})
                if "aggregate" in _schema['features']:
                    _aggregates = _schema['features']['aggregate']
                    self._aggregate_feats.update({key : AggregateSchema(name=key, all_elements=val) for key,val in _aggregates.items()})
            else:
                Logger.Log(f"{self._game_id} game schema does not define any features.", logging.INFO)
            # 4. Get level_range, if any
            if "level_range" in _schema.keys():
                self._min_level = _schema.get("level_range", {}).get('min', None)
                self._max_level = _schema.get("level_range", {}).get('max', None)

            # 5. Get other ranges, if any
            self._other_ranges = {key:range(val.get('min', 0), val.get('max', 1)) for key,val in _schema.items() if key.endswith("_range")}

            # 6. Get config, if any
            self._config = _schema.get('config', {})
            if "SUPPORTED_VERS" in _schema['config']:
                self._supported_vers = _schema['config']['SUPPORTED_VERS']
            else:
                self._supported_vers = None
                Logger.Log(f"{self._game_id} game schema does not define supported versions, defaulting to support all versions.", logging.INFO)

            # 7. Collect any other, unexpected elements
            _leftovers = { key:val for key,val in _schema.items() if key not in {'events', 'detectors', 'features', 'level_range', 'config'}.union(self._other_ranges.keys()) }
            super().__init__(name=self._game_id, other_elements=_leftovers)

    # def __getitem__(self, key) -> Any:
    #     return _schema[key] if _schema is not None else None

    # *** PUBLIC METHODS ***

    def GetCountRange(self, count:Any) -> range:
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
        if self._legacy_mode:
            return False
        ret_val : bool

        _detector_schema : Optional[DetectorSchema]
        if iter_mode == IterationMode.AGGREGATE:
            _detector_schema = self.Detectors['aggregate'].get(detector_name)
        elif iter_mode == IterationMode.PERCOUNT:
            _detector_schema = self.Detectors['per_count'].get(detector_name, self.Detectors['perlevel'].get(detector_name))
        else:
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
        if iter_mode == IterationMode.AGGREGATE:
            _feature_schema = self.AggregateFeatures.get(feature_name)
        elif iter_mode == IterationMode.PERCOUNT:
            _feature_schema = self.PerCountFeatures.get(feature_name)
        else:
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

    # *** PROPERTIES ***

    @property
    def GameName(self) -> str:
        return self._game_id

    ## Function to retrieve the dictionary of event types for the game.
    @property
    def Events(self) -> List[EventSchema]:
        return self._event_list

    ## Function to retrieve the names of all event types for the game.
    @property
    def EventTypes(self) -> List[str]:
        return [event.Name for event in self.Events]

    ## Function to retrieve the dictionary of categorized detectors to extract.
    @property
    def Detectors(self) -> Dict[str, Dict[str, DetectorSchema]]:
        return self._detector_map

    ## Function to retrieve the compiled list of all detector names.
    @property
    def DetectorNames(self) -> List[str]:
        ret_val : List[str] = []
        for _category in self.Detectors.values():
            ret_val += [detector.Name for detector in _category.values()]
        return ret_val

    ## Function to retrieve the dictionary of per-custom-count detectors.
    @property
    def PerCountDetectors(self) -> Dict[str, DetectorSchema]:
        return self.Detectors.get("per_count", {})

    ## Function to retrieve the dictionary of aggregate detectors.
    @property
    def AggregateDetectors(self) -> Dict[str, DetectorSchema]:
        return self.Detectors.get("aggregate", {})

    ## Function to retrieve the dictionary of categorized features to extract.
    @property
    def Features(self) -> Dict[str, Union[Dict[str, AggregateSchema], Dict[str, PerCountSchema]]]:
        return { 'aggregate' : self._aggregate_feats, 'per_count' : self._percount_feats, 'perlevel' : self._legacy_perlevel_feats }

    ## Function to retrieve the compiled list of all feature names.
    @property
    def FeatureNames(self) -> List[str]:
        ret_val : List[str] = []
        for _category in self.Features.values():
            ret_val += [feature.Name for feature in _category.values()]
        return ret_val

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str,PerCountSchema]:
        return self._legacy_perlevel_feats

    ## Function to retrieve the dictionary of per-custom-count features.
    @property
    def PerCountFeatures(self) -> Dict[str,PerCountSchema]:
        return self._percount_feats

    ## Function to retrieve the dictionary of aggregate features.
    @property
    def AggregateFeatures(self) -> Dict[str,AggregateSchema]:
        return self._aggregate_feats

    @property
    def LevelRange(self) -> range:
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
                         "The individual fields encoded in the *event_data* Event element for each type of event logged by the game."
                        ]
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

        ret_val = "  \n\n".join(event_summary + event_list + detector_summary + detector_list + feature_summary + feature_list)

        return ret_val

    # *** PRIVATE STATICS ***

    @staticmethod
    def _loadSchemaFile(game_name:str, schema_path:Optional[Path] = None) -> Optional[Dict[Any, Any]]:
        ret_val = None

        # 1. make sure the name and path are in the right form.
        schema_name = f"{game_name.upper()}.json"
        if schema_path == None:
            schema_path = Path("./") / "ogd" / "core" / "games" / game_name / "schemas"
        # 2. try to actually load the contents of the file.
        try:
            ret_val = utils.loadJSONFile(filename=schema_name, path=schema_path)
        except FileNotFoundError as err:
            Logger.Log(f"Unable to load GameSchema for {game_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARN, depth=1)
            print(f"Unable to load GameSchema for {game_name}, {schema_name} does not exist! Trying to load from json template instead...")
            ret_val = GameSchema._schemaFromTemplate(schema_path=schema_path, schema_name=schema_name)
            if ret_val is not None:
                Logger.Log(f"Loaded schema for {game_name} from template.", logging.WARN, depth=1)
                print(f"Loaded schema for {game_name} from template.")
            else:
                Logger.Log(f"Failed to load schema for {game_name} from template.", logging.WARN, depth=1)
                print(f"Failed to load schema for {game_name} from template.")
        else:
            if ret_val is None:
                Logger.Log(f"Could not find game schema at {schema_path / schema_name}", logging.ERROR)
                print(f"Could not find game schema at {schema_path / schema_name}")
        print(f"Finished attempting to load schema, with game_name {game_name} and size {len(ret_val) if ret_val is not None else 'None'}")
        return ret_val

    @staticmethod
    def _schemaFromTemplate(schema_path:Path, schema_name:str) -> Optional[Dict[Any, Any]]:
        ret_val = None

        template_name = schema_name + ".template"
        template = schema_path / template_name
        try:
            copyfile(template, schema_path / schema_name)
        except FileNotFoundError as no_file:
            Logger.Log(f"Could not create {schema_name} from template, the template does not exist at {template}.\nTrying to load from package, without copy.", logging.WARN, depth=2)
            print(f"Could not create {schema_name} from template, the template does not exist at {template}.\nTrying to load from package, without copy.")
            ret_val = loadJSONFile(filename=template_name, path=schema_path, autocorrect_extension=False)
        except Exception as cp_err:
            Logger.Log(f"Could not create {schema_name} from template, an error occurred:\n{cp_err}", logging.WARN, depth=2)
            print(f"Could not create {schema_name} from template, an error occurred:\n{cp_err}")
        else:
            ret_val = loadJSONFile(filename=schema_name, path=schema_path)
        return ret_val

    # *** PRIVATE METHODS ***
