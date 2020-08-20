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