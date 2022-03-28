from typing import Any, Dict, List, Union
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

class FeatureData:
   def __init__(self, sess_id:Union[str, None], app_id:Union[str, None], event_name:str, event_data:Map, player_id:Union[str, None]=None, ):
      self._name = name
      self._count_index = count_index
      self._cols = cols
      self._vals = vals
      self._player_id = player_id
      self._sess_id = sess_id

   def Name(self):
      return self._name

   def CountIndex(self):
      return self._count_index

   def FeatureNames(self) -> List[str]:
      return self._cols

   def FeatureValues(self) -> List[Any]:
      return self._vals

   def PlayerID(self) -> Union[str, None]:
      return self._player_id

   def SessionID(self) -> Union[str, None]:
      return self._sess_id