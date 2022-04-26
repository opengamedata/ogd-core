# import libraries
import abc
from datetime import datetime
from typing import Any, Dict, List, Union
# import locals
from schemas.Event import Event, EventSource
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

class DetectorEvent(Event):
   def __init__(self, sess_id:str, app_id:str, event_name:str, event_data:Map, timestamp:datetime=datetime.now(),
                app_version:Union[str, None]=None, log_version:Union[str, None]=None, time_offset:Union[int,None] = None,
                user_id:Union[str,None] = "",   user_data:Union[Map,None] = {},
                game_state:Union[Map,None] = {}, event_sequence_index:Union[int,None] = None):
      super().__init__(session_id=sess_id,      app_id=app_id,           timestamp=timestamp,
                       event_name=event_name,   event_data=event_data,   event_source=EventSource.GENERATED,
                       app_version=app_version, log_version=log_version, time_offset=time_offset,
                       user_id=user_id, user_data=user_data,
                       game_state=game_state, event_sequence_index=event_sequence_index)