## @namespace utils
#  A module of utility functions used in the feature_extraction_to_csv project
import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
# local imports
from config.config import settings as settings

## Function to open a given JSON file, and retrieve the data as a Python object.
#  @param filename  The name of the JSON file. If the file extension is not .json,
#                       then ".json" will be appended.
#  @param path      The path (relative or absolute) to the folder containing the
#                       JSON file. If path does not end in /, then "/" will be appended.
#  @return          A python object parsed from the JSON.
def loadJSONFile(filename:str, path:Path = Path("./")) -> Dict[Any, Any]:
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
        print(f"File {file_path} does not exist.")
        raise err
    except Exception as err:
        Logger.toStdOut(f"Could not read file at {file_path}\nFull error message: {type(err)} {str(err)}\nCurrent directory: {os.getcwd()}",
                        logging.ERROR)
        raise err

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
        now = datetime.now().strftime("%y-%m-%d %H:%M:%S")
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
