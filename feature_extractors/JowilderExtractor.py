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
        self.average_handler_session = defaultdict(lambda: {'n': 0, 'total': 0})
        self.debug_strs = []
        self.last_logged_text = None
        self.made_choice = False



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
        self.level = row_with_complex_parsed[game_table.level_index]
        self._cur_levels = [self.level]
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
                if self._VERSION == 6:
                    debug_strs.append(f'ans: {d.get("interacted_fqid") if d.get("cur_cmd_type")==2 else None}')
                    debug_strs.append(f'corr: {d.get("cur_cmd_fqid") if d.get("cur_cmd_type")==2 else None}')  # v6+ only
                    debug_strs.append(f'type: {d.get("cur_cmd_type")}')
            self.add_debug_str(f'{self.level} {self.cur_question} {self.time_since_start} {event_type_str} {"|".join(debug_strs)}')
            # Ensure we have private data initialized for this level.
            if "click" in event_type_str:
                self._extractFromClick(event_client_time, event_data_complex_parsed)
            elif "hover" in event_type_str:
                self._extractFromHover(event_client_time, event_data_complex_parsed)
            if event_type_str == "checkpoint":
                self._extractFromCheckpoint(event_client_time, event_data_complex_parsed)
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

    def _extractFromClick(self, event_client_time, event_data_complex_parsed):
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
        _text = d.get("text") if self._VERSION == 6 and d.get("text") != "undefined" else None

        self.feature_count(feature_base="count_clicks")
        if _subtype == "wildcard" and d.get("cur_cmd_type") == 2:
            return

        # # helpers
        wps = None
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

        self.feature_average(fname_base='words_per_second', value=wps)


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

        if self._VERSION == 6:
            choice = _cur_cmd_type == 2
            if choice and _interacted_fqid and not self.made_choice:
                self.made_choice = True
                got_correct_ans = _cur_cmd_fqid == _interacted_fqid
                if _interacted_fqid == 'HACKME':
                    got_correct_ans = _interacted_fqid in ['tunic.entry_basketballplaque', 'tunic.entry_cleanerslip']
                answer_char = je.interactive_entry_to_char(_interacted_fqid)
                cur_question = je.answer_to_question(_cur_cmd_fqid)
                prev_answers = self.getValByIndex('answers', cur_question)
                if prev_answers in JowilderExtractor._NULL_FEATURE_VALS:
                    self.setValByIndex('answers', cur_question, '')
                    prev_answers = ''
                if not got_correct_ans:
                    self.feature_cc_inc('num_wrong_guesses', cur_question, 1)
                self.setValByIndex('answers', cur_question, prev_answers + answer_char)
            elif not choice:
                self.made_choice = False





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

        # helpers
        # set class variables
        # set features

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
    
    def feature_average(self, fname_base, value):
        if value is None:
            return
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        level_feature, session_feature = lvl_pref + fname_base, sess_pref + fname_base
        for lvl in self._cur_levels:
            self.average_handler_level[level_feature][lvl]['total'] += value
            self.average_handler_level[level_feature][lvl]['n'] += 1
            avg = self.average_handler_level[level_feature][lvl]['total'] / \
                  self.average_handler_level[level_feature][lvl]['n']
            self.setValByIndex(level_feature, lvl, avg)

        self.average_handler_session[session_feature]['total'] += value
        self.average_handler_session[session_feature]['n'] += 1
        avg = self.average_handler_session[session_feature]['total'] / self.average_handler_session[session_feature][
            'n']
        self.setValByName(session_feature, avg)
    
    def feature_count(self, feature_base):
        self.feature_inc(feature_base=feature_base, increment=1)

    def feature_inc(self, feature_base, increment):
        lvl_pref, sess_pref = JowilderExtractor._LEVEL_PREFIX, JowilderExtractor._SESS_PREFIX
        self._increment_feature_in_cur_levels(feature_name=lvl_pref + feature_base, increment=increment)
        self._increment_sess_feature(feature_name=sess_pref + feature_base, increment=increment)

    def feature_cc_inc(self, feature_name, index, increment):
        if self.getValByIndex(feature_name=feature_name, index=index) in JowilderExtractor._NULL_FEATURE_VALS:
            self.setValByIndex(feature_name, index=index, new_value=self._get_default_val(feature_name))
        self.features.incValByIndex(feature_name=feature_name, index=index, increment=increment)

    def feature_time_since_start(self, feature_base, cur_client_time):
        """
        Sets a session time since start feature. Will not write over a feature that has already been set.
        :param feature_base: name of feature without sess or level prefix
        :param cur_client_time: client time at which the event happened
        """
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
        
        

