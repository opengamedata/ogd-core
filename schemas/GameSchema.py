# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
# import local files
import utils
from schemas.IterationMode import IterationMode
from schemas.ExtractionMode import ExtractionMode
from utils import Logger

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
        self._schema:        Optional[Dict] = {}
        self._game_name:     str  = schema_name.split('.')[0]
        self._detector_list: Optional[List[str]] = None
        self._feature_list:  Optional[List[str]] = None
        self._min_level:     Optional[int] = None
        self._max_level:     Optional[int] = None
        self._job_map:       Dict = {}
        # set instance vars
        if not schema_name.lower().endswith(".json"):
            schema_name += ".json"
        if schema_path == None:
            schema_path = Path("./games") / f"{schema_name.split('.')[0]}"
        self._schema = utils.loadJSONFile(filename=schema_name, path=schema_path)
        if self._schema is not None:
            if "detectors" in self._schema.keys():
                self._detector_list = []
                for feat_kind in ["perlevel", "per_count", "aggregate"]:
                    if feat_kind in self._schema['detectors']:
                        self._detector_list += self._schema['detectors'][feat_kind].keys()
            else:
                self._schema["detectors"] = {}
                Logger.Log(f"{schema_name} game schema does not define any detectors.", logging.WARN)
            if "features" in self._schema.keys():
                self._feature_list = []
                for feat_kind in ["perlevel", "per_count", "aggregate"]:
                    if feat_kind in self._schema['features']:
                        self._feature_list += self._schema['features'][feat_kind].keys()
            else:
                self._schema["features"] = {}
                Logger.Log(f"{schema_name} game schema does not define any features.", logging.WARN)
            # lastly, get max and min levels.
            if "level_range" in self._schema.keys():
                self._min_level = self._schema["level_range"]['min']
                self._max_level = self._schema["level_range"]['max']
            if "job_map" in self._schema.keys():
                self._job_map = self._schema["job_map"]
        else:
            Logger.Log(f"Could not find game schema at {schema_path / schema_name}", logging.ERROR)

    def __getitem__(self, key) -> Any:
        return self._schema[key] if self._schema is not None else None
    
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

    def DetectorEnabled(self, detector_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        _val : Union[bool, List[str]] = False
        # get the value from the schema
        if iter_mode == IterationMode.AGGREGATE:
            _val = self.AggregateDetectors.get(detector_name, False)
        if iter_mode == IterationMode.PERCOUNT:
            _val = self.PerCountDetectors.get(detector_name, False)
        # figure out if the feature was enabled or not
        if type(_val) == bool:
            return bool(_val)
        elif isinstance(_val, list):
            _val = [str(item).upper() for item in _val]
            if extract_mode is not None:
                return extract_mode.name in _val
        else:
            raise ValueError(f"Invalid data type for detector {detector_name} in {self.GameName}")

    def FeatureEnabled(self, feature_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        _val : Union[bool, List[str]] = False
        # get the value from the schema
        if iter_mode == IterationMode.AGGREGATE:
            _val = self.AggregateFeatures.get(feature_name, False)
        if iter_mode == IterationMode.PERCOUNT:
            _val = self.PerCountFeatures.get(feature_name, False)
        # figure out if the feature was enabled or not
        if type(_val) == bool:
            return bool(_val)
        elif isinstance(_val, list):
            _val = [str(item).upper() for item in _val]
            return extract_mode.name in _val
        else:
            raise ValueError(f"Invalid data type for feature {feature_name} in {self.GameName}")

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
    def Events(self) -> Dict[str,Any]:
        return self["events"]

    ## Function to retrieve the names of all event types for the game.
    @property
    def EventTypes(self) -> List[str]:
        return list(self["events"].keys())

    ## Function to retrieve the dictionary of categorized detectors to extract.
    @property
    def Detectors(self) -> Dict[str, Dict[str,Any]]:
        return self["detectors"]

    ## Function to retrieve the compiled list of all detector names.
    @property
    def DetectorNames(self) -> Optional[List[str]]:
        return self._detector_list

    ## Function to retrieve the dictionary of per-custom-count detectors.
    @property
    def PerCountDetectors(self) -> Dict[str,Any]:
        return self["detectors"]["per_count"] if "per_count" in self["detectors"].keys() else {}

    ## Function to retrieve the dictionary of aggregate detectors.
    @property
    def AggregateDetectors(self) -> Dict[str,Any]:
        return self["detectors"]["aggregate"] if "aggregate" in self["detectors"].keys() else {}

    ## Function to retrieve the dictionary of categorized features to extract.
    @property
    def Features(self) -> Dict[str, Dict[str,Any]]:
        return self["features"]

    ## Function to retrieve the compiled list of all feature names.
    @property
    def FeatureNames(self) -> Optional[List[str]]:
        return self._feature_list

    ## Function to retrieve the dictionary of per-custom-count features.
    @property
    def PerCountFeatures(self) -> Dict[str,Any]:
        return self["features"]["per_count"] if "per_count" in self["features"].keys() else {}

    ## Function to retrieve the dictionary of aggregate features.
    @property
    def AggregateFeatures(self) -> Dict[str,Any]:
        return self["features"]["aggregate"] if "aggregate" in self["features"].keys() else {}

    # *** PRIVATE METHODS ***

    @staticmethod
    def _makeFeatureMarkdown(feat_name:str, feat_kind:str, feat_items) -> str:
        ret_val   : str                     = ""
        _subfeats : Dict[str,Dict[str,str]] = feat_items.get("subfeatures", {})

        ret_val += f"**{feat_name}** : *{feat_items.get('type', 'Unknown')}*, *{feat_kind} feature* {' (disabled)' if not feat_items.get('enabled', True) else ''}  \n"
        ret_val += f"{feat_items.get('description', 'No description.')}  \n"
        if len(_subfeats.keys()) > 0:
            ret_val += "*Sub-features*:  \n\n"
            for subfeat_name, subfeat_items in _subfeats.items():
                ret_val += f"- **{subfeat_name}** : *{subfeat_items.get('type', 'Unknown')}*, {subfeat_items.get('description', 'No description.')}  \n"
        return ret_val