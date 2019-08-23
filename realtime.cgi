#!/usr/bin/python3.6
# import standard libraries
import cgi
import cgitb
import json
import logging
import traceback
from datetime import datetime, timedelta
# import local files
import Request
import utils
from feature_extractors.Extractor import Extractor
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.WaveExtractor import WaveExtractor
from GameTable import GameTable
from ProcManager import ProcManager
from schemas.Schema import Schema

## Simple formatting function for writing out timestamped debug prints.
def _cgi_debug(msg: str, level: str, file):
    file.write(f"[{level}] At {str(datetime.now())}, {msg}.\n")

class RTServer:
    @staticmethod
    def getAllActiveSessions(game_id: str):
        tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        cursor = db.cursor()
        start_time = datetime.now() - timedelta(minutes=5)

        filt = f"app_id={game_id} AND server_time > '{start_time.isoformat()}';"
        active_sessions_raw = utils.SQL.SELECT(cursor=cursor,
                                               db_name=DB_NAME_DATA, table=DB_TABLE,\
                                               columns=["session_id", "remote_addr"], filter=filt,\
                                               sort_columns=["remote_addr"], distinct=True)
        print(f"got stuff from db: {str(active_sessions_raw)}")
        utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
        return "quit"
        ID_INDEX = 0
        IP_INDEX = 1
        ret_val = {}
        for item in active_sessions_raw:
            (state, city) = RTServer._ip_to_loc(item[IP_INDEX])
            if state not in ret_val.keys():
                ret_val[state] = {}
            if city not in ret_val[state].keys():
                ret_val[state][city] = []
            ret_val[state][city].append(item[ID_INDEX])
        utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
        return ret_val

    @staticmethod
    def getActiveSessionsByLoc(game_id: str, state: str, city: str):
        all_sessions = RTServer.getAllActiveSessions(game_id)
        return all_sessions[state][city]

    @staticmethod
    def getFeaturesBySessID(sess_id: str, game_id: str, features):
        tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)

        cursor = db.cursor()
        filt = f"session_id = '{sess_id}';"
        session_data = utils.SQL.SELECT(cursor=cursor,
                                        db_name=DB_NAME_DATA, table=DB_TABLE,\
                                        filter=filt,\
                                        sort_columns=["session_n", "client_time"])
        if len(session_data) == 0:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return {"error": "Empty Session!"}
        else:
            request = Request.IDListRequest(game_id=game_id, session_ids=[sess_id])
            game_table = GameTable(db, settings, request)
            schema = Schema(schema_name=f"{game_id}.JSON")
            extractor: Extractor
            if game_id == "WAVES":
                extractor = WaveExtractor(session_id=sess_id, game_table = game_table, game_schema=schema)
            elif game_id == "CRYSTAL":
                extractor = CrystalExtractor(session_id=sess_id, game_table = game_table, game_schema=schema)
            else:
                raise Exception("Got an invalid game ID!")
            for row in session_data:
                col = row[game_table.complex_data_index]
                complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":row[game_table.event_index]}
                if "event_custom" not in complex_data_parsed.keys():
                    complex_data_parsed["event_custom"] = row[game_table.event_index]
                row = list(row)
                row[game_table.complex_data_index] = complex_data_parsed
                extractor.extractFromRow(row_with_complex_parsed=row, game_table=game_table)
            all_features = dict(zip( extractor.getFeatureNames(game_table=game_table, game_schema=schema),
                                     extractor.getCurrentFeatures() ))
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            if features is not None:
                return {i:all_features[i] for i in features}
            else:
                return all_features

    @staticmethod
    def getFeatureNamesByGame(game_id: str):
        _cgi_debug("Ready to load schema", "Info", log_file)
        try:
            schema = Schema(schema_name=f"{game_id}.json")
            _cgi_debug(f"schema features: {schema.feature_list()}", "Info", log_file)
            return {"features": schema.feature_list()}
        except Exception as err:
            _cgi_debug(f"Got exception message: {str(err)}", "Error", log_file)
            _cgi_debug("Had to return None", "Warning", log_file)
            return None

    @staticmethod
    def getPredictionsBySessID(sess_id: str, game_id: str, predictions):
        #tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        #ln = 155
        #print(f"ran to the quit in line {ln}")
        #quit()
        #cursor = db.cursor()
        return {f"stub:{sess_id}":{"stub:prediction_name_1": 1, "stub:prediction_name_2": False}}

    @staticmethod
    def getPredictionNamesByGame(game_id: str):
        return {"stub:prediction_names":["stub:prediction_name_1", "stub:prediction_name_2"]}

    @staticmethod
    def _ip_to_loc(ip):
        # in future, convert ip to a (state, city) pair
        return ("Stub:Wisconsin", "Stub:Madison")

try:
    header = "Content-type:text/plain \r\n\r\n"
    print(str(header))

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
    log_file = open("./python_errors.log", "a")
    _cgi_debug("Opened log file", "Info", log_file)

    request = cgi.FieldStorage()
    method = request.getvalue("method")
    print(f"method is: {method}")

    if method == "say_hello":
        body = "Hello, world."
    elif method == "get_all_active_sessions":
        game_id = request.getvalue("gameID")
        body = RTServer.getAllActiveSessions(game_id=game_id)
    elif method == "get_active_sessions_by_loc":
        game_id = request.getvalue("gameID")
        state = request.getvalue("state")
        city = request.getvalue("city")
        body = RTServer.getActiveSessionsByLoc(game_id=game_id, state=state, city=city)
    elif method == "get_features_by_sessID":
        sess_id = request.getvalue("sessID")
        features = request.getvalue("features")
        body = RTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, features=features)
    elif method == "get_feature_names_by_game":
        _cgi_debug("Ready to get all feature names", "Info", log_file)
        game_id = request.getvalue("gameID")
        _cgi_debug(f"Game ID is {game_id}", "Info", log_file)
        body = RTServer.getFeatureNamesByGame(game_id=game_id)
    elif method == "get_predictions_by_sessID":
        sess_id = request.getvalue("sessID")
        predictions = request.getvalue("predictions")
        body = RTServer.getPredictionsBySessID(sess_id=sess_id, predictions=predictions)
    elif method == "get_prediction_names_by_game":
        game_id = request.getvalue("gameID")
        body = RTServer.getPredictionNamesByGame(game_id=game_id)

    print(json.dumps(body))
except Exception as err:
    print(f"Error in realtime script! {str(err)}")
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")
