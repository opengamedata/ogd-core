## import standard libraries
import abc
import typing
import logging
## import local libraries
from models.SequenceModel import SequenceModel

## @class SingleFeatureModel
#  Implementation for models which simply mirror a single feature to the dashboard.
#  Dead simple "model," but convenient way to integrate individual features into the dashboard.
class SimpleDeathPredictionModel(SequenceModel):
    def __init__(self, levels: typing.List[int] = []):
        super().__init__(levels)
        self.levels = levels
    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A row of data for a session, which should be a mapping of column names to
    #  @return     : A result for the given row of data
    def _eval(self, session: typing.Dict):
        death_trig_flag = False
        row_cnt = 0
        for i, row in enumerate(session):
            if row.category == 24:
                if row.emote_enum == 2:
                    death_trig_flag = True
                    row_cnt = i
            elif row.category == 18:
                #if the farmbitdeath event doeesn't trigger right after a desperate_emote_fullness (1/10), false
                if not((row_cnt +1) == i) and death_trig_flag:
                    return 0
        return 1