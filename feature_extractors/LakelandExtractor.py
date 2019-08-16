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
from collections import defaultdict, Counter
import copy



## @class CrystalExtractor
#  Extractor subclass for extracting features from Crystal game data.
class LakelandExtractor(Extractor):
    _tutorial_mode = [
        "build_a_house",
        "buy_food",
        "build_a_farm",
        "timewarp",
        "sell_food",
        "buy_fertilizer",
        "buy_livestock",
        "livestock",
        "poop",
    ]
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
        self._tiles = defaultdict(lambda x: {'marks': [1,1,1,1], 'type':0})
        self._tile_og_types = []
        self._client_start_time = None
        self._tutorial_start_and_end_times = {key: [0,0] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        self._tutorial_times_per_blurb = {key: [] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        self._time_per_speed = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['SPEED']}
        self._last_speed_change = None
        self._time_in_nutrition_view = 0
        self._last_nutrition_open = None
        self._money_spent_per_item = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['BUYS']}
        self._selected_buy_cost = 0
        self._max_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        self._num_farmbits = 0



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
            self._last_speed_change = self._client_start_time
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
            if LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "GAMESTATE":
                self._extractFromGamestate(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "STARTGAME":
                self._extractFromStartgame(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "CHECKPOINT":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SELECTTILE":
                self._extractFromSelecttile(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SELECTFARMBIT":
                self._extractFromSelectfarmbit(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SELECTITEM":
                self._extractFromSelectitem(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SELECTBUY":
                self._extractFromSelectbuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "BUY":
                self._extractFromBuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "CANCELBUY":
                self._extractFromCancelbuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "ROADBUILDS":
                self._extractFromRoadbuilds(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "TILEUSESELECT":
                self._extractFromTileuseselect(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "ITEMUSESELECT":
                self._extractFromItemuseselect(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "TOGGLENUTRITION":
                self._extractFromTogglenutrition(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "TOGGLESHOP":
                self._extractFromToggleshop(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "TOGGLEACHIEVEMENTS":
                self._extractFromToggleachievements(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SKIPTUTORIAL":
                self._extractFromSkiptutorial(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "SPEED":
                self._extractFromSpeed(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "ACHIEVEMENT":
                self._extractFromAchievement(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "FARMBITDEATH":
                self._extractFromFarmbitdeath(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "BLURB":
                self._extractFromBlurb(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "CLICK":
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "RAINSTOPPED":
                self._extractFromRainstopped(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "HISTORY":
                self._extractFromHistory(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type] == "ENDGAME":
                self._extractFromEndgame(event_client_time, event_data_complex_parsed)
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))

    def _extractFromGamestate(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tiles = d["tiles"]
        farmbits = d["farmbits"]
        items = d["items"]
        money = d["money"]
        speed = d["speed"]
        achievements = d["achievements"]
        num_checkpoints_completed = d["num_checkpoints_completed"]
        raining = d["raining"]
        curr_selection_type = d["curr_selection_type"]
        curr_selection_data = d["curr_selection_data"]
        camera_center = d["camera_center"]
        gametime = d["gametime"]
        client_time = d["client_time"]
        num_food_produced = d["num_food_produced"]
        num_milk_produced = d["num_milk_produced"]
        num_poop_produced = d["num_poop_produced"]


        cur_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        items = LakelandExtractor.array_to_mat(4,items)
        tiles = LakelandExtractor.array_to_mat(4,tiles)
        farmbits = LakelandExtractor.array_to_mat(9, farmbits)
        for it in items:
            type = it[2]
            key = LakelandExtractor._ENUM_TO_STR["ITEM TYPE"][type]
            cur_num_items_on_screen[key] += 1
        for t in tiles:
            type = t[3]
            key = LakelandExtractor._ENUM_TO_STR["TILE TYPE"][type]
            cur_num_items_on_screen[key] += 1
        for (k,cur_num) in cur_num_items_on_screen.items():
            if cur_num > self._max_num_items_on_screen[k]:
                self._max_num_items_on_screen = cur_num


        food_marked_eat = lambda it: it[2] == "food" and it[3] == "feed"
        num_food_marked_eat = sum(list(map(food_marked_eat, items)))
        num_farmbits = len(d["farmbits"]//9)
        num_food_marked_eat_per_capita = num_food_marked_eat/num_farmbits

        total_money_earned = sum(self._money_spent_per_item.values()) + money


    def _extractFromStartgame(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._tile_og_types = d["tile_states"]

    def _extractFromCheckpoint(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["event_type"] == 'tutorial':
            tutorial = d["event_label"]
            is_tutorial_end = 1 if d["event_category"] == 'end' else 0
            self._tutorial_start_and_end_times[tutorial][is_tutorial_end] = event_client_time
            if is_tutorial_end:
                average_screen_time = 0
                if d["blurb_history"]:
                    blurb_history = d["blurb_history"]
                    time_per_blurb = LakelandExtractor._list_deltas(blurb_history)
                    self._tutorial_times_per_blurb[tutorial] = time_per_blurb



    def _extractFromSelecttile(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self.features.incAggregateVal("num_inspect_tile")

    def _extractFromSelectfarmbit(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromSelectitem(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromSelectbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._selected_buy_cost = d["cost"]

    def _extractFromBuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["success"]:
            self.features.incAggregateVal(feature_name=
                                          self._get_feature(base='num_buy_', enum=d["buy"], enum_type='Buys'))
            self._money_spent_per_item[LakelandExtractor._ENUM_TO_STR["BUYS"][d["buy"]]] += self._selected_buy_cost
            self.features.incAggregateVal(feature_name="money_spent", increment=self._selected_buy_cost)
            self._selected_buy_cost = 0
            if d["buy"] == 1: # home
                self._num_farmbits += 1;

    def _extractFromCancelbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._selected_buy_cost = 0

    def _extractFromRoadbuilds(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromTileuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile_array, marks = d["tile"], d["marks"]
        if self._tile_mark_change(tile_array, marks):
            self.features.incAggregateVal("num_change_tile_mark")
        total_farm_marks1 = [t["marks"][0] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_farm_marks2 = [t["marks"][1] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_dairy_marks = [t["marks"][0] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['dairy']]
        total_marks = total_dairy_marks + total_farm_marks1 + total_farm_marks2
        allocations_per_capita = {LakelandExtractor._ENUM_TO_STR['MARK'][k]:v/self._num_farmbits for k,v in Counter(total_marks).items()}



    def _extractFromItemuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        item_array = d["item"]
        curr_mark = item_array[3]
        if d["prev_mark"] != curr_mark:
            self.features.incAggregateVal("num_change_item_mark")

    def _extractFromTogglenutrition(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        toggle_opened = d["to_state"]
        if not toggle_opened:
            self._time_in_nutrition_view += event_client_time - self._last_nutrition_open
        else: # if nutriton opened
            self._last_nutrition_open = event_client_time


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
        cur_speed, prev_speed = d["cur_speed"], d["prev_speed"]
        if cur_speed != prev_speed:
            time_at_prev_speed = event_client_time - self._last_speed_change
            self._last_speed_change = event_client_time
            self._time_per_speed[LakelandExtractor._ENUM_TO_STR[prev_speed]] += time_at_prev_speed



    def _extractFromAchievement(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromFarmbitdeath(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._num_farmbits -= 1

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
        type = tile_array[3]
        self._tiles[(tx, ty)]['type'] = type
        if marks == self._tiles[(tx,ty)]['marks']:
            return False
        else:
            self._tiles[(tx,ty)]['marks'] = marks
            return True

    def _is_tutorial_mode_over(self):
        for tut, [tut_start, tut_end] in self._tutorial_start_and_end_times.items():
            if tut in LakelandExtractor._tutorial_mode and not tut_end:
                return False
        return True

    def _avg_time_per_tutorial_mode_blurb(self):
        all_deltas = []
        for tut in LakelandExtractor._tutorial_mode:
            all_deltas.extend(self._tutorial_times_per_blurb[tut])
        return sum(all_deltas)/len(all_deltas)

    def _avg_lake_nutrition(self, all_nutritions):
        lake_nutritions = []
        for og_type, nutrition in zip(self._tile_og_types, all_nutritions):
            if LakelandExtractor._ENUM_TO_STR["TILE TYPE"][og_type] == "lake":
                lake_nutritions.append(nutrition)
        return sum(lake_nutritions)/len(lake_nutritions)

            




    @staticmethod
    def get_feature(base, enum, enum_type):
        return base + LakelandExtractor._ENUM_TO_STR[enum_type][enum]

    @staticmethod
    def str_to_int(str):
        return int(str.strip())

    @staticmethod
    def list_deltas(l):
        return [l[i]-l[i-1] for i in range(1,len(l))]

    @staticmethod
    def onscreen_item_dict():
        ret = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['ITEM TYPE']}
        ret.update({key: 0 for key in LakelandExtractor._STR_TO_ENUM['TILE TYPE']})
        return ret

    @staticmethod
    def array_to_mat(num_columns, arr):
        assert len(arr) % num_columns == 0
        return [arr[i:i+num_columns] for i in range(0, len(arr), num_columns)]

