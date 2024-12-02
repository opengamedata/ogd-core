from typing import List
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.PopulationModel import PopulationModel

class KMeansModel(PopulationModel):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        raise TypeError(f"Can't call function on class {cls.__name__} with abstract method _featureFilter")

    def _updateFromFeatureData(self, feature:FeatureData):
        pass

    def _train(self):
        pass

    def _apply(self, apply_to:List[FeatureData]) -> FeatureData:
        pass
