# import standard libraries
import cProfile
#import datetime
import argparse
import csv
import logging
import os
import sys
import traceback
from argparse import Namespace
from calendar import monthrange
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import List, Optional, Set, Tuple

# import 3rd-party libraries

# import local files
from utils.Logger import Logger
from config.config import settings
from interfaces.events.EventInterface import EventInterface
from interfaces.events.CSVInterface import CSVInterface
from interfaces.events.MySQLInterface import MySQLInterface
from interfaces.events.BigQueryInterface import BigQueryInterface
from interfaces.events.BQFirebaseInterface import BQFirebaseInterface
from interfaces.outerfaces.DataOuterface import DataOuterface
from interfaces.outerfaces.TSVOuterface import TSVOuterface
from interfaces.outerfaces.DebugOuterface import DebugOuterface
from interfaces.outerfaces.MySQLOuterface import MySQLOuterface
from managers.ExportManager import ExportManager
from schemas.ExportMode import ExportMode
from schemas.IDMode import IDMode
from schemas.games.GameSchema import GameSchema
from schemas.tables.EventTableSchema import EventTableSchema
from schemas.configs.ConfigSchema import ConfigSchema
from schemas.data_sources.GameSourceSchema import GameSourceSchema
from ogd_requests.Request import Request, ExporterRange
from ogd_requests.RequestResult import RequestResult, ResultStatus
from utils.Logger import Logger
from utils.Readme import Readme

def GetGameParser() -> argparse.ArgumentParser:
    """Function to set up a simple argument parser to retrieve the 'game' argument

    :return: An ArgumentParser that yields the 'game' command-line argument.
    :rtype: argparse.ArgumentParser
    """
    ret_val = argparse.ArgumentParser(add_help=False)
    ret_val.add_argument("game", type=str.upper, choices=games_list,
                        help="The game to use with the given command.")
    return ret_val

def GetExportParser() -> argparse.ArgumentParser:
    """Function to set up a simple argument parser to retrieve the command-line arguments pertaining to date range and optional inputs

    :return: An ArgumentParser that yields the start_date, end_date, and optional command-line arguments.
    :rtype: argparse.ArgumentParser
    """
    ret_val = argparse.ArgumentParser(add_help=False, parents=[game_parser])
    ret_val.add_argument("start_date", nargs="?", default=None,
                        help="The starting date of an export range in MM/DD/YYYY format (defaults to today).")
    ret_val.add_argument("end_date", nargs="?", default=None,
                        help="The ending date of an export range in MM/DD/YYYY format (defaults to today).")
    ret_val.add_argument("-f", "--file", default="",
                        help="Tell the program to use a file as input, instead of looking up a database.")
    ret_val.add_argument("-m", "--monthly", default=False, action="store_true",
                        help="Set the program to export a month's-worth of data, instead of using a date range. Replace the start_date argument with a month in MM/YYYY format.")
    ret_val.add_argument("-d", "--to_database", default=False, action="store_true",
                        help="Set the program to export data to the database in the game_destinations config, in addition to any file export.")
    # allow specifying only certain players/sessions for export
    ret_val.add_argument("-p", "--player", default="",
                        help="Tell the program to output data for a player with given ID, instead of using a date range.")
    ret_val.add_argument("-s", "--session", default="",
                        help="Tell the program to output data for a session with given ID, instead of using a date range.")
    ret_val.add_argument("--player_id_file", default="",
                        help="Tell the program to output data for a collection of players with IDs in given file, instead of using a date range.")
    ret_val.add_argument("--session_id_file", default="",
                        help="Tell the program to output data for a collection of sessions with IDs in given file, instead of using a date range.")
    # allow individual feature files to be skipped.
    ret_val.add_argument("--no_files", default=False, action="store_true",
                        help="Tell the program to skip outputting any files from the export (useful if exporting exclusively to database).")
    ret_val.add_argument("--no_session_output", "--no_session_file", default=False, action="store_true",
                        help="Tell the program to skip outputting a per-session file/database entries.")
    ret_val.add_argument("--no_player_output", "--no_player_file", default=False, action="store_true",
                        help="Tell the program to skip outputting a per-player file/database_entries.")
    ret_val.add_argument("--no_pop_output", "--no_pop_file", default=False, action="store_true",
                        help="Tell the program to skip outputting a population file/database_entries.")
    return ret_val

# set up main parser, with one sub-parser per-command.
def GetMainParser(game_parser:argparse.ArgumentParser, export_parser:argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Function to set up a an argument parser (with subparsers) to retrieve the export commands from the command-line arguments.

    :param export_parser: An ArgumentParser for export commands, which will be parented to appropriate subparsers
    :type export_parser: argparse.ArgumentParser
    :param game_parser: An ArgumentParser for game commands, which will be parented to appropriate subparsers
    :type game_parser: argparse.ArgumentParser
    :return: An ArgumentParser that yields the export commands.
    :rtype: argparse.ArgumentParser
    """
    ret_val = argparse.ArgumentParser(description="Simple command-line utility to execute OpenGameData export requests.")
    sub_parsers = ret_val.add_subparsers(help="Chosen command to run", dest="command")
    sub_parsers.add_parser("export", parents=[export_parser],
                            help="Export data in a given date range.")
    sub_parsers.add_parser("export-events", parents=[export_parser],
                            help="Export event data in a given date range.")
    sub_parsers.add_parser("export-features", parents=[export_parser],
                            help="Export session feature data in a given date range.")
    sub_parsers.add_parser("info", parents=[game_parser],
                            help="Display info about the given game.")
    sub_parsers.add_parser("readme", parents=[game_parser],
                            help="Generate a readme for the given game.")
    sub_parsers.add_parser("list-games",
                            help="Display a list of games available for parsing.")
    # sub_parsers.add_parser("help",
    #                         help="Display a list of games available for parsing.")
    return ret_val

def ListGames(games_list:List[str]) -> bool:
    print(f"The games available for export are:\n{games_list}")
    return True

def ShowGameInfo(game_id:str, config:ConfigSchema) -> bool:
    """Function to print out info on a game from the game's schema.
   This does a similar function to writeReadme, but is limited to the CSV metadata part
   (basically what was in the schema, at one time written into the csv's themselves).
   Further, the output is printed rather than written to file.

    :return: True if game metadata was successfully loaded and printed, or False if an error occurred
    :rtype: bool
    """
    try:
        game_schema = GameSchema(schema_name=f"{game_id}.json")
        table_schema = EventTableSchema(schema_name=f"{config.GameSourceMap[game_id].EventTableSchema}.json")
        readme = Readme(game_schema=game_schema, table_schema=table_schema)
        print(readme.CustomReadmeSource)
    except Exception as err:
        msg = f"Could not print information for {game_id}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        return True

def WriteReadme(game_id:str, config:ConfigSchema) -> bool:
    """Function to write out the readme file for a given game.
   This includes the CSV metadata (data from the schema, originally written into
   the CSV files themselves), custom readme source, and the global changelog.
   The readme is placed in the game's data folder.

    :return: _description_
    :rtype: bool
    """
    path = Path(f"./data") / game_id
    try:
        game_schema = GameSchema(schema_name=f"{args.game}.json")
        table_schema = EventTableSchema(schema_name=f"{config.GameSourceMap[game_id].EventTableSchema}.json")
        readme = Readme(game_schema=game_schema, table_schema=table_schema)
        readme.GenerateReadme(path=path)
    except Exception as err:
        msg = f"Could not create a readme for {game_id}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        Logger.Log(f"Successfully generated a readme for {game_id}.", logging.INFO)
        return True

def RunExport(game_id:str, config:ConfigSchema, with_events:bool = False, with_features:bool = False) -> bool:
    """Function to handle execution of export code.
    This is the main intended use of the program.

    :param events: _description_, defaults to False
    :type events: bool, optional
    :param features: _description_, defaults to False
    :type features: bool, optional
    :return: _description_
    :rtype: bool
    """
    success : bool = False

    req = genRequest(game_id=game_id, config=config, with_events=with_events, with_features=with_features)
    if req.Interface.IsOpen():
        export_manager : ExportManager = ExportManager(config=config)
        result         : RequestResult = export_manager.ExecuteRequest(request=req)
        success = result.Status == ResultStatus.SUCCESS
        level = logging.INFO if success else logging.ERROR
        Logger.Log(message=result.Message, level=level)
        Logger.Log(f"Total data request execution time: {result.Duration}", logging.INFO)
        # cProfile.runctx("feature_exporter.ExportFromSQL(request=req)",
                        # {'req':req, 'feature_exporter':feature_exporter}, {})
    return success

def genRequest(game_id:str, config:ConfigSchema, with_events:bool, with_features:bool) -> Request:
    export_modes   : Set[ExportMode]
    interface      : EventInterface
    range          : ExporterRange
    dataset_id     : Optional[str]

    # 1. get exporter modes to run
    export_modes = getModes(with_events=with_events, with_features=with_features)
    # 2. figure out the interface and range; optionally set a different dataset_id
    interface, range, dataset_id = genInterface(game_id=game_id)
    # 3. set up the outerface, based on the range and dataset_id.
    outerfaces : Set[DataOuterface] = set()
    if not args.no_files:
        _cfg = GameSourceSchema(name="FILE DEST", all_elements={"SCHEMA":"OGD_EVENT_FILE", "DB_TYPE":"FILE"}, data_sources={})
        outerfaces.add(TSVOuterface(game_id=game_id, config=_cfg, export_modes=export_modes, date_range=range.DateRange,
                                  file_indexing=config.FileIndexConfig, dataset_id=dataset_id))
    else:
        Logger.Log(f"Found command-line option disabling file output; all file outputs will be skipped")
    if args.to_database:
        _cfg = config.GameDestinationMap.get(game_id)
        outerfaces.add(MySQLOuterface(game_id=game_id, config=_cfg, export_modes=export_modes))
    # If we're in debug level of output, include a debug outerface, so we know what is *supposed* to go through the outerfaces.
    if config.DebugLevel == "DEBUG":
        _cfg = GameSourceSchema(name="DEBUG", all_elements={"SCHEMA":"OGD_DEBUG_OUTPUT", "DB_TYPE":"FILE"}, data_sources={})
        outerfaces.add(DebugOuterface(game_id=game_id, config=_cfg, export_modes=export_modes))

    # 4. Once we have the parameters parsed out, construct the request.
    return Request(range=range, exporter_modes=export_modes, interface=interface, outerfaces=outerfaces)

def genInterface(game_id:str) -> Tuple[EventInterface, ExporterRange, Optional[str]]:
    ret_val : Tuple[EventInterface, ExporterRange, Optional[str]]

    interface   : EventInterface
    range       : ExporterRange
    dataset_id  : Optional[str] = None
    if args.file is not None and args.file != "":
        # raise NotImplementedError("Sorry, exports with file inputs are currently broken.")
        _ext = str(args.file).split('.')[-1]
        _cfg = GameSourceSchema(name="FILE SOURCE", all_elements={"schema":"OGD_EVENT_FILE"}, data_sources={})
        interface = CSVInterface(game_id=game_id, config=_cfg, fail_fast=config.FailFast, filepath=Path(args.file), delim="\t" if _ext == 'tsv' else ',')
        # retrieve/calculate id range.
        ids = interface.AllIDs()
        range = ExporterRange.FromIDs(source=interface, ids=ids if ids is not None else [])
    else:
        interface = genDBInterface(game_id=game_id, config=config)
        if args.player is not None and args.player != "":
            range = ExporterRange.FromIDs(source=interface, ids=[args.player], id_mode=IDMode.USER)
            dataset_id = f"{args.game}_{args.player}"
        elif args.player_id_file is not None and args.player_id_file != "":
            file_path = Path(args.player_id_file)
            with open(file_path) as player_file:
                reader = csv.reader(player_file)
                file_contents = list(reader) # this gives list of lines, each line a list
                names = list(chain.from_iterable(file_contents)) # so, convert to single list
                print(f"list of names: {list(names)}")
                range = ExporterRange.FromIDs(source=interface, ids=names, id_mode=IDMode.USER)
        elif args.session is not None and args.session != "":
            range = ExporterRange.FromIDs(source=interface, ids=[args.session], id_mode=IDMode.SESSION)
            dataset_id = f"{args.game}_{args.session}"
        elif args.session_id_file is not None and args.session_id_file != "":
            file_path = Path(args.session_id_file)
            with open(file_path) as session_file:
                reader = csv.reader(session_file)
                file_contents = list(reader) # this gives list of lines, each line a list
                names = list(chain.from_iterable(file_contents)) # so, convert to single list
                print(f"list of sessions: {list(names)}")
                range = ExporterRange.FromIDs(source=interface, ids=names, id_mode=IDMode.SESSION)
        else:
            start_date, end_date = getDateRange()
            range = ExporterRange.FromDateRange(source=interface, date_min=start_date, date_max=end_date)
    ret_val = (interface, range, dataset_id)
    return ret_val

def genDBInterface(game_id:str, config:ConfigSchema) -> EventInterface:
    ret_val : EventInterface
    _game_cfg = config.GameSourceMap.get(game_id)
    if _game_cfg is not None and _game_cfg.DataHost is not None:
        match (_game_cfg.DataHost.Type):
            case "Firebase" | "FIREBASE":
                ret_val = BQFirebaseInterface(game_id=game_id, config=_game_cfg, fail_fast=config.FailFast)
            case "BigQuery" | "BIGQUERY":
                ret_val = BigQueryInterface(game_id=game_id, config=_game_cfg, fail_fast=config.FailFast)
            case "MySQL" | "MYSQL":
                ret_val = MySQLInterface(game_id=game_id, config=_game_cfg, fail_fast=config.FailFast)
            case _:
                raise Exception(f"{_game_cfg.DataHost.Type} is not a valid EventInterface type!")
        return ret_val
    else:
        raise ValueError(f"Config for {args.game} was invalid or not found!")

def getModes(with_events:bool, with_features:bool) -> Set[ExportMode]:
    ret_val = set()

    if with_events:
        ret_val.add(ExportMode.EVENTS)
        ret_val.add(ExportMode.DETECTORS)
    if with_features:
        if not (args.no_session_output or args.no_session_file):
            ret_val.add(ExportMode.SESSION)
        if not (args.no_player_output or args.no_player_file):
            ret_val.add(ExportMode.PLAYER)
        if not (args.no_pop_output or args.no_pop_file):
            ret_val.add(ExportMode.POPULATION)

    return ret_val
    
# retrieve/calculate date range.
def getDateRange() -> Tuple[datetime, datetime]:
    start_date: datetime
    end_date  : datetime
    today     : datetime = datetime.now()
    # If we want to export all data for a given month, calculate a date range.
    if args.monthly:
        month: int = today.month
        year:  int = today.year
        month_year = args.start_date.split("/")
        month = int(month_year[0])
        year  = int(month_year[1])
        month_range = monthrange(year, month)
        days_in_month = month_range[1]
        start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
        end_date   = datetime(year=year, month=month, day=days_in_month, hour=23, minute=59, second=59)
        Logger.Log(f"Exporting {month}/{year} data for {args.game}...", logging.DEBUG)
    # Otherwise, create date range from given pair of dates.
    else:
        start_date = datetime.strptime(args.start_date, "%m/%d/%Y") if args.start_date is not None else today
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date   = datetime.strptime(args.end_date, "%m/%d/%Y") if args.end_date is not None else today
        end_date = end_date.replace(hour=23, minute=59, second=59)
        Logger.Log(f"Exporting from {str(start_date)} to {str(end_date)} of data for {args.game}...", logging.INFO)
    return (start_date, end_date)

## This section of code is what runs main itself. Just need something to get it started.
# Logger.Log(f"Running {sys.argv[0]}...", logging.INFO)
config : ConfigSchema = ConfigSchema(name="config.py", all_elements=settings)
games_folder : Path   = Path("./games")
games_list = [name.upper() for name in os.listdir(games_folder) if (os.path.isdir(games_folder / name) and name != "__pycache__")]

# set up parent parsers with arguments for each class of command
game_parser   = GetGameParser()
export_parser = GetExportParser()
parser        = GetMainParser(game_parser=game_parser, export_parser=export_parser)
args : Namespace = parser.parse_args()

success : bool
if args is not None:
    cmd = args.command.lower()
    game_id = args.game.upper()
    if cmd == "export":
        success = RunExport(game_id=game_id, config=config, with_events=True, with_features=True)
    elif cmd == "export-events":
        success = RunExport(game_id=game_id, config=config, with_events=True)
    elif cmd == "export-features":
        success = RunExport(game_id=game_id, config=config, with_features=True)
    elif cmd == "info":
        success = ShowGameInfo(game_id=game_id, config=config)
    elif cmd == "readme":
        success = WriteReadme(game_id=game_id, config=config)
    elif cmd == "list-games":
        success = ListGames(games_list=games_list)
    # elif cmd == "help":
    #     success = ShowHelp()
    else:
        print(f"Invalid Command {cmd}!")
        success = False
else:
    print(f"Need to enter a command!")
    success = False
if not success:
    sys.exit(1)
