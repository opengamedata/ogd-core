from datetime import datetime
from typing import Any, Dict, List, Optional

from schemas.ExtractionMode import ExtractionMode

class FeatureData:
   def __init__(self,                  feature_type:str,        mode:ExtractionMode,
                feature_name:str,      value:Any,               state:Dict[str, Any],
                user_id:Optional[str], sess_id:Optional[str],   game_unit_id:Optional[str],
                feature_version:int,   ogd_version:str,         app_version:str, app_branch:str,
                last_session:str,      last_index:int,
                last_timestamp:datetime, start_timestamp:datetime):
      self._feature_name = feature_name
      self._feature_type = feature_type
      self._mode = mode
      self._feature_val = value
      self._feature_state = state

      self._user_id = user_id or "*"
      self._sess_id = sess_id or "*"
      self._game_unit_id = game_unit_id or "*"

      self._feat_version = feature_version
      self._ogd_version = ogd_version
      self._app_version = app_version
      self._app_branch = app_branch

      self._last_session = last_session
      self._last_index   = last_index
      self._last_timestamp = last_timestamp
      self._start_timestamp = start_timestamp

   def __str__(self):
      return f"Name: {self.Name}\tSub-unit ID: {self.GameUnitID}\nValues: {self._feature_val}\nMode: {self._mode.name}\tPlayer: {self.PlayerID}\tSession: {self.SessionID}"

   def __repr__(self):
      return self.Name

   @property
   def Name(self):
      return self._feature_name

   @property
   def FeatureType(self):
      return self._feature_type

   @property
   def ExportMode(self):
      return self._mode

   @property
   def FeatureValue(self) -> Any:
      return self._feature_val

   @property
   def FeatureState(self) -> Dict[str, Any]:
      return self._feature_state

   @property
   def PlayerID(self) -> Optional[str]:
      return self._user_id

   @property
   def SessionID(self) -> Optional[str]:
      return self._sess_id

   @property
   def GameUnitID(self) -> Optional[str]:
      return self._game_unit_id

   @property
   def FeatureVersion(self) -> int:
      return self._feat_version

   @property
   def OGDVersion(self) -> str:
      return self._ogd_version

   @property
   def AppVersion(self) -> str:
      return self._app_version

   @property
   def AppBranch(self) -> str:
      return self._app_branch

   @property
   def LastSession(self) -> str:
      return self._last_session

   @property
   def LastIndex(self) -> int:
      return self._last_index

   @property
   def LastTime(self) -> datetime:
      return self._last_timestamp

   @property
   def StartTime(self) -> datetime:
      return self._start_timestamp
