## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.WAVES.features import *
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
class WaveLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features
    
    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        # Session-level features.
        if extractor_params._count_index is None:
            match feature_type:
                case "AverageFails":
                    ret_val = AverageFails.AverageFails(params=extractor_params)
                case "AverageLevelTime":
                    ret_val = AverageLevelTime.AverageLevelTime(params=extractor_params)
                case "AverageMoveTypeChanges":
                    ret_val = AverageMoveTypeChanges.AverageMoveTypeChanges(params=extractor_params)
                case "AverageSliderMoves":
                    ret_val = AverageSliderMoves.AverageSliderMoves(params=extractor_params)
                case "OverallPercentAmplitudeMoves":
                    ret_val = OverallPercentAmplitudeMoves.OverallPercentAmplitudeMoves(params=extractor_params)
                case "OverallPercentOffsetMoves":
                    ret_val = OverallPercentOffsetMoves.OverallPercentOffsetMoves(params=extractor_params)
                case "OverallPercentWavelengthMoves":
                    ret_val = OverallPercentWavelengthMoves.OverallPercentWavelengthMoves(params=extractor_params)
                case "OverallSliderAverageRange":
                    ret_val = OverallSliderAverageRange.OverallSliderAverageRange(params=extractor_params)
                case "OverallSliderAverageStandardDeviations":
                    ret_val = OverallSliderAverageStandardDeviations.OverallSliderAverageStandardDeviations(params=extractor_params)
                case "PersistentSessionID":
                    ret_val = PersistentSessionID.PersistentSessionID(params=extractor_params)
                case "SessionID":
                    ret_val = SessionID.SessionID(params=extractor_params, sessionID=self._session_id)
                case "SessionSucceedCount":
                    ret_val = SessionSucceedCount.SessionSucceedCount(params=extractor_params)
                    # sequence features
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature for Waves.")
        # Per-count features
        # level attempt features
        else:
            match feature_type:
                case "BeginCount":
                    ret_val = BeginCount.BeginCount(params=extractor_params)
                case "Completed":
                    ret_val = Completed.Completed(params=extractor_params)
                case "MenuButtonCount":
                    ret_val = MenuButtonCount.MenuButtonCount(params=extractor_params)
                case "SequenceLevel":
                    ret_val = SequenceLevel.SequenceLevel(params=extractor_params)
                case "SucceedCount":
                    ret_val = SucceedCount.SucceedCount(params=extractor_params)
                case "TotalFails":
                    ret_val = TotalFails.TotalFails(params=extractor_params)
                case "TotalLevelTime":
                    ret_val = TotalLevelTime.TotalLevelTime(params=extractor_params)
                case "TotalResets":
                    ret_val = TotalResets.TotalResets(params=extractor_params)
                case "TotalSkips":
                    ret_val = TotalSkips.TotalSkips(params=extractor_params)
                    # slider move features
                case "FirstMoveType":
                    ret_val = FirstMoveType.FirstMoveType(params=extractor_params)
                case "AmplitudeGoodMoveCount":
                    ret_val = AmplitudeGoodMoveCount.AmplitudeGoodMoveCount(params=extractor_params)
                case "OffsetGoodMoveCount":
                    ret_val = OffsetGoodMoveCount.OffsetGoodMoveCount(params=extractor_params)
                case "WavelengthGoodMoveCount":
                    ret_val = WavelengthGoodMoveCount.WavelengthGoodMoveCount(params=extractor_params)
                case "PercentAmplitudeMoves":
                    ret_val = PercentAmplitudeMoves.PercentAmplitudeMoves(params=extractor_params)
                case "PercentOffsetMoves":
                    ret_val = PercentOffsetMoves.PercentOffsetMoves(params=extractor_params)
                case "PercentWavelengthMoves":
                    ret_val = PercentWavelengthMoves.PercentWavelengthMoves(params=extractor_params)
                case "PercentAmplitudeGoodMoves":
                    ret_val = PercentAmplitudeGoodMoves.PercentAmplitudeGoodMoves(params=extractor_params)
                case "PercentOffsetGoodMoves":
                    ret_val = PercentOffsetGoodMoves.PercentOffsetGoodMoves(params=extractor_params)
                case "PercentWavelengthGoodMoves":
                    ret_val = PercentWavelengthGoodMoves.PercentWavelengthGoodMoves(params=extractor_params)
                case "SliderAverageRange":
                    ret_val = SliderAverageRange.SliderAverageRange(params=extractor_params)
                case "SliderAverageStandardDeviations":
                    ret_val = SliderAverageStandardDeviations.SliderAverageStandardDeviations(params=extractor_params)
                case "TotalArrowMoves":
                    ret_val = TotalArrowMoves.TotalArrowMoves(params=extractor_params)
                case "TotalMoveTypeChanges":
                    ret_val = TotalMoveTypeChanges.TotalMoveTypeChanges(params=extractor_params)
                case "TotalSliderMoves":
                    ret_val = TotalSliderMoves.TotalSliderMoves(params=extractor_params)
                    # level progress over time features
                # case "ClosenessIntercept":
                #     ret_val = ClosenessIntercept.ClosenessIntercept(params=extractor_params)
                # case "ClosenessR2":
                #     ret_val = ClosenessR2.ClosenessR2(params=extractor_params)
                # case "ClosenessSlope":
                #     ret_val = ClosenessSlope.ClosenessSlope(params=extractor_params)
                # case "RangeIntercept":
                #     ret_val = RangeIntercept.RangeIntercept(params=extractor_params)
                # case "RangeR2":
                #     ret_val = RangeR2.RangeR2(params=extractor_params)
                # case "RangeSlope":
                #     ret_val = RangeSlope.RangeSlope(params=extractor_params)
                    # quiz features
                case "QuestionAnswered":
                    ret_val = QuestionAnswered.QuestionAnswered(params=extractor_params)
                case "QuestionCorrect":
                    ret_val = QuestionCorrect.QuestionCorrect(params=extractor_params)
                case "TimeToAnswerMS":
                    ret_val = TimeToAnswerMS.TimeToAnswerMS(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature for Waves.")
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid detector for Waves.")
        return None

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the WaveLoader class.
    def __init__(self, player_id:str, session_id: str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]=None):
        """Constructor for the WaveLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GameSchema
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)
        # self._last_adjust_type : Optional[str] = None
        # self.start_times: Dict       = {}
        # self.end_times:   Dict       = {}
        # self.amp_move_counts:  Dict   = {}
        # self.off_move_counts:  Dict   = {}
        # self.wave_move_counts: Dict   = {}
        # self.saw_first_move: Dict[int, bool] = {}
        # self.latest_complete_lvl8 = None
        # self.latest_complete_lvl16 = None
        # self.latest_answer_Q0 = None
        # self.latest_answer_Q2 = None
        # self.active_begin = None
        # self.move_closenesses_tx: Dict = {}
        # self._features.setValByName(feature_name="sessionID", new_value=session_id)
        # # we specifically want to set the default value for questionAnswered to None, for unanswered.
        # for ans in self._features.getValByName(feature_name="questionAnswered").keys():
        #     self._features.setValByIndex(feature_name="questionAnswered", index=ans, new_value=None)
        # for q in self._features.getValByName(feature_name="questionCorrect"):
        #     self._features.setValByIndex(feature_name="questionCorrect", index=q, new_value=None)
        # for elem in self._features.getValByName(feature_name="firstMoveType"):
        #     self._features.setValByIndex(feature_name="firstMoveType", index=elem, new_value=None)

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    # def _extractFeaturesFromEvent(self, event:Event, table_schema:TableSchema):
    #     if event.SessionID == self._session_id:
    #         level = event.GameState['level']
    #         # If we haven't set persistent id, set now.
    #         if self._features.getValByName(feature_name="persistentSessionID") == 0:
    #             self._features.setValByName(feature_name="persistentSessionID", new_value=event.UserData['persistent_session_id'])
    #         # Ensure we have private data initialized for the given level.
    #         if not level in self._levels:
    #             bisect.insort(self._levels, level)
    #             self._features.initLevel(level)
    #             self.amp_move_counts[level] = 0
    #             self.off_move_counts[level] = 0
    #             self.wave_move_counts[level] = 0
    #         # Then, handle cases for each type of event
    #         # NOTE: for BEGIN and COMPLETE, we assume only one event of each type happens.
    #         # If there are somehow multiples, the previous times are overwritten by the newer ones.
    #         # 1) figure out what type of event we had. If CUSTOM, we'll use the event_custom sub-item.
    #         event_type = event.EventName.split('.')[0]
    #         if event_type == "CUSTOM":
    #             event_type = event.EventData['event_custom']
    #         # 2) handle cases for each type of event
    #         match event_type:
    #             case "BEGIN":
    #                 self._extractFromBegin(level=level, event_client_time=event.Timestamp)
    #             case "COMPLETE":
    #                 self._extractFromComplete(level=level, event_client_time=event.Timestamp)
    #             case "SUCCEED":
    #                 self._extractFromSucceed(level=level)
    #             case "MENU_BUTTON":
    #                 self._extractFromMenuBtn(level=level, event_client_time=event.Timestamp)
    #             case "SKIP_BUTTON":
    #                 self._extractFromSkipBtn(level=level)
    #             case "DISMISS_MENU_BUTTON":
    #                 pass
    #                 # print("Stub: Got a DISMISS_MENU_BUTTON event, nothing to do with it.")
    #             case "RESET_BTN_PRESS":
    #                 self._extractFromResetBtnPress(level=level)
    #             case "FAIL":
    #                 self._extractFromFail(level=level)
    #             case ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"] :
    #                 self._extractFromMoveRelease(level=level, event_data=event.EventData, event_client_time=event.Timestamp)
    #             case "QUESTION_ANSWER":
    #                 self._extractFromQuestionAnswer(event_data=event.EventData, event_client_time=event.Timestamp)
    #                 # print("Q+A: " + str(event_data))
    #             case _:
    #                 raise Exception(f"Found an unrecognized event type: {event_type}")
    #     else:
    #         Logger.Log(f"Got a row with incorrect session id! Expected {self._session_id}, got {event.SessionID}!", logging.ERROR)
                                               
    ## Function to perform calculation of aggregate features from existing
    #  per-level/per-custom-count features.
    # def CalculateAggregateFeatures(self):
    #     if len(self._levels) > 0:
    #         # Calculate per-level averages and percentages, since we can't calculate
    #         # them until we know how many total events occur.
    #         for lvl in self._levels:
    #             total_slider_moves = self._features.getValByIndex(feature_name="totalSliderMoves", index=lvl)
    #             total_moves = total_slider_moves + self._features.getValByIndex(feature_name="totalArrowMoves", index=lvl)
    #             # percents of each move type
    #             try:
    #                 val   = self.amp_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
    #             except Exception as err:
    #                 val = None
    #                 Logger.Log(f"Currently, total_moves = {total_moves}")
    #                 msg = f"{type(err)} {str(err)}"
    #                 Logger.Log(msg, logging.ERROR)
    #                 traceback.print_tb(err.__traceback__)
    #             self._features.setValByIndex(feature_name="percentAmplitudeMoves", index=lvl, new_value=val)
    #             val   = self.off_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
    #             self._features.setValByIndex(feature_name="percentOffsetMoves", index=lvl, new_value=val)
    #             val   = self.wave_move_counts[lvl] / total_moves if total_moves > 0 else total_moves
    #             self._features.setValByIndex(feature_name="percentWavelengthMoves", index=lvl, new_value=val)
    #             # percents of good moves for each type
    #             val   = self._features.getValByIndex(feature_name="amplitudeGoodMoveCount", index=lvl) / self.amp_move_counts[lvl] \
    #                  if lvl in self.amp_move_counts.keys() and self.amp_move_counts[lvl] > 0 else 0.0
    #             self._features.setValByIndex(feature_name="percentAmplitudeGoodMoves", index=lvl, new_value=val)
    #             val   = self._features.getValByIndex(feature_name="offsetGoodMoveCount", index=lvl) / self.off_move_counts[lvl] \
    #                  if lvl in self.off_move_counts.keys() and self.off_move_counts[lvl] > 0 else 0.0
    #             self._features.setValByIndex(feature_name="percentOffsetGoodMoves", index=lvl, new_value=val)
    #             val   = self._features.getValByIndex(feature_name="wavelengthGoodMoveCount", index=lvl) / self.wave_move_counts[lvl] \
    #                  if lvl in self.wave_move_counts.keys() and self.wave_move_counts[lvl] > 0 else 0.0
    #             self._features.setValByIndex(feature_name="percentWavelengthGoodMoves", index=lvl, new_value=val)
    #             # avg slider std devs and ranges.
    #             total_slider_stdevs = self._features.getValByIndex(feature_name="sliderAvgStdDevs", index=lvl)
    #             val = total_slider_stdevs / total_slider_moves if total_slider_moves > 0 else total_slider_moves
    #             self._features.setValByIndex(feature_name="sliderAvgStdDevs", index=lvl, new_value=val)
    #             total_slider_range  = self._features.getValByIndex(feature_name="sliderAvgRange", index=lvl)
    #             val = total_slider_range / total_slider_moves if total_slider_moves > 0 else total_slider_moves
    #             self._features.setValByIndex(feature_name="sliderAvgRange", index=lvl, new_value=val)
    #         # Then, calculate true aggregates.
    #         num_lvl = len(self._levels)
    #         all_vals = [elem["val"] for elem in self._features.getValByName(feature_name="totalSliderMoves").values() if elem["val"] is not None]
    #         self._features.setValByName(feature_name="avgSliderMoves", new_value=sum(all_vals) / num_lvl)

    #         all_vals = [elem["val"] for elem in self._features.getValByName(feature_name="totalLevelTime").values() if elem["val"] is not None]
    #         self._features.setValByName(feature_name="avgLevelTime", new_value=sum(all_vals) / num_lvl)

    #         all_vals = [elem["val"] for elem in self._features.getValByName(feature_name="totalMoveTypeChanges").values() if elem["val"] is not None]
    #         self._features.setValByName(feature_name="avgMoveTypeChanges", new_value=sum(all_vals) / num_lvl)

    #         # Determine number of moves that occurred across all levels
    #         all_amps = sum(list(self.amp_move_counts.values()))
    #         all_offs = sum(list(self.off_move_counts.values()))
    #         all_waves = sum(list(self.wave_move_counts.values()))
    #         all_moves = all_amps + all_offs + all_waves

    #         # Calculate percentages of each move type over all moves.
    #         perc_amps = all_amps / all_moves if all_moves > 0 else all_moves
    #         perc_offs = all_offs / all_moves if all_moves > 0 else all_moves
    #         perc_waves = all_waves / all_moves if all_moves > 0 else all_moves
    #         self._features.setValByName(feature_name="overallPercentAmplitudeMoves", new_value=perc_amps)
    #         self._features.setValByName(feature_name="overallPercentOffsetMoves", new_value=perc_offs)
    #         self._features.setValByName(feature_name="overallPercentWavelengthMoves", new_value=perc_waves)

    #         # Calculate average ranges and std devs over all moves.
    #         all_stdevs = sum([elem["val"] for elem in self._features.getValByName(feature_name="sliderAvgStdDevs").values() if elem["val"] is not None])
    #         all_ranges = sum([elem["val"] for elem in self._features.getValByName(feature_name="sliderAvgRange").values() if elem["val"] is not None])
    #         avg_stdevs = all_stdevs / all_moves if all_moves > 0 else all_moves
    #         avg_ranges = all_ranges / all_moves if all_moves > 0 else all_moves
    #         self._features.setValByName(feature_name="overallSliderAvgStdDevs", new_value=avg_stdevs)
    #         self._features.setValByName(feature_name="overallSliderAvgRange", new_value=avg_ranges)

    #         # Finally, calculate average fails per level
    #         all_fails = sum([elem["val"] for elem in self._features.getValByName(feature_name="totalFails").values() if elem["val"] is not None])
    #         avg_fails = all_fails / all_moves if all_moves > 0 else all_moves
    #         self._features.setValByName(feature_name="avgFails", new_value=avg_fails)

    ## Private function to extract features from a "BEGIN" event.
    #  The features affected are:
    #  - start_times (used to calculate totalLevelTime and avgLevelTime)
    #  - beginCount
    #  - totalLevelTime
    #
    #  @param level             The level being played when event occurred.
    #  @param event_client_time The time when this event occurred, according to game client.
    # def _extractFromBegin(self, level:int, event_client_time:datetime):
    #     self._features.incValByIndex(feature_name="beginCount", index=level)
    #     if self.active_begin == None:
    #         self.start_times[level] = event_client_time
    #         self.move_closenesses_tx[level] = {'t': [], 'completeness': [], 'range': []}
    #     elif self.active_begin == level:
    #         pass # in this case, just keep going.
    #     else:
    #         self.end_times[self.active_begin] = event_client_time
    #         self._calc_level_end(self.active_begin)
    #         try:
    #             self._features.incValByIndex(feature_name="totalLevelTime", index=self.active_begin, increment=self._calcLevelTime(self.active_begin))
    #         except Exception as err:
    #             raise(Exception(f"{type(err)} {str(err)}, level={level}, method=extractFromBegin, active_begin={self.active_begin}"))
    #         self.start_times[level] = event_client_time
    #         self.move_closenesses_tx[level] = {'t': [], 'completeness': [], 'range': []}
    #     # in any case, current level now has active begin event.
    #     self.active_begin = level

    # ## Private function to extract features from a "COMPLETE" event.
    # #  The features affected are:
    # #  - end_times (used to calculate totalLevelTime and avgLevelTime)
    # #  - completed
    # #  - completeCount
    # #  - totalLevelTime
    # #
    # #  @param level             The level being played when event occurred.
    # #  @param event_client_time The time when this event occurred, according to game client.
    # def _extractFromComplete(self, level:int, event_client_time:datetime):
    #     self._features.incValByIndex(feature_name="completeCount", index=level)
    #     # track latest completion of levels 8 & 16, for the timeToAnswerMS features.
    #     if (level == 8):
    #         self.latest_complete_lvl8 = event_client_time
    #     elif (level == 16):
    #         self.latest_complete_lvl16 = event_client_time
    #     # Handle tracking of level play times.
    #     if self.active_begin == None:
    #         sess_id = self._features.getValByName(feature_name="sessionID")
    #         Logger.Log(f"Got a 'Complete' event when there was no active 'Begin' event! Sess ID: {sess_id}, level: {level}", logging.ERROR)
    #     elif self.active_begin != level:
    #         sess_id = self._features.getValByName(feature_name="sessionID")
    #         Logger.Log(f"Got a 'Complete' event when the active 'Begin' was for a different level ({self.active_begin})! Sess ID: {sess_id}, level: {level}", logging.ERROR)
    #     else:
    #         self.end_times[level] = event_client_time
    #         self._calc_level_end(level)
    #         self._features.setValByIndex(feature_name="completed", index=level, new_value=1)
    #         try:
    #             self._features.incValByIndex(feature_name="totalLevelTime", index=level, increment=self._calcLevelTime(level))
    #         except Exception as err:
    #             raise(Exception(f"{type(err)} {str(err)}, level={level}, method=extractFromComplete, active_begin={self.active_begin}"))
    #         self.active_begin = None

    # ## Private function to extract features from a "SUCCEED" event.
    # #  The features affected are:
    # #  - succeedCount
    # #
    # #  @param level The level being played when succeed event occurred.
    # def _extractFromSucceed(self, level:int):
    #     self._features.incValByIndex(feature_name="succeedCount", index=level)

    # ## Private function to extract features from a "MENU_BUTTON" event.
    # #  The features affected are:
    # #  - end_times (used to calculate totalLevelTime and avgLevelTime)
    # #  - menuBtnCount
    # #  - totalLevelTime
    # #
    # #  @param level             The level being played when event occurred.
    # #  @param event_client_time The time when this event occurred, according to game client.
    # def _extractFromMenuBtn(self, level:int, event_client_time:datetime):
    #     self._features.incValByIndex(feature_name="menuBtnCount", index=level)
    #     if self.active_begin == None:
    #         sess_id = self._features.getValByName(feature_name="sessionID")
    #         Logger.Log(f"Got a 'Menu Button' event when there was no active 'Begin' event! Sess ID: {sess_id}, level: {level}", logging.ERROR)
    #     elif self.active_begin != level:
    #         sess_id = self._features.getValByName(feature_name="sessionID")
    #         Logger.Log(f"Got a 'Menu Button' event when the active 'Begin' was for a different level ({self.active_begin})! Sess ID: {sess_id}, level: {level}", logging.ERROR)
    #     else:
    #         self.end_times[level] = event_client_time
    #         self._calc_level_end(level)
    #         try:
    #             self._features.incValByIndex(feature_name="totalLevelTime", index=level, increment=self._calcLevelTime(level))
    #         except Exception as err:
    #             raise(Exception(f"{type(err)} {str(err)}, level={level}, method=extractFromMenuBtn, active_begin={self.active_begin}"))
    #         self.active_begin = None

    # ## Private function to extract features from a "SKIP_BUTTON" event.
    # #  The features affected are:
    # #  - totalSkips
    # #
    # #  @param level The level being played when reset button was pressed.
    # def _extractFromSkipBtn(self, level:int):
    #     self._features.incValByIndex(feature_name="totalSkips", index=level)
    #     self.active_begin = None

    # ## Private function to extract features from a "RESET_BTN_PRESS" event.
    # #  The features affected are:
    # #  - totalResets
    # #
    # #  @param level The level being played when reset button was pressed.
    # def _extractFromResetBtnPress(self, level:int):
    #     self._features.incValByIndex(feature_name="totalResets", index=level)

    # ## Private function to extract features from a "FAIL" event.
    # #  The features affected are:
    # #  - totalFails
    # #
    # #  @param level The level being played when the event occurred.
    # def _extractFromFail(self, level:int):
    #     self._features.incValByIndex(feature_name="totalFails", index=level)

    # ## Private function to extract features from a "SLIDER_MOVE_RELEASE" or 
    # #  "ARROW_MOVE_RELEASE" event.
    # #  The features affected are:
    # #  - totalMoveTypeChanges
    # #  - totalSliderMoves
    # #  - totalArrowMoves
    # #  - sliderAvgStdDevs
    # #  - sliderAvgRange
    # #
    # #  @param level      The level being played when event occurred.
    # #  @param event_data Parsed JSON data from the row being processed.
    # def _extractFromMoveRelease(self, level:int, event_data:Dict[str,Any], event_client_time:datetime):
    #     def isGoodMove(event_data):
    #         end_distance   = abs(event_data["correct_val"] - event_data["end_val"])
    #         start_distance = abs(event_data["correct_val"] - event_data["begin_val"])
    #         return end_distance < start_distance
    #     # first, log the type of move.
    #     if event_data["slider"] != self._last_adjust_type:
    #         self._last_adjust_type = event_data["slider"]
    #         # NOTE: We assume data are processed in order of event time.
    #         # If events are not sorted by time, the "move type changes" may be inaccurate.
    #         self._features.incValByIndex(feature_name="totalMoveTypeChanges", index=level)
    #     if event_data["slider"] == "AMPLITUDE":
    #         self.amp_move_counts[level] += 1
    #         if isGoodMove(event_data):
    #             self._features.incValByIndex(feature_name="amplitudeGoodMoveCount", index=level)
    #         if not level in self.saw_first_move.keys() or not self.saw_first_move[level]:
    #             self.saw_first_move[level] = True
    #             self._features.setValByIndex(feature_name="firstMoveType", index=level, new_value='A')
    #     elif event_data["slider"] == "OFFSET":
    #         self.off_move_counts[level] += 1
    #         if isGoodMove(event_data):
    #             self._features.incValByIndex(feature_name="offsetGoodMoveCount", index=level)
    #         if not level in self.saw_first_move.keys() or not self.saw_first_move[level]:
    #             self.saw_first_move[level] = True
    #             self._features.setValByIndex(feature_name="firstMoveType", index=level, new_value='O')
    #     elif event_data["slider"] == "WAVELENGTH":
    #         self.wave_move_counts[level] += 1
    #         if isGoodMove(event_data):
    #             self._features.incValByIndex(feature_name="wavelengthGoodMoveCount", index=level)
    #         if not level in self.saw_first_move.keys() or not self.saw_first_move[level]:
    #             self.saw_first_move[level] = True
    #             self._features.setValByIndex(feature_name="firstMoveType", index=level, new_value='W')
    #     # then, log things specific to slider move:
    #     if event_data["event_custom"] == "SLIDER_MOVE_RELEASE":
    #         self._features.incValByIndex(feature_name="totalSliderMoves", index=level)
    #         # These will be averages over the level. Per-row, just accumulate,
    #         # then we'll divide in the aggregate feature step.
    #         self._features.incValByIndex(feature_name="sliderAvgStdDevs", index=level,
    #                                     increment=event_data["stdev_val"])
    #         self._features.incValByIndex(feature_name="sliderAvgRange", index=level,
    #                                     increment= event_data["max_val"]
    #                                              - event_data["min_val"])
    #     else: # log things specific to arrow move:
    #         self._features.incValByIndex(feature_name="totalArrowMoves", index=level)

    #     if event_data['event_custom'] == 'ARROW_MOVE_RELEASE':
    #         begin_closeness, end_closeness = None, event_data['closeness']
    #         range = event_data['begin_val'] - event_data['end_val']
    #         range = range if range > 0 else range*-1
    #     else: #SLIDER MOVE RELEASE
    #         begin_closeness, end_closeness = event_data['begin_closeness'], event_data['end_closeness']
    #         range = event_data['max_val'] - event_data['min_val']

    #     if begin_closeness and not self.move_closenesses_tx[level]:
    #         self.move_closenesses_tx[level]['completeness'].append(begin_closeness)
    #         self.move_closenesses_tx[level]['t'].append(self.start_times[level])
    #         self.move_closenesses_tx[level]['range'].append(None)
    #     self.move_closenesses_tx[level]['completeness'].append(end_closeness)
    #     self.move_closenesses_tx[level]['t'].append(event_client_time)
    #     self.move_closenesses_tx[level]['range'].append(range)




    # ## Private function to extract features from a "QUESTION_ANSWER" event.
    # #  The features affected are:
    # #  - questionAnswered
    # #  - questionCorrect
    # #
    # #  @param event_data Parsed JSON data from the row being processed.
    # def _extractFromQuestionAnswer(self, event_data:Dict[str,Any], event_client_time:datetime):
    #     q_num = event_data["question"]
    #     if (q_num == 0):
    #         self.latest_answer_Q0 = event_client_time
    #     elif (q_num == 2):
    #         self.latest_answer_Q2 = event_client_time
    #     answer_time = self._calcAnswerTime(q_num=q_num, event_client_time=event_client_time)
    #     self._features.setValByIndex(feature_name="timeToAnswerMS", index=q_num, new_value=answer_time)
    #     self._features.setValByIndex(feature_name="questionAnswered", index=q_num,
    #                                 new_value=event_data["answered"])
    #     correctness = 1 if event_data["answered"] == event_data["answer"] else 0
    #     self._features.setValByIndex(feature_name="questionCorrect", index=q_num, new_value=correctness)

    # ## Private function to calculate percent of moves made of a given type,
    # #  for a given level.
    # #
    # #  @param key   The feature name for the type of move to calculate percentage on.
    # #  @param level The level for which we want to calculate a percentage.
    # def _calcPercentMoves(self, key:str, level:int) -> float:
    #     all_vals = [elem["val"] for elem in self._features.getValByName(feature_name=key).values()]
    #     num = sum(all_vals)
    #     if num == 0:
    #         return 0
    #     else:
    #         slider_vals = [elem["val"] for elem in self._features.getValByName(feature_name="totalSliderMoves").values()]
    #         arrow_vals = [elem["val"] for elem in self._features.getValByName(feature_name="totalArrowMoves").values()]
    #         denom = sum(slider_vals) + sum(arrow_vals)
    #         return num/denom

    # ## Private function to calculate the time spent on a given level.
    # #
    # #  @param lvl      The level whose play time should be calculated
    # #  @return         The play time if level is valid, -1 if level
    # #                  was not completed, 0 if level was never attempted.
    # def _calcLevelTime(self, lvl:int) -> int:
    #     # use 0 if not played, -1 if not completed
    #     if lvl in self._levels:
    #         if lvl in self.start_times and lvl in self.end_times:
    #             return (self.end_times[lvl] - self.start_times[lvl]).total_seconds()
    #         else:
    #             raise Exception(f"Level {lvl} is missing a start or end time")
    #     else:
    #         return 0
        
    # def _calcAnswerTime(self, q_num:int, event_client_time) -> Optional[int]:
    #     millis: Optional[float]
    #     if q_num == 0:
    #         millis = 1000.0 * (event_client_time - self.latest_complete_lvl8).total_seconds()
    #     elif q_num == 1:
    #         millis = 1000.0 * (event_client_time - self.latest_answer_Q0).total_seconds()
    #     elif q_num == 2:
    #         millis = 1000.0 * (event_client_time - self.latest_complete_lvl16).total_seconds()
    #     elif q_num == 3:
    #         millis = 1000.0 * (event_client_time - self.latest_answer_Q2).total_seconds()
    #     else:
    #         millis = None
    #     return int(millis) if millis is not None else None

    # ## Private function to do feature calculation at the end of a level.
    # #
    # #  @param lvl      The level whose features should be calculated
    # #  @return         (void)
    # def _calc_level_end(self, lvl:int) -> None:
    #     closenesses = self.move_closenesses_tx[lvl]['completeness']
    #     times = self.move_closenesses_tx[lvl]['t']
    #     ranges = self.move_closenesses_tx[lvl]['range']
    #     if times:
    #         try:
    #             X = [(times[i]-times[0]).seconds for i in range(len(times))]
    #         except Exception as err:
    #             Logger.Log(times[0])
    #             raise err
    #         y = closenesses
    #         if len(X) > 1:
    #             intercept, slope, r_sq = self._2D_linear_regression(X, y)
    #             r_sq = r_sq if not np.isnan(r_sq) else 0
    #         else:
    #             intercept, slope, r_sq = 0,0,0
    #         self._features.setValByIndex(feature_name='closenessIntercept', index=lvl, new_value=intercept)
    #         self._features.setValByIndex(feature_name='closenessSlope', index=lvl, new_value=slope)
    #         self._features.setValByIndex(feature_name='closenessR2', index=lvl, new_value=r_sq)

    #         if ranges[0] is None:
    #             del ranges[0]
    #             del times[0]

    #         X = [(times[i] - times[0]).seconds for i in range(len(times))]
    #         y = ranges
    #         if len(X) > 1:
    #             intercept, slope, r_sq = self._2D_linear_regression(X, y)
    #             r_sq = r_sq if not np.isnan(r_sq) else 0
    #         else:
    #             intercept, slope, r_sq = 0, 0, 0
    #         self._features.setValByIndex(feature_name='rangeIntercept', index=lvl, new_value=intercept)
    #         self._features.setValByIndex(feature_name='rangeSlope', index=lvl, new_value=slope)
    #         self._features.setValByIndex(feature_name='rangeR2', index=lvl, new_value=r_sq)


    # ## Private function to do feature calculation at the end of a level.
    # #
    # #  @param lvl      The level whose features should be calculated
    # #  @return         (void)
    # def _2D_linear_regression(self, x_vals:List[float], y_vals:List[float]):
    #     X, y = np.array(x_vals).reshape((-1,1)), np.array(y_vals)
    #     linreg = LinearRegression()
    #     linreg.fit(X, y)
    #     intercept, slope, r_sq = linreg.intercept_, linreg.coef_[0], linreg.score(X, y)
    #     return (intercept, slope, r_sq)
