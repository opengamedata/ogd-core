## import standard libraries
import bisect
import json
import logging
import math
import typing
import datetime
import sys
import traceback
from collections import defaultdict, deque
## import local files
import utils
import numpy as np
from sklearn.linear_model import LinearRegression
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema
from game_info.Jowilder import Jowilder_Enumerators as je

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
# TODO: Some FQIDs are called HACKME and are placeholders
class JowilderExtractor(Extractor):
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
         21: 'quiz'
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

    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)
        self.cur_task = 1
        self.time_since_start = datetime.timedelta(0)
        self._task_complete_helper = dict()
        self.level_start_timestamp = dict()
        self._CLIENT_START_TIME = None
        self.setValByName(feature_name="sessionID", new_value=session_id)
        self.level = 0
        self._cur_levels = [self.level]
        self.cur_question = 0
        self._VERSION = None
        self.last_display_time_text = ()
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
        self.text_fqid_start_end = []
        self.last_click_type = ''
        self.this_click_type = ''
        self.cur_question = 0
        self.chosen_answer = ''
        self.prev_interaction = None
        self.cur_interaction = None
        self.next_objective = None
        self.cur_objective = None
        self.finished_encounters = defaultdict(lambda: False)



    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        try:
            self._extractFromRow(row_with_complex_parsed, game_table)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for place in [utils.Logger.toFile, utils.Logger.toStdOut]:
                place('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)), logging.ERROR)
                place('DEBUG STRINGS:', logging.ERROR)
                place(self.get_debug_string(num_lines=20), logging.ERROR)

            

    def _extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        # put some data in local vars, for readability later.
        old_level = self.level
        self.level = row_with_complex_parsed[game_table.level_index]
        self._cur_levels = [self.level]
        self.setValByName('max_level', self.level)
        if not old_level == self.level:
            self.new_level()
        event_data_complex_parsed = row_with_complex_parsed[game_table.complex_data_index]
        event_type = row_with_complex_parsed[game_table.event_custom_index]
        event_client_time = row_with_complex_parsed[game_table.client_time_index].replace(microsecond=
                                                    row_with_complex_parsed[game_table.client_time_ms_index]*1000)
        server_time = row_with_complex_parsed[game_table.server_time_index]
        event_type_str = JowilderExtractor._EVENT_CUSTOM_TO_STR[event_type].lower()
        # Check for invalid row.
        row_sess_id = row_with_complex_parsed[game_table.session_id_index]
        if row_sess_id != self.session_id:
            utils.Logger.toFile(
                f"Got a row with incorrect session id! Expected {self.session_id}, got {row_sess_id}!",
                logging.ERROR)
        elif "event_custom" not in event_data_complex_parsed.keys():
            utils.Logger.toFile("Invalid event_data_complex, does not contain event_custom field!", logging.ERROR)
        # If row is valid, process it.
        else:
            # If we haven't set persistent id, set now.
            if self.getValByName(feature_name="persistentSessionID") == 0:
                self.setValByName(feature_name="persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            if not self._CLIENT_START_TIME:
                # initialize this time as the start
                self._CLIENT_START_TIME = event_client_time
                self._VERSION = row_with_complex_parsed[game_table.version_index]

            if self.level_start_timestamp.get(self.level) == None:
                self.level_start_timestamp[self.level] = event_client_time
            self.setValByIndex('time_in_level', self.level, event_client_time - self.level_start_timestamp[self.level])

            self.time_since_start = self.get_time_since_start(client_time=event_client_time)
            self.feature_count(feature_base="EventCount")
            self.setValByName(feature_name="sessDuration", new_value=self.time_since_start)
            debug_strs = []
            if event_data_complex_parsed.get("text"):
                debug_strs.append("Text: "+event_data_complex_parsed.get("text"))
            if event_type_str == "wildcard_click":
                d = event_data_complex_parsed
                if self._VERSION <= 4:
                    debug_strs.append(f'ans: {d.get("answer")}')
                    debug_strs.append(f'corr: {d.get("correct")}')
            self.add_debug_str(f'{self.level} {self.cur_question} {self.time_since_start} {event_type_str} {"|".join(debug_strs)}')
            # Ensure we have private data initialized for this level.
            if "click" in event_type_str or "hover" in event_type_str:
                self._extractFromClickOrHover(event_client_time, event_data_complex_parsed)
            if "click" in event_type_str:
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif "hover" in event_type_str:
                self._extractFromHover(event_client_time, event_data_complex_parsed)
            if event_type_str == "checkpoint":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
            elif event_type_str == "quiz":
                self._extractFromQuiz(event_client_time, event_data_complex_parsed)
            elif event_type_str == "startgame":
                self._extractFromStartgame(event_client_time, event_data_complex_parsed)
            elif event_type_str == "endgame":
                self._extractFromEndgame(event_client_time, event_data_complex_parsed)
            elif event_type_str == "navigate_click":
                self._extractFromNavigate_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "notebook_click":
                self._extractFromNotebook_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "map_click":
                self._extractFromMap_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "notification_click":
                self._extractFromNotification_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "object_click":
                self._extractFromObject_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "observation_click":
                self._extractFromObservation_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "person_click":
                self._extractFromPerson_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "cutscene_click":
                self._extractFromCutscene_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "wildcard_click":
                self._extractFromWildcard_click(event_client_time, event_data_complex_parsed)
            elif event_type_str == "navigate_hover":
                self._extractFromNavigate_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "notebook_hover":
                self._extractFromNotebook_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "map_hover":
                self._extractFromMap_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "notification_hover":
                self._extractFromNotification_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "object_hover":
                self._extractFromObject_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "observation_hover":
                self._extractFromObservation_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "person_hover":
                self._extractFromPerson_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "cutscene_hover":
                self._extractFromCutscene_hover(event_client_time, event_data_complex_parsed)
            elif event_type_str == "wildcard_hover":
                self._extractFromWildcard_hover(event_client_time, event_data_complex_parsed)

    def _extractFromClickOrHover(self, event_client_time, event_data_complex_parsed):
        pass

    def _extractFromClick(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _name = d["name"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _level = d["level"]
        _text = d.get("text") if self._VERSION == 6 and d.get("text") != "undefined" else None
        _text_fqid = d.get("text_fqid")

        self.last_click_type = self.this_click_type
        self.this_click_type = f'{_subtype}_{_name}'
        self.prev_interaction = self.cur_interaction or self.prev_interaction
        self.cur_interaction = je.fqid_to_enum.get(_text_fqid)
        self.feature_count(feature_base="count_clicks")
        if self.last_click_time:
            self.feature_average('avg_time_between_clicks',event_client_time - self.last_click_time)
        self.last_click_time = event_client_time

        if _subtype == "wildcard" and d.get("cur_cmd_type") == 2:
            return

        # # helpers
        wps = None
        word_count = None
        time_diff_secs = None
        if self.last_display_time_text:
            last_time, last_text = self.last_display_time_text
            time_diff_secs = (event_client_time - last_time).total_seconds()
            if last_text == self.last_logged_text:
                utils.Logger.toFile(f"The player read {last_text} twice in a row.", logging.WARN)
            elif time_diff_secs <= 0:
                self.log_warning(f"The player read '{last_text}' in 0 seconds! (time_diff_secs = {time_diff_secs} <= 0)",3)
            else:
                word_count = len(last_text.split())
                wps = word_count / time_diff_secs
                self.last_logged_text = last_text

        # clicked_fqid = _room_fqid + _fqid
        # completed_task = 0
        # if JowilderExtractor[self.cur_task] == clicked_fqid:
        #     completed_task = self.cur_task
        #     self.cur_task += 1
        
        # set class variables
        if _text:
            if (not self.last_display_time_text) or (self.last_logged_text != _text):
                self.last_display_time_text = (event_client_time, _text)
        else:
            self.last_display_time_text = ()

        if self.text_fqid_start_end and self.text_fqid_start_end[0] != _text_fqid:
            self.feature_average('avgTimePerTextBox', self.text_fqid_start_end[2] - self.text_fqid_start_end[1])
            self.text_fqid_start_end = []
        if _text_fqid:
            if not self.text_fqid_start_end:
                self.text_fqid_start_end = [_text_fqid, event_client_time, event_client_time]
            elif _text_fqid == self.text_fqid_start_end[0]:
                self.text_fqid_start_end[2] = event_client_time

        # feature helpers
        # def set_task_finished(completed_task):
        #     self._task_complete_helper[completed_task] = event_client_time
        #     if not completed_task:
        #         return
        #     if completed_task == 1:
        #         time_to_complete = datetime.timedelta(0)
        #     else:
        #         prev_complete_time = self._task_complete_helper[completed_task-1]
        #         time_to_complete = event_client_time - prev_complete_time
        #     feature_name = 'time_to_complete_task_'+completed_task
        #     self.setValByName(feature_name=feature_name, new_value=time_to_complete)
        # # set features
        # set_task_finished(completed_task)
        if self.cur_interaction is not None:
            self.feature_time_since_start('time_to', cur_client_time=event_client_time,
                                          interaction_num=self.cur_interaction)
        if self.prev_interaction != self.cur_interaction:
            self.feature_count("num_enc", self.cur_interaction)
        if not self.finished_encounters[self.prev_interaction] and word_count is not None:
            self.feature_inc("first_enc_words_read", word_count, interaction_num=self.prev_interaction)
            self.feature_inc("first_enc_boxes_read", 1, interaction_num=self.prev_interaction)
            self.feature_inc("first_enc_duration", time_diff_secs, interaction_num=self.prev_interaction)
            self.feature_average("first_enc_avg_wps", wps, interaction_num=self.prev_interaction)
            self.feature_variance("first_enc_var_wps", wps, interaction_num=self.prev_interaction)
            self.feature_average("first_enc_avg_tbps", 1/time_diff_secs, interaction_num=self.prev_interaction)
            self.feature_variance("first_enc_var_tbps", 1/time_diff_secs, interaction_num=self.prev_interaction)

        self.feature_average(fname_base='words_per_second', value=wps)

        if self.prev_interaction is not None and self.prev_interaction != self.cur_interaction:
            self.finished_encounters[self.prev_interaction] = True


    def _extractFromHover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromCheckpoint(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromQuiz(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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
            self.features.setValByIndex(feature_name="quiz_response", index=i, new_value=response["response_index"])

    def _extractFromStartgame(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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
        self.setValByName('fullscreen', _fullscreen)
        self.setValByName('music', _music)
        self.setValByName('hq', _hq)
        self.setValByName('save_code', _save_code)


    def _extractFromEndgame(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromNavigate_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        _room_fqid = d["room_fqid"]
        _type = d["type"]
        _subtype = d["subtype"]
        _fqid = d["fqid"]
        _event_custom = d["event_custom"]
        _screen_coor = d["screen_coor"]
        _room_coor = d["room_coor"]
        _level = d["level"]

        if _fqid != 0:
            self.feature_count('meaningful_action_count')

        # helpers
        # set class variables
        # set features

    def _extractFromNotebook_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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
            self.feature_inc(feature_base="count_notebook_uses", increment=1)

    def _extractFromMap_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromNotification_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromObject_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromObservation_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromPerson_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromCutscene_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromWildcard_click(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

        # if self._VERSION == 4:
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
        # # elif self._VERSION == 6:
        # #     click = bool(_interacted_fqid)
        # #     wrong_guess = click and (_)

        def set_answer_features():
            self.feature_cc_inc('num_guesses', self.cur_question, 1)
            incorrect = "fail" in _cur_cmd_fqid
            self.add_debug_str(f'Q{self.cur_question} chose {self.chosen_answer} ({"in" if incorrect else ""}correct)')
            answer_char = je.interactive_entry_to_char(self.chosen_answer)
            if self.cur_question in [10,16] and incorrect and answer_char == je._answer_chars[self.cur_question]:
                answer_char = '?'
            prev_answers = self.getValByIndex('answers', self.cur_question)
            if prev_answers in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByIndex('answers', self.cur_question, '')
                prev_answers = ''
            self.setValByIndex('answers', self.cur_question, prev_answers + answer_char)
            answer_number = len(prev_answers) + 1
            if answer_number <= 3:
                self.setValByIndex(f'A{answer_number}', self.cur_question, answer_char)
                self.setValByIndex(f'A{answer_number}_time', self.cur_question, event_client_time - self.time_before_answer)


            # got_correct_ans = _cur_cmd_fqid == self.chosen_answer
            # if self.chosen_answer == 'HACKME':
            #     got_correct_ans = self.chosen_answer in ['tunic.entry_basketballplaque', 'tunic.entry_cleanerslip']
            # if not got_correct_ans:
            #     self.feature_cc_inc('num_wrong_guesses', cur_question, 1)


        if self._VERSION == 6:
            if _cur_cmd_type == 2:
                self.cur_question = je.answer_to_question(_cur_cmd_fqid,self.level)
                self.chosen_answer = _interacted_fqid
            elif _cur_cmd_type == 1:
                if self.chosen_answer:
                    set_answer_features()
                    self.chosen_answer = None
                self.time_before_answer = event_client_time




        # set features


    def _extractFromNavigate_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromNotebook_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromMap_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromNotification_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromObject_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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

    def _extractFromObservation_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromPerson_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromCutscene_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
        # no data - likely not a used event

        # helpers
        # set class variables
        # set features

    def _extractFromWildcard_hover(self, event_client_time, event_data_complex_parsed):
        # assign event_data_complex_parsed variables
        d = event_data_complex_parsed
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
                                f'but accidentally hovered over {_interacted_fqid}, choosing that on accident.', logging.WARN)
            self.chosen_answer = _interacted_fqid

        # helpers
        # set class variables
        # set features

    def new_level(self):
        self._set_value_in_cur_levels('count_notebook_uses',0)

    def calculateAggregateFeatures(self):
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

        self.variance_handler_session[level_feature] += [value]
        var = variance(self.variance_handler_session[session_feature])
        self.setValByName(session_feature, var)

        if interaction_num is not None:
            int_feature = JowilderExtractor._INT_PREFIX + fname_base
            self.variance_handler_interaction[int_feature][interaction_num] += [value]
            self.setValByIndex(int_feature, interaction_num, variance(self.variance_handler_interaction[int_feature][interaction_num]))


    def feature_count(self, feature_base, interaction_num=None):
        self.feature_inc(feature_base=feature_base, increment=1, interaction_num=interaction_num)

    # Helper function to increment both the per-level and full-session values of corresponding features.
    # Takes a base name common to the per-level and full-session features, adds a prefix to each,
    # and increments each by given increment.
    def feature_inc(self, feature_base, increment, interaction_num=None):
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        self._increment_feature_in_cur_levels(feature_name=lvl_pref + feature_base, increment=increment)
        self._increment_sess_feature(feature_name=sess_pref + feature_base, increment=increment)
        if interaction_num is not None:
            self.feature_cc_inc(JowilderExtractor._INT_PREFIX+feature_base, interaction_num, increment)


    def feature_cc_inc(self, feature_name, index, increment):
        if self.getValByIndex(feature_name=feature_name, index=index) in JowilderExtractor._NULL_FEATURE_VALS:
            self.setValByIndex(feature_name, index=index, new_value=self._get_default_val(feature_name))
        self.features.incValByIndex(feature_name=feature_name, index=index, increment=increment)

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
        increment = increment or 1
        for lvl in self._cur_levels:
            if self.getValByIndex(feature_name=feature_name, index=lvl) in JowilderExtractor._NULL_FEATURE_VALS:
                self.setValByIndex(feature_name, index=lvl, new_value=self._get_default_val(feature_name))
            self.features.incValByIndex(feature_name=feature_name, index=lvl, increment=increment)

    def _increment_sess_feature(self, feature_name, increment=None):
        increment = increment or 1
        if self.getValByName(feature_name) in JowilderExtractor._NULL_FEATURE_VALS:
            self.setValByName(feature_name, new_value=self._get_default_val(feature_name))
        self.features.incAggregateVal(feature_name=feature_name, increment=increment)


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

    def _get_default_val(self, feature_name):
        startswith = lambda prefix: feature_name.startswith(JowilderExtractor._SESS_PREFIX+prefix) or \
            feature_name.startswith(JowilderExtractor._LEVEL_PREFIX+prefix)
        if startswith('min_'):
            return float('inf')
        if 'time' in feature_name.lower():
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


    def get_debug_string(self, num_lines=20):
        ret = [f'{"*" * 10} {self.session_id} v{self._VERSION} @ {self._CLIENT_START_TIME} {"*"*10}']
        ret.extend(deque(self.debug_strs, num_lines))
        return '\n'.join(ret)

    def add_debug_str(self, s):
        self.debug_strs.append(s)
    
    def log_warning(self, message, num_lines=20):
        self.add_debug_str('WARNING: '+message)
        debug_str = '\n\n'+self.get_debug_string(num_lines+1)
        utils.Logger.toFile(debug_str, logging.WARN)
        self.debug_strs = []
        
        

