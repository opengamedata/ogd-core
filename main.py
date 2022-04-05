# import standard libraries
import cProfile
#import datetime
import argparse
import logging
import os
import sys
import traceback
from argparse import Namespace
from calendar import monthrange
from datetime import datetime
from pathlib import Path
from typing import Tuple
from git.remote import FetchInfo

# import local files
import utils
from config.config import settings as settings
from interfaces.DataInterface import DataInterface
from interfaces.CSVInterface import CSVInterface
from interfaces.MySQLInterface import MySQLInterface
from interfaces.BigQueryInterface import BigQueryInterface
from managers.ExportManager import ExportManager
from managers.FileManager import FileManager
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from schemas.Request import Request, ExporterTypes, ExporterRange
from utils import Logger

## Function to print a "help" listing for the export tool.
#  Hopefully not needed too often, if at all.
#  Just nice to have on hand, in case we ever need it.
# def ShowHelp() -> bool:
#     width = 30
#     print(width*"*")
#     print("usage: <python> main.py <cmd> [<args>] [<opt-args>]")
#     print("")
#     print("<python> is your python command.")
#     print("<cmd>    is one of the available commands:")
#     print("         - export")
#     print("         - export-events")
#     print("         - export-session-features")
#     print("         - info")
#     print("         - readme")
#     print("         - help")
#     print("[<args>] are the arguments for the command:")
#     print("         - export: game_id, [start_date, end_date]")
#     print("             game_id    = id of game to export")
#     print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
#     print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
#     print("         - export-events: game_id")
#     print("             game_id    = id of game to export")
#     print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
#     print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
#     print("         - export-session-features: game_id, [month_year]")
#     print("             game_id    = id of game to export")
#     print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
#     print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
#     print("         - info: game_id")
#     print("             game_id    = id of game whose info should be shown")
#     print("         - readme: game_id")
#     print("             game_id    = id of game whose readme should be generated")
#     print("         - help: *None*")
#     print("[<opt-args>] are optional arguments, which affect certain commands:")
#     print("         --file: specifies a file to export events or features")
#     print("         --monthly: with this flag, specify dates by mm/yyyy instead of mm/dd/yyyy.")
#     print(width*"*")
#     return True

def ListGames() -> bool:
    print(f"The games available for export are:\n{games_list}")
    return True

## Function to print out info on a game from the game's schema.
#  This does a similar function to writeReadme, but is limited to the CSV
#  metadata part (basically what was in the schema, at one time written into
#  the csv's themselves). Further, the output is printed rather than written
#  to file.
def ShowGameInfo() -> bool:
    try:
        game_schema = GameSchema(schema_name=f"{args.game}.json")
        table_schema = TableSchema(schema_name=f"{settings['GAME_SOURCE_MAP'][args.game]['table']}.json")
        print(FileManager.GenCSVMetadata(game_schema=game_schema, table_schema=table_schema))
    except Exception as err:
        msg = f"Could not print information for {args.game}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        return True

## Function to write out the readme file for a given game.
#  This includes the CSV metadata (data from the schema, originally written into
#  the CSV files themselves), custom readme source, and the global changelog.
#  The readme is placed in the game's data folder.
def WriteReadme() -> bool:
    path = Path(f"./data") / args.game
    try:
        game_schema = GameSchema(schema_name=f"{args.game}.json")
        table_schema = TableSchema(schema_name=f"FIELDDAY_MYSQL.json")
        FileManager.GenerateReadme(game_schema=game_schema, table_schema=table_schema, path=path)
    except Exception as err:
        msg = f"Could not create a readme for {args.game}: {type(err)} {str(err)}"
        Logger.Log(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        return False
    else:
        Logger.Log(f"Successfully generated a readme for {args.game}.", logging.INFO)
        return True

## Function to handle execution of export code. This is the main intended use of
#  the program.
def RunExport(events:bool = False, features:bool = False) -> bool:
    ret_val : bool = False

    start = datetime.now()
    req = genRequest(events=events, features=features)
    if req.GetInterface().IsOpen():
        export_manager = ExportManager(settings=settings)
        result = export_manager.ExecuteRequest(request=req)
        ret_val = result['success']
        # cProfile.runctx("feature_exporter.ExportFromSQL(request=req)",
                        # {'req':req, 'feature_exporter':feature_exporter}, {})
    time_taken = datetime.now() - start
    Logger.Log(f"Total time taken: {time_taken}", logging.INFO)
    Logger.Log(f"Done with {args.game}.", logging.INFO)
    return ret_val

def genRequest(events:bool, features:bool) -> Request:
    interface : DataInterface
    range     : ExporterRange
    exporter_files : ExporterTypes
    exporter_files = ExporterTypes(events=events, sessions=features, population=features) 
    supported_vers = GameSchema(schema_name=f"{args.game}.json")['config']['SUPPORTED_VERS']
    if args.file is not None and args.file != "":
        raise NotImplementedError("Sorry, exports with file inputs are currently broken.")
        ext = str(args.file).split('.')[-1]
        interface = CSVInterface(game_id=args.game, filepath=args.file, delim="\t" if ext == '.tsv' else ',')
        # retrieve/calculate id range.
        ids = interface.AllIDs()
        range = ExporterRange.FromIDs(source=interface, ids=ids if ids is not None else [], versions=supported_vers)
        # breakpoint()
    else:
        interface_type = settings["GAME_SOURCE_MAP"][args.game]['interface']
        if interface_type == "BigQuery":
            interface = BigQueryInterface(game_id=args.game, settings=settings)
        elif interface_type == "MySQL":
            interface = MySQLInterface(game_id=args.game, settings=settings)
        else:
            raise Exception(f"{interface_type} is not a valid DataInterface type!")
        # retrieve/calculate date range.
        start_date, end_date = getDateRange()
        range = ExporterRange.FromDateRange(source=interface, date_min=start_date, date_max=end_date, versions=supported_vers)
    # Once we have the parameters parsed out, construct the request.
    return Request(interface=interface, range=range, exporter_types=exporter_files)

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

## This section of code is what runs main itself. Just need something to get it
#  started.
# Logger.Log(f"Running {sys.argv[0]}...", logging.INFO)
games_folder : Path = Path("./games")
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
export_parser.add_argument("-m", "--monthly", default=False, action="store_true",
                    help="Set the program to export a month's-worth of data, instead of using a date range. Replace the start_date argument with a month in MM/YYYY format.")
export_parser.add_argument("-f", "--file", default="",
                    help="Tell the program to use a file as input, instead of looking up a database.")
# set up main parser, with one sub-parser per-command.
command_list = ["export", "export-events", "export-session-features",
                "info", "readme", "list-games", "help"]
parser = argparse.ArgumentParser(description="Simple command-line utility to execute OpenGameData export requests.")
sub_parsers = parser.add_subparsers(help="Chosen command to run", dest="command")
# parser.add_argument("command", choices=command_list, help="The command to run.")
sub_parsers.add_parser("export", parents=[export_parser],
                        help="Export data in a given date range.")
sub_parsers.add_parser("export-events", parents=[export_parser],
                        help="Export event data in a given date range.")
sub_parsers.add_parser("export-session-features", parents=[export_parser],
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
cmd = args.command.lower()
if cmd == "export":
    success = RunExport(events=True, features=True)
elif cmd == "export-events":
    success = RunExport(events=True)
elif cmd == "export-session-features":
    success = RunExport(features=True)
elif cmd == "info":
    success = ShowGameInfo()
elif cmd == "readme":
    success = WriteReadme()
elif cmd == "list-games":
    success = ListGames()
# elif cmd == "help":
#     success = ShowHelp()
else:
    print(f"Invalid Command {cmd}!")
    success = False
if not success:
    sys.exit(1)
