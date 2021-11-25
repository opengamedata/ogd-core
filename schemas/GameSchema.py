# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Union
# import local files
import utils

## @class GameSchema
#  A fairly simple class that reads a JSON schema with information on how a given
#  game's data is structured in the database, and the features we want to extract
#  for that game.
#  The class includes several functions for easy access to the various parts of
#  this schema data.
class GameSchema:

    # *** BUILT-INS ***

    def __init__(self, schema_name:str, schema_path:Union[Path,None] = None):
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
        self._schema:       Dict = {}
        self._game_name:    str  = schema_name.split('.')[0]
        self._feature_list: Union[List[str],None] = None
        self._min_level:    Union[int,None] = None
        self._max_level:    Union[int,None] = None
        self._job_map:      Dict = {}
        # set instance vars
        if not schema_name.lower().endswith(".json"):
            schema_name += ".json"
        if schema_path == None:
            schema_path = Path("./games") / f"{schema_name.split('.')[0]}"
        self._schema = utils.loadJSONFile(filename=schema_name, path=schema_path)
        if self._schema is not None:
            if "features" in self._schema.keys():
                self._feature_list = []
                for feat_kind in ["perlevel", "per_count", "aggregate"]:
                    if feat_kind in self._schema['features']:
                        self._feature_list += self._schema['features'][feat_kind].keys()
            else:
                self._schema["features"] = {}
                utils.Logger.Log(f"{schema_name} game schema does not define any features.", logging.WARN)
        else:
            utils.Logger.Log(f"Could not find game schema at {schema_path}{schema_name}", logging.ERROR)
        # lastly, get max and min levels.
        if "level_range" in self._schema.keys():
            self._min_level = self._schema["level_range"]['min']
            self._max_level = self._schema["level_range"]['max']
        if "job_map" in self._schema.keys():
            self._job_map = self._schema["job_map"]

    def __getitem__(self, key) -> Any:
        return self._schema[key]
    
    def __str__(self) -> str:
        return str(self._game_name)

    def level_range(self) -> range:
        ret_val = range(0)
        if self._min_level is not None and self._max_level is not None:
            # for i in range(self._min_level, self._max_level+1):
            ret_val = range(self._min_level, self._max_level+1)
        else:
            utils.Logger.Log(f"Could not generate per-level features, min_level={self._min_level} and max_level={self._max_level}", logging.ERROR)
        return ret_val

    ## Function to retrieve the dictionary of event types for the game.
    def events(self) -> Dict[str,Any]:
        return self["events"]

    ## Function to retrieve the names of all event types for the game.
    def event_types(self) -> List[str]:
        return list(self["events"].keys())

    ## Function to retrieve the dictionary of categorized features to extract.
    def features(self) -> Dict[str, Dict[str,Any]]:
        return self["features"]

    ## Function to retrieve the compiled list of all feature names.
    def feature_names(self) -> Union[List[str], None]:
        return self._feature_list

    ## Function to retrieve the dictionary of per-level features.
    def perlevel_features(self) -> Dict[str,Any]:
        return self["features"]["perlevel"] if "perlevel" in self["features"].keys() else {}

    ## Function to retrieve the dictionary of per-custom-count features.
    def percount_features(self) -> Dict[str,Any]:
        return self["features"]["per_count"] if "per_count" in self["features"].keys() else {}

    ## Function to retrieve the dictionary of aggregate features.
    def aggregate_features(self) -> Dict[str,Any]:
        return self["features"]["aggregate"] if "aggregate" in self["features"].keys() else {}

    # *** PRIVATE METHODS ***
