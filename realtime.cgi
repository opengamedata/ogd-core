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
    def getAllActiveSessions(game_id: str) -> typing.List:
        tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        log_file = open("./python_errors.log", "a")
        try:
            cursor = db.cursor()
            start_time = datetime.now() - timedelta(minutes=5)
            filt = f"`app_id`='{game_id}' AND `server_time` > '{start_time.isoformat()}'"
            active_sessions_raw = utils.SQL.SELECT(cursor=cursor,
                                                   db_name=DB_NAME_DATA, table=DB_TABLE,\
                                                   columns=["session_id", "remote_addr"], filter=filt,\
                                                   sort_columns=["remote_addr", "session_id"], distinct=True)

            _cgi_debug(f"Got result from db: {str(active_sessions_raw)}", "Info", log_file)
            ID_INDEX = 0
            IP_INDEX = 1
            ret_val = []
            for item in active_sessions_raw:
                ret_val.append(item[ID_INDEX])
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            _cgi_debug(f"returning: {str(ret_val)}", "Info", log_file)
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
    def getFeaturesBySessID(sess_id: str, game_id: str, features = None):
        tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        try:
            log_file = open("./python_errors.log", "a")
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
            _cgi_debug(f"schema features: {schema.feature_list()}", "Info", log_file)
            return {"features": schema.feature_list()}
        except Exception as err:
            _cgi_debug(f"Got exception in getFeatureNamesByGame: {str(err)}", "Error", log_file)
            _cgi_debug("Had to return None", "Warning", log_file)
            return None
        finally:
            log_file.close()

    @staticmethod
    def getPredictionsBySessID(sess_id: str, game_id: str, predictions):
        #tunnel,db = utils.SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        #cursor = db.cursor()

        # TODO: move models out into a JSON file.
        models = {"lvl0 Only": {
            "lvl0_percentAmplitudeMoves": -0.29425597674098386,
            "lvl0_percentWavelengthMoves": 0.13063514099244697,
            "lvl0_sliderAvgRange": 0.008400398230626093,
            "lvl0_sliderAvgStdDevs": -0.02313995234070279,
            "lvl0_totalLevelTime": -6.206149653582499E-5,
            "lvl0_totalMoveTypeChanges": -0.055159425820165066,
            "lvl0_totalSliderMoves": 0.020683891752809193,
            "Intercept": 1.4707148480736822
        }, "lvl0-lvl1": {
            "lvl0_percentAmplitudeMoves": -0.031454240241031904,
            "lvl0_percentWavelengthMoves": 0.44354811998921,
            "lvl0_sliderAvgRange": 0.008765856320059315,
            "lvl0_sliderAvgStdDevs": -0.022555598430227822,
            "lvl0_totalFails": -8.306585563078928,
            "lvl0_totalLevelTime": -2.8775186451121113E-6,
            "lvl0_totalMoveTypeChanges": -0.024204161840695543,
            "lvl0_totalSliderMoves":-0.004943425659682401,
            "lvl1_beginCount":0.12804684223409327,
            "lvl1_percentAmplitudeMoves":-9.756265026792823,
            "lvl1_percentOffsetMoves":-10.759012271172631,
            "lvl1_percentWavelengthMoves":-10.653336629748745,
            "lvl1_sliderAvgRange":0.007582127665132338,
            "lvl1_sliderAvgStdDevs":-0.014010840412089932,
            "lvl1_succeedCount":0.8146416097764155,
            "lvl1_totalFails":-0.7967873087354845,
            "lvl1_totalLevelTime":0.4863672679031432,
            "lvl1_totalMoveTypeChanges":-0.036142124485923834,
            "lvl1_totalSliderMoves":0.031712585991452616,
            "Intercept":27.09633783191419
        }, "lvl0-lvl1-lvl2":{
            "lvl0_percentAmplitudeMoves":0.459158238383812,
            "lvl0_percentWavelengthMoves":0.3135214271506894,
            "lvl0_sliderAvgRange":-0.0013117419408848361,
            "lvl0_sliderAvgStdDevs":0.00669981749761533,
            "lvl0_totalFails":-8.226148587978404,
            "lvl0_totalLevelTime":-3.6625608176976495E-5,
            "lvl0_totalMoveTypeChanges":-0.041051219451867835,
            "lvl0_totalSliderMoves":7.007514356091027E-4,
            "lvl1_beginCount":-0.16572283226855725,
            "lvl1_percentAmplitudeMoves":1.0252735396745971,
            "lvl1_percentOffsetMoves":0.1185165469106207,
            "lvl1_percentWavelengthMoves":0.0,
            "lvl1_sliderAvgRange":0.003967364097424138,
            "lvl1_sliderAvgStdDevs":0.004642781223435156,
            "lvl1_succeedCount":0.7854890801716204,
            "lvl1_totalFails":-0.7875038149126333,
            "lvl1_totalLevelTime":0.31370367282653333,
            "lvl1_totalMoveTypeChanges":-0.02794149786486569,
            "lvl1_totalSliderMoves":0.02286447936937795,
            "lvl2_percentAmplitudeMoves":0.17551876816901577,
            "lvl2_percentOffsetMoves":0.5810184625950897,
            "lvl2_percentWavelengthMoves":0.0,
            "lvl2_sliderAvgRange":0.003681281277771455,
            "lvl2_sliderAvgStdDevs":0.0017375492899164532,
            "lvl2_succeedCount":0.20577019317888698,
            "lvl2_totalFails":-0.20081695019279536,
            "lvl2_totalMoveTypeChanges":-0.03032808481851513,
            "lvl2_totalSliderMoves":0.02213082289552295,
            "Intercept":15.91617862447785
        } }
        ret_val = {}
        features = RTServer.getFeaturesBySessID(sess_id, game_id)
        for model in models.keys():
            ret_val[model] = RTServer.EvaluateModel(models[model], features)

        return ret_val

    ## Function to evaluate a logistic regression model, creating a prediction.
    #  This is based around the equation for probability of Y=1, denoted as p:
    #  p = 1 / (1 + e^-logit(X)),
    #  where X is the input data used to predict Y, and
    #  logit(X) = b0 + b1*x1 + b2*x2 + ... + bn*xn,
    #  where bi are the coefficients.
    #  Based on information at https://www.medcalc.org/manual/logistic_regression.php
    @staticmethod
    def EvaluateModel(model, feature_data) -> float:
        logit = 0
        for coeff in model.keys():
            if coeff == "Intercept":
                logit += model[coeff]
            else:
                logit += model[coeff] * feature_data[coeff]
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

    request = cgi.FieldStorage()
    method = request.getvalue("method")

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
    _cgi_debug(f"method: {method}; result string: {result}", "Info", log_file)
    print(result)
except Exception as err:
    print(f"Error in realtime script! {str(err)}")
    traceback.print_tb(err.__traceback__)
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")
