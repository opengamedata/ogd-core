# import libraries
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event
from ogd.games.JOWILDER import Jowilder_Enumerators as je
from ogd.core.utils.utils import loadJSONFile
from ogd.core.utils.Logger import Logger

interaction_path = Path('.') / "ogd" / "games" / "JOWILDER"
METADATA_RAW : Dict[str, Dict[str, Any]] = loadJSONFile(filename="interaction_metadata.json", path=interaction_path, search_in_src=True)
METADATA     : Dict[int, Dict[str, Any]] = {je.fqid_to_enum.get(v.get("fqid", "FQID NOT FOUND"), -1): v for v in METADATA_RAW.values()}
Logger.Log(f"JoWilder InteractionName loaded {len(METADATA.keys())} metadata items.")

class InteractionName(PerCountFeature):

    def __init__(self, params=GeneratorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        return False

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        cur_interaction : Optional[Dict[str, Any]] = METADATA.get(self.CountIndex)
        if cur_interaction is not None:
            ret_val : List[Any] = [cur_interaction.get("fqid"), cur_interaction.get("count_boxes"), cur_interaction.get("num_words")]
        else:
            raise ValueError(f"Could not find metadata for interaction #{self.CountIndex}")
        return ret_val

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["BoxesCount", "WordsCount"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
