# import libraries
import abc
from datetime import datetime
from typing import Any, Dict, List, Union
# import locals
from schemas.Event import Event
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

class DetectorEvent(abc.ABC):
   def __init__(self, sess_id:str, app_id:str, event_name:str, event_data:Map, player_id:Union[str, None]=None, app_version:Union[str, None]=None, log_version:Union[str, None]=None):
      self._event = Event(session_id=sess_id,      app_id=app_id,         timestamp=datetime.now(),
                          event_name=event_name,   event_data=event_data, app_version=app_version,
                          log_version=log_version, user_id=player_id)