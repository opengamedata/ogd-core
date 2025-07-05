import abc
from typing import List
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.Model import Model

class PopulationModel(Model):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    ## Abstract function to get a list of event types the Feature wants.
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []
