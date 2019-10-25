#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
#/usr/bin/python3.6
# import standard libraries
import cgi
import cgitb
import json
import logging
import traceback
from datetime import datetime
# # import local files
import Request
import utils
from RTServer import RTServer

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
        game_id = request.getvalue("gameID")
        require_player_id = request.getvalue("require_player_id")
        body = RTServer.getAllActiveSessions(game_id=game_id, require_player_id=require_player_id)
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

    result: str = json.dumps(body, default=lambda ob: ob.isoformat() if type(ob) == datetime else json.dumps(ob))
    print(result)
except Exception as err:
    print(f"Error in realtime script! {str(err)}, traceback:\n{traceback.format_exc()}")
    traceback.print_tb(err.__traceback__)
    #print(f"Traceback: {traceback.print_stack(limit=10)}")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")
