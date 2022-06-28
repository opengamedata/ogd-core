from typing import Any, List, Optional

class FeatureData:
   def __init__(self, name:str, count_index:Optional[int], cols:List[str], vals:List[Any],
                player_id:Optional[str]=None, sess_id:Optional[str]=None):
      self._name = name
      self._count_index = count_index
      self._cols = cols
      self._vals = vals
      self._player_id = player_id
      self._sess_id = sess_id

   @property
   def Name(self):
      return self._name

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
   def PlayerID(self) -> Optional[str]:
      return self._player_id

   @property
   def SessionID(self) -> Optional[str]:
      return self._sess_id