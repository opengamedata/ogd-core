## import standard libraries
from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional
## import local files
import games.JOURNALISM.features
from games.JOURNALISM.features import *
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from extractors.ExtractorLoader import ExtractorLoader
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema



class JournalismLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return games.JOURNALISM.features

    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        if feature_type == "ChoiceClickCount":
            ret_val = ChoiceClickCount.ChoiceClickCount(params=extractor_params)
        elif feature_type == "IdleState":
            ret_val = IdleState.IdleState(params=extractor_params, threshold=schema_args.get("IDLE_THRESH_SECONDS", IdleState.IdleState.IDLE_TIME_THRESHOLD))
        elif feature_type == "SkillSequenceCount":
            ret_val = SkillSequenceCount.SkillSequenceCount(params = extractor_params)
        elif feature_type == "MeanSnippetTime":
            ret_val = MeanSnippetTime.MeanSnippetTime(params = extractor_params)
        elif feature_type == "TextClickCount":
            ret_val = TextClickCount.TextClickCount(params=extractor_params)
        elif feature_type == "SnippetReceivedCount":
            ret_val = SnippetReceivedCount.SnippetReceivedCount(params =extractor_params)
        elif feature_type == "StoryCompleteTime":
            ret_val = StoryCompleteTime.StoryCompleteTime(params = extractor_params)
        elif feature_type == "TotalLevelTime":
            ret_val = TotalLevelTime.TotalLevelTime(params = extractor_params)
        elif feature_type == "PlayerAttributes":
            ret_val = PlayerAttributes.PlayerAttributes(params = extractor_params)
        elif feature_type == "QuitTimestamp":
            ret_val = QuitTimestamp.QuitTimestamp(params = extractor_params)
        elif feature_type == "QuitType":
            ret_val = QuitType.QuitType(params = extractor_params)
        elif feature_type == "WorstAttribute":
            ret_val = WorstAttribute.WorstAttribute(params = extractor_params)
        elif feature_type == "TopAttribute":
            ret_val = TopAttribute.TopAttribute(params=extractor_params)
        elif feature_type == "TopPlayerAttribute":
            ret_val = TopPlayerAttribute.TopPlayerAttribute(params=extractor_params)
        
        ##per-count features
        elif extractor_params._count_index is not None:
            if feature_type == "LevelStoryAlignment":
                ret_val = LevelStoryAlignment.LevelStoryAlignment(params = extractor_params)
            elif feature_type == "WorstPlayerAttribute":
                ret_val = WorstPlayerAttribute.WorstPlayerAttribute(params=extractor_params)
            elif feature_type == "MaxedPlayerAttribute":
                ret_val = MaxedPlayerAttribute.MaxedPlayerAttribute(params=extractor_params)           


        else:
            raise NotImplementedError(
                f"'{feature_type}' is not a valid feature for Journalism.")
        return ret_val
    

    def _loadDetector(self, detector_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Journalism.")

    # *** BUILT-INS ***

    ## Constructor for the JournalismExtractor class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the CrystalLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GameSchema
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)
