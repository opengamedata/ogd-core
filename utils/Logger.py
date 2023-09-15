import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals
from config.config import settings as settings

class Logger:
    std_logger  : logging.Logger   = logging.getLogger("std_logger")
    file_logger : Optional[logging.Logger] = None

    # Set up loggers. First, the std out logger
    if not std_logger.hasHandlers():
        stdout_handler = logging.StreamHandler()
        std_logger.addHandler(stdout_handler)
    else:
        std_logger.warning(f"Trying to add a handler to std_logger, when handlers ({std_logger.handlers}) already exist!")
    if settings['DEBUG_LEVEL'] == "ERROR":
        std_logger.setLevel(level=logging.ERROR)
    elif settings['DEBUG_LEVEL'] == "WARNING":
        std_logger.setLevel(level=logging.WARNING)
    elif settings['DEBUG_LEVEL'] == "INFO":
        std_logger.setLevel(level=logging.INFO)
    elif settings['DEBUG_LEVEL'] == "DEBUG":
        std_logger.setLevel(level=logging.DEBUG)
    std_logger.info("Testing standard out logger")

    # Then, set up the file logger. Check for permissions errors.
    if settings.get('LOG_FILE', False):
        file_logger = logging.getLogger("file_logger")
        file_logger.setLevel(level=logging.DEBUG)
        # file_logger.setLevel(level=logging.DEBUG)
        try:
            err_handler = logging.FileHandler("./ExportErrorReport.log", encoding="utf-8")
            debug_handler = logging.FileHandler("./ExportDebugReport.log", encoding="utf-8")
        except PermissionError as err:
            std_logger.exception(f"Failed permissions check for log files. No file logging on server.")
        else:
            std_logger.info("Successfully set up logging files.")
            err_handler.setLevel(level=logging.WARNING)
            file_logger.addHandler(err_handler)
            debug_handler.setLevel(level=logging.DEBUG)
            file_logger.addHandler(debug_handler)
        finally:
            file_logger.debug("Testing file logger")
    
    # Function to print a method to both the standard out and file logs.
    # Useful for "general" errors where you just want to print out the exception from a "backstop" try-catch block.
    @staticmethod
    def Log(message:str, level=logging.DEBUG, depth:int=0) -> None:
        now = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        indent = ''.join(['  '*depth])
        if Logger.file_logger is not None:
            if level == logging.DEBUG:
                Logger.file_logger.debug(f"DEBUG:   {now} {indent}{message}")
            elif level == logging.INFO:
                Logger.file_logger.info( f"INFO:    {now} {indent}{message}")
            elif level == logging.WARNING:
                Logger.file_logger.warn( f"WARNING: {now} {indent}{message}")
            elif level == logging.ERROR:
                Logger.file_logger.error(f"ERROR:   {now} {indent}{message}")
        if Logger.std_logger is not None:
            if level == logging.DEBUG:
                Logger.std_logger.debug(f"DEBUG:   {indent}{message}")
            elif level == logging.INFO:
                Logger.std_logger.info( f"INFO:    {indent}{message}")
            elif level == logging.WARNING:
                Logger.std_logger.warn( f"WARNING: {indent}{message}")
            elif level == logging.ERROR:
                Logger.std_logger.error(f"ERROR:   {indent}{message}")

    @staticmethod
    def Print(message:str, level=logging.DEBUG) -> None:
        if level == logging.DEBUG:
            print(f"debug:   {message}")
        elif level == logging.INFO:
            print(f"info:    {message}")
        elif level == logging.WARNING:
            print(f"warning: {message}")
        elif level == logging.ERROR:
            print(f"error:   {message}")
