from typing import Any, List, Optional

from ogd.core.models.enums.ExtractionMode import ExtractionMode

class FeatureData:
   def __init__(self, name:str, feature_type:str, count_index:Optional[int],
                cols:List[str], vals:List[Any],   mode:ExtractionMode,
                player_id:Optional[str]=None,     sess_id:Optional[str]=None):
      self._name = name
      self._feature_type = feature_type
      self._count_index = count_index
      self._cols = cols
      self._vals = vals
      self._mode = mode
      self._player_id = player_id
      self._sess_id = sess_id

   def __str__(self):
      return f"Name: {self.Name}\tCount Index: {self.CountIndex}\nColumns: {self._cols}\t Values: {self._vals}\nMode: {self._mode.name}\tPlayer: {self.PlayerID}\tSession: {self.SessionID}"

   def __repr__(self):
      return self.Name

   @property
   def Name(self):
      return self._name

   @property
   def FeatureType(self):
      return self._feature_type

   @property
   def CountIndex(self):
      return self._count_index

   @property
   def FeatureNames(self) -> List[str]:
      return self._cols

   @property
   def FeatureValues(self) -> List[Any]:
      return self._vals

   @property
   def ExportMode(self):
      return self._mode

   @property
   def PlayerID(self) -> Optional[str]:
      return self._player_id

   @property
   def SessionID(self) -> Optional[str]:
      return self._sess_id