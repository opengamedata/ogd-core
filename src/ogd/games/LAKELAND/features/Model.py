## import standard libraries
import abc
import enum
import typing
import logging

@enum.unique
class ModelInputType(enum.Enum):
    FEATURE  = enum.auto()
    SEQUENCE = enum.auto()

    def __str__(self):
        return self.name

## @class Model
#  Abstract base class for models to be displayed in realtime dashboard.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Model(abc.ABC):
    def __init__(self, input_type: ModelInputType, levels: typing.List[int] = []):
        self._input_type : ModelInputType   = input_type
        self._levels     : typing.List[int] = levels

    def GetInputType(self):
        return self._input_type

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A list of rows, where each row contains all columns expected by the specific model implementation.
    #  @return     : A list of results for the data (how many results depends on the model)
    @abc.abstractmethod
    def Eval(self, rows: typing.List) -> typing.List:
        pass