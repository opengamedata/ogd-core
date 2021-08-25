## import standard libraries
import bisect
import logging
import sys
import typing
import traceback
from collections import defaultdict, deque
from config.config import settings
from datetime import datetime, timedelta
from typing import Any, Dict,Tuple, Union
## import local files
import utils
from extractors.LegacyExtractor import LegacyExtractor
from games.JOWILDER import Jowilder_Enumerators as je
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

# temp comment

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
# TODO: Some FQIDs are called HACKME and are placeholders
class JowilderExtractor(LegacyExtractor):
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
    
    _SESS_PREFIX = 'sess_'
    _LEVEL_PREFIX = ''
    _INT_PREFIX = 'i'
    _OBJ_PREFIX = 'o'

    _EVENT_CUSTOM_TO_STR = {
         0: 'checkpoint',
         1: 'startgame',
         2: 'endgame',
         3: 'navigate_click',
         4: 'notebook_click',
         5: 'map_click',
         6: 'notification_click',
         7: 'object_click',
         8: 'observation_click',
         9: 'person_click',
         10: 'cutscene_click',
         11: 'wildcard_click',
         12: 'navigate_hover',
         13: 'notebook_hover',
         14: 'map_hover',
         15: 'notification_hover',
         16: 'object_hover',
         17: 'observation_hover',
         18: 'person_hover',
         19: 'cutscene_hover',
         20: 'wildcard_hover',
         21: 'quiz',
         22: 'quizquestion',
         23: 'quizstart',
         24: 'quizend',
    }

    _TASK_LIST = ["", "dummy_fqid0", "dummy_fqid1"]

    _LEVEL_TO_STR = {
        0: 'startgame',
        1: 'notebook',
        2: 'wiscwonders',
        3: 'mystery',
        4: 'plaque',
        5: 'notajersey',
        6: 'trashed',
        7: 'archivist',
        8: 'textile',
        9: 'logbook',
        10: 'suffragist',
        11: 'taxidermist',
        12: 'wellsdidit',
        13: 'saveteddy',
        14: 'scratches',
        15: "hesalive",
        16: 'akey',
        17: 'rescued',
        18: 'backtowork',
        19: 'sadanimals',
        20: 'flaglady',
        21: 'ecologists',
        22: 'donethework',
        23: 'sunset',
    }


    _NULL_FEATURE_VALS = ['null', 0, None]

    def __init__(self, session_id: int, game_schema: GameSchema):
        super().__init__(session_id=session_id, game_schema=game_schema)
        config = game_schema['config']
        self._IDLE_THRESH_SECONDS = config['IDLE_THRESH_SECONDS']
        self._IDLE_THRESH = timedelta(seconds=self._IDLE_THRESH_SECONDS)
        self._level_range = range(game_schema.min_level   if game_schema.min_level is not None else 0,
                                  game_schema.max_level+1 if game_schema.max_level is not None else 1)

        self.cur_task = 1
        self.time_since_start = timedelta(0)
        self._task_complete_helper = dict()
        self.level_start_timestamp = dict()
        self._CLIENT_START_TIME = None
        self.game_started = False
        self.setValByName(feature_name="sessionID", new_value=session_id)
        self.level : Union[int,None] = None
        self._cur_levels = []
        self.cur_question = 0
        self.last_display_time_text : Tuple = ()
        self.average_handler_level = defaultdict(lambda: {k: {'n': 0, 'total': 0} for k in self._level_range})
        self.average_handler_interaction = defaultdict(lambda: {k: {'n': 0, 'total': 0} for k in range(189)})
        self.average_handler_session = defaultdict(lambda: {'n': 0, 'total': 0})
        self.variance_handler_level = defaultdict(lambda: {k: [] for k in self._level_range})
        self.variance_handler_interaction = defaultdict(lambda: {k: [] for k in range(189)})
        self.variance_handler_session = defaultdict(lambda: [])
        self.debug_strs = []
        self.last_logged_text = None
        self.asked = False
        self.time_before_answer = None
        self.last_click_time = None
        self.last_click_hover_time = None
        self.text_fqid_start_end = []
        self.last_click_type = ''
        self.this_click_type = ''
        self.cur_question = 0
        self.chosen_answer = ''
        self.prev_interaction = None
        self.cur_interaction = None
        self.cur_objective = None
        self.finished_encounters = defaultdict(lambda: False)
        self.objective_chain_started = False
        self.verbose = False # bool(settings['john_sessids'])
        self.halt = False
        self._active = True
        self._last_quizstart = None
        self._quiztimes = [None]*16

    def ExtractFeaturesFromEvent(self, event:Event, table_schema:TableSchema):
        try:
            self._extractFeaturesFromRow(event, table_schema)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for place in [utils.Logger.toFile, utils.Logger.toStdOut]:
                place('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)), logging.ERROR)
                place('DEBUG STRINGS:', logging.DEBUG)
                place(self.get_debug_string(version=event.app_version, num_lines=2), logging.DEBUG)

    def _extractFeaturesFromRow(self, event:Event, table_schema: TableSchema):
        # put some data in local vars, for readability later.
        if self.halt:
            return
        old_level = self.level
        if self.game_started:
            self.level = event.event_data['level']
        if self.level is not None:
            self._cur_levels = [self.level]
        if not old_level == self.level:
            self.new_level(old_level)
        event_type_str = JowilderExtractor._EVENT_CUSTOM_TO_STR[int(event.event_name.split('.')[-1])].lower()
        # Check for invalid row.
        if event.session_id != self._session_id:
            utils.Logger.toFile(
                f"Got a row with incorrect session id! Expected {self._session_id}, got {event.session_id}!",
                logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.getValByName(feature_name="persistentSessionID") == 0:
                self.setValByName(feature_name="persistentSessionID", new_value=event.event_data['persistent_session_id'])
            if not self._CLIENT_START_TIME:
                # initialize this time as the start
                self._CLIENT_START_TIME = event.timestamp
                self.last_click_time = self._CLIENT_START_TIME
                self.last_click_hover_time = self._CLIENT_START_TIME
                self.setValByName("version", event.app_version)
                self.setValByName("play_year", self._CLIENT_START_TIME.year)
                self.setValByName("play_month",self._CLIENT_START_TIME.month)
                self.setValByName("play_day", self._CLIENT_START_TIME.day)
                self.setValByName("play_hour", self._CLIENT_START_TIME.hour)
                self.setValByName("play_minute", self._CLIENT_START_TIME.minute)
                self.setValByName("play_second", self._CLIENT_START_TIME.second)
                if self.verbose:
                    utils.Logger.toStdOut(f'{"*" * 10} {self._session_id} v{event.app_version} @ {self._CLIENT_START_TIME} {"*" * 10}')

            if self.level is not None:
                if self.level_start_timestamp.get(self.level) == None:
                    self.level_start_timestamp[self.level] = event.timestamp
                self.setValByIndex('time_in_level', self.level, event.timestamp - self.level_start_timestamp[self.level])

            self.time_since_start = self.get_time_since_start(client_time=event.timestamp)
            self.feature_count(feature_base="EventCount")
            self.setValByName(feature_name="sessDuration", new_value=self.time_since_start)
            debug_strs = []
            if event.event_data.get("save_code"):
                debug_strs.append(f"Save code: {event.event_data.get('save_code')}")
            if event.event_data.get("text"):
                debug_strs.append(f"Text: {event.event_data.get('text')}")
            if event_type_str == "wildcard_click":
                d = event.event_data
                if Event.CompareVersions(event.app_version, "4") < 0:
                    debug_strs.append(f'ans: {d.get("answer")}')
                    debug_strs.append(f'corr: {d.get("correct")}')
            self.add_debug_str(f'{self.level} {self.cur_question} {self.time_since_start} {event_type_str} {"|".join(debug_strs)}')
            # Ensure we have private data initialized for this level.
            if "click" in event_type_str or "hover" in event_type_str:
                self._extractFromClickOrHover(timestamp=event.timestamp, event_data=event.event_data)
            if "click" in event_type_str:
                self._extractFromClick(timestamp=event.timestamp, event_data=event.event_data, version=event.app_version)
            elif "hover" in event_type_str:
                self._extractFromHover(timestamp=event.timestamp, event_data=event.event_data)
            if event_type_str == "checkpoint":
                self._extractFromCheckpoint(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "quiz":
                self._extractFromQuiz(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "quizquestion":
               self._extractFromQuizquestion(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "quizstart":
                self._extractFromQuizstart(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "quizend":
                self._extractFromQuizend(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "startgame":
                self._extractFromStartgame(timestamp=event.timestamp, event_data=event.event_data, version=event.app_version)
            elif event_type_str == "endgame":
                self._extractFromEndgame(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "navigate_click":
                self._extractFromNavigate_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "notebook_click":
                self._extractFromNotebook_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "map_click":
                self._extractFromMap_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "notification_click":
                self._extractFromNotification_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "object_click":
                self._extractFromObject_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "observation_click":
                self._extractFromObservation_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "person_click":
                self._extractFromPerson_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "cutscene_click":
                self._extractFromCutscene_click(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "wildcard_click":
                self._extractFromWildcard_click(timestamp=event.timestamp, event_data=event.event_data, version=event.app_version)
            elif event_type_str == "navigate_hover":
                self._extractFromNavigate_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "notebook_hover":
                self._extractFromNotebook_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "map_hover":
                self._extractFromMap_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "notification_hover":
                self._extractFromNotification_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "object_hover":
                self._extractFromObject_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "observation_hover":
                self._extractFromObservation_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "person_hover":
                self._extractFromPerson_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "cutscene_hover":
                self._extractFromCutscene_hover(timestamp=event.timestamp, event_data=event.event_data)
            elif event_type_str == "wildcard_hover":
                self._extractFromWildcard_hover(timestamp=event.timestamp, event_data=event.event_data)

    def _extractFromClickOrHover(self, timestamp, event_data):
        time_between_click_hovers = timestamp - self.last_click_hover_time

        if time_between_click_hovers < self._IDLE_THRESH:
            active_time = time_between_click_hovers
            idle_time = timedelta(0)
        else:
            self.feature_count('count_idle')
            active_time = timedelta(0)
            idle_time = time_between_click_hovers
        self.feature_inc('time_active', active_time)
        self.feature_inc('time_idle', idle_time)


        self.last_click_hover_time = timestamp
        pass

    def _extractFromClick(self, timestamp, event_data, version):
        # assign event_data variables
        _room_fqid = event_data["room_fqid"]
        _type = event_data["type"]
        _subtype = event_data["subtype"]
        _fqid = event_data["fqid"]
        _name = event_data["name"]
        _event_custom = event_data["event_custom"]
        _screen_coor = event_data["screen_coor"]
        _room_coor = event_data["room_coor"]
        _level = event_data["level"]
        _text = event_data.get("text") if Event.CompareVersions(version, "6") == 0 and event_data.get("text") != "undefined" else None
        _text_fqid = event_data.get("text_fqid") or event_data.get("cur_cmd_fqid")

        # for all clicks, increment count clicks


        #
        if _subtype == "wildcard" and event_data.get("cur_cmd_type") == 2: # what does this mean?
            return

        def finish_text(last_time, last_text, last_interaction):
            time_diff_secs = (timestamp - last_time).microseconds / 1000000
            # record unexpected behavior
            if time_diff_secs <= 0:
                self.log_warning(f"The player read '{last_text}' in 0 seconds! (time_diff_secs = {time_diff_secs} <= 0)",3)
            else:
                # record word speed
                word_count = len(last_text.split())
                wps = word_count / time_diff_secs
                self.last_logged_text = last_text
                if not self.finished_encounters[last_interaction]:
                    # if encounter is unfinished, record encounter features
                    self.feature_inc("first_enc_words_read", word_count, interaction_num=last_interaction)
                    self.feature_inc("first_enc_boxes_read", 1, interaction_num=last_interaction)
                    self.feature_average("first_enc_avg_wps", wps, interaction_num=last_interaction)
                    self.feature_variance("first_enc_var_wps", wps, interaction_num=last_interaction)
                    self.feature_average("first_enc_avg_tbps", 1 / time_diff_secs,
                                         interaction_num=last_interaction)
                    self.feature_variance("first_enc_var_tbps", 1 / time_diff_secs,
                                          interaction_num=last_interaction)

        def new_click():
            self.feature_count(feature_base="count_clicks", objective_num=self.cur_objective)
            time_between_clicks = timestamp - self.last_click_time



            # record information on what click type and where we are in the game
            self.last_click_type = self.this_click_type
            self.this_click_type = f'{_subtype}_{_name}'
            if self.cur_interaction is not None:
                self.feature_cc_inc(self._INT_PREFIX+"total_duration", self.cur_interaction, time_between_clicks)
                if not self.finished_encounters[self.cur_interaction]:
                    self.feature_inc("first_enc_duration", time_between_clicks, interaction_num=self.cur_interaction)
            if self.cur_objective is not None:
                self.feature_cc_inc(self._OBJ_PREFIX+"time_to_next_obj", index=self.cur_objective, increment=time_between_clicks)
            self.feature_average('avg_time_between_clicks', time_between_clicks)

            if time_between_clicks < self._IDLE_THRESH:
                self.feature_inc('time_active_clicking', time_between_clicks)



            self.last_click_time = timestamp

        def new_objective(new_obj):
            # set val to 0 if not already
            if self.cur_objective is not None:
                for f in [
                    "omeaningful_action_count",
                    "onum_enc",
                    "ocount_clicks",
                    "ocount_notebook_uses",
                ]:
                    self.feature_cc_inc(f, index=self.cur_objective, increment=0)
            if not self.objective_chain_started:
                self.setValByName("sess_start_obj", new_obj)
                self.objective_chain_started = True
            self.setValByName("sess_end_obj", new_obj)
            self.cur_objective = new_obj

        def new_interaction(new_int):
            self.feature_time_since_start('time_to', cur_client_time=timestamp,
                                          interaction_num=new_int)
            self.feature_count("num_enc", interaction_num=new_int, objective_num=self.cur_objective)


            f = JowilderExtractor._OBJ_PREFIX + "next_int"
            if self.cur_objective is not None and self.getValByIndex(f, index=self.cur_objective) is None:
                self.setValByIndex(f, index=self.cur_objective, new_value=new_int)

            finish_interaction()
            self.cur_interaction = new_int

        def finish_interaction():

            self.prev_interaction = self.cur_interaction
            self.cur_interaction = None

            self.finished_encounters[self.cur_interaction] = True



        if not self.game_started:
            return

        interaction_enum = je.fqid_to_enum.get(_text_fqid)
        new_click()
        if self.last_display_time_text: # if the previous log had text
            last_time, last_text = self.last_display_time_text
            if _text == last_text:
                utils.Logger.toFile(f"The player read {last_text} twice in a row!", logging.WARNING)
            else:
                finish_text(last_time, last_text, last_interaction=self.cur_interaction)

        if _text: # if the current log has text
            if (not self.last_display_time_text) or (self.last_display_time_text[1] != _text):
                self.last_display_time_text = (timestamp, _text)
        else:
            self.last_display_time_text = ()

        if interaction_enum != self.cur_interaction: # if the current interaction has changed
            if self.cur_interaction is not None:
                finish_interaction()
            if interaction_enum is not None: # if current there is currently an interaction
                new_interaction(new_int=interaction_enum)
            if interaction_enum is not None and interaction_enum <= je.max_objective:  # if it is one of the objective interactions (0-max_obj)
                if interaction_enum != self.cur_objective and not self.finished_encounters[interaction_enum]: # if its different from the current objective
                    new_objective(new_obj=interaction_enum)

    def _extractFromHover(self, timestamp:datetime, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _start_time = d["start_time"]
        _end_time = d["end_time"]
        _name = d.get("name")
        _level = d["level"]
        _answer = d.get("answer")  # uncertain field
        _correct = d.get("correct")  # uncertain field

        # helpers
        # set class variables
        # set features
        self.feature_count(feature_base="count_hovers")

    def _extractFromCheckpoint(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromQuiz(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _questions = d["questions"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features
        for i, response in enumerate(_questions):
            self._features.setValByIndex(feature_name="quiz_response", index=i, new_value=response["response_index"])

    def _extractFromQuizquestion(self, timestamp:datetime, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _quiz_number = d["quiz_number"]
        _question = d["question"]
        _question_index = d["question_index"]
        _response = d["response"]
        _response_index = d["response_index"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        index = je.quizn_answern_to_index(_quiz_number, _question_index)
        if index%4==0:
            time_taken = timestamp - self._last_quizstart
        else:
            time_taken = timestamp - self._quiztimes[index - 1]


        # set class variables
        self._quiztimes[index] = timestamp

        # set features

        if self.getValByIndex("sa_time", index=index) in self._NULL_FEATURE_VALS:
            self.setValByIndex("sa_time", index=index, new_value=time_taken)
        self.setValByIndex("sa_index", index=index, new_value=_response_index)
        self.setValByIndex("sa_text", index=index, new_value=_response)
        self.feature_cc_inc("sa_num_answers", index=index, increment=1)

    def _extractFromQuizstart(self, timestamp:datetime, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _quiz_number = d["quiz_number"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        assert self._last_quizstart is None
        self._last_quizstart = timestamp
        # set class variables
        # set features

    def _extractFromQuizend(self, timestamp:datetime, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _quiz_number = d["quiz_number"]
        _name = d["name"]
        _level = d["level"]




        # helpers

        assert self._last_quizstart is not None
        quiz_duration = timestamp - self._last_quizstart
        quiz_index = je.quizn_to_index(_quiz_number)


        # set class variables
        self._last_quizstart = None

        # set features
        self.setValByIndex(feature_name='s_time', index=quiz_index, new_value=quiz_duration)

    def _extractFromStartgame(self, timestamp, event_data, version):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _save_code = d["save_code"]
        _fullscreen = d["fullscreen"]
        _music = d["music"]
        _hq = d["hq"]
        _name = d["name"]
        _level = d["level"]


        # helpers
        # set class variables
        # set features
        if self.game_started:
            self.log_warning(message='Player had a second startgame event!', version=version)
            self.halt = True
            return
        self.setValByName('fullscreen', int(_fullscreen))
        self.setValByName('music', int(_music))
        self.setValByName('hq', int(_hq))
        self.setValByName('save_code', _save_code)
        self.setValByName("continue", 0)

        if Event.CompareVersions(version, "7") >= 0:
            _script_type = d["script_type"]
            _script_version = d["script_version"]
            self.setValByName("script_type", _script_type)
            self.setValByName("script_version", _script_version)

        self.game_started = True

    def _extractFromEndgame(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromNavigate_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _level = d["level"]

        if _fqid != 0:
            self.feature_count('meaningful_action_count', objective_num=self.cur_objective)

        # helpers
        # set class variables
        # set features

    def _extractFromNotebook_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _page = d["page"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features
        if d.get("name") == "open":
            self.feature_inc(feature_base="count_notebook_uses", increment=1, objective_num=self.cur_objective)

    def _extractFromMap_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features
        if _fqid != 0:
            self.feature_count('meaningful_action_count')

    def _extractFromNotification_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromObject_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromObservation_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromPerson_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromCutscene_click(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromWildcard_click(self, timestamp, event_data, version):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _name = d["name"]
        _level = d["level"]
        # v4-
        _correct = d.get("correct")  # v4- only
        _answer = d.get("answer")  # v4- only
        # v6+
        _cur_cmd_fqid = d.get("cur_cmd_fqid")  # v6+ only
        _cur_cmd_type = d.get("cur_cmd_type")  # v6+ only
        _text = d.get("text")  # v6+ only
        _interacted_fqid = d.get("interacted_fqid")  # v6+ only

        # if self.cur_question > 18:
        #     self.log_warning(f'Question {self.cur_question} > max (18)!')
        #     return

        # answer = _cur_cmd_fqid if _cur_cmd_type==2 else _answer or None
        # correct = _interacted_fqid if _cur_cmd_type==2 else _answer or None

        # if event.app_version == 4:
        #
        #     # helpers
        #     click = bool(answer)
        #     wrong_guess = click and (answer != correct)
        #     if correct == 'HACKME':
        #         wrong_guess = answer in ['tunic.entry_basketballplaque', 'tunic.entry_cleanerslip']
        #
        #     answer_char = je.interactive_entry_to_char(answer) if click else ''
        #     prev_answers = self.getValByIndex('answers', self.cur_question)
        #     if prev_answers in JowilderExtractor._NULL_FEATURE_VALS:
        #         self.setValByIndex('answers', self.cur_question, '')
        #         prev_answers = ''
        #
        #     # set class variables
        #
        #     # set features
        #     if wrong_guess:
        #         self.feature_cc_inc('num_wrong_guesses',self.cur_question, 1)
        #     self.features.setValByIndex('answers', self.cur_question, prev_answers + answer_char)
        #
        #     if click and not wrong_guess:
        #         self.cur_question += 1
        #
        # # elif event.app_version == 6:
        # #     click = bool(_interacted_fqid)
        # #     wrong_guess = click and (_)

        def set_answer_features():
            self.feature_cc_inc('num_guesses', self.cur_question, 1)
            incorrect = "fail" in _cur_cmd_fqid
            self.add_debug_str(f'Q{self.cur_question} chose {self.chosen_answer} ({"in" if incorrect else ""}correct)')
            answer_char = je.interactive_entry_to_char(self.chosen_answer)
            if self.cur_question in [10,16] and incorrect and answer_char == je._answer_chars[self.cur_question]:
                answer_char = '?'
            prev_answers : str = self.getValByIndex('answers', self.cur_question)
            if prev_answers in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByIndex('answers', self.cur_question, '')
                prev_answers = ''
            self.setValByIndex('answers', self.cur_question, prev_answers + answer_char)
            answer_number = len(prev_answers) + 1
            if answer_number <= 3:
                self.setValByIndex(f'A{answer_number}', self.cur_question, answer_char)
                self.setValByIndex(f'A{answer_number}_time', self.cur_question, timestamp - self.time_before_answer)


            # got_correct_ans = _cur_cmd_fqid == self.chosen_answer
            # if self.chosen_answer == 'HACKME':
            #     got_correct_ans = self.chosen_answer in ['tunic.entry_basketballplaque', 'tunic.entry_cleanerslip']
            # if not got_correct_ans:
            #     self.feature_cc_inc('num_wrong_guesses', cur_question, 1)


        if Event.CompareVersions(version, "6") == 0:
            if _cur_cmd_type == 2:
                self.cur_question = je.answer_to_question(_cur_cmd_fqid,self.level)
                self.chosen_answer = _interacted_fqid
            elif _cur_cmd_type == 1:
                if self.chosen_answer:
                    set_answer_features()
                    self.chosen_answer = None
                self.time_before_answer = timestamp




        # set features

    def _extractFromNavigate_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _start_time = d["start_time"]
        _end_time = d["end_time"]
        _name = d.get("name")
        _level = d["level"]
        _answer = d.get("answer")  # uncertain field
        _correct = d.get("correct")  # uncertain field

        # helpers
        # set class variables
        # set features

    def _extractFromNotebook_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromMap_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _start_time = d["start_time"]
        _end_time = d["end_time"]
        _name = d["name"]
        _level = d["level"]

        # helpers
        # set class variables
        # set features

    def _extractFromNotification_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromObject_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _start_time = d["start_time"]
        _end_time = d["end_time"]
        _level = d["level"]
        _name = d.get("name")  # uncertain field

        # helpers
        # set class variables
        # set features

    def _extractFromObservation_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromPerson_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromCutscene_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromWildcard_hover(self, timestamp, event_data):
        # assign event_data variables
        d = event_data
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _start_time = d["start_time"]
        _end_time = d["end_time"]
        _name = d.get("name")  # uncertain field
        _level = d["level"]
        # v4-
        _correct = d.get("correct")  # v4- only
        _answer = d.get("answer")  # v4- only
        # v6+
        _cur_cmd_fqid = d.get("cur_cmd_fqid")  # v6+ only
        _cur_cmd_type = d.get("cur_cmd_type")  # v6+ only
        _text = d.get("text")  # v6+ only
        _interacted_fqid = d.get("interacted_fqid")  # v6+ only

        if self.cur_question in [10,16] and self.chosen_answer and _interacted_fqid:
            utils.Logger.toFile(f'During Jowilder Q{self.cur_question}, player chose {self.chosen_answer} '
                                f'but accidentally hovered over {_interacted_fqid}, choosing that on accident.', logging.WARNING)
            self.chosen_answer = _interacted_fqid

        # helpers
        # set class variables
        # set features

    def new_level(self, old_level):
        if self.level > self.getValByName('max_level'):
            self.setValByName('max_level', self.level)
        if old_level is None:
            self.setValByName('start_level', self.level)
            if self.level != 0 and not self.getValByName("save_code"):
                    self.setValByName("continue", 1)

        self._set_value_in_cur_levels('count_notebook_uses',0)
        self._set_value_in_cur_levels('count_hovers', 0)

        for obj in range(je.level_to_start_obj[self.level]):
            self.finished_encounters[obj] = True

    def CalculateAggregateFeatures(self):
        pass

    # def feature_time_since_start(self, feature_name, cur_client_time):
    #     """
    #     Sets a session time since start feature. Will not write over a feature that has already been set.
    #     :param feature_base: name of feature without sess or level prefix
    #     :param cur_client_time: client time at which the event happened
    #     """
    #     if self.getValByName(feature_name) in JowilderExtractor._NULL_FEATURE_VALS:
    #         self.setValByName(feature_name=feature_name, new_value=self.time_since_start(cur_client_time))



    def get_time_since_start(self, client_time):
        return client_time - self._CLIENT_START_TIME

    def feature_average(self, fname_base, value, interaction_num=None):
        if value is None:
            return
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        level_feature, session_feature = lvl_pref + fname_base, sess_pref + fname_base
        for lvl in self._cur_levels:
            if not self.average_handler_level[level_feature][lvl]['total']:
                self.average_handler_level[level_feature][lvl]['total'] = self._get_default_val(level_feature)
            self.average_handler_level[level_feature][lvl]['total'] += value
            self.average_handler_level[level_feature][lvl]['n'] += 1
            avg = self.average_handler_level[level_feature][lvl]['total'] / \
                  self.average_handler_level[level_feature][lvl]['n']
            self.setValByIndex(level_feature, lvl, avg)

        if not self.average_handler_session[session_feature]['total']:
            self.average_handler_session[session_feature]['total'] = self._get_default_val(session_feature)
        self.average_handler_session[session_feature]['total'] += value
        self.average_handler_session[session_feature]['n'] += 1
        avg = self.average_handler_session[session_feature]['total'] / self.average_handler_session[session_feature][
            'n']
        self.setValByName(session_feature, avg)

        if interaction_num is not None:
            int_feature = JowilderExtractor._INT_PREFIX + fname_base
            if not self.average_handler_interaction[int_feature][interaction_num]['total']:
                self.average_handler_interaction[int_feature][interaction_num]['total'] = self._get_default_val(int_feature)
            self.average_handler_interaction[int_feature][interaction_num]['total'] += value
            self.average_handler_interaction[int_feature][interaction_num]['n'] += 1
            avg = self.average_handler_interaction[int_feature][interaction_num]['total'] / \
                  self.average_handler_interaction[int_feature][interaction_num]['n']
            self.setValByIndex(int_feature, interaction_num, avg)

    def feature_variance(self, fname_base, value, interaction_num=None):
        """
        This function can be redone to reduce memory usage at the expense of some (perhaps minimal accuracy along the form
        of (from wikipedia):
        K = n = Ex = Ex2 = 0.0

        def add_variable(x):
            if (n == 0):
                K = x
            n = n + 1
            Ex += x - K
            Ex2 += (x - K) * (x - K)

        def remove_variable(x):
            n = n - 1
            Ex -= (x - K)
            Ex2 -= (x - K) * (x - K)

        def get_meanvalue():
            return K + Ex / n

        def get_variance():
            return (Ex2 - (Ex * Ex) / n) / (n - 1)

        :param fname_base:
        :param value:
        :param interaction_num:
        :return:
        """
        def variance(l):
            N = len(l)
            if N == 0:
                return None
            Ex = sum(l)
            Ex2 = sum([x*x for x in l])
            mean_sq = (Ex/N)*(Ex/N)
            mean_x2 = Ex2/N
            return mean_x2 - mean_sq

        if value is None:
            return
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        level_feature, session_feature = lvl_pref + fname_base, sess_pref + fname_base
        for lvl in self._cur_levels:
            self.variance_handler_level[level_feature][lvl] += [value]
            var = variance(self.variance_handler_level[level_feature][lvl])
            self.setValByIndex(level_feature, lvl, var)

        self.variance_handler_session[session_feature] += [value]
        var = variance(self.variance_handler_session[session_feature])
        self.setValByName(session_feature, var)

        if interaction_num is not None:
            int_feature = JowilderExtractor._INT_PREFIX + fname_base
            self.variance_handler_interaction[int_feature][interaction_num] += [value]
            self.setValByIndex(int_feature, interaction_num, variance(self.variance_handler_interaction[int_feature][interaction_num]))


    def feature_count(self, feature_base, interaction_num=None, objective_num=None):
        self.feature_inc(feature_base=feature_base, increment=1, interaction_num=interaction_num,
                         objective_num=objective_num)

    # Helper function to increment both the per-level and full-session values of corresponding features.
    # Takes a base name common to the per-level and full-session features, adds a prefix to each,
    # and increments each by given increment.
    def feature_inc(self, feature_base, increment, interaction_num=None, objective_num=None):
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        self._increment_feature_in_cur_levels(feature_name=lvl_pref + feature_base, increment=increment)
        self._increment_sess_feature(feature_name=sess_pref + feature_base, increment=increment)
        if interaction_num is not None:
            self.feature_cc_inc(JowilderExtractor._INT_PREFIX+feature_base, interaction_num, increment)
        if objective_num is not None:
            self.feature_cc_inc(JowilderExtractor._OBJ_PREFIX+feature_base, objective_num, increment)


    def feature_cc_inc(self, feature_name, index, increment):
        if index is None:
            return
        if self.getValByIndex(feature_name=feature_name, index=index) in JowilderExtractor._NULL_FEATURE_VALS:
            self.setValByIndex(feature_name, index=index, new_value=self._get_default_val(feature_name))
        self._features.incValByIndex(feature_name=feature_name, index=index, increment=increment)

    def feature_time_since_start(self, feature_base, cur_client_time, interaction_num=None):
        """
        Sets a session time since start feature. Will not write over a feature that has already been set.
        :param feature_base: name of feature without sess or level prefix
        :param cur_client_time: client time at which the event happened
        """

        if interaction_num is not None:
            feature_name = JowilderExtractor._INT_PREFIX + feature_base
            if self.getValByIndex(feature_name, interaction_num) in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByIndex(feature_name=feature_name, new_value=self.get_time_since_start(cur_client_time),
                               index=interaction_num)
        else:
            feature_name = JowilderExtractor._SESS_PREFIX + feature_base
            if self.getValByName(feature_name) in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByName(feature_name=feature_name, new_value=self.get_time_since_start(cur_client_time))

    def feature_max_min(self, fname_base, val):
        """feature must have the same fname_base that gets put on the following four features:
        - {_SESS_PREFIX}max_
        - {_SESS_PREFIX}min_
        - {_LEVEL_PREFIX}max_
        - {_LEVEL_PREFIX}min_ """

        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        self._set_feature_max_in_cur_levels(feature_name=lvl_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_cur_levels(feature_name=lvl_pref + "min_" + fname_base, val=val)
        self._set_feature_max_in_session(feature_name=sess_pref + "max_" + fname_base, val=val)
        self._set_feature_min_in_session(feature_name=sess_pref + "min_" + fname_base, val=val)

    def _increment_feature_in_cur_levels(self, feature_name, increment=None):
        if increment is None:
            increment = 1
        for lvl in self._cur_levels:
            if self.getValByIndex(feature_name=feature_name, index=lvl) in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByIndex(feature_name, index=lvl, new_value=self._get_default_val(feature_name))
            self._features.incValByIndex(feature_name=feature_name, index=lvl, increment=increment)

    def _increment_sess_feature(self, feature_name, increment=None):
        if increment is None:
            increment = 1
        if self.getValByName(feature_name) in JowilderExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name, new_value=self._get_default_val(feature_name))
        self._features.incAggregateVal(feature_name=feature_name, increment=increment)


    def _set_value_in_cur_levels(self, feature_name, value):
        for lvl in self._cur_levels:
            self.setValByIndex(feature_name=feature_name, index=lvl, new_value=value)

    def _set_feature_max_in_cur_levels(self, feature_name, val):
        for lvl in self._cur_levels:
            prev_val = self.getValByIndex(feature_name=feature_name, index=lvl)
            if prev_val in JowilderExtractor._NULL_FEATURE_VALS or val > prev_val:
                self.setValByIndex(feature_name=feature_name, index=lvl, new_value=val)

    def _set_feature_min_in_cur_levels(self, feature_name, val):
        for lvl in self._cur_levels:
            prev_val = self.getValByIndex(feature_name=feature_name, index=lvl)
            if prev_val in JowilderExtractor._NULL_FEATURE_VALS or val < prev_val:
                self.setValByIndex(feature_name=feature_name, index=lvl, new_value=val)

    def _set_feature_max_in_session(self, feature_name, val):
        prev_val = self.getValByName(feature_name=feature_name)
        if prev_val in JowilderExtractor._NULL_FEATURE_VALS or val > prev_val:
            self.setValByName(feature_name=feature_name, new_value=val)

    def _set_feature_min_in_session(self, feature_name, val):
        prev_val = self.getValByName(feature_name=feature_name)
        if prev_val in JowilderExtractor._NULL_FEATURE_VALS or val < prev_val:
            self.setValByName(feature_name=feature_name, new_value=val)

    def _get_default_val(self, feature_name) -> Union[float,timedelta,int]:
        startswith = lambda prefix: feature_name.startswith(JowilderExtractor._SESS_PREFIX+prefix) or \
            feature_name.startswith(JowilderExtractor._LEVEL_PREFIX+prefix)
        if startswith('min_'):
            return float('inf')
        if 'time' in feature_name.lower() or 'duration' in feature_name.lower():
            return timedelta(0)
        else:
            return 0

    def getValByName(self, feature_name):
        return self._features.getValByName(feature_name)

    def setValByName(self, feature_name, new_value):
        self._features.setValByName(feature_name, new_value)

    def getValByIndex(self, feature_name, index):
        return self._features.getValByIndex(feature_name, index)

    def setValByIndex(self, feature_name, index, new_value):
        self._features.setValByIndex(feature_name, index, new_value)


    def get_debug_string(self, version:Union[str,None], num_lines=20):
        ret = [f'{"*" * 10} {self._session_id} v{version} @ {self._CLIENT_START_TIME} {"*"*10}']
        ret.extend(deque(self.debug_strs, num_lines))
        return '\n'.join(ret)

    def add_debug_str(self, s):
        self.debug_strs.append(s)
        if self.verbose:
            utils.Logger.toStdOut(s)
    
    def log_warning(self, message, version, num_lines=20):
        self.add_debug_str('WARNING: '+message)
        debug_str = '\n\n'+self.get_debug_string(version=version, num_lines=num_lines+1)
        utils.Logger.toFile(debug_str, logging.WARNING)
        self.debug_strs = []
        
        

