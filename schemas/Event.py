from datetime import datetime
from typing import Any, Dict, Union

## @class Event
#  Completely dumb struct that enforces a particular structure for the data we get from a source.
#  Basically, whenever we fetch data, the TableSchema will be used to map columns to the required elements of an Event.
#  Then the extractors etc. can just access columns in a direct manner.
class Event:
    def __init__(self, session_id:int, app_id:str, timestamp:datetime, event_name:str, event_data:Dict[str,Any],
                 user_id:Union[int,None] = None,   user_data:Union[Dict[str,Any],None] = None,
                 game_state:Union[Dict[str,Any],None] = None, time_offset:Union[int,None] = None,
                 event_sequence_index:Union[int,None] = None):
        self.session_id = session_id
        self.app_id = app_id
        self.timestamp = timestamp
        self.event_name = event_name
        self.event_data = event_data
        self.user_id = user_id
        self.user_data = user_data
        self.game_state = game_state
        self.time_offset = time_offset
        self.event_sequence_index = event_sequence_index
