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
    _TUTORIAL_MODE = [
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
    _ITEM_MARK_COMBINATIONS = [ ('food', 'sell'), ('food', 'use'), ('food', 'eat'),
        ('milk', 'sell'), ('milk', 'use'), ('poop', 'sell'), ('poop', 'use')
    ]

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
        self.features.features = {k: defaultdict(lambda: {'val': 0, 'prefix': 'lvl'}) if v else v
                                  for k,v in self.features.features.items()}
        for k in self.features.features.keys():
            if 'min' in k and 'window' in k:
                self._set_default_window_val(feature_name=k, val=float('inf'))

        self._NUM_SECONDS_PER_WINDOW = 5 * 60
        self._NUM_SECONDS_PER_WINDOW_OVERLAP = 1 * 60
        self._tiles = defaultdict(lambda: {'marks': [1,1,1,1], 'type':0})
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
        self._windows = []
        self._cur_windows = []



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
        event_type = row_with_complex_parsed[game_table.event_custom_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        # Check for invalid row.
        if row_with_complex_parsed[game_table.session_id_index] != self.session_id:
            logging.error("Got a row with incorrect session id!")
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="session_persistentSessionID") == 0:
                self.features.setValByName(feature_name="session_persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # if this is the first row
            if not self._client_start_time:
                self._client_start_time = event_client_time
                self._last_speed_change = self._client_start_time

            # set current windows
            secs_since_start = (event_client_time - self._client_start_time).seconds
            self._cur_windows = [secs_since_start // self._NUM_SECONDS_PER_WINDOW,
                                 (secs_since_start - self._NUM_SECONDS_PER_WINDOW_OVERLAP) // self._NUM_SECONDS_PER_WINDOW]
            # remove negative or duplicate windows
            if self._cur_windows[1] < 0:
                self._cur_windows[1] = 0
            if self._cur_windows[0] == self._cur_windows[1]:
                self._cur_windows = [self._cur_windows[0]]
            # make sure windows are both in the list of all windows
            for window in self._cur_windows:
                if not window in self._windows:
                    bisect.insort(self._windows, window)

            # Ensure we have private data initialized for this level.
            if not level in self.levels:
                bisect.insort(self.levels, level)

            # First, record that an event of any kind occurred, for the level & session
            self.features.incValByIndex(feature_name="window_eventCount", index=level)
            self.features.incAggregateVal(feature_name="session_sessionEventCount")

            # Then, handle cases for each type of event
            if LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "GAMESTATE":
                return
                self._extractFromGamestate(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "STARTGAME":
                self._extractFromStartgame(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "CHECKPOINT":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SELECTTILE":
                self._extractFromSelecttile(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SELECTFARMBIT":
                self._extractFromSelectfarmbit(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SELECTITEM":
                self._extractFromSelectitem(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SELECTBUY":
                self._extractFromSelectbuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "BUY":
                self._extractFromBuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "CANCELBUY":
                self._extractFromCancelbuy(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "ROADBUILDS":
                self._extractFromRoadbuilds(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "TILEUSESELECT":
                self._extractFromTileuseselect(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "ITEMUSESELECT":
                self._extractFromItemuseselect(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "TOGGLENUTRITION":
                self._extractFromTogglenutrition(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "TOGGLESHOP":
                self._extractFromToggleshop(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "TOGGLEACHIEVEMENTS":
                self._extractFromToggleachievements(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SKIPTUTORIAL":
                self._extractFromSkiptutorial(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "SPEED":
                self._extractFromSpeed(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "ACHIEVEMENT":
                self._extractFromAchievement(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "FARMBITDEATH":
                self._extractFromFarmbitdeath(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "BLURB":
                self._extractFromBlurb(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "CLICK":
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "RAINSTOPPED":
                self._extractFromRainstopped(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "HISTORY":
                self._extractFromHistory(event_client_time, event_data_complex_parsed)
            elif LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "ENDGAME":
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
        client_time = d["timestamp"]
        num_food_produced = d["num_food_produced"]
        num_milk_produced = d["num_milk_produced"]
        num_poop_produced = d["num_poop_produced"]


        cur_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        items = LakelandExtractor.array_to_mat(4,items)
        tiles = LakelandExtractor.array_to_mat(4,tiles)
        farmbits = LakelandExtractor.array_to_mat(9, farmbits)
        num_farmbits = len(farmbits)

        for it in items:
            type = it[2]
            key = LakelandExtractor._ENUM_TO_STR["ITEM TYPE"][type]
            cur_num_items_on_screen[key] += 1
        for t in tiles:
            type = t[3]
            key = LakelandExtractor._ENUM_TO_STR["TILE TYPE"][type]
            cur_num_items_on_screen[key] += 1
        for (key, cur_num) in cur_num_items_on_screen.items():
            max_num_feature_name = 'window_max_number_of_'+ key +'_in_play'
            min_num_feature_name = 'window_min_number_of_' + key + '_in_play'
            self._set_feature_max_in_cur_windows(cur_num,max_num_feature_name)
            self._set_feature_min_in_cur_windows(cur_num, min_num_feature_name)
        # for (k,cur_num) in cur_num_items_on_screen.items():
        #     if cur_num > self._max_num_items_on_screen[k]:
        #         self._max_num_items_on_screen = cur_num

        for combo_type, combo_mark in LakelandExtractor._ITEM_MARK_COMBINATIONS:
            # each item type is it[2] and the mark is it[3]
            match = lambda it: combo_type == it[2] and combo_mark == it[3]
            count_matches = sum([match(it) for it in items])
            count_matches_per_capita = count_matches/num_farmbits
            max_per_capita_fname = f"window_max_num_per_capita_of_{combo_type}_marked_{combo_mark}"
            min_per_capita_fname = f"window_min_num_per_capita_of_{combo_type}_marked_{combo_mark}"
            total_fname = f"window_total_{combo_type}_marked_{combo_mark}"
            self._set_feature_max_in_cur_windows(max_per_capita_fname, count_matches_per_capita)
            self._set_feature_min_in_cur_windows(min_per_capita_fname, count_matches_per_capita)
            self._increment_feature_in_cur_windows(total_fname,count_matches)







        food_marked_eat = lambda it: it[2] == "food" and it[3] == "feed"
        num_food_marked_eat = sum(list(map(food_marked_eat, items)))
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
                    time_per_blurb = LakelandExtractor.list_deltas(blurb_history)
                    self._tutorial_times_per_blurb[tutorial] = time_per_blurb



    def _extractFromSelecttile(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._increment_feature_in_cur_windows("window_num_inspect_tile")

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
            self._money_spent_per_item[LakelandExtractor._ENUM_TO_STR["BUYS"][d["buy"]]] += self._selected_buy_cost
            self.features.incAggregateVal(feature_name="session_money_spent", increment=self._selected_buy_cost)
            self._increment_feature_in_cur_windows(feature_name="window_money_spent", increment=self._selected_buy_cost)
            self._selected_buy_cost = 0
            if d["buy"] == 1: # home
                self._num_farmbits += 1;

            num_buy_feature_name = LakelandExtractor.get_feature(base='window_num_buy_', enum=d["buy"], enum_type='BUYS')
            self._increment_feature_in_cur_windows(feature_name=num_buy_feature_name, increment=1)
            money_spent_feature_name = LakelandExtractor.get_feature(base='window_money_spent_on_', enum=d["buy"], enum_type='BUYS')
            self._increment_feature_in_cur_windows(feature_name=money_spent_feature_name, increment=1)

            tile_hovers = d['buy_hovers']
            num_hovers = len(tile_hovers)
            num_hovers_feature_name = LakelandExtractor.get_feature(base='window_total_num_tiles_hovered_before_placing_', enum=d['buy'], enum_type='BUYS')
            self._increment_feature_in_cur_windows(feature_name=num_buy_feature_name, increment=num_hovers)


    def _extractFromCancelbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        self._selected_buy_cost = 0

    def _extractFromRoadbuilds(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromTileuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile_array, marks = d["tile"], d["marks"]
        if self._tile_mark_change(tile_array, marks):
            self._increment_feature_in_cur_windows("window_num_change_tile_mark")
        total_farm_marks1 = [t["marks"][0] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_farm_marks2 = [t["marks"][1] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_dairy_marks = [t["marks"][0] for t in self._tiles.values() if t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['livestock']]
        total_marks = total_dairy_marks + total_farm_marks1 + total_farm_marks2
        allocations_per_capita = {LakelandExtractor._ENUM_TO_STR['MARK'][k]:v/self._num_farmbits for k,v in Counter(total_marks).items()}



    def _extractFromItemuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        item_array = d["item"]
        curr_mark = item_array[3]
        if d["prev_mark"] != curr_mark:
            self.features.incAggregateVal("window_num_change_item_mark")

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
            self._increment_feature_in_cur_windows("window_num_open_shop")

    def _extractFromToggleachievements(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        if d["achievements_open"]:
            self._increment_feature_in_cur_windows("window_num_open_achievements")

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
            if tut in LakelandExtractor._TUTORIAL_MODE and not tut_end:
                return False
        return True

    def _avg_time_per_tutorial_mode_blurb(self):
        all_deltas = []
        for tut in LakelandExtractor._TUTORIAL_MODE:
            all_deltas.extend(self._tutorial_times_per_blurb[tut])
        return sum(all_deltas)/len(all_deltas)

    def _avg_lake_nutrition(self, all_nutritions):
        lake_nutritions = []
        for og_type, nutrition in zip(self._tile_og_types, all_nutritions):
            if LakelandExtractor._ENUM_TO_STR["TILE TYPE"][og_type] == "lake":
                lake_nutritions.append(nutrition)
        return sum(lake_nutritions)/len(lake_nutritions)

    def _increment_feature_in_cur_windows(self, feature_name, increment=None):
        increment = increment or 1
        for w in self._cur_windows:
            self.features.incValByIndex(feature_name=feature_name, index=w, increment=increment)

    def _set_feature_max_in_cur_windows(self, feature_name, val):
        for w in self._cur_windows:
            prev_val = self.features.getValByIndex(feature_name=feature_name, index=w)
            if val > prev_val:
                self.features.setValByIndex(feature_name=feature_name, index=w, new_value=val)

    def _set_feature_min_in_cur_windows(self, feature_name, val):
        for w in self._cur_windows:
            prev_val = self.features.getValByIndex(feature_name=feature_name, index=w)
            if val < prev_val:
                self.features.setValByIndex(feature_name=feature_name, index=w, new_value=val)

    def _set_default_window_val(self, feature_name, val):
        self.features.features[feature_name] = defaultdict(lambda: {'val': val, 'prefix': 'lvl'})

    def calculateAggregateFeatures(self):
        buys = list(LakelandExtractor._ENUM_TO_STR['BUYS'].values())
        ave_num_tile_features = ["window_ave_num_tiles_hovered_before_placing_" + buy for buy in
                                 LakelandExtractor._ENUM_TO_STR['BUYS'].values()]
        for buy in buys:
            num_buys_feature = 'window_num_buy_' + buy
            num_hovers_feature = "window_total_num_tiles_hovered_before_placing_" + buy
            ave_hovers_feature = "window_ave_num_tiles_hovered_before_placing_" + buy
            for window in self.features.features[num_buys_feature].keys():
                avg_hovers = self.features.getValByIndex(num_hovers_feature, window) / self.features.getValByIndex(
                    num_buys_feature, window)
                self.features.setValByIndex(feature_name=ave_hovers_feature, index=window)




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

