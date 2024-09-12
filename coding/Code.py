# standard libraries
import json
from typing import List, Optional
# OGD imports
from ogd.common.utils.typing import Map
# local imports
from coding.Coder import Coder

class Code: 
    class EventID:
        def __init__(self, sess_id:str, index:int):
            self._session_id = sess_id
            self._index      = index

        @staticmethod
        def FromJSON(json_obj:Map):
            _session_id : Optional[str] = json_obj.get("session_id", None)
            _index      : Optional[int] = json_obj.get("index", None)
            if _index is None:
                raise ValueError("JSON object for Coder has no 'name' element!")
            elif _session_id is None:
                raise ValueError("JSON object for Coder has no 'id' element!")
            else:
                return Code.EventID(sess_id=_session_id, index=_index)

        @property
        def SessionID(self):
            return self._session_id

        @property
        def Index(self):
            return self._index

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, code_word:str, id:str, coder:Coder, events:List[EventID], notes:Optional[str]=None):
        self._code   = code_word
        self._id     = id
        self._coder  = coder
        self._events = events
        self._notes  = notes

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromJSON(json_obj:Map):
        _code_word  : Optional[str]       = json_obj.get("code_word", None)
        _id         : Optional[str]       = json_obj.get("id", None)
        _coder_obj  : Optional[Map]       = json_obj.get("coder", None)
        _events_obj : Optional[List[Map]] = json_obj.get("events", None)
        _notes      : Optional[str]       = json_obj.get("notes", None)
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

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

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

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
