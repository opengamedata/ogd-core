# import locals
from features.Feature import Feature

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class SessionFeature(Feature):
    def __init__(self, name:str, description:str):
        Feature.__init__(self, name=name, description=description, count_index=0)