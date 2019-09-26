#!/usr/bin/python3.6
# import standard libraries
import cgi
import cgitb
import json
import logging
import math
import random
import traceback
import typing
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
    def getAllActiveSessions(game_id: str, require_player_id: bool) -> typing.Dict:
        start_time = datetime.now()
        tunnel,db = utils.SQL.prepareDB(db_settings=db_settings, ssh_settings=ssh_settings)
        log_file = open("./python_errors.log", "a+")
        try:
            cursor = db.cursor()
            start_time = datetime.now() - timedelta(minutes=5)
            player_id_filter = "AND `player_id` IS NOT NULL" if require_player_id else ""
            filt = f"`app_id`='{game_id}' AND `server_time` > '{start_time.isoformat()}' {player_id_filter}"
            active_sessions_raw = utils.SQL.SELECT(cursor=cursor,
                                                   db_name=DB_NAME_DATA, table=DB_TABLE,\
                                                   columns=["session_id", "player_id"], filter=filt,\
                                                   sort_columns=["session_id"], distinct=True)

            # _cgi_debug(f"Got result from db: {str(active_sessions_raw)}", "Info", log_file)
            ret_val = {}
            for item in active_sessions_raw:
                sess_id = item[0]
                filt = f"`session_id`='{sess_id}'"
                max_level_raw = utils.SQL.SELECT(cursor=cursor,
                                                 db_name=DB_NAME_DATA, table=DB_TABLE,\
                                                 columns=["MAX(level)"], filter=filt)
                cur_level_raw = utils.SQL.SELECT(cursor=cursor,
                                                 db_name=DB_NAME_DATA, table=DB_TABLE,\
                                                 columns=["level"], filter=filt, limit=1,\
                                                 sort_columns=["client_time"], sort_direction="DESC")
                ret_val[sess_id] = {"session_id":sess_id, "max_level":max_level_raw[0][0], "cur_level":cur_level_raw[0][0]}
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            # _cgi_debug(f"returning: {str(ret_val)}", "Info", log_file)
            # print(f"returning from realtime, with all active sessions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
            return ret_val
        except Exception as err:
            #print(f"got error in RTServer.py: {str(err)}")
            _cgi_debug(f"Got an error in getAllActiveSessions: {str(err)}", "Error", log_file)
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            raise err
        finally:
            log_file.close()

    @staticmethod
    def getActiveSessionsByLoc(game_id: str, state: str, city: str):
        all_sessions = RTServer.getAllActiveSessions(game_id)
        return all_sessions[state][city]

    @staticmethod
    def getFeaturesBySessID(sess_id: str, game_id: str, features = None) -> typing.Dict:
        tunnel,db = utils.SQL.prepareDB(db_settings=db_settings, ssh_settings=ssh_settings)
        try:
            log_file = open("./python_errors.log", "a+")
            _cgi_debug(f"Getting all features for session {sess_id}", "Info", log_file)
            cursor = db.cursor()
            filt = f"`session_id`='{sess_id}'"
            session_data = utils.SQL.SELECT(cursor=cursor,
                                            db_name=DB_NAME_DATA, table=DB_TABLE,\
                                            filter=filt,\
                                            sort_columns=["session_n", "client_time"])
            ret_val: typing.Dict
            if len(session_data) > 0:
                request = Request.IDListRequest(game_id=game_id, session_ids=[sess_id])
                game_table = GameTable(db, settings, request)
                schema = Schema(schema_name=f"{game_id}.json")
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
                if features is not None and features != "null":
                    ret_val = {i:all_features[i] for i in features}
                else:
                    ret_val = all_features
            else:
                print("error, empty session!")
                _cgi_debug(f"error, empty session! all_features: {all_features}", "Error", log_file)
                logging.warning(f"all_features: {all_features}")
                ret_val = {"error": "Empty Session!"}
            log_file.close()
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return ret_val
        except Exception as err:
            print(f"got error in RTServer.py: {str(err)}")
            _cgi_debug(f"Got an error in getFeaturesBySessID: {str(err)}", "Error", log_file)
            traceback.print_tb(err.__traceback__)
            log_file.close()
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            raise err

    @staticmethod
    def getFeatureNamesByGame(game_id: str):
        log_file = open("./python_errors.log", "a")
        try:
            schema = Schema(schema_name=f"{game_id}.json")
            # _cgi_debug(f"schema features: {schema.feature_list()}", "Info", log_file)
            return {"features": schema.feature_list()}
        except Exception as err:
            _cgi_debug(f"Got exception in getFeatureNamesByGame: {str(err)}", "Error", log_file)
            _cgi_debug("Had to return None", "Warning", log_file)
            return None
        finally:
            log_file.close()

    @staticmethod
    def getPredictionsBySessID(sess_id: str, game_id: str, predictions):
        log_file = open("./python_errors.log", "a")
        _cgi_debug(f"Trying to get predictions for session {sess_id}", "Info", log_file)
        #tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        #cursor = db.cursor()
        start_time = datetime.now()

        # TODO: move models out into a JSON file.
        models = utils.loadJSONFile(filename=f"{game_id}_models.json", path="./models/")
        ret_val = {}
        features_raw = RTServer.getFeaturesBySessID(sess_id, game_id)
        # print(f"features_raw: {features_raw}")
        features_parsed = RTServer._parseRawToDict(features_raw)
        for model in models.keys():
            ret_val[model] = RTServer.EvaluateLogRegModel(models[model], features_parsed)

        print(f"returning from realtime, with session_predictions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
        return {sess_id:ret_val}

    @staticmethod
    def _parseRawToDict(features_raw):
        ret_val = {}
        for feature_name in features_raw.keys():
            if features_raw[feature_name].replace('.','',1).isdigit():
                ret_val[feature_name] = float(features_raw[feature_name])
            else:
                ret_val[feature_name] = features_raw[feature_name]
        return ret_val
    ## Function to evaluate a logistic regression model, creating a prediction.
    #  This is based around the equation for probability of Y=1, denoted as p:
    #  p = 1 / (1 + e^-logit(X)),
    #  where X is the input data used to predict Y, and
    #  logit(X) = b0 + b1*x1 + b2*x2 + ... + bn*xn,
    #  where bi are the coefficients.
    #  Based on information at https://www.medcalc.org/manual/logistic_regression.php
    @staticmethod
    def EvaluateLogRegModel(model, feature_data) -> float:
        logit = 0
        for coeff in model.keys():
            if coeff == "Intercept":
                logit += model[coeff]
            else:
                # print(f"feature_data[coeff]: {str(type(feature_data[coeff]))} {feature_data[coeff]}")
                # print(f"model[coeff]: {str(type(model[coeff]))} {model[coeff]}")
                # print(f"product: {model[coeff] * feature_data[coeff]}")
                logit += model[coeff] * feature_data[coeff]
        # print(f"logit: {logit}")
        p = 1 / (1 + math.exp(-logit))
        return p

    @staticmethod
    def getPredictionNamesByGame(game_id: str):
        return {"stub:prediction_names":["stub:this_should_be_1", "stub:this_should_be_0.168", "stub:random_1", "stub:random_2", "stub:random_3", "stub:random_4"]}

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
    DB_TABLE = db_settings["table"]
    ssh_settings = settings["ssh_config"]

    # set up other global vars as needed:
    logging.basicConfig(level=logging.INFO)
    log_file = open("./python_errors.log", "a+")

    request = cgi.FieldStorage()
    method = request.getvalue("method")

    _cgi_debug(f"method requested: {method}", "Info", log_file)
    if method == "say_hello":
        body = "Hello, world."
    elif method == "get_all_active_sessions":
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        body = RTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id)
    elif method == "get_active_sessions_by_loc":
        game_id = request.getvalue("gameID")
        state = request.getvalue("state")
        city = request.getvalue("city")
        body = RTServer.getActiveSessionsByLoc(game_id=game_id, state=state, city=city)
    elif method == "get_features_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        features = request.getvalue("features")
        body = RTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, features=features)
        logging.info("got features by session ID in main realtime code.")
        _cgi_debug(f"got features by session ID in main realtime code, sess_id={sess_id}, game_id={game_id}", "Info", log_file)
    elif method == "get_feature_names_by_game":
        game_id = request.getvalue("gameID")
        body = RTServer.getFeatureNamesByGame(game_id=game_id)
    elif method == "get_predictions_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        predictions = request.getvalue("predictions")
        body = RTServer.getPredictionsBySessID(sess_id=sess_id, game_id=game_id, predictions=predictions)
    elif method == "get_prediction_names_by_game":
        game_id = request.getvalue("gameID")
        body = RTServer.getPredictionNamesByGame(game_id=game_id)

    result: str = json.dumps(body, default=lambda ob: ob.isoformat() if type(ob) == datetime else json.dumps(ob))
    # _cgi_debug(f"method: {method}; result string: {result}", "Info", log_file)
    print(result)
except Exception as err:
    print(f"Error in realtime script! {str(err)}, traceback:\n{traceback.format_exc()}")
    traceback.print_tb(err.__traceback__)
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")
