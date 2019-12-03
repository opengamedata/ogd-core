## import standard libraries
import bisect
import json
import logging
import typing
## import local files
import utils
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema

## @class CrystalExtractor
#  Extractor subclass for extracting features from Crystal game data.
class CrystalExtractor(Extractor):
    ## Constructor for the CrystalExtractor class.
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
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        # Define custom private data.
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
        self.totalMoleculeDragDuration      = {}
        self.active_begin = None
        self.features.setValByName(feature_name="sessionID", new_value=session_id)
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self.features.getValByName(feature_name="questionAnswered").keys():
            self.features.setValByIndex(feature_name="questionAnswered", index=ans, new_value=None)
        for q in self.features.getValByName(feature_name="questionCorrect"):
            self.features.setValByIndex(feature_name="questionCorrect", index=q, new_value=None)

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        # put some data in local vars, for readability later.
        level = row_with_complex_parsed[game_table.level_index]
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        # Check for invalid row.
        row_sess_id = row_with_complex_parsed[game_table.session_id_index]
        if row_sess_id != self.session_id:
            utils.Logger.toFile(f"Got a row with incorrect session id! Expected {self.session_id}, got {row_sess_id}!", logging.ERROR)
        elif "event_custom" not in event_data_complex_parsed.keys():
            utils.Logger.toFile("Invalid event_data_complex, does not contain event_custom field!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="persistentSessionID") == 0:
                self.features.setValByName(feature_name="persistentSessionID",
                                           new_value   = row_with_complex_parsed[game_table.pers_session_id_index])
            # Ensure we have private data initialized for this level.
            if not level in self.levels:
                bisect.insort(self.levels, level)
                self.features.initLevel(level)
                self.totalMoleculeDragDuration[level] = 0
                # self.start_times[level] = None
                # self.end_times[level] = None
            # First, record that an event of any kind occurred, for the level & session
            self.features.incValByIndex(feature_name="eventCount", index=level)
            self.features.incAggregateVal(feature_name="sessionEventCount")
            # Then, handle cases for each type of event
            event_type = event_data_complex_parsed["event_custom"]
            if event_type == "BEGIN":
                self._extractFromBegin(level, event_client_time)
            elif event_type == "COMPLETE":
                self._extractFromComplete(level, event_client_time, event_data_complex_parsed)
            elif event_type == "MOLECULE_RELEASE":
                self._extractFromMoleculeRelease(level, event_data_complex_parsed)
            elif event_type == "MOLECULE_ROTATE":
                self._extractFromMoleculeRotate(level, event_data_complex_parsed)
            elif event_type == "BACK_TO_MENU":
                self._extractFromMenuBtn(level, event_client_time)
            elif event_type == "CLEAR_BTN_PRESS":
                self._extractFromClearBtnPress(level)
            elif event_type in "MUSEUM_CLOSE" :
                self._extractFromMuseumClose(event_data_complex_parsed)
            elif event_type == "QUESTION_ANSWER":
                self._extractFromQuestionAnswer(event_data_complex_parsed)
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))
                                               
    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    def calculateAggregateFeatures(self):
        # Calculate per-level averages and percentages, since we can't calculate
        # them until we know how many total events occur.
        for level in self.levels:
            count = self.features.getValByIndex(feature_name="moleculeMoveCount", index=level)
            avg = self.totalMoleculeDragDuration[level] / count if count > 0 else count
            self.features.setValByIndex(feature_name="avgMoleculeDragDurationInSecs", index=level, new_value=avg)

    ## Private function to extract features from a "BEGIN" event.
    #  The features affected are:
    #  - start_times (used to calculate durationInSecs and sessionDurationInSecs)
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromBegin(self, level, event_client_time):
        self.features.incValByIndex(feature_name="beginCount", index=level, increment=1)
        if self.active_begin == None:
            self.start_times[level] = event_client_time
        elif self.active_begin == level:
            pass # in this case, just keep going.
        else:
            self.end_times[self.active_begin] = event_client_time
            time_taken = self._calcLevelTime(self.active_begin)
            self.features.incValByIndex(feature_name="durationInSecs", index=self.active_begin, increment=time_taken)
            self.features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self.start_times[level] = event_client_time
        # in any case, current level now has active begin event.
        self.active_begin = level

    ## Private function to extract features from a "COMPLETE" event.
    #  The features affected are:
    #  - end_times (used to calculate durationInSecs and sessionDurationInSecs)
    #  - durationInSecs
    #  - sessionDurationInSecs
    #  - completesCount
    #  - finalScore
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    #  @param event_data        Parsed JSON data from the row being processed.
    def _extractFromComplete(self, level, event_client_time, event_data):
        self.features.incValByIndex(feature_name="completesCount", index=level, increment=1)
        if self.active_begin == None:
            sess_id = self.features.getValByName(feature_name="sessionID")
            utils.Logger.toFile(f"Got a 'Complete' event when there was no active 'Begin' event! Level {level}, Sess ID: {sess_id}", logging.ERROR)
        else:
            self.end_times[level] = event_client_time
            time_taken = self._calcLevelTime(level)
            self.features.incValByIndex(feature_name="durationInSecs", index=level, increment=time_taken)
            self.features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self.active_begin = None
            score = event_data["stability"]["pack"] + event_data["stability"]["charge"]
            max_score = max(score, self.features.getValByIndex(feature_name="finalScore", index=level))
            self.features.setValByIndex(feature_name="finalScore", index=level, new_value=max_score)

    ## Private function to extract features from a "BACK_TO_MENU" event.
    #  The features affected are:
    #  - end_times (used to calculate totalLevelTime and avgLevelTime)
    #  - durationInSecs
    #  - sessionDurationInSecs
    #  - menuBtnCount
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromMenuBtn(self, level, event_client_time):
        self.features.incValByIndex(feature_name="menuBtnCount", index=level)
        if self.active_begin == None:
            sess_id = self.features.getValByName(feature_name="sessionID")
            utils.Logger.toFile(f"Got a 'Back to Menu' event when there was no active 'Begin' event! Sess ID: {sess_id}", logging.ERROR)
        else:
            self.end_times[level] = event_client_time
            time_taken = self._calcLevelTime(level)
            self.features.incValByIndex(feature_name="durationInSecs", index=level, increment=time_taken)
            self.features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self.active_begin = None

    ## Private function to extract features from a "MOLECULE_RELEASE" event.
    #  The features affected are:
    #  - totalMoleculeDragDuration (used to calculate avgMoleculeDragDurationInSecs)
    #  - moleculeMoveCount
    #  - sessionMoleculeMoveCount
    #
    #  @param level      The level being played when event occurred.
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMoleculeRelease(self, level, event_data):
        if not level in self.totalMoleculeDragDuration.keys():
            self.totalMoleculeDragDuration[level] = 0
        self.totalMoleculeDragDuration[level] += event_data["time"]
        self.features.incValByIndex(feature_name="moleculeMoveCount", index=level)
        self.features.incAggregateVal(feature_name="sessionMoleculeMoveCount")

    ## Private function to extract features from a "MOLECULE_ROTATE" event.
    #  The features affected are:
    #  - stampRotateCount
    #  - sessionStampRotateCount
    #  - singleRotateCount
    #  - sessionSingleRotateCount
    #
    #  @param level      The level being played when event occurred.
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMoleculeRotate(self, level, event_data):
        if event_data["isStamp"]:
            self.features.incValByIndex(feature_name="stampRotateCount", index=level)
            self.features.incAggregateVal(feature_name="sessionStampRotateCount")
        else:
            self.features.incValByIndex(feature_name="singleRotateCount", index=level)
            self.features.incAggregateVal(feature_name="sessionSingleRotateCount")

    ## Private function to extract features from a "CLEAR_BTN_PRESS" event.
    #  The features affected are:
    #  - clearBtnPresses
    #  - sessionClearBtnPresses
    #
    #  @param level The level being played when clear button was pressed.
    def _extractFromClearBtnPress(self, level):
        self.features.incValByIndex(feature_name="clearBtnPresses", index=level)
        self.features.incAggregateVal(feature_name="sessionClearBtnPresses")

    ## Private function to extract features from a "MUSEUM_CLOSE" event.
    #  The features affected are:
    #  - sessionMuseumDurationInSecs
    #
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMuseumClose(self, event_data):
        self.features.incAggregateVal(feature_name="sessionMuseumDurationInSecs", increment=event_data["timeOpen"])

    ## Private function to extract features from a "QUESTION_ANSWER" event.
    #  The features affected are:
    #  - questionAnswered
    #  - questionCorrect
    #
    #  @param event_data_parsed Parsed JSON data from the row being processed.
    def _extractFromQuestionAnswer(self, event_data):
        q_num = event_data["question"]
        self.features.setValByIndex(feature_name="questionAnswered", index=q_num, new_value=event_data["answered"])
        correctness = 1 if event_data["answered"] == event_data["answer"] else 0
        self.features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value= correctness)

    ## Private function to calculate the time spent on a level for the given level
    #  and play index (each level may have been played multiple times).
    #
    #  @param lvl      The level whose play time should be calculated
    #  @return         The play time if level is valid, -1 if level was not
    #                  completed, 0 if level was never attempted.
    def _calcLevelTime(self, lvl:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl] - self.start_times[lvl]).total_seconds()
            else:
                return -1
        else:
            return 0