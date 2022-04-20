from typing import Any, List, Union

class FeatureData:
   def __init__(self, name:str, count_index:int, cols:List[str], vals:List[Any],
                player_id:Union[str, None]=None, sess_id:Union[str, None]=None):
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
   def PlayerID(self) -> Union[str, None]:
      return self._player_id

   @property
   def SessionID(self) -> Union[str, None]:
      return self._sess_id