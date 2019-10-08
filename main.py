# import standard libraries
import cProfile
import logging
import math
import os
import sys
import typing
from datetime import datetime
# import local files
import feature_extractors.Extractor
import Request
import utils
from config import settings
from FeatureExporter import FeatureExporter
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.WaveExtractor import WaveExtractor
from GameTable import GameTable
from schemas.Schema import Schema

## Function to print a "help" listing for the export tool.
#  Hopefully not needed too often, if at all.
#  Just nice to have on hand, in case we ever need it.
def showHelp():
    width = 30
    print(width*"*")
    print("usage: <python> main.py <cmd> [<args>]")
    print("")
    print("<python> is your python command.")
    print("<cmd>    is one of the available commands:")
    print("         - export")
    print("         - export_month")
    print("         - help")
    print("[<args>] are the arguments for the command:")
    print("         - export: game_id, [start_date, end_date]")
    print("             game_id    = id of game to export")
    print("             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("         - export_month: game_id, [month_year]")
    print("             game_id    = id of game to export")
    print("             month_year = month (and year) to export, in form mm/yyyy (default=current month)")
    print("         - help: *None*")
    print(width*"*")

## Function to handle execution of export code. This is the main intended use of
#  the program.
def runExport(month: bool = False):
    # retrieve game id
    if num_args > 2:
        game_id = sys.argv[2]
    else:
        showHelp()
        return
    # retrieve/calculate date range.
    start_date: datetime
    end_date: datetime
    month_year: typing.List[int]
    # If we want to export all data for a given month, calculate a date range.
    if month is True:
        from calendar import monthrange
        if num_args > 3:
            month_year_str = sys.argv[3].split("/")
            month_year = [int(month_year_str[0]), int(month_year_str[1])]
        else:
            today   = datetime.now()
            month_year = [today.month, today.year]
        month_range = monthrange(month_year[1], month_year[0])
        days_in_month = month_range[1]
        start_date = datetime(year=month_year[1], month=month_year[0], day=1, hour=0, minute=0, second=0)
        end_date   = datetime(year=month_year[1], month=month_year[0], day=days_in_month, hour=23, minute=59, second=59)
    # Otherwise, create date range from given pair of dates.
    else:
        today   = datetime.now()
        start_date = datetime.strptime(sys.argv[3], "%m/%d/%Y") if num_args > 4 \
                else today
        start_date = start_date.replace(day=1, hour=0, minute=0, second=0)
        end_date   = datetime.strptime(sys.argv[4], "%m/%d/%Y") if num_args > 4 \
                else today
        end_date = end_date.replace(hour=23, minute=59, second=59)

    tunnel, db = utils.SQL.prepareDB(db_settings=db_settings, ssh_settings=ssh_settings)

    # Once we have the parameters parsed out, construct the request.
    req = Request.DateRangeRequest(game_id=game_id, start_date=start_date, end_date=end_date, \
                max_sessions=settings["MAX_SESSIONS"], min_moves=settings["MIN_MOVES"], \
                )
    start = datetime.now()
    feature_exporter = FeatureExporter(req.game_id, db=db, settings=settings)
    try:
        feature_exporter.exportFromRequest(request=req)
        # cProfile.runctx("feature_exporter.exportFromRequest(request=req)",
                        # {'req':req, 'feature_exporter':feature_exporter}, {})
    finally:
        end = datetime.now()
        time_delta = end - start
        print(f"Total time taken: {math.floor(time_delta.total_seconds()/60)} min, \
                                  {time_delta.total_seconds() % 60} sec")
        utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)

## Function to print out info on a game from the game's schema.
#  This does a similar function to writeReadme, but is limited to the CSV
#  metadata part (basically what was in the schema, at one time written into
#  the csv's themselves). Further, the output is printed rather than written
#  to file.
def showGameInfo():
    if num_args > 2:
        try:
            tunnel, db = prepareDB(db_settings=db_settings, ssh_settings=ssh_settings)
            game_name = sys.argv[2]
            schema = Schema(f"{game_name}.json")

            feature_descriptions = {**schema.perlevel_features(), **schema.aggregate_features()}
            print(_genCSVMetadata(game_name=game_name, raw_field_list=schema.db_columns_with_types(),
                                                         proc_field_list=feature_descriptions))
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
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
            game_name = sys.argv[2]
            path = f"./data/{game_name}"
            os.makedirs(name=path, exist_ok=True)
            readme        = open(f"{path}/readme.md",                "w")
            # Load schema, and write feature & column descriptions to the readme.
            schema = Schema(f"{game_name}.json")
            feature_descriptions = {**schema.perlevel_features(), **schema.aggregate_features()}
            readme.write(_genCSVMetadata(game_name=game_name, raw_field_list=schema.db_columns_with_types(),
                                                                proc_field_list=feature_descriptions))
            # Open files with game-specific readme data, and global db changelog.
            readme_src    = open(f"./doc/readme_src/{game_name}_readme_src.md", "r")
            changelog_src = open("./doc/readme_src/changelog_src.md",           "r")
            # Finally, write those into the new readme file.
            readme.write(readme_src.read())
            readme.write("\n")
            readme.write(changelog_src.read())
        except Exception as err:
            logging.error(str(err))
    else:
        print("Error, no game name given!")
        showHelp()

## Function to generate metadata for a given game.
#  The "fields" are a sort of generalization of columns. Basically, columns which
#  are repeated (say, once per level) all fall under a single field.
#  Columns which are completely unique correspond to individual fields.
#
#  @param game_name         The name of the game for which the csv metadata is being generated.
#  @param raw_field_list    A mapping of raw csv "fields" to descriptions of the fields.
#  @param proc_field_list   A mapping of processed csv features to descriptions of the features.
#  @return                  A string containing metadata for the given game.
def _genCSVMetadata(game_name: str, raw_field_list: typing.Dict[str,str], proc_field_list: typing.Dict[str,str]) -> str:
    raw_field_descriptions = [f"{key} - {raw_field_list[key]}" for key in raw_field_list.keys()]
    proc_field_descriptions = [f"{key} - {proc_field_list[key]}" for key in proc_field_list.keys()]
    raw_field_string = "\n".join(raw_field_descriptions)
    proc_field_string = "\n".join(proc_field_descriptions)
    template_str = \
f"## Field Day Open Game Data \n\
### Retrieved from https://fielddaylab.wisc.edu/opengamedata \n\
### These anonymous data are provided in service of future educational data mining research. \n\
### They are made available under the Creative Commons CCO 1.0 Universal license. \n\
### See https://creativecommons.org/publicdomain/zero/1.0/ \n\
\n\
## Suggested citation: \n\
### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://fielddaylab.wisc.edu/opengamedata \n\
\n\
## Game: {game_name} \n\
\n\
## Field Descriptions: \n\
### Raw CSV Columns:\n\
{raw_field_string}\n\
\n\
### Processed Features:\n\
{proc_field_string}\n\
\n"
    return template_str

## This section of code is what runs main itself. Just need something to get it
#  started.
num_args = len(sys.argv)
# print(sys.argv)
fname = sys.argv[0] if num_args > 0 else None
print(f"Running {fname}...")
cmd = sys.argv[1] if num_args > 1 else "help"
if type(cmd) == str:
    # if we have a real command, load the config file.
    # settings = utils.loadJSONFile("config.json")
    db_settings = settings["db_config"]
    ssh_settings = settings["ssh_config"]

    cmd = cmd.lower()

    if cmd == "export":
        runExport()
    elif cmd == "export_month":
        runExport(month=True)
    elif cmd == "info":
        showGameInfo()
    elif cmd == "readme":
        writeReadme()
    else:
        if not cmd == "help":
            print("Invalid Command!")
        showHelp()
else:
    print("Command is not a string!")
    showHelp()
