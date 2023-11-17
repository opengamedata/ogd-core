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
from typing import Any, Dict, Optional, Set, Tuple

# import 3rd-party libraries

# import local files
from utils.Logger import Logger
from config.config import settings
from interfaces.DataInterface import DataInterface
from interfaces.CSVInterface import CSVInterface
from interfaces.MySQLInterface import MySQLInterface
from interfaces.BigQueryInterface import BigQueryInterface
from interfaces.BQFirebaseInterface import BQFirebaseInterface
from interfaces.outerfaces.DataOuterface import DataOuterface
from interfaces.outerfaces.TSVOuterface import TSVOuterface
from interfaces.outerfaces.DebugOuterface import DebugOuterface
from managers.ExportManager import ExportManager
from schemas.ExportMode import ExportMode
from schemas.IDMode import IDMode
from schemas.games.GameSchema import GameSchema
from schemas.tables.TableSchema import TableSchema
from schemas.configs.ConfigSchema import ConfigSchema
from schemas.configs.GameSourceSchema import GameSourceSchema
from ogd_requests.Request import Request, ExporterRange
from ogd_requests.RequestResult import RequestResult, ResultStatus
from utils.Logger import Logger
from utils.Readme import Readme

def ListGames() -> bool:
    print(f"The games available for export are:\n{games_list}")
    return True

def ShowGameInfo(config:ConfigSchema) -> bool:
    """Function to print out info on a game from the game's schema.
   This does a similar function to writeReadme, but is limited to the CSV metadata part
   (basically what was in the schema, at one time written into the csv's themselves).
   Further, the output is printed rather than written to file.

    :return: True if game metadata was successfully loaded and printed, or False if an error occurred
    :rtype: bool
    """
    try:
        game_schema = GameSchema(schema_name=f"{args.game}.json")
        table_schema = TableSchema(schema_name=f"{config.GameSourceMap[args.game].TableSchema}.json")
        readme = Readme(game_schema=game_schema, table_schema=table_schema)
        print(readme.CustomReadmeSource)
    except Exception as err:
        msg = f"Could not print information for {args.game}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        return True

def WriteReadme(config:ConfigSchema) -> bool:
    """Function to write out the readme file for a given game.
   This includes the CSV metadata (data from the schema, originally written into
   the CSV files themselves), custom readme source, and the global changelog.
   The readme is placed in the game's data folder.

    :return: _description_
    :rtype: bool
    """
    path = Path(f"./data") / args.game
    try:
        game_schema = GameSchema(schema_name=f"{args.game}.json")
        table_schema = TableSchema(schema_name=f"{config.GameSourceMap[args.game].TableSchema}.json")
        readme = Readme(game_schema=game_schema, table_schema=table_schema)
        readme.GenerateReadme(path=path)
    except Exception as err:
        msg = f"Could not create a readme for {args.game}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        Logger.Log(f"Successfully generated a readme for {args.game}.", logging.INFO)
        return True

def RunExport(config:ConfigSchema, with_events:bool = False, with_features:bool = False) -> bool:
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

    req = genRequest(config=config, with_events=with_events, with_features=with_features)
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

def genRequest(config:ConfigSchema, with_events:bool, with_features:bool) -> Request:
    export_modes   : Set[ExportMode]
    interface      : DataInterface
    range          : ExporterRange
    file_outerface : DataOuterface
    dataset_id     : Optional[str] = None

    # 1. get exporter modes to run
    export_modes = getModes(with_events=with_events, with_features=with_features)
    # 2. figure out the interface and range; optionally set a different dataset_id
    if args.file is not None and args.file != "":
        # raise NotImplementedError("Sorry, exports with file inputs are currently broken.")
        _ext = str(args.file).split('.')[-1]
        _cfg = GameSourceSchema(name="FILE SOURCE", all_elements={"schema":"OGD_EVENT_FILE"}, data_sources={})
        interface = CSVInterface(game_id=args.game, config=_cfg, fail_fast=config.FailFast, filepath=Path(args.file), delim="\t" if _ext == 'tsv' else ',')
        # retrieve/calculate id range.
        ids = interface.AllIDs()
        range = ExporterRange.FromIDs(source=interface, ids=ids if ids is not None else [])
    else:
        interface = genDBInterface(config=config)
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
    # 3. set up the outerface, based on the range and dataset_id.
    _cfg = GameSourceSchema(name="FILE DEST", all_elements={"database":"FILE", "table":"DEBUG", "schema":"OGD_EVENT_FILE"}, data_sources={})
    file_outerface = TSVOuterface(game_id=args.game, config=_cfg, export_modes=export_modes, date_range=range.DateRange,
                                  file_indexing=config.FileIndexConfig, dataset_id=dataset_id)
    outerfaces : Set[DataOuterface] = {file_outerface}
    # If we're in debug level of output, include a debug outerface, so we know what is *supposed* to go through the outerfaces.
    if config.DebugLevel == "DEBUG":
        _cfg = GameSourceSchema(name="DEBUG", all_elements={"database":"DEBUG", "table":"DEBUG", "schema":"OGD_EVENT_FILE"}, data_sources={})
        outerfaces.add(DebugOuterface(game_id=args.game, config=_cfg, export_modes=export_modes))

    # 4. Once we have the parameters parsed out, construct the request.
    return Request(range=range, exporter_modes=export_modes, interface=interface, outerfaces=outerfaces)

def genDBInterface(config:ConfigSchema) -> DataInterface:
    ret_val : DataInterface
    _game_cfg = config.GameSourceMap.get(args.game)
    if _game_cfg is not None and _game_cfg.Source is not None:
        match (_game_cfg.Source.Type):
            case "Firebase" | "FIREBASE":
                ret_val = BQFirebaseInterface(game_id=args.game, config=_game_cfg, fail_fast=config.FailFast)
            case "BigQuery" | "BIGQUERY":
                ret_val = BigQueryInterface(game_id=args.game, config=_game_cfg, fail_fast=config.FailFast)
            case "MySQL" | "MYSQL":
                ret_val = MySQLInterface(game_id=args.game, config=_game_cfg, fail_fast=config.FailFast)
            case _:
                raise Exception(f"{_game_cfg.Source.Type} is not a valid DataInterface type!")
        return ret_val
    else:
        raise ValueError(f"Config for {args.game} was invalid or not found!")

def getModes(with_events:bool, with_features:bool) -> Set[ExportMode]:
    ret_val = set()

    if with_events:
        ret_val.add(ExportMode.EVENTS)
        ret_val.add(ExportMode.DETECTORS)
    if with_features:
        if not args.no_session_file:
            ret_val.add(ExportMode.SESSION)
        if not args.no_player_file:
            ret_val.add(ExportMode.PLAYER)
        if not args.no_pop_file:
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
        end_date   = datetime.strptime(args.end_date, "%m/%d/%Y") if args.end_date is not None else start_date
        end_date = end_date.replace(hour=23, minute=59, second=59)
        Logger.Log(f"Exporting from {str(start_date)} to {str(end_date)} of data for {args.game}...", logging.INFO)
    return (start_date, end_date)

## This section of code is what runs main itself. Just need something to get it
#  started.
# Logger.Log(f"Running {sys.argv[0]}...", logging.INFO)
games_folder : Path = Path("./games")
config = ConfigSchema(name="config.py", all_elements=settings)
# set up parent parsers with arguments for each class of command
games_list = [name.upper() for name in os.listdir(games_folder) if (os.path.isdir(games_folder / name) and name != "__pycache__")]
game_parser = argparse.ArgumentParser(add_help=False)
game_parser.add_argument("game", type=str.upper, choices=games_list,
                    help="The game to use with the given command.")
export_parser = argparse.ArgumentParser(add_help=False, parents=[game_parser])
export_parser.add_argument("start_date", nargs="?", default=None,
                    help="The starting date of an export range in MM/DD/YYYY format (defaults to today).")
export_parser.add_argument("end_date", nargs="?", default=None,
                    help="The ending date of an export range in MM/DD/YYYY format (defaults to today).")
export_parser.add_argument("-p", "--player", default="",
                    help="Tell the program to output data for a player with given ID, instead of using a date range.")
export_parser.add_argument("-s", "--session", default="",
                    help="Tell the program to output data for a session with given ID, instead of using a date range.")
export_parser.add_argument("--player_id_file", default="",
                    help="Tell the program to output data for a collection of players with IDs in given file, instead of using a date range.")
export_parser.add_argument("--session_id_file", default="",
                    help="Tell the program to output data for a collection of sessions with IDs in given file, instead of using a date range.")
export_parser.add_argument("-f", "--file", default="",
                    help="Tell the program to use a file as input, instead of looking up a database.")
export_parser.add_argument("-m", "--monthly", default=False, action="store_true",
                    help="Set the program to export a month's-worth of data, instead of using a date range. Replace the start_date argument with a month in MM/YYYY format.")
# allow individual feature files to be skipped.
export_parser.add_argument("--no_session_file", default=False, action="store_true",
                    help="Tell the program to skip outputting a per-session file.")
export_parser.add_argument("--no_player_file", default=False, action="store_true",
                    help="Tell the program to skip outputting a per-player file.")
export_parser.add_argument("--no_pop_file", default=False, action="store_true",
                    help="Tell the program to skip outputting a population file.")
# set up main parser, with one sub-parser per-command.
parser = argparse.ArgumentParser(description="Simple command-line utility to execute OpenGameData export requests.")
sub_parsers = parser.add_subparsers(help="Chosen command to run", dest="command")
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

args : Namespace = parser.parse_args()

success : bool
if args is not None:
    cmd = (args.command or "help").lower()
    if cmd == "export":
        success = RunExport(config=config, with_events=True, with_features=True)
    elif cmd == "export-events":
        success = RunExport(config=config, with_events=True)
    elif cmd == "export-features":
        success = RunExport(config=config, with_features=True)
    elif cmd == "info":
        success = ShowGameInfo(config=config)
    elif cmd == "readme":
        success = WriteReadme(config=config)
    elif cmd == "list-games":
        success = ListGames()
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
