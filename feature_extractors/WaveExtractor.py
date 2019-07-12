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

class WaveExtractor(Extractor):
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self.features["questionAnswered"].keys():
            self.features["questionAnswered"][ans] = -1
        for q in self.features["questionCorrect"]:
            self.features["questionCorrect"][q] = -1

    def extractFromRow(self, level:int, event_data_complex_parsed, event_client_time: datetime.datetime):
        if "event_custom" not in event_data_complex_parsed.keys():
            logging.error("Invalid event_data_complex, does not contain event_custom field!")
        else:
            if not level in self.levels:
                bisect.insort(self.levels, level)
            # handle cases for each type of event
            # NOTE: for BEGIN and COMPLETE, we assume only one event of each type happens.
            # If there are somehow multiples, the previous times are overwritten by the newer ones.
            event_type = event_data_complex_parsed["event_custom"]
            if event_type == "BEGIN":
                self._extractFromBegin(level, event_client_time)
            elif event_type == "COMPLETE":
                self._extractFromComplete(level, event_client_time)
            elif event_type == "SUCCEED":
                pass
            elif event_type == "RESET_BTN_PRESS":
                self._extractFromResetBtnPress(level)
            elif event_type == "FAIL":
                self._extractFromFail(level)
            elif event_type in ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"] :
                self._extractFromMoveRelease(level, event_data_complex_parsed)
            elif event_type == "QUESTION_ANSWER":
                self._extractFromQuestionAnswer(event_data_complex_parsed)
                # print("Q+A: " + str(event_data_complex_parsed))
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))
                                               
    def calculateAggregateFeatures(self):
        if len(self.levels) > 0:
            # the percent____Moves features are per-level, but can't be calculated until the end.
            self.features["percentAmplitudeMoves"] = {lvl: self._calcPercentMoves("totalAmplitudeMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in self._level_range}
            self.features["percentOffsetMoves"] = {lvl: self._calcPercentMoves("totalOffsetMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in self._level_range}
            self.features["percentWavelengthMoves"] = {lvl: self._calcPercentMoves("totalWavelengthMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in self._level_range}
            self.features["avgSliderMoves"] = sum(self.features["totalSliderMoves"].values()) / len(self.levels)
            self.features["totalLevelTime"] = {lvl:self._calcLevelTime(lvl) for lvl in self._level_range}
            self.features["avgLevelTime"] = sum(self.features["totalLevelTime"].values()) / len(self.levels)
            self.features["avgKnobStdDevs"] = sum(self.features["totalKnobStdDevs"].values()) / len(self.levels)
            self.features["avgMoveTypeChanges"] = sum(self.features["totalMoveTypeChanges"].values()) / len(self.levels)
            self.features["avgKnobAvgMaxMin"] = sum(self.features["totalKnobAvgMaxMin"].values()) / len(self.levels)
            self.features["avgAmplitudeMoves"] = sum(self.features["totalAmplitudeMoves"].values()) / len(self.levels)
            self.features["avgOffsetMoves"] = sum(self.features["totalOffsetMoves"].values()) / len(self.levels)
            self.features["avgWavelengthMoves"] = sum(self.features["totalWavelengthMoves"].values()) / len(self.levels)

    @staticmethod
    def writeCSVHeader(game_table: GameTable, game_schema: Schema, file: typing.IO.writable):
        columns = []
        features = WaveExtractor._generateFeatureDict(range(game_table.min_level, game_table.max_level+1), game_schema)
        for key in features.keys():
            if type(features[key]) is type({}):
                # if it's a dictionary, expand.
                columns.extend(["lvl{}_{}".format(lvl, key) for lvl in features[key].keys()])
            else:
                columns.append(key)
        file.write(",".join(columns))
        file.write("\n")

    # TODO: It looks like I might be assuming that dictionaries always have same order here.
    # May need to revisit that issue. I mean, it should be fine because Python won't just go
    # and change order for no reason, but still...
    def writeCurrentFeatures(self, file: typing.IO.writable):
        column_vals = []
        for key in self.features.keys():
            if type(self.features[key]) is type({}):
                # if it's a dictionary, expand.
                column_vals.extend([str(self.features[key][index]) for index in self.features[key].keys()])
            else:
                column_vals.append(str(self.features[key]))
        file.write(",".join(column_vals))
        file.write("\n")

    def _extractFromBegin(self, level, event_client_time):
        self.start_times[level] = event_client_time

    def _extractFromComplete(self, level, event_client_time):
        self.end_times[level] = event_client_time
        self.features["completed"][level] = 1

    def _extractFromResetBtnPress(self, level):
        self.features["totalResets"][level] += 1

    def _extractFromFail(self, level):
        self.features["totalFails"][level] += 1

    def _extractFromMoveRelease(self, level, event_data_complex_parsed):
        # first, log the type of move.
        if event_data_complex_parsed["slider"] is not self.last_adjust_type:
            self.last_adjust_type = event_data_complex_parsed["slider"]
            # NOTE: We assume data are processed in order of event time.
            # If events are not sorted by time, the "move type changes" may be inaccurate.
            self.features["totalMoveTypeChanges"][level] += 1
        if event_data_complex_parsed["slider"] == "AMPLITUDE":
            self.features["totalAmplitudeMoves"][level] += 1
        elif event_data_complex_parsed["slider"] == "OFFSET":
            self.features["totalOffsetMoves"][level] += 1
        if event_data_complex_parsed["slider"] == "WAVELENGTH":
            self.features["totalWavelengthMoves"][level] += 1
        # then, log things specific to slider move:
        if event_data_complex_parsed["event_custom"] == "SLIDER_MOVE_RELEASE":
            self.features["totalSliderMoves"][level] += 1
            self.features["totalKnobStdDevs"][level] += event_data_complex_parsed["stdev_val"]
            self.features["totalKnobAvgMaxMin"][level] += event_data_complex_parsed["max_val"] - event_data_complex_parsed["min_val"]
        else: # log things specific to arrow move:
            self.features["totalArrowMoves"][level] += 1

    def _extractFromQuestionAnswer(self, event_data_complex_parsed):
        q_num = event_data_complex_parsed["question"]
        self.features["questionAnswered"][q_num] = event_data_complex_parsed["answered"]
        correctness = 1 if event_data_complex_parsed["answered"] == event_data_complex_parsed["answer"] else 0
        self.features["questionCorrect"][q_num] = correctness

    def _calcPercentMoves(self, key:str, level:int) -> int:
        num = sum(self.features[key].values())
        if num == 0:
            return 0
        else:
            denom = sum(self.features["totalSliderMoves"].values()) \
                  + sum(self.features["totalArrowMoves"].values())
            return num/denom

    def _calcLevelTime(self, lvl:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl] - self.start_times[lvl]).total_seconds()
            else:
                return -1
        else:
            return 0