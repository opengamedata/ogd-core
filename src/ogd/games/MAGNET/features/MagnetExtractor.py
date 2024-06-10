## import standard libraries
import bisect
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
## import local files
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.legacy.LegacyFeature import LegacyFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema

## @class MagnetExtractor
#  Extractor subclass for extracting features from Magnet game data.
class MagnetExtractor(LegacyFeature):
    ## Constructor for the MagnetExtractor class.
    #  Initializes some custom private data (not present in base class) for use
    #  when calculating some features.
    #  Sets the sessionID feature.
    #  Further, initializes all Q&A features to -1, representing unanswered questions.
    #
    #  @param session_id The id number for the session whose data is being processed
    #                    by this extractor instance.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with this game is structured.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, params:GeneratorParameters, game_schema:GameSchema, session_id:str):
        super().__init__(params=params, game_schema=game_schema, session_id=session_id)
        # Define custom private data.
        self._game_schema : GameSchema = game_schema
        self._features.setValByName(feature_name="sessionID", new_value=session_id)

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def _updateFromEvent(self, event:Event):
        # put some data in local vars, for readability later.
        level = event.GameState['level']
        if level > self._game_schema._max_level:
            Logger.Log(f"Got an event with level too high, full data:\n{str(event)}")
        # Check for invalid row.
        if self.ExtractionMode == ExtractionMode.SESSION and event.SessionID != self._session_id:
            Logger.Log(f"Got an event with incorrect session id! Expected {self._session_id}, got {event.SessionID}!",
                                logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self._features.getValByName(feature_name="persistentSessionID") == 0:
                self._features.setValByName(feature_name="persistentSessionID", new_value=event.UserData['persistent_session_id'])
            # Ensure we have private data initialized for this level.
            if not level in self._levels:
                bisect.insort(self._levels, level)
                self._features.initLevel(level)
            # 1) record that an event of any kind occurred, for the level & session
            self._features.incValByIndex(feature_name="eventCount", index=level)
            self._features.incAggregateVal(feature_name="sessionEventCount")
            # 2) figure out what type of event we had. If CUSTOM, we'll use the event_custom sub-item.
            event_type = event.EventName.split('.')[0]
            if event_type == "CUSTOM":
                event_type = event.EventData['event_custom']
            # 3) handle cases for each type of event
            match event_type:
                case "COMPLETE":
                    self._extractFromComplete(level=level, event_data=event.EventData)
                case "DRAG_TOOL":
                    pass
                case "DRAG_POLE":
                    pass
                case "PLAYGROUND_EXIT":
                    self._extractFromPlaygroundExit(level=level, event_data=event.EventData)
                case "TUTORIAL_EXIT":
                    self._extractFromTutorialExit(level=level, event_data=event.EventData)
                case _:
                    raise Exception(f"Found an unrecognized event type: {event_type}")

    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    def _calculateAggregateFeatures(self):
        # Calculate per-level averages and percentages, since we can't calculate
        # them until we know how many total events occur.
        totalScore = 0
        for level in self._levels:
            southScore = self._features.getValByIndex(feature_name="southPoleScore", index=level)
            northScore = self._features.getValByIndex(feature_name="northPoleScore", index=level)
            totalScore = totalScore + southScore + northScore
        numPlays = self._features.getValByName(feature_name="numberOfCompletePlays")
        if numPlays != 0:
            avgScore = totalScore / numPlays
        else:
            avgScore = 0
        self._features.setValByName(feature_name="averageScore", new_value=avgScore)


    ## Private function to extract features from a "COMPLETE" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromComplete(self, level:int, event_data:Dict[str,Any]):
        south_score = event_data["guessScore"]["southDist"]
        north_score = event_data["guessScore"]["northDist"]
        south_score_if_switched = event_data["guessScoreIfSwitched"]["northPoleToSouthGuess"]
        north_score_if_switched = event_data["guessScoreIfSwitched"]["southPoleToNorthGuess"]
        num_compasses = event_data["numCompasses"]
        iron_filings = event_data["ironFilingsUsed"]
        magnetic_film = event_data["magneticFilmUsed"]
        times_poles_moved = event_data["numTimesPolesMoved"]
        time_spent = event_data["levelTime"]
        self._features.setValByIndex(feature_name="southPoleScore", index=level, new_value=south_score)
        self._features.setValByIndex(feature_name="northPoleScore", index=level, new_value=north_score)
        self._features.setValByIndex(feature_name="northPoleToSouthGuess", index=level, new_value=south_score_if_switched)
        self._features.setValByIndex(feature_name="southPoleToNorthGuess", index=level, new_value=north_score_if_switched)
        self._features.setValByIndex(feature_name="numberOfCompassesUsed", index=level, new_value=num_compasses)
        self._features.setValByIndex(feature_name="usedIronFilings", index=level, new_value=iron_filings)
        self._features.setValByIndex(feature_name="usedMagneticFilm", index=level, new_value=magnetic_film)
        self._features.setValByIndex(feature_name="numTimesPolesMoved", index=level, new_value=times_poles_moved)
        self._features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self._features.incAggregateVal(feature_name="sessionTime", increment=time_spent)

    ## Private function to extract features from a "PLAYGROUND_EXIT" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromPlaygroundExit(self, level:int, event_data:Dict[str,Any]):
        time_spent = event_data["timeSpent"]
        self._features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self._features.incAggregateVal(feature_name="sessionTime", increment=time_spent)

    ## Private function to extract features from a "TUTORIAL_EXIT" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromTutorialExit(self, level:int, event_data:Dict[str,Any]):
        time_spent = event_data["timeSpent"]
        self._features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self._features.incAggregateVal(feature_name="sessionTime", increment=time_spent)
