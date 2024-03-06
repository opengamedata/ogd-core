## import standard libraries
import logging
import typing
## import local libraries
from models.FeatureModel import FeatureModel

## @class SingleFeatureModel
#  Implementation for models which simply mirror a single feature to the dashboard.
#  Dead simple "model," but convenient way to integrate individual features into the dashboard.
class SingleFeatureModel(FeatureModel):
    def __init__(self, column_name: str, levels: typing.List[int] = []):
        super().__init__(levels)
        self._col_name = column_name

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A row of data for a session, which should be a mapping of column names to 
    #  @return     : A result for the given row of data
    def _eval(self, row: typing.Dict):
        return row[self._col_name]