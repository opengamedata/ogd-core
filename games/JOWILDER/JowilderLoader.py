## import standard libraries
from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional
## import local files
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from extractors.ExtractorLoader import ExtractorLoader
from games.JOWILDER.features.UsedContinue import UsedContinue
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema
from games.JOWILDER.features import *



class JowilderLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        if feature_type == "QuestionAnswers":
            ret_val = QuestionAnswers.QuestionAnswers(params=extractor_params)
        elif feature_type == "SurveyItem":
            ret_val = SurveyItem.SurveyItem(params=extractor_params)
        elif feature_type == "Interaction":
            ret_val = Interaction.Interaction(params=extractor_params)
        elif feature_type == "SurveyTime":
            ret_val = SurveyTime.SurveyTime(params=extractor_params)
        elif feature_type == "Clicks":
            ret_val = Clicks.Clicks(params=extractor_params)
        elif feature_type == "Hovers":
            ret_val = Hovers.Hovers(params=extractor_params)
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(params=extractor_params)
        elif feature_type == "InteractionName":
            ret_val = InteractionName.InteractionName(params=extractor_params)
        elif feature_type == "NotebookUses":
            ret_val = NotebookUses.NotebookUses(params=extractor_params)
        elif feature_type == "EventCount":
            ret_val = EventCount.EventCount(params=extractor_params)
        elif feature_type == "UserEnabled":
            ret_val = UserEnabled.UserEnabled(params=extractor_params)
        elif feature_type == "GameVersion":
            ret_val = GameVersion.GameVersion(params=extractor_params)
        elif feature_type == "UsedSaveCode":
            ret_val = UsedSaveCode.UsedSaveCode(params=extractor_params)
        elif feature_type == "GameScript":
            ret_val = GameScript.GameScript(params=extractor_params)
        elif feature_type == "SessionStart":
            ret_val = SessionStart.SessionStart(params=extractor_params)
        elif feature_type == "IdleState":
            ret_val = IdleState.IdleState(params=extractor_params, threshold=schema_args.get("IDLE_THRESH_SECONDS", IdleState.IdleState.IDLE_TIME_THRESHOLD))
        elif feature_type == "ActiveStateTime":
            ret_val = ActiveStateTime.ActiveStateTime(params=extractor_params, threshold=schema_args.get('ACTIVE_THRESH_SECONDS', ActiveStateTime.ActiveStateTime.ACTIVE_TIME_THRESHOLD))
        elif feature_type == "MeaningfulActions":
            ret_val = MeaningfulActions.MeaningfulActions(params=extractor_params)
        elif feature_type == "FirstInteraction":
            ret_val = FirstInteraction.FirstInteraction(params=extractor_params)
        elif feature_type == "LastInteraction":
            ret_val = LastInteraction.LastInteraction(params=extractor_params)
        elif feature_type == "UsedContinue":
            ret_val = UsedContinue.UsedContinue(params=extractor_params)
        elif feature_type == "InteractionWordsPerSecond":
            ret_val = InteractionWordsPerSecond.InteractionWordsPerSecond(params=extractor_params)
        elif feature_type == "InteractionTextBoxesPerSecond":
            ret_val = InteractionTextBoxesPerSecond.InteractionTextBoxesPerSecond(params=extractor_params)
        else:
            raise NotImplementedError(
                f"'{feature_type}' is not a valid feature for Jowilder.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Lakeland.")

    # *** BUILT-INS ***

    ## Constructor for the JoWilderExtractor class.
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
