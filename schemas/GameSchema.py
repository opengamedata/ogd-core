# import standard libraries
import logging
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Set, Union
# import local files
import utils
from schemas.game_schemas.AggregateSchema import AggregateSchema
from schemas.game_schemas.DetectorSchema import DetectorSchema
from schemas.game_schemas.EventSchema import EventSchema
from schemas.game_schemas.FeatureSchema import FeatureSchema
from schemas.game_schemas.PerCountSchema import PerCountSchema
from schemas.IterationMode import IterationMode
from schemas.ExtractionMode import ExtractionMode
from utils import Logger, loadJSONFile

## @class GameSchema
#  A fairly simple class that reads a JSON schema with information on how a given
#  game's data is structured in the database, and the features we want to extract
#  for that game.
#  The class includes several functions for easy access to the various parts of
#  this schema data.
class GameSchema:
    # *** BUILT-INS ***

    def __init__(self, schema_name:str, schema_path:Optional[Path] = None):
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
        self._schema         : Optional[Dict[str, Dict[str, Any]]]
        self._event_list     : List[EventSchema] = []
        self._detector_map   : Dict[str, Dict[str, DetectorSchema]] = {}
        self._feature_map    : Dict[str, Dict[str, FeatureSchema]] = {}
        self._min_level      : Optional[int]
        self._max_level      : Optional[int]
        self._supported_vers : Optional[List[int]]
        self._game_name      : str = schema_name.split('.')[0]
        # set instance vars
        self._schema = GameSchema._loadSchema(game_name=self._game_name, schema_name=schema_name, schema_path=schema_path)
        if self._schema is not None:
            # 1. Get events, if any
            if "events" in self._schema.keys():
                self._event_list = [EventSchema(name=key, all_elements=val) for key,val in self._schema['events'].items()]
            else:
                Logger.Log(f"{self._game_name} game schema does not document any events.", logging.INFO)
            # 2. Get detectors, if any
            if "detectors" in self._schema.keys():
                if "perlevel" in self._schema['detectors']:
                    _perlevels = self._schema['detectors']['perlevel']
                    self._detector_map['perlevel'] = {key : DetectorSchema(name=key, all_elements=val) for key,val in _perlevels.items()}
                if "per_count" in self._schema['detectors']:
                    _percounts = self._schema['detectors']['per_count']
                    self._detector_map['per_count'] = {key : DetectorSchema(name=key, all_elements=val) for key,val in _percounts.items()}
                if "aggregate" in self._schema['detectors']:
                    _aggregates = self._schema['detectors']['aggregate']
                    self._detector_map['aggregate'] = {key : DetectorSchema(name=key, all_elements=val) for key,val in _aggregates.items()}
            else:
                Logger.Log(f"{self._game_name} game schema does not define any detectors.", logging.INFO)
            # 3. Get features, if any
            if "features" in self._schema.keys():
                if "perlevel" in self._schema['features']:
                    _perlevels = self._schema['features']['perlevel']
                    self._feature_map['perlevel'] = {key : PerCountSchema(name=key, all_elements=val) for key,val in _perlevels.items()}
                if "per_count" in self._schema['features']:
                    _percounts = self._schema['features']['per_count']
                    self._feature_map['per_count'] = {key : PerCountSchema(name=key, all_elements=val) for key,val in _percounts.items()}
                if "aggregate" in self._schema['features']:
                    _aggregates = self._schema['features']['aggregate']
                    self._feature_map['aggregate'] = {key : AggregateSchema(name=key, all_elements=val) for key,val in _aggregates.items()}
            else:
                Logger.Log(f"{self._game_name} game schema does not define any features.", logging.INFO)
            # 4. Get level_range, if any
            if "level_range" in self._schema.keys():
                self._min_level = self._schema.get("level_range", {}).get('min', None)
                self._max_level = self._schema.get("level_range", {}).get('max', None)

            # 5. Get config, if any
            if "config" in self._schema.keys():
                if "SUPPORTED_VERS" in self._schema['config']:
                    self._supported_vers = self._schema['config']['SUPPORTED_VERS']
                else:
                    self._supported_vers = None
                    Logger.Log(f"{self._game_name} game schema does not define supported versions, defaulting to support all versions.", logging.INFO)

            # 6. Notify if there are other, unexpected elements

    # def __getitem__(self, key) -> Any:
    #     return self._schema[key] if self._schema is not None else None
    
    def __str__(self) -> str:
        return str(self._game_name)

    # *** PUBLIC METHODS ***

    def Markdown(self) -> str:
        ret_val = "## Event Types  \n\n"
        ret_val += "The individual fields encoded in the *event_data* Event element for each type of event logged by the game.  \n\n"
        # Set up list of events
        event_list = ['\n'.join([f"**{evt_name}**:  "]
                              + [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in evt_items.items()])
                     for evt_name,evt_items in self.Events.items()]
        ret_val += "\n\n".join(event_list)
        # Set up list of features
        ret_val += "\n\n## Processed Features  \n\n"
        ret_val += "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  \n\n"
        feature_list = []
        for feat_kind in ["perlevel", "per_count", "aggregate"]:
            if feat_kind in self['features']:
                feature_list += [GameSchema._makeFeatureMarkdown(feat_name=feat_name, feat_kind=feat_kind, feat_items=feat_items)
                                for feat_name,feat_items in self['features'][feat_kind].items()]
        ret_val += "\n".join(feature_list)
        return ret_val

    def DetectorEnabled(self, detector_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode, overrides:Optional[List[str]]) -> bool:
        _val : Union[bool, List[str]] = False
        # get the value from the schema
        if iter_mode == IterationMode.AGGREGATE:
            _val = self.AggregateDetectors.get(detector_name, {}).get('enabled', False)
        if iter_mode == IterationMode.PERCOUNT:
            _val = self.PerCountDetectors.get(detector_name, {}).get('enabled', False)
        # figure out if the feature was enabled or not
        _is_enabled : bool = False
        if type(_val) == bool:
            _is_enabled = bool(_val)
        elif isinstance(_val, list):
            _val = [str(item).upper() for item in _val]
            if extract_mode is not None:
                is_enabled = extract_mode.name in _val
        else:
            raise ValueError(f"Invalid data type for 'enabled' for detector {detector_name} in {self.GameName}, expected bool or list but got  of {type(_val)}!")
        if overrides is not None:
            if detector_name in overrides:
                return _is_enabled
            else:
                return False
        else:
            return _is_enabled

    def FeatureEnabled(self, feature_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode, overrides:Optional[List[str]]=None) -> bool:
        _val : Union[bool, List[str]] = False
        # get the value from the schema
        if iter_mode == IterationMode.AGGREGATE:
            _val = self.AggregateFeatures.get(feature_name, {}).get('enabled', False)
        if iter_mode == IterationMode.PERCOUNT:
            _val = self.PerCountFeatures.get(feature_name, {}).get('enabled', False)
        # figure out if the feature was enabled or not
        _is_enabled : bool = False
        if type(_val) == bool:
            _is_enabled = bool(_val)
        elif isinstance(_val, list):
            _val = [str(item).upper() for item in _val]
            _is_enabled = extract_mode.name in _val
        else:
            raise ValueError(f"Invalid data type for feature {feature_name} in {self.GameName}")
        if overrides is not None and len(overrides) > 0:
            if feature_name in overrides:
                return _is_enabled
            else:
                return False
        else:
            return _is_enabled

    def level_range(self) -> range:
        ret_val = range(0)
        if self._min_level is not None and self._max_level is not None:
            # for i in range(self._min_level, self._max_level+1):
            ret_val = range(self._min_level, self._max_level+1)
        else:
            Logger.Log(f"Could not generate per-level features, min_level={self._min_level} and max_level={self._max_level}", logging.ERROR)
        return ret_val

    # *** PROPERTIES ***

    @property
    def GameName(self) -> str:
        return self._game_name

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
        return self.Detectors.get("percount", {})

    ## Function to retrieve the dictionary of aggregate detectors.
    @property
    def AggregateDetectors(self) -> Dict[str, DetectorSchema]:
        return self.Detectors.get("aggregate", {})

    ## Function to retrieve the dictionary of categorized features to extract.
    @property
    def Features(self) -> Dict[str, Dict[str, FeatureSchema]]:
        return self._feature_map

    ## Function to retrieve the compiled list of all feature names.
    @property
    def FeatureNames(self) -> List[str]:
        ret_val : List[str] = []
        for _category in self.Features.values():
            ret_val += [feature.Name for feature in _category.values()]
        return ret_val

    ## Function to retrieve the dictionary of per-custom-count features.
    @property
    def PerCountFeatures(self) -> Dict[str,PerCountSchema]:
        _percounts = self.Features.get("percount", {}).items()
        return {key:val for key,val in _percounts if isinstance(val, GameSchema.PerCountSchema)}

    ## Function to retrieve the dictionary of aggregate features.
    @property
    def AggregateFeatures(self) -> Dict[str,Any]:
        return self["features"]["aggregate"] if "aggregate" in self["features"].keys() else {}

    # *** PRIVATE STATICS ***

    @staticmethod
    def _loadSchema(game_name:str, schema_name:str, schema_path:Optional[Path] = None) -> Optional[Dict[Any, Any]]:
        ret_val = None

        # 1. make sure the name and path are in the right form.
        if not schema_name.lower().endswith(".json"):
            schema_name += ".json"
        if schema_path == None:
            schema_path = Path("./games") / f"{game_name}"
        # 2. try to actually load the contents of the file.
        try:
            ret_val = utils.loadJSONFile(filename=schema_name, path=schema_path)
        except FileNotFoundError as err:
            Logger.Log(f"Unable to load GameSchema for {game_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARN, depth=1)
            ret_val = GameSchema._schemaFromTemplate(schema_path=schema_path, schema_name=schema_name)
            if ret_val is not None:
                Logger.Log(f"Loaded schema for {game_name} from template.", logging.WARN, depth=1)
            else:
                Logger.Log(f"Failed to load schema for {game_name} from template.", logging.WARN, depth=1)
        else:
            if ret_val is None:
                Logger.Log(f"Could not find game schema at {schema_path / schema_name}", logging.ERROR)
        return ret_val

    @staticmethod
    def _schemaFromTemplate(schema_path:Path, schema_name:str) -> Optional[Dict[Any, Any]]:
        ret_val = None

        try:
            template_name = schema_name + ".template"
            template = schema_path / template_name
            copyfile(template, schema_path / schema_name)
        except Exception as cp_err:
            Logger.Log(f"Could not create {schema_name} from template, an error occurred:\n{cp_err}", logging.WARN, depth=2)
        else:
            ret_val = loadJSONFile(filename=schema_name, path=schema_path)
        return ret_val

    # *** PRIVATE METHODS ***
