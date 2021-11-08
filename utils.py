## @namespace utils
#  A module of utility functions used in the feature_extraction_to_csv project
import datetime
import json
import logging
import os
import traceback
import typing
from typing import Dict, List
from pathlib import Path
# local imports
from config.config import core_settings
from schemas.GameSchema import GameSchema

## Function to open a given JSON file, and retrieve the data as a Python object.
#  @param filename  The name of the JSON file. If the file extension is not .json,
#                       then ".json" will be appended.
#  @param path      The path (relative or absolute) to the folder containing the
#                       JSON file. If path does not end in /, then "/" will be appended.
#  @return          A python object parsed from the JSON.
def loadJSONFile(filename:str, path:Path = Path("./")) -> typing.Any:
    if not filename.lower().endswith(".json"):
        Logger.toStdOut(f"Got a filename that didn't end with .json: {filename}, appending .json", logging.DEBUG)
        filename = filename + ".json"
    # once we've validated inputs, try actual loading and reading.
    file_path = path / filename
    try:
        with open(file_path, "r") as json_file:
            return json.loads(json_file.read())
    except FileNotFoundError as err:
        Logger.toStdOut(f"File {file_path} does not exist.", logging.WARNING)
        raise err
    except Exception as err:
        Logger.toStdOut(f"Could not read file at {file_path}\nFull error message: {type(err)} {str(err)}\nCurrent directory: {os.getcwd()}",
                        logging.ERROR)
        raise err

def GenerateReadme(game_name:str, game_schema:GameSchema, column_list:List[Dict[str,str]], path:Path = Path("./")):
    try:
        os.makedirs(name=path, exist_ok=True)
        with open(path / "readme.md", "w") as readme:
            # 1. Open files with game-specific readme data, and global db changelog.
            source_dir = Path("./doc/readme_src/")
            try:
                with open(source_dir / f"{game_name}_readme_src.md", "r") as readme_src:
                    readme.write(readme_src.read())
            except FileNotFoundError as err:
                readme.write("No readme prepared")
                Logger.toStdOut(f"Could not find readme_src for {game_name}", logging.WARNING)
            finally:
                readme.write("\n")
            # 2. Use schema to write feature & column descriptions to the readme.
            feature_descriptions = {**game_schema.perlevel_features(), **game_schema.aggregate_features()}
            meta = GenCSVMetadata(game_name=game_name, column_list=column_list, feature_list=feature_descriptions)
            readme.write(meta)
            # 3. Append any important data from the data changelog.
            try:
                with open(source_dir / "changelog_src.md", "r") as changelog_src:
                    readme.write(changelog_src.read())
            except FileNotFoundError as err:
                readme.write("No changelog prepared")
                Logger.toStdOut(f"Could not find changelog_src", logging.WARNING)
    except FileNotFoundError as err:
        Logger.Log(f"Could not open readme.md for writing.", logging.ERROR)
        traceback.print_tb(err.__traceback__)
    except Exception as err:
        msg = f"{type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)

def GenCSVMetadata(game_name: str, column_list: List[Dict[str,str]], feature_list: Dict[str,str]) -> str:
    """Function to generate metadata for a given game.
    The "fields" are a sort of generalization of columns. Basically, columns which
    are repeated (say, once per level) all fall under a single field.
    Columns which are completely unique correspond to individual fields.

    :param game_name: The name of the game for which the csv metadata is being generated.
    :type game_name: str
    :param raw_field_list: A mapping of raw csv "fields" to descriptions of the fields.
    :type raw_field_list: List[Dict[str,str]]
    :param sessions_field_list: A mapping of session csv features to descriptions of the features.
    :type sessions_field_list: Dict[str,str]
    :return: A string containing metadata for the given game.
    :rtype: str
    """
    raw_field_descriptions = [f"{col['readable']} ({col['name']}) : {col['type']} - {col['desc']}" for col in column_list]
    sessions_field_descriptions = [f"{key} - {feature_list[key]}" for key in feature_list.keys()]
    raw_field_string = "\n".join(raw_field_descriptions)
    sessions_field_string = "\n".join(sessions_field_descriptions)
    template_str =\
    "\n".join(["## Field Day Open Game Data",
    "### Retrieved from https://fielddaylab.wisc.edu/opengamedata",
    "### These anonymous data are provided in service of future educational data mining research.",
    "### They are made available under the Creative Commons CCO 1.0 Universal license.",
    "### See https://creativecommons.org/publicdomain/zero/1.0/",
    "",
    "## Suggested citation:",
    "### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://fielddaylab.wisc.edu/opengamedata",
    "",
    f"## Game: {game_name}",
    "",
    "## Field Descriptions:",
    "### Raw CSV Columns:",
    f"{raw_field_string}",
    "",
    "### Processed Session Features:",
    f"{sessions_field_string}",
    ""])
    return template_str

class Logger:
    # Set up loggers. First, the std out logger
    std_logger = logging.getLogger("std_logger")
    stdout_handler = logging.StreamHandler()
    std_logger.addHandler(stdout_handler)
    if settings['DEBUG_LEVEL'] == "ERROR":
        std_logger.setLevel(level=logging.ERROR)
    elif settings['DEBUG_LEVEL'] == "WARNING":
        std_logger.setLevel(level=logging.WARNING)
    elif settings['DEBUG_LEVEL'] == "INFO":
        std_logger.setLevel(level=logging.INFO)
    elif settings['DEBUG_LEVEL'] == "DEBUG":
        std_logger.setLevel(level=logging.DEBUG)
    std_logger.debug("Testing standard out logger")

    # Then, set up the file logger. Check for permissions errors.
    file_logger = logging.getLogger("file_logger")
    file_logger.setLevel(level=logging.DEBUG)
    # file_logger.setLevel(level=logging.DEBUG)
    try:
        err_handler = logging.FileHandler("ExportErrorReport.log", encoding="utf-8")
        debug_handler = logging.FileHandler("ExportDebugReport.log", encoding="utf-8")
    except PermissionError as err:
        std_logger.exception(f"Failed permissions check for log files. No file logging on server.", stack_info=False)
    else:
        std_logger.info("Successfully set up logging files.")
        err_handler.setLevel(level=logging.WARNING)
        file_logger.addHandler(err_handler)
        debug_handler.setLevel(level=logging.DEBUG)
        file_logger.addHandler(debug_handler)
    finally:
        file_logger.debug("Testing file logger")

    @staticmethod
    def toFile(message:str, level=logging.DEBUG) -> None:
        now = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        if Logger.file_logger is not None:
            if level == logging.DEBUG:
                Logger.file_logger.debug(f"DEBUG:   {now} {message}")
            elif level == logging.INFO:
                Logger.file_logger.info( f"INFO:    {now} {message}")
            elif level == logging.WARNING:
                Logger.file_logger.warn( f"WARNING: {now} {message}")
            elif level == logging.ERROR:
                Logger.file_logger.error(f"ERROR:   {now} {message}")

    @staticmethod
    def toStdOut(message:str, level=logging.DEBUG) -> None:
        if Logger.std_logger is not None:
            if level == logging.DEBUG:
                Logger.std_logger.debug(f"DEBUG:   {message}")
            elif level == logging.INFO:
                Logger.std_logger.info( f"INFO:    {message}")
            elif level == logging.WARNING:
                Logger.std_logger.warn( f"WARNING: {message}")
            elif level == logging.ERROR:
                Logger.std_logger.error(f"ERROR:   {message}")
    
    # Function to print a method to both the standard out and file logs.
    # Useful for "general" errors where you just want to print out the exception from a "backstop" try-catch block.
    @staticmethod
    def Log(message:str, level=logging.DEBUG) -> None:
        Logger.toFile(message, level)
        Logger.toStdOut(message, level)

    @staticmethod
    def toPrint(message:str, level=logging.DEBUG) -> None:
        if level == logging.DEBUG:
            print(f"debug:   {message}")
        elif level == logging.INFO:
            print(f"info:    {message}")
        elif level == logging.WARNING:
            print(f"warning: {message}")
        elif level == logging.ERROR:
            print(f"error:   {message}")
