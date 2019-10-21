## import standard libraries
import bisect
import datetime
import logging
import json

## import local files
import utils
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema
from collections import defaultdict, Counter
from math import sqrt


## @class LakelandExtractor
#  Extractor subclass for extracting features from Lakeland game data.
class LakelandExtractor(Extractor):
    _SESS_PREFIX = 'sess'
    _WINDOW_PREFIX = ''
    _TUTORIAL_MODE = [
        "build_a_house",
        "buy_food",
        "build_a_farm",
        "timewarp",
        "sell_food",
        "buy_fertilizer",
        "buy_livestock",
    ]
    _STR_TO_ENUM = utils.loadJSONFile("Lakeland Enumerators/Lakeland Enumerators.json")
    _ENUM_TO_STR = {cat: {y: x for x, y in ydict.items()} for cat, ydict in _STR_TO_ENUM.items()}
    _ITEM_MARK_COMBINATIONS = [('food', 'sell'), ('food', 'use'), ('food', 'eat'),
                               ('milk', 'sell'), ('milk', 'use'), ('poop', 'sell'), ('poop', 'use')
                               ]
    _EMOTE_STR_TO_AFFECT = {
        "null": 0,
        "fullness_motivated_txt": 0,
        "fullness_desperate_txt": -1,
        "energy_desperate_txt": -1,
        "joy_motivated_txt": 0,
        "joy_desperate_txt": -1,
        "puke_txt": -1,
        "yum_txt": 0,
        "tired_txt": -1,
        "happy_txt": 1,
        "swim_txt": 0,
        "sale_txt": 0
    }

    _TUT_NAME_COMPLIANT_BUY_NAME = [
        ("build_a_house", "house"),
        ("buy_food", "food"),
        ("build_a_farm", "farm"),
        ("buy_fertilizer", "fertilizer"),
        ("buy_livestock", "livestock"),
    ]
    _BUILDING_TYPES = ["home", "farm", "livestock"]

    ## Constructor for the LakelandExtractor class.
    #  Initializes some custom private data (not present in base class) for use
    #  when calculating some features.
    #  Sets the sessionID feature.
    #
    #  @param session_id The id number for the session whose data is being processed
    #                    by this extractor instance.
    #  @param game_table A data structure containing information on how the db
    #                    table associated with this game is structured.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema,
                 err_logger: logging.Logger, std_logger: logging.Logger):
        # Set window and overlap size
        config = game_schema.schema()['config']
        self._NUM_SECONDS_PER_WINDOW = config['WINDOW_SIZE_SECONDS']
        self._NUM_SECONDS_PER_WINDOW_OVERLAP = config["WINDOW_OVERLAP_SECONDS"]
        # set window range
        max_secs = max(p[0] - p[1] for p in game_table.playtimes).seconds
        self.window_range = range(max_secs // self._NUM_SECONDS_PER_WINDOW + 1)
        # Initialize superclass
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema,
                         err_logger=err_logger, std_logger=std_logger)
        # Set any 'min' feature to have a default of positive infinity
        for k in self.features.features.keys():
            if 'min' in k:
                if 'window' in k:
                    self._set_default_window_val(feature_name=k, val=float('inf'))
                if 'session' in k:
                    self._set_default_session_val(feature_name=k, val=float('inf'))

        # Initialize Lakeland variables
        self._tiles = defaultdict(lambda: {'marks': [1, 1, 1, 1], 'type': 0})
        self._tile_og_types = []
        self._client_start_time = None
        self._tutorial_start_and_end_times = {key: [None, None] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        self._tutorial_times_per_blurb = {key: [] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        self._time_per_speed = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['SPEED']}
        self._last_speed_change = None
        self._nutrition_view_on = False
        self._last_nutrition_open = None
        self._money_spent_per_item = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['BUYS']}
        self._selected_buy_cost = 0
        self._max_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        self._num_farmbits = 0
        self._population_history = [(0, 0)]
        self._emotes_by_window = defaultdict(lambda: [])
        self._windows = []
        self._cur_windows = []
        self.prev_windows = []
        self._curr_money = 0
        self._cur_speed = 2  # default is play, 2
        self._tutorial_compliance = {tut: None for tut in LakelandExtractor._TUTORIAL_MODE}
        self.lake_xys = []
        self.average_handler_window = defaultdict(lambda: {k: {'n': 0, 'total': 0} for k in self.window_range})
        self.average_handler_session = defaultdict(lambda: {'n': 0, 'total': 0})
        self.building_xys = []

    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        # put some data in local vars, for readability later.
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_type = row_with_complex_parsed[game_table.event_custom_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index]
        server_time = row_with_complex_parsed[game_table.server_time_index]

        # Check for invalid row.
        row_sess_id = row_with_complex_parsed[game_table.session_id_index]
        if row_sess_id != self.session_id:
            self._err_logger.error(f"Got a row with incorrect session id! Expected {self.session_id}, got {row_sess_id}!")
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.features.getValByName(feature_name="session_persistentSessionID") == 0:
                self.features.setValByName(feature_name="session_persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # if this is the first row
            if not self._client_start_time:
                # initialize this time as the start
                self._client_start_time = event_client_time
                self._last_speed_change = self._client_start_time

            # set current windows
            self._prev_windows = self._cur_windows
            self._cur_windows = self._get_windows_at_time(event_client_time)

            # Record that an event of any kind occurred, for the window & session
            self._increment_feature_in_cur_windows(feature_name="window_eventCount", increment=1)
            self.features.incAggregateVal(feature_name="session_sessionEventCount")
            time_since_start = event_client_time - self._client_start_time
            self.features.setValByName(feature_name="sessionDuration",
                                       new_value=time_since_start)

            # Then, handle cases for each type of event
            if LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper() == "GAMESTATE":
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
        timestamp = d["timestamp"]
        num_food_produced = d["num_food_produced"]
        num_milk_produced = d["num_milk_produced"]
        num_poop_produced = d["num_poop_produced"]
        tiles = LakelandExtractor.read_stringified_array(d["tiles"])
        farmbits = LakelandExtractor.read_stringified_array(d["farmbits"])
        items = LakelandExtractor.read_stringified_array(d["items"])

        self.feature_inc("num_food_produced", num_food_produced)
        self.feature_inc("num_milk_produced", num_milk_produced)
        self.feature_inc("num_poop_produced", num_poop_produced)

        cur_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        items = LakelandExtractor.array_to_mat(4, items)
        tiles = LakelandExtractor.array_to_mat(4, tiles)
        tile_nutritions = [t[1] for t in tiles]  # 1 is the nutrition index
        farmbits = LakelandExtractor.array_to_mat(9, farmbits)

        for it in items:
            type = it[2]
            key = LakelandExtractor._ENUM_TO_STR["ITEM TYPE"][type]
            cur_num_items_on_screen[key] += 1
        for t in tiles:
            type = t[3]
            key = LakelandExtractor._ENUM_TO_STR["TILE TYPE"][type]
            if key in cur_num_items_on_screen:
                cur_num_items_on_screen[key] += 1
        for (key, cur_num) in cur_num_items_on_screen.items():
            max_num_feature_name = 'window_max_number_of_' + key + '_in_play'
            min_num_feature_name = 'window_min_number_of_' + key + '_in_play'
            self._set_feature_max_in_cur_windows(max_num_feature_name, cur_num)
            self._set_feature_min_in_cur_windows(min_num_feature_name, cur_num)

        total_money_earned = sum(self._money_spent_per_item.values()) + money
        self.features.setValByName(feature_name="session_money_earned", new_value=total_money_earned)
        avg_lake_nutrition = self._avg_lake_nutrition(tile_nutritions)
        self._set_feature_max_min_sess_win(fname_base="ave_lake_nutrition", val=avg_lake_nutrition)

        farms_low_productivity = [t for t in tiles if t[3] == 9 and t[
            1] < 3]  # type == farm and nutrition < 3 (the circle is heavily black)
        self._set_feature_max_min_sess_win("num_farms_low_productivity", len(farms_low_productivity))

        lake_bloom = [t for t in tiles if t[3] == 5 and t[1] > 25]  # lake tiles bloom when nutrition > 10% of 255,
        # so technically not all tiles > 25 nutrition are blooming, but we will put the cutoff here
        self._set_feature_max_min_sess_win("num_lake_tiles_in_bloom", len(lake_bloom))

    def _extractFromStartgame(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile_states = d["tile_states"]
        tile_nutritions = d["tile_nutritions"]
        self._tile_og_types = d["tile_states"]
        self.lake_xys = self.get_tile_types_xys(['lake'])

    def _extractFromCheckpoint(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        event_category = d["event_category"]
        event_label = d["event_label"]
        event_type = d["event_type"]
        blurb_history = d["blurb_history"]
        client_time = d["client_time"]
        cont = d["continue"]
        language = d["language"]
        audio = d["audio"]
        fullscreen = d["fullscreen"]
        if d["event_type"] == 'tutorial':
            tutorial = d["event_label"]
            is_tutorial_end = 1 if d["event_category"] == 'end' else 0
            self._tutorial_start_and_end_times[tutorial][is_tutorial_end] = event_client_time
            if is_tutorial_end:
                time_since_start = event_client_time - self._client_start_time
                fname = f"session_secs_to_{tutorial}_tutorial"
                self.features.setValByName(feature_name=fname, new_value=time_since_start)
                self._increment_feature_in_cur_windows(feature_name="window_num_encounter_tutorial")
                self.features.incAggregateVal(feature_name="session_count_of_tutorials")
                average_screen_time = 0
                if d["blurb_history"]:
                    client_time = d["client_time"]
                    blurb_history = d["blurb_history"]
                    self.process_history_array(blurb_history, client_time)
                    time_per_blurb = LakelandExtractor.list_deltas(blurb_history)
                    self._tutorial_times_per_blurb[tutorial] = time_per_blurb
                    if len(time_per_blurb) > 0:
                        avg_secs_per_blurb = sum([t.seconds + t.microseconds / 1000000 for t in time_per_blurb]) / len(
                            time_per_blurb) / 1000
                    else:
                        avg_secs_per_blurb = 0
                    fname = f"session_avg_secs_per_blurb_in_{tutorial}_tutorial"
                    self.features.setValByName(feature_name=fname, new_value=avg_secs_per_blurb)

    def _extractFromSelecttile(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile = d["tile"]
        marks = d["marks"]
        self._increment_feature_in_cur_windows("window_num_inspect_tile")

    def _extractFromSelectfarmbit(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        farmbit = d["farmbit"]

    def _extractFromSelectitem(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        item = d["item"]
        mark = d["mark"]

    def _extractFromSelectbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        buy = d["buy"]
        cost = d["cost"]
        curr_money = d["curr_money"]
        success = d["success"]
        self._selected_buy_cost = d["cost"]
        self._curr_money = d["curr_money"]

    def _extractFromBuy(self, event_client_time, event_data_complex_parsed):

        d = event_data_complex_parsed
        buy = d["buy"]
        tile = d["tile"]
        success = d["success"]
        buy_hovers = d["buy_hovers"]
        client_time = d["client_time"]
        if d["success"]:
            tx, ty = d['tile'][4], d['tile'][5]
            chosen_tile = d['tile']
            buy_name = LakelandExtractor._ENUM_TO_STR['BUYS'][d['buy']]
            self._money_spent_per_item[buy_name] += self._selected_buy_cost
            self.features.incAggregateVal(feature_name="session_money_spent", increment=self._selected_buy_cost)
            self._increment_feature_in_cur_windows(feature_name="window_money_spent", increment=self._selected_buy_cost)

            num_buy_feature_name = f'window_num_buy_{buy_name}'
            self._increment_feature_in_cur_windows(feature_name=num_buy_feature_name, increment=1)
            money_spent_feature_name = f'window_money_spent_on_{buy_name}'
            self._increment_feature_in_cur_windows(feature_name=money_spent_feature_name,
                                                   increment=self._selected_buy_cost)

            time_to_first_fname = f"session_secs_to_first_{buy_name}"
            if not self.features.getValByName(time_to_first_fname):
                self.features.setValByName(time_to_first_fname, event_client_time - self._client_start_time)
            self._selected_buy_cost = 0
            if d["buy"] == 1:  # home
                self._change_population(event_client_time, 1)

            tile_hovers = d['buy_hovers']
            avg_hovers_window_fname = 'window_ave_num_tiles_hovered_before_placing_' + buy_name
            avg_hovers_session_fname = 'session_ave_num_tiles_hovered_before_placing_' + buy_name
            self.average_in_windows_and_session(window_feature=avg_hovers_window_fname,
                                                session_feature=avg_hovers_session_fname, value=len(tile_hovers))

            if buy_name == 'farm':
                chosen_txy = (tx, ty)  # tile tx,ty
                window_fname = "window_percent_building_a_farm_on_highest_nutrition_tile"
                session_fname = "session_percent_building_a_farm_on_highest_nutrition_tile"
                for t in tile_hovers:
                    if t[3] == 1:  # t has the current type of land (only type that farms can be built on)
                        if t[1] - 2 > chosen_tile[1]:  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
                            self.average_in_windows_and_session(window_fname, session_fname,
                                                                0)  # failed to put on highest nutrition tile
                            break
                else:
                    self.average_in_windows_and_session(window_fname, session_fname, 1)

            if buy_name == 'fertilizer':
                chosen_txy = (tx, ty)  # tile tx,ty
                window_fname = "window_percent_placing_fertilizer_on_lowest_nutrient_farm"
                session_fname = "session_percent_placing_fertilizer_on_lowest_nutrient_farm"
                for t in tile_hovers:
                    if t[3] == 9:  # t has the current type of farm (only type that fertilizer can be built on)
                        if t[1] - 2 < chosen_tile[1]:  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
                            self.average_in_windows_and_session(window_fname, session_fname,
                                                                0)  # failed to put on lowest nutrition tile
                            break
                else:
                    self.average_in_windows_and_session(window_fname, session_fname, 1)

            for tut, compliant_buy in LakelandExtractor._TUT_NAME_COMPLIANT_BUY_NAME:
                if buy_name == compliant_buy:
                    self._tutorial_compliance_check(tut, event_client_time)

            if buy_name == 'fertilizer':
                min_lake_dist = sqrt(min([(tx - x) ** 2 + (ty - y) ** 2 for x, y in self.lake_xys]))
                window_fname = "window_average_distance_between_poop_placement_and_lake"
                session_fname = "session_average_distance_between_poop_placement_and_lake"
                self.average_in_windows_and_session(window_fname, session_fname, min_lake_dist)

            if buy_name in LakelandExtractor._BUILDING_TYPES:
                self.building_xys.append((tx, ty))
                if len(self.building_xys) > 1:
                    avg_dist_from_buildings = \
                        sum(self.distance((tx, ty), pt2) for pt2 in self.building_xys) / (len(self.building_xys) - 1)
                    session_fname = "session_avg_avg_distance_between_buildings"
                    window_fname = "window_avg_avg_distance_between_buildings"
                    self.average_in_windows_and_session(window_fname, session_fname, avg_dist_from_buildings)

    def _tutorial_compliance_check(self, tut_name, event_client_time):
        tutorial_end_time = self._tutorial_start_and_end_times[tut_name][1]
        if not self._tutorial_compliance[tut_name] and tutorial_end_time:
            compliance_interval = event_client_time - tutorial_end_time
            fname = f"{tut_name}_compliance_interval"
            self.features.setValByName(feature_name=fname, new_value=compliance_interval)

    def _extractFromCancelbuy(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        selected_buy = d["selected_buy"]
        cost = d["cost"]
        curr_money = d["curr_money"]
        buy_hovers = d["buy_hovers"]
        client_time = d["client_time"]
        self._selected_buy_cost = 0

    def _extractFromRoadbuilds(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        road_builds = d["road_builds"]
        client_time = d["client_time"]

    def _extractFromTileuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        tile = d["tile"]
        marks = d["marks"]
        tile_array, marks = d["tile"], d["marks"]
        if self._tile_mark_change(tile_array, marks):
            self._increment_feature_in_cur_windows("window_num_change_tile_mark")
        total_farm_marks1 = [t["marks"][0] for t in self._tiles.values() if
                             t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_farm_marks2 = [t["marks"][1] for t in self._tiles.values() if
                             t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['farm']]
        total_dairy_marks1 = [t["marks"][0] for t in self._tiles.values() if
                              t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['livestock']]  # milk
        total_dairy_marks2 = [t["marks"][1] for t in self._tiles.values() if
                              t["type"] == LakelandExtractor._STR_TO_ENUM["TILE TYPE"]['livestock']]  # fertilizer

        for type, marks in [('food', total_farm_marks2 + total_farm_marks1), ('milk', total_dairy_marks1),
                            ('poop', total_dairy_marks2)]:
            mark_counts = {LakelandExtractor._ENUM_TO_STR["MARK"][k]: v for k, v in Counter(marks).items()}
            for use in mark_counts:
                max_per_capita_fname = f"window_max_num_per_capita_of_{type}_marked_{use}"
                min_per_capita_fname = f"window_min_num_per_capita_of_{type}_marked_{use}"
                total_fname = f"window_total_{type}_marked_{use}"
                use_percentage_fname = f"window_percent_of_{type}_marked_{use}"
                if self._num_farmbits:
                    self._set_feature_max_in_cur_windows(max_per_capita_fname, mark_counts[use] / self._num_farmbits)
                    self._set_feature_min_in_cur_windows(min_per_capita_fname, mark_counts[use] / self._num_farmbits)
                    self._set_feature_max_in_session(max_per_capita_fname.replace('window', 'session'),
                                                     mark_counts[use] / self._num_farmbits)
                    self._set_feature_min_in_session(min_per_capita_fname.replace('window', 'session'),
                                                     mark_counts[use] / self._num_farmbits)
                self._increment_feature_in_cur_windows(total_fname, mark_counts[use])
                self._set_value_in_cur_windows(use_percentage_fname, mark_counts[use] / len(marks))

    def _extractFromItemuseselect(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        item = d["item"]
        prev_mark = d["prev_mark"]
        item_array = d["item"]
        curr_mark = item_array[3]
        if d["prev_mark"] != curr_mark:
            self._increment_feature_in_cur_windows("window_num_change_item_mark")

    def _extractFromTogglenutrition(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        to_state = d["to_state"]
        tile_nutritions = d["tile_nutritions"]
        toggle_opened = d["to_state"]
        if not toggle_opened:
            self._nutrition_view_on = False
            self.increment_nutrition_view_secs(event_client_time)

        else:  # if nutriton opened
            self._nutrition_view_on = True
            self._last_nutrition_open = event_client_time

    def _extractFromToggleshop(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        shop_open = d["shop_open"]
        if d["shop_open"]:
            self._increment_feature_in_cur_windows("window_num_open_shop")

    def _extractFromToggleachievements(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        achievements_open = d["achievements_open"]
        if d["achievements_open"]:
            self._increment_feature_in_cur_windows("window_num_open_achievements")

    def _extractFromSkiptutorial(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        (none) = d["(none)"]
        self.features.incAggregateVal("session_count_of_skips")
        self._increment_feature_in_cur_windows("window_num_press_skip_button")

    def _extractFromSpeed(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        cur_speed = d["cur_speed"]
        prev_speed = d["prev_speed"]
        manual = d["manual"]
        self._cur_speed, prev_speed = d["cur_speed"], d["prev_speed"]
        if self._cur_speed != prev_speed:
            self.update_secs_at_speed(event_client_time, prev_speed)

    def _extractFromAchievement(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        achievement = d["achievement"]
        self.features.incAggregateVal("session_count_of_achievements")
        achievement_enum = d["achievement"]
        achievement_str = LakelandExtractor._ENUM_TO_STR["ACHIEVEMENTS"]
        time_since_start = (event_client_time - self._client_start_time).seconds
        fname = f"session_secs_to_{achievement_str}_achievement"
        self.features.setValByName(feature_name=fname, new_value=time_since_start)

    def _extractFromFarmbitdeath(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        farmbit = d["farmbit"]
        grave = d["grave"]
        self._change_population(event_client_time, -1)
        self.features.incAggregateVal("session_num_deaths")
        self._increment_feature_in_cur_windows("window_num_deaths")

    def _extractFromBlurb(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromClick(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromRainstopped(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed

    def _extractFromHistory(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        client_time = d["client_time"]
        camera_history = d["camera_history"]
        emote_history = d["emote_history"]
        emote_history = d["emote_history"]
        client_time = d["client_time"]
        self.process_history_array(emote_history, client_time)
        for e in emote_history:
            self._add_emote_to_window_by_time(e)

    def _extractFromEndgame(self, event_client_time, event_data_complex_parsed):
        d = event_data_complex_parsed
        (none) = d["(none)"]
        self.update_secs_at_speed(event_client_time, self._cur_speed)
        if self._nutrition_view_on:
            self.increment_nutrition_view_secs(event_client_time)

    # UTILS

    # Feature modulators

    def feature_average(self, fname_base, value):
        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        window_feature, session_feature = win_pref + fname_base, sess_pref + fname_base
        for w in self._cur_windows:
            self.average_handler_window[window_feature][w]['total'] += value
            self.average_handler_window[window_feature][w]['n'] += 1
            avg = self.average_handler_window[window_feature][w]['total'] / \
                  self.average_handler_window[window_feature][w]['n']
            self.features.setValByIndex(window_feature, w, avg)

        self.average_handler_session[session_feature]['total'] += value
        self.average_handler_session[session_feature]['n'] += 1
        avg = self.average_handler_session[session_feature]['total'] / self.average_handler_session[session_feature][
            'n']
        self.features.setValByName(session_feature, avg)

    def feature_inc(self, feature_base, increment=1):
        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._increment_feature_in_cur_windows(feature_name=win_pref + feature_base, increment=increment)
        self.features.incAggregateVal(feature_name=sess_pref + feature_base, increment=increment)

    def feature_max_min(self, fname_base, val):
        """feature must have the same fname_base that gets put on the following four features:
        - session_max_
        - session_min_
        - window_max_
        - window_min_ """

        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._set_feature_max_in_cur_windows(feature_name=win_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_cur_windows(feature_name=win_pref + "min_" + fname_base, val=val)
        self._set_feature_max_in_session(feature_name=sess_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_session(feature_name=sess_pref + "min_" + fname_base, val=val)

    def _increment_feature_in_cur_windows(self, feature_name, increment=None):
        increment = increment or 1
        for w in self._cur_windows:
            self.features.incValByIndex(feature_name=feature_name, index=w, increment=increment)

    def _set_value_in_cur_windows(self, feature_name, value):
        for w in self._cur_windows:
            self.features.setValByIndex(feature_name=feature_name, index=w, new_value=value)

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

    def _set_feature_max_in_session(self, feature_name, val):
        prev_val = self.features.getValByName(feature_name=feature_name)
        if val > prev_val:
            self.features.setValByName(feature_name=feature_name, new_value=val)

    def _set_feature_min_in_session(self, feature_name, val):
        prev_val = self.features.getValByName(feature_name=feature_name)
        if val < prev_val:
            self.features.setValByName(feature_name=feature_name, new_value=val)

    # Signle Functions

    def update_secs_at_speed(self, event_client_time, prev_speed):
        secs_at_prev_speed = (event_client_time - self._last_speed_change).seconds
        self._last_speed_change = event_client_time
        prev_speed_str = LakelandExtractor._ENUM_TO_STR["SPEED"][prev_speed]
        self._time_per_speed[prev_speed_str] += secs_at_prev_speed
        window_fname = f"window_secs_in_game_speed_{prev_speed_str}"
        session_fname = f"session_secs_in_game_speed_{prev_speed_str}"
        self.features.incAggregateVal(session_fname, secs_at_prev_speed)
        self._increment_feature_in_cur_windows(window_fname, secs_at_prev_speed)

    def increment_nutrition_view_secs(self, event_client_time):
        secs_in_nutrtion_view = (event_client_time - self._last_nutrition_open).seconds
        window_fname = "window_secs_in_nutrition_view"
        session_fname = "session_secs_in_nutrition_view"
        self._increment_feature_in_cur_windows(window_fname, secs_in_nutrtion_view)
        self.features.incAggregateVal(session_fname, secs_in_nutrtion_view)

    def _tile_mark_change(self, tile_array, marks):
        tx, ty = tile_array[4], tile_array[5]
        type = tile_array[3]
        self._tiles[(tx, ty)]['type'] = type
        if marks == self._tiles[(tx, ty)]['marks']:
            return False
        else:
            self._tiles[(tx, ty)]['marks'] = marks
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
        return sum(all_deltas) / len(all_deltas)

    def _avg_lake_nutrition(self, all_nutritions):
        lake_nutritions = []
        for og_type, nutrition in zip(self._tile_og_types, all_nutritions):
            if LakelandExtractor._ENUM_TO_STR["TILE TYPE"][og_type] == "lake":
                lake_nutritions.append(nutrition)
        return sum(lake_nutritions) / len(lake_nutritions)

    def _set_default_window_val(self, feature_name, val):
        for w in self.window_range:
            self.features.features[feature_name][w]['val'] = val

    def _set_default_session_val(self, feature_name, val):
        for w in self.window_range:
            self.features.features[feature_name] = val

    def _change_population(self, client_time, increment):
        self._num_farmbits += increment;
        self._population_history.append((client_time, self._population_history[-1][1] + increment))

    def _get_pops_at_times(self, time_list):
        # takes in a sorted list of times and returns the population of farmbits at those times
        ret = []
        pop_cur = 0
        for t in time_list:
            while (not pop_cur + 1 >= len(self._population_history)) and self._population_history[pop_cur + 1][0] < t:
                pop_cur += 1
            ret.append(self._population_history[pop_cur][1])
        return ret

    def _get_windows_at_time(self, client_time):
        seconds_since_start = (client_time - self._client_start_time).seconds
        windows = [seconds_since_start // self._NUM_SECONDS_PER_WINDOW,
                   (seconds_since_start - self._NUM_SECONDS_PER_WINDOW_OVERLAP) // self._NUM_SECONDS_PER_WINDOW]

        # remove negative or duplicate windows
        if windows[1] < 0:
            windows[1] = 0
        if windows[0] == windows[1]:
            windows = [windows[0]]

        return windows

    def _add_emote_to_window_by_time(self, emote):
        event_time = emote[-1]
        windows = self._get_windows_at_time(event_time)
        for window in windows:
            self._emotes_by_window[window].append(emote)

    def calculateAggregateFeatures(self):
        self.calculate_emotes()
        # --------

    def calculate_emotes(self):
        for window, emotes in self._emotes_by_window.items():
            total_emotes = len(emotes)
            emote_type_index, emote_time_index = -2, -1
            emote_type_enums = [e[emote_type_index] for e in emotes]
            emote_times = [e[emote_time_index] for e in emotes]
            emote_pops = self._get_pops_at_times(emote_times)

            # initialize
            total_emotes_per_capita = {k: 0 for k in LakelandExtractor._STR_TO_ENUM['EMOTES'].keys()}
            # emotes_per_capita_per_second = {k:0 for k in LakelandExtractor._STR_TO_ENUM['EMOTES'].keys()}

            total_pos_emotes = 0
            total_neg_emotes = 0
            total_neutral_emotes = 0
            # fill
            for enum, pop in zip(emote_type_enums, emote_pops):
                # TODO: there are instances where pop is 0, and I don't know why
                if pop == 0:
                    pop = 1
                emote_str = LakelandExtractor._ENUM_TO_STR['EMOTES'][enum]
                total_emotes_per_capita[emote_str] += 1 / pop
                if LakelandExtractor._EMOTE_STR_TO_AFFECT[emote_str] == -1:
                    total_neg_emotes += 1
                elif LakelandExtractor._EMOTE_STR_TO_AFFECT[emote_str] == 0:
                    total_neutral_emotes += 1
                elif LakelandExtractor._EMOTE_STR_TO_AFFECT[emote_str] == 1:
                    total_pos_emotes += 1

            for emote_str, per_capita_value in total_emotes_per_capita.items():
                if emote_str == 'null':
                    continue
                fname_total = f'window_num_of_{emote_str}_emotes_per_capita'
                self.features.setValByIndex(fname_total, window, per_capita_value)

            self.features.setValByIndex("window_percent_positive_emotes", window, total_pos_emotes / total_emotes)
            self.features.setValByIndex("window_percent_negative_emotes", window, total_neg_emotes / total_emotes)
            self.features.setValByIndex("window_percent_neutral_emotes", window, total_neutral_emotes / total_emotes)
            self.features.incAggregateVal("session_percent_positive_emotes", total_pos_emotes)
            self.features.incAggregateVal("session_percent_negative_emotes", total_neg_emotes)
            self.features.incAggregateVal("session_percent_neutral_emotes", total_neutral_emotes)

            # for i, (enum, pop) in enumerate(zip(emote_type_enums, emote_pops)):
            #     if i < 20:
            #         emotes
            #         emotes_per_capita_per_second_max[LakelandExtractor._ENUM_TO_STR['EMOTES'][enum]] += 1/pop
            # fname_per_second_min = f'window_min_num_of_{emote_str}__emotes_per_capita_per_second'
            # fname_per_second_max = f'window_max_num_of_{emote_str}__emotes_per_capita_per_second'

            # assign

    def milliseconds_to_datetime(self, milliseconds):
        # round #milliseconds to #secs because event_client_time resolves to seconds not msecs
        ret = datetime.datetime.utcfromtimestamp(milliseconds // 1000)
        assert ret >= self._client_start_time
        return ret

    def process_history_array(self, array, client_time):
        if not array:
            return
        if type(array[0]) == int:
            for i in range(len(array)):
                array[i] = self.milliseconds_to_datetime(array[i] + client_time)
        else:
            for i in range(len(array)):
                array[i][-1] = self.milliseconds_to_datetime(array[i][-1] + client_time)

    def get_tile_types_xys(self, type_list):
        return [LakelandExtractor.index_to_xy(i) for i, type in enumerate(self._tile_og_types) if
                LakelandExtractor._ENUM_TO_STR['TILE TYPE'][type] in type_list]  # 5 is the lake type enum

    @staticmethod
    def get_feature(base, enum, enum_type):
        return base + LakelandExtractor._ENUM_TO_STR[enum_type][enum]

    @staticmethod
    def str_to_int(str):
        return int(str.strip())

    @staticmethod
    def list_deltas(l):
        return [l[i] - l[i - 1] for i in range(1, len(l))]

    @staticmethod
    def onscreen_item_dict():
        ret = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['ITEM TYPE']}
        ret.update({key: 0 for key in LakelandExtractor._STR_TO_ENUM['BUYS']})
        del ret['null']
        return ret

    @staticmethod
    def array_to_mat(num_columns, arr):
        assert len(arr) % num_columns == 0
        return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]

    @staticmethod
    def get_timezone(utc_time, local_time):
        tdelta = local_time - utc_time
        offset = datetime.timedelta(days=tdelta.days, hours=tdelta.seconds // 3500)
        ## return tzinfo(offset)
        return offset

    @staticmethod
    def index_to_xy(index):
        x = index % 50
        y = index // 50
        return (x, y)

    @staticmethod
    def distance(point1, point2):
        """

        :param point1: x,y for point 1
        :param point2: x,y for point 2
        :return: euclidean distance between x and y
        """
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    @staticmethod
    def read_stringified_array(arr):
        if not arr:
            return []
        return [int(x) for x in arr.split(',')]

    @staticmethod
    def _get_sess_window_fname(fname_base):
        return (LakelandExtractor._SESS_PREFIX + fname_base, LakelandExtractor._WINDOW_PREFIX + fname_base)


class tzinfo(datetime.tzinfo):
    def __init__(self, tdelta):
        self._offset = tdelta
        self._dst = datetime.timedelta(0)
        self._name = "+local"

    def utcoffset(self, dt):
        return self._offset

    def dst(self, dt):
        return self._dst

    def tzname(self, dt):
        return self._name

