# global imports
import abc
from typing import Any, Dict, Union
# local imports
from extractors.Feature import Feature

class FeatureLoader(abc.ABC):
    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        pass