#!/usr/bin/python3.6
# import standard libraries
import json
import logging
from datetime import datetime
# import local files
import cgi, cgitb
import utils

# Load settings, set up consts.
settings = utils.loadJSONFile("config.json")
db_settings = settings["db_config"]
DB_NAME_DATA = db_settings["DB_NAME_DATA"]
DB_USER = db_settings['DB_USER']
DB_PW = db_settings['DB_PW']
DB_HOST = db_settings['DB_HOST']
DB_PORT = db_settings['DB_PORT']
DB_TABLE = db_settings["table"]
ssh_settings = settings["ssh_config"]
SSH_USER = ssh_settings['SSH_USER']
SSH_PW = ssh_settings['SSH_PW']
SSH_HOST = ssh_settings['SSH_HOST']
SSH_PORT = ssh_settings['SSH_PORT']

# set up other global vars as needed:
logging.basicConfig(level=logging.INFO)
sql_login = utils.SQLLogin(host=DB_HOST, port=DB_PORT, user=DB_USER, pword=DB_PW, db_name=DB_NAME_DATA)
ssh_login = utils.SSHLogin(host=SSH_HOST, port=SSH_PORT, user=SSH_USER, pword=SSH_PW)
tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
cursor = db.cursor(buffered=True)

header = "Content-type:text/plain \r\n\r\n"

try:
    request = cgi.FieldStorage()
    method = request.getvalue("method")

    if method == "say_hello":
        body = "Hello, world."
    elif method == "get_all_active_sessions":
        game_id = request.getvalue("gameID")
        body = _getAllActiveSessions(game_id=game_id)
    elif method == "get_active_sessions_by_loc":
        game_id = request.getvalue("gameID")
        state = request.getvalue("state")
        city = request.getvalue("city")
        body = _getActiveSessionsByLoc(game_id=game_id, state=state, city=city)
    elif method == "get_features_by_sessID":
        sess_id = request.getvalue("sessID")
        features = request.getvalue("features")
        body = _getFeaturesBySessID(sess_id=sess_id, features=features)
    elif method == "get_feature_names_by_game":
        game_id = request.getvalue("gameID")
        body = _getFeatureNamesByGame(game_id=game_id)
    elif method == "get_predictions_by_sessID":
        sess_id = request.getvalue("sessID")
        predictions = request.getvalue("predictions")
        body = _getPredictionsBySessID(sess_id=sess_id, predictions=predictions)
    elif method == "get_prediction_names_by_game":
        game_id = request.getvalue("gameID")
        body = _getPredictionNamesByGame(game_id=game_id)

    print(str(header))
    print(json.dumps(body))
except Exception as err:
    print(f"Error in realtime script!")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")

def _getAllActiveSessions(game_id: str):
    start_time = datetime.datetime.now() - datetime.timedelta(minutes=5)

    filt = f"app_id={game_id} AND server_time > '{start_time.isoformat()}';"
    active_sessions_raw = utils.SQL.SELECT(cursor=cursor,
                                           db_name=DB_NAME_DATA, table=DB_TABLE,\
                                           columns=["session_d", "remote_addr"], filter=filt,\
                                           sort_columns=["remote_addr"], distinct=True)
    ID_INDEX = 0
    IP_INDEX = 1
    ret_val = {}
    for item in active_sessions_raw:
        (state, city) = _ip_to_loc(item[IP_INDEX])
        if state not in ret_val.keys():
            ret_val[state] = {}
        if city not in ret_val[state].keys():
            ret_val[state][city] = []
        ret_val[state][city].append(item[ID_INDEX])
    return ret_val

def _ip_to_loc(ip):
    # in future, convert ip to a (state, city) pair
    return ("Stub:Wisconsin", "Stub:Madison")

def _getActiveSessionsByLoc(game_id: str, state: str, city: str):
    pass

def _getFeaturesBySessID(sess_id: str, features):
    pass

def _getFeatureNamesByGame(gameID: str, features):
    pass

def _getPredictionsBySessID(sess_id: str, predictions):
    pass

def _getPredictionNamesByGame(gameID: str, predictions):
    pass