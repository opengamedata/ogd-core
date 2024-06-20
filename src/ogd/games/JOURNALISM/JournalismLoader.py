## import standard libraries
from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.games.JOURNALISM.features import *
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.games.JOURNALISM.features import StoryScoreSequence
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

class JournalismLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        if extractor_params._count_index == None:
            match feature_type:
                case "ChoiceClickCount":
                    ret_val = ChoiceClickCount.ChoiceClickCount(params=extractor_params)
                case "SessionPlayTime":
                    ret_val = SessionPlayTime.SessionPlayTime(params=extractor_params, threshold=schema_args.get("IDLE_THRESH_SECONDS", SessionPlayTime.SessionPlayTime.IDLE_TIME_THRESHOLD))
                case "FinalAttributes":
                    ret_val = FinalAttributes.FinalAttributes(params=extractor_params)
                case "FailureAttributes":
                    ret_val = FailureAttributes.FailureAttributes(params=extractor_params)
                case "SkillSequenceCount":
                    ret_val = SkillSequenceCount.SkillSequenceCount(params = extractor_params)
                case "MeanSnippetTime":
                    ret_val = MeanSnippetTime.MeanSnippetTime(params = extractor_params)
                case "TextClickCount":
                    ret_val = TextClickCount.TextClickCount(params=extractor_params)
                case "SnippetReceivedCount":
                    ret_val = SnippetReceivedCount.SnippetReceivedCount(params =extractor_params)
                case "StoryCompleteTime":
                    ret_val = StoryCompleteTime.StoryCompleteTime(params = extractor_params)
                case "TotalLevelTime":
                    ret_val = TotalLevelTime.TotalLevelTime(params = extractor_params)
                case "PlayerAttributes":
                    ret_val = PlayerAttributes.PlayerAttributes(params = extractor_params)
                case "QuitLevel":
                    ret_val = QuitLevel.QuitLevel(params = extractor_params)
                case "QuitType":
                    ret_val = QuitType.QuitType(params = extractor_params)
                case "WorstAttribute":
                    ret_val = WorstAttribute.WorstAttribute(params = extractor_params)
                case "TopAttribute":
                    ret_val = TopAttribute.TopAttribute(params=extractor_params)
                case "TopPlayerAttribute":
                    ret_val = TopPlayerAttribute.TopPlayerAttribute(params=extractor_params)
                case "TotalFails":
                    ret_val = TotalFails.TotalFails(params=extractor_params)
                case "ContinuesOnFail":
                    ret_val = ContinuesOnFail.ContinuesOnFail(params = extractor_params)        
                case "PlayTime":
                    ret_val = PlayTime.PlayTime(params=extractor_params, threshold= schema_args.get("IDLE_THRESH_SECONDS", PlayTime.PlayTime.IDLE_TIME_THRESHOLD))
                case "UserPlayTime":
                    ret_val = UserPlayTime.UserPlayTime(params=extractor_params)
                case "GameComplete":
                    ret_val = GameComplete.GameComplete(params=extractor_params)
                case "QuitNode":
                    ret_val = QuitNode.QuitNode(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature for Journalism.")
        ##per-count features
        else:
            match feature_type:
                case "StoryAlignment":
                    ret_val = StoryAlignment.StoryAlignment(params = extractor_params)
                case "WorstPlayerAttribute":
                    ret_val = WorstPlayerAttribute.WorstPlayerAttribute(params=extractor_params)
                case "MaxedPlayerAttribute":
                    ret_val = MaxedPlayerAttribute.MaxedPlayerAttribute(params=extractor_params)           
                case "LevelCompleteCount":
                    ret_val = LevelCompleteCount.LevelCompleteCount(params=extractor_params)
                case "LevelCompleted":
                    ret_val = LevelCompleted.LevelCompleted(params=extractor_params)
                case "FailureCount":
                    ret_val = FailureCount.FailureCount(params=extractor_params)
                case "SnippetReplace":
                    ret_val = SnippetReplace.SnippetReplace(params=extractor_params)
                case "StoryEditorTime":
                    ret_val = StoryEditorTime.StoryEditorTime(params=extractor_params, threshold= schema_args.get("IDLE_THRESH_SECONDS", PlayTime.PlayTime.IDLE_TIME_THRESHOLD))
                case "AttributeView":
                    ret_val = AttributeView.AttributeView(params=extractor_params)
                case "EditorNoteOpen":
                    ret_val = EditorNoteOpen.EditorNoteOpen(params=extractor_params)
                case "TopPlayerQuitType":
                    ret_val= TopPlayerQuitType.TopPlayerQuitType(params=extractor_params)
                case "StoryScore":
                    ret_val= StoryScore.StoryScore(params=extractor_params)    
                case "StoryAlignmentSequence":
                    ret_val= StoryAlignmentSequence.StoryAlignmentSequence(params=extractor_params)    
                case "StoryScoreSequence":
                    ret_val= StoryScoreSequence.StoryScoreSequence(params=extractor_params)    
                case "LevelTime":
                    ret_val= LevelTime.LevelTime(params=extractor_params)    
                case "SnippetsCollected":
                    ret_val= SnippetsCollected.SnippetsCollected(params=extractor_params)    
                case "SnippetsSubmitted":
                    ret_val= SnippetsSubmitted.SnippetsSubmitted(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature for Journalism.")
        return ret_val
    

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid detector for Journalism.")
        return None

    # *** BUILT-INS & PROPERTIES ***

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
