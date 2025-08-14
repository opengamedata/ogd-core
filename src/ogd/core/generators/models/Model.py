import abc
from typing import List
from ogd.common.models.Event import Event
from ogd.common.models.FeatureData import FeatureData
from ogd.core.generators.Generator import Generator
from ogd.core.generators.Generator import GeneratorParameters

class Model(Generator):
    @abc.abstractmethod
    def _train(self):
        pass

    @abc.abstractmethod
    def _apply(self, apply_to:List[FeatureData | Event]) -> FeatureData | Event:
        pass

    ## Abstract declaration of a function to perform update of a feature from a row.
    @abc.abstractmethod
    def _updateFromFeatureData(self, feature:FeatureData):
        """Abstract declaration of a function to perform update of a feature from a row.

        TODO : this will get removed once patch is in that puts _updateFromFeatureData in Generator base class.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        pass

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    def Train(self):
        self._train()

    def Apply(self, apply_to:List[FeatureData | Event]) -> FeatureData | Event:
        return self._apply(apply_to=apply_to)
    
    def Render(self, save_path:str = None):
        return self._render(save_path=save_path)
    
    def ModelInfo(self):
        return self._modelInfo()
