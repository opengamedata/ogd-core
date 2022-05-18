# standard libraries
import json
from typing import Any, Dict, List, Union
# local imports
from coding.Coder import Coder
from utils import map

class Code: 
    class EventID:
        def __init__(self, sess_id:str, index:int):
            self._session_id = sess_id
            self._index      = index

        @staticmethod
        def FromJSON(json_obj:map):
            _session_id : Union[str, None] = json_obj.get("session_id", None)
            _index      : Union[str, None] = json_obj.get("index", None)
            if _index is None:
                raise ValueError("JSON object for Coder has no 'name' element!")
            elif _session_id is None:
                raise ValueError("JSON object for Coder has no 'id' element!")
            else:
                return Code.EventID(name=_index, id=_session_id)

        @property
        def SessionID(self):
            return self._session_id

        @property
        def Index(self):
            return self._index

    def __init__(self, code_word:str, id:str, coder:Coder, events:List[EventID], notes:Union[str, None]=None):
        self._code   = code_word
        self._id     = id
        self._coder  = coder
        self._events = events
        self._notes  = notes

    @staticmethod
    def FromJSON(json_obj:map):
        _code_word  : Union[str, None]       = json_obj.get("code_word", None)
        _id         : Union[str, None]       = json_obj.get("id", None)
        _coder_obj  : Union[map, None]       = json_obj.get("coder", None)
        _events_obj : Union[List[map], None] = json_obj.get("events", None)
        _notes      : Union[str, None]       = json_obj.get("notes", None)
        if _code_word is None:
            raise ValueError("JSON object for Code has no 'code_word' element!")
        elif _id is None:
            raise ValueError("JSON object for Code has no 'id' element!")
        elif _coder_obj is None:
            raise ValueError("JSON object for Code has no 'coder' element!")
        elif _events_obj is None:
            raise ValueError("JSON object for Code has no 'events' element!")
        else:
            _coder = Coder.FromJSON(json_obj=_coder_obj)
            _events = [Code.EventID.FromJSON(item) for item in _events_obj]
            return Code(code_word=_code_word, id=_id, coder=_coder, events=_events, notes=_notes)

    @property
    def CodeWord(self):
        return self._code

    @property
    def ID(self):
        return self._id

    @property
    def Coder(self):
        return self._coder

    @property
    def Events(self):
        return self._events

    @property
    def Notes(self):
        return self._notes

    @property
    def JSON(self) -> str:
        return json.dumps({
            "code_word":self.CodeWord,
            "id":self.ID,
            "coder":self.Coder,
            "events":self.Events,
            "notes":self.Notes
        })
