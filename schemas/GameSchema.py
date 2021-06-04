# import standard libraries
import logging
import os
import typing
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
    ## Constructor for the GameSchema class.
    #  Given a path and filename, it loads the data from a JSON schema,
    #  storing the full schema into a private variable, and compiling a list of
    #  all features to be extracted.
    #
    #  @param schema_name The name of the JSON schema file
    #                     (if .json is not the file extension, .json will be appended)
    #  @param schema_path Path to the folder containing the JSON schema file
    #                     (if the path does not end in "/", a "/" will be appended)
    def __init__(self, schema_name:str, schema_path:str = os.path.dirname(__file__) + "/GAMES/"):
        # define instance vars
        self._schema:       Dict = {}
        self._feature_list: Union[List,None] = None
        # set instance vars
        if not schema_name.lower().endswith(".json"):
            schema_name += ".json"
        self._schema = utils.loadJSONFile(schema_name, schema_path)
        if self._schema is None:
            utils.Logger.Log(f"Could not find event_data_complex schemas at {schema_path}{schema_name}", logging.ERROR)
        else:
            self._feature_list = list(self._schema["features"]["perlevel"].keys()) \
                               + list(self._schema["features"]["per_custom_count"].keys()) \
                               + list(self._schema["features"]["aggregate"].keys())
        # lastly, get max and min levels, and get the session ids.
        self.max_level: Union[int,None] = self.level_range()['min']
        self.min_level: Union[int,None] = self.level_range()['max']

    def __getitem__(self, key) -> Any:
        return self._schema[key]

    def level_range(self) -> Dict[str,int]:
        return self["level_range"]

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
        return self["features"]["perlevel"]

    ## Function to retrieve the dictionary of per-custom-count features.
    def percount_features(self) -> Dict[str,Any]:
        return self["features"]["per_custom_count"]

    ## Function to retrieve the dictionary of aggregate features.
    def aggregate_features(self) -> Dict[str,Any]:
        return self["features"]["aggregate"]
