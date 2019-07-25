## import standard libraries
import bisect
import datetime
import json
import logging
import typing
## import local files
import utils
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema

class CrystalExtractor(Extractor):
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
        self.totalMoleculeDragDuration      = {}
        self.features.setValByName(feature_name="sessionID", new_value=session_id)
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self.features.getValByName(feature_name="questionAnswered").keys():
            self.features.setValByIndex(feature_name="questionAnswered", index=ans, new_value= -1)
        for q in self.features.getValByName(feature_name="questionCorrect"):
            self.features.setValByIndex(feature_name="questionCorrect", index=q, new_value= -1)

    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        if row_with_complex_parsed[game_table.session_id_index] != self.session_id:
            raise Exception("Got a row with incorrect session id!")
        if self.features.getValByName(feature_name="persistentSessionID") == 0:
            self.features.setValByName(feature_name="persistentSessionID",
                                       new_value   = row_with_complex_parsed[game_table.pers_session_id_index])
        level = row_with_complex_parsed[game_table.level_index]
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        if "event_custom" not in event_data_complex_parsed.keys():
            logging.error("Invalid event_data_complex, does not contain event_custom field!")
        else:
            if not level in self.levels:
                bisect.insort(self.levels, level)
                self.totalMoleculeDragDuration[level] = 0
                self.start_times[level] = []
                self.end_times[level] = []
            # First, record the fact that an event has occurred for the level & session
            self.features.incValByIndex(feature_name="eventCount", index=level)
            self.features.incAggregateVal(feature_name="sessionEventCount")
            # handle cases for each type of event
            event_type = event_data_complex_parsed["event_custom"]
            if event_type == "BEGIN":
                self._extractFromBegin(level, event_client_time)
            elif event_type == "COMPLETE":
                self._extractFromComplete(level, event_client_time, event_data_complex_parsed)
            elif event_type == "MOLECULE_RELEASE":
                self._extractFromMoleculeRelease(level, event_data_complex_parsed)
            elif event_type == "MOLECULE_ROTATE":
                self._extractFromMoleculeRotate(level, event_data_complex_parsed)
            elif event_type == "CLEAR_BTN_PRESS":
                self._extractFromClearBtnPress(level)
            elif event_type in "MUSEUM_CLOSE" :
                self._extractFromMuseumClose(level, event_data_complex_parsed)
            elif event_type == "QUESTION_ANSWER":
                self._extractFromQuestionAnswer(event_data_complex_parsed)
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))
                                               
    def calculateAggregateFeatures(self):
        for level in self.levels:
            count = self.features.getValByIndex(feature_name="moleculeMoveCount", index=level)
            avg = 0 if count == 0 else self.totalMoleculeDragDuration[level] / count
            self.features.setValByIndex(feature_name="avgMoleculeDragDurationInSecs", index=level, new_value=avg)
            # for each each time we started a play in the level, do stuff.
            for play in range(len(self.start_times[level])):
                if len(self.end_times[level]) > play:
                    time_taken = self._calcLevelTime(level, play)
                    self.features.incValByIndex(feature_name="durationInSecs", index=level, increment=time_taken)
                    self.features.incAggregateVal(feature_name="sessionDurationInSecs", increment=time_taken)

    def _extractFromBegin(self, level, event_client_time):
        # we'll maintain lists of start times for each level, since there may
        # be multiple playthroughs.
        if not level in self.start_times.keys():
            self.start_times[level] = []
        self.start_times[level].append(event_client_time)

    def _extractFromComplete(self, level, event_client_time, event_data_complex_parsed):
        # we'll maintain lists of end times for each level, since there may
        # be multiple playthroughs.
        if not level in self.end_times.keys():
            self.end_times[level] = []
        # We assume completion of the most recent BEGIN event.
        # Thus, if there have been multiple BEGINS, we pad with empty COMPLETES
        # until we match lengths again by adding the current COMPLETE.
        while len(self.end_times) < len(self.start_times)-1:
            self.end_times[level].append(None)
        self.end_times[level].append(event_client_time)
        self.features.incValByIndex(feature_name="completesCount", index=level, increment=1)
        score = event_data_complex_parsed["stability"]["pack"] \
              + event_data_complex_parsed["stability"]["charge"]
        self.features.setValByIndex(feature_name="finalScore", index=level, new_value=score)

    def _extractFromMoleculeRelease(self, level, event_data_complex_parsed):
        if not level in self.totalMoleculeDragDuration.keys():
            self.totalMoleculeDragDuration[level] = 0
        self.totalMoleculeDragDuration[level] += event_data_complex_parsed["time"]
        self.features.incValByIndex(feature_name="moleculeMoveCount", index=level)
        self.features.incAggregateVal(feature_name="sessionMoleculeMoveCount")

    def _extractFromMoleculeRotate(self, level, event_data_complex_parsed):
        if event_data_complex_parsed["isStamp"]:
            self.features.incValByIndex(feature_name="stampRotateCount", index=level)
            self.features.incAggregateVal(feature_name="sessionStampRotateCount")
        if event_data_complex_parsed["numRotations"] == 1:
            self.features.incValByIndex(feature_name="singleRotateCount", index=level)
            self.features.incAggregateVal(feature_name="sessionSingleRotateCount")

    def _extractFromClearBtnPress(self, level):
        self.features.incValByIndex(feature_name="clearBtnPresses", index=level)
        self.features.incAggregateVal(feature_name="sessionClearBtnPresses")

    def _extractFromMuseumClose(self, level, event_data_complex_parsed):
        self.features.incAggregateVal(feature_name="sessionMuseumDurationInSecs", increment=event_data_complex_parsed["timeOpen"])

    def _extractFromQuestionAnswer(self, event_data_complex_parsed):
        q_num = event_data_complex_parsed["question"]
        self.features.setValByIndex(feature_name="questionAnswered", index=q_num, new_value=event_data_complex_parsed["answered"])
        correctness = 1 if event_data_complex_parsed["answered"] == event_data_complex_parsed["answer"] else 0
        self.features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value= correctness)

    def _calcLevelTime(self, lvl:int, play_num:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl][play_num] - self.start_times[lvl][play_num]).total_seconds()
            else:
                return -1
        else:
            return 0