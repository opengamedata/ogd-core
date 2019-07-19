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
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self.features["answerGiven"].keys():
            self.features["answerGiven"][ans]["val"] = -1
        for q in self.features["wasCorrect"]:
            self.features["wasCorrect"][q]["val"] = -1

    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
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
            self.features["eventCount"][level]["val"] += 1
            self.features["sessionEventCount"] += 1
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
            count = self.features["moleculeMoveCount"][level]["val"]
            avg = 0 if count == 0 else self.totalMoleculeDragDuration[level] / count
            self.features["avgMoleculeDragDurationInSecs"][level]["val"] = avg
            # for each each time we started a play in the level, do stuff.
            for play in range(len(self.start_times[level])):
                if len(self.end_times[level]) > play:
                    time_taken = self._calcLevelTime(level, play)
                    self.features["durationInSecs"][level]["val"] += time_taken
                    self.features["sessionDurationInSecs"] += time_taken

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
        self.features["completesCount"][level]["val"] += 1
        score = event_data_complex_parsed["stability"]["pack"] \
              + event_data_complex_parsed["stability"]["charge"]
        self.features["finalScore"][level]["val"] = score

    def _extractFromMoleculeRelease(self, level, event_data_complex_parsed):
        if not level in self.totalMoleculeDragDuration.keys():
            self.totalMoleculeDragDuration[level] = 0
        self.totalMoleculeDragDuration[level] += event_data_complex_parsed["time"]
        self.features["moleculeMoveCount"][level]["val"] += 1
        self.features["sessionMoleculeMoveCount"] += 1

    def _extractFromMoleculeRotate(self, level, event_data_complex_parsed):
        if event_data_complex_parsed["isStamp"]:
            self.features["stampRotateCount"][level]["val"] += 1
            self.features["sessionStampRotateCount"] += 1
        if event_data_complex_parsed["numRotations"] == 1:
            self.features["singleRotateCount"][level]["val"] += 1
            self.features["sessionSingleRotateCount"] += 1

    def _extractFromClearBtnPress(self, level):
        self.features["clearBtnPresses"][level]["val"] += 1
        self.features["sessionClearBtnPresses"] += 1

    def _extractFromMuseumClose(self, level, event_data_complex_parsed):
        self.features["sessionMuseumDurationInSecs"] += event_data_complex_parsed["timeOpen"]

    def _extractFromQuestionAnswer(self, event_data_complex_parsed):
        q_num = event_data_complex_parsed["question"]
        self.features["answerGiven"][q_num]["val"] = event_data_complex_parsed["answered"]
        correctness = 1 if event_data_complex_parsed["answered"] == event_data_complex_parsed["answer"] else 0
        self.features["wasCorrect"][q_num]["val"] = correctness

    def _calcLevelTime(self, lvl:int, play_num:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl][play_num] - self.start_times[lvl][play_num]).total_seconds()
            else:
                return -1
        else:
            return 0