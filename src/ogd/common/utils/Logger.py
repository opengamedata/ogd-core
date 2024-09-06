import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals

class Logger:
    debug_level : int = logging.INFO
    std_logger  : logging.Logger   = logging.getLogger("std_logger")
    file_logger : Optional[logging.Logger] = None

    @staticmethod
    def InitializeLogger(level:int, use_logfile:bool):
        """Function to set up the stdout and file loggers of the Logging package.

        :param level: The logging level, which must be one of the levels defined by the Python `logging` package (`ERROR`, `WARN`, `INFO`, or `DEBUG`)
        :type level: int
        :param use_logfile: Bool for whether to use file output for logging or not.
        :type use_logfile: bool
        """
        # Set up loggers. First, the std out logger
        if not Logger.std_logger.hasHandlers():
            stdout_handler = logging.StreamHandler()
            Logger.std_logger.addHandler(stdout_handler)
            print("Added handler to std_logger")
        else:
            Logger.std_logger.warning(f"Trying to add a handler to std_logger, when handlers ({Logger.std_logger.handlers}) already exist!")
        _valid_levels = {logging.ERROR, logging.WARN, logging.WARNING, logging.INFO, logging.DEBUG}
        if level in _valid_levels:
            Logger.std_logger.setLevel(level=level)
        else:
            Logger.std_logger.setLevel(level=logging.INFO)
            Logger.std_logger.info("No valid logging level given, defaulting to INFO.")
        Logger.std_logger.info("Initialized standard out logger")

        # Then, set up the file logger. Check for permissions errors.
        if use_logfile:
            Logger.file_logger = logging.getLogger("file_logger")
            Logger.file_logger.setLevel(level=logging.DEBUG)
            # file_logger.setLevel(level=logging.DEBUG)
            try:
                err_handler = logging.FileHandler("./ExportErrorReport.log", encoding="utf-8")
                debug_handler = logging.FileHandler("./ExportDebugReport.log", encoding="utf-8")
            except PermissionError as err:
                Logger.std_logger.exception(f"Failed permissions check for log files. No file logging on server.")
            else:
                Logger.std_logger.info("Successfully set up logging files.")
                err_handler.setLevel(level=logging.WARNING)
                Logger.file_logger.addHandler(err_handler)
                debug_handler.setLevel(level=logging.DEBUG)
                Logger.file_logger.addHandler(debug_handler)
            finally:
                Logger.file_logger.debug("Initialized file logger")
    
    # Function to print a method to both the standard out and file logs.
    # Useful for "general" errors where you just want to print out the exception from a "backstop" try-catch block.
    @staticmethod
    def Log(message:str, level=logging.INFO, depth:int=0) -> None:
        now = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        indent = ''.join(['  '*depth])
        _idt_msg = message.replace("\n", f"\n{' '*9}{indent}")
        if Logger.file_logger is not None:
            match level:
                case logging.DEBUG:
                    Logger.file_logger.debug(f"DEBUG:   {now} {indent}{_idt_msg}")
                case logging.INFO:
                    Logger.file_logger.info( f"INFO:    {now} {indent}{_idt_msg}")
                case logging.WARNING:
                    Logger.file_logger.warning( f"WARNING: {now} {indent}{_idt_msg}")
                case logging.ERROR:
                    Logger.file_logger.error(f"ERROR:   {now} {indent}{_idt_msg}")
        if Logger.std_logger is not None:
            match level:
                case logging.DEBUG:
                    Logger.std_logger.debug(f"DEBUG:   {indent}{_idt_msg}")
                case logging.INFO:
                    Logger.std_logger.info( f"INFO:    {indent}{_idt_msg}")
                case logging.WARNING:
                    Logger.std_logger.warning( f"WARNING: {indent}{_idt_msg}")
                case logging.ERROR:
                    Logger.std_logger.error(f"ERROR:   {indent}{_idt_msg}")

    @staticmethod
    def Print(message:str, level=logging.DEBUG) -> None:
        match level:
            case logging.DEBUG:
                print(f"debug:   {message}")
            case logging.INFO:
                print(f"info:    {message}")
            case logging.WARNING:
                print(f"warning: {message}")
            case logging.ERROR:
                print(f"error:   {message}")
