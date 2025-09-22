# import libraries
from datetime import datetime, timedelta, timezone
from typing import Optional
# import locals
from ogd.common.models.Event import Event, EventSource
from ogd.common.utils.typing import Map

class DetectorEvent(Event):
   def __init__(self, app_id:str,          user_id:Optional[str],                       session_id:str,
                app_version:Optional[str], app_branch:Optional[str],                    log_version:Optional[str],
                timestamp:datetime,        time_offset:Optional[timedelta | timezone],  event_sequence_index:Optional[int],
                event_name:str,            event_data:Map,
                game_state:Optional[Map],  user_data:Optional[Map]):
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
      tz : timezone
      if isinstance(time_offset, timezone):
         tz = time_offset
      elif isinstance(time_offset, timedelta):
         tz = timezone(offset=time_offset)
      super().__init__(app_id=app_id,           user_id=user_id,                    session_id=session_id,
                       app_version=app_version, app_branch=app_branch,              log_version=log_version,
                       timestamp=timestamp,     time_offset=tz,                     event_sequence_index=event_sequence_index,
                       event_name=event_name,   event_source=EventSource.GENERATED, event_data=event_data,
                       game_state=game_state,   user_data=user_data)