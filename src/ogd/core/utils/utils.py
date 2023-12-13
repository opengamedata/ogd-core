## @namespace utils
#  A module of utility functions used in the feature_extraction_to_csv project
import json
import logging
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals
from ogd.core.utils.Logger import Logger

map = Dict[str, Any]
ExportRow = List[Any]

## Function to open a given JSON file, and retrieve the data as a Python object.
#  @param filename  The name of the JSON file. If the file extension is not .json,
#                       then ".json" will be appended.
#  @param path      The path (relative or absolute) to the folder containing the
#                       JSON file. If path does not end in /, then "/" will be appended.
#  @return          A python object parsed from the JSON.
def loadJSONFile(filename:str, path:Path = Path("./")) -> Dict[Any, Any]:
    if not filename.lower().endswith(".json"):
        Logger.Log(f"Got a filename that didn't end with .json: {filename}, appending .json", logging.DEBUG)
        filename = filename + ".json"
    # once we've validated inputs, try actual loading and reading.
    file_path = path / filename
    try:
        with open(file_path, "r") as json_file:
            return json.loads(json_file.read())
    except FileNotFoundError as err:
        Logger.Log(f"File {file_path} does not exist, trying to find within package.", logging.WARNING)
        print(f"File {file_path} does not exist, trying to find within package.")
        package_file_path = files(".".join(path.parts)).joinpath(filename)
        print(f"Loading json file based on path {path}/{filename}, within package the path will be '{package_file_path}'")
        try:
            with package_file_path.open() as json_file:
                return json.loads(json_file.read())
        except FileNotFoundError as err:
            Logger.Log(f"File {package_file_path} does not exist.", logging.WARNING)
            print(f"File {package_file_path} does not exist.")
            raise err
