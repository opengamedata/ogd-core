# import libraries
import json
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.PerCountFeature import PerCountFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from games.JOWILDER import Jowilder_Enumerators as je

with open(file="./games/JOWILDER/interaction_metadata.json") as f:
    METADATA = json.load(f)
    METADATA = {je.fqid_to_enum.get(v.get("fqid")): v for k, v in METADATA.items()}

class InteractionName(PerCountFeature):

    def __init__(self, params=ExtractorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        return False

    def _getEventDependencies(self) -> List[str]:
        return [] 

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        cur_interaction : dict = METADATA.get(self.CountIndex)
        ret_val : List[Any] = [cur_interaction.get("fqid"), cur_interaction.get("count_boxes"), cur_interaction.get("num_words")]
        return ret_val

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["BoxesCount", "WordsCount"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
