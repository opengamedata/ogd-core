## import standard libraries
import abc
import typing
import logging
## import local libraries
from models.Model import *

## @class FeatureModel
#  Abstract base class for models that use per-session feature data as input rows.
#  For these models, we wrap the functionality in a private _eval function, which is called once per row.
class FeatureModel(Model):
    def __init__(self, levels: typing.List[int] = []):
        super().__init__(levels=levels, input_type=ModelInputType.FEATURE)
    ## Very simple implementation of the Eval function.
    #  We assume each row is a session, so call private _eval function once per row.
    #
    #  @param rows : A list of rows, where each row contains all columns expected by the specific model implementation.
    #  @return     : A list of results for the data (how many results depends on the model)
    def Eval(self, rows: typing.List) -> typing.List:
        return [self._eval(row) for row in rows]

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A row of data for a session, which should be a mapping of column names to 
    #  @return     : A result for the given row of data
    @abc.abstractmethod
    def _eval(self, row: typing.Dict):
        pass