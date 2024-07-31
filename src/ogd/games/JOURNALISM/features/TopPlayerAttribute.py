# import libraries
from os import truncate
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models import Event
from typing import Any, Final, List
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class TopPlayerAttribute(PerCountFeature):
    def __init__(self, params:GeneratorParameters):
        PerCountFeature.__init__(self, params=params)
        self._attr_count = 0
        self._ATTRIBUTE_ENUM : Final[List[str]] = ["endurance", "resourceful", "tech","social","trust","research"]
        self._attr_name = self._ATTRIBUTE_ENUM[self.CountIndex]


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event:Event):
        
        return False
        #return int(event.GameState['att']) == self.CountIndex



    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return [""]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["TopAttribute"]

    def _updateFromEvent(self, event:Event) -> None:
        #self._story_alignment = event.EventData["story_alignment"]

        pass


    def _updateFromFeatureData(self, feature:FeatureData):
        #add logic to make sure that MODE is session, not player so we don't get duplicates
        if(feature._mode == ExtractionMode.SESSION):
            attribute_list = feature._vals[1]
            for attr in attribute_list:
                if(self._ATTRIBUTE_ENUM.index(attr) == self.CountIndex):
                    self._attr_count+=1
            
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._attr_name, self._attr_count]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Count"]
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION] # >>> delete any modes you don't want run for your Feature. <<<
    
