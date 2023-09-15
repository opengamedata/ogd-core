# import libraries
from os import truncate
from extractors.features.PerCountFeature import PerCountFeature
from extractors.features.SessionFeature import SessionFeature
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class ContinuesOnFail(SessionFeature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._quit_type : Optional[bool] = None
        self._total_fails : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event:Event):
        
        return False
        #return int(event.GameState['att']) == self.CountIndex



    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [""]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["QuitType", "TotalFails"]

    def _extractFromEvent(self, event:Event) -> None:
        #self._story_alignment = event.EventData["story_alignment"]

        pass


    def _extractFromFeatureData(self, feature:FeatureData):
        if(feature._name =="QuitType"):
            self._quit_type = feature._vals
        elif(feature._name == "TotalFails"):
            self._total_fails = feature._vals


            
        return

    def _getFeatureValues(self) -> List[Any]:
        
        if(self._quit_type[2] == False):
            #didn't quit on fail
            return [self._total_fails[0]]
        else:
            #quit on fail, so subtract 1 for 
            return [self._total_fails[0]-1]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION, ExtractionMode.PLAYER,ExtractionMode.POPULATION] # >>> delete any modes you don't want run for your Feature. <<<
    
