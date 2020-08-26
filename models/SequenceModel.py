## import standard libraries
import abc
import typing
import logging
## import local libraries
from models.Model import *

## @class FeatureModel
#  Abstract base class for models that use per-session feature data as input rows.
#  For these models, we wrap the functionality in a private _eval function, which is called once per row.
class SequenceModel(Model):
    def __init__(self, levels: typing.List[int] = []):
        super().__init__(levels=levels, input_type=ModelInputType.SEQUENCE)

    def Eval(self, rows: typing.List) -> typing.List:
        return self._eval(rows)

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A list of rows of data for a session, which should each be a mapping of column names to values.
    #  @return     : A result for the given row of data
    @abc.abstractmethod
    def _eval(self, rows: typing.List):
        pass