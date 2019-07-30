# import standard libraries
import datetime
import logging
import math
import sys
# import local files
import utils
from FeatureExporter import FeatureExporter
from Request import Request
from feature_extractors.WaveExtractor import WaveExtractor

## Function to print a "help" listing for the export tool.
#  Hopefully not needed too often, if at all.
#  Just nice to have on hand, in case we ever need it.
def showHelp():
    width = 15
    print(width*"*")
    print("Invoke main.py with the following format: <python> main.py <cmd> [<args>]")
    print("<python> is your python command.")
    print("<cmd> is one of the available commands:")
    print("    export")
    print("    help")
    print("[<args>] are the arguments for the command.")
    print("    export args: game_id, [start_date, end_date]")
    print("        game_id    = id of game to export")
    print("        start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("        end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("    help arguments: *None*")
    print(width*"*")

## Function to handle execution of export code. This is the main use of the
#  program.
def runExport():
    # retrieve game id and date range.
    if num_args > 2:
        game_id = sys.argv[2]
    else:
        showHelp()
        return
    today   = datetime.datetime.now()
    start_date = datetime.datetime.strptime(sys.argv[3], "%m/%d/%Y") if num_args > 4 \
            else today
    start_date = start_date.replace(day=1, hour=0, minute=0, second=0)
    end_date   = datetime.datetime.strptime(sys.argv[4], "%m/%d/%Y") if num_args > 4 \
            else today
    end_date = end_date.replace(hour=23, minute=59, second=59)
    # Load settings, set up consts.
    settings = utils.loadJSONFile("config.json")
    db_settings = settings["db_config"]
    DB_NAME_DATA = db_settings["DB_NAME_DATA"]
    DB_USER = db_settings['DB_USER']
    DB_PW = db_settings['DB_PW']
    DB_HOST = db_settings['DB_HOST']
    DB_PORT = db_settings['DB_PORT']

    # set up other global vars as needed:
    logging.basicConfig(level=logging.WARNING)
    db = utils.SQL.connectToMySQL(DB_HOST, DB_PORT, DB_USER, DB_PW, DB_NAME_DATA)

    # TODO: if we have a GET call, handle here:

    # otherwise, for direct testing, handle here:
    req = Request(game_id=game_id, start_date=start_date, end_date=end_date, \
                max_sessions=settings["MAX_SESSIONS"], min_moves=settings["MIN_MOVES"], \
                )
    # import cProfile
    start = datetime.datetime.now()
    # cProfile.run("DataToCSV.exportDataToCSV(db=db, settings=settings, request=req)")
    feature_exporter = FeatureExporter(req.game_id, db=db, settings=settings)
    feature_exporter.exportFromRequest(request=req)
    end = datetime.datetime.now()

    time_delta = end - start
    logging.info(f"Total time taken: {math.floor(time_delta.total_seconds()/60)} min, {time_delta.total_seconds() % 60} sec")

## This section of code is what runs main itself. Just need something to get it
#  started.
num_args = len(sys.argv)
# print(sys.argv)
fname = sys.argv[0] if num_args > 0 else None
print(f"Running {fname}...")
cmd = sys.argv[1] if num_args > 1 else "help"
if type(cmd) == str:
    if cmd.lower() == "export":
        runExport()
    else:
        showHelp()
else:
    showHelp()