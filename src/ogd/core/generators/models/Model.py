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

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    def Train(self):
        self._train()

    def Apply(self, apply_to:List[FeatureData | Event]) -> FeatureData | Event:
        return self._apply(apply_to=apply_to)
