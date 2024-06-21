## import standard libraries
import bisect
import logging
import typing
from datetime import datetime
from typing import Any, Dict, List, Optional
## import local files
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.legacy.LegacyFeature import LegacyFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema

# temp comment

## @class CrystalExtractor
#  Extractor subclass for extracting features from Crystal game data.
class CrystalExtractor(LegacyFeature):
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
    def __init__(self, params:GeneratorParameters, game_schema:GameSchema, session_id:str):
        super().__init__(params=params, game_schema=game_schema, session_id=session_id)
        # Define custom private data.
        self._start_times: typing.Dict       = {}
        self._end_times:   typing.Dict       = {}
        self._totalMoleculeDragDuration      = {}
        self._active_begin = None
        self._features.setValByName(feature_name="sessionID", new_value=session_id)
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self._features.getValByName(feature_name="questionAnswered").keys():
            self._features.setValByIndex(feature_name="questionAnswered", index=ans, new_value=None)
        for q in self._features.getValByName(feature_name="questionCorrect"):
            self._features.setValByIndex(feature_name="questionCorrect", index=q, new_value=None)

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def _updateFromEvent(self, event:Event):
        # put some data in local vars, for readability later.
        level = event.GameState['level']
        event_client_time = event.Timestamp
        # Check for invalid row.
        if self.ExtractionMode == ExtractionMode.SESSION and event.SessionID != self._session_id:
            Logger.Log(f"Got a row with incorrect session id! Expected {self._session_id}, got {event.SessionID}!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self._features.getValByName(feature_name="persistentSessionID") == 0:
                self._features.setValByName(feature_name="persistentSessionID", new_value=event.UserData['persistent_session_id'])
            # Ensure we have private data initialized for this level.
            if not level in self._levels:
                bisect.insort(self._levels, level)
                self._features.initLevel(level)
                self._totalMoleculeDragDuration[level] = 0
                # self.start_times[level] = None
                # self.end_times[level] = None
            # 1) record that an event of any kind occurred, for the level & session
            self._features.incValByIndex(feature_name="eventCount", index=level)
            self._features.incAggregateVal(feature_name="sessionEventCount")
            # 2) figure out what type of event we had. If CUSTOM, we'll use the event_custom sub-item.
            event_type = event.EventName.split('.')[0]
            if event_type == "CUSTOM":
                event_type = event.EventData['event_custom']
            # 3) handle cases for each type of event
            match event_type:
                case "BEGIN":
                    self._extractFromBegin(level, event_client_time)
                case "COMPLETE":
                    self._extractFromComplete(level, event_client_time, event.EventData)
                case "MOLECULE_RELEASE":
                    self._extractFromMoleculeRelease(level, event.EventData)
                case "MOLECULE_ROTATE":
                    self._extractFromMoleculeRotate(level, event.EventData)
                case "BACK_TO_MENU":
                    self._extractFromMenuBtn(level, event_client_time)
                case "CLEAR_BTN_PRESS":
                    self._extractFromClearBtnPress(level)
                case "MUSEUM_CLOSE" :
                    self._extractFromMuseumClose(event.EventData)
                case "QUESTION_ANSWER":
                    self._extractFromQuestionAnswer(event.EventData)
                case _:
                    raise Exception(f"Found an unrecognized event type: {event_type}")
                                               
    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    def _calculateAggregateFeatures(self):
        # Calculate per-level averages and percentages, since we can't calculate
        # them until we know how many total events occur.
        for level in self._levels:
            count = self._features.getValByIndex(feature_name="moleculeMoveCount", index=level)
            avg = self._totalMoleculeDragDuration[level] / count if (count is not None and count > 0) else count
            self._features.setValByIndex(feature_name="avgMoleculeDragDurationInSecs", index=level, new_value=avg)

    ## Private function to extract features from a "BEGIN" event.
    #  The features affected are:
    #  - start_times (used to calculate durationInSecs and sessionDurationInSecs)
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromBegin(self, level, event_client_time:datetime):
        self._features.incValByIndex(feature_name="beginCount", index=level, increment=1)
        if self._active_begin == None:
            self._start_times[level] = event_client_time
        elif self._active_begin == level:
            pass # in this case, just keep going.
        else:
            self._end_times[self._active_begin] = event_client_time
            time_taken = self._calcLevelTime(self._active_begin)
            self._features.incValByIndex(feature_name="durationInSecs", index=self._active_begin, increment=time_taken)
            self._features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self._start_times[level] = event_client_time
        # in any case, current level now has active begin event.
        self._active_begin = level

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
    def _extractFromComplete(self, level, event_client_time:datetime, event_data:Dict[str,Any]):
        self._features.incValByIndex(feature_name="completesCount", index=level, increment=1)
        if self._active_begin == None:
            sess_id = self._features.getValByName(feature_name="sessionID")
            Logger.Log(f"Got a 'Complete' event when there was no active 'Begin' event! Level {level}, Sess ID: {sess_id}", logging.ERROR)
        else:
            self._end_times[level] = event_client_time
            time_taken = self._calcLevelTime(level)
            self._features.incValByIndex(feature_name="durationInSecs", index=level, increment=time_taken)
            self._features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self._active_begin = None
            score = event_data["stability"]["pack"] + event_data["stability"]["charge"]
            max_score = max(score, self._features.getValByIndex(feature_name="finalScore", index=level))
            self._features.setValByIndex(feature_name="finalScore", index=level, new_value=max_score)

    ## Private function to extract features from a "BACK_TO_MENU" event.
    #  The features affected are:
    #  - end_times (used to calculate totalLevelTime and avgLevelTime)
    #  - durationInSecs
    #  - sessionDurationInSecs
    #  - menuBtnCount
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromMenuBtn(self, level:int, event_client_time:datetime):
        self._features.incValByIndex(feature_name="menuBtnCount", index=level)
        if self._active_begin == None:
            sess_id = self._features.getValByName(feature_name="sessionID")
            Logger.Log(f"Got a 'Back to Menu' event when there was no active 'Begin' event! Sess ID: {sess_id}", logging.ERROR)
        else:
            self._end_times[level] = event_client_time
            time_taken = self._calcLevelTime(level)
            self._features.incValByIndex(feature_name="durationInSecs", index=level, increment=time_taken)
            self._features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)
            self._active_begin = None

    ## Private function to extract features from a "MOLECULE_RELEASE" event.
    #  The features affected are:
    #  - totalMoleculeDragDuration (used to calculate avgMoleculeDragDurationInSecs)
    #  - moleculeMoveCount
    #  - sessionMoleculeMoveCount
    #
    #  @param level      The level being played when event occurred.
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMoleculeRelease(self, level:int, event_data:Dict[str,Any]):
        if not level in self._totalMoleculeDragDuration.keys():
            self._totalMoleculeDragDuration[level] = 0
        self._totalMoleculeDragDuration[level] += event_data["time"]
        self._features.incValByIndex(feature_name="moleculeMoveCount", index=level)
        self._features.incAggregateVal(feature_name="sessionMoleculeMoveCount")

    ## Private function to extract features from a "MOLECULE_ROTATE" event.
    #  The features affected are:
    #  - stampRotateCount
    #  - sessionStampRotateCount
    #  - singleRotateCount
    #  - sessionSingleRotateCount
    #
    #  @param level      The level being played when event occurred.
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMoleculeRotate(self, level:int, event_data:Dict[str,Any]):
        if event_data["isStamp"]:
            self._features.incValByIndex(feature_name="stampRotateCount", index=level)
            self._features.incAggregateVal(feature_name="sessionStampRotateCount")
        else:
            self._features.incValByIndex(feature_name="singleRotateCount", index=level)
            self._features.incAggregateVal(feature_name="sessionSingleRotateCount")

    ## Private function to extract features from a "CLEAR_BTN_PRESS" event.
    #  The features affected are:
    #  - clearBtnPresses
    #  - sessionClearBtnPresses
    #
    #  @param level The level being played when clear button was pressed.
    def _extractFromClearBtnPress(self, level:int):
        self._features.incValByIndex(feature_name="clearBtnPresses", index=level)
        self._features.incAggregateVal(feature_name="sessionClearBtnPresses")

    ## Private function to extract features from a "MUSEUM_CLOSE" event.
    #  The features affected are:
    #  - sessionMuseumDurationInSecs
    #
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMuseumClose(self, event_data:Dict[str,Any]):
        self._features.incAggregateVal(feature_name="sessionMuseumDurationInSecs", increment=event_data["timeOpen"])

    ## Private function to extract features from a "QUESTION_ANSWER" event.
    #  The features affected are:
    #  - questionAnswered
    #  - questionCorrect
    #
    #  @param event_data_parsed Parsed JSON data from the row being processed.
    def _extractFromQuestionAnswer(self, event_data:Dict[str,Any]):
        q_num = event_data["question"]
        self._features.setValByIndex(feature_name="questionAnswered", index=q_num, new_value=event_data["answered"])
        correctness = 1 if event_data["answered"] == event_data["answer"] else 0
        self._features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value= correctness)

    ## Private function to calculate the time spent on a level for the given level
    #  and play index (each level may have been played multiple times).
    #
    #  @param lvl      The level whose play time should be calculated
    #  @return         The play time if level is valid, -1 if level was not
    #                  completed, 0 if level was never attempted.
    def _calcLevelTime(self, lvl:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self._levels:
            if lvl in self._start_times and lvl in self._end_times:
                return (self._end_times[lvl] - self._start_times[lvl]).total_seconds()
            else:
                return -1
        else:
            return 0