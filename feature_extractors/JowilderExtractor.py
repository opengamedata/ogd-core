## import standard libraries
import bisect
import json
import logging
import math
import typing
## import local files
import utils
import numpy as np
from sklearn.linear_model import LinearRegression
from feature_extractors.Extractor import Extractor
from GameTable import GameTable
from schemas.Schema import Schema

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
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
         20: 'wildcard_hover'
    }
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        super().__init__(session_id=session_id, game_table=game_table, game_schema=game_schema)

        self.features.setValByName(feature_name="sessionID", new_value=session_id)

    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        # put some data in local vars, for readability later.
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
            if self.features.getValByName(feature_name="persistentSessionID") == 0:
                self.features.setValByName(feature_name="persistentSessionID",
                                           new_value=row_with_complex_parsed[game_table.pers_session_id_index])
            # Ensure we have private data initialized for this level.
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
        _correct = d.get("correct")  # uncertain field
        _answer = d["answer"]
        _level = d["level"]

        # helpers
        # set class variables
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
        _name = d["name"]
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
        _correct = d.get("correct")  # uncertain field
        _answer = d.get("answer")  # uncertain field
        _level = d["level"]

        # helpers
        # set class variables
        # set features