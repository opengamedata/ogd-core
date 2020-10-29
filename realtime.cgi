#!C:\Program Files\Python38\python.exe -u
#/usr/bin/python3.6

# Before doing anything at all, send the header.
header = "Content-type:text/plain \r\n\r\n"
print(str(header))

# import standard libraries
import cgi
import cgitb
import json
import logging
import math
import sys
import traceback
from datetime import datetime
# import local files
import Request
import utils
from realtime.RTServer import RTServer
from realtime.SimRTServer import SimRTServer

try:
    # print("{\"msg\": \"test return\"}")
    # quit()

    # set up other global vars as needed:
    request = cgi.FieldStorage()
    method = request.getvalue("method")

    utils.Logger.toStdOut(f"method requested: {method}", logging.INFO)
    #+++
    start = datetime.now()
    #---
    if method == "say_hello":
        body = "Hello, world."
    elif method == "get_all_active_sessions":
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        body = RTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id)
    elif method == "get_all_active_sessions_by_classroom":
        game_id = request.getvalue("gameID")
        class_id = request.getvalue("class_id")
        body = RTServer.getAllActiveSessionsByClassroom(game_id=game_id, class_id=class_id)
    # elif method == "get_active_sessions_by_loc":
    #     game_id = request.getvalue("gameID")
    #     state = request.getvalue("state")
    #     city = request.getvalue("city")
    #     body = RTServer.getActiveSessionsByLoc(game_id=game_id, state=state, city=city)
    # elif method == "get_features_by_sessID":
    #     game_id = request.getvalue("gameID")
    #     sess_id = request.getvalue("sessID")
    #     features = request.getvalue("features")
    #     body = RTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, features=features)
    #     utils.Logger.toStdOut(f"got features by session ID in main realtime code, sess_id={sess_id}, game_id={game_id}", logging.INFO)
    # elif method == "get_feature_names_by_game":
    #     game_id = request.getvalue("gameID")
    #     body = RTServer.getFeatureNamesByGame(game_id=game_id)
    elif method == "get_models_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        models = request.getvalue("models").split(",")
        body = RTServer.getModelsBySessID(sess_id=sess_id, game_id=game_id, models=models)
    # elif method == "get_model_names_by_game":
    #     game_id = request.getvalue("gameID")
    #     body = RTServer.getModelNamesByGameLevel(game_id=game_id)
    elif method == "sim_all_active_sessions":
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id, sim_time=sim_time)
    elif method == "sim_all_active_sessions_by_classroom":
        game_id = request.getvalue("gameID")
        class_id = request.getvalue("class_id")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getAllActiveSessions(game_id=game_id, class_id=class_id, sim_time=sim_time)
    # elif method == "sim_features_by_sessID":
    #     game_id = request.getvalue("gameID")
    #     sess_id = request.getvalue("sessID")
    #     features = request.getvalue("features")
    #     sim_time = int(request.getvalue("sim_time"))
    #     body = SimRTServer.getFeaturesBySessID(sess_id=sess_id, game_id=game_id, sim_time=sim_time, features=features)
    #     utils.Logger.toStdOut(f"got simulated features by session ID in main realtime code, sess_id={sess_id}, game_id={game_id}, sim_time={sim_time}", logging.INFO)
    elif method == "sim_models_by_sessID":
        game_id = request.getvalue("gameID")
        sess_id = request.getvalue("sessID")
        models = request.getvalue("models").split(",")
        sim_time = int(request.getvalue("sim_time"))
        body = SimRTServer.getModelsBySessID(sess_id=sess_id, game_id=game_id, sim_time=sim_time, models=models)
    #+++
    end = datetime.now()
    time_delta = end - start
    minutes = math.floor(time_delta.total_seconds()/60)
    seconds = time_delta.total_seconds() % 60
    utils.Logger.toFile(f"Total time taken to {method}: {minutes} min, {seconds} sec", logging.DEBUG)
    #---

    result: str = json.dumps(body, default=lambda ob: ob.isoformat() if type(ob) == datetime else json.dumps(ob))
    print(result)
except Exception as err:
    msg = f"{type(err)} {str(err)}"
    print(f"Error in realtime script! {msg}, traceback:\n{traceback.format_exc()}", file=sys.stderr)
    traceback.print_tb(err.__traceback__, file=sys.stderr)
    utils.Logger.toFile(f"Error in realtime script! {msg}, traceback:\n{traceback.format_exc()}", level=logging.ERROR)
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
