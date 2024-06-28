""" Lakeland Feature Extractor
Note that a separate file unique to the lakeland extractor is necessary to run this script.
The file is Lakeland Enumerators.json, and is required for the line:
_STR_TO_ENUM = utils.loadJSONFile("games/LAKELAND/Lakeland Enumerators.json")

This json file is created from the fielddaylab/lakeland README on github via
"produce_lakeland_enumerators.py". Please run that script with the appropriate inpath and outpath before running this
script.
"""

## import standard libraries
import logging
import os
import sys
import traceback
import typing
from collections import defaultdict, Counter
from copy import deepcopy
from datetime import datetime, timedelta
from math import sqrt
from pathlib import Path
from typing import Any, Dict, List, Optional
## import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.legacy.LegacyFeature import LegacyFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils import utils
from ogd.core.utils.Logger import Logger

# temp comment

## @class LakelandExtractor
#  Extractor subclass for extracting features from Lakeland game data.
class LakelandExtractor(LegacyFeature):
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
    try:
        # TODO: someday, change directory to the directory of current file first, and fix this path, so we don't have indirection issues.
        _STR_TO_ENUM = utils.loadJSONFile(filename="LakelandEnumerators.json", path=Path(".") / "ogd" / "games" / "LAKELAND" / "features" )
    except FileNotFoundError as err:
        Logger.Log(message=f"Could not load Lakeland Enumerators", level=logging.WARNING)
        _STR_TO_ENUM = {}
    _ENUM_TO_STR = {cat: {y: x for x, y in ydict.items()} for cat, ydict in _STR_TO_ENUM.items()}
    _ITEM_MARK_COMBINATIONS = [('food', 'sell'), ('food', 'use'), ('food', 'eat'),
                               ('milk', 'sell'), ('milk', 'use'), ('poop', 'sell'), ('poop', 'use')
                               ]
    _EMOTE_STR_TO_AFFECT = { # 0 neutral, -1 negative, 1 positive
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
    _BUILDING_TYPES = ['farm', 'livestock', 'home', 'road', 'sign', 'grave'] # cannot remove these items

    _ACTIVE_EVENTS = ["SELECTTILE", "SELECTFARMBIT", "SELECTITEM", "SELECTBUY", "BUY",
                    "CANCELBUY","TILEUSESELECT","ITEMUSESELECT", 'STARTGAME', 'TOGGLENUTRITION',
                      "TOGGLESHOP", "TOGGLEACHIEVEMENTS", "SKIPTUTORIAL", "SPEED"]

    _EXPLORATORY_EVENTS = ['SELECTTILE', 'SELECTFARMBIT', 'SELECTITEM', 'TOGGLEACHIEVEMENTS', 'TOGGLESHOP', 'TOGGLENUTRITION']

    _IMPACT_EVENTS = ["BUY","TILEUSESELECT","ITEMUSESELECT"]

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
    def __init__(self, params:GeneratorParameters, game_schema:GameSchema, session_id:str):
        # Initialize superclass
        super().__init__(params=params, game_schema=game_schema, session_id=session_id)
        # Set window and overlap size
        self._NUM_SECONDS_PER_WINDOW = game_schema.Config[LakelandExtractor._WINDOW_PREFIX+'WINDOW_SIZE_SECONDS']
        self._NUM_SECONDS_PER_WINDOW_OVERLAP = game_schema.Config["WINDOW_OVERLAP_SECONDS"]
        self._GAME_SCHEMA = game_schema
        self._IDLE_THRESH_SECONDS = game_schema.Config['IDLE_THRESH_SECONDS']
        self.WINDOW_RANGE = range(game_schema.LevelRange.stop)
        self._WINDOW_RANGES = self._get_window_ranges()
        self._cur_gameplay = 1
        self._startgame_count = 0
        self.debug_strs = []

        # set window range
        
        self.reset()
        self.setValByName('num_play', self._cur_gameplay)
    
    def _extractFeaturesFromEvent(self, event:Event):
        try:
            self._updateFromEvent(event)
        except Exception as e:
            if len(self.debug_strs) > 10:
                debug_strs = self.debug_strs[:5] + ['...'] + self.debug_strs[-5:]
            else:
                debug_strs = self.debug_strs
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Logger.Log('\n'.join(debug_strs), logging.DEBUG)
            Logger.Log('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)), logging.ERROR)
            if True:
                pass


    ## Function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param table_schema A data structure containing information on how the db
    #                      table assiciated with this game is structured.
    def _updateFromEvent(self, event:Event):

        # put some data in local vars, for readability later.
        self.event_client_time = event.Timestamp
        server_time = event.EventData['server_time']
        event_type_str = LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][int(event.EventName.split('.')[-1])].upper()
        if self._end and event_type_str in ['STARTGAME', 'NEWFARMBIT']:
            self._cur_gameplay += 1
            self.setValByName('num_play', self._cur_gameplay)
        if not self._VERSION:
            self._VERSION = event.LogVersion
            self.setValByName("version", self._VERSION)
        # Check for invalid row.
        if self.ExtractionMode == ExtractionMode.SESSION and event.SessionID != self._session_id:
            Logger.Log(f"Got a row with incorrect session id! Expected {self._session_id}, got {event.SessionID}!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.getValByName(feature_name="persistentSessionID") == 0:
                self.setValByName(feature_name="persistentSessionID", new_value=event.UserData['persistent_session_id'])
            # if self.getValByName(feature_name="player_id") == 0:
            #     self.setValByName(feature_name="player_id",
            #                                new_value=row_with_complex_parsed[table_schema.player_id_index])

            # if this is the first row
            if not self._CLIENT_START_TIME:
                # initialize this time as the start
                self._extractFromFirst(event.Timestamp, event.EventData)

            # set current windows
            new_windows = self._get_windows_at_time(event.Timestamp)
            if not new_windows:
                return # reached past the max windows
            old_max, new_min = max(self._cur_windows), min(new_windows)
            skipped_windows = list(range(old_max+1, new_min))
            started_windows = [w for w in new_windows if w not in self._cur_windows]
            finished_windows = [w for w in self._cur_windows if w not in new_windows]
            window_len_td = timedelta(self._NUM_SECONDS_PER_WINDOW)
            if skipped_windows:
                if self._active:
                    self._add_event("Z")
                    self.feature_count('count_idle', windows=[skipped_windows[0]])
                self._active = False
                self.setValByName('rt_currently_active', int(self._active))
                for w in skipped_windows:
                    self.start_window(w)
                    self.feature_inc('time_in_secs', window_len_td, windows=[w])
                    self.feature_inc('time_idle', window_len_td, windows=[w])
                    self.finish_window(w)

            for w in started_windows:
                self.start_window(w)
                # prev_window_end_time = self._CLIENT_START_TIME + \
                #     timedelta(seconds = self._WINDOW_RANGES[w-1][1],
                #                         milliseconds= 999)
                # if event_type_str not in LakelandExtractor._ACTIVE_EVENTS:
                #     self._extractFromActive(prev_window_end_time, None)
                # else:
                #     self._extractFromInactive(prev_window_end_time, None)
            for w in finished_windows:
                self.finish_window(w)

            self._cur_windows = new_windows

            # Record that an event of any kind occurred, for the window & session
            time_since_start = self.time_since_start(event.Timestamp)
            self.feature_count(feature_base="EventCount")
            self.setValByName(feature_name="sessDuration", new_value=time_since_start)
            if event_type_str == "BUY" and event.EventData["success"]:
                debug_str = LakelandExtractor._ENUM_TO_STR['BUYS'][event.EventData["buy"]].upper()
            if event_type_str == 'STARTGAME':
                debug_str = "START" if event.EventData.get("continue") == False else "CONTINUE"
                debug_str += f' Language: {event.EventData.get("language")}'
            else:
                debug_str = ''
            self.add_debug_str(f'{self._num_farmbits } {time_since_start} {event_type_str} {debug_str}')


            self._extractFromAll(event.Timestamp, event.EventData)
            # Then, handle cases for each type of event
            if event_type_str in LakelandExtractor._ACTIVE_EVENTS:
                self._extractFromActive(event.Timestamp, event.EventData)
            else:
                self._extractFromInactive(event.Timestamp, event.EventData)
            if event_type_str in LakelandExtractor._EXPLORATORY_EVENTS:
                self._extractFromExplore(event.Timestamp, event.EventData)
            if event_type_str in LakelandExtractor._IMPACT_EVENTS:
                self._extractFromImpact(event.Timestamp, event.EventData)
            match event_type_str:
                case "GAMESTATE":
                    self._extractFromGamestate(event.Timestamp, event.EventData)
                case "STARTGAME":
                    self._extractFromStartgame(event.Timestamp, event.EventData)
                case "CHECKPOINT":
                    self._extractFromCheckpoint(event.Timestamp, event.EventData)
                case "SELECTTILE":
                    self._extractFromSelecttile(event.Timestamp, event.EventData)
                case "SELECTFARMBIT":
                    self._extractFromSelectfarmbit(event.Timestamp, event.EventData)
                case "SELECTITEM":
                    self._extractFromSelectitem(event.Timestamp, event.EventData)
                case "SELECTBUY":
                    self._extractFromSelectbuy(event.Timestamp, event.EventData)
                case "BUY":
                    self._extractFromBuy(event.Timestamp, event.EventData)
                case "CANCELBUY":
                    self._extractFromCancelbuy(event.Timestamp, event.EventData)
                case "ROADBUILDS":
                    self._extractFromRoadbuilds(event.Timestamp, event.EventData)
                case "TILEUSESELECT":
                    self._extractFromTileuseselect(event.Timestamp, event.EventData)
                case "ITEMUSESELECT":
                    self._extractFromItemuseselect(event.Timestamp, event.EventData)
                case "TOGGLENUTRITION":
                    self._extractFromTogglenutrition(event.Timestamp, event.EventData)
                case "TOGGLESHOP":
                    self._extractFromToggleshop(event.Timestamp, event.EventData)
                case "TOGGLEACHIEVEMENTS":
                    self._extractFromToggleachievements(event.Timestamp, event.EventData)
                case "SKIPTUTORIAL":
                    self._extractFromSkiptutorial(event.Timestamp, event.EventData)
                case "SPEED":
                    self._extractFromSpeed(event.Timestamp, event.EventData)
                case "ACHIEVEMENT":
                    self._extractFromAchievement(event.Timestamp, event.EventData)
                case "FARMBITDEATH":
                    self._extractFromFarmbitdeath(event.Timestamp, event.EventData)
                case "BLURB":
                    self._extractFromBlurb(event.Timestamp, event.EventData)
                case "CLICK":
                    self._extractFromClick(event.Timestamp, event.EventData)
                case "RAINSTOPPED":
                    self._extractFromRainstopped(event.Timestamp, event.EventData)
                case "HISTORY":
                    self._extractFromHistory(event.Timestamp, event.EventData)
                case "ENDGAME":
                    self._extractFromEndgame(event.Timestamp, event.EventData)
                case "EMOTE":
                    self._extractFromEmote(event.Timestamp, event.EventData)
                case "FARMFAIL":
                    self._extractFromFarmfail(event.Timestamp, event.EventData)
                case "BLOOM":
                    self._extractFromBloom(event.Timestamp, event.EventData)
                case "FARMHARVESTED":
                    self._extractFromFarmharvested(event.Timestamp, event.EventData)
                case "MILKPRODUCED":
                    self._extractFromMilkproduced(event.Timestamp, event.EventData)
                case "POOPPRODUCED":
                    self._extractFromPoopproduced(event.Timestamp, event.EventData)
                case "DEBUG":
                    self._extractFromDebug(event.Timestamp, event.EventData)
                case "NEWFARMBIT":
                    self._extractFromNewfarmbit(event.Timestamp, event.EventData)
                case "AVAILABLEFOOD":
                    self._extractFromAvailablefood(event.Timestamp, event.EventData)
                case "MONEYRATE":
                    self._extractFromMoneyrate(event.Timestamp, event.EventData)
                case "SADFARMBITS":
                    self._extractFromSadfarmbits(event.Timestamp, event.EventData)
                case "LAKENUTRITION":
                    self._extractFromLakenutrition(event.Timestamp, event.EventData)
                case "SALESTART":
                    self._extractFromSalestart(event.Timestamp, event.EventData)
                case "SALEEND":
                    self._extractFromSaleend(event.Timestamp, event.EventData)
                case "RAINSTARTED":
                    self._extractFromRainstarted(event.Timestamp, event.EventData)
                case "EATFOOD":
                    self._extractFromEatfood(event.Timestamp, event.EventData)
                case "RESET":
                    self._extractFromReset(event.Timestamp, event.EventData)
                case _:
                    raise Exception(f"Found an unrecognized event type: {event.EventName}")

    def _extractFromFirst(self, event_client_time, event_data):
        self._CLIENT_START_TIME = event_client_time
        self._last_speed_change = self._CLIENT_START_TIME
        self._last_active_event_time = event_client_time
        self._last_event_time = event_client_time
        self._active = True
        self.add_debug_str(f'{"*" * 10}\nPlay {self._cur_gameplay} \n' +
                           f'{self._session_id} v{self._VERSION} @ {self._CLIENT_START_TIME}')
        self.setValByName("play_year", self._CLIENT_START_TIME.year)
        self.setValByName("play_month", self._CLIENT_START_TIME.month)
        self.setValByName("play_day", self._CLIENT_START_TIME.day)
        self.setValByName("play_hour", self._CLIENT_START_TIME.hour)
        self.setValByName("play_minute", self._CLIENT_START_TIME.minute)
        self.setValByName("play_second", self._CLIENT_START_TIME.second)


    def _extractFromAll(self, event_client_time, event_data):
        pass

    def _extractFromActive(self, event_client_time, event_data=None):
        # if event_data_complex is none, this isnt an event, its a start/end of a window
        zero_td = timedelta(0)
        idle_thresh_td = timedelta(seconds=self._IDLE_THRESH_SECONDS)
        time_between_actives = event_client_time - self._last_active_event_time
        if time_between_actives < idle_thresh_td:
            self._increment_sess_feature('sess_time_active', time_between_actives)
        else:
            self._increment_sess_feature('sess_time_idle', time_between_actives)
            pass
        if len(self._cur_windows) == 1:
            prev_windows = self._get_windows_at_time(self._last_active_event_time)
            if len(prev_windows) == 1:
                # only works if windows are only in series, never in parallel
                # feature to increment
                prev_window, cur_window = prev_windows[0], self._cur_windows[0]
                cur_window_start_time, _ = self._get_window_start_end_time(cur_window)
                if self._last_active_event_time < cur_window_start_time:
                    # split between two windows
                    time_between_actives_1 = cur_window_start_time - self._last_active_event_time
                    time_between_actives_2 = event_client_time - cur_window_start_time
                    if time_between_actives < idle_thresh_td:
                        # active, two windows
                        self._increment_feature_in_cur_windows('time_active', time_between_actives_1, windows=[prev_window])
                        self._increment_feature_in_cur_windows('time_active', time_between_actives_2, windows=[cur_window])
                    else:
                        # idle, two windows
                        if not self._active:
                            # if went idle
                            self._add_event("Z")
                            self.feature_count('count_idle', windows=[prev_window])
                            self._active = False
                        self._increment_feature_in_cur_windows('time_idle', time_between_actives_1, windows=[prev_window])
                        self._increment_feature_in_cur_windows('time_idle', time_between_actives_2, windows=[cur_window])
                else:
                    # keep in one window
                    if time_between_actives < idle_thresh_td:
                        # active, one window
                        self._increment_feature_in_cur_windows('time_active', time_between_actives)
                    else:
                        # idle, one window
                        if not self._active:
                            # if went idle
                            self._add_event("Z")
                            self.feature_count('count_idle')
                            self._active = False
                        self._increment_feature_in_cur_windows('time_idle', time_between_actives)



        #     # if all in one window
        #     prev_windows = self._get_windows_at_time(self._last_active_event_time)
        #     # logic breaks if multiple windows at a time
        #     assert len(prev_windows) == 1
        #
        #     # if split between multiple prev window
        #     if time_between_actives > timedelta(seconds=self._IDLE_THRESH_SECONDS):
        #         self._add_event("Z")
        #         self.feature_count('count_idle')
        #         time_idle = time_between_actives
        #         time_active = zero_td
        #     else:
        #         time_active = time_between_actives
        #         time_idle = zero_td
        # else:
        #     time_active = zero_td
        #     time_idle = event_client_time - self._last_event_time

        self._last_active_event_time = event_client_time
        self._last_event_time = event_client_time
        self._active = True
        # self.feature_inc('time_in_secs',time_active+time_idle)
        # self.feature_inc('time_idle', time_idle)
        # self.feature_inc('time_active', time_active)
        self.setValByName('rt_currently_active',int(self._active))
        if event_data is not None:
            self.feature_count(feature_base="ActiveEventCount")


    def _extractFromInactive(self, event_client_time, event_data=None):
        # if event_data_complex is none, this isnt an event, its a start/end of a window
        # zero_td = timedelta(0)
        # if not self._active:
        #     time_idle = event_client_time - self._last_event_time
        # else:
        #     time_since_last_active = event_client_time - self._last_active_event_time
        #     idle_thresh = timedelta(seconds=self._IDLE_THRESH_SECONDS)
        #     if time_since_last_active > idle_thresh:
        #         self._active = False
        #         self._add_event("Z")
        #         self.feature_count('count_idle')
        #         time_idle = time_since_last_active
        #     else:
        #         time_idle = zero_td
        #
        # self._last_event_time = event_client_time
        # self.feature_inc('time_in_secs',time_idle)
        # self.feature_inc('time_idle', time_idle)
        self.setValByName('rt_currently_active', int(self._active))
        if event_data is not None:
            self.feature_count(feature_base="InactiveEventCount")

    def _extractFromExplore(self, event_client_time, event_data):
        self.feature_count('count_explore_events')

    def _extractFromImpact(self, event_client_time, event_data):
        self.feature_count('count_impact_events')



    def _extractFromGamestate(self, event_client_time, event_data):
        pass
        # # assign event_data variables
        # d = event_data
        # _tiles = d["tiles"]
        # _farmbits = d["farmbits"]
        # _items = d["items"]
        # _money = d["money"]
        # _speed = d["speed"]
        # _achievements = d["achievements"]
        # _num_checkpoints_completed = d["num_checkpoints_completed"]
        # _raining = d["raining"]
        # _curr_selection_type = d["curr_selection_type"]
        # _curr_selection_data = d.get("curr_selection_data")
        # _camera_center = d["camera_center"]
        # _gametime = d["gametime"]
        # _timestamp = d["timestamp"]
        # _num_food_produced = d["num_food_produced"]
        # _num_milk_produced = d["num_milk_produced"]
        # _num_poop_produced = d["num_poop_produced"]
        #
        # # reformat raw variable functions
        # def array_to_mat(num_columns, arr):
        #     assert len(arr) % num_columns == 0
        #     return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]
        # def read_stringified_array(arr):
        #     if not arr:
        #         return []
        #     return [int(x) for x in arr.split(',')]
        #
        # # reformat array variables
        # _tiles = read_stringified_array(_tiles)
        # _farmbits = read_stringified_array(_farmbits)
        # _items = read_stringified_array(_items)
        # _tiles = array_to_mat(4, _tiles)
        # _farmbits = array_to_mat(9, _farmbits)
        # _items = array_to_mat(4, _items)
        #
        # # set class variables
        # if self._first_gamestate and self._continue:
        #     for i,t in enumerate(_tiles):
        #         type = t[3]
        #         if LakelandExtractor._ENUM_TO_STR['TILE TYPE'][type] in LakelandExtractor._BUILDING_TYPES:
        #             self.building_xys.append(tile_i_to_xy(i))
        #         if type in [9,10]: #farm or livestock
        #             self._tiles[tile_i_to_xy(i)]['type'] = type
        #
        # if self._num_farmbits != len(_farmbits):
        #     # if the num farmbits arent as expected or just one more than expected (sometimes takes a while to show), show warning.
        #     self.log_warning(f'Gamestate showed {len(_farmbits)} but expected {self._num_farmbits} farmbits.')
        #      # self._change_population(event_client_time, len(_farmbits) - self._num_farmbits)
        #
        #
        # #  feature functions
        # # def farms_low_productivity(tiles):
        # #     return [t for t in tiles if t[3] == 9 and t[1] < 3]  # type == farm and nutrition < 3 (the circle is heavily black)
        #
        # 0# def lake_tiles_bloom(tiles):
        # #     return [t for t in tiles if t[3] == 5 and t[1] > 25]  # lake tiles bloom when nutrition > 10% of 255,
        # # so technically not all tiles > 25 nutrition are blooming, but we will put the cutoff here
        #
        # def avg_lake_nutrition(tiles):
        #     lake_nutritions = [t[1] for t in tiles if t[2] == 5] # 5 is the lake enum for tile type
        #     if len(lake_nutritions) == 0:
        #         self.log_warning(f'No lake nutritions!!')
        #
        #     return sum(lake_nutritions) / len(lake_nutritions)
        #
        # def num_items_in_play(items, tiles):
        #     cur_num_items_on_screen = LakelandExtractor.onscreen_item_dict()
        #     for it in items:
        #         type = it[2]
        #         key = LakelandExtractor._ENUM_TO_STR["ITEM TYPE"][type]
        #         cur_num_items_on_screen[key] += 1
        #     for t in tiles:
        #         type = t[3]
        #         key = LakelandExtractor._ENUM_TO_STR["TILE TYPE"][type]
        #         if key in cur_num_items_on_screen:
        #             cur_num_items_on_screen[key] += 1
        #     return cur_num_items_on_screen
        #
        # # set features
        # self.feature_count('count_gamestate_logs')
        #
        # for (key, cur_num) in num_items_in_play(_items, _tiles).items():
        #     self.feature_max_min(f'num_{key}_in_play', cur_num)
        # self.feature_max_min(fname_base="avg_lake_nutrition", val=avg_lake_nutrition(_tiles))
        # # self.feature_max_min("num_farms_low_productivity", len(farms_low_productivity(_tiles)))
        # # self.feature_max_min("num_lake_tiles_in_bloom", len(lake_tiles_bloom(_tiles)))

    def _extractFromStartgame(self, event_client_time, event_data):
        self._startgame_count += 1
        if self._startgame_count > 1:
            self.add_debug_str(f"Starting game {self._startgame_count}.")
        if self._startgame_count != self._cur_gameplay:
            self.log_warning(f"Starting game {self._cur_gameplay} but this is the {self._startgame_count}th start!")

        # assign event_data variables
        d = event_data
        _tile_states = d["tile_states"]
        _tile_nutritions = d["tile_nutritions"]
        _continue = d["continue"]
        _language = d["language"]
        _audio = d["audio"]
        _fullscreen = d["fullscreen"]

        # set class variables
        self._TILE_OG_TYPES = _tile_states
        self._continue = _continue
        self._first_gamestate = False


        # feature functions

        # set features
        self.setValByName("continue", _continue)
        self.setValByName("language", _language)
        self.setValByName("audio", _audio)
        self.setValByName("fullscreen", _fullscreen)

        if not self._continue:
            for key in self.onscreen_item_dict():
                self.feature_max_min(f'num_{key}_in_play', 0)



    def _extractFromCheckpoint(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
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
            self.feature_time_since_start(feature_base=f"time_to_{_event_label}_tutorial")
            self.feature_inc(feature_base='count_encounter_tutorial', increment=is_tutorial_start)
        # TODO: Case where blurb history exists but player skipped
        if is_tutorial_end and len(_blurb_history) > 1:
            self.setValByName(
                feature_name=f"{LakelandExtractor._SESS_PREFIX}avg_time_per_blurb_in_{_event_label}_tutorial",
                new_value=avg_time_per_blurb(_event_label))

    def _extractFromSelecttile(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # set features
        self.feature_count("count_inspect_tile")

    def _extractFromSelectfarmbit(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]

        # set features
        self.feature_count("count_inspect_farmbit")

    def _extractFromSelectitem(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _item = d["item"]

        # set features
        self.feature_count("count_inspect_item")

    def _extractFromSelectbuy(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _buy = d["buy"]
        _cost = d["cost"]
        _cur_money = d["curr_money"]
        _success = d["success"]

        # set class variables
        self._selected_buy_cost = _cost
        self._cur_money = _cur_money

    def _extractFromBuy(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _buy = d["buy"]
        _tile = d["tile"]
        _success = d["success"]
        _buy_hovers = d["buy_hovers"]
        _client_time = d["client_time"]

        if not _success:
            return

        # helpers
        valid_hovers = [h for h in _buy_hovers if h[6] > 0] # h[6] (placement_valid) denotes if players can build there or not
        buy_name = LakelandExtractor._ENUM_TO_STR['BUYS'][_buy]

        # set class variables
        if buy_name in LakelandExtractor._BUILDING_TYPES:
            self.building_xys.append(get_tile_txy(_tile))

        if buy_name in ['farm', 'livestock', 'home', 'road', 'sign']:
            self._tiles[get_tile_txy(_tile)]['type'] = buy_name

        # feature functions
        def chose_highest_nutrient_tile(buy_hovers, chosen_tile):
            if not buy_hovers:
                return None
            building_buildable_func = self.get_building_buildable_function() if Event.CompareVersions(self._VERSION, "15") < 0 \
                else lambda buy_t: buy_t[-2] # whether the tile is buildable (v15 buy hover data contains:
                                             # [tile_data_short, buildable, hover_time]
            for t in buy_hovers:
                # t has the current type of land (only type that farms can be built on) and a building (farm) can be placed there
                if t[3] == 1 and building_buildable_func(t):
                    # if any tile found has a nutrient value more than 2 above the chosen tile, fail
                    if t[1] > (chosen_tile[1]+2):  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
                       return 0  # failed to put on highest nutrition tile
            return 1

        # I think that the calculation was mostly fine, but it definitely doesnt work if player never hovers tiles.
        def chose_lowest_nutrient_farm(buy_hovers, chosen_tile):
            if not buy_hovers:
                return None
            for t in buy_hovers:
                if t[3] == 9:  # t has the current type of farm (only type that fertilizer can be built on)
                    # if any tile found has a nutrient value less than 2 below the chosen tile, fail
                    if t[1] < (chosen_tile[1]-2):  # comparing the nutritions give or take 2/255 ~ 1% of nutrition
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
        self.feature_time_since_start(f'time_to_first_{buy_name}_buy')
        self.feature_inc(feature_base=f"money_spent_{buy_name}", increment=self._selected_buy_cost)
        self.feature_count(feature_base=f'count_buy_{buy_name}')
        self.feature_average(fname_base=f'avg_num_tiles_hovered_before_placing_{buy_name}', value=len(valid_hovers))
        if buy_name == 'farm':
            self.feature_average(fname_base='percent_building_a_farm_on_highest_nutrition_tile',
                             value=chose_highest_nutrient_tile(valid_hovers, _tile))
        if buy_name == 'fertilizer':
            self.feature_average(fname_base="percent_placing_fertilizer_on_lowest_nutrient_farm",
                                 value=chose_lowest_nutrient_farm(valid_hovers, _tile))
            dist = dist_to_lake(_tile)
            if dist:
                self.feature_average("avg_distance_between_poop_placement_and_lake", dist)
        if buy_name in LakelandExtractor._BUILDING_TYPES:
            self.feature_average(fname_base='avg_avg_distance_between_buildings', value=avg_distance_between_buildings())
            self.feature_max_min(f'num_{buy_name}_in_play', len([t for t in self._tiles.values() if t['type'] == buy_name]))

        self._add_event(_buy)

    # def _tutorial_compliance_check(self, tut_name, event_client_time):
    #     tutorial_end_time = self._tutorial_start_and_end_times[tut_name][1]
    #     if not self._tutorial_compliance[tut_name] and tutorial_end_time:
    #         compliance_interval = event_client_time - tutorial_end_time
    #         fname = f"{tut_name}_compliance_interval"
    #         self.setValByName(feature_name=fname, new_value=compliance_interval)

    def _extractFromCancelbuy(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _selected_buy = d["selected_buy"]
        _cost = d["cost"]
        _buy_hovers = d["buy_hovers"]
        _client_time = d["client_time"]

        # set class variables
        self._selected_buy_cost = 0

    def _extractFromRoadbuilds(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _road_builds = d["road_builds"]
        _client_time = d["client_time"]

    def _extractFromTileuseselect(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        mark_change = self._tiles[(get_tile_txy(_tile))]['marks'] != _marks
        if not mark_change:
            return
        self._tiles[(get_tile_txy(_tile))]['marks'] = _marks
        all_farm_marks = [t["marks"] for t in self._tiles.values() if t["type"] == 'farm'] # 9 == farm
        all_dairy_marks = [t["marks"] for t in self._tiles.values() if t["type"] == 'livestock'] # 10 == livestock
        food_uses = [t[0] for t in all_farm_marks] + [t[1] for t in all_farm_marks] # mark index=0,1 food mark
        milk_uses = [t[0] for t in all_dairy_marks] # mark index=0 is the dairy mark
        poop_uses = [t[1] for t in all_dairy_marks] # mark index=1 is the poop mark

        # set class variables
        # self._tiles[get_tile_txy(_tile)]['type'] = _tile[3] # tile index 3 is type

        # feature setters

        self.feature_count(feature_base="count_change_tile_mark")
        self.feature_time_since_start("time_to_first_tilemarkchange")
        for produced, produced_uses in [('food', food_uses), ('milk', milk_uses), ('poop', poop_uses)]:
            mark_counts = {LakelandExtractor._ENUM_TO_STR["MARK"][k]: v for k, v in Counter(produced_uses).items()}
            # for each produced item (food, milk, poop), we now have mark counts
            # {eat: ?, use: ?, sell: ?} of total numbers marked eat, use, sell.
            for use, count in mark_counts.items():
                self.feature_max_min(f"num_{produced}_marked_{use}", count) #mark use = eat in case of food
                self.feature_max_min(f"num_per_capita_{produced}_marked_{use}", count / (self._num_farmbits or 1))
                self.feature_max_min(f"percent_{produced}_marked_{use}", count/len(produced_uses))

    def _extractFromItemuseselect(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _item = d["item"]
        _prev_mark = d["prev_mark"]

        # feature setters
        if d["prev_mark"] != _item[3]: # if the mark has changed
            self.feature_count(feature_base="count_change_item_mark")
            self.feature_time_since_start("time_to_first_itemmarkchange")

    def _extractFromTogglenutrition(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _to_state = d["to_state"]
        _tile_nutritions = d["tile_nutritions"]

        # set class variables
        self._nutrition_view_on = _to_state # (on is state==1)
        if self._nutrition_view_on:
            self._last_nutrition_open = event_client_time
            self.feature_time_since_start("time_to_first_togglenutrition")

        # set features
        self.set_time_in_nutrition_view(event_client_time)

    def _extractFromToggleshop(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _shop_open = d["shop_open"]

        # set features
        if _shop_open:
            self.feature_count("count_open_shop")

    def _extractFromToggleachievements(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _achievements_open = d["achievements_open"]

        # set features
        if _achievements_open:
            self.feature_count("count_open_achievements")
            self.feature_time_since_start("time_to_first_toggleachievements")

    def _extractFromSkiptutorial(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data

        # set features
        self.feature_count("count_skips")
        self.feature_time_since_start("time_to_first_skip")

    def _extractFromSpeed(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _cur_speed = d["cur_speed"]
        _prev_speed = d["prev_speed"]
        _manual = d["manual"]

        # set class variables
        self._cur_speed = _cur_speed


        # set features (this feature is modified by 2+ events)
        if self._cur_speed != _prev_speed:
            self.update_time_at_speed(event_client_time, _prev_speed)
            if LakelandExtractor._ENUM_TO_STR["SPEED"][_cur_speed] == "pause":
                self._add_event("P")
            elif LakelandExtractor._ENUM_TO_STR["SPEED"][_cur_speed] == "play":
                self._add_event("Q")
            elif LakelandExtractor._ENUM_TO_STR["SPEED"][_cur_speed] == "fast":
                self._add_event("R")
            elif LakelandExtractor._ENUM_TO_STR["SPEED"][_cur_speed] == "vfast":
                self._add_event("S")

    def _extractFromAchievement(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _achievement = d["achievement"]

        # helpers
        achievement_str = LakelandExtractor._ENUM_TO_STR["ACHIEVEMENTS"][_achievement]

        # set features
        self.feature_count("count_achievements")
        self.feature_time_since_start(f"time_to_{achievement_str}_achievement")

    def _extractFromFarmbitdeath(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]
        _grave = d["grave"]

        # set session variables
        self._change_population(event_client_time, -1)

        # set features
        self.feature_count("count_deaths")
        self.feature_time_since_start('time_to_first_death')
        self._add_event("D")

    def _extractFromBlurb(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data

    def _extractFromClick(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data

    def _extractFromRainstopped(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        self.feature_count("count_rains")
        self.feature_time_since_start("time_to_first_rain")

    def _extractFromHistory(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _client_time = d["client_time"]
        _camera_history = d["camera_history"]
        _emote_history = d["emote_history"]

        # reformat variables
        # _emote_history = self.reformat_history_array(_emote_history, _client_time)

        # set global variables
        # for e in _emote_history:
        #     self._add_emote_to_window_by_time(e)

    def _extractFromEndgame(self, event_client_time, event_data):
        # assign event_data variables 
        d = event_data
        # (none) = d["(none)"]
        self.update_time_at_speed(event_client_time, self._cur_speed)
        if self._nutrition_view_on:
            self.set_time_in_nutrition_view(event_client_time)

        self._end = True

    def _extractFromEmote(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]
        _emote_enum = d["emote_enum"]

        # fix bug in v13 logging where emote 2s show up as emote 0s
        if Event.CompareVersions(self._VERSION, "13") == 0 and _emote_enum == 0:
            _emote_enum = 2

        # helpers
        emote_str = LakelandExtractor._ENUM_TO_STR['EMOTES'][_emote_enum]
        affect = LakelandExtractor._EMOTE_STR_TO_AFFECT[emote_str]
        self.feature_time_since_start(f"time_to_first_{emote_str.replace('_txt','')}_emote")
        is_positive = affect == 1
        is_neutral = affect == 0
        is_negative = affect == -1
        if(self._num_farmbits) < 1:
            # self.WarningMessage(f"Num farmbits < 1 @ {self._num_farmbits}!! Setting to 1.")
            self.log_warning(f"Num farmbits < 1 @ {self._num_farmbits}!! Setting to 1.")
            self._num_farmbits = 1

        per_capita_val = 1/self._num_farmbits

        # set features
        self.feature_inc(f"count_{emote_str}_emotes_per_capita", per_capita_val)

        self.feature_average("percent_negative_emotes", is_negative)
        self.feature_average("percent_neutral_emotes", is_neutral)
        self.feature_average("percent_positive_emotes", is_positive)

        self.feature_inc("total_negative_emotes", is_negative)
        self.feature_inc("total_neutral_emotes", is_neutral)
        self.feature_inc("total_positive_emotes", is_positive)

    def _extractFromFarmfail(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers

        # set class variables

        # set features
        self.feature_count("count_farmfails")
        self.feature_time_since_start("time_to_first_farmfail")

    def _extractFromBloom(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_count("count_blooms")
        self.feature_time_since_start('time_to_first_bloom')
        self._add_event("B")

    def _extractFromFarmharvested(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_food_produced", 2)

    def _extractFromMilkproduced(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_milk_produced", 1)
        self.feature_time_since_start("time_to_first_milkproduced")

    def _extractFromPoopproduced(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _tile = d["tile"]
        _marks = d["marks"]

        # helpers
        # set class variables
        # set features
        self.feature_inc("count_poop_produced", 1)
        self.feature_time_since_start("time_to_first_poopproduced")

    def _extractFromDebug(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        self.add_debug_str('Set debug')

        # helpers
        self._debug = True
        # set class variables
        # set features
        self.setValByName(feature_name='debug', new_value=1)

    def _extractFromNewfarmbit(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]

        # helpers
        # set class variables
        self._change_population(client_time=event_client_time, increment=1)
        # set features

    def _extractFromAvailablefood(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _foods = d["food"]  # gg.food | Current amount of food available on board  |
        _farmbits = d["farmbit"]  # gg.farmbits.length | Current number of farmbits on board  |
        _foodrate = d["food_perfarmbit"]  # gg.food/gg.farmbits.length | Food available per farmbit  |

        #helpers
        # set class variables
        # set features

    def _extractFromMoneyrate(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _money = d["money"]  # sell_rate*item_worth_food | Money accumulated according to amount of available items to sell  |
        _rate = d["rate"]  # money/permin | Rate of money accumulation  |

        #helpers
        # set class variables
        # set features

    def _extractFromSadfarmbits(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _sads = d["sad"]  # sad | Number of farmbits with joy status of DESPERATE  |
        _farmbits = d["farmbit"]  # gg.farmbits.length | Current number of farmbits on board  |
        _sad_perfarmbit = d["sad_perfarmbit"]  # sad/gg.farmbits.length | Amount of sadness per farmbit  |

        #helpers
        # set class variables
        # set features

    def _extractFromLakenutrition(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _lake_pos_tile = d["lake_pos_tile"]  # gg.lake_nutes.length | Number of lake tiles on the board  |
        _total_nutrition = d["total_nutrition"]  # gg.lake_nutes.reduce((a,b) => a + b, 0) | Total nutrition of the lake
        #helpers
        # set class variables
        # set features

    def _extractFromSalestart(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]  # farmbit_data_short(f) | Farmbit information reduced to an array.
        _item = d["item"]  # item_data_short(it)| Item information reduced to an array. See [Data Short](#DataShort)  |
        _worth = d["worth"]  # worth | monetary value of the item to be sold |
        #helpers
        # set class variables
        # set features

        item_type_str = self._ENUM_TO_STR["ITEM TYPE"][_item[2]]
        # items_on_screen[item_type_str] -= 1

        self.feature_time_since_start(f"time_to_first_{item_type_str}_sale")

    def _extractFromSaleend(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]  # farmbit_data_short(f) | Farmbit information reduced to an array.
        _item = d["item"]  # item_data_short(it)| Item information reduced to an array. See [Data Short](#DataShort)  |
        _worth = d["worth"]  # worth | monetary value of the item sold |

        #helpers
        # set class variables
        # set features
        self.feature_inc("money_earned", _worth)

    def _extractFromRainstarted(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        # The log itself indicates that rain has started.

        #helpers
        # set class variables
        # set features

    def _extractFromEatfood(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
        _farmbit = d["farmbit"]  # farmbit_data_short(f) | Farmbit information reduced to an array.
        _item = d["item"]  # item_data_short(it)| Item information reduced to an array. See [Data Short](#DataShort)  |

        #helpers
        # set class variables
        # set features

    def _extractFromReset(self, event_client_time, event_data):
        # assign event_data variables
        d = event_data
         # The log itself indicates that the game has recieved the signal to reset.

        #helpers
        # set class variables
        # set features
        self.feature_time_since_start(feature_base=f"time_to_reset")

    def finish_window(self, w):
        window_end_time = timedelta(seconds=self._WINDOW_RANGES[w][1])
        for f in self.features._perlevel_names:
            cur_val = self.getValByIndex(f, w)
            if cur_val == float('inf'):
                # if min_ feature is still float('inf'), then max_value and min_value should still be 0.
                self.setValByIndex(f, w, new_value=0)
        if self._nutrition_view_on:
            self.set_time_in_nutrition_view(self._CLIENT_START_TIME + window_end_time)
            self._last_nutrition_open = self._CLIENT_START_TIME + window_end_time

        # update time_in_secs to full (might not be full

    def start_window(self, w):
        for f in self.features._perlevel_names:
            self.setValByIndex(f, w, new_value=self._get_default_val(f))
        if w > 0:
            for type in self._BUILDING_TYPES:
                # these types are immutable, so they will be at minimum the max previous value
                prev_val = self.getValByIndex(f'max_num_{type}_in_play', w-1)
                self.setValByIndex(f'min_num_{type}_in_play', w, prev_val)
                self.setValByIndex(f'max_num_{type}_in_play', w, prev_val)

    def _calculateAggregateFeatures(self):
        for w in self._cur_windows:
            self.finish_window(w)

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
        if value == None:
            return
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

    def feature_count(self, feature_base, windows=None):
        self.feature_inc(feature_base=feature_base, increment=1, windows=windows)

    def feature_inc(self, feature_base, increment, windows=None):
        win_pref, sess_pref = LakelandExtractor._WINDOW_PREFIX, LakelandExtractor._SESS_PREFIX
        self._increment_feature_in_cur_windows(feature_name=win_pref + feature_base, increment=increment, windows=windows)
        self._increment_sess_feature(feature_name=sess_pref + feature_base, increment=increment)

    def feature_time_since_start(self, feature_base):
        """
        Sets a session time since start feature. Will not write over a feature that has already been set.
        :param feature_base: name of feature without sess or window prefix
        :param cur_client_time: client time at which the event happened
        """
        feature_name = LakelandExtractor._SESS_PREFIX + feature_base
        feature_name_active = feature_name.replace('time_','time_active_')
        if self.getValByName(feature_name) in LakelandExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name=feature_name, new_value=self.time_since_start(self.event_client_time))

        if self.getValByName(feature_name_active) in LakelandExtractor._NULL_FEATURE_VALS:
            time_active = self.getValByName('sess_time_active') or timedelta(0)
            self.setValByName(feature_name=feature_name_active, new_value=time_active)

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

    def _increment_feature_in_cur_windows(self, feature_name, increment=None, windows = None):
        if windows == None:
            windows = self._cur_windows
        if increment is None:
            increment = 1
        for w in windows:
            if self.getValByIndex(feature_name=feature_name, index=w) in LakelandExtractor._NULL_FEATURE_VALS:
                self.setValByIndex(feature_name, index=w, new_value=self._get_default_val(feature_name))
            self.features.incValByIndex(feature_name=feature_name, index=w, increment=increment)

    def _increment_sess_feature(self, feature_name, increment=None):
        if increment is None:
            increment = 1
        if self.getValByName(feature_name) in LakelandExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name, new_value=self._get_default_val(feature_name))
        self.features.incAggregateVal(feature_name=feature_name, increment=increment)

    def _set_value_in_cur_windows(self, feature_name, value, windows = None):
        if windows == None:
            windows = self._cur_windows
        for w in windows:
            self.setValByIndex(feature_name=feature_name, index=w, new_value=value)

    def _set_feature_max_in_cur_windows(self, feature_name, val, windows = None):
        if windows == None:
            windows = self._cur_windows
        for w in windows:
            prev_val = self.getValByIndex(feature_name=feature_name, index=w)
            if val > prev_val:
                self.setValByIndex(feature_name=feature_name, index=w, new_value=val)

    def _set_feature_min_in_cur_windows(self, feature_name, val, windows = None):
        if windows == None:
            windows = self._cur_windows
        for w in windows:
            prev_val = self.getValByIndex(feature_name=feature_name, index=w)
            if val < prev_val:
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
        if startswith('time_'):
            return timedelta(0)
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

    def _get_windows_at_time(self, client_time=None):
        # if no client time, get windows at start
        if client_time is not None:
            seconds_since_start = self.time_since_start(client_time).total_seconds()
        else:
            seconds_since_start = 0
        windows = []
        for i, (window_start, window_end) in self._WINDOW_RANGES.items():
            if window_start <= seconds_since_start < window_end:
                windows.append(i)

        return windows

    def _get_window_start_end_time(self, w):
        start_time = self._CLIENT_START_TIME + timedelta(
            seconds=self._WINDOW_RANGES[w][0])
        end_time = self._CLIENT_START_TIME + timedelta(
            seconds=self._WINDOW_RANGES[w][1])

        return (start_time, end_time)

    def _get_window_ranges(self):
        #window ranges are inclusive of the first number and exclusive of the second, i.e. (0, 30) is the range from
        # 0s to 29s
        window_start = 0
        window_end = 0
        window_ranges = {}
        for i in self.WINDOW_RANGE:
            window_end = window_end + self._NUM_SECONDS_PER_WINDOW
            window_ranges[i] = (window_start, window_end)
            window_start = window_end - self._NUM_SECONDS_PER_WINDOW_OVERLAP
        return window_ranges

    def _add_emote_to_window_by_time(self, emote):
        event_time = emote[-1]
        windows = self._get_windows_at_time(event_time)
        for window in windows:
            self._emotes_by_window[window].append(emote)

    def milliseconds_to_datetime(self, milliseconds):
        ret = datetime.utcfromtimestamp(milliseconds / 1000)
        assert ret >= self._CLIENT_START_TIME - timedelta(seconds=1)
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
        Logger.Log(debug_str, logging.WARNING)
        self.debug_strs = []
        
    def reset(self):
        self.levels:           List[int]       = []
        self.last_adjust_type: Optional[str] = None
        self.features:         LegacyFeature.LegacySessionFeatures = LegacyFeature.LegacySessionFeatures(game_schema=self._GAME_SCHEMA)
        self.setValByName('sessID', new_value=self._session_id)

        # Initialize Lakeland Variables
        # Constants
        self._TILE_OG_TYPES = []
        self._CLIENT_START_TIME = None
        self._VERSION = "0"
        

        # Feature Setting Vars
        self._cur_windows = self._get_windows_at_time()
        self.average_handler_window = defaultdict(lambda: {k: {'n': 0, 'total': 0} for k in self.WINDOW_RANGE})
        self.average_handler_session = defaultdict(lambda: {'n': 0, 'total': 0})

        # Flags
        self._active = True
        self._nutrition_view_on = False
        self._first_gamestate = True
        self._debug = False
        self._continue = None
        self._end = False

        # Timestamps
        self._last_active_event_time = None

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
        self._population_history = [(datetime.min, 0)]  # client time, population
        self.building_xys = []
        self._tiles = defaultdict(lambda: {'marks': [1, 1, 1, 1], 'type': None}) #maps (tx,ty) => {marks: [], type: int}
        self._max_population = 0

        # start first windows:
        for w in self._cur_windows:
            self.start_window(w)

    @staticmethod
    def onscreen_item_dict():
        ret = {key: 0 for key in LakelandExtractor._BUILDING_TYPES + ['food', 'poop', 'fertilizer', 'milk']}
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
