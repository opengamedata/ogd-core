# import standard libraries
import datetime
import logging
import math
import sys
# import local files
import DataToCSV
import utils
from Request import Request
from feature_extractors.WaveExtractor import WaveExtractor

# Get variables from command line args
num_args = len(sys.argv)
cmd = sys.argv[0] if num_args > 0 else "help"
if type(cmd) == str:
    if cmd.lower() == "export":
        runExport()
    else:
        showHelp()
else:
    showHelp()

def showHelp():
    print("Invoke main.py with the following format: <python> main.py <cmd> [<args>]")
    print("<python> is your python command.")
    print("<cmd> is one of the available commands:")
    print("    export")
    print("    help")
    print("[<args>] are the arguments for the command.")
    print("export arguments: game_id, [start_date, end_date]")
    print("    game_id    = id of game to export")
    print("    start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)")
    print("    end_date   = ending date for export, in form mm/dd/yyyy (default=current day)")
    print("help arguments: *None*")

def runExport():
    game_id = sys.argv[1] if num_args > 1 else ""
    today   = datetime.date.today()
    start_date = datetime.datetime.strptime(sys.argv[2], "%m/%d/%Y") if num_args > 3 \
            else today.replace(day=1)
    end_date   = datetime.datetime.strptime(sys.argv[3], "%m/%d/%Y") if num_args > 3 \
            else today
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

    # print("Content-type:text/html\r\n\r\n \
    #        <html> \
    #        <head> \
    #            <title>Parser CGI test</test>\
    #        </head> \
    #        <body> \
    #            <p>")

    db = utils.SQL.connectToMySQL(DB_HOST, DB_PORT, DB_USER, DB_PW, DB_NAME_DATA)

    # TODO: if we have a GET call, handle here:

    # otherwise, for direct testing, handle here:
    # req = Request(game_id="WAVES", start_date=datetime.datetime(2019, 3, 1, 0, 0, 0), \
    #               end_date=datetime.datetime(2019, 3, 31, 23, 59, 59), max_sessions=settings["MAX_SESSIONS"], min_moves=1, \
    #               read_cache=False, write_cache=False
    #              )
    req = Request(game_id=game_id, start_date=start_date, end_date=end_date, \
                max_sessions=settings["MAX_SESSIONS"], min_moves=settings["MIN_MOVES"], \
                read_cache=False, write_cache=False)
    import cProfile
    start = datetime.datetime.now()
    # cProfile.run("DataToCSV.exportDataToCSV(db=db, settings=settings, request=req)")
    DataToCSV.exportDataToCSV(db=db, settings=settings, request=req)
    end = datetime.datetime.now()

    time_delta = end - start
    print("Total time taken: {} min, {} sec".format(math.floor(time_delta.total_seconds()/60), time_delta.total_seconds() % 60))
    # print("</p>")
    # print("</body>")
    # print("</html>")
