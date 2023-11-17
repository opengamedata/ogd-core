## @namespace utils
#  A module of utility functions used in the feature_extraction_to_csv project
import json
import logging
import itertools
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals
from utils.Logger import Logger

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
        Logger.Log(f"File {file_path} does not exist.", logging.WARNING)
        raise err


def GetAqualabJobCount(db_export_path:Path=Path("./games/AQUALAB/")):
    db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    return len(db_export.get("jobs", []))

def GetAqualabTaskCount(db_export_path:Path=Path("./games/AQUALAB/")):
    db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    list_o_lists = [job.get('tasks', []) for job in db_export.get('jobs', [])]
    # jobs_to_task_cts = [f"{job.get('id')}: {len(job.get('tasks', []))}" for job in db_export.get('jobs', [])]
    # Logger.Log(f"Task counts by job:\n{jobs_to_task_cts}", logging.DEBUG)
    all_tasks    = list(itertools.chain.from_iterable(list_o_lists))
    return len(all_tasks)