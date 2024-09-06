## @namespace utils
#  A module of utility functions used in the feature_extraction_to_csv project
import json
import logging
import os
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals
from ogd.core.utils.Logger import Logger

map = Dict[str, Any]
ExportRow = List[Any]

## Function to open a given JSON file, and retrieve the data as a Python object.
def loadJSONFile(filename:str, path:Path = Path("./"), search_in_src:bool = False, autocorrect_extension:bool = True) -> Dict[str, Any]:
    """Function to open a given JSON file, and retrieve the data as a Python object.

    :param filename: The name of the JSON file. If the file extension is not .json, then ".json" will be appended.
    :type filename: str
    :param path: The path (relative or absolute) to the folder containing the JSON file. Defaults to Path("./")
    :type path: Path, optional
    :param search_in_src: When True, prepends "src" to the path when searching for file directly, defaults to False
    :type search_in_src: bool, optional
    :param autocorrect_extension: When False, overrides default behavior and will not append .json to a filename with other extension, defaults to True
    :type autocorrect_extension: bool, optional
    :raises err: _description_
    :return: A python object parsed from the JSON.
    :rtype: Dict[Any, Any]
    """
    if autocorrect_extension and not filename.lower().endswith(".json"):
        Logger.Log(f"Got a filename that didn't end with .json: {filename}, appending .json", logging.DEBUG)
        filename = filename + ".json"
    # once we've validated inputs, try actual loading and reading.
    file_path = Path("src") / path / filename if search_in_src else path / filename
    try:
        with open(file_path, "r") as json_file:
            return json.loads(json_file.read())
    except FileNotFoundError as err:
        Logger.Log(f"Could not load JSON file, {file_path} could not be found from {os.getcwd()}, trying to find within package.", logging.WARNING)
        package_file_path = None
        try:
            package_file_path = files(".".join(path.parts)).joinpath(filename)
            with package_file_path.open() as json_file:
                return json.loads(json_file.read())
        except ModuleNotFoundError as err:
            Logger.Log(f"Could not load JSON file, unable to search in module for {path}, got the following error:\n{err.msg}.", logging.WARNING)
            raise err
        except FileNotFoundError as err:
            Logger.Log(f"Could not load JSON file from package, {package_file_path} does not exist.", logging.WARNING)
            raise err
