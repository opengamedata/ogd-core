import json
import logging
import math
import pandas as pd
import random
import re
import sys
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
from feature_extractors.LakelandExtractor import LakelandExtractor
from schemas.TableSchema import TableSchema
from interfaces.MySQLInterface import SQL
from managers.SessionProcessor import SessionProcessor
from models.Model import ModelInputType
# from models.Model import *
from realtime.ModelManager import ModelManager
from schemas.Schema import Schema

## Class to handle API calls for the realtime page.
#  Defines a bunch of static handler functions, one for each valid API call.
class RTServer:

    # Load settings, set up consts.
    ssh_settings = settings["ssh_config"]
    rt_settings  = settings["realtime_config"]
    db_settings  = settings["db_config"]
    DB_NAME_DATA = db_settings["DB_NAME_DATA"]
    DB_TABLE     = db_settings["TABLE"]

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
        ret_val = {}
        start_time = datetime.now()
        active_sessions_raw = RTServer._fetchActiveSessions(game_id=game_id, require_player_id=require_player_id)
        fetch_time = datetime.now() - start_time
        start_time = datetime.now()
        for item in active_sessions_raw:
            sess_id = item[0]
            player_id = item[1]
            # TODO: is require_player_id really coming in as a string?
            if (require_player_id == "false") or re.search("^[a-z,A-Z][0-9]{3}$", player_id):
                prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
                idle_time = prog["idle_time"]
                max_level = prog["max_level"]
                cur_level = prog["cur_level"]
                ret_val[sess_id] = {"session_id":sess_id, "player_id":item[1], "max_level":max_level, "cur_level":cur_level, "idle_time":idle_time}
        # print(f"returning from realtime, with all active sessions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
        ret_val["message"] = f"Time to fetch sessions: {fetch_time}, time to get progress: {datetime.now() - start_time}"
        return ret_val

    @staticmethod
    def getAllActiveSessionsByClassroom(game_id: str, class_id: bool) -> typing.Dict:
        ret_val = {}
        start_time = datetime.now()
        active_sessions_raw = RTServer._fetchActiveSessions(game_id=game_id, require_player_id=True, class_id=class_id)
        fetch_time = datetime.now() - start_time
        start_time = datetime.now()
        for session in active_sessions_raw:
            sess_id = session[0]
            player_id = session[1]
            username = session[2]
            if re.search("^[0-9]+$", player_id):
                prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
                idle_time = prog["idle_time"]
                max_level = prog["max_level"]
                cur_level = prog["cur_level"]
                ret_val[sess_id] = {"session_id":sess_id, "username":username, "max_level":max_level, "cur_level":cur_level, "idle_time":idle_time}
        # print(f"returning from realtime, with all active sessions. Time spent was {(datetime.now()-start_time).seconds} seconds.")
        ret_val["message"] = f"Time to fetch sessions: {fetch_time}, time to get progress: {datetime.now() - start_time}"
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
    def getSessionAndFeaturesBySessID(sess_id: str, game_id: str, features: typing.List = None) -> typing.Dict:
        ret_val: typing.Dict = {}
        # if we got a features list, it'll be a string that we must split.
        if features is not None and type(features) == str:
            features = features.split(",")
        request = Request.IDListRequest(game_id=game_id, session_ids=[sess_id])
        start_time = datetime.now()
        session_data, game_table = RTServer._fetchSessionData(sess_id, settings=settings, request=request)
        utils.Logger.toStdOut(f"Time to fetch session data: {datetime.now() - start_time}", logging.DEBUG)
        try:
            if len(session_data) > 0:
                # return "Line 88: Killing features function in realtime.cgi."
                schema = Schema(schema_name=f"{game_id}.json")
                extractor: Extractor
                if game_id == "WAVES":
                    extractor = WaveExtractor(session_id=sess_id, game_table = game_table, game_schema=schema)
                elif game_id == "CRYSTAL":
                    extractor = CrystalExtractor(session_id=sess_id, game_table = game_table, game_schema=schema)
                elif game_id == "LAKELAND":
                    extractor = LakelandExtractor(session_id=sess_id, game_table=game_table, game_schema=schema, sessions_file=None)
                else:
                    raise Exception("Got an invalid game ID!")

                start_time = datetime.now()
                for row in session_data:
                    col = row[game_table.complex_data_index]
                    complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":row[game_table.event_index]}
                    if "event_custom" not in complex_data_parsed.keys():
                        complex_data_parsed["event_custom"] = row[game_table.event_index]
                    row = list(row)
                    row[game_table.complex_data_index] = complex_data_parsed
                    extractor.extractFromRow(row_with_complex_parsed=row, game_table=game_table)
                extractor.calculateAggregateFeatures()
                utils.Logger.toStdOut(f"Time to process rows: {datetime.now() - start_time}", logging.DEBUG)

                all_features = dict(zip( extractor.getFeatureNames(game_table=game_table, game_schema=schema),
                                            extractor.getCurrentFeatures() ))
                # print(f"all_features: {all_features}")
                # prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
                cur_level = 1 # prog["cur_level"] # TODO: get back to not hard-coding level
                if features is not None and features != None:
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
                utils.Logger.toStdOut(f"error, empty session!", logging.ERROR)
                ret_val = {"error": "Empty Session!"}
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            # print(f"got error in RTServer.py: {msg}")
            # traceback.print_tb(err.__traceback__)
            utils.Logger.toStdOut(f"Got an error in getFeaturesBySessID: {msg}", logging.ERROR)
            print(f"Error: Got an error in getFeaturesBySessID: {msg}", file=sys.stderr)
            # traceback.print_tb(err.__traceback__)
            ret_val = {"error": "Got error in RTServer!"}
            raise err
        finally:
            return {sess_id:{"features": ret_val, "session": session_data, "table": game_table}}

    ## Function to retrieve the game progress in a session.
    #  Specifically, the current level, max level, and current idle time.
    #  Other data could be added as needed.
    @staticmethod
    def getGameProgress(sess_id: str, game_id: str) -> typing.Dict[str, object]:
        max_level: int
        cur_level: int
        idle_time: int
    
        #+++
        start = datetime.now()
        #---
        tunnel,db = SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
        try:
            cursor = db.cursor()
            # filt = f"`session_id`='{sess_id}' AND `event`='COMPLETE'"
            # max_level_raw = SQL.SELECT(cursor=cursor,
            #                                  db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
            #                                  columns=["MAX(level)"], filter=filt)
            filt = f"`session_id`='{sess_id}'"
            cur_level_raw = SQL.SELECT(cursor=cursor,
                                             db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                             columns=["level", "server_time"], filter=filt,\
                                             sort_columns=["client_time"], sort_direction="DESC", limit=1)
            # max_level = max_level_raw[0][0] if max_level_raw[0][0] != None else 0
            cur_level = cur_level_raw[0][0]
            max_level = 1
            # cur_level = 1
            idle_time = (datetime.now() - cur_level_raw[0][1]).seconds
            # idle_time = 5
            #+++
            end = datetime.now()
            time_delta = end - start
            minutes = math.floor(time_delta.total_seconds()/60)
            seconds = time_delta.total_seconds() % 60
            utils.Logger.toStdOut(f"Total time taken to get game progress: {minutes} min, {seconds} sec", logging.DEBUG)
            #---
        except Exception as err:
            #print(f"got error in RTServer.py: {str(err)}")
            utils.Logger.toStdOut(f"Got an error in getGameProgress: {type(err)} {str(err)}", logging.ERROR)
            print(f"Error: Got an error in getGameProgress: {type(err)} {str(err)}", file=sys.stderr)
            raise err
        finally:
            # SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return {"max_level": max_level, "cur_level": cur_level, "idle_time": idle_time}

    ## Handler to get a list of all feature names for a given game.
    #  @param  game_id The id for the game being played in the given session.
    #  @return A dictionary mapping "features" to a list of feature names,
    #          or None if an eror occurred when reading the game schema.
    # @staticmethod
    # def getFeatureNamesByGame(game_id: str) -> typing.Dict[str, typing.List]:
    #     ret_val: typing.Dict[str, typing.List]
    #     try:
    #         schema: Schema = Schema(schema_name=f"{game_id}.json")
    #         ret_val = {"features": schema.feature_list()}
    #     except Exception as err:
    #         utils.Logger.toStdOut(f"Got exception in getFeatureNamesByGame: {type(err)} {str(err)}", logging.ERROR)
    #         utils.Logger.toStdOut("Had to return None", logging.WARNING)
    #         print(f"Got exception in getFeatureNamesByGame: {type(err)} {str(err)}", file=sys.stderr)
    #         ret_val = None
    #     finally:
    #         return ret_val

    ## Handler to get a list of all model names for a given game level.
    #  This is based on the assumption that models for the game are stored in a file
    #  with naming format game_id_models.json.
    #  @param  game_id The id for the game being played in the given session.
    #  @param  level   The level for which we want a list of models
    #  @return A list of all model names.
    # @staticmethod
    # def getModelNamesByGameLevel(game_id: str, level: int) -> typing.List:
    #     ret_val: typing.List

    #     # models = utils.loadJSONFile(filename=f"{game_id}_models.json", path="./models/")
    #     model_mgr = ModelManager(game_id)
    #     models = model_mgr.ListModels(level)
    #     if len(models) < 1:
    #         ret_val = ["No models for given level"]
    #     else:
    #         ret_val = models
    #     return ret_val

    @staticmethod
    def getModelsBySessID(sess_id: str, game_id: str, models):
        # start_time = datetime.now()
        ret_val = {}
        message = ""
        try:
            # prog = RTServer.getGameProgress(sess_id=sess_id, game_id=game_id)
            # max_level = prog["max_level"]
            # cur_level = prog["cur_level"]
            # idle_time = prog["idle_time"]
            # ret_val["max_level"] = {"name": "Max Level", "value": max_level}
            # ret_val["cur_level"] = {"name": "Current Level", "value": cur_level}
            # ret_val["seconds_inactive"] = {"name": "Seconds Inactive", "value": idle_time}
            # model_level = str(max(1, min(8, cur_level)))
            # models = utils.loadJSONFile(filename=f"{game_id}_models.json", path="./models/")
            # print(f"***List of valid models***: {model_list}")
            # Retrieve data for the session, before we start looping over all sessions.
            start_time = datetime.now()
            request = Request.IDListRequest(game_id=game_id, session_ids=[sess_id])
            sess_and_feats_ob = RTServer.getSessionAndFeaturesBySessID(sess_id, game_id)
            sess_and_feats = sess_and_feats_ob[sess_id]
            # TODO: streamline this process. Shouldn't need to call to get the table.
            features_raw = sess_and_feats["features"]
            session_data_raw = sess_and_feats["session"]
            game_table = sess_and_feats["table"]
            # session_data_raw, game_table = RTServer._fetchSessionData(sess_id, settings=settings, request=request)
            session_data = [list(row) for row in session_data_raw]
            for row in session_data:
                col = row[game_table.complex_data_index]
                row[game_table.complex_data_index] = json.loads(col.replace("'", "\"")) if (col is not None) else {"event_custom":row[game_table.event_index]}
            session_data_parsed = [game_table.RowToDict(row) for row in session_data]
            features_parsed = RTServer._parseRawToDict(features_raw)
            fetch_time = datetime.now() - start_time

            start_time = datetime.now()
            model_mgr = ModelManager(game_id)
            # NOTE: We assume current level is the one to use. If player back-tracks, you may end up with "earlier" model relative to max level.
            cur_level = 1; # TODO: eventually, we'll want to actually get levels, for games which use levels.
            model_list = model_mgr.ListModels(cur_level)
            # For each model in the model list, call eval on the proper type of data.
            for model_name in models:
                if model_name in model_list:
                    model = model_mgr.LoadModel(model_name=model_name)
                    try:
                        if model.GetInputType() == ModelInputType.FEATURE:
                            result_list = model.Eval([features_parsed])
                            result_list = result_list[0] # so, technically we get back a list of results for each session given, and we only give one session.
                        elif model.GetInputType() == ModelInputType.SEQUENCE:
                            result_list = model.Eval(session_data_parsed)
                        ret_val[model_name] = {"name": model_name, "success": True, "value": str(result_list)}
                    except Exception as err:
                        ret_val[model_name] = {"name": model_name, "success": False, "value": f"Failed with error {err}"}
                        utils.Logger.toStdOut(f"Got an error in getModelsBySessID: {type(err)} {str(err)}", logging.ERROR)
                        traceback.print_tb(err.__traceback__, file=sys.stderr)
                else:
                    ret_val[model_name] = {"name": model_name, "success": False, "value": f"Invalid model for level {cur_level}!"}
            message = f"Time to get session data: {fetch_time}, time to process models: {datetime.now() - start_time}"
        except Exception as err:
            # print(f"got error in RTServer.py: {str(err)}")
            # traceback.print_tb(err.__traceback__)
            utils.Logger.toStdOut(f"Got an error in getModelsBySessID: {type(err)} {str(err)}", logging.ERROR)
            traceback.print_tb(err.__traceback__, file=sys.stderr)
            # print(f"Got an error in getModelsBySessID: {type(err)} {str(err)}", file=sys.stderr)
            ret_val = {"NoModel": {"name":"No Model", "value":f"No models for {game_id}"}}
            raise err
        finally:
            result = {sess_id:ret_val, "message":message}
            # print(f"returning from realtime, with session_models: {result}") # Time spent was {(datetime.now()-start_time).seconds} seconds.")
            return result

    ## Simple helper method to take in a raw (string) version of a feature from file,
    #  and parse it to a float if the feature is numeric, else maintain it as a string.
    #  @param  features_raw A dictionary mapping feature names to raw (string) values.
    #  @return A dictionary mapping feature names to parsed values (i.e. numeric inputs are parsed to floats)
    @staticmethod
    def _parseRawToDict(features_raw):
        ret_val = {}
        for feature_name in features_raw.keys():
            try:
                ret_val[feature_name] = float(features_raw[feature_name])
            except ValueError:
                ret_val[feature_name] = features_raw[feature_name]
        return ret_val

    @staticmethod
    def _fetchActiveSessions(game_id, require_player_id, class_id=None):
        if RTServer.rt_settings["data_source"] == "DB":
            # if we're using DB, allow realtime settings to override base settings.
            RTServer.db_settings["DB_HOST"]   = RTServer.rt_settings["DB_HOST"]
            RTServer.ssh_settings["SSH_HOST"] = RTServer.rt_settings["SSH_HOST"]
            try:
                tunnel,db = SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
                #+++
                start = datetime.now()
                #---
                cursor = db.cursor()
                start_time = datetime.now() - timedelta(minutes=5)
                # disamb = f"{RTServer.DB_NAME_DATA}.{RTServer.DB_TABLE}"
                player_id_filter = f"AND {RTServer.DB_TABLE}.player_id IS NOT NULL" if require_player_id else ""
                if class_id is not None:
                    join_statement = f"INNER JOIN players ON {RTServer.DB_TABLE}.player_id=players.player_id" 
                    column_names = [f"{RTServer.DB_TABLE}.session_id", f"{RTServer.DB_TABLE}.player_id", "logger.players.username"]
                else:
                    join_statement = ""
                    column_names   = [f"session_id", "player_id"]
                filt = f"{RTServer.DB_TABLE}.app_id='{game_id}' AND {RTServer.DB_TABLE}.server_time > '{start_time.isoformat()}' {player_id_filter}"
                active_sessions_raw = SQL.SELECT(cursor=cursor,
                                                    db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                                    columns=column_names, join=join_statement, filter=filt,\
                                                    sort_columns=["session_id"], distinct=True)
                #+++
                end = datetime.now()
                time_delta = end - start
                minutes = math.floor(time_delta.total_seconds()/60)
                seconds = time_delta.total_seconds() % 60
                utils.Logger.toStdOut(f"Time taken to fetch active sessions from database: {minutes} min, {seconds} sec", logging.DEBUG)
                #---
            except Exception as err:
                msg = f"{type(err)} {str(err)}"
                print(f"Got an error in _fetchActiveSessions: {msg}", file=sys.stderr)
                utils.Logger.toStdOut(f"Got an error in _fetchActiveSessions: {msg}", logging.ERROR)
                raise err
            finally:
                SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
        elif RTServer.rt_settings["data_source"] == "FILE":
            raise Exception("not supported!") # TODO: remove this line after implementing the queries.
            path = RTServer.rt_settings["path"]
            data = pd.read_csv(path, sep="\t")
            if require_player_id:
                # TODO: Add pandas query to get a list of all unique session IDs in the table, paired with a player ID.
                # Any sessions that do not have a player ID should be left out.
                # Results should be stored in active_sessions_raw, as a list of Tuples with form (session_id, player_id)
                active_sessions_raw = list(
                    data[((data['session_id'].unique()) & (data['player_id'] is not None))][
                        'session_id', 'player_id'].itertuples(name=None, index=False)
                )
                pass
            else:
                # TODO: Add pandas query to get a list of all unique session IDs in the table, paired with a player ID *or None*.
                # That is, we don't require a player ID for each session, just include it if it has a value, else leave the column value as None or null or whatever.
                # Results should have same form as the other case.
                active_sessions_raw = list(
                    data[(data['session_id'].unique())][
                        'session_id', 'player_id'].itertuples(name=None, index=False)
                )
                pass
        return active_sessions_raw
    
    @staticmethod
    def _fetchSessionData(session_id, settings, request):
        session_data = []
        if RTServer.rt_settings["data_source"] == "DB":
            try:
                tunnel,db = SQL.prepareDB(db_settings=RTServer.db_settings, ssh_settings=RTServer.ssh_settings)
                game_table = TableSchema.FromDB(db=db, settings=settings, request=request)
                utils.Logger.toStdOut(f"Getting all features for session {session_id}", logging.INFO)
                cursor = db.cursor()
                filt = f"`session_id`='{session_id}'"
                session_data = SQL.SELECT(cursor=cursor,
                                                db_name=RTServer.DB_NAME_DATA, table=RTServer.DB_TABLE,\
                                                filter=filt,\
                                                sort_columns=["session_n", "client_time"])
            except Exception as err:
                msg = f"{type(err)} {str(err)}"
                print(f"Got an error in _fetchSessionData: {msg}", file=sys.stderr)
                traceback.print_tb(err.__traceback__, file=sys.stderr)
                utils.Logger.toStdOut(f"Got an error in _fetchSessionData: {msg}", logging.ERROR)
                # traceback.print_tb(err.__traceback__)
                raise err
            finally:
                SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
        elif RTServer.rt_settings["data_source"] == "FILE":
            raise Exception("not supported!") # TODO: remove this line after implementing the queries.
            path = RTServer.rt_settings["path"]
            data = pd.read_csv(path, sep="\t")
            game_table = TableSchema.FromCSV(data)
            # TODO: Add pandas query to get all rows with given session_id, sorted in ascending order by session_n.
            # Results should be stored in session_data as a list of tuples.
            # Example line of code doing the conversion to list of tuples is here:
            # return list(self._data.loc[self._data['session_id'].isin(id_list)].itertuples(index=False, name=None))
            # Basically, use itertuples(index=False, name=None) to convert from series to tuples, and wrap everything in list(...)
            queried_data = data[(data['session_id'] == session_id)].sort_values("session_n", axis=0, ascending=True, inplace=True, na_position='last')
            session_data = list(queried_data.itertuples(index=False, name=None))

        return session_data, game_table

    # @staticmethod
    # def _ip_to_loc(ip):
    #     # in future, convert ip to a (state, city) pair
    #     return ("Stub:Wisconsin", "Stub:Madison")
