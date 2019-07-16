# import standard libraries
import datetime
import logging
import math
# import local files
import DataToCSV
import utils
from Request import Request
from feature_extractors.WaveExtractor import WaveExtractor

# Load settings, set up consts.
settings = utils.loadJSONFile("config.json")
db_settings = settings["db_config"]
DB_NAME_DATA = db_settings["DB_NAME_DATA"]
DB_USER = db_settings['DB_USER']
DB_PW = db_settings['DB_PW']
DB_HOST = db_settings['DB_HOST']
DB_PORT = db_settings['DB_PORT']

# set up other global vars as needed:
logging.basicConfig(level=logging.DEBUG)

db = utils.SQL.connectToMySQL(DB_HOST, DB_PORT, DB_USER, DB_PW, DB_NAME_DATA)

# TODO: if we have a GET call, handle here:

# otherwise, for direct testing, handle here:
req = Request(game_id="WAVES", start_date=datetime.datetime(2019, 3, 1, 0, 0, 0), \
              end_date=datetime.datetime(2019, 3, 31, 23, 59, 59), max_sessions=settings["MAX_SESSIONS"], min_moves=1, \
              read_cache=False, write_cache=False
             )
start = datetime.datetime.now()
DataToCSV.exportDataToCSV(db=db, settings=settings, request=req)
end = datetime.datetime.now()

time_delta = end - start
print("Total time taken: {} min, {} sec".format(math.floor(time_delta.total_seconds()/60), time_delta.total_seconds() % 60))