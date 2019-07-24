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
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
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
            self.features.setValByName(feature_name="persistentSessionID", \
                                       new_value=row_with_complex_parsed[game_table.pers_session_id_index])
        level = row_with_complex_parsed[game_table.level_index]
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
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
            percents = {lvl: {"prefix":"lvl",
                              "val":self._calcPercentMoves("totalAmplitudeMoves", lvl) if lvl in self.levels else 0}
                        for lvl in self._level_range}
            self.features.setValByName(feature_name="percentAmplitudeMoves", new_value=percents)
            percents = {lvl: {"prefix":"lvl",
                              "val":self._calcPercentMoves("totalOffsetMoves", lvl) if lvl in self.levels else 0}
                        for lvl in self._level_range}
            self.features.setValByName(feature_name="percentOffsetMoves", new_value=percents) 
            percents = {lvl: {"prefix":"lvl",
                              "val":self._calcPercentMoves("totalWavelengthMoves", lvl) if lvl in self.levels else 0}
                        for lvl in self._level_range}
            self.features.setValByName(feature_name="percentWavelengthMoves", new_value=percents)
            num_lvl = len(self.levels)
            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalSliderMoves").values()]
            self.features.setValByName(feature_name="avgSliderMoves", new_value=sum(all_vals) / num_lvl)

            for lvl in self._level_range:
                self.features.setValByIndex(feature_name="totalLevelTime", index=lvl, new_value=self._calcLevelTime(lvl))
            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalLevelTime").values()]
            self.features.setValByName(feature_name="avgLevelTime", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalKnobStdDevs").values()]
            self.features.setValByName(feature_name="avgKnobStdDevs", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalMoveTypeChanges").values()]
            self.features.setValByName(feature_name="avgMoveTypeChanges", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalKnobAvgMaxMin").values()]
            self.features.setValByName(feature_name="avgKnobAvgMaxMin", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalAmplitudeMoves").values()]
            self.features.setValByName(feature_name="avgAmplitudeMoves", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalOffsetMoves").values()]
            self.features.setValByName(feature_name="avgOffsetMoves", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalWavelengthMoves").values()]
            self.features.setValByName(feature_name="avgWavelengthMoves", new_value=sum(all_vals) / num_lvl)

    def _extractFromBegin(self, level, event_client_time):
        self.start_times[level] = event_client_time

    def _extractFromComplete(self, level, event_client_time):
        self.end_times[level] = event_client_time
        self.features.setValByIndex(feature_name="completed", index=level, new_value=1)

    def _extractFromResetBtnPress(self, level):
        self.features.incValByIndex(feature_name="totalResets", index=level)

    def _extractFromFail(self, level):
        self.features.incValByIndex(feature_name="totalFails", index=level)

    def _extractFromMoveRelease(self, level, event_data_complex_parsed):
        # first, log the type of move.
        if event_data_complex_parsed["slider"] != self.last_adjust_type:
            self.last_adjust_type = event_data_complex_parsed["slider"]
            # NOTE: We assume data are processed in order of event time.
            # If events are not sorted by time, the "move type changes" may be inaccurate.
            self.features.incValByIndex(feature_name="totalMoveTypeChanges", index=level)
        if event_data_complex_parsed["slider"] == "AMPLITUDE":
            self.features.incValByIndex(feature_name="totalAmplitudeMoves", index=level)
        elif event_data_complex_parsed["slider"] == "OFFSET":
            self.features.incValByIndex(feature_name="totalOffsetMoves", index=level)
        if event_data_complex_parsed["slider"] == "WAVELENGTH":
            self.features.incValByIndex(feature_name="totalWavelengthMoves", index=level)
        # then, log things specific to slider move:
        if event_data_complex_parsed["event_custom"] == "SLIDER_MOVE_RELEASE":
            self.features.incValByIndex(feature_name="totalSliderMoves", index=level)
            self.features.incValByIndex(feature_name="totalKnobStdDevs", index=level, increment=event_data_complex_parsed["stdev_val"])
            self.features.incValByIndex(feature_name="totalKnobAvgMaxMin", index=level, increment=event_data_complex_parsed["max_val"] - event_data_complex_parsed["min_val"])
        else: # log things specific to arrow move:
            self.features.incValByIndex(feature_name="totalArrowMoves", index=level)

    def _extractFromQuestionAnswer(self, event_data_complex_parsed):
        q_num = event_data_complex_parsed["question"]
        self.features.setValByIndex(feature_name="questionAnswered", index=q_num, new_value=event_data_complex_parsed["answered"])
        correctness = 1 if event_data_complex_parsed["answered"] == event_data_complex_parsed["answer"] else 0
        self.features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value=correctness)

    def _calcPercentMoves(self, key:str, level:int) -> int:
        all_vals = [elem["val"] for elem in self.features.getValByName(feature_name=key).values()]
        num = sum(all_vals)
        if num == 0:
            return 0
        else:
            slider_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalSliderMoves").values()]
            arrow_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalArrowMoves").values()]
            denom = sum(slider_vals) + sum(arrow_vals)
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