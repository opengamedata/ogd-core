import json
import logging
import math
import random
import re
import traceback
import typing
from datetime import datetime, timedelta
# # import local files
import Request
import utils
from config import settings
from feature_extractors.Extractor import Extractor
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.WaveExtractor import WaveExtractor
from GameTable import GameTable
from managers.ProcManager import ProcManager
from schemas.Schema import Schema

## Class to handle API calls for the realtime page.
#  Defines a bunch of static handler functions, one for each valid API call.
class RTServer:

    # Load settings, set up consts.
    db_settings = settings["db_config"]
    DB_NAME_DATA = db_settings["DB_NAME_DATA"]
    DB_TABLE = db_settings["table"]
    ssh_settings = settings["ssh_config"]

    ## Handler to retrieve all active sessions for a given game.
    #  If the require_player_id flag is set to true, only players with a value
    #  in the playerID column will be returned.
    #  @param game_id The ID name of the game whose sessions should be returned.
    #  @param require_player_id A flag to determine whether to filter out sessions
    #                           lacking a valid playerID.
    #  @return A dictionary mapping session ids to some data about the session.
    #          Specifically, we get each session's max completed level, current
    #          level, and time since last move.
    @staticmethod
    def getAllActiveSessions(game_id: str, require_player_id: bool) -> typing.Dict:
        # start_time = datetime.now()
        tunnel,db = utils.SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
        ret_val = {}
        try:
            cursor = db.cursor()
            start_time = datetime.now() - timedelta(minutes=5)
            player_id_filter = "AND `player_id` IS NOT NULL" if require_player_id else ""
            filt = f"`app_id`='{game_id}' AND `server_time` > '{start_time.isoformat()}' {player_id_filter}"
            active_sessions_raw = utils.SQL.SELECT(cursor=cursor,
                                                   db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                                   columns=["session_id", "player_id"], filter=filt,\
                                                   sort_columns=["session_id"], distinct=True)

            for item in active_sessions_raw:
                sess_id = item[0]
                player_id = item[1]
                if (require_player_id == "false") or re.search("^[a-z,A-Z][0-9]{3}$", player_id):
                    prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
                    idle_time = prog["idle_time"]
                    max_level = prog["max_level"]
                    cur_level = prog["cur_level"]
                    ret_val[sess_id] = {"session_id":sess_id, "player_id":item[1], "max_level":max_level, "cur_level":cur_level, "idle_time":idle_time}
            # print(f"returning from realtime, with all active sessions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
        except Exception as err:
            print(f"got error in RTServer.py: {str(err)}")
            utils.Logger.toFile(f"Got an error in getAllActiveSessions: {str(err)}", logging.ERROR)
            raise err
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return ret_val

    ## Handler to retrieve features for a given session.
    #  For now, at least, the game ID must be given as well, in order to load
    #  information about the way that data from that game is structured.
    #  In theory, we may be able to get the game ID by pulling it from the database,
    #  but it's easier just to make it a parameter for the call.
    #  @param sess_id  The id number for the session whose features are needed.
    #  @param game_id  The id for the game being played in the given session.
    #  @param features An optional list of specific features to be retrieved.
    #                  By default, all available features are retrieved.
    #  @return A dictionary mapping feature names to feature values.
    #          If a features argument was given, only returns the corresponding features.
    @staticmethod
    def getFeaturesBySessID(sess_id: str, game_id: str, features: typing.List = None) -> typing.Dict:
        tunnel,db = utils.SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
        ret_val: typing.Dict
        # if we got a features list, it'll be a string that we must split.
        if features is not None and type(features) == str:
            features = features.split(",")
        try:
            utils.Logger.toFile(f"Getting all features for session {sess_id}", logging.INFO)
            cursor = db.cursor()
            filt = f"`session_id`='{sess_id}'"
            session_data = utils.SQL.SELECT(cursor=cursor,
                                            db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                            filter=filt,\
                                            sort_columns=["session_n", "client_time"])
            if len(session_data) > 0:
                request = Request.IDListRequest(game_id=game_id, session_ids=[sess_id])
                game_table = GameTable(db, settings, request)
                # return "Line 88: Killing features function in realtime.cgi."
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
                extractor.calculateAggregateFeatures()
                all_features = dict(zip( extractor.getFeatureNames(game_table=game_table, game_schema=schema),
                                            extractor.getCurrentFeatures() ))
                # print(f"all_features: {all_features}")
                prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
                cur_level = prog["cur_level"]
                ret_val = {}
                if features is not None and features != "null":
                    for feature_name in features:
                        if feature_name in all_features.keys():
                            ret_val[feature_name] = {"name": feature_name, "value": all_features[feature_name]}
                        elif feature_name in schema.perlevel_features():
                            ret_val[feature_name] = {"name": feature_name, "value": all_features[f"lvl{cur_level}_{feature_name}"]}
                        else:
                            ret_val[feature_name] = {"name": feature_name, "value":None }
                    # ret_val = {i:all_features[i] for i in features}
                else:
                    ret_val = all_features
            else:
                print("error, empty session!")
                utils.Logger.toFile(f"error, empty session! all_features: {all_features}", logging.ERROR)
                ret_val = {"error": "Empty Session!"}
        except Exception as err:
            print(f"got error in RTServer.py: {str(err)}")
            utils.Logger.toFile(f"Got an error in getFeaturesBySessID: {str(err)}", logging.ERROR)
            traceback.print_tb(err.__traceback__)
            raise err
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return {sess_id:ret_val}

    ## Function to retrieve the game progress in a session.
    #  Specifically, the current level, max level, and current idle time.
    #  Other data could be added as needed.
    @staticmethod
    def getGameProgress(sess_id: str, game_id: str) -> typing.Dict[str, object]:
        max_level: int
        cur_level: int
        idle_time: int
    
        tunnel,db = utils.SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
        try:
            cursor = db.cursor()
            filt = f"`session_id`='{sess_id}' AND `event`='COMPLETE'"
            max_level_raw = utils.SQL.SELECT(cursor=cursor,
                                             db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                             columns=["MAX(level)"], filter=filt)
            filt = f"`session_id`='{sess_id}'"
            cur_level_raw = utils.SQL.SELECT(cursor=cursor,
                                             db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                             columns=["level", "server_time"], filter=filt, limit=1,\
                                             sort_columns=["client_time"], sort_direction="DESC")
            max_level = max_level_raw[0][0] if max_level_raw[0][0] != None else 0
            cur_level = cur_level_raw[0][0]
            idle_time = (datetime.now() - cur_level_raw[0][1]).seconds
        except Exception as err:
            #print(f"got error in RTServer.py: {str(err)}")
            utils.Logger.toFile(f"Got an error in getGameProgress: {str(err)}", logging.ERROR)
            raise err
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return {"max_level": max_level, "cur_level": cur_level, "idle_time": idle_time}

    @staticmethod
    def getFeatureNamesByGame(game_id: str) -> typing.Dict[str, typing.List]:
        ret_val: typing.Dict[str, typing.List]
        try:
            schema: Schema = Schema(schema_name=f"{game_id}.json")
            ret_val = {"features": schema.feature_list()}
        except Exception as err:
            utils.Logger.toFile(f"Got exception in getFeatureNamesByGame: {str(err)}", logging.ERROR)
            utils.Logger.toFile("Had to return None", logging.WARNING)
            ret_val = None
        finally:
            return ret_val

    @staticmethod
    def getPredictionNamesByGameLevel(game_id: str, level: int):
        ret_val: typing.List

        models = utils.loadJSONFile(filename=f"{game_id}_models.json", path="./models/")
        if level in models.keys():
            ret_val = models[level].keys()
        else:
            ret_val = ["No models for given level"]
        return ret_val

    @staticmethod
    def getPredictionsBySessID(sess_id: str, game_id: str, predictions):
        # start_time = datetime.now()
        tunnel,db = utils.SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
        try:
            prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
            max_level = prog["max_level"]
            cur_level = prog["cur_level"]
            idle_time = prog["idle_time"]

            models = utils.loadJSONFile(filename=f"{game_id}_models.json", path="./models/")
            ret_val = {}
            ret_val["max_level"] = {"name": "Max Level", "value": max_level}
            ret_val["cur_level"] = {"name": "Current Level", "value": cur_level}
            ret_val["seconds_inactive"] = {"name": "Seconds Inactive", "value": idle_time}
            features_raw = RTServer.getFeaturesBySessID(sess_id, game_id)
            features_parsed = RTServer._parseRawToDict(features_raw[sess_id])
            model_level = str(max(1, min(8, cur_level)))
            for model in models[model_level].keys():
                raw_val = RTServer.EvaluateLogRegModel(models[model_level][model], features_parsed)
                name: str
                if "display_name" in models[model_level][model].keys():
                    name = models[model_level][model]["display_name"]
                else:
                    name = model
                ret_val[model] = {"name": name, "value": str(round(raw_val * 100)) + "%"}

        except Exception as err:
            #print(f"got error in RTServer.py: {str(err)}")
            utils.Logger.toFile(f"Got an error in getPredictionsBySessID: {str(err)}", logging.ERROR)
            ret_val = {"NoModel": "No models for given game"}
            raise err
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            # print(f"returning from realtime, with session_predictions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
            return {sess_id:ret_val}

    @staticmethod
    def _parseRawToDict(features_raw):
        ret_val = {}
        for feature_name in features_raw.keys():
            try:
                ret_val[feature_name] = float(features_raw[feature_name])
            except ValueError:
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
            # case where coefficient is a normal feature
            if coeff in feature_data.keys():
                try:
                    logit += model[coeff] * feature_data[coeff]
                except Exception as err:
                    print(f"Got error when trying to add {coeff} term. Value is {feature_data[coeff]}. Type is {type(feature_data[coeff])}")
                    raise err
            # enum case, where we have coefficient = feature_name.enum_val
            elif re.search("\w+\.\w+", coeff):
                pieces = coeff.split(".")
                if pieces[0] in feature_data.keys():
                    logit += model[coeff] * (1.0 if feature_data[pieces[0]] == pieces[1] else 0.0)
                else:
                    print(f"Found an element of model that is not a feature: {coeff}")
            # specific cases, where we just hardcode a thing that must be consistent across all models.
            elif coeff == "Intercept":
                logit += model[coeff]
            elif coeff == "display_name":
                pass
            # default case, print a line.
            else:
                print(f"Found an element of model that is not a feature: {coeff}")
        # print(f"logit: {logit}")
        p = 1 / (1 + math.exp(-logit))
        return p

    # @staticmethod
    # def _ip_to_loc(ip):
    #     # in future, convert ip to a (state, city) pair
    #     return ("Stub:Wisconsin", "Stub:Madison")