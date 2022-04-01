# import libraries
from typing import Any, Dict, List, Type
# import locals
from extractors.Extractor import Extractor
from features.FeatureData import FeatureData
from features.FeatureLoader import FeatureLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

class EventExtractor(Extractor):
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getFeatureNames(self) -> List[str]:
        return ["No Features for Event extractor"]

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    def _getFeatureValues(self, export_types:ExporterTypes) -> Dict[str,List[Any]]:
        return {}

    def _getFeatureData(self, order:int) -> Dict[str,List[FeatureData]]:
        return {}

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    def _processEvent(self, event:Event):
        pass

    def _processFeatureData(self, feature:FeatureData):
        pass

    def _prepareLoader(self) -> FeatureLoader:
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self, LoaderClass: Type[FeatureLoader], game_schema: GameSchema):
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=None)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***