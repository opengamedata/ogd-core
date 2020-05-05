""" Lakeland Feature Extractor
Note that a separate file unique to the lakeland extractor is necessary to run this script.
The file is Lakeland Enumerators.json, and is required for the line:
_STR_TO_ENUM = utils.loadJSONFile("game_info/Lakeland/Lakeland Enumerators.json")

This json file is created from the fielddaylab/lakeland README on github via
"produce_lakeland_enumerators.py". Please run that script with the appropriate inpath and outpath before running this
script.
"""



## import standard libraries
import datetime
import logging
import sys
import traceback

## import local files
import typing
import utils
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema
from collections import defaultdict, Counter
from math import sqrt
from copy import deepcopy


## @class LakelandExtractor
#  Extractor subclass for extracting features from Lakeland game data.
class LakelandExtractor(Extractor):
    _SESS_PREFIX = 'sess_'
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
    _STR_TO_ENUM = utils.loadJSONFile("game_info/Lakeland/Lakeland Enumerators.json")
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

    _ACTIVE_LOGS = ["SELECTTILE", "SELECTFARMBIT", "SELECTITEM", "SELECTBUY", "BUY",
                    "CANCELBUY","TILEUSESELECT","ITEMUSESELECT"]

    _NULL_FEATURE_VALS = ['null', 0, None]


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
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema, proc_file: typing.IO.writable):
        # Set window and overlap size
        config = game_schema.schema()['config']
        WINPREF, SESSPREF = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._NUM_SECONDS_PER_WINDOW = config[LakelandExtractor._WINDOW_PREFIX+'WINDOW_SIZE_SECONDS']
        self._NUM_SECONDS_PER_WINDOW_OVERLAP = config["WINDOW_OVERLAP_SECONDS"]
        self._GAME_SCHEMA = game_schema
        # TODO: Ask John whether this is needed - the point of extractors is they aren't responsible for knowing when to write data.
        if proc_file:
            self._WRITE_FEATURES = lambda: self.writeCurrentFeatures(file=proc_file)
        else:
            self._WRITE_FEATURES = lambda: print("Dumping feature data, no writable file was given!")
        self.WINDOW_RANGE = range(game_table.max_level + 1)
        self._cur_gameplay = 1
        self._startgame_count = 0
        self.debug_strs = []


        # set window range
        # Initialize superclass
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        
        self.reset()
        self.setValByName('num_play', self._cur_gameplay)
    
    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        try:
            self._extractFromRow(row_with_complex_parsed, game_table)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for place in [utils.Logger.toFile, utils.Logger.toStdOut]:
                place('\n'.join(self.debug_strs), logging.ERROR)
                place('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)), logging.ERROR)
                # if len(self.debug_strs) > 10:
                    # self.debug_strs = self.debug_strs[:5] + ['...'] + self.debug_strs[-5:]
            if True:
                pass


    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    def _extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        if self._halt:
            return

        # put some data in local vars, for readability later.
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_type = row_with_complex_parsed[game_table.event_custom_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index].replace(microsecond=
                                                    row_with_complex_parsed[game_table.client_time_ms_index]*1000)
        server_time = row_with_complex_parsed[game_table.server_time_index]
        event_type_str = LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_type].upper()
        if self._end and event_type_str in ['STARTGAME', 'NEWFARMBIT']:
            self._WRITE_FEATURES()
            self.reset()
            self._cur_gameplay += 1
            self.setValByName('num_play', self._cur_gameplay)
        if not self._VERSION:
            self._VERSION = row_with_complex_parsed[game_table.version_index]
            self.setValByName("version", self._VERSION)
        # Check for invalid row.
        row_sess_id = row_with_complex_parsed[game_table.session_id_index]
        if row_sess_id != self.session_id:
            utils.Logger.toFile(f"Got a row with incorrect session id! Expected {self.session_id}, got {row_sess_id}!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.getValByName(feature_name="persistentSessionID") == 0:
                self.setValByName(feature_name="persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # if self.getValByName(feature_name="player_id") == 0:
            #     self.setValByName(feature_name="player_id",
            #                                new_value=row_with_complex_parsed[game_table.player_id_index])

            # if this is the first row
            if not self._CLIENT_START_TIME:
                # initialize this time as the start
                self._CLIENT_START_TIME = event_client_time
                self._last_speed_change = self._CLIENT_START_TIME
                self._last_active_log_time = event_client_time
                self.add_debug_str(f'{"*"*10}\nPlay {self._cur_gameplay} \n'+
                                      f'{self.session_id} v{self._VERSION} @ {self._CLIENT_START_TIME}')
                self.setValByName("play_year", self._CLIENT_START_TIME.year)
                self.setValByName("play_month",self._CLIENT_START_TIME.month)
                self.setValByName("play_day", self._CLIENT_START_TIME.day)
                self.setValByName("play_hour", self._CLIENT_START_TIME.hour)
                self.setValByName("play_minute", self._CLIENT_START_TIME.minute)
                self.setValByName("play_second", self._CLIENT_START_TIME.second)
            # set current windows
            self._cur_windows = self._get_windows_at_time(event_client_time)
            if any([w > game_table.max_level for w in self._cur_windows]):
                self._halt = True
                return

            # Record that an event of any kind occurred, for the window & session
            time_since_start = self.time_since_start(event_client_time)
            if event_type_str in LakelandExtractor._ACTIVE_LOGS:
                self.feature_count(feature_base="ActiveEventCount")
            self.feature_count(feature_base="EventCount")
            self.setValByName(feature_name="sessDuration", new_value=time_since_start)
            if event_type_str == "BUY" and event_data_complex_parsed["success"]:
                debug_str = LakelandExtractor._ENUM_TO_STR['BUYS'][event_data_complex_parsed["buy"]].upper()
            if event_type_str == 'STARTGAME':
                debug_str = "START" if event_data_complex_parsed.get("continue") == False else "CONTINUE"
                debug_str += f' Language: {event_data_complex_parsed.get("language")}'
            else:
                debug_str = ''
            self.add_debug_str(f'{self._num_farmbits } {time_since_start} {event_type_str} {debug_str}')

            # Then, handle cases for each type of event
            if event_type_str == "GAMESTATE":
                self._extractFromGamestate(event_client_time, event_data_complex_parsed)
            elif event_type_str == "STARTGAME":
                self._extractFromStartgame(event_client_time, event_data_complex_parsed)
            elif event_type_str == "CHECKPOINT":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SELECTTILE":
                self._extractFromSelecttile(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SELECTFARMBIT":
                self._extractFromSelectfarmbit(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SELECTITEM":
                self._extractFromSelectitem(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SELECTBUY":
                self._extractFromSelectbuy(event_client_time, event_data_complex_parsed)
            elif event_type_str == "BUY":
                self._extractFromBuy(event_client_time, event_data_complex_parsed)
            elif event_type_str == "CANCELBUY":
                self._extractFromCancelbuy(event_client_time, event_data_complex_parsed)
            elif event_type_str == "ROADBUILDS":
                self._extractFromRoadbuilds(event_client_time, event_data_complex_parsed)
            elif event_type_str == "TILEUSESELECT":
                self._extractFromTileuseselect(event_client_time, event_data_complex_parsed)
            elif event_type_str == "ITEMUSESELECT":
                self._extractFromItemuseselect(event_client_time, event_data_complex_parsed)
            elif event_type_str == "TOGGLENUTRITION":
                self._extractFromTogglenutrition(event_client_time, event_data_complex_parsed)
            elif event_type_str == "TOGGLESHOP":
                self._extractFromToggleshop(event_client_time, event_data_complex_parsed)
            elif event_type_str == "TOGGLEACHIEVEMENTS":
                self._extractFromToggleachievements(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SKIPTUTORIAL":
                self._extractFromSkiptutorial(event_client_time, event_data_complex_parsed)
            elif event_type_str == "SPEED":
                self._extractFromSpeed(event_client_time, event_data_complex_parsed)
            elif event_type_str == "ACHIEVEMENT":
                self._extractFromAchievement(event_client_time, event_data_complex_parsed)
            elif event_type_str == "FARMBITDEATH":
                self._extractFromFarmbitdeath(event_client_time, event_data_complex_parsed)
            elif event_type_str == "BLURB":
                self._extractFromBlurb(event_client_time, event_data_complex_parsed)
            elif event_type_str == "CLICK":
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif event_type_str == "RAINSTOPPED":
                self._extractFromRainstopped(event_client_time, event_data_complex_parsed)
            elif event_type_str == "HISTORY":
                self._extractFromHistory(event_client_time, event_data_complex_parsed)
            elif event_type_str == "ENDGAME":
                self._extractFromEndgame(event_client_time, event_data_complex_parsed)
            elif event_type_str == "EMOTE":
                self._extractFromEmote(event_client_time, event_data_complex_parsed)
            elif event_type_str == "FARMFAIL":
                self._extractFromFarmfail(event_client_time, event_data_complex_parsed)
            elif event_type_str == "BLOOM":
                self._extractFromBloom(event_client_time, event_data_complex_parsed)
            elif event_type_str == "FARMHARVESTED":
                self._extractFromFarmharvested(event_client_time, event_data_complex_parsed)
            elif event_type_str == "MILKPRODUCED":
                self._extractFromMilkproduced(event_client_time, event_data_complex_parsed)
            elif event_type_str == "POOPPRODUCED":
                self._extractFromPoopproduced(event_client_time, event_data_complex_parsed)
            elif event_type_str == "DEBUG":
                self._extractFromDebug(event_client_time, event_data_complex_parsed)
            elif event_type_str == "NEWFARMBIT":
                self._extractFromNewfarmbit(event_client_time, event_data_complex_parsed)
            else:
                raise Exception("Found an unrecognized event type: {}".format(event_type))


    def _extractFromGamestate(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables 
        d = event_data_complex_parsed
        _tiles = d["tiles"]
        _farmbits = d["farmbits"]
        _items = d["items"]
        _money = d["money"]
        _speed = d["speed"]
        _achievements = d["achievements"]
        _num_checkpoints_completed = d["num_checkpoints_completed"]
        _raining = d["raining"]
        _curr_selection_type = d["curr_selection_type"]
        _curr_selection_data = d.get("curr_selection_data")
        _camera_center = d["camera_center"]
        _gametime = d["gametime"]
        _timestamp = d["timestamp"]
        _num_food_produced = d["num_food_produced"]
        _num_milk_produced = d["num_milk_produced"]
        _num_poop_produced = d["num_poop_produced"]

        # reformat raw variable functions
        def array_to_mat(num_columns, arr):
            assert len(arr) % num_columns == 0
            return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]
        def read_stringified_array(arr):
            if not arr:
                return []
            return [int(x) for x in arr.split(',')]

        # reformat array variables
        _tiles = read_stringified_array(_tiles)
        _farmbits = read_stringified_array(_farmbits)
        _items = read_stringified_array(_items)
        _tiles = array_to_mat(4, _tiles)
        _farmbits = array_to_mat(9, _farmbits)
        _items = array_to_mat(4, _items)

        # set class variables
        # TODO: If continue, initalize variables
        if self._first_gamestate and self._continue:
            for i,t in enumerate(_tiles):
                type = t[3]
                if LakelandExtractor._ENUM_TO_STR['TILE TYPE'][type] in LakelandExtractor._BUILDING_TYPES:
                    self.building_xys.append(tile_i_to_xy(i))
                if type in [9,10]: #farm or livestock
                    self._tiles[tile_i_to_xy(i)]['type'] = type

        if self._num_farmbits != len(_farmbits):
            # if the num farmbits arent as expected or just one more than expected (sometimes takes a while to show), show warning.
            self.log_warning(f'Gamestate showed {len(_farmbits)} but expected {self._num_farmbits} farmbits.')
             # self._change_population(event_client_time, len(_farmbits) - self._num_farmbits)

        self._first_gamestate = False

        #  feature functions
        # def farms_low_productivity(tiles):
        #     return [t for t in tiles if t[3] == 9 and t[1] < 3]  # type == farm and nutrition < 3 (the circle is heavily black)

        0# def lake_tiles_bloom(tiles):
        #     return [t for t in tiles if t[3] == 5 and t[1] > 25]  # lake tiles bloom when nutrition > 10% of 255,
        # so technically not all tiles > 25 nutrition are blooming, but we will put the cutoff here

        def avg_lake_nutrition(tiles):
            lake_nutritions = [t[1] for t in tiles if t[2] == 5] # 5 is the lake enum for tile type
            if len(lake_nutritions) == 0:
                self.log_warning(f'No lake nutritions!!')

            return sum(lake_nutritions) / len(lake_nutritions)

        def num_items_in_play(items, tiles):
            cur_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
            for it in items:
                type = it[2]
                key = LakelandExtractor._ENUM_TO_STR["ITEM TYPE"][type]
                cur_num_items_on_screen[key] += 1
            for t in tiles:
                type = t[3]
                key = LakelandExtractor._ENUM_TO_STR["TILE TYPE"][type]
                if key in cur_num_items_on_screen:
                    cur_num_items_on_screen[key] += 1
            return cur_num_items_on_screen

        # set features
        self.feature_count('count_gamestate_logs')

        for (key, cur_num) in num_items_in_play(_items, _tiles).items():
            self.feature_max_min(f'num_{key}_in_play', cur_num)
        self.feature_max_min(fname_base="avg_lake_nutrition", val=avg_lake_nutrition(_tiles))
        # self.feature_max_min("num_farms_low_productivity", len(farms_low_productivity(_tiles)))
        # self.feature_max_min("num_lake_tiles_in_bloom", len(lake_tiles_bloom(_tiles)))

    def _extractFromStartgame(self, event_client_time, event_data_complex_parsed):
        self._startgame_count += 1
        if self._startgame_count > 1:
            self.add_debug_str(f"Starting game {self._startgame_count}.")
        if self._startgame_count != self._cur_gameplay:
            self.log_warning(f"Starting game {self._cur_gameplay} but this is the {self._startgame_count}th start!")

        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile_states = d["tile_states"]
        _tile_nutritions = d["tile_nutritions"]
        _continue = d["continue"]
        _language = d["language"]
        _audio = d["audio"]
        _fullscreen = d["fullscreen"]

        # set class variables
        self._TILE_OG_TYPES = _tile_states
        self._continue = _continue

        # feature functions

        # set features
        self.setValByName("continue", _continue)
        self.setValByName("language", _language)
        self.setValByName("audio", _audio)
        self.setValByName("fullscreen", _fullscreen)


    def _extractFromCheckpoint(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _event_category = d["event_category"] # start or end
        _event_label = d["event_label"] # tutorial name
        _event_type = d["event_type"]
        _blurb_history = d["blurb_history"]
        _client_time = d["client_time"]


        # reformat variables
        _blurb_history = self.reformat_history_array(_blurb_history, _client_time)

        # helpers
        assert _event_type == 'tutorial'
        is_tutorial_end = 1 if _event_category == 'end' else 0
        is_tutorial_start = not is_tutorial_end
        time_since_start = self.time_since_start(event_client_time)
        if is_tutorial_end:
            assert _blurb_history is not None

        # set class variables
        # self._tutorial_start_and_end_times[_event_label][is_tutorial_end] = event_client_time
        if is_tutorial_end:
            self._tutorial_times_per_blurb[_event_label] = list_deltas(_blurb_history)

        # feature functions
        def avg_time_per_blurb(tut_name):
            time_per_blurb = self._tutorial_times_per_blurb.get(tut_name)
            assert time_per_blurb
            return avg(time_per_blurb)

        # set features
        if is_tutorial_start:
            self.feature_time_since_start(feature_base=f"time_to_{_event_label}_tutorial",
                                          cur_client_time=event_client_time)
            self.feature_inc(feature_base='count_encounter_tutorial', increment=is_tutorial_start)
        # TODO: Case where blurb history exists but player skipped
        if is_tutorial_end and len(_blurb_history) > 1:
            self.setValByName(
                feature_name=f"{LakelandExtractor._SESS_PREFIX}avg_time_per_blurb_in_{_event_label}_tutorial",
                new_value=avg_time_per_blurb(_event_label))


    def _extractFromSelecttile(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # set features
        self.feature_count("count_inspect_tile")

    def _extractFromSelectfarmbit(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _farmbit = d["farmbit"]

    def _extractFromSelectitem(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _item = d["item"]


    def _extractFromSelectbuy(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _buy = d["buy"]
        _cost = d["cost"]
        _cur_money = d["curr_money"]
        _success = d["success"]

        # set class variables
        self._selected_buy_cost = _cost
        self._cur_money = _cur_money

    def _extractFromBuy(self, event_client_time, event_data_complex_parsed):

        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _buy = d["buy"]
        _tile = d["tile"]
        _success = d["success"]
        _buy_hovers = d["buy_hovers"]
        _client_time = d["client_time"]

        if not _success:
            return

        # helpers
        buy_name = LakelandExtractor._ENUM_TO_STR['BUYS'][_buy]
        time_since_start = self.time_since_start(event_client_time)

        # set class variables
        if buy_name in LakelandExtractor._BUILDING_TYPES:
            self.building_xys.append(get_tile_txy(_tile))

        if buy_name in ['farm', 'livestock']:
            tile_type = LakelandExtractor._STR_TO_ENUM['TILE TYPE'][buy_name]
            self._tiles[get_tile_txy(_tile)]['type'] = buy_name

        # feature functions
        def chose_highest_nutrient_tile(buy_hovers, chosen_tile):
            building_buildable_func = self.get_building_buildable_function() if self._VERSION < 15 \
                else lambda buy_t: buy_t[-2] # whether the tile is buildable (v15 buy hover data contains:
                                             # [tile_data_short, buildable, hover_time]
            for t in buy_hovers:
                # t has the current type of land (only type that farms can be built on) and a building (farm) can be placed there
                if t[3] == 1 and building_buildable_func(t):
                    if t[1] - 2 > chosen_tile[1]:  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
                       return 0  # failed to put on highest nutrition tile
            return 1

        def chose_lowest_nutrient_farm(buy_hovers, chosen_tile):
            for t in buy_hovers:
                if t[3] == 9:  # t has the current type of farm (only type that fertilizer can be built on)
                    if t[1] - 2 < chosen_tile[1]:  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
                        return 0  # failed to put on lowest nutrition tile
            return 1

        def dist_to_lake(tile):
            tile_pt = (tile[4], tile[5])
            lake_xys = self.get_tile_types_xys(['lake'])
            if not lake_xys:
                self.log_warning('There were no lake tiles found!')
                return None
            min_lake_dist = sqrt(min([distance(tile_pt, lake_pt) for lake_pt in lake_xys]))
            return min_lake_dist

        def avg_distance_between_buildings():
            if len(self.building_xys) < 2:
                return 0
            distances = [distance(pt1, pt2) for pt1 in self.building_xys for pt2 in self.building_xys if pt1 != pt2]
            return sum(distances)/len(distances)

        # set features
        self.feature_inc(feature_base="money_spent", increment=self._selected_buy_cost)
        self.feature_inc(feature_base=f"money_spent_{buy_name}", increment=self._selected_buy_cost)
        self.feature_count(feature_base=f'count_buy_{buy_name}')
        self.feature_time_since_start(feature_base=f'time_to_first_{buy_name}', cur_client_time=event_client_time)
        self.feature_average(fname_base=f'avg_num_tiles_hovered_before_placing_{buy_name}', value=len(_buy_hovers))
        if buy_name == 'farm':
            self.feature_average(fname_base='percent_building_a_farm_on_highest_nutrition_tile',
                             value=chose_highest_nutrient_tile(_buy_hovers, _tile))
        if buy_name == 'fertilizer':
            self.feature_average(fname_base="percent_placing_fertilizer_on_lowest_nutrient_farm",
                                 value=chose_lowest_nutrient_farm(_buy_hovers, _tile))
            dist = dist_to_lake(_tile)
            if dist:
                self.feature_average("avg_distance_between_poop_placement_and_lake", dist)
        if buy_name in LakelandExtractor._BUILDING_TYPES:
            self.feature_average(fname_base='avg_avg_distance_between_buildings', value=avg_distance_between_buildings())

        self._add_event(_buy)



    # def _tutorial_compliance_check(self, tut_name, event_client_time):
    #     tutorial_end_time = self._tutorial_start_and_end_times[tut_name][1]
    #     if not self._tutorial_compliance[tut_name] and tutorial_end_time:
    #         compliance_interval = event_client_time - tutorial_end_time
    #         fname = f"{tut_name}_compliance_interval"
    #         self.setValByName(feature_name=fname, new_value=compliance_interval)

    def _extractFromCancelbuy(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _selected_buy = d["selected_buy"]
        _cost = d["cost"]
        _buy_hovers = d["buy_hovers"]
        _client_time = d["client_time"]

        # set class variables
        self._selected_buy_cost = 0

    def _extractFromRoadbuilds(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _road_builds = d["road_builds"]
        _client_time = d["client_time"]

    def _extractFromTileuseselect(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        mark_change = self._tiles[(get_tile_txy(_tile))]['marks'] != _marks
        if not mark_change:
            return
        self._tiles[(get_tile_txy(_tile))]['marks'] = _marks
        all_farm_marks = [t["marks"] for t in self._tiles.values() if t["type"] == 9] # 9 == farm
        all_dairy_marks = [t["marks"] for t in self._tiles.values() if t["type"] == 10] # 10 == livestock
        food_uses = [t[0] for t in all_farm_marks] + [t[1] for t in all_farm_marks] # mark index=0,1 food mark
        milk_uses = [t[0] for t in all_dairy_marks] # mark index=0 is the dairy mark
        poop_uses = [t[1] for t in all_dairy_marks] # mark index=1 is the poop mark

        # set class variables
        # self._tiles[get_tile_txy(_tile)]['type'] = _tile[3] # tile index 3 is type

        # feature setters

        self.feature_count(feature_base="count_change_tile_mark")
        for produced, produced_uses in [('food', food_uses), ('milk', milk_uses), ('poop', poop_uses)]:
            mark_counts = {LakelandExtractor._ENUM_TO_STR["MARK"][k]: v for k, v in Counter(produced_uses).items()}
            # for each produced item (food, milk, poop), we now have mark counts
            # {eat: ?, use: ?, sell: ?} of total numbers marked eat, use, sell.
            for use, count in mark_counts.items():
                self.feature_max_min(f"num_{produced}_marked_{use}", count) #mark use = eat in case of food
                self.feature_max_min(f"num_per_capita_{produced}_marked_{use}", count / (self._num_farmbits or 1))
                self.feature_max_min(f"percent_{produced}_marked_{use}", count/len(produced_uses))

    def _extractFromItemuseselect(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _item = d["item"]
        _prev_mark = d["prev_mark"]

        # feature setters
        if d["prev_mark"] != _item[3]: # if the mark has changed
            self.feature_count(feature_base="count_change_item_mark")

    def _extractFromTogglenutrition(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _to_state = d["to_state"]
        _tile_nutritions = d["tile_nutritions"]

        # set class variables
        self._nutrition_view_on = _to_state # (on is state==1)
        if self._nutrition_view_on:
            self._last_nutrition_open = event_client_time

        # set features
        self.set_time_in_nutrition_view(event_client_time)


    def _extractFromToggleshop(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _shop_open = d["shop_open"]

        # set features
        if _shop_open:
            self.feature_count("count_open_shop")

    def _extractFromToggleachievements(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _achievements_open = d["achievements_open"]

        # set features
        if _achievements_open:
            self.feature_count("count_open_achievements")

    def _extractFromSkiptutorial(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed

        # set features
        self.feature_count("count_skips")

    def _extractFromSpeed(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _cur_speed = d["cur_speed"]
        _prev_speed = d["prev_speed"]
        _manual = d["manual"]

        # set class variables
        self._cur_speed = _cur_speed

        # set features (this feature is modified by 2+ events)
        if self._cur_speed != _prev_speed:
            self.update_time_at_speed(event_client_time, _prev_speed)

    def _extractFromAchievement(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _achievement = d["achievement"]

        # helpers
        achievement_str = LakelandExtractor._ENUM_TO_STR["ACHIEVEMENTS"][_achievement]

        # set features
        self.feature_count("count_achievements")
        self.feature_time_since_start(f"time_to_{achievement_str}_achievement", event_client_time)


    def _extractFromFarmbitdeath(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _farmbit = d["farmbit"]
        _grave = d["grave"]

        # set session variables
        self._change_population(event_client_time, -1)

        # set features
        self.feature_count("count_deaths")
        self._add_event("D")

    def _extractFromBlurb(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed

    def _extractFromClick(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed

    def _extractFromRainstopped(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed

    def _extractFromHistory(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _client_time = d["client_time"]
        _camera_history = d["camera_history"]
        _emote_history = d["emote_history"]

        # reformat variables
        # _emote_history = self.reformat_history_array(_emote_history, _client_time)

        # set global variables
        # for e in _emote_history:
        #     self._add_emote_to_window_by_time(e)

    def _extractFromEndgame(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables 
        d = event_data_complex_parsed
        # (none) = d["(none)"]
        self.update_time_at_speed(event_client_time, self._cur_speed)
        if self._nutrition_view_on:
            self.set_time_in_nutrition_view(event_client_time)

        self._end = True



    def _extractFromEmote(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _farmbit = d["farmbit"]
        _emote_enum = d["emote_enum"]

        # fix bug in v13 logging where emote 2s show up as emote 0s
        if self._VERSION == 13 and _emote_enum == 0:
            _emote_enum = 2

        # helpers
        emote_str = LakelandExtractor._ENUM_TO_STR['EMOTES'][_emote_enum]
        affect = LakelandExtractor._EMOTE_STR_TO_AFFECT[emote_str]
        is_positive = affect == 1
        is_neutral = affect == 0
        is_negative = affect == -1
        if(self._num_farmbits) < 1:
            utils.Logger.toFile(f"Num farmbits < 1 @ {self._num_farmbits}!! Setting to 1.", logging.WARN)
            self.log_warning(f"Num farmbits < 1 @ {self._num_farmbits}!! Setting to 1.")
            self._num_farmbits = 1

        per_capita_val = 1/self._num_farmbits

        # set features
        self.feature_inc(f"count_{emote_str}_emotes_per_capita", per_capita_val)
        if emote_str == 'sale_txt':
            self.feature_inc("money_earned", 100)

        self.feature_average("percent_negative_emotes", is_negative)
        self.feature_average("percent_neutral_emotes", is_neutral)
        self.feature_average("percent_positive_emotes", is_positive)

        self.feature_inc("total_negative_emotes", is_negative)
        self.feature_inc("total_neutral_emotes", is_neutral)
        self.feature_inc("total_positive_emotes", is_positive)


    def _extractFromFarmfail(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers

        # set class variables

        # set features
        self.feature_count("count_farmfails")

    def _extractFromBloom(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_count("count_blooms")
        self._add_event("B")

    def _extractFromFarmharvested(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_food_produced", 2)

    def _extractFromMilkproduced(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_milk_produced", 1)

    def _extractFromPoopproduced(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_poop_produced", 1)

    def _extractFromDebug(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        self.add_debug_str('Set debug')

        # helpers
        self._debug = True
        # set class variables
        # set features
        self.setValByName(feature_name='debug', new_value=1)

    def _extractFromNewfarmbit(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _farmbit = d["farmbit"]

        # helpers
        # set class variables
        self._change_population(client_time=event_client_time, increment=1)
        # set features

    def calculateAggregateFeatures(self):
        pass

    def set_time_in_nutrition_view(self, event_client_time):
        if not self._nutrition_view_on:
            self.feature_inc("time_in_nutrition_view", event_client_time - self._last_nutrition_open)

    def update_time_at_speed(self, event_client_time, prev_speed):
        # helpers
        prev_speed_str = LakelandExtractor._ENUM_TO_STR["SPEED"][prev_speed]
        time_at_prev_speed = event_client_time - self._last_speed_change
        
        # set class variables
        self._last_speed_change = event_client_time
        
        # set features
        self.feature_inc(f'time_in_game_speed_{prev_speed_str}', time_at_prev_speed)


    # Feature Type Setters 
    def feature_average(self, fname_base, value):
        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        window_feature, session_feature = win_pref + fname_base, sess_pref + fname_base
        for w in self._cur_windows:
            self.average_handler_window[window_feature][w]['total'] += value
            self.average_handler_window[window_feature][w]['n'] += 1
            avg = self.average_handler_window[window_feature][w]['total'] / \
                  self.average_handler_window[window_feature][w]['n']
            self.setValByIndex(window_feature, w, avg)

        self.average_handler_session[session_feature]['total'] += value
        self.average_handler_session[session_feature]['n'] += 1
        avg = self.average_handler_session[session_feature]['total'] / self.average_handler_session[session_feature][
            'n']
        self.setValByName(session_feature, avg)

    def feature_count(self, feature_base):
        self.feature_inc(feature_base=feature_base, increment=1)

    def feature_inc(self, feature_base, increment):
        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._increment_feature_in_cur_windows(feature_name=win_pref + feature_base, increment=increment)
        self._increment_sess_feature(feature_name=sess_pref + feature_base, increment=increment)

    def feature_time_since_start(self, feature_base, cur_client_time):
        """
        Sets a session time since start feature. Will not write over a feature that has already been set.
        :param feature_base: name of feature without sess or window prefix
        :param cur_client_time: client time at which the event happened
        """
        feature_name = LakelandExtractor._SESS_PREFIX + feature_base
        if self.getValByName(feature_name) in LakelandExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name=feature_name, new_value=self.time_since_start(cur_client_time))

    def feature_max_min(self, fname_base, val):
        """feature must have the same fname_base that gets put on the following four features:
        - {_SESS_PREFIX}max_
        - {_SESS_PREFIX}min_
        - {_WINDOW_PREFIX}max_
        - {_WINDOW_PREFIX}min_ """

        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._set_feature_max_in_cur_windows(feature_name=win_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_cur_windows(feature_name=win_pref + "min_" + fname_base, val=val)
        self._set_feature_max_in_session(feature_name=sess_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_session(feature_name=sess_pref + "min_" + fname_base, val=val)

    def _increment_feature_in_cur_windows(self, feature_name, increment=None):
        increment = increment or 1
        for w in self._cur_windows:
            if self.getValByIndex(feature_name=feature_name, index=w) in LakelandExtractor._NULL_FEATURE_VALS:
                self.setValByIndex(feature_name, index=w, new_value=self._get_default_val(feature_name))
            self.features.incValByIndex(feature_name=feature_name, index=w, increment=increment)

    def _increment_sess_feature(self, feature_name, increment=None):
        increment = increment or 1
        if self.getValByName(feature_name) in LakelandExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name, new_value=self._get_default_val(feature_name))
        self.features.incAggregateVal(feature_name=feature_name, increment=increment)


    def _set_value_in_cur_windows(self, feature_name, value):
        for w in self._cur_windows:
            self.setValByIndex(feature_name=feature_name, index=w, new_value=value)

    def _set_feature_max_in_cur_windows(self, feature_name, val):
        for w in self._cur_windows:
            prev_val = self.getValByIndex(feature_name=feature_name, index=w)
            if prev_val in LakelandExtractor._NULL_FEATURE_VALS or val > prev_val:
                self.setValByIndex(feature_name=feature_name, index=w, new_value=val)

    def _set_feature_min_in_cur_windows(self, feature_name, val):
        for w in self._cur_windows:
            prev_val = self.getValByIndex(feature_name=feature_name, index=w)
            if prev_val in LakelandExtractor._NULL_FEATURE_VALS or val < prev_val:
                self.setValByIndex(feature_name=feature_name, index=w, new_value=val)

    def _set_feature_max_in_session(self, feature_name, val):
        prev_val = self.getValByName(feature_name=feature_name)
        if prev_val in LakelandExtractor._NULL_FEATURE_VALS or val > prev_val:
            self.setValByName(feature_name=feature_name, new_value=val)

    def _set_feature_min_in_session(self, feature_name, val):
        prev_val = self.getValByName(feature_name=feature_name)
        if prev_val in LakelandExtractor._NULL_FEATURE_VALS or val < prev_val:
            self.setValByName(feature_name=feature_name, new_value=val)

    def _get_default_val(self, feature_name):
        startswith = lambda prefix: feature_name.startswith(LakelandExtractor._SESS_PREFIX+prefix) or \
            feature_name.startswith(LakelandExtractor._WINDOW_PREFIX+prefix)
        if startswith('min_'):
            return float('inf')
        if startswith('time_in_'):
            return datetime.timedelta(0)
        else:
            return 0

    def getValByName(self, feature_name):
        return self.features.getValByName(feature_name)

    def setValByName(self, feature_name, new_value):
        self.features.setValByName(feature_name, new_value)

    def getValByIndex(self, feature_name, index):
        return self.features.getValByIndex(feature_name, index)

    def setValByIndex(self, feature_name, index, new_value):
        self.features.setValByIndex(feature_name, index, new_value)




    # Single Functions




    # unused
    # def _is_tutorial_mode_over(self):
    #     for tut, [tut_start, tut_end] in self._tutorial_start_and_end_times.items():
    #         if tut in LakelandExtractor._TUTORIAL_MODE and not tut_end:
    #             return False
    #     return True

    # def _avg_time_per_tutorial_mode_blurb(self):
    #     all_deltas = []
    #     for tut in LakelandExtractor._TUTORIAL_MODE:
    #         all_deltas.extend(self._tutorial_times_per_blurb[tut])
    #     return sum(all_deltas) / len(all_deltas)


    def _add_event(self, event_char):
        old = self.getValByName("event_sequence") or ''
        self.setValByName("event_sequence", old+str(event_char))

    def _change_population(self, client_time, increment):
        self._num_farmbits += increment
        self._max_population = max([self._num_farmbits, self._max_population])
        self._population_history.append((client_time, self._num_farmbits))

    def _get_pops_at_times(self, datetime_list):
        # takes in a sorted list of times and returns the population of farmbits at those times
        ret = []
        pop_i = 0
        for t in datetime_list:
            while not (pop_i + 1 >= len(self._population_history)) and self._population_history[pop_i + 1][0] < t:
                pop_i += 1
            ret.append(self._population_history[pop_i][1])
        return ret

    def _get_windows_at_time(self, client_time):
        seconds_since_start = self.time_since_start(client_time).seconds
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

  
    def milliseconds_to_datetime(self, milliseconds):
        # round #milliseconds to #secs because event_client_time resolves to seconds not msecs
        ret = datetime.datetime.utcfromtimestamp(milliseconds // 1000)
        assert ret >= self._CLIENT_START_TIME - datetime.timedelta(seconds=1)
        return ret

    def reformat_history_array(self, array, timestamp):
        """
        This function should be done in the reformatting step. History arrays contain timestamps relative to another
        timestamp that is when the array is sent through the logger. This function returns an array with absolute
        datetimes.
        :param self: self
        :param array: array to be processed. These arrays are either a list of times relative to client time or a list
        of subarrays with the last item as the time before timestamp.
        :param timestamp: time that each element is relative to (Javascript Date.now(), milliseconds since beginning 1970 UTC)
        :return: A 2D array where each subarray's final element is the absolute client time.
        """
        if not array:
            return []
        if type(array[0]) == int:
            return [self.milliseconds_to_datetime(t + timestamp) for t in array]
        else:
            ret = deepcopy(array)
            for i in range(len(ret)):
                ret[i][-1] = self.milliseconds_to_datetime(array[i][-1] + timestamp)
            return ret

    def get_tile_types_xys(self, type_list):
        if not self._TILE_OG_TYPES:
            self.log_warning("THERE ARE NO OG TYPES")
        else:
            return [LakelandExtractor.index_to_xy(i) for i, type in enumerate(self._TILE_OG_TYPES) if
                LakelandExtractor._ENUM_TO_STR['TILE TYPE'][type] in type_list]  # 5 is the lake type enum


    def time_since_start(self, client_time):
        return client_time - self._CLIENT_START_TIME

    def get_building_buildable_function(self):
        buildable_area_around_building = lambda bx, by:set((x,y) for x in range(bx-2, bx+3) for y in range(by-2, by+3))
        buildable_xys = set()
        for bx, by in self.building_xys:
            buildable_xys = buildable_xys | buildable_area_around_building(bx, by)

        # does not consider the small area in the beginning by the lake that players get for free.
        def building_buildable(t):
            type, tx, ty = t[3], t[4], t[5]
            if type != 1: # land
                return False
            if not self.in_bounds(tx, ty):
                return False
            return (tx,ty) in buildable_xys

        return building_buildable


    def in_bounds(self, tx, ty):
        # initial bounds 17-30 for 0 or 1 max farmbits.
        min_bound, max_bound = 17, 30
        # intial bounds 16-31 for 2 max farmbits, etc.
        if self._max_population > 1:
            change = self._max_population - 1
            min_bound = max(0, min_bound - self._max_population)
            max_bound = min(50, max_bound - self._max_population)
        return all(min_bound <= z <= max_bound for z in [tx, ty])

    def add_debug_str(self, s):
        self.debug_strs.append(s)
        
    def log_warning(self, message):
        self.add_debug_str('WARNING: '+message)
        debug_str = '\n'.join(self.debug_strs)
        utils.Logger.toFile(debug_str, logging.WARN)
        self.debug_strs = []
        
    def reset(self):
        self.levels:       typing.List[int]  = []
        self.last_adjust_type: str           = None
        self.features:     Extractor.SessionFeatures = Extractor.SessionFeatures(self._level_range, self._GAME_SCHEMA)
        self.setValByName('sessID', new_value=self.session_id)

        # Initialize Lakeland Variables
        # Constants
        self._TILE_OG_TYPES = []
        self._CLIENT_START_TIME = None
        self._VERSION = 0
        

        # Feature Setting Vars
        self._cur_windows = []
        self.average_handler_window = defaultdict(lambda: {k: {'n': 0, 'total': 0} for k in self.WINDOW_RANGE})
        self.average_handler_session = defaultdict(lambda: {'n': 0, 'total': 0})

        # Flags
        self._nutrition_view_on = False
        self._halt = False
        self._first_gamestate = True
        self._debug = False
        self._continue = None
        self._end = False

        # Timestamps
        self._last_active_log_time = None
        self._last_speed_change = None
        self._last_nutrition_open = None
        self._last_event_time = None

        # Gamestate Trackers: Continue Independent
        self._selected_buy_cost = 0
        self._emotes_by_window = defaultdict(lambda: [])
        self._cur_speed = 2  # default is play, 2
        # TODO: Check and see if all the tutorials are correct with skips/continues etc
        self._tutorial_times_per_blurb = {key: [] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        # self._time_per_speed = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['SPEED']}
        # self._tutorial_start_and_end_times = {key: [None, None] for key in LakelandExtractor._STR_TO_ENUM['TUTORIALS']}
        # self._tutorial_compliance = {tut: None for tut in LakelandExtractor._TUTORIAL_MODE}

        # Gamestate Trackers: Continue Dependent
        self._num_farmbits = 0
        self._population_history = [(datetime.datetime.min, 0)]  # client time, population
        self.building_xys = []
        self._tiles = defaultdict(lambda: {'marks': [1, 1, 1, 1], 'type': 0})
        self._max_population = 0


    @staticmethod
    def onscreen_item_dict():
        ret = {key: 0 for key in LakelandExtractor._STR_TO_ENUM['ITEM TYPE']}
        ret.update({key: 0 for key in LakelandExtractor._STR_TO_ENUM['BUYS']})
        del ret['null']
        return ret


    @staticmethod
    def index_to_xy(index):
        x = index % 50
        y = index // 50
        return x, y




def avg(l):
    """
    Returns average of a list. Allows elements to be datetime time intervals.
    :param l: list
    :return: Average (L1 distance between elements)
    """
    if len(l) == 0:
        return None
    if len(l) == 1:
        return l[0]

    lsum = l[0]
    for d in l[1:]:
        lsum += d
    return lsum / len(l)


def list_deltas(l):
    return [l[i] - l[i - 1] for i in range(1, len(l))]


def distance(point1, point2):
    """

    :param point1: x,y for point 1
    :param point2: x,y for point 2
    :return: euclidean distance between x and y
    """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def get_tile_txy(tile):
    return tile[4], tile[5]

def tile_i_to_xy(i):
    ty = i//50
    tx = i%50
    return tx,ty




