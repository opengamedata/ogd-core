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
from enum import Enum
from collections import defaultdict



## @class CrystalExtractor
#  Extractor subclass for extracting features from Crystal game data.
class LakelandExtractor(Extractor):

    _STR_TO_ENUM = utils.loadJSONFile("Lakeland Enumerators/Lakeland Enumerators.json")
    _ENUM_TO_STR = {cat: {y: x for x, y in ydict.items()} for cat, ydict in _STR_TO_ENUM.items()}

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
        self._tile_marks = defaultdict(lambda x: [1,1,1,1])
        self._client_start_time = None
        self._num_checkpoints_completed = 0



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
        event_type = row_with_complex_parsed[game_table.event_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        if not self._client_start_time:
            self._client_start_time = event_client_time
        # Check for invalid row.
        if row_with_complex_parsed[game_table.session_id_index] != self.session_id:
            logging.error("Got a row with incorrect session id!")
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="persistentSessionID") == 0:
                self.features.setValByName(feature_name="persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # Ensure we have private data initialized for this level.
            if not level in self.levels:
                bisect.insort(self.levels, level)
                # initialization
            # First, record that an event of any kind occurred, for the level & session
            self.features.incValByIndex(feature_name="eventCount", index=level)
            self.features.incAggregateVal(feature_name="sessionEventCount")
            # Then, handle cases for each type of event
            if self._LOG_CATS[event_type] == "GAMESTATE":
                self._extractFromGamestate(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "STARTGAME":
                self._extractFromStartgame(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "CHECKPOINT":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SELECTTILE":
                self._extractFromSelecttile(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SELECTFARMBIT":
                self._extractFromSelectfarmbit(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SELECTITEM":
                self._extractFromSelectitem(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SELECTBUY":
                self._extractFromSelectbuy(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "BUY":
                self._extractFromBuy(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "CANCELBUY":
                self._extractFromCancelbuy(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "ROADBUILDS":
                self._extractFromRoadbuilds(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "TILEUSESELECT":
                self._extractFromTileuseselect(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "ITEMUSESELECT":
                self._extractFromItemuseselect(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "TOGGLENUTRITION":
                self._extractFromTogglenutrition(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "TOGGLESHOP":
                self._extractFromToggleshop(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "TOGGLEACHIEVEMENTS":
                self._extractFromToggleachievements(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SKIPTUTORIAL":
                self._extractFromSkiptutorial(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "SPEED":
                self._extractFromSpeed(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "ACHIEVEMENT":
                self._extractFromAchievement(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "FARMBITDEATH":
                self._extractFromFarmbitdeath(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "BLURB":
                self._extractFromBlurb(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "CLICK":
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "RAINSTOPPED":
                self._extractFromRainstopped(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "HISTORY":
                self._extractFromHistory(event_client_time, event_data_complex_parsed)
            elif self._LOG_CATS[event_type] == "ENDGAME":
                self._extractFromEndgame(event_client_time, event_data_complex_parsed)
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))

    def _extractFromGamestate(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromStartgame(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromCheckpoint(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._num_checkpoints_completed += 1
        if self._num_checkpoints_completed == 50:
            self.features.setValByName(feature_name="time_in_tutorial_mode", new_value=event_client_time-self._client_start_time)

    def _extractFromSelecttile(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self.features.incAggregateVal("num_inspect_tile")

    def _extractFromSelectfarmbit(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromSelectitem(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromSelectbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromBuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["success"]:
            self.features.incAggregateVal(feature_name=
                                          self._get_feature(base='num_buy_',enum=d["buy"],enum_type='Buys'))

    def _extractFromCancelbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromRoadbuilds(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromTileuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile_array, marks = d["tile"], d["marks"]
        if self._tile_mark_change(tile_array, marks):
            self.features.incAggregateVal("num_change_tile_mark")


    def _extractFromItemuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        item_array = d["item"]
        curr_mark = item_array[3]
        if d["prev_mark"] != curr_mark:
            self.features.incAggregateVal("num_change_tile_mark")

    def _extractFromTogglenutrition(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromToggleshop(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["shop_open"]:
            self.features.incAggregateVal("num_open_buy_menu")

    def _extractFromToggleachievements(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["achievements_open"]:
            self.features.incAggregateVal("num_open_achievements")

    def _extractFromSkiptutorial(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromSpeed(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromAchievement(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromFarmbitdeath(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromBlurb(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromClick(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromRainstopped(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromHistory(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromEndgame(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    # UTILS

    def _tile_mark_change(self, tile_array, marks):
        tx,ty = tile_array[4], tile_array[5]
        if marks == self._tile_marks[(tx,ty)]:
            return False
        else:
            self._tile_marks[(tx,ty)] = marks
            return True

    @staticmethod
    def get_feature(base, enum, enum_type):
        return base + LakelandExtractor._ENUM_TO_STR[enum_type][enum]

    @staticmethod
    def str_to_int(str):
        return int(str.strip())
