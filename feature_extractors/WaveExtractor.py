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

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
class WaveExtractor(Extractor):
    ## Constructor for the WaveExtractor class.
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
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
        self.amp_move_counts: typing.Dict   = {}
        self.off_move_counts: typing.Dict   = {}
        self.wave_move_counts: typing.Dict  = {}
        self.features.setValByName(feature_name="sessionID", new_value=session_id)
        # we specifically want to set the default value for questionAnswered to -1, for unanswered.
        for ans in self.features.getValByName(feature_name="questionAnswered").keys():
            self.features.setValByIndex(feature_name="questionAnswered", index=ans, new_value= -1)
        for q in self.features.getValByName(feature_name="questionCorrect"):
            self.features.setValByIndex(feature_name="questionCorrect", index=q, new_value= -1)

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
        if row_with_complex_parsed[game_table.session_id_index] != self.session_id:
            raise Exception("Got a row with incorrect session id!")
        elif "event_custom" not in event_data_complex_parsed.keys():
            logging.error("Invalid event_data_complex, does not contain event_custom field!")
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="persistentSessionID") == 0:
                self.features.setValByName(feature_name="persistentSessionID", \
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # Ensure we have private data initialized for the given level.
            if not level in self.levels:
                bisect.insort(self.levels, level)
                self.amp_move_counts[level] = 0
                self.off_move_counts[level] = 0
                self.wave_move_counts[level] = 0
            # Then, handle cases for each type of event
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
                                               
    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    def calculateAggregateFeatures(self):
        if len(self.levels) > 0:
            # Calculate per-level averages and percentages, since we can't calculate
            # them until we know how many total events occur.
            for lvl in self._level_range:
                total_slider_moves = self.features.getValByIndex(feature_name="totalSliderMoves", index=lvl)
                total_moves = total_slider_moves + self.features.getValByIndex(feature_name="totalArrowMoves", index=lvl)
                # percents of each move type
                val   = self.amp_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
                self.features.setValByIndex(feature_name="percentAmplitudeMoves", index=lvl, new_value=val)
                val   = self.off_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
                self.features.setValByIndex(feature_name="percentOffsetMoves", index=lvl, new_value=val)
                val   = self.wave_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
                self.features.setValByIndex(feature_name="percentWavelengthMoves", index=lvl, new_value=val)
                # avg slider std devs and ranges.
                total_slider_stdevs = self.features.getValByIndex(feature_name="sliderAvgStdDevs", index=lvl)
                val = total_slider_stdevs / total_slider_moves if total_slider_moves > 0 else total_slider_moves
                self.features.setValByIndex(feature_name="sliderAvgStdDevs", index=lvl, new_value=val)
                total_slider_range  = self.features.getValByIndex(feature_name="sliderAvgRange", index=lvl)
                val = total_slider_range / total_slider_moves if total_slider_moves > 0 else total_slider_moves
                self.features.setValByIndex(feature_name="sliderAvgRange", index=lvl, new_value=val)
            # Then, calculate true aggregates.
            num_lvl = len(self.levels)
            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalSliderMoves").values()]
            self.features.setValByName(feature_name="avgSliderMoves", new_value=sum(all_vals) / num_lvl)

            for lvl in self._level_range:
                self.features.setValByIndex(feature_name="totalLevelTime", index=lvl, new_value=self._calcLevelTime(lvl))
            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalLevelTime").values()]
            self.features.setValByName(feature_name="avgLevelTime", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="sliderAvgStdDevs").values()]
            self.features.setValByName(feature_name="avgSliderAvgStdDevs", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalMoveTypeChanges").values()]
            self.features.setValByName(feature_name="avgMoveTypeChanges", new_value=sum(all_vals) / num_lvl)

            all_vals = [elem["val"] for elem in self.features.getValByName(feature_name="sliderAvgRange").values()]
            self.features.setValByName(feature_name="avgSliderAvgRange", new_value=sum(all_vals) / num_lvl)

            all_vals = list(self.amp_move_counts.values())
            self.features.setValByName(feature_name="avgAmplitudeMoves", new_value=sum(all_vals) / num_lvl)

            all_vals = list(self.off_move_counts.values())
            self.features.setValByName(feature_name="avgOffsetMoves", new_value=sum(all_vals) / num_lvl)

            all_vals = list(self.wave_move_counts.values())
            self.features.setValByName(feature_name="avgWavelengthMoves", new_value=sum(all_vals) / num_lvl)

    ## Private function to extract features from a "BEGIN" event.
    #  The features affected are:
    #  - start_times (used to calculate totalLevelTime and avgLevelTime)
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromBegin(self, level, event_client_time):
        self.start_times[level] = event_client_time

    ## Private function to extract features from a "COMPLETE" event.
    #  The features affected are:
    #  - end_times (used to calculate totalLevelTime and avgLevelTime)
    #  - completed
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    def _extractFromComplete(self, level, event_client_time):
        self.end_times[level] = event_client_time
        self.features.setValByIndex(feature_name="completed", index=level, new_value=1)

    ## Private function to extract features from a "RESET_BTN_PRESS" event.
    #  The features affected are:
    #  - totalResets
    #
    #  @param level The level being played when reset button was pressed.
    def _extractFromResetBtnPress(self, level):
        self.features.incValByIndex(feature_name="totalResets", index=level)

    ## Private function to extract features from a "FAIL" event.
    #  The features affected are:
    #  - totalFails
    #
    #  @param level The level being played when the event occurred.
    def _extractFromFail(self, level):
        self.features.incValByIndex(feature_name="totalFails", index=level)

    ## Private function to extract features from a "SLIDER_MOVE_RELEASE" event.
    #  The features affected are:
    #  - totalMoveTypeChanges
    #  - totalSliderMoves
    #  - totalArrowMoves
    #  - sliderAvgStdDevs
    #  - sliderAvgRange
    #
    #  @param level      The level being played when event occurred.
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromMoveRelease(self, level, event_data):
        # first, log the type of move.
        if event_data["slider"] != self.last_adjust_type:
            self.last_adjust_type = event_data["slider"]
            # NOTE: We assume data are processed in order of event time.
            # If events are not sorted by time, the "move type changes" may be inaccurate.
            self.features.incValByIndex(feature_name="totalMoveTypeChanges", index=level)
        if event_data["slider"] == "AMPLITUDE":
            self.amp_move_counts[level] += 1
        elif event_data["slider"] == "OFFSET":
            self.off_move_counts[level] += 1
        elif event_data["slider"] == "WAVELENGTH":
            self.wave_move_counts[level] += 1
        # then, log things specific to slider move:
        if event_data["event_custom"] == "SLIDER_MOVE_RELEASE":
            self.features.incValByIndex(feature_name="totalSliderMoves", index=level)
            # These will be averages over the level. Per-row, just accumulate,
            # then we'll divide in the aggregate feature step.
            self.features.incValByIndex(feature_name="sliderAvgStdDevs", index=level,
                                        increment=event_data["stdev_val"])
            self.features.incValByIndex(feature_name="sliderAvgRange", index=level,
                                        increment= event_data["max_val"]
                                                 - event_data["min_val"])
        else: # log things specific to arrow move:
            self.features.incValByIndex(feature_name="totalArrowMoves", index=level)

    ## Private function to extract features from a "QUESTION_ANSWER" event.
    #  The features affected are:
    #  - questionAnswered
    #  - questionCorrect
    #
    #  @param event_data Parsed JSON data from the row being processed.
    def _extractFromQuestionAnswer(self, event_data):
        q_num = event_data["question"]
        self.features.setValByIndex(feature_name="questionAnswered", index=q_num,
                                    new_value=event_data["answered"])
        correctness = 1 if event_data["answered"] == event_data["answer"] else 0
        self.features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value=correctness)

    ## Private function to calculate percent of moves made of a given type,
    #  for a given level.
    #
    #  @param key   The feature name for the type of move to calculate percentage on.
    #  @param level The level for which we want to calculate a percentage.
    def _calcPercentMoves(self, key:str, level:int) -> int:
        all_vals = [elem["val"] for elem in self.features.getFeatureByName(feature_name=key).values()]
        num = sum(all_vals)
        if num == 0:
            return 0
        else:
            slider_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalSliderMoves").values()]
            arrow_vals = [elem["val"] for elem in self.features.getValByName(feature_name="totalArrowMoves").values()]
            denom = sum(slider_vals) + sum(arrow_vals)
            return num/denom

    ## Private function to calculate the time spent on a given level.
    #
    #  @param lvl      The level whose play time should be calculated
    #  @return         The play time if level is valid, -1 if level
    #                  was not completed, 0 if level was never attempted.
    def _calcLevelTime(self, lvl:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl] - self.start_times[lvl]).total_seconds()
            else:
                return -1
        else:
            return 0