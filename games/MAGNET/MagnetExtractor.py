## import standard libraries
import bisect
import json
import logging
import typing
## import local files
import utils
from extractors.Extractor import Extractor
from schemas.TableSchema import TableSchema
from schemas.GameSchema import GameSchema

## @class MagnetExtractor
#  Extractor subclass for extracting features from Magnet game data.
class MagnetExtractor(Extractor):
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
    def __init__(self, session_id: int, game_table: TableSchema, game_schema: GameSchema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        # Define custom private data.
        self.features.setValByName(feature_name="sessionID", new_value=session_id)

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def extractFeaturesFromRow(self, row_with_complex_parsed, game_table: TableSchema):
        # put some data in local vars, for readability later.
        level = row_with_complex_parsed[game_table.level_index]
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        # Check for invalid row.
        row_sess_id = row_with_complex_parsed[game_table.session_id_index]
        if row_sess_id != self.session_id:
            utils.Logger.toFile(f"Got a row with incorrect session id! Expected {self.session_id}, got {row_sess_id}!",
                                logging.ERROR)
        elif "event_custom" not in event_data_complex_parsed.keys():
            utils.Logger.toFile("Invalid event_data_complex, does not contain event_custom field!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="persistentSessionID") == 0:
                self.features.setValByName(feature_name="persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # Ensure we have private data initialized for this level.
            if not level in self.levels:
                bisect.insort(self.levels, level)
                self.features.initLevel(level)
            # First, record that an event of any kind occurred, for the level & session
            self.features.incValByIndex(feature_name="eventCount", index=level)
            self.features.incAggregateVal(feature_name="sessionEventCount")
            # Then, handle cases for each type of event
            event_type = event_data_complex_parsed["event_custom"]
            if event_type == "COMPLETE":
                self._extractFromComplete(level, event_client_time, event_data_complex_parsed)
            elif event_type == "DRAG_TOOL":
                pass
            elif event_type == "DRAG_POLE":
                pass
            elif event_type == "PLAYGROUND_EXIT":
                self._extractFromPlaygroundExit(level, event_client_time, event_data_complex_parsed)
            elif event_type == "TUTORIAL_EXIT":
                self._extractFromTutorialExit(level, event_client_time, event_data_complex_parsed)
            else:
                raise Exception(f"Found an unrecognized event type: {event_type}")

    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    def calculateAggregateFeatures(self):
        # Calculate per-level averages and percentages, since we can't calculate
        # them until we know how many total events occur.
        totalScore = 0
        for level in self.levels:
            southScore = self.features.getValByIndex(feature_name="southPoleScore", index=level)
            northScore = self.features.getValByIndex(feature_name="northPoleScore", index=level)
            totalScore = totalScore + southScore + northScore
        numPlays = self.features.getValByName(feature_name="numberOfCompletePlays")
        if numPlays != 0:
            avgScore = totalScore / numPlays
        else:
            avgScore = 0
        self.features.setValByName(feature_name="averageScore", new_value=avgScore)


    ## Private function to extract features from a "COMPLETE" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromComplete(self, level, event_client_time, event_data):
        south_score = event_data["guessScore"]["southDist"]
        north_score = event_data["guessScore"]["northDist"]
        south_score_if_switched = event_data["guessScoreIfSwitched"]["northPoleToSouthGuess"]
        north_score_if_switched = event_data["guessScoreIfSwitched"]["southPoleToNorthGuess"]
        num_compasses = event_data["numCompasses"]
        iron_filings = event_data["ironFilingsUsed"]
        magnetic_film = event_data["magneticFilmUsed"]
        times_poles_moved = event_data["numTimesPolesMoved"]
        time_spent = event_data["levelTime"]
        self.features.setValByIndex(feature_name="southPoleScore", index=level, new_value=south_score)
        self.features.setValByIndex(feature_name="northPoleScore", index=level, new_value=north_score)
        self.features.setValByIndex(feature_name="northPoleToSouthGuess", index=level, new_value=south_score_if_switched)
        self.features.setValByIndex(feature_name="southPoleToNorthGuess", index=level, new_value=north_score_if_switched)
        self.features.setValByIndex(feature_name="numberOfCompassesUsed", index=level, new_value=num_compasses)
        self.features.setValByIndex(feature_name="usedIronFilings", index=level, new_value=iron_filings)
        self.features.setValByIndex(feature_name="usedMagneticFilm", index=level, new_value=magnetic_film)
        self.features.setValByIndex(feature_name="numTimesPolesMoved", index=level, new_value=times_poles_moved)
        self.features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self.features.incAggregateVal(feature_name="sessionTime", increment=time_spent)

    ## Private function to extract features from a "PLAYGROUND_EXIT" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromPlaygroundExit(self, level, event_client_time, event_data):
        time_spent = event_data["timeSpent"]
        self.features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self.features.incAggregateVal(feature_name="sessionTime", increment=time_spent)

    ## Private function to extract features from a "TUTORIAL_EXIT" event.
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromTutorialExit(self, level, event_client_time, event_data):
        time_spent = event_data["timeSpent"]
        self.features.setValByIndex(feature_name="levelTime", index=level, new_value=time_spent)
        self.features.incAggregateVal(feature_name="sessionTime", increment=time_spent)
