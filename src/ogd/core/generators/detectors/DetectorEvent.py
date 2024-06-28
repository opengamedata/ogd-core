# import libraries
import abc
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
# import locals
from ogd.core.models.Event import Event, EventSource
from ogd.core.utils.typing import Map

class DetectorEvent(Event):
   def __init__(self, session_id:str,      app_id:str,
                event_name:str,            event_data:Map,
                timestamp:datetime,        time_offset:Optional[timedelta],
                app_version:Optional[str], log_version:Optional[str],
                user_id:Optional[str],     user_data:Optional[Map],
                game_state:Optional[Map],  event_sequence_index:Optional[int]):
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
      :type app_version: Optional[str], optional
      :param log_version: _description_, defaults to None
      :type log_version: Optional[str], optional
      :param time_offset: _description_, defaults to None
      :type time_offset: Optional[int], optional
      :param user_id: _description_, defaults to ""
      :type user_id: Optional[str], optional
      :param user_data: _description_, defaults to {}
      :type user_data: Optional[Map], optional
      :param game_state: _description_, defaults to {}
      :type game_state: Optional[Map], optional
      :param event_sequence_index: _description_, defaults to None
      :type event_sequence_index: Optional[int], optional
      """
      super().__init__(session_id=session_id,   app_id=app_id,           timestamp=timestamp,
                       event_name=event_name,   event_data=event_data,   event_source=EventSource.GENERATED,
                       app_version=app_version, log_version=log_version, time_offset=time_offset,
                       user_id=user_id,         user_data=user_data,
                       game_state=game_state,   event_sequence_index=event_sequence_index)