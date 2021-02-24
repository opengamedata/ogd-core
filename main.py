# import standard libraries
import cProfile
import datetime
import getopt
import logging
import math
import os
import sys
import traceback
import typing
from datetime import datetime
# import local files
import feature_extractors.Extractor
import Request
import utils
from config import settings
from managers.ExportManager import ExportManager
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.WaveExtractor import WaveExtractor
from schemas.Schema import Schema

## Function to print a "help" listing for the export tool.
#  Hopefully not needed too often, if at all.
#  Just nice to have on hand, in case we ever need it.
def showHelp():
    width = 30
    print(width*"*")
    print("usage: <python> main.py <cmd> [<args>] [<opt-args>]")
    print("")
    print("<python> is your python command.")
    print("<cmd>    is one of the available commands:")
    print("         - export")
    print("         - export-events")
    print("         - export-session-features")
    print("         - info")
    print("         - readme")
    print("         - help")
    print("[<args>] are the arguments for the command:")
    print("         - export: game_id, [start_date, end_date]")
    print("             game_id    = id of game to export")
    print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("         - export-events: game_id")
    print("             game_id    = id of game to export")
    print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("         - export-session-features: game_id, [month_year]")
    print("             game_id    = id of game to export")
    print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("         - info: game_id")
    print("             game_id    = id of game whose info should be shown")
    print("         - readme: game_id")
    print("             game_id    = id of game whose readme should be generated")
    print("         - help: *None*")
    print("[<opt-args>] are optional arguments, which affect certain commands:")
    print("         --file: specifies a file to export events or features")
    print("         --monthly: with this flag, specify dates by mm/yyyy instead of mm/dd/yyyy.")
    print(width*"*")


## Function to handle execution of export code. This is the main intended use of
#  the program.
def runExport(events: bool = False, features: bool = False):
    if "--file" in opts.keys():
        _extractFromFile(file_path=opts["--file"], events=True, features=True)
    else:
        # retrieve game id
        if num_args > 2:
            game_id = args[2]
        else:
            showHelp()
            return
        # retrieve/calculate date range.
        start_date: datetime
        end_date: datetime
        # If we want to export all data for a given month, calculate a date range.
        if "--monthly" in opts.keys():
            month_year: typing.List[int]
            if num_args > 3:
                month_year_str = args[3].split("/")
                month_year = [int(month_year_str[0]), int(month_year_str[1])]
            else:
                today   = datetime.now()
                month_year = [today.month, today.year]
            utils.Logger.toStdOut(f"Exporting {month_year[0]}/{month_year[1]} data for {game_id}...", logging.DEBUG)
            _execMonthExport(game_id=game_id, month=month_year[0], year=month_year[1], events=events, features=features)
            utils.Logger.toStdOut(f"Done with {game_id}.", logging.DEBUG)
        # Otherwise, create date range from given pair of dates.
        else:
            today   = datetime.now()
            start_date = datetime.strptime(args[3], "%m/%d/%Y") if num_args > 3 \
                    else today
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date   = datetime.strptime(args[4], "%m/%d/%Y") if num_args > 4 \
                    else today
            end_date = end_date.replace(hour=23, minute=59, second=59)
            utils.Logger.toStdOut(f"Exporting from {str(start_date)} to {str(end_date)} of data for {game_id}...", logging.DEBUG)
            _execExport(game_id, start_date, end_date, events=events, features=features)
            utils.Logger.toStdOut(f"Done with {game_id}.", logging.DEBUG)

def _execMonthExport(game_id, month, year, events: bool, features: bool):
    from calendar import monthrange
    month_range = monthrange(year, month)
    days_in_month = month_range[1]
    start_date = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    end_date   = datetime(year=year, month=month, day=days_in_month, hour=23, minute=59, second=59)
    _execExport(game_id, start_date, end_date, events, features)

def _execExport(game_id, start_date, end_date, events: bool, features: bool):
    # Once we have the parameters parsed out, construct the request.
    export_files = Request.ExportFiles(events=events, raw=False, proc=features)
    req = Request.DateRangeRequest(game_id=game_id, start_date=start_date, end_date=end_date, \
                export_files=export_files)
    start = datetime.now()
    # breakpoint()
    export_manager = ExportManager(game_id=req.game_id, settings=settings)
    try:
        schema = Schema(game_id)
        export_manager.ExportFromSQL(request=req, game_schema=schema)
        # cProfile.runctx("feature_exporter.ExportFromSQL(request=req)",
                        # {'req':req, 'feature_exporter':feature_exporter}, {})
    except Exception as err:
        msg = f"{type(err)} {str(err)}"
        utils.Logger.toStdOut(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        utils.Logger.toFile(msg, logging.ERROR)
    finally:
        end = datetime.now()
        time_delta = end - start
        minutes = math.floor(time_delta.total_seconds()/60)
        seconds = time_delta.total_seconds() % 60
        print(f"Total time taken: {minutes} min, {seconds} sec")

def _extractFromFile(file_path: str, events: bool = False, features: bool = False):
    if num_args > 2:
        game_id = args[2]
    else:
        showHelp()
        return
    start = datetime.now()
    export_files = Request.ExportFiles(events=events, raw=False, proc=features) 
    req = Request.FileRequest(file_path=file_path, game_id=game_id, export_files=export_files)
    # breakpoint()
    export_manager = ExportManager(game_id=req.game_id, settings=settings)
    try:
        export_manager.ExtractFromFile(request=req, delimiter='\t')
        # cProfile.runctx("feature_exporter.ExportFromSQL(request=req)",
                        # {'req':req, 'feature_exporter':feature_exporter}, {})
    except Exception as err:
        msg = f"{type(err)} {str(err)}"
        utils.Logger.toStdOut(msg, logging.ERROR)
        traceback.print_tb(err.__traceback__)
        utils.Logger.toFile(msg, logging.ERROR)
    finally:
        end = datetime.now()
        time_delta = end - start
        minutes = math.floor(time_delta.total_seconds()/60)
        seconds = time_delta.total_seconds() % 60
        print(f"Total time taken: {minutes} min, {seconds} sec")

## Function to print out info on a game from the game's schema.
#  This does a similar function to writeReadme, but is limited to the CSV
#  metadata part (basically what was in the schema, at one time written into
#  the csv's themselves). Further, the output is printed rather than written
#  to file.
def showGameInfo():
    if num_args > 2:
        game_name = args[2]
        schema = Schema(schema_name=f"{game_name}.json")

        feature_descriptions = {**schema.perlevel_features(), **schema.aggregate_features()}
        print(utils.GenCSVMetadata(game_name=game_name, raw_field_list=schema.db_columns_with_types(),\
                                                        proc_field_list=feature_descriptions))
    else:
        print("Error, no game name given!")
        showHelp()

## Function to write out the readme file for a given game.
#  This includes the CSV metadata (data from the schema, originally written into
#  the CSV files themselves), custom readme source, and the global changelog.
#  The readme is placed in the game's data folder.
def writeReadme():
    if num_args > 2:
        try:
            game_name = args[2]
            path = f"./data/{game_name}"
            schema = Schema(schema_name=f"{game_name}.json")
            utils.GenerateReadme(game_name=game_name, schema=schema, path=path)
            utils.Logger.toStdOut(f"Successfully generated a readme for {game_name}.")
        except Exception as err:
            msg = f"Could not create a readme for {game_name}: {type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
    else:
        print("Error, no game name given!")
        showHelp()

## This section of code is what runs main itself. Just need something to get it
#  started.
utils.Logger.toStdOut(f"Running {sys.argv[0]}...", logging.INFO)
utils.Logger.toFile(f"Running {sys.argv[0]}...", logging.INFO)
try:
    arg_options = ["file=", "help", "monthly"]
    optupi, args = getopt.gnu_getopt(sys.argv, shortopts="-h", longopts=arg_options)

    opts = {opt[0]: opt[1] for opt in optupi}
    num_args = len(args)
    cmd = args[1] if num_args > 1 else "help"
except getopt.GetoptError as err:
    print(f"Error, invalid option given!\n{err}")
    cmd = "help"
if type(cmd) == str:
    # if we have a real command, load the config file.
    # settings = utils.loadJSONFile("config.json")
    db_settings = settings["db_config"]
    ssh_settings = settings["ssh_config"]

    cmd = cmd.lower()

    if cmd == "export":
        runExport(events=True, features=True)
    elif cmd == "export-events":
        runExport(events=True)
    elif cmd == "export-session-features":
        runExport(features=True)
    elif cmd == "info":
        showGameInfo()
    elif cmd == "readme":
        writeReadme()
    elif cmd == "help" or "-h" in opts.keys() or "--help" in opts.keys():
        showHelp()
    else:
        print(f"Invalid Command {cmd}!")
else:
    print("Command is not a string!")
    showHelp()
