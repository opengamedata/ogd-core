#!C:\Program Files\Python38\python.exe -u
#/usr/bin/python3.6
# import standard libraries
import cgi
import cgitb
import json
import logging
import math
import traceback
from datetime import datetime
# # import local files
import Request
import utils
from RTServer import RTServer
from SimRTServer import SimRTServer

try:
    header = "Content-type:text/plain \r\n\r\n"
    print(str(header))
    # print("test return")
    # quit()

    # set up other global vars as needed:
    request = cgi.FieldStorage()
    method = request.getvalue("method")

    utils.Logger.toStdOut(f"method requested: {method}", logging.INFO)
    if method == "say_hello":
        body = "Hello, world."
    elif method == "get_all_active_sessions":
        #+++
        start = datetime.now()
        #---
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        body = RTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id)
        #+++
        end = datetime.now()
        time_delta = end - start
        minutes = math.floor(time_delta.total_seconds()/60)
        seconds = time_delta.total_seconds() % 60
        utils.Logger.toFile(f"Total time taken to get active sessions: {minutes} min, {seconds} sec", logging.DEBUG)
        #---
    # elif method == "get_active_sessions_by_loc":
    #     game_id = request.getvalue("gameID")
    #     state = request.getvalue("state")
    #     city = request.getvalue("city")
    #     body = RTServer.getActiveSessionsByLoc(game_id=game_id, state=state, city=city)
    elif method == "get_features_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        features = request.getvalue("features")
        body = RTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, features=features)
        utils.Logger.toStdOut(f"got features by session ID in main realtime code, sess_id={sess_id}, game_id={game_id}", logging.INFO)
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
        body = RTServer.getPredictionNamesByGameLevel(game_id=game_id)
    elif method == "sim_all_active_sessions":
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id, sim_time=sim_time)
    elif method == "sim_features_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        features = request.getvalue("features")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, sim_time=sim_time, features=features)
        utils.Logger.toStdOut(f"got simulated features by session ID in main realtime code, sess_id={sess_id}, game_id={game_id}, sim_time={sim_time}", logging.INFO)
    elif method == "sim_predictions_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        predictions = request.getvalue("predictions")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getPredictionsBySessID(sess_id=sess_id, game_id=game_id, sim_time=sim_time, predictions=predictions)

    result: str = json.dumps(body, default=lambda ob: ob.isoformat() if type(ob) == datetime else json.dumps(ob))
    print(result)
except Exception as err:
    msg = f"{type(err)} {str(err)}"
    print(f"Error in realtime script! {msg}, traceback:\n{traceback.format_exc()}")
    traceback.print_tb(err.__traceback__)
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{msg}\n")
