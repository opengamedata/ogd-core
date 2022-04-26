# import libraries
import abc
from datetime import datetime
from typing import Any, Dict, List, Union
# import locals
from schemas.Event import Event, EventSource
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

class DetectorEvent(Event):
   def __init__(self, session_id:str,  app_id:str, event_name:str,    event_data:Map, timestamp:datetime=datetime.now(),
                app_version:Union[str, None]=None, log_version:Union[str, None]=None, time_offset:Union[int,None] = None,
                user_id:Union[str,None] = "",      user_data:Union[Map,None] = {},
                game_state:Union[Map,None] = {},   event_sequence_index:Union[int,None] = None):
      """Constructor for the simple DetectorEvent wrapper.

      :param session_id: _description_
      :type session_id: str
      :param app_id: _description_
      :type app_id: str
      :param event_name: _description_
      :type event_name: str
      :param event_data: _description_
      :type event_data: Map
      :param timestamp: _description_, defaults to datetime.now()
      :type timestamp: datetime, optional
      :param app_version: _description_, defaults to None
      :type app_version: Union[str, None], optional
      :param log_version: _description_, defaults to None
      :type log_version: Union[str, None], optional
      :param time_offset: _description_, defaults to None
      :type time_offset: Union[int,None], optional
      :param user_id: _description_, defaults to ""
      :type user_id: Union[str,None], optional
      :param user_data: _description_, defaults to {}
      :type user_data: Union[Map,None], optional
      :param game_state: _description_, defaults to {}
      :type game_state: Union[Map,None], optional
      :param event_sequence_index: _description_, defaults to None
      :type event_sequence_index: Union[int,None], optional
      """
      super().__init__(session_id=session_id,   app_id=app_id,           timestamp=timestamp,
                       event_name=event_name,   event_data=event_data,   event_source=EventSource.GENERATED,
                       app_version=app_version, log_version=log_version, time_offset=time_offset,
                       user_id=user_id,         user_data=user_data,
                       game_state=game_state,   event_sequence_index=event_sequence_index)