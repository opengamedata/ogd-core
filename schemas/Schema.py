# import standard libraries
import logging
import os
import typing
# import local files
import utils

## @class Schema
#  A fairly simple class that reads a JSON schema with information on how a given
#  game's data is structured in the database, and the features we want to extract
#  for that game.
#  The class includes several functions for easy access to the various parts of
#  this schema data.
class Schema:
    ## Constructor for the Schema class.
    #  Given a path and filename, it loads the data from a JSON schema,
    #  storing the full schema into a private variable, and compiling a list of
    #  all features to be extracted.
    #
    #  @param schema_name The name of the JSON schema file
    #                     (if .json is not the file extension, .json will be appended)
    #  @param schema_path Path to the folder containing the JSON schema file
    #                     (if the path does not end in "/", a "/" will be appended)
    def __init__(self, schema_name:str, schema_path:str = os.path.dirname(__file__) + "/JSON/"):
        # define instance vars
        self._schema:       typing.Dict = {}
        self._feature_list: typing.Dict = None
        # set instance vars
        if not schema_name.endswith(".json"):
            schema_name += ".json"
        if not schema_path.endswith("/"):
            schema_path += "/"
        self._schema = utils.loadJSONFile(schema_name, schema_path)
        if self._schema is None:
            logging.error(f"Could not find event_data_complex schemas at {schema_path}{schema_name}")
        else:
            self._feature_list = list(self._schema["features"]["perlevel"].keys()) \
                               + list(self._schema["features"]["per_custom_count"].keys()) \
                               + list(self._schema["features"]["aggregate"].keys())

    ## Function to retrieve the full schema dictionary.
    def schema(self) -> typing.Dict:
        return self._schema

    ## Function to retrieve the dictionary of event types for the game.
    def events(self) -> typing.Dict:
        return self._schema["events"]

    ## Function to retrieve the names of all event types for the game.
    def event_types(self):
        return self._schema["events"].keys()

    ## Function to retrieve the dictionary of categorized features to extract.
    def features(self) -> typing.Dict:
        return self._schema["features"]

    ## Function to retrieve the dictionary of per-level features.
    def perlevel_features(self) -> typing.Dict:
        return self._schema["features"]["perlevel"]

    ## Function to retrieve the dictionary of per-custom-count features.
    def percount_features(self) -> typing.Dict:
        return self._schema["features"]["per_custom_count"]

    ## Function to retrieve the dictionary of aggregate features.
    def aggregate_features(self) -> typing.Dict:
        return self._schema["features"]["aggregate"]

    ## Function to retrieve the compiled list of all feature names.
    def feature_list(self) -> typing.List:
        return self._feature_list

    ## Function to retrieve the dictionary of database columns.
    def db_columns_with_types(self) -> typing.Dict:
        return self._schema["db_columns"]

    ## Function to retrieve the names of all database columns.
    def db_columns(self):
        return self._schema["db_columns"].keys()